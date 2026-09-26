#!/usr/bin/env python3
"""Contract tests for runtime/scripts/check_reply.py (S3).

check/reply as one fail-closed invoker: at most one read mode
(--unread/--peek/--all, mirroring the upstream handler), --types against
the orchestration type keyset, positive-int --timeout-ms, and the
ORCA_TERMINAL_HANDLE --from assertion. Refusals exit 2 with no orca call;
receipts parse fail-closed.
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "check_reply.py"

TYPES = ("status", "dispatch", "worker_done", "merge_ready", "escalation",
         "handoff", "decision_gate", "question", "heartbeat")


def load():
    spec = importlib.util.spec_from_file_location("check_reply", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(args, env_extra=None, payload=None):
    with tempfile.TemporaryDirectory() as tmp:
        resp = Path(tmp) / "resp.json"
        resp.write_text(json.dumps(payload if payload is not None else {
            "result": {"messages": [], "count": 0, "deliveryId": None}}))
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


class TestCheckArgv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_check_argv_full(self):
        argv = self.m.build_check_argv(self.m.parse_args(
            ["check", "--terminal", "t", "--run", "r", "--ack", "d1",
             "--peek", "--types", "worker_done,escalation", "--format",
             "--wait", "--timeout-ms", "5000", "--retry-request", "q"]))
        self.assertEqual(argv, ["orchestration", "check", "--terminal", "t",
                                "--run", "r", "--ack", "d1", "--peek",
                                "--types", "worker_done,escalation", "--format",
                                "--wait", "--timeout-ms", "5000",
                                "--retry-request", "q"])

    def test_each_read_mode_alone(self):
        for mode in ("--unread", "--peek", "--all"):
            argv = self.m.build_check_argv(self.m.parse_args(["check", mode]))
            self.assertIn(mode, argv)

    def test_two_read_modes_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_check_argv(self.m.parse_args(
                ["check", "--unread", "--peek"]))

    def test_unknown_type_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_check_argv(self.m.parse_args(
                ["check", "--types", "worker_done,bogus"]))

    def test_empty_type_member_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_check_argv(self.m.parse_args(
                ["check", "--types", "worker_done,"]))

    def test_all_types_accepted(self):
        argv = self.m.build_check_argv(self.m.parse_args(
            ["check", "--types", ",".join(TYPES)]))
        self.assertIn(",".join(TYPES), argv)

    def test_bad_timeout_refused(self):
        for bad in ("abc", "0", "-1", "1.5"):
            with self.subTest(bad=bad), self.assertRaises(self.m.Refused):
                self.m.build_check_argv(self.m.parse_args(
                    ["check", "--wait", "--timeout-ms", bad]))


class TestReplyArgv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_reply_argv(self):
        argv = self.m.build_reply_argv(self.m.parse_args(
            ["reply", "--id", "m1", "--body", "ack", "--run", "r"]))
        self.assertEqual(argv, ["orchestration", "reply", "--id", "m1",
                                "--body", "ack", "--run", "r"])

    def test_empty_id_or_body_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_reply_argv(self.m.parse_args(
                ["reply", "--id", "", "--body", "b"]))
        with self.assertRaises(self.m.Refused):
            self.m.build_reply_argv(self.m.parse_args(
                ["reply", "--id", "m", "--body", ""]))

    def test_from_defaults_to_env_handle(self):
        argv = self.m.build_reply_argv(
            self.m.parse_args(["reply", "--id", "m", "--body", "b"]),
            env={"ORCA_TERMINAL_HANDLE": "term_9"})
        self.assertIn("--from", argv)
        self.assertIn("term_9", argv)

    def test_from_mismatch_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_reply_argv(
                self.m.parse_args(["reply", "--id", "m", "--body", "b",
                                   "--from", "term_other"]),
                env={"ORCA_TERMINAL_HANDLE": "term_9"})


class TestCli(unittest.TestCase):
    def test_check_reports_count(self):
        rc, out, err, calls = run_cli(
            ["check", "--peek"],
            payload={"result": {"messages": [{"id": "m1"}], "count": 1,
                                "deliveryId": "d9", "runId": "run_1"}})
        self.assertEqual(rc, 0, err)
        self.assertIn("COUNT=1", out)
        self.assertIn("DELIVERY=d9", out)
        self.assertIn("orchestration check --peek --json", calls)

    def test_check_prints_bounded_bodies(self):
        rc, out, err, _c = run_cli(
            ["check", "--peek"],
            payload={"result": {"messages": [
                {"id": "m1", "type": "question", "from_handle": "term_a",
                 "subject": "need input", "body": "which region?"},
                {"id": "m2", "type": "worker_done", "from_handle": "term_b",
                 "subject": "done", "body": "shipped"}], "count": 2,
                "deliveryId": "d9"}})
        self.assertEqual(rc, 0, err)
        self.assertIn("--- m1 (question) from term_a", out)
        self.assertIn("SUBJ: need input", out)
        self.assertIn("which region?", out)
        self.assertIn("--- m2 (worker_done) from term_b", out)

    def test_long_body_truncated_with_marker(self):
        rc, out, err, _c = run_cli(
            ["check", "--peek"],
            payload={"result": {"messages": [
                {"id": "m1", "body": "x" * 2500}], "count": 1,
                "deliveryId": "d9"}})
        self.assertEqual(rc, 0, err)
        self.assertIn("[truncated 500 chars]", out)
        self.assertNotIn("x" * 2500, out)

    def test_malformed_message_skipped_with_warn(self):
        rc, out, err, _c = run_cli(
            ["check", "--peek"],
            payload={"result": {"messages": [
                {"id": "m1", "body": "ok"}, "junk"], "count": 2,
                "deliveryId": "d9"}})
        self.assertEqual(rc, 0, err)
        self.assertIn("--- m1 (?) from ?", out)
        self.assertIn("WARN: skipped 1 malformed message", err)

    def test_check_timeout_is_a_receipt_not_a_failure(self):
        rc, out, err, _c = run_cli(
            ["check", "--wait", "--timeout-ms", "100"],
            payload={"result": {"messages": [], "count": 0,
                                "deliveryId": None, "timedOut": True}})
        self.assertEqual(rc, 0, err)
        self.assertIn("TIMED_OUT=yes", out)

    def test_reply_reports_message(self):
        rc, out, err, calls = run_cli(["reply", "--id", "m1", "--body", "got it"])
        self.assertEqual(rc, 0, err)
        self.assertIn("m1", out)
        self.assertIn("orchestration reply --id m1 --body got it --json", calls)

    def test_refusal_exits_2_with_no_call(self):
        rc, _o, err, calls = run_cli(["check", "--peek", "--all"])
        self.assertEqual(rc, 2, err)
        self.assertIn("REFUSED", err)
        self.assertEqual(calls, "")

    def test_error_envelope_exits_1(self):
        rc, _o, err, _c = run_cli(
            ["reply", "--id", "m1", "--body", "b"],
            payload={"error": {"code": "sender_not_assignee", "message": "no"}})
        self.assertEqual(rc, 1, err)
        self.assertIn("sender_not_assignee", err)


if __name__ == "__main__":
    unittest.main()
