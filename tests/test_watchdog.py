#!/usr/bin/env python3
"""Regression tests for #418: the liveness watchdog mechanizes the two
highest-frequency responses from runtime/worker-supervision.md — liveness
watch and auto-nudge — while stop and re-dispatch stay coordinator decisions.

The policy's shape, as witnessed in the 2026-09-14 clean-sweep tracker run:
slow-but-alive is not stuck (no action); HUNG gets one auto-nudge; still-HUNG
after the budget, or WEDGED on positive evidence, yields a stop-redispatch
RECOMMENDATION with JSONL evidence — never an auto-dispatch.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("watchdog", ROOT / "runtime" / "scripts" / "watchdog.py")
watchdog = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(watchdog)

TRACE = ROOT / "tests" / "watchdog-trace-2026-09-14.jsonl"
CONFIG = ROOT / "runtime" / "watchdog.json"

T0 = watchdog.parse_ts("2026-09-14T12:00:00Z", "t0")


def worker(wid="task_w", idle_min=1, stop_min=None, **kw):
    now = T0
    rec = {
        "worker_id": wid,
        "dispatch_id": "d-" + wid,
        "dispatched_at": (now - timedelta(minutes=90)).isoformat(),
        "last_movement_at": (now - timedelta(minutes=idle_min)).isoformat(),
    }
    if stop_min is not None:
        rec["stop_at"] = (now - timedelta(minutes=stop_min)).isoformat()
    rec.update(kw)
    return rec


def cfg(**over):
    base = dict(watchdog.DEFAULTS)
    base.update(over)
    return base


CFG = cfg()


class ClassifyStates(unittest.TestCase):
    def test_ok_when_fresh(self):
        state, _ = watchdog.classify(worker(idle_min=1), T0, CFG)
        self.assertEqual(state, "OK")

    def test_slow_but_alive_is_not_stuck(self):
        state, _ = watchdog.classify(worker(idle_min=12), T0, CFG)
        self.assertEqual(state, "SLOW")
        _, action, _, _ = watchdog.decide(worker(idle_min=12), T0, CFG, {"workers": {}})
        self.assertEqual(action, "none")

    def test_hung_past_idle_threshold_gets_one_nudge(self):
        _, action, _, _ = watchdog.decide(worker(idle_min=45), T0, CFG, {"workers": {}})
        self.assertEqual(action, "nudge")

    def test_past_stop_silence_is_hung_not_slow(self):
        # Fresh movement but past STOP with no report: the policy's partial-report
        # STOP was missed, so this is STUCK even though idle is small.
        rec = worker(idle_min=2, stop_min=10, reported=False)
        state, _ = watchdog.classify(rec, T0, CFG)
        self.assertEqual(state, "HUNG")

    def test_past_stop_reporter_is_not_stuck(self):
        rec = worker(idle_min=2, stop_min=10, reported=True)
        state, _ = watchdog.classify(rec, T0, CFG)
        self.assertEqual(state, "OK")

    def test_wedge_marker_recommends_immediately_without_nudge(self):
        rec = worker(idle_min=5, wedge_markers=["provider_stream_dead"])
        state, action, _, _ = watchdog.decide(rec, T0, CFG, {"workers": {}})
        self.assertEqual((state, action), ("WEDGED", "recommend"))

    def test_frozen_past_stop_plus_unanswered_nudge_is_wedged(self):
        rec = worker(idle_min=75, stop_min=30, reported=False,
                     last_nudge_at=(T0 - timedelta(minutes=30)).isoformat(),
                     last_nudge_answered=False,
                     prior_nudges=[(T0 - timedelta(minutes=30)).isoformat()])
        state, action, ev, _ = watchdog.decide(rec, T0, CFG, {"workers": {}})
        self.assertEqual(state, "WEDGED")
        self.assertEqual(action, "recommend")
        self.assertIn("wedge_basis", ev)

    def test_answered_nudge_breaks_the_wedge_test(self):
        rec = worker(idle_min=75, stop_min=30, reported=False,
                     last_nudge_at=(T0 - timedelta(minutes=30)).isoformat(),
                     last_nudge_answered=True)
        state, _ = watchdog.classify(rec, T0, CFG)
        self.assertEqual(state, "HUNG")  # still stuck, but not positively wedged

    def test_malformed_timestamp_is_a_heartbeat_error(self):
        rec = worker(last_movement_at="not-a-time")
        with self.assertRaises(watchdog.HeartbeatError):
            watchdog.classify(rec, T0, CFG)

    def test_settled_workers_are_not_the_watchdogs_business(self):
        for terminal in ("exited", "completed", "released"):
            rec = worker(idle_min=999, terminal=terminal)
            state, action, _, _ = watchdog.decide(rec, T0, CFG, {"workers": {}})
            self.assertEqual((state, action), ("SETTLED", "none"))


class NudgeRateLimits(unittest.TestCase):
    def test_still_hung_after_budget_recommends(self):
        rec = worker(idle_min=45,
                     prior_nudges=[(T0 - timedelta(hours=2)).isoformat()])
        state, action, _, note = watchdog.decide(rec, T0, CFG, {"workers": {}})
        self.assertEqual((state, action), ("HUNG", "recommend"))
        self.assertIn("budget spent", note)

    def test_nudge_window_holds_back_to_back_nudges(self):
        generous = cfg(max_nudges_per_dispatch=5, max_nudges_per_hour_per_worker=5)
        rec = worker(idle_min=45,
                     prior_nudges=[(T0 - timedelta(minutes=10)).isoformat()])
        _, action, _, note = watchdog.decide(rec, T0, generous, {"workers": {}})
        self.assertEqual(action, "recommend")
        self.assertIn("window holds", note)

    def test_hourly_cap_holds(self):
        generous = cfg(max_nudges_per_dispatch=9, nudge_window_s=0,
                       max_nudges_per_hour_per_worker=2)
        rec = worker(idle_min=45, prior_nudges=[
            (T0 - timedelta(minutes=50)).isoformat(),
            (T0 - timedelta(minutes=20)).isoformat()])
        _, action, _, note = watchdog.decide(rec, T0, generous, {"workers": {}})
        self.assertEqual(action, "recommend")
        self.assertIn("hourly cap", note)

    def test_flapping_worker_causes_no_nudge_storm(self):
        # HUNG/OK oscillation across ticks: the per-dispatch budget caps total
        # nudges no matter how often the worker flaps back to HUNG.
        state = {"workers": {}}
        nudges = 0
        for minute, idle in ((0, 45), (10, 1), (20, 45), (30, 1), (40, 45)):
            now = T0 + timedelta(minutes=minute)
            rec = worker(idle_min=idle)
            if idle == 1:
                rec["last_movement_at"] = now.isoformat()
            _, action, _, _ = watchdog.decide(rec, now, CFG, state)
            if action == "nudge":
                nudges += 1
                watchdog.record_nudge(state, rec["worker_id"], rec["dispatch_id"], now)
        self.assertEqual(nudges, 1)

    def test_fresh_dispatch_resets_the_budget(self):
        state = {"workers": {"task_w": {"dispatch_id": "d-old",
                                       "nudges": [T0.isoformat()] * 5}}}
        rec = worker(idle_min=45)  # dispatch_id d-task_w != d-old
        _, action, _, _ = watchdog.decide(rec, T0, CFG, state)
        self.assertEqual(action, "nudge")


class ConfigContract(unittest.TestCase):
    def test_unknown_config_key_fails_loud(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "w.json"
            p.write_text(json.dumps({"hung_after_s": 60, "hung_after_sec": 60}))
            with self.assertRaises(watchdog.ConfigError) as cm:
                watchdog.load_config(p)
            self.assertIn("hung_after_sec", str(cm.exception))

    def test_thresholds_tunable_without_code_edits(self):
        strict = cfg(hung_after_s=60)
        state, _ = watchdog.classify(worker(idle_min=5), T0, strict)
        self.assertEqual(state, "HUNG")
        state, _ = watchdog.classify(worker(idle_min=5), T0, CFG)
        self.assertEqual(state, "OK")

    def test_shipped_config_loads(self):
        loaded = watchdog.load_config(CONFIG)
        self.assertEqual(loaded["max_nudges_per_dispatch"], 1)


class RecordedTraceReplay(unittest.TestCase):
    def test_replay_matches_the_manual_log(self):
        loaded = watchdog.load_config(CONFIG)
        ticks = 0
        for line in TRACE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            snap = json.loads(line)
            now = watchdog.parse_ts(snap["now"], "now")
            results = watchdog.tick(snap, now, loaded, {"workers": {}})
            self.assertEqual(
                {r["worker_id"] for r in results}, set(snap["expect"]),
                f"tick {snap['tick']}: worker set drifted from the fixture")
            for res in results:
                with self.subTest(tick=snap["tick"], worker=res["worker_id"]):
                    self.assertEqual([res["classification"], res["action"]],
                                     snap["expect"][res["worker_id"]])
            ticks += 1
        self.assertGreaterEqual(ticks, 5, "fixture lost its ticks")


def run_cli(*argv):
    return subprocess.run([sys.executable, str(ROOT / "runtime" / "scripts" / "watchdog.py"), *argv],
                          capture_output=True, text=True, cwd=ROOT)


class DryRunPurity(unittest.TestCase):
    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            beats = tmp / "beats.json"
            beats.write_text(json.dumps({
                "run_id": "run_purity",
                "workers": [worker(idle_min=45),
                            worker(wid="task_v", idle_min=5,
                                   wedge_markers=["dialog_block"])],
            }))
            state, log, sink = tmp / "s.json", tmp / "w.jsonl", tmp / "sink.txt"
            nudge_cfg = tmp / "w.json"
            nudge_cfg.write_text(json.dumps({
                "nudge_command": ["sh", "-c", "echo nudged >> " + str(sink)]}))
            proc = run_cli("--heartbeats", str(beats), "--config", str(nudge_cfg),
                           "--state", str(state), "--log", str(log),
                           "--now", "2026-09-14T12:00:00Z", "--dry-run")
            self.assertEqual(proc.returncode, 1)  # WOULD-recommend present
            self.assertIn("WOULD-NUDGE", proc.stdout)
            self.assertIn("WOULD-RECOMMEND", proc.stdout)
            for path in (state, log, sink):
                self.assertFalse(path.exists(), f"dry-run created {path.name}")

    def test_dry_run_exit_zero_when_nothing_needs_the_coordinator(self):
        with tempfile.TemporaryDirectory() as tmp:
            beats = Path(tmp) / "beats.json"
            beats.write_text(json.dumps({"run_id": "run_ok", "workers": [worker()]}))
            proc = run_cli("--heartbeats", str(beats), "--config", str(CONFIG),
                           "--now", "2026-09-14T12:00:00Z", "--dry-run")
            self.assertEqual(proc.returncode, 0)
            self.assertIn("OK none", proc.stdout)


class LiveMode(unittest.TestCase):
    def _live_cfg(self, tmp):
        sink = tmp / "sink.txt"
        nudge_cmd = ["sh", "-c", "echo \"{worker_id} {dispatch_id}\" >> " + str(sink)]
        conf = tmp / "w.json"
        conf.write_text(json.dumps({"nudge_command": nudge_cmd}))
        return conf, sink

    def _beats(self, tmp, workers):
        beats = tmp / "beats.json"
        beats.write_text(json.dumps({"run_id": "run_live", "workers": workers}))
        return beats

    def test_hung_worker_nudged_once_then_recommended(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            conf, sink = self._live_cfg(tmp)
            state, log = tmp / "s.json", tmp / "w.jsonl"
            beats = self._beats(tmp, [worker(idle_min=45)])
            base = ["--heartbeats", str(beats), "--config", str(conf),
                    "--state", str(state), "--log", str(log)]
            first = run_cli(*base, "--now", "2026-09-14T12:00:00Z")
            self.assertEqual(first.returncode, 0)
            self.assertIn("NUDGED", first.stdout)
            second = run_cli(*base, "--now", "2026-09-14T12:40:00Z")
            self.assertEqual(second.returncode, 1)
            self.assertIn("RECOMMENDED", second.stdout)
            self.assertEqual(sink.read_text(encoding="utf-8").splitlines(),
                             ["task_w d-task_w"], "exactly one nudge sent")
            events = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([e["event"] for e in events], ["nudge", "recommend"])
            for ev in events:
                for key in ("ts", "run_id", "worker_id", "dispatch_id",
                            "classification", "evidence"):
                    self.assertIn(key, ev)
            self.assertEqual(events[0]["run_id"], "run_live")
            self.assertEqual(events[1]["classification"], "HUNG")
            self.assertGreaterEqual(events[1]["evidence"]["idle_s"], 1800)

    def test_live_mode_without_transport_refuses(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            beats = self._beats(tmp, [worker(idle_min=45)])
            proc = run_cli("--heartbeats", str(beats), "--config", str(CONFIG),
                           "--state", str(tmp / "s.json"), "--log", str(tmp / "w.jsonl"))
            self.assertEqual(proc.returncode, 2)
            self.assertIn("nudge_command", proc.stderr)

    def test_nudge_transport_failure_is_exit_2_not_a_logged_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            conf = tmp / "w.json"
            conf.write_text(json.dumps({"nudge_command": ["sh", "-c", "exit 3"]}))
            log = tmp / "w.jsonl"
            beats = self._beats(tmp, [worker(idle_min=45)])
            proc = run_cli("--heartbeats", str(beats), "--config", str(conf),
                           "--state", str(tmp / "s.json"), "--log", str(log),
                           "--now", "2026-09-14T12:00:00Z")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("NUDGE-FAILED", proc.stderr)
            self.assertFalse(log.exists(), "a failed nudge must not be logged as sent")


if __name__ == "__main__":
    unittest.main()
