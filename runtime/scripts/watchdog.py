#!/usr/bin/env python3
"""Liveness watchdog: mechanized first response from runtime/worker-supervision.md.

The 2026-09-14 clean-sweep tracker run handled every stuck worker by hand: a
reviewer hung 60+ min with a transcript frozen 20+ min (nudged, unanswered,
stopped), a verdict worker wedged on a dead provider stream (nudged,
unanswered, stopped), four builders wedged on a provider-exhaustion dialog
(stopped + relaunched), and a reviewer stuck on a permission dialog with sends
blocked twice (stopped + re-dispatched). This script mechanizes the policy's
two highest-frequency responses — liveness watch and auto-nudge — and leaves
the expensive ones (stop, re-dispatch) as coordinator decisions.

Detection criteria (all thresholds from runtime/watchdog.json, tunable without
code edits; --help prints the effective values):

* OK:   last movement within slow_after_s. No action.
* SLOW: idle past slow_after_s but short of hung_after_s and its STOP.
  Slow-but-alive is not stuck: no action.
* HUNG: idle past hung_after_s, OR past its per-dispatch STOP with no report
  (the policy: past-STOP silence is STUCK, not slow). First response is one
  auto-nudge; still-HUNG after max_nudges_per_dispatch nudges escalates to a
  stop-redispatch RECOMMENDATION.
* WEDGED: positive wedge evidence — an explicit wedge marker (wedge_markers:
  e.g. send_blocked, provider_stream_dead, dialog_block, provider_exhausted),
  OR a transcript frozen past wedge_frozen_s beyond STOP plus an unanswered
  nudge (the policy's presence-not-absence test). Nudging a wedged worker is
  futile, so WEDGED recommends stop-redispatch immediately and never nudges.

Rate limits (anti-flap: a worker oscillating HUNG/OK must not cause a nudge
storm): at most max_nudges_per_dispatch nudges per dispatch, at least
nudge_window_s between nudges to one worker, and at most
max_nudges_per_hour_per_worker per worker per hour. Nudge history persists in
the state file so the limits hold across invocations.

Modes:

* --dry-run classifies and prints WOULD-nudge / WOULD-recommend with zero side
  effects: no subprocess, no state write, no log append. This is the mode CI
  and cautious coordinators use.
* live mode performs nudges by exec'ing nudge_command (argv placeholders
  {run_id} {worker_id} {dispatch_id} {text}; substituted per argv item, never
  through a shell) and appends every nudge/recommendation as JSONL carrying
  run id, worker id, dispatch id, timestamps, and the cited evidence. Live
  mode refuses to run without a nudge transport configured: a nudge the
  script cannot send must not be logged as sent.

Exit codes
    0  tick completed, nothing needs the coordinator
    1  tick completed, at least one stop-redispatch recommendation (or, under
       --dry-run, at least one WOULD-recommend)
    2  could not run — unreadable heartbeats/config/state, unknown config key,
       live mode without nudge_command, or a nudge transport failure
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "watchdog.json"
DEFAULT_STATE = Path(".orca") / "watchdog-state.json"
DEFAULT_LOG = Path(".orca") / "watchdog.jsonl"

DEFAULTS = {
    "slow_after_s": 600,
    "hung_after_s": 1800,
    "wedge_frozen_s": 1200,
    "max_nudges_per_dispatch": 1,
    "nudge_window_s": 3600,
    "max_nudges_per_hour_per_worker": 1,
    "nudge_text": "finish-or-report now.",
    "nudge_command": None,
}

# Terminal values mean the worker is settled or dead: liveness-resume.md owns
# the dead, not this script. Anything else counts as alive.
SETTLED = {"exited", "completed", "failed", "stopped", "released", "settled"}

PLACEHOLDERS = ("run_id", "worker_id", "dispatch_id", "text")


def utcnow():
    return datetime.now(timezone.utc)


def parse_ts(value, field):
    """ISO-8601 (Z or offset) or epoch seconds -> aware UTC datetime."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            raise ValueError(f"{field}: not a timestamp: {value!r}")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    raise ValueError(f"{field}: not a timestamp: {value!r}")


def load_config(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read config {path}: {exc}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config {path} is not JSON: {exc}")
    if not isinstance(data, dict):
        raise ConfigError(f"config {path} must be a JSON object")
    unknown = sorted(k for k in data if not k.startswith("_") and k not in DEFAULTS)
    if unknown:
        raise ConfigError(f"config {path}: unknown key(s): {', '.join(unknown)}")
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in data.items() if not k.startswith("_")})
    for key in ("slow_after_s", "hung_after_s", "wedge_frozen_s",
                "max_nudges_per_dispatch", "nudge_window_s",
                "max_nudges_per_hour_per_worker"):
        if not isinstance(cfg[key], (int, float)) or cfg[key] < 0:
            raise ConfigError(f"config {path}: {key} must be a non-negative number")
    if cfg["nudge_command"] is not None and (
            not isinstance(cfg["nudge_command"], list)
            or not cfg["nudge_command"]
            or not all(isinstance(a, str) for a in cfg["nudge_command"])):
        raise ConfigError(f"config {path}: nudge_command must be a non-empty argv list or null")
    if not isinstance(cfg["nudge_text"], str) or not cfg["nudge_text"].strip():
        raise ConfigError(f"config {path}: nudge_text must be a non-empty string")
    return cfg


class ConfigError(Exception):
    pass


class HeartbeatError(Exception):
    pass


def load_heartbeats(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise HeartbeatError(f"cannot read heartbeats {path}: {exc}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HeartbeatError(f"heartbeats {path} is not JSON: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("workers"), list):
        raise HeartbeatError(f"heartbeats {path} must be an object with a workers list")
    return data


def load_state(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"workers": {}}
    except OSError as exc:
        raise HeartbeatError(f"cannot read state {path}: {exc}")
    try:
        data = json.loads(raw) if raw.strip() else {"workers": {}}
    except json.JSONDecodeError as exc:
        raise HeartbeatError(f"state {path} is not JSON: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("workers", {}), dict):
        raise HeartbeatError(f"state {path} must be an object with a workers map")
    return data


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def classify(worker, now, cfg):
    """(state, evidence) for one worker heartbeat record.

    state is one of OK / SLOW / HUNG / WEDGED / SETTLED. SETTLED covers the
    dead and the released — liveness-resume.md territory; the watchdog takes
    no action on it.
    """
    wid = worker.get("worker_id", "?")
    terminal = worker.get("terminal")
    if terminal in SETTLED:
        return "SETTLED", {"terminal": terminal}
    try:
        dispatched = parse_ts(worker["dispatched_at"], "dispatched_at") \
            if worker.get("dispatched_at") else now
        last_move = parse_ts(worker["last_movement_at"], "last_movement_at") \
            if worker.get("last_movement_at") else dispatched
        stop_at = parse_ts(worker["stop_at"], "stop_at") \
            if worker.get("stop_at") else None
    except ValueError as exc:
        raise HeartbeatError(f"worker {wid}: {exc}")
    idle_s = max(0.0, (now - last_move).total_seconds())
    past_stop = bool(stop_at and now > stop_at)
    reported = bool(worker.get("reported"))
    markers = worker.get("wedge_markers") or []
    if not isinstance(markers, list) or not all(isinstance(m, str) for m in markers):
        raise HeartbeatError(f"worker {wid}: wedge_markers must be a list of strings")
    last_nudge_raw = worker.get("last_nudge_at")
    last_nudge = parse_ts(last_nudge_raw, "last_nudge_at") if last_nudge_raw else None
    nudge_answered = worker.get("last_nudge_answered")
    evidence = {
        "idle_s": round(idle_s),
        "past_stop": past_stop,
        "reported": reported,
        "wedge_markers": markers,
        "last_nudge_answered": nudge_answered,
    }
    if markers:
        return "WEDGED", evidence
    if past_stop and idle_s >= cfg["wedge_frozen_s"] and nudge_answered is False:
        evidence["wedge_basis"] = "frozen past STOP with an unanswered nudge"
        return "WEDGED", evidence
    if (past_stop and not reported) or idle_s >= cfg["hung_after_s"]:
        return "HUNG", evidence
    if idle_s >= cfg["slow_after_s"]:
        return "SLOW", evidence
    return "OK", evidence


def prior_nudge_times(worker, state_entry):
    times = []
    for raw in (worker.get("prior_nudges") or []):
        times.append(parse_ts(raw, "prior_nudges"))
    for raw in (state_entry.get("nudges") or []):
        times.append(parse_ts(raw, "state nudges"))
    return sorted(times)


def nudge_allowed(worker_id, dispatch_id, worker, state, now, cfg):
    """(allowed, reason): rate-limit check for a HUNG worker."""
    entry = state.get("workers", {}).get(worker_id, {})
    if entry.get("dispatch_id") and entry.get("dispatch_id") != dispatch_id:
        entry = {}  # a fresh dispatch resets the per-dispatch budget
    try:
        times = prior_nudge_times(worker, entry)
    except ValueError as exc:
        raise HeartbeatError(f"worker {worker_id}: {exc}")
    if len(times) >= cfg["max_nudges_per_dispatch"]:
        return False, f"nudge budget spent ({len(times)}/{cfg['max_nudges_per_dispatch']})"
    hour_ago = now.timestamp() - 3600
    recent = [t for t in times if t.timestamp() >= hour_ago]
    if len(recent) >= cfg["max_nudges_per_hour_per_worker"]:
        return False, f"hourly cap reached ({len(recent)}/{cfg['max_nudges_per_hour_per_worker']})"
    if times and (now - times[-1]).total_seconds() < cfg["nudge_window_s"]:
        wait = int(cfg["nudge_window_s"] - (now - times[-1]).total_seconds())
        return False, f"nudge window holds for {wait}s"
    return True, "within budget"


def record_nudge(state, worker_id, dispatch_id, at):
    workers = state.setdefault("workers", {})
    entry = workers.setdefault(worker_id, {"dispatch_id": dispatch_id, "nudges": []})
    if entry.get("dispatch_id") != dispatch_id:
        entry["dispatch_id"] = dispatch_id
        entry["nudges"] = []
    entry["nudges"].append(at.isoformat())


def build_nudge_argv(cfg, run_id, worker_id, dispatch_id):
    values = {"run_id": run_id, "worker_id": worker_id,
              "dispatch_id": dispatch_id, "text": cfg["nudge_text"]}
    argv = []
    for item in cfg["nudge_command"]:
        for name in PLACEHOLDERS:
            item = item.replace("{" + name + "}", values[name])
        argv.append(item)
    return argv


def decide(worker, now, cfg, state):
    """Pure decision: (classification, action, evidence, note).

    action is one of none / nudge / recommend. decide() never sends, writes,
    or mutates — the caller applies the action. SETTLED workers get none.
    """
    wid = worker.get("worker_id", "?")
    dispatch_id = worker.get("dispatch_id", "?")
    classification, evidence = classify(worker, now, cfg)
    if classification in ("OK", "SLOW", "SETTLED"):
        return classification, "none", evidence, "slow-but-alive is not stuck"
    if classification == "WEDGED":
        return classification, "recommend", evidence, \
            "wedged: stop + re-dispatch fresh (coordinator decision)"
    allowed, reason = nudge_allowed(wid, dispatch_id, worker, state, now, cfg)
    if allowed:
        return classification, "nudge", evidence, reason
    return classification, "recommend", evidence, \
        f"still HUNG, nudge withheld ({reason}): stop + re-dispatch fresh"


def tick(data, now, cfg, state):
    """Decide every worker in a heartbeat snapshot. Pure: no IO."""
    run_id = data.get("run_id", "?")
    results = []
    for worker in data["workers"]:
        classification, action, evidence, note = decide(worker, now, cfg, state)
        results.append({
            "run_id": run_id,
            "worker_id": worker.get("worker_id", "?"),
            "dispatch_id": worker.get("dispatch_id", "?"),
            "classification": classification,
            "action": action,
            "evidence": evidence,
            "note": note,
        })
    return results


def send_nudge(cfg, run_id, worker_id, dispatch_id):
    argv = build_nudge_argv(cfg, run_id, worker_id, dispatch_id)
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    except OSError as exc:
        return False, f"nudge transport failed to start: {exc}"
    except subprocess.TimeoutExpired:
        return False, "nudge transport timed out after 120s"
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return False, f"nudge transport exited {proc.returncode}: {tail[-1] if tail else '?'}"
    return True, "sent"


def append_jsonl(path, event):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def run_tick(args, cfg, data, state, now):
    """Apply one tick: print classifications, perform live side effects.

    Returns the process exit code. Under --dry-run this performs zero side
    effects: no subprocess, no state write, no log append.
    """
    results = tick(data, now, cfg, state)
    exit_code = 0
    for res in results:
        action = res["action"]
        if action == "recommend":
            exit_code = 1
        if args.dry_run:
            shown = {"nudge": "WOULD-NUDGE", "recommend": "WOULD-RECOMMEND"}.get(
                action, "none")
            print(f"{res['worker_id']} {res['classification']} {shown} :: {res['note']}")
            continue
        if action == "none":
            print(f"{res['worker_id']} {res['classification']} none :: {res['note']}")
            continue
        if action == "nudge":
            ok, detail = send_nudge(cfg, res["run_id"], res["worker_id"], res["dispatch_id"])
            if not ok:
                print(f"{res['worker_id']} HUNG NUDGE-FAILED :: {detail}", file=sys.stderr)
                return 2
            record_nudge(state, res["worker_id"], res["dispatch_id"], now)
            append_jsonl(args.log, {
                "ts": now.isoformat(), "run_id": res["run_id"],
                "worker_id": res["worker_id"], "dispatch_id": res["dispatch_id"],
                "event": "nudge", "classification": res["classification"],
                "detail": detail, "evidence": res["evidence"],
            })
            print(f"{res['worker_id']} {res['classification']} NUDGED :: {detail}")
        elif action == "recommend":
            append_jsonl(args.log, {
                "ts": now.isoformat(), "run_id": res["run_id"],
                "worker_id": res["worker_id"], "dispatch_id": res["dispatch_id"],
                "event": "recommend", "classification": res["classification"],
                "detail": "stop + re-dispatch fresh (coordinator decision)",
                "evidence": res["evidence"],
            })
            print(f"{res['worker_id']} {res['classification']} RECOMMENDED :: {res['note']}")
    if not args.dry_run:
        save_state(args.state, state)
    return exit_code


def build_parser():
    ap = argparse.ArgumentParser(
        description="Liveness watchdog: classify workers OK/SLOW/HUNG/WEDGED, "
                    "auto-nudge HUNG once, recommend stop-redispatch on still-HUNG "
                    "or WEDGED. Thresholds come from --config (default "
                    "runtime/watchdog.json); --help shows the effective values.")
    ap.add_argument("--heartbeats", required=True,
                    help="JSON snapshot: {run_id, workers: [{worker_id, dispatch_id, "
                         "dispatched_at, last_movement_at, stop_at, reported, "
                         "terminal, wedge_markers, last_nudge_at, "
                         "last_nudge_answered, prior_nudges}]}")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG),
                    help="threshold/rate-limit JSON (default: runtime/watchdog.json)")
    ap.add_argument("--state", default=str(DEFAULT_STATE),
                    help="nudge-history JSON (default: .orca/watchdog-state.json)")
    ap.add_argument("--log", default=str(DEFAULT_LOG),
                    help="JSONL action log (default: .orca/watchdog.jsonl)")
    ap.add_argument("--now", default=None,
                    help="override the tick timestamp (ISO-8601); default: current time")
    ap.add_argument("--dry-run", action="store_true",
                    help="classify only: print WOULD-nudge/WOULD-recommend, change nothing")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"watchdog: {exc}", file=sys.stderr)
        return 2
    try:
        data = load_heartbeats(args.heartbeats)
        state = load_state(args.state)
        now = parse_ts(args.now, "--now") if args.now else utcnow()
    except (HeartbeatError, ValueError) as exc:
        print(f"watchdog: {exc}", file=sys.stderr)
        return 2
    if not args.dry_run and not cfg.get("nudge_command"):
        print("watchdog: live mode needs nudge_command in the config "
              "(a nudge the script cannot send must not be logged as sent); "
              "use --dry-run or configure the transport", file=sys.stderr)
        return 2
    try:
        return run_tick(args, cfg, data, state, now)
    except HeartbeatError as exc:
        print(f"watchdog: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
