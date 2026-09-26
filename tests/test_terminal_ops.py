#!/usr/bin/env python3
"""Contract tests for runtime/scripts/terminal_ops.py (S9/S18).

terminal create (--shell keyset + --focus) and read (--screen/--cursor
exclusivity + older-host refusal mirroring the upstream handler), plus the
read-only list/show inventory. Mutating verbs (close/rename/split/switch/
stop/send/wait) are PARKED and stay out of this tool.
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "terminal_ops.py"

SHELLS = ("cmd.exe", "powershell.exe", "pwsh.exe", "wsl.exe", "bash.exe",
          "git-bash")

SUMMARY = {"handle": "term_1", "ptyId": "pty_1", "worktreeId": "w1",
           "worktreePath": "/w", "branch": "main", "tabId": "t",
           "leafId": "l", "title": "RUNNER", "connected": True,
           "writable": True, "lastOutputAt": 1, "preview": "hi"}


def load():
    spec = importlib.util.spec_from_file_location("terminal_ops", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(args, payload=None):
    with tempfile.TemporaryDirectory() as tmp:
        resp = Path(tmp) / "resp.json"
        resp.write_text(json.dumps(payload if payload is not None else {
            "result": {"terminal": {"handle": "term_1"}}}))
        log = Path(tmp) / "calls.log"
        stub = Path(tmp) / "orca"
        stub.write_text(f'#!/bin/sh\nprintf \'%s\\n\' "$*" >> "{log}"\ncat "{resp}"\n')
        stub.chmod(0o755)
        env = {"PATH": f"{tmp}:/usr/bin:/bin"}
        p = subprocess.run(["python3", str(SCRIPT), *args], env=env,
                           capture_output=True, text=True)
        calls = log.read_text() if log.exists() else ""
        return p.returncode, p.stdout, p.stderr, calls


class TestCreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_argv_full(self):
        argv = self.m.build_argv(self.m.parse_args(
            ["create", "--worktree", "path:/w", "--title", "R",
             "--command", "codex", "--shell", "pwsh.exe", "--focus"]))
        self.assertEqual(argv, ["terminal", "create", "--worktree", "path:/w",
                                "--title", "R", "--command", "codex",
                                "--shell", "pwsh.exe", "--focus"])

    def test_all_shells_accepted(self):
        for shell in SHELLS:
            argv = self.m.build_argv(self.m.parse_args(
                ["create", "--shell", shell]))
            self.assertIn(shell, argv)

    def test_unknown_shell_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(
                ["create", "--shell", "fish"]))

    def test_empty_command_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(
                ["create", "--command", ""]))

    def test_cli_create_reports_handle(self):
        rc, out, err, calls = run_cli(["create", "--command", "codex"])
        self.assertEqual(rc, 0, err)
        self.assertIn("HANDLE=term_1", out)
        self.assertIn('terminal create --command codex --json', calls)

    def test_cli_create_without_handle_is_a_failure(self):
        rc, _o, err, _c = run_cli(["create"],
                                  payload={"result": {"terminal": {}}})
        self.assertEqual(rc, 1, err)
        self.assertIn("FAILED", err)


class TestRead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_argv(self):
        argv = self.m.build_argv(self.m.parse_args(
            ["read", "--terminal", "t", "--cursor", "42", "--limit", "100"]))
        self.assertEqual(argv, ["terminal", "read", "--terminal", "t",
                                "--cursor", "42", "--limit", "100"])

    def test_screen_and_cursor_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(
                ["read", "--screen", "--cursor", "42"]))

    def test_non_integer_cursor_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(["read", "--cursor", "-1"]))

    def test_screen_source_certified(self):
        lines = self.m.format_read({"handle": "t", "source": "screen",
                                    "tail": ["frame"], "truncated": False},
                                   want_screen=True)
        self.assertIn("SOURCE=screen", lines)
        self.assertIn("frame", lines)

    def test_screen_with_absent_source_is_an_older_host_failure(self):
        # Upstream refuses with incompatible_runtime; the wrapper fails closed
        # the same way (exit 1: orca WAS invoked, so this is not a usage
        # refusal) rather than handing back the other question's answer.
        with self.assertRaises(self.m.Failed) as ctx:
            self.m.format_read({"handle": "t"}, want_screen=True)
        self.assertIn("older host", str(ctx.exception))

    def test_screen_unavailable_is_degraded_not_certified(self):
        with self.assertRaises(self.m.Failed) as ctx:
            self.m.format_read({"handle": "t", "source": "screen-unavailable"},
                               want_screen=True)
        self.assertIn("screen-unavailable", str(ctx.exception))

    def test_stream_read_without_screen_passes(self):
        lines = self.m.format_read({"handle": "t", "source": "stream",
                                    "tail": ["$ ok"], "truncated": False},
                                   want_screen=False)
        self.assertIn("SOURCE=stream", lines)

    def test_read_prints_bounded_tail(self):
        lines = self.m.format_read(
            {"handle": "t", "source": "stream", "truncated": True,
             "tail": ["$ deploy", "done"]}, want_screen=False)
        self.assertIn("SOURCE=stream", lines)
        self.assertIn("TRUNCATED=yes", lines)
        self.assertIn("$ deploy", lines)
        self.assertIn("done", lines)

    def test_tail_prints_inert(self):
        lines = self.m.format_read(
            {"handle": "t", "source": "stream", "truncated": False,
             "tail": ["$ ok", "\x1b[2Kcls"]}, want_screen=False)
        joined = "\n".join(lines)
        self.assertIn("\\x1b", joined)
        self.assertNotIn("\x1b", joined)

    def test_read_without_tail_fails_closed(self):
        with self.assertRaises(self.m.Failed) as ctx:
            self.m.format_read({"handle": "t", "source": "stream",
                                "truncated": False}, want_screen=False)
        self.assertIn("names no tail", str(ctx.exception))

    def test_cli_read_screen(self):
        rc, out, err, calls = run_cli(
            ["read", "--terminal", "term_1", "--screen"],
            payload={"result": {"terminal": {"handle": "term_1",
                                             "source": "screen",
                                             "tail": ["frame"],
                                             "truncated": False}}})
        self.assertEqual(rc, 0, err)
        self.assertIn("SOURCE=screen", out)
        self.assertIn("--screen", calls)


class TestInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    ROWS = {"terminals": [SUMMARY,
                          dict(SUMMARY, handle="term_2", title="OTHER")],
            "totalCount": 2, "truncated": False}

    def test_list_argv(self):
        argv = self.m.build_argv(self.m.parse_args(
            ["list", "--worktree", "active", "--limit", "10",
             "--include-visual-layouts"]))
        self.assertEqual(argv, ["terminal", "list", "--worktree", "active",
                                "--limit", "10", "--include-visual-layouts"])

    def test_show_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(["show", "--terminal", "t"])),
            ["terminal", "show", "--terminal", "t"])
        self.assertEqual(self.m.build_argv(self.m.parse_args(["show"])),
                         ["terminal", "show"])

    def test_list_format(self):
        lines = self.m.format_list(self.ROWS)
        self.assertIn("ROWS=2", lines)
        self.assertIn("TRUNCATED=no", lines)
        self.assertIn("term_1 RUNNER", lines)

    def test_show_format(self):
        lines = self.m.format_show({"terminal": SUMMARY})
        self.assertIn("HANDLE=term_1", lines)
        self.assertIn("TITLE=RUNNER", lines)

    def test_title_prints_inert(self):
        lines = self.m.format_list(
            {"terminals": [{"handle": "t", "title": "\x1b[2Kx"}],
             "truncated": False})
        joined = "\n".join(lines)
        self.assertIn("\\x1b", joined)
        self.assertNotIn("\x1b", joined)

    def test_cli_list(self):
        rc, out, err, calls = run_cli(["list"],
                                      payload={"result": self.ROWS})
        self.assertEqual(rc, 0, err)
        self.assertIn("ROWS=2", out)
        self.assertIn("terminal list --json", calls)


class TestCliFailures(unittest.TestCase):
    def test_refusal_exits_2_with_no_call(self):
        rc, _o, err, calls = run_cli(["create", "--shell", "fish"])
        self.assertEqual(rc, 2, err)
        self.assertIn("REFUSED", err)
        self.assertEqual(calls, "")

    def test_error_envelope_exits_1(self):
        rc, _o, err, _c = run_cli(
            ["show", "--terminal", "t"],
            payload={"error": {"code": "terminal_gone", "message": "gone"}})
        self.assertEqual(rc, 1, err)
        self.assertIn("terminal_gone", err)


if __name__ == "__main__":
    unittest.main()
