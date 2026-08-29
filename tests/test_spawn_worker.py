#!/usr/bin/env python3
"""Contract tests for runtime/scripts/spawn_worker.sh hardening (issues #43, #44).

These exercise the real script through its SW_SELFTEST hook, which computes the two
hardened values (validated effort, collision-safe scratch key) and exits before any
orchestration side effect. Standard library only.
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


if __name__ == "__main__":
    unittest.main()
