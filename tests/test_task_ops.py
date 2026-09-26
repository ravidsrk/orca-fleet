#!/usr/bin/env python3
"""Contract tests for runtime/scripts/task_ops.py (S2).

task-create + task-update lifecycle flags as one fail-closed tool: status
keyset, deps/result JSON shape, and nonempty ids are validated before any
orca call (exit 2, zero side effects); receipts are parsed fail-closed
(exit 1 when the runtime refuses or the receipt is unreadable).
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "task_ops.py"


def load():
    spec = importlib.util.spec_from_file_location("task_ops", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(args, env_extra=None, payload=None):
    with tempfile.TemporaryDirectory() as tmp:
        resp = Path(tmp) / "resp.json"
        resp.write_text(json.dumps(payload if payload is not None else {
            "result": {"task": {"id": "task_1", "status": "pending"}}}))
        log = Path(tmp) / "calls.log"
        stub = Path(tmp) / "orca"
        stub.write_text(f'#!/bin/sh\nprintf \'%s\\n\' "$*" >> "{log}"\ncat "{resp}"\n')
        stub.chmod(0o755)
        env = {"PATH": f"{tmp}:/usr/bin:/bin"}
        env.update(env_extra or {})
        p = subprocess.run(["python3", str(SCRIPT), *args], env=env,
                           capture_output=True, text=True)
        calls = log.read_text() if log.exists() else ""
        return p.returncode, p.stdout, p.stderr, calls


class TestCreateArgv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_create_argv_full(self):
        argv = self.m.build_create_argv(self.m.parse_args(
            ["create", "--spec", "do it", "--task-title", "T",
             "--display-name", "D", "--deps", '["a"]', "--parent", "p",
             "--run", "r", "--from", "h", "--retry-request", "q"]))
        self.assertEqual(argv, ["orchestration", "task-create", "--spec", "do it",
                                "--task-title", "T", "--display-name", "D",
                                "--deps", '["a"]', "--parent", "p",
                                "--run", "r", "--from", "h",
                                "--retry-request", "q"])

    def test_create_minimal(self):
        argv = self.m.build_create_argv(self.m.parse_args(["create", "--spec", "s"]))
        self.assertEqual(argv, ["orchestration", "task-create", "--spec", "s"])

    def test_empty_spec_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_create_argv(self.m.parse_args(["create", "--spec", ""]))

    def test_non_array_deps_refused(self):
        for bad in ("nope", '{"a":1}', '["ok",7]', ""):
            with self.subTest(bad=bad), self.assertRaises(self.m.Refused):
                self.m.build_create_argv(self.m.parse_args(
                    ["create", "--spec", "s", "--deps", bad]))

    def test_empty_optionals_refused(self):
        for flag in ("--task-title", "--display-name", "--parent", "--run",
                     "--from", "--retry-request"):
            with self.subTest(flag=flag), self.assertRaises(self.m.Refused):
                self.m.build_create_argv(self.m.parse_args(
                    ["create", "--spec", "s", flag, ""]))


class TestUpdateArgv(unittest.TestCase):
    STATUSES = ("pending", "ready", "dispatched", "completed", "failed", "blocked")

    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_update_argv_full(self):
        argv = self.m.build_update_argv(self.m.parse_args(
            ["update", "--id", "t", "--status", "ready", "--result", '{"a":1}',
             "--run", "r", "--from", "h", "--retry-request", "q"]))
        self.assertEqual(argv, ["orchestration", "task-update", "--id", "t",
                                "--status", "ready", "--result", '{"a":1}',
                                "--run", "r", "--from", "h",
                                "--retry-request", "q"])

    def test_all_statuses_accepted(self):
        for status in self.STATUSES:
            argv = self.m.build_update_argv(self.m.parse_args(
                ["update", "--id", "t", "--status", status]))
            self.assertIn(status, argv)

    def test_unknown_status_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_update_argv(self.m.parse_args(
                ["update", "--id", "t", "--status", "Ready"]))

    def test_empty_id_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_update_argv(self.m.parse_args(
                ["update", "--id", "", "--status", "ready"]))

    def test_non_json_result_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_update_argv(self.m.parse_args(
                ["update", "--id", "t", "--status", "ready", "--result", "nope"]))


class TestCli(unittest.TestCase):
    def test_create_reports_id_and_status(self):
        rc, out, err, calls = run_cli(["create", "--spec", "s"])
        self.assertEqual(rc, 0, err)
        self.assertIn("CREATED=task_1", out)
        self.assertIn("STATUS=pending", out)
        self.assertIn("orchestration task-create --spec s --json", calls)

    def test_update_reports_transition(self):
        rc, out, err, calls = run_cli(
            ["update", "--id", "task_1", "--status", "ready"],
            payload={"result": {"task": {"id": "task_1", "status": "ready"}}})
        self.assertEqual(rc, 0, err)
        self.assertIn("UPDATED=task_1", out)
        self.assertIn("STATUS=ready", out)
        self.assertIn("--status ready", calls)

    def test_refusal_exits_2_with_no_call(self):
        rc, _o, err, calls = run_cli(
            ["update", "--id", "t", "--status", "bogus"])
        self.assertEqual(rc, 2, err)
        self.assertIn("REFUSED", err)
        self.assertEqual(calls, "")

    def test_error_envelope_exits_1(self):
        rc, _o, err, _c = run_cli(
            ["update", "--id", "t", "--status", "ready"],
            payload={"error": {"code": "task_not_found", "message": "no"}})
        self.assertEqual(rc, 1, err)
        self.assertIn("task_not_found", err)

    def test_receipt_without_task_is_a_failure(self):
        rc, _o, err, _c = run_cli(["create", "--spec", "s"],
                                  payload={"result": {}})
        self.assertEqual(rc, 1, err)
        self.assertIn("FAILED", err)


if __name__ == "__main__":
    unittest.main()
