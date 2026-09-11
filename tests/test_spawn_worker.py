#!/usr/bin/env python3
"""Contract tests for runtime/scripts/spawn_worker.sh (issues #43, #44; v5 re-pin).

The hardening tests exercise the real script through its SW_SELFTEST hook, which computes
the two hardened values (validated effort, collision-safe scratch key) and exits before any
orchestration side effect. The lane tests stub `orca` per subcommand and assert the v5
receipt contracts against Orca v1.4.199 — the SHIPPED tag, not upstream HEAD. Standard
library only.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPAWN = ROOT / "runtime" / "scripts" / "spawn_worker.sh"


def run(title, agent="claude", effort="high", task="task_test"):
    """Invoke spawn_worker.sh in self-test mode; return (rc, stdout, stderr)."""
    p = subprocess.run(
        ["bash", str(SPAWN), task, "active", title, agent, effort],
        env={"SW_SELFTEST": "1", "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True,
    )
    return p.returncode, p.stdout, p.stderr


def run_spawn(args, env_extra=None, task_list=None):
    """Invoke spawn_worker.sh past the selftest hook; return (rc, stdout, stderr).

    env_extra: extra env vars on top of a minimal PATH. task_list: if given, a
    stub `orca` is put on PATH whose `task-list --json` output is that payload
    (written to a file the stub cats, so no shell quoting of the JSON).
    """
    with tempfile.TemporaryDirectory() as tmp:
        env = {"PATH": "/usr/bin:/bin", "SP": tmp}
        if task_list is not None:
            payload = Path(tmp) / "task-list.json"
            payload.write_text(json.dumps(task_list))
            stub = Path(tmp) / "orca"
            stub.write_text(f'#!/bin/sh\ncat "{payload}"\n')
            stub.chmod(0o755)
            env["PATH"] = f"{tmp}:/usr/bin:/bin"
        env.update(env_extra or {})
        p = subprocess.run(
            ["bash", str(SPAWN), *args],
            env=env, capture_output=True, text=True,
        )
        return p.returncode, p.stdout, p.stderr


def task_list_payload(*tasks):
    return {"result": {"tasks": list(tasks)}}


class TestDangerSandboxEvidence(unittest.TestCase):
    """PROFILE=danger needs evidence of a sandbox, and the evidence has to be PRODUCED here.

    `ORCA_COORD_ALLOW_DANGER=1` alone said only that a coordinator meant it. A transcript the
    caller names said only that the caller could name a file: `ORCA_SANDBOX_RECIPE=root` with
    `ORCA_SANDBOX_DOCTOR=/etc/passwd` spawned a danger worker, while a real transcript reporting
    `"failures": []` was refused because the substring "fail" was in it (#283).

    So spawn_worker.sh runs `orca vm recipe doctor <recipe> --provision` itself and reads the
    verdict; ORCA_SANDBOX_DOCTOR is now where the transcript is WRITTEN.
    """

    ENV = {"PROFILE": "danger", "ORCA_COORD_ALLOW_AUTONOMOUS_WRITE": "1",
           "ORCA_COORD_ALLOW_DANGER": "1"}
    ARGS = ["t1", "wt", "some title", "claude"]

    def _spawn(self, **extra):
        env = dict(self.ENV)
        env.update(extra)
        return run_spawn(self.ARGS, env_extra=env)

    def _with_doctor(self, output, rc=0, **extra):
        """Run spawn with a stub `orca` whose `vm recipe doctor` prints `output` and exits `rc`."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "doctor-output"
            out.write_text(output, encoding="utf-8")
            stub = Path(tmp) / "orca"
            stub.write_text(
                "#!/bin/sh\n"
                'case "$*" in\n'
                f'  *"recipe doctor"*) cat "{out}"; exit {rc} ;;\n'
                '  *) echo "{}" ;;\n'
                "esac\n")
            stub.chmod(0o755)
            env = dict(self.ENV)
            env.update(extra)
            env["PATH"] = f"{tmp}:/usr/bin:/bin"
            return run_spawn(self.ARGS, env_extra=env)

    def test_the_opt_in_alone_is_refused(self):
        rc, _out, err = self._spawn()
        self.assertEqual(rc, 2, err)
        self.assertIn("ORCA_SANDBOX_RECIPE", err)

    def test_a_non_recipe_id_is_refused(self):
        rc, _out, err = self._spawn(ORCA_SANDBOX_RECIPE="ab")
        self.assertEqual(rc, 2, err)
        self.assertIn("is not a recipe id", err)

    def test_a_recipe_id_with_shell_metacharacters_is_refused(self):
        rc, _out, err = self._spawn(ORCA_SANDBOX_RECIPE="lane-7; rm -rf /")
        self.assertEqual(rc, 2, err)
        self.assertIn("is not a recipe id", err)

    def test_without_orca_the_lane_is_refused(self):
        # #283: a sandbox cannot be certified without the runtime that provides it. Before this,
        # any readable file stood in for the runtime's own verdict.
        rc, _out, err = self._spawn(ORCA_SANDBOX_RECIPE="lane-7")
        self.assertEqual(rc, 2, err)
        self.assertIn("needs `orca` on PATH", err)

    def test_a_caller_named_transcript_is_no_longer_evidence(self):
        # THE bug: ORCA_SANDBOX_RECIPE=root + ORCA_SANDBOX_DOCTOR=/etc/passwd spawned a danger
        # worker. /etc/passwd names "root" and carries neither "fail" nor "warn". With no orca on
        # PATH the lane is now refused outright, and the named file is never read as evidence.
        rc, _out, err = self._spawn(ORCA_SANDBOX_RECIPE="root",
                                    ORCA_SANDBOX_DOCTOR="/etc/passwd")
        self.assertEqual(rc, 2, err)
        self.assertIn("needs `orca` on PATH", err)
        self.assertNotIn("SPAWN=NOTE", err)

    def test_a_doctor_that_exits_nonzero_is_refused(self):
        rc, _out, err = self._with_doctor("provisioning lane-7\n", rc=3,
                                          ORCA_SANDBOX_RECIPE="lane-7")
        self.assertEqual(rc, 2, err)
        self.assertIn("did not come up clean", err)

    def test_a_transcript_for_another_recipe_is_refused(self):
        rc, _out, err = self._with_doctor('{"recipe": "other-lane", "ok": true}',
                                          ORCA_SANDBOX_RECIPE="lane-7")
        self.assertEqual(rc, 2, err)
        self.assertIn("not clear", err)

    def test_a_warn_is_refused(self):
        # sandbox-policy.md: clear means no fail AND no warn; ok:true proves nothing.
        rc, _out, err = self._with_doctor(
            '{"recipe": "lane-7", "ok": true, "warnings": ["low disk"]}',
            ORCA_SANDBOX_RECIPE="lane-7")
        self.assertEqual(rc, 2, err)
        self.assertIn("no fail AND no warn", err)

    def test_a_fail_is_refused(self):
        rc, _out, err = self._with_doctor(
            '{"recipe": "lane-7", "ok": false, "checks": [{"name": "net", "status": "fail"}]}',
            ORCA_SANDBOX_RECIPE="lane-7")
        self.assertEqual(rc, 2, err)
        self.assertIn("no fail AND no warn", err)

    def test_an_empty_findings_list_is_clear(self):
        # The other half of #283: a REAL clear transcript says `"failures": []`, and the old
        # substring grep refused it for containing "fail".
        rc, _out, err = self._with_doctor(
            '{"recipe": "lane-7", "ok": true, "failures": [], "warnings": []}',
            ORCA_SANDBOX_RECIPE="lane-7")
        self.assertIn("doctored clear by this script", err)
        self.assertNotIn("sandbox", err.split("doctored clear by this script")[1])

    def test_a_clear_text_transcript_passes_the_gate(self):
        rc, _out, err = self._with_doctor("recipe lane-7 ok:true\n0 warnings, no failures\n",
                                          ORCA_SANDBOX_RECIPE="lane-7")
        self.assertIn("doctored clear by this script", err)
        self.assertNotIn("sandbox", err.split("doctored clear by this script")[1])

    def test_the_transcript_is_written_where_the_ledger_wants_it(self):
        # ORCA_SANDBOX_DOCTOR inverted: an OUTPUT path for the lane ledger, not a trusted input.
        with tempfile.TemporaryDirectory() as out_dir:
            dest = Path(out_dir) / "lane-7-doctor.json"
            payload = '{"recipe": "lane-7", "ok": true, "failures": []}'
            rc, _out, err = self._with_doctor(payload, ORCA_SANDBOX_RECIPE="lane-7",
                                              ORCA_SANDBOX_DOCTOR=str(dest))
            self.assertIn("doctored clear by this script", err)
            self.assertTrue(dest.is_file(), "the doctor transcript was not recorded")
            self.assertIn("lane-7", dest.read_text(encoding="utf-8"))

    def test_an_unwritable_ledger_path_is_refused(self):
        rc, _out, err = self._with_doctor('{"recipe": "lane-7", "ok": true, "failures": []}',
                                          ORCA_SANDBOX_RECIPE="lane-7",
                                          ORCA_SANDBOX_DOCTOR="/nonexistent-dir/doctor.json")
        self.assertEqual(rc, 2, err)
        self.assertIn("could not write the doctor transcript", err)

    def test_ro_and_rw_do_not_need_a_sandbox_recipe(self):
        for profile, opt_in in (("ro", {}), ("rw", {"ORCA_COORD_ALLOW_AUTONOMOUS_WRITE": "1"})):
            env = {"PROFILE": profile}
            env.update(opt_in)
            _rc, _out, err = run_spawn(self.ARGS, env_extra=env)
            self.assertNotIn("ORCA_SANDBOX_RECIPE", err, profile)


class TestSpawnWorkerHardening(unittest.TestCase):

    def test_scratch_key_distinguishes_tr_colliding_titles(self):
        # #44: "Fix: a/b" and "Fix: a\\b" both tr-squash to the same name; the raw-title
        # checksum must keep their scratch keys distinct so parallel spawns don't clobber.
        _, out_a, _ = run("Fix: a/b")
        _, out_b, _ = run("Fix: a\\b")
        key_a = next(l for l in out_a.splitlines() if l.startswith("safe_title="))
        key_b = next(l for l in out_b.splitlines() if l.startswith("safe_title="))
        self.assertNotEqual(key_a, key_b,
                            "tr-colliding titles must yield distinct scratch keys")

    def test_invalid_effort_is_refused(self):
        # #43: effort is interpolated into the codex launch command; an unknown value must
        # be rejected (fail closed), never interpolated verbatim. Same strict contract as
        # the other refusals (#173): exit 2 with the SPAWN=REFUSED marker.
        rc, _, err = run("t", effort='high"; touch /tmp/pwned; echo "')
        self.assertEqual(rc, 2, f"expected exit 2, got {rc}; stderr: {err}")
        self.assertIn("SPAWN=REFUSED", err)
        self.assertIn("invalid effort", err)

    def test_valid_effort_accepted(self):
        for eff in ("minimal", "low", "medium", "high", "xhigh"):
            rc, out, _ = run("t", effort=eff)
            self.assertEqual(rc, 0, f"valid effort {eff} should pass")
            self.assertIn(f"effort={eff}", out)


class TestSpawnWorkerRefusals(unittest.TestCase):
    """#173: every SPAWN=REFUSED branch must exit 2 with the marker on stderr.

    These run PAST the SW_SELFTEST hook — the refusal gates are the only thing
    between a fat-fingered coordinator invocation and an autonomous
    permission-bypass worker, so deleting one must turn this suite red.
    """

    BASE_ARGS = ["task_test", "path:/tmp/wt", "t"]

    def assert_refused(self, rc, err, needle):
        self.assertEqual(rc, 2, f"expected exit 2, got {rc}; stderr: {err}")
        self.assertIn("SPAWN=REFUSED", err)
        self.assertIn(needle, err)

    def test_unknown_agent_refused(self):
        rc, _, err = run_spawn(self.BASE_ARGS + ["bogus"])
        self.assert_refused(rc, err, "unknown agent 'bogus'")

    def test_unknown_profile_refused(self):
        rc, _, err = run_spawn(self.BASE_ARGS, env_extra={"PROFILE": "bogus"})
        self.assert_refused(rc, err, "unknown PROFILE='bogus'")

    def test_rw_without_optin_refused(self):
        # rw is the default profile; a bare invocation must fail closed.
        rc, _, err = run_spawn(self.BASE_ARGS)
        self.assert_refused(rc, err, "ORCA_COORD_ALLOW_AUTONOMOUS_WRITE=1")

    def test_danger_without_optin_refused(self):
        rc, _, err = run_spawn(self.BASE_ARGS, env_extra={"PROFILE": "danger"})
        self.assert_refused(rc, err, "ORCA_COORD_ALLOW_DANGER=1")

    def test_cmd_override_without_optin_refused(self):
        rc, _, err = run_spawn(
            self.BASE_ARGS,
            env_extra={"PROFILE": "ro", "WORKER_CMD": "echo hi"},
        )
        self.assert_refused(rc, err, "ORCA_COORD_ALLOW_CMD_OVERRIDE=1")

    def test_grok_ro_no_verified_flag_refused(self):
        # grok has no read-only mode in Orca's flag map and no WORKER_CMD given.
        rc, _, err = run_spawn(
            self.BASE_ARGS + ["grok"], env_extra={"PROFILE": "ro"},
        )
        self.assert_refused(rc, err, "no verified PROFILE=ro launch flag")

    def test_pending_without_mark_ready_refused(self):
        rc, _, err = run_spawn(
            self.BASE_ARGS, env_extra={"PROFILE": "ro"},
            task_list=task_list_payload({"id": "task_test", "status": "pending"}),
        )
        self.assert_refused(rc, err, "status=pending")

    def test_pending_unreadable_deps_refused(self):
        # deps present but not parseable JSON must fail closed, not count as none.
        rc, _, err = run_spawn(
            ["--mark-ready"] + self.BASE_ARGS, env_extra={"PROFILE": "ro"},
            task_list=task_list_payload(
                {"id": "task_test", "status": "pending", "deps": "not-json"}),
        )
        self.assert_refused(rc, err, "deps metadata unreadable")

    def test_pending_unmet_deps_refused(self):
        rc, _, err = run_spawn(
            ["--mark-ready"] + self.BASE_ARGS, env_extra={"PROFILE": "ro"},
            task_list=task_list_payload(
                {"id": "task_test", "status": "pending", "deps": ["dep1"]},
                {"id": "dep1", "status": "pending"}),
        )
        self.assert_refused(rc, err, "unmet_deps=1")

    def test_task_not_found_refused(self):
        rc, _, err = run_spawn(
            self.BASE_ARGS, env_extra={"PROFILE": "ro"},
            task_list=task_list_payload(),
        )
        self.assert_refused(rc, err, "not found in task-list")

    def test_non_ready_status_refused(self):
        rc, _, err = run_spawn(
            self.BASE_ARGS, env_extra={"PROFILE": "ro"},
            task_list=task_list_payload({"id": "task_test", "status": "in_progress"}),
        )
        self.assert_refused(rc, err, "only ready")


class TestSpawnWorkerV5Lanes(unittest.TestCase):
    """v5 (2026-09-10 upstream re-pin, source-witnessed at v1.4.199).

    The v4 lane shipped three false mechanisms: a blind re-Enter/heartbeat loop on a preamble
    `--inject` had ALREADY submitted, four of ten refusal codes handled, and a `terminal wait`
    result nobody read. Each of those is a way to put a second writer on a live worktree, so
    deleting any assertion below must turn this suite red.
    """

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

    def _stub(self, tmp, *, receipt=None, ws_rc=0, inject=None, wait=None,
              preamble=None, send=None, send_rc=0):
        """Stub orca per subcommand. Each payload is written to a file the stub cats, so no
        JSON ever passes through shell quoting."""
        files = {
            "task-list.json": task_list_payload({"id": "task_test", "status": "ready"}),
            "receipt.json": receipt if receipt is not None else self.READY_RECEIPT,
            "inject.json": inject if inject is not None else {
                "result": {"dispatch": {"id": "ctx_x"}, "injected": True,
                           "prompt": {"requestId": "req_1", "stages": ["input_accepted",
                                                                      "turn_started"],
                                      "provider": "claude", "observation": "supported"}}},
            "wait.json": wait if wait is not None else {"result": {"wait": {"satisfied": True}}},
            "preamble.json": preamble if preamble is not None else {
                "result": {"dispatch": {"id": "ctx_x"}, "preamble": "PREAMBLE BODY"}},
            "send.json": send if send is not None else {
                "result": {"send": {"accepted": True,
                                    "prompt": {"requestId": "req_1",
                                               "stages": ["input_accepted", "turn_started"]}}}},
            "terminal-create.json": {"result": {"terminal": {"handle": "term_shell1"}}},
        }
        for name, payload in files.items():
            (Path(tmp) / name).write_text(json.dumps(payload))
        log = Path(tmp) / "orca-calls.log"
        stub = Path(tmp) / "orca"
        stub.write_text(f"""#!/bin/sh
printf '%s\\n' "$*" >> "{log}"
case "$*" in
  *task-list*)          cat "{tmp}/task-list.json" ;;
  *worker-start*)       cat "{tmp}/receipt.json"; exit {ws_rc} ;;
  *dispatch-show*)      cat "{tmp}/preamble.json" ;;
  *dispatch*--inject*)  cat "{tmp}/inject.json" ;;
  *terminal\\ create*)   cat "{tmp}/terminal-create.json" ;;
  *terminal\\ wait*)     cat "{tmp}/wait.json" ;;
  *terminal\\ send*)     cat "{tmp}/send.json"; exit {send_rc} ;;
  *)                    printf '%s' '{{"result": {{}}}}' ;;
esac
""")
        stub.chmod(0o755)
        return log

    def _run(self, tmp, args, env_extra=None):
        env = {"PATH": f"{tmp}:/usr/bin:/bin", "SP": tmp,
               "SETTLE_SECS": "0", "SUBMIT_SECS": "1"}
        env.update(env_extra or {})
        return subprocess.run(["bash", str(SPAWN), *args], env=env,
                              capture_output=True, text=True)

    RW = {"PROFILE": "rw", "ORCA_COORD_ALLOW_AUTONOMOUS_WRITE": "1"}
    RO = {"PROFILE": "ro"}
    ARGS = ["task_test", "path:/tmp/wt", "t"]

    # --- (a) custom-argv lane: receipted sends, no blind Enter ---------------------------

    def test_no_blind_enter_and_no_loop(self):
        # §7 item 2: `dispatch --inject` ALREADY submits the preamble, so a bare
        # `terminal send --enter` is a stray keystroke outside the receipt model, and the guide's
        # rule is "never resend on silence". The lane must issue NO --enter send at all when the
        # receipt already carries turn_started, and must never poll dispatch-show for a heartbeat.
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp)
            p = self._run(tmp, self.ARGS, self.RO)
            self.assertEqual(p.returncode, 0, p.stderr)
            calls = log.read_text()
            self.assertNotIn("terminal send", calls,
                             "a receipt carrying turn_started needs no send at all")
            self.assertNotIn("dispatch-show", calls,
                             "the heartbeat poll loop is gone; the receipt is the verdict")
            self.assertIn("STAGES=input_accepted,turn_started", p.stdout)
            self.assertIn("HANDLE=term_shell1", p.stdout)

    def test_input_accepted_only_is_exit_3_unproven(self):
        # `accepted: true` proves input acceptance, NOT a started turn. With no requestId there is
        # nothing to replay, so the lane must report UNPROVEN — never resend, never respawn.
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp, inject={"result": {"injected": True, "prompt": {
                "requestId": "", "stages": ["input_accepted"]}}})
            p = self._run(tmp, self.ARGS, self.RO)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            self.assertIn("STAGES=input_accepted", p.stdout)
            self.assertIn("SPAWN=UNPROVEN", p.stderr)
            self.assertIn("--screen", p.stderr,
                          "exit 3 must name the runtime's own inspection command")
            self.assertNotIn("terminal send", log.read_text(),
                             "no replay is possible without a requestId — and no resend either")

    def test_missing_turn_start_replays_receipt_exactly_once(self):
        # The replay is `terminal send --retry-request <id> --wait-submit <s>`: it REPLAYS the
        # recorded receipt and never resends. v1.4.199 also requires --text with --enter, so the
        # exact preamble is recovered with `dispatch-show --preamble` first.
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp, inject={"result": {"injected": True, "prompt": {
                "requestId": "req_1", "stages": ["input_accepted"]}}})
            p = self._run(tmp, self.ARGS, self.RO)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            sends = [l for l in log.read_text().splitlines() if "terminal send" in l]
            self.assertEqual(len(sends), 1, f"exactly one replay, never a loop: {sends}")
            self.assertIn("--retry-request req_1", sends[0])
            self.assertIn("--wait-submit", sends[0])
            self.assertIn("--text", sends[0])
            self.assertIn("dispatch-show --task task_test --preamble", log.read_text())
            self.assertIn("STAGES=input_accepted,turn_started", p.stdout)

    def test_replay_refusal_never_falls_back_to_resend(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp, inject={"result": {"injected": True, "prompt": {
                "requestId": "req_1", "stages": ["input_accepted"]}}},
                send={"error": {"code": "incompatible_runtime"}}, send_rc=1)
            p = self._run(tmp, self.ARGS, self.RO)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            self.assertIn("SPAWN=REPLAY_REFUSED", p.stderr)
            sends = [l for l in log.read_text().splitlines() if "terminal send" in l]
            self.assertEqual(len(sends), 1, "a refused replay is never retried or downgraded")

    # --- (c) terminal wait: read wait.satisfied ------------------------------------------

    def test_unsatisfied_wait_fails_closed_on_the_field(self):
        # v4 failed closed only because the CLI also sets exit 1 for this case. Read the field.
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp, wait={"result": {"wait": {"satisfied": False}}})
            p = self._run(tmp, self.ARGS, self.RO)
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("wait.satisfied=false", p.stderr)
            self.assertNotIn("--inject", log.read_text(),
                             "a preamble must never be injected into a pane that never went idle")

    def test_absent_wait_field_is_not_a_false(self):
        # An older host that omits the field is absence, not a negative verdict.
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp, wait={"result": {}})
            p = self._run(tmp, self.ARGS, self.RO)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    # --- (b) supervised lane: every typed refusal, nextSteps, outcome_unknown -------------

    POLICY_CODES = ["task_not_found", "task_not_startable", "inject_rejected",
                    "nested_worker_depth_exceeded", "consumer_fenced", "dispatch_inactive"]

    def test_every_typed_refusal_is_exit_2_with_next_steps(self):
        # v4 whitelisted four codes; task_not_found / inject_rejected / runtime_error fell through
        # to "spawn failed" and were retried as transport errors. Branch on error.code.
        for code in self.POLICY_CODES:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                self._stub(tmp, ws_rc=1, receipt={"error": {
                    "code": code, "message": "refused",
                    "data": {"nextSteps": [f"do the {code} thing", "then this"]}}})
                p = self._run(tmp, self.ARGS, self.RW)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("SPAWN=REFUSED", p.stderr)
                self.assertIn(code, p.stderr)
                self.assertIn(f"nextStep: do the {code} thing", p.stderr,
                              "error.data.nextSteps is the runtime's own recovery text and is "
                              "surfaced verbatim")
                self.assertIn("nextStep: then this", p.stderr)

    def test_runtime_error_is_exit_1_not_a_policy_refusal(self):
        # runtime_error is the documented catch-all: "do not retry unchanged".
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp, ws_rc=1, receipt={"error": {
                "code": "runtime_error", "message": "boom",
                "data": {"nextSteps": ["read the message"]}}})
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("SPAWN=FAILED", p.stderr)
            self.assertIn("runtime_error", p.stderr)
            self.assertIn("nextStep: read the message", p.stderr)

    def test_refusal_without_data_still_branches(self):
        # Older hosts may omit `data` entirely — every field is optional.
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp, ws_rc=1, receipt={"error": {"code": "consumer_fenced"}})
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("consumer_fenced", p.stderr)

    def test_nonzero_call_with_unparseable_receipt_fails_closed(self):
        # A missing binary / truncated write / unknown response shape exits nonzero with nothing
        # the parser can object to. That must READ AS FAILURE, never as ready — a fail-open here
        # would report a worker that was never started.
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp, ws_rc=127, receipt={})
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("SPAWN=FAILED", p.stderr)
            self.assertNotIn("READY=", p.stdout)

    def test_outcome_unknown_is_exit_4_with_next_commands(self):
        # The next release returns this for an unobserved turn start. It is NOT a failure: a
        # respawn here puts a second writer beside a possibly-live pane (the 2026-07-15 class).
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp, ws_rc=1, receipt={"result": {
                "taskId": "task_test", "dispatchId": "ctx_x",
                "state": "outcome_unknown", "stage": "turn_start_unobserved",
                "effects": [{"kind": "terminal", "role": "agent", "id": "term_agent1"}],
                "nextCommands": [
                    "orca orchestration worker-show --dispatch ctx_x --json",
                    "orca orchestration worker-abandon --dispatch ctx_x --json"]}})
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
            self.assertIn("SPAWN=OUTCOME_UNKNOWN", p.stderr)
            self.assertIn("nextCommand: orca orchestration worker-show --dispatch ctx_x", p.stderr)
            self.assertIn("nextCommand: orca orchestration worker-abandon --dispatch ctx_x",
                          p.stderr)
            self.assertRegex(p.stderr, r"(?i)never\s+respawn")
            self.assertIn("HANDLE=term_agent1", p.stdout)

    # --- (e) launch.effective -------------------------------------------------------------

    def test_launch_effective_is_printed_when_present(self):
        # Never claim a permission flag, model, or effort from the REQUESTED args alone.
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp)
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("LAUNCH_EFFECTIVE=", p.stdout)
            self.assertIn("--dangerously-skip-permissions", p.stdout)

    def test_launch_effective_absent_is_not_invented(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp, receipt={"result": {
                "taskId": "task_test", "dispatchId": "ctx_x", "state": "ready",
                "effects": [{"kind": "terminal", "role": "agent", "id": "term_agent1"}]}})
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertNotIn("LAUNCH_EFFECTIVE=", p.stdout)

    # --- (d) roster: cursor in, kilo deliberately out --------------------------------------

    def test_cursor_is_on_the_roster_for_write_tiers(self):
        # Orca maps cursor to --yolo (tui-agent-permissions.ts:21 at v1.4.199); v4 excluded it.
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp)
            p = self._run(tmp, self.ARGS + ["cursor"], self.RW)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("--agent cursor", log.read_text())

    def test_cursor_ro_has_no_verified_flag(self):
        # Orca has no read-only mode for cursor — fail closed, exactly like grok.
        rc, _, err = run_spawn(self.ARGS + ["cursor"], env_extra={"PROFILE": "ro"})
        self.assertEqual(rc, 2, err)
        self.assertIn("no verified PROFILE=ro launch flag", err)

    def test_kilo_stays_off_the_roster(self):
        # Orca STRIPS --dangerously-skip-permissions from kilo as it does from opencode
        # (tui-agent-launch-defaults.ts:5-8), so kilo must not silently launch a prompting worker.
        rc, _, err = run_spawn(self.ARGS + ["kilo"], env_extra=dict(self.RW))
        self.assertEqual(rc, 2, err)
        self.assertIn("unknown agent 'kilo'", err)

    # --- lane contracts carried forward from v3/v4 (still true at v1.4.199) ----------------

    def test_worker_start_lane_omits_name_on_existing_worktree(self):
        # Creation flags (--name et al.) are rejected for current/existing worktrees.
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp)
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 0, p.stderr)
            ws_call = next(l for l in log.read_text().splitlines() if "worker-start" in l)
            self.assertNotIn("--name", ws_call)
            self.assertIn("--task task_test", ws_call)

    def test_worker_start_lane_names_new_child_worktrees(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp)
            p = self._run(tmp, ["task_test", "new-child", "t"], self.RW)
            self.assertEqual(p.returncode, 0, p.stderr)
            ws_call = next(l for l in log.read_text().splitlines() if "worker-start" in l)
            self.assertIn("--name", ws_call)

    def test_ro_never_takes_worker_start(self):
        # A worker-start launch takes its args from the host's agentDefaultArgs, whose migrated
        # default is the YOLO map — a PROFILE=ro reviewer must never ride it.
        with tempfile.TemporaryDirectory() as tmp:
            log = self._stub(tmp)
            p = self._run(tmp, self.ARGS, self.RO)
            self.assertEqual(p.returncode, 0, p.stderr)
            calls = log.read_text()
            self.assertNotIn("worker-start", calls)
            self.assertIn("--permission-mode plan", calls)

    def test_flat_receipt_parses_handle_from_effects(self):
        # The receipt is flat; the agent terminal is effects[kind=terminal, role=agent].
        with tempfile.TemporaryDirectory() as tmp:
            self._stub(tmp)
            p = self._run(tmp, self.ARGS, self.RW)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("HANDLE=term_agent1", p.stdout)
            self.assertIn("DISPATCH=ctx_x", p.stdout)


if __name__ == "__main__":
    unittest.main()
