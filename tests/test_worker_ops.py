#!/usr/bin/env python3
"""Contract tests for runtime/scripts/worker_ops.py (S5/S6/S7/S8/S21).

One fail-closed tool for the worker lifecycle verbs: show (minimal
agentWait/projection.nextAction consumption), read (--source validation +
transcript-evidence certification), stop/abandon (scripted fencing),
release/retain (reclaim), and list (watchdog enumeration). Refusals exit 2
with no orca call; unknown states exit 1, never a claimed verdict.
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "worker_ops.py"

SHOW_FULL = {
    "dispatch": {"id": "ctx_1", "taskId": "task_1", "status": "dispatched"},
    "worker": {"state": "running", "stage": "dispatch_input",
               "agentTerminalHandle": "term_1"},
    "projection": {"liveness": {"verdict": "healthy"},
                   "nextAction": {"argv": ["orca", "orchestration",
                                           "worker-show"]}},
    "observation": {"agentWait": {"source": "hook", "reason": "trust prompt"}},
}


def load():
    spec = importlib.util.spec_from_file_location("worker_ops", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(args, payload=None):
    with tempfile.TemporaryDirectory() as tmp:
        resp = Path(tmp) / "resp.json"
        resp.write_text(json.dumps(payload if payload is not None else {
            "result": SHOW_FULL}))
        log = Path(tmp) / "calls.log"
        stub = Path(tmp) / "orca"
        stub.write_text(f'#!/bin/sh\nprintf \'%s\\n\' "$*" >> "{log}"\ncat "{resp}"\n')
        stub.chmod(0o755)
        env = {"PATH": f"{tmp}:/usr/bin:/bin"}
        p = subprocess.run(["python3", str(SCRIPT), *args], env=env,
                           capture_output=True, text=True)
        calls = log.read_text() if log.exists() else ""
        return p.returncode, p.stdout, p.stderr, calls


class TestShow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(["show", "--dispatch", "d1"])),
            ["orchestration", "worker-show", "--dispatch", "d1"])

    def test_empty_dispatch_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(["show", "--dispatch", ""]))

    def test_full_receipt(self):
        lines = self.m.format_show(SHOW_FULL)
        self.assertIn("DISPATCH=ctx_1", lines)
        self.assertIn("STATE=running", lines)
        self.assertIn("STAGE=dispatch_input", lines)
        self.assertIn("PROJECTION_VERDICT=healthy", lines)
        self.assertIn("NEXT_ACTION=orca orchestration worker-show", lines)
        self.assertIn("AGENT_WAIT=waiting:hook:trust prompt", lines)

    def test_null_wait_is_none_absent_is_unknown(self):
        obs_none = dict(SHOW_FULL, observation={"agentWait": None})
        self.assertIn("AGENT_WAIT=none", self.m.format_show(obs_none))
        obs_absent = {k: v for k, v in SHOW_FULL.items() if k != "observation"}
        self.assertIn("AGENT_WAIT=unknown", self.m.format_show(obs_absent))
        obs_no_key = dict(SHOW_FULL, observation={})
        self.assertIn("AGENT_WAIT=unknown", self.m.format_show(obs_no_key))

    def test_absent_projection_is_absent(self):
        no_proj = {k: v for k, v in SHOW_FULL.items() if k != "projection"}
        lines = self.m.format_show(no_proj)
        self.assertIn("PROJECTION_VERDICT=absent", lines)
        self.assertIn("NEXT_ACTION=absent", lines)

    def test_cli_show(self):
        rc, out, err, calls = run_cli(["show", "--dispatch", "ctx_1"])
        self.assertEqual(rc, 0, err)
        self.assertIn("DISPATCH=ctx_1", out)
        self.assertIn("AGENT_WAIT=waiting:hook:trust prompt", out)
        self.assertIn("orchestration worker-show --dispatch ctx_1 --json", calls)


class TestRead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    TRANSCRIPT = {"dispatchId": "ctx_1", "source": "transcript",
                  "sourceIdentity": "hook:abc", "cursor": "c9",
                  "status": {"worker": "running", "terminal": "live"},
                  "fallbackReason": None}
    TERMINAL = {"dispatchId": "ctx_1", "source": "terminal",
                "sourceIdentity": "pty:1", "cursor": None,
                "status": {"worker": "running", "terminal": "live"},
                "fallbackReason": "transcript_missing"}

    def test_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["read", "--dispatch", "d1", "--source", "transcript",
                 "--cursor", "c", "--limit", "50"])),
            ["orchestration", "worker-read", "--dispatch", "d1",
             "--source", "transcript", "--cursor", "c", "--limit", "50"])

    def test_bad_source_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(
                ["read", "--dispatch", "d1", "--source", "TRANSCRIPT"]))

    def test_bad_limit_refused(self):
        for bad in ("0", "-3", "abc"):
            with self.subTest(bad=bad), self.assertRaises(self.m.Refused):
                self.m.build_argv(self.m.parse_args(
                    ["read", "--dispatch", "d1", "--limit", bad]))

    def test_transcript_evidence_certified(self):
        lines = self.m.format_read(self.TRANSCRIPT, want="transcript")
        self.assertIn("SOURCE=transcript", lines)
        self.assertIn("CURSOR=c9", lines)

    def test_terminal_when_transcript_asked_is_an_evidence_failure(self):
        with self.assertRaises(self.m.Failed):
            self.m.format_read(self.TERMINAL, want="transcript")

    def test_terminal_fallback_reason_surfaced(self):
        lines = self.m.format_read(self.TERMINAL, want="auto")
        self.assertIn("SOURCE=terminal", lines)
        self.assertIn("FALLBACK=transcript_missing", lines)

    def test_cli_read(self):
        rc, out, err, calls = run_cli(
            ["read", "--dispatch", "ctx_1", "--source", "transcript"],
            payload={"result": self.TRANSCRIPT})
        self.assertEqual(rc, 0, err)
        self.assertIn("SOURCE=transcript", out)
        self.assertIn("--source transcript", calls)


class TestFencing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_stop_and_abandon_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["stop", "--dispatch", "d1", "--retry-request", "q"])),
            ["orchestration", "worker-stop", "--dispatch", "d1",
             "--retry-request", "q"])
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["abandon", "--dispatch", "d1"])),
            ["orchestration", "worker-abandon", "--dispatch", "d1"])

    def test_release_and_retain_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["release", "--dispatch", "d1"])),
            ["orchestration", "worker-release", "--dispatch", "d1"])
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["retain", "--dispatch", "d1", "--retry-request", "q"])),
            ["orchestration", "worker-retain", "--dispatch", "d1",
             "--retry-request", "q"])

    def test_empty_dispatch_refused_everywhere(self):
        for verb in ("stop", "abandon", "release", "retain"):
            with self.subTest(verb=verb), self.assertRaises(self.m.Refused):
                self.m.build_argv(self.m.parse_args([verb, "--dispatch", ""]))

    def test_stop_unknown_is_a_failure(self):
        with self.assertRaises(self.m.Failed):
            self.m.format_fence({"dispatchId": "d", "state": "stop_unknown"},
                                unknown="stop_unknown")

    def test_release_unknown_is_a_failure(self):
        with self.assertRaises(self.m.Failed):
            self.m.format_fence({"dispatchId": "d", "state": "release_unknown"},
                                unknown="release_unknown")

    def test_settled_states_report(self):
        self.assertIn("STATE=stopped", self.m.format_fence(
            {"dispatchId": "d", "state": "stopped"}, unknown="stop_unknown"))
        self.assertIn("STATE=already_released", self.m.format_fence(
            {"dispatchId": "d", "state": "already_released"},
            unknown="release_unknown"))

    def test_cli_stop(self):
        rc, out, err, calls = run_cli(
            ["stop", "--dispatch", "ctx_1"],
            payload={"result": {"dispatchId": "ctx_1", "state": "stopped",
                                "processAction": "killed"}})
        self.assertEqual(rc, 0, err)
        self.assertIn("STATE=stopped", out)
        self.assertIn("orchestration worker-stop --dispatch ctx_1 --json", calls)


class TestList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    ROWS = {"workers": [
        {"dispatchId": "a", "taskId": "t1", "runId": "r",
         "workerState": "running", "dispatchStatus": "dispatched",
         "agentTerminalHandle": "h1", "terminalState": "active"},
        {"dispatchId": "b", "taskId": "t2", "runId": "r",
         "workerState": "settled", "dispatchStatus": "completed",
         "agentTerminalHandle": None, "terminalState": "retained"}],
        "counts": {"active": 1, "retained": 1},
        "scope": {"run": "r", "source": "bound"},
        "page": {"hasMore": False, "nextCursor": None, "total": 2}}

    def test_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["list", "--run", "r", "--terminal-state", "retained",
                 "--include-remote", "--cursor", "c", "--limit", "100"])),
            ["orchestration", "worker-list", "--run", "r",
             "--terminal-state", "retained", "--include-remote",
             "--cursor", "c", "--limit", "100"])

    def test_bad_terminal_state_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(
                ["list", "--terminal-state", "bogus"]))

    def test_limit_range_is_1_to_100(self):
        for bad in ("0", "101", "abc"):
            with self.subTest(bad=bad), self.assertRaises(self.m.Refused):
                self.m.build_argv(self.m.parse_args(["list", "--limit", bad]))
        argv = self.m.build_argv(self.m.parse_args(["list", "--limit", "1"]))
        self.assertIn("1", argv)

    def test_rows_format(self):
        lines = self.m.format_list(self.ROWS)
        self.assertIn("ROWS=2", lines)
        self.assertIn("SCOPE=bound", lines)
        self.assertIn("NEXT_CURSOR=none", lines)
        self.assertIn("a t1 active", lines)

    def test_cli_list(self):
        rc, out, err, calls = run_cli(["list", "--terminal-state", "active"],
                                      payload={"result": self.ROWS})
        self.assertEqual(rc, 0, err)
        self.assertIn("ROWS=2", out)
        self.assertIn("--terminal-state active", calls)


class TestCliFailures(unittest.TestCase):
    def test_refusal_exits_2_with_no_call(self):
        rc, _o, err, calls = run_cli(["read", "--dispatch", "d",
                                      "--source", "bogus"])
        self.assertEqual(rc, 2, err)
        self.assertIn("REFUSED", err)
        self.assertEqual(calls, "")

    def test_error_envelope_exits_1(self):
        rc, _o, err, _c = run_cli(
            ["release", "--dispatch", "d"],
            payload={"error": {"code": "stale_dispatch", "message": "old"}})
        self.assertEqual(rc, 1, err)
        self.assertIn("stale_dispatch", err)


if __name__ == "__main__":
    unittest.main()
