#!/usr/bin/env python3
"""Contract tests for runtime/scripts/worktree_ops.py (S10).

worktree list/show with selector validation: the `active`/`current`
shortcuts and the documented prefixed forms (identity:|id:|name:|
branch:|issue:|path:|folder:|worktree:) pass; bare paths, unknown
prefixes, and empty remainders refuse with exit 2 before any orca call.
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "worktree_ops.py"

ROW = {"id": "repo1::/w/a", "repoId": "repo1", "displayName": "alpha",
       "comment": "", "linkedIssue": None, "linkedPR": None}


def load():
    spec = importlib.util.spec_from_file_location("worktree_ops", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(args, payload=None):
    with tempfile.TemporaryDirectory() as tmp:
        resp = Path(tmp) / "resp.json"
        resp.write_text(json.dumps(payload if payload is not None else {
            "result": {"worktrees": [ROW], "totalCount": 1,
                       "truncated": False}}))
        log = Path(tmp) / "calls.log"
        stub = Path(tmp) / "orca"
        stub.write_text(f'#!/bin/sh\nprintf \'%s\\n\' "$*" >> "{log}"\ncat "{resp}"\n')
        stub.chmod(0o755)
        env = {"PATH": f"{tmp}:/usr/bin:/bin"}
        p = subprocess.run(["python3", str(SCRIPT), *args], env=env,
                           capture_output=True, text=True)
        calls = log.read_text() if log.exists() else ""
        return p.returncode, p.stdout, p.stderr, calls


class TestSelectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_known_forms_accepted(self):
        for sel in ("active", "current", "identity:abc", "id:repo1::/w/a",
                    "name:alpha", "branch:main", "issue:42",
                    "path:/abs/path", "folder:f1", "worktree:repo1::/w/a"):
            with self.subTest(sel=sel):
                self.assertEqual(self.m.validate_selector(sel), sel)

    def test_unknown_forms_refused(self):
        for sel in ("", "/abs/bare/path", "relative/path", "repo1::/w/a",
                    "unknown:x", "path:", "id:", "ACTIVE", " path:/w"):
            with self.subTest(sel=sel), self.assertRaises(self.m.Refused):
                self.m.validate_selector(sel)


class TestArgv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_list_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["list", "--repo", "id:r1", "--limit", "5"])),
            ["worktree", "list", "--repo", "id:r1", "--limit", "5"])

    def test_list_bad_limit_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(["list", "--limit", "0"]))

    def test_show_argv(self):
        self.assertEqual(
            self.m.build_argv(self.m.parse_args(
                ["show", "--worktree", "path:/w/a"])),
            ["worktree", "show", "--worktree", "path:/w/a"])

    def test_show_bad_selector_refused(self):
        with self.assertRaises(self.m.Refused):
            self.m.build_argv(self.m.parse_args(
                ["show", "--worktree", "/w/a"]))


class TestFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_list_format(self):
        lines = self.m.format_list({"worktrees": [ROW,
                                                 dict(ROW, id="r::/b",
                                                      displayName="beta")],
                                    "totalCount": 2, "truncated": True})
        self.assertIn("ROWS=2", lines)
        self.assertIn("TRUNCATED=yes", lines)
        self.assertIn("repo1::/w/a alpha", lines)

    def test_show_format(self):
        lines = self.m.format_show({"worktree": ROW})
        self.assertIn("ID=repo1::/w/a", lines)
        self.assertIn("NAME=alpha", lines)

    def test_show_without_worktree_is_a_failure(self):
        with self.assertRaises(self.m.Failed):
            self.m.format_show({"worktree": {}})


class TestCli(unittest.TestCase):
    def test_cli_list(self):
        rc, out, err, calls = run_cli(["list"])
        self.assertEqual(rc, 0, err)
        self.assertIn("ROWS=1", out)
        self.assertIn("worktree list --json", calls)

    def test_cli_show(self):
        rc, out, err, calls = run_cli(
            ["show", "--worktree", "id:repo1::/w/a"],
            payload={"result": {"worktree": ROW}})
        self.assertEqual(rc, 0, err)
        self.assertIn("ID=repo1::/w/a", out)
        self.assertIn("worktree show --worktree id:repo1::/w/a --json", calls)

    def test_refusal_exits_2_with_no_call(self):
        rc, _o, err, calls = run_cli(["show", "--worktree", "/bare/path"])
        self.assertEqual(rc, 2, err)
        self.assertIn("REFUSED", err)
        self.assertEqual(calls, "")

    def test_error_envelope_exits_1(self):
        rc, _o, err, _c = run_cli(
            ["show", "--worktree", "active"],
            payload={"error": {"code": "worktree_not_found",
                               "message": "gone"}})
        self.assertEqual(rc, 1, err)
        self.assertIn("worktree_not_found", err)


if __name__ == "__main__":
    unittest.main()
