#!/usr/bin/env python3
"""Contract tests for runtime/scripts/hitl_ask.py (S4).

Durable `orchestration ask` for the hitl loop: exactly one of
--question/--resume (mirroring the upstream handler), --options only for
new questions, --timeout-ms in 1..1800000, and the ORCA_TERMINAL_HANDLE
--from assertion. Answers print verbatim; timeouts report HITL_RESUME for
the rerun instead of losing the question.
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "hitl_ask.py"

ANSWERED = {"answer": "yes — flaked twice", "messageId": "msg_3",
            "threadId": "th_1", "timedOut": False}
TIMED_OUT = {"answer": None, "messageId": "msg_4", "threadId": "th_1",
             "timedOut": True, "timeoutMs": 1000}


def load():
    spec = importlib.util.spec_from_file_location("hitl_ask", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(args, env_extra=None, payload=None):
    with tempfile.TemporaryDirectory() as tmp:
        resp = Path(tmp) / "resp.json"
        resp.write_text(json.dumps(payload if payload is not None else {
            "result": ANSWERED}))
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


class TestArgv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def build(self, args, env=None):
        return self.m.build_argv(self.m.parse_args(args), env or {})

    def test_question_argv(self):
        self.assertEqual(self.build(["--question", "did it flake?"]),
                         ["orchestration", "ask", "--question", "did it flake?"])

    def test_resume_argv(self):
        self.assertEqual(self.build(["--resume", "msg_4"]),
                         ["orchestration", "ask", "--resume", "msg_4"])

    def test_full_argv(self):
        argv = self.build(["--question", "q", "--to", "run:r1", "--run", "r1",
                          "--options", "y,n", "--timeout-ms", "60000",
                          "--from", "term_9"])
        self.assertEqual(argv, ["orchestration", "ask", "--question", "q",
                                "--to", "run:r1", "--run", "r1",
                                "--options", "y,n", "--timeout-ms", "60000",
                                "--from", "term_9"])

    def test_neither_or_both_refused(self):
        with self.assertRaises(self.m.Refused):
            self.build([])
        with self.assertRaises(self.m.Refused):
            self.build(["--question", "q", "--resume", "m"])

    def test_env_resume_counts_as_resume(self):
        argv = self.build([], {"HITL_RESUME": "msg_4"})
        self.assertIn("--resume", argv)
        with self.assertRaises(self.m.Refused):
            self.build(["--question", "q"], {"HITL_RESUME": "msg_4"})

    def test_options_with_resume_refused(self):
        with self.assertRaises(self.m.Refused):
            self.build(["--resume", "m", "--options", "y,n"])
        with self.assertRaises(self.m.Refused):
            self.build([], {"HITL_RESUME": "m", "HITL_ASK_OPTIONS": "y,n"})

    def test_bad_timeout_refused(self):
        for bad in ("abc", "0", "-5", "1800001"):
            with self.subTest(bad=bad), self.assertRaises(self.m.Refused):
                self.build(["--question", "q", "--timeout-ms", bad])
        argv = self.build(["--question", "q", "--timeout-ms", "1800000"])
        self.assertIn("1800000", argv)

    def test_env_timeout_validated(self):
        with self.assertRaises(self.m.Refused):
            self.build(["--question", "q"], {"HITL_ASK_TIMEOUT_MS": "huge"})

    def test_env_defaults_applied(self):
        argv = self.build(["--question", "q"],
                         {"HITL_ASK_TO": "run:r", "HITL_ASK_OPTIONS": "y,n",
                          "HITL_ASK_TIMEOUT_MS": "5000"})
        for flag in ("--to", "run:r", "--options", "y,n", "--timeout-ms",
                     "5000"):
            self.assertIn(flag, argv)

    def test_from_assertion(self):
        argv = self.build(["--question", "q"],
                         {"ORCA_TERMINAL_HANDLE": "term_9"})
        self.assertIn("term_9", argv)
        with self.assertRaises(self.m.Refused):
            self.build(["--question", "q", "--from", "other"],
                       {"ORCA_TERMINAL_HANDLE": "term_9"})

    def test_empty_question_refused(self):
        with self.assertRaises(self.m.Refused):
            self.build(["--question", ""])


class TestCli(unittest.TestCase):
    def test_answer_prints_verbatim(self):
        rc, out, err, calls = run_cli(["--question", "did it flake?"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(out, "yes — flaked twice\n")
        self.assertIn("orchestration ask --question did it flake? --json",
                      calls)

    def test_timeout_reports_resume_id(self):
        rc, _o, err, _c = run_cli(["--question", "q"],
                                  payload={"result": TIMED_OUT})
        self.assertEqual(rc, 1, err)
        self.assertIn("HITL_ASK_TIMEOUT=yes", err)
        self.assertIn("HITL_RESUME=msg_4", err)
        self.assertIn("--resume msg_4", err)

    def test_timeout_without_id_still_fails(self):
        payload = dict(TIMED_OUT, messageId=None)
        rc, _o, err, _c = run_cli(["--question", "q"],
                                  payload={"result": payload})
        self.assertEqual(rc, 1, err)
        self.assertIn("HITL_RESUME=none", err)

    def test_null_answer_without_timeout_is_a_failure(self):
        payload = {"answer": None, "messageId": "m", "threadId": "t",
                   "timedOut": False}
        rc, _o, err, _c = run_cli(["--question", "q"],
                                  payload={"result": payload})
        self.assertEqual(rc, 1, err)
        self.assertIn("FAILED", err)

    def test_refusal_exits_2_with_no_call(self):
        rc, _o, err, calls = run_cli(["--question", "q", "--resume", "m"])
        self.assertEqual(rc, 2, err)
        self.assertIn("REFUSED", err)
        self.assertEqual(calls, "")

    def test_error_envelope_exits_1(self):
        rc, _o, err, _c = run_cli(
            ["--question", "q"],
            payload={"error": {"code": "timeout", "message": "slow"}})
        self.assertEqual(rc, 1, err)
        self.assertIn("timeout", err)


if __name__ == "__main__":
    unittest.main()
