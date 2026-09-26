#!/usr/bin/env python3
"""Contract tests for runtime/scripts/hitl-loop.template.sh.

The diagnosis playbook promises this template; a promise a repo does not keep is
a documentation bug with a tooling cost. These tests pin the two things a
template must guarantee before anyone copies it: it runs end to end without a
human (``--dry-run``), and it is bounded, so a non-reproducing bug stops instead
of asking forever.
"""
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HITL = ROOT / "runtime" / "scripts" / "hitl-loop.template.sh"


def run(*args, stdin=""):
    return subprocess.run(["sh", str(HITL), *args], input=stdin,
                          capture_output=True, text=True, timeout=30)


class TestDryRun(unittest.TestCase):
    def test_dry_run_completes_without_a_human(self):
        r = run("--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_dry_run_prints_the_captured_block(self):
        r = run("--dry-run")
        self.assertIn("--- captured", r.stdout)
        self.assertIn("ERRORED=", r.stdout)
        self.assertIn("ERROR_MSG=", r.stdout)

    def test_dry_run_reaches_the_not_reproduced_terminal(self):
        r = run("--dry-run")
        self.assertIn("REPRODUCED=no", r.stdout)
        self.assertIn("ROUNDS_USED=3", r.stdout)

    def test_dry_run_shows_every_step_instruction(self):
        r = run("--dry-run")
        self.assertIn(">>> ", r.stdout)
        self.assertIn("CHECKPOINT", r.stdout)

    def test_the_loop_is_bounded_by_rounds(self):
        r = run("--dry-run", "--rounds", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("round 1 of 1", r.stdout)
        self.assertNotIn("round 2", r.stdout)
        self.assertIn("ROUNDS_USED=1", r.stdout)

    def test_more_rounds_run_more_times(self):
        r = run("--dry-run", "--rounds", "2")
        self.assertIn("round 1 of 2", r.stdout)
        self.assertIn("round 2 of 2", r.stdout)

    def test_output_is_key_value_parseable(self):
        r = run("--dry-run", "--rounds", "1")
        pairs = dict(
            line.split("=", 1) for line in r.stdout.splitlines()
            if "=" in line and not line.startswith(" ") and line.split("=", 1)[0].isupper()
        )
        self.assertIn("ERRORED", pairs)
        self.assertIn("REPRODUCED", pairs)
        self.assertEqual(pairs["REPRODUCED"], "no")


class TestInteractivePath(unittest.TestCase):
    def test_a_yes_answer_stops_at_the_first_round(self):
        # step consumes a line, then two captures: "", "y", "boom".
        r = run(stdin="\ny\nboom\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("REPRODUCED=yes", r.stdout)
        self.assertIn("ERROR_MSG=boom", r.stdout)
        self.assertNotIn("round 2", r.stdout)

    def test_a_no_answer_moves_to_the_next_round(self):
        r = run("--rounds", "2", stdin="\nn\nnone\n\n\nn\nnone\n\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("round 2 of 2", r.stdout)
        self.assertIn("REPRODUCED=no", r.stdout)

    def test_closed_stdin_does_not_hang(self):
        r = run("--rounds", "1", stdin="")
        self.assertEqual(r.returncode, 0, r.stderr)


class TestUsage(unittest.TestCase):
    def test_help_exits_zero_and_documents_the_helpers(self):
        r = run("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("step ", r.stdout)
        self.assertIn("capture ", r.stdout)
        self.assertIn("--dry-run", r.stdout)

    def test_an_unknown_argument_is_a_usage_error(self):
        r = run("--nope")
        self.assertEqual(r.returncode, 2)
        self.assertIn("unknown argument", r.stderr)

    def test_a_non_numeric_round_count_is_a_usage_error(self):
        r = run("--rounds", "many")
        self.assertEqual(r.returncode, 2)


class TestScriptShape(unittest.TestCase):
    def test_executable_and_shebanged(self):
        self.assertTrue(os.access(HITL, os.X_OK))
        self.assertTrue(HITL.read_text(encoding="utf-8").startswith("#!/usr/bin/env sh"))

    def test_stays_within_the_template_budget(self):
        lines = HITL.read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 60, "a template nobody reads is a template nobody edits")

    def test_posix_and_bash_syntax_both_parse(self):
        for shell in ("sh", "bash"):
            with self.subTest(shell=shell):
                r = subprocess.run([shell, "-n", str(HITL)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_it_marks_where_to_edit(self):
        text = HITL.read_text(encoding="utf-8")
        self.assertIn("EDIT BELOW", text)
        self.assertIn("EDIT ABOVE", text)

    def test_it_says_the_captured_text_is_data(self):
        self.assertIn("it is DATA", HITL.read_text(encoding="utf-8"))


class TestDurableAsk(unittest.TestCase):
    """S4: HITL_ASK=1 replaces capture's shell read with durable
    `orchestration ask` (hitl_ask.py), resuming timeouts via HITL_RESUME."""

    ASK_HELPER = ROOT / "runtime" / "scripts" / "hitl_ask.py"

    def run_ask(self, *args, env_extra=None, payload=None, stdin="\n\n\n\n"):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            resp = Path(tmp) / "ask.json"
            resp.write_text(json.dumps(payload if payload is not None else {
                "result": {"answer": "yes — reproduced", "messageId": "m1",
                           "threadId": "t1", "timedOut": False}}))
            log = Path(tmp) / "calls.log"
            stub = Path(tmp) / "orca"
            stub.write_text(
                f'#!/bin/sh\nprintf \'%s\\n\' "$*" >> "{log}"\ncat "{resp}"\n')
            stub.chmod(0o755)
            env = {"PATH": f"{tmp}:/usr/bin:/bin",
                   "HITL_ASK": "1",
                   "HITL_ASK_HELPER": str(self.ASK_HELPER)}
            env.update(env_extra or {})
            import os
            full = dict(os.environ)
            full.update(env)
            r = subprocess.run(["sh", str(HITL), *args], input=stdin,
                               capture_output=True, text=True, timeout=60,
                               env=full)
            calls = log.read_text() if log.exists() else ""
            return r, calls

    def test_answers_come_from_ask_not_stdin(self):
        r, calls = self.run_ask("--rounds", "1", stdin="\n\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("yes — reproduced", r.stdout)
        self.assertIn("orchestration ask --question", calls)

    def test_dry_run_never_calls_ask(self):
        r, calls = self.run_ask("--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(calls, "")

    def test_missing_helper_is_a_usage_error(self):
        r, _ = self.run_ask("--rounds", "1",
                            env_extra={"HITL_ASK_HELPER": "/nonexistent/ask.py"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("HITL_ASK_HELPER", r.stderr)

    def test_timeout_reports_resume_and_exits_1(self):
        r, _ = self.run_ask(
            "--rounds", "1",
            payload={"result": {"answer": None, "messageId": "msg_9",
                                "threadId": "t1", "timedOut": True}})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("HITL_RESUME=msg_9", r.stderr)

    def test_resume_answers_the_first_capture_only(self):
        # The template asks two questions per round; HITL_RESUME must resume
        # the first and let the second ask fresh.
        r, calls = self.run_ask("--rounds", "1",
                                env_extra={"HITL_RESUME": "msg_9"})
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = [l for l in calls.splitlines() if "orchestration ask" in l]
        self.assertEqual(len(lines), 2, calls)
        self.assertIn("--resume msg_9", lines[0])
        self.assertNotIn("--resume", lines[1])
        self.assertIn("--question", lines[1])

    def test_resume_at_targets_the_timed_out_capture(self):
        # A timeout after the first capture resumes THAT capture; earlier
        # captures re-ask fresh instead of receiving the wrong answer.
        r, calls = self.run_ask(
            "--rounds", "1",
            env_extra={"HITL_RESUME": "msg_9", "HITL_RESUME_AT": "2"})
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = [l for l in calls.splitlines() if "orchestration ask" in l]
        self.assertEqual(len(lines), 2, calls)
        self.assertIn("--question", lines[0])
        self.assertNotIn("--resume", lines[0])
        self.assertIn("--resume msg_9", lines[1])

    def test_timeout_names_its_capture_number(self):
        r, _ = self.run_ask(
            "--rounds", "1",
            payload={"result": {"answer": None, "messageId": "msg_9",
                                "threadId": "t1", "timedOut": True}})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("HITL_RESUME=msg_9", r.stderr)
        self.assertIn("capture 1", r.stderr)
        self.assertIn("HITL_RESUME_AT=1", r.stderr)

    def test_non_numeric_resume_at_is_a_usage_error(self):
        r, _ = self.run_ask("--rounds", "1",
                            env_extra={"HITL_RESUME_AT": "second"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("HITL_RESUME_AT must be a number", r.stderr)

    def test_bad_timeout_is_a_usage_error(self):
        r, calls = self.run_ask("--rounds", "1",
                                env_extra={"HITL_ASK_TIMEOUT_MS": "huge"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(calls, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
