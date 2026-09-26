#!/usr/bin/env python3
"""Upstream-adoption contract tests for runtime/scripts/spawn_worker.sh (S1/S12/S16/S17/S20/S22).

The pinned worker-start surface carries flags the v5 lane never passed through:
--timeout-ms, --run/--from binding, --retry-of, --retry-request (+ request-show
triage of an unknown mutation result), --on, the global routing flags
(--environment/--pairing-code), ORCA_CLI_CWD, task-list scoping, and inline
task creation (--spec/--task-title/--deps/--parent). Every new flag is
fail-closed argv: validated before any orchestration side effect, refused with
exit 2 and SPAWN=REFUSED, and never interpolated unvalidated. Live routing
(--on against a paired server, --environment/--host remotes) is PARKED —
these tests pin argv + validation + hermetic receipts only.

Standard library only. The stub `orca` routes per subcommand and logs argv.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPAWN = ROOT / "runtime" / "scripts" / "spawn_worker.sh"

READY_RECEIPT = {
    "result": {
        "runId": "run_x", "taskId": "task_test", "dispatchId": "ctx_x",
        "state": "ready", "stage": "dispatch_input",
        "launch": {"requested": {"agent": "claude"},
                   "effective": {"agent": "claude", "args": "--dangerously-skip-permissions"}},
        "effects": [{"kind": "terminal", "role": "agent", "action": "created",
                     "id": "term_agent1"}],
    }
}

UNKNOWN_RECEIPT = {
    "result": {
        "runId": "run_x", "taskId": "task_test", "dispatchId": "ctx_x",
        "state": "outcome_unknown", "stage": "dispatch_input",
        "effects": [{"kind": "terminal", "role": "agent", "action": "created",
                     "id": "term_agent1"}],
        "nextCommands": ["orca orchestration worker-show --dispatch ctx_x --json"],
    }
}

RW = {"PROFILE": "rw", "ORCA_COORD_ALLOW_AUTONOMOUS_WRITE": "1"}
ARGS = ["task_test", "path:/tmp/wt", "t"]


def task_list_payload(*tasks):
    return {"result": {"tasks": list(tasks)}}


def write_stub(tmp, *, receipt=None, request_show=None, task_create=None,
               task_list=None, record_env=()):
    """Stub orca routing per subcommand; returns (log_path, env_path)."""
    tmp = Path(tmp)
    files = {
        "task-list.json": task_list if task_list is not None else task_list_payload(
            {"id": "task_test", "status": "ready"}),
        "receipt.json": receipt if receipt is not None else READY_RECEIPT,
        "task-create.json": task_create if task_create is not None else {
            "result": {"task": {"id": "task_new", "status": "pending"}}},
        "request-show.json": request_show if request_show is not None else {
            "result": {"requestId": "req_1", "state": "completed",
                       "method": "orchestration.workerStart",
                       "interpretation": "the mutation landed"}},
    }
    for name, payload in files.items():
        (tmp / name).write_text(json.dumps(payload))
    log = tmp / "orca-calls.log"
    env_rec = tmp / "orca-env.log"
    wants = " ".join(record_env)
    stub = tmp / "orca"
    stub.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> \"{log}\"\n"
        f"for v in {wants}; do eval \"printf '%s=%s\\n' \\\"$v\\\" \\\"\\${{$v:-}}\\\"\" >> \"{env_rec}\"; done\n"
        'case "$*" in\n'
        f'  *task-create*) cat "{tmp}/task-create.json" ;;\n'
        f'  *task-list*)   cat "{tmp}/task-list.json" ;;\n'
        f'  *request-show*) cat "{tmp}/request-show.json" ;;\n'
        f'  *worker-start*) cat "{tmp}/receipt.json" ;;\n'
        '  *) printf \'%s\' \'{"result": {}}\' ;;\n'
        "esac\n")
    stub.chmod(0o755)
    return log, env_rec


def run_spawn(args, env_extra=None, **stub_kw):
    with tempfile.TemporaryDirectory() as tmp:
        log, env_rec = write_stub(tmp, **stub_kw)
        env = {"PATH": f"{tmp}:/usr/bin:/bin", "SP": tmp, "SETTLE_SECS": "0"}
        env.update(env_extra or {})
        p = subprocess.run(["bash", str(SPAWN), *args], env=env,
                           capture_output=True, text=True)
        calls = log.read_text() if log.exists() else ""
        seen_env = env_rec.read_text() if env_rec.exists() else ""
        return p.returncode, p.stdout, p.stderr, calls, seen_env


def run_selftest(*args):
    p = subprocess.run(
        ["bash", str(SPAWN), *args],
        env={"SW_SELFTEST": "1", "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class TestEffortKeyset(unittest.TestCase):
    """S12: effort feeds only the codex path (-c model_reasoning_effort=); the
    codex catalog runs minimal..ultra, so max|ultra must pass and anything else
    must refuse exactly like the old keyset."""

    def test_max_and_ultra_are_accepted(self):
        for eff in ("max", "ultra"):
            rc, out, err = run_selftest("t1", "active", "t", "codex", eff)
            self.assertEqual(rc, 0, f"effort {eff}: {err}")
            self.assertIn(f"effort={eff}", out)

    def test_old_keyset_still_accepted(self):
        for eff in ("minimal", "low", "medium", "high", "xhigh"):
            rc, out, _ = run_selftest("t1", "active", "t", "codex", eff)
            self.assertEqual(rc, 0, eff)
            self.assertIn(f"effort={eff}", out)

    def test_case_and_neighbors_still_refused(self):
        # ("" is the default xhigh via `:-`, a pre-existing contract — not a refusal.)
        for eff in ("MAX", "Ultra", "xxhigh", "maxx"):
            rc, _, err = run_selftest("t1", "active", "t", "codex", eff)
            self.assertEqual(rc, 2, eff)
            self.assertIn("SPAWN=REFUSED", err)
            self.assertIn("invalid effort", err)


class TestTimeoutMs(unittest.TestCase):
    """S1: --timeout-ms passes through to worker-start only, as a positive
    integer (upstream getOptionalPositiveIntegerValueFlag)."""

    def test_timeout_passthrough_on_success(self):
        rc, out, err, calls, _ = run_spawn(
            ["--timeout-ms", "5000"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 0, err)
        self.assertIn("--timeout-ms 5000", calls)
        ws = [l for l in calls.splitlines() if "worker-start" in l]
        self.assertEqual(len(ws), 1)
        self.assertIn("--timeout-ms 5000", ws[0])
        tl = [l for l in calls.splitlines() if "task-list" in l]
        self.assertTrue(tl and all("--timeout-ms" not in l for l in tl))

    def test_timeout_missing_value_refused(self):
        rc, _, err, calls, _ = run_spawn(["--timeout-ms"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertNotIn("worker-start", calls)

    def test_timeout_non_integer_refused(self):
        for bad in ("abc", "0", "-5", "5.5", "5;evil", ""):
            with self.subTest(bad=bad):
                rc, _, err, calls, _ = run_spawn(
                    ["--timeout-ms", bad] + ARGS, env_extra=RW)
                self.assertEqual(rc, 2, bad)
                self.assertIn("SPAWN=REFUSED", err)
                self.assertIn("--timeout-ms", err)
                self.assertNotIn("worker-start", calls)


class TestRunFromBinding(unittest.TestCase):
    """S1: --run/--from scope the orchestration calls (task-list, task-update,
    worker-start) and nothing else."""

    def test_binding_reaches_orchestration_calls(self):
        rc, _o, err, calls, _ = run_spawn(
            ["--run", "run_9", "--from", "term_9"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 0, err)
        for verb in ("task-list", "worker-start"):
            lines = [l for l in calls.splitlines() if verb in l]
            self.assertTrue(lines, verb)
            for line in lines:
                self.assertIn("--run run_9", line, verb)
                self.assertIn("--from term_9", line, verb)

    def test_binding_reaches_mark_ready_update(self):
        payload = task_list_payload({"id": "task_test", "status": "pending"})
        rc, _o, err, calls, _ = run_spawn(
            ["--mark-ready", "--run", "run_9", "--from", "term_9"] + ARGS,
            env_extra=RW, task_list=payload)
        self.assertEqual(rc, 0, err)
        upd = [l for l in calls.splitlines() if "task-update" in l]
        self.assertEqual(len(upd), 1)
        self.assertIn("--run run_9", upd[0])
        self.assertIn("--from term_9", upd[0])

    def test_empty_binding_refused_before_side_effects(self):
        rc, _, err, calls, _ = run_spawn(
            ["--run", ""] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")
        rc, _, err, calls, _ = run_spawn(
            ["--from", ""] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")


class TestRetryFlags(unittest.TestCase):
    """S1: --retry-of retries a failed dispatch (needs --task); --retry-request
    is the durable mutation id for worker-start only — one id, one mutation."""

    def test_retry_of_reaches_worker_start(self):
        rc, _o, err, calls, _ = run_spawn(
            ["--retry-of", "ctx_old"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 0, err)
        ws = [l for l in calls.splitlines() if "worker-start" in l]
        self.assertEqual(len(ws), 1)
        self.assertIn("--retry-of ctx_old", ws[0])
        self.assertIn("--task task_test", ws[0])

    def test_retry_request_reaches_worker_start_only(self):
        rc, _o, err, calls, _ = run_spawn(
            ["--retry-request", "req_1"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 0, err)
        ws = [l for l in calls.splitlines() if "worker-start" in l]
        self.assertEqual(len(ws), 1)
        self.assertIn("--retry-request req_1", ws[0])
        tl = [l for l in calls.splitlines() if "task-list" in l]
        self.assertTrue(tl and all("--retry-request" not in l for l in tl))

    def test_empty_retry_ids_refused(self):
        for flag in ("--retry-of", "--retry-request"):
            rc, _, err, calls, _ = run_spawn([flag, ""] + ARGS, env_extra=RW)
            self.assertEqual(rc, 2, flag)
            self.assertIn("SPAWN=REFUSED", err)
            self.assertEqual(calls, "")


class TestRequestShowTriage(unittest.TestCase):
    """S1: an unknown mutation result with --retry-request is triaged through
    request-show (read-only): completed/pending/absent, never a second launch."""

    def test_unknown_outcome_is_triaged_completed(self):
        rc, out, err, calls, _ = run_spawn(
            ["--retry-request", "req_1"] + ARGS, env_extra=RW,
            receipt=UNKNOWN_RECEIPT)
        self.assertEqual(rc, 4, err)
        self.assertIn("request-show --request req_1", calls)
        self.assertIn("req_1", err)
        self.assertIn("completed", err)
        self.assertIn("HANDLE=term_agent1", out)

    def test_unknown_outcome_triaged_pending(self):
        rs = {"result": {"requestId": "req_1", "state": "pending",
                         "interpretation": "still running"}}
        rc, _o, err, calls, _ = run_spawn(
            ["--retry-request", "req_1"] + ARGS, env_extra=RW,
            receipt=UNKNOWN_RECEIPT, request_show=rs)
        self.assertEqual(rc, 4, err)
        self.assertIn("request-show --request req_1", calls)
        self.assertIn("pending", err)

    def test_unknown_outcome_triaged_absent(self):
        rs = {"result": {"requestId": "req_1", "state": "absent",
                         "interpretation": "no receipt"}}
        rc, _o, err, calls, _ = run_spawn(
            ["--retry-request", "req_1"] + ARGS, env_extra=RW,
            receipt=UNKNOWN_RECEIPT, request_show=rs)
        self.assertEqual(rc, 4, err)
        self.assertIn("absent", err)

    def test_ready_outcome_never_triages(self):
        rc, _o, err, calls, _ = run_spawn(
            ["--retry-request", "req_1"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("request-show", calls)

    def test_unknown_without_retry_request_never_triages(self):
        rc, _o, err, calls, _ = run_spawn(
            ARGS, env_extra=RW, receipt=UNKNOWN_RECEIPT)
        self.assertEqual(rc, 4, err)
        self.assertNotIn("request-show", calls)

    def test_triage_failure_stays_unknown(self):
        rs = {"error": {"code": "incompatible_runtime",
                        "message": "server too old"}}
        rc, _o, err, calls, _ = run_spawn(
            ["--retry-request", "req_1"] + ARGS, env_extra=RW,
            receipt=UNKNOWN_RECEIPT, request_show=rs)
        self.assertEqual(rc, 4, err)
        self.assertIn("request-show --request req_1", calls)
        self.assertIn("triage unavailable", err)


class TestOnFlag(unittest.TestCase):
    """S16: --on names the worker server for worker-start only. Remote
    current/new-child are invalid upstream, so they refuse here. Live use
    against a paired server is PARKED (no paired server in this env)."""

    def test_on_reaches_worker_start(self):
        rc, _o, err, calls, _ = run_spawn(
            ["--on", "srv_a"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 0, err)
        ws = [l for l in calls.splitlines() if "worker-start" in l]
        self.assertEqual(len(ws), 1)
        self.assertIn("--on srv_a", ws[0])

    def test_on_with_current_or_new_child_refused(self):
        for sel in ("current", "new-child"):
            with self.subTest(sel=sel):
                rc, _, err, calls, _ = run_spawn(
                    ["--on", "srv_a", "task_test", sel, "t"], env_extra=RW)
                self.assertEqual(rc, 2, sel)
                self.assertIn("SPAWN=REFUSED", err)
                self.assertIn("--on", err)
                self.assertEqual(calls, "")

    def test_empty_on_refused(self):
        rc, _, err, calls, _ = run_spawn(["--on", ""] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")


class TestGlobalRouting(unittest.TestCase):
    """S17: --environment/--pairing-code are GLOBAL, so they ride every orca
    call; --host is NOT valid on orchestration verbs (unknown-flag rejection
    upstream) so it refuses here; ORCA_CLI_CWD passes through by env."""

    def test_routing_flags_ride_every_call(self):
        rc, _o, err, calls, _ = run_spawn(
            ["--environment", "env_a", "--pairing-code", "pc_1"] + ARGS,
            env_extra=RW)
        self.assertEqual(rc, 0, err)
        # The pin-drift `orca --version` probe rides bare; every real call routes.
        lines = [l for l in calls.splitlines()
                 if l.strip() and "--version" not in l]
        self.assertGreater(len(lines), 1)
        for line in lines:
            self.assertIn("--environment env_a", line)
            self.assertIn("--pairing-code pc_1", line)

    def test_routing_disagreement_with_ambient_env_refused(self):
        rc, _, err, calls, _ = run_spawn(
            ["--environment", "env_a"] + ARGS,
            env_extra=dict(RW, ORCA_ENVIRONMENT="env_b"))
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")

    def test_routing_matching_ambient_env_allowed(self):
        rc, _o, err, _c, _e = run_spawn(
            ["--environment", "env_a"] + ARGS,
            env_extra=dict(RW, ORCA_ENVIRONMENT="env_a"))
        self.assertEqual(rc, 0, err)

    def test_host_refused_on_the_spawn_path(self):
        rc, _, err, calls, _ = run_spawn(
            ["--host", "runtime:abc"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertIn("--host", err)
        self.assertEqual(calls, "")

    def test_cli_cwd_reaches_orca_by_env(self):
        with tempfile.TemporaryDirectory() as cwd:
            rc, _o, err, _c, seen = run_spawn(
                ["--cli-cwd", cwd] + ARGS, env_extra=RW,
                record_env=("ORCA_CLI_CWD",))
            self.assertEqual(rc, 0, err)
            self.assertIn(f"ORCA_CLI_CWD={cwd}", seen)

    def test_cli_cwd_must_be_an_absolute_directory(self):
        for bad in ("relative/path", "/nonexistent-dir-xyz", ""):
            with self.subTest(bad=bad):
                rc, _, err, calls, _ = run_spawn(
                    ["--cli-cwd", bad] + ARGS, env_extra=RW)
                self.assertEqual(rc, 2, bad)
                self.assertIn("SPAWN=REFUSED", err)
                self.assertEqual(calls, "")


class TestCustomLaneRefusals(unittest.TestCase):
    """worker-start-only flags are refused (not dropped) on the custom-argv
    lane, where no worker-start runs."""

    RO = {"PROFILE": "ro"}

    def test_worker_start_flags_refused_on_ro_lane(self):
        for extra in (["--timeout-ms", "5000"], ["--on", "srv_a"],
                      ["--retry-of", "ctx_old"], ["--retry-request", "req_1"]):
            with self.subTest(extra=extra):
                rc, _, err, calls, _ = run_spawn(extra + ARGS, env_extra=self.RO)
                self.assertEqual(rc, 2, str(extra))
                self.assertIn("SPAWN=REFUSED", err)
                self.assertIn("custom-argv lane", err)
                real = [l for l in calls.splitlines() if "--version" not in l]
                self.assertEqual(real, [])

    def test_scope_flags_allowed_on_ro_lane(self):
        # --run/--from ride dispatch --inject, so they stay (no worker-start).
        rc, _, err, calls, _ = run_spawn(
            ["--run", "run_9", "--from", "term_9"] + ARGS, env_extra=self.RO)
        self.assertNotIn("SPAWN=REFUSED", err)
        _ = (rc, calls)


class TestTaskListFlags(unittest.TestCase):
    """S20: --brief is safe passthrough for the spawn-time task-list read;
    --status/--ready would hide deps and corrupt the DAG check, so they
    refuse on this path."""

    def test_brief_reaches_task_list(self):
        rc, _o, err, calls, _ = run_spawn(["--task-brief"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 0, err)
        tl = [l for l in calls.splitlines() if "task-list" in l]
        self.assertEqual(len(tl), 1)
        self.assertIn("--brief", tl[0])
        ws = [l for l in calls.splitlines() if "worker-start" in l]
        self.assertTrue(ws and all("--brief" not in l for l in ws))

    def test_status_and_ready_filters_refused(self):
        rc, _, err, calls, _ = run_spawn(
            ["--task-status", "ready"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")
        rc, _, err, calls, _ = run_spawn(["--task-ready"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")


class TestInlineCreation(unittest.TestCase):
    """S22: --spec creates the task first (task-create), then the normal
    verified path runs with the created id — the fleet DAG check needs the
    id upfront, so spawn never passes --spec straight to worker-start."""

    CREATE_TL = task_list_payload({"id": "task_new", "status": "ready"})

    def test_spec_creates_then_dispatches(self):
        rc, out, err, calls, _ = run_spawn(
            ["--spec", "do the thing", "path:/tmp/wt", "t"], env_extra=RW,
            task_list=self.CREATE_TL)
        self.assertEqual(rc, 0, err)
        tc = [l for l in calls.splitlines() if "task-create" in l]
        self.assertEqual(len(tc), 1)
        self.assertIn("--spec do the thing", tc[0])
        ws = [l for l in calls.splitlines() if "worker-start" in l]
        self.assertEqual(len(ws), 1)
        self.assertIn("--task task_new", ws[0])
        self.assertNotIn("--spec", ws[0])
        self.assertIn("DISPATCH=ctx_x", out)

    def test_creation_flags_ride_task_create(self):
        rc, _o, err, calls, _ = run_spawn(
            ["--spec", "s", "--task-title", "T", "--deps", '["d1"]',
             "--parent", "p1", "path:/tmp/wt", "t"],
            env_extra=RW, task_list=self.CREATE_TL)
        self.assertEqual(rc, 0, err)
        tc = [l for l in calls.splitlines() if "task-create" in l]
        self.assertEqual(len(tc), 1)
        for flag in ("--task-title T", '--deps ["d1"]', "--parent p1"):
            self.assertIn(flag, tc[0])

    def test_spec_with_positional_task_refused(self):
        rc, _, err, calls, _ = run_spawn(
            ["--spec", "s"] + ARGS, env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")

    def test_creation_flags_without_spec_refused(self):
        for extra in (["--task-title", "T"], ["--deps", "[]"],
                      ["--parent", "p1"]):
            with self.subTest(extra=extra):
                rc, _, err, calls, _ = run_spawn(extra + ARGS, env_extra=RW)
                self.assertEqual(rc, 2, str(extra))
                self.assertIn("SPAWN=REFUSED", err)
                self.assertEqual(calls, "")

    def test_non_array_deps_refused(self):
        for bad in ("not-json", '{"a": 1}', '["ok", 1]', '"str"', "5"):
            with self.subTest(bad=bad):
                rc, _, err, calls, _ = run_spawn(
                    ["--spec", "s", "--deps", bad, "path:/tmp/wt", "t"],
                    env_extra=RW)
                self.assertEqual(rc, 2, bad)
                self.assertIn("SPAWN=REFUSED", err)
                self.assertIn("--deps", err)
                self.assertEqual(calls, "")

    def test_empty_spec_refused(self):
        rc, _, err, calls, _ = run_spawn(
            ["--spec", "", "path:/tmp/wt", "t"], env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")

    def test_retry_of_with_spec_refused(self):
        rc, _, err, calls, _ = run_spawn(
            ["--spec", "s", "--retry-of", "ctx_old", "path:/tmp/wt", "t"],
            env_extra=RW)
        self.assertEqual(rc, 2, err)
        self.assertIn("SPAWN=REFUSED", err)
        self.assertEqual(calls, "")

    def test_create_without_an_id_is_a_failure(self):
        bad = {"result": {"task": {"status": "pending"}}}
        rc, _, err, _c, _e = run_spawn(
            ["--spec", "s", "path:/tmp/wt", "t"], env_extra=RW,
            task_create=bad, task_list=self.CREATE_TL)
        self.assertEqual(rc, 1, err)
        self.assertIn("SPAWN=FAILED", err)


if __name__ == "__main__":
    unittest.main()
