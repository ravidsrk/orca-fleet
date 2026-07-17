#!/usr/bin/env python3
"""
Contract tests for runtime/scripts/preflight.py.

The docstring promises: exit 0 = OK, exit 1 = usage/dependency, exit 2 = invariant
violation. argparse's default SystemExit(2) on unknown flags and bad choices collapsed
usage errors into the invariant bucket — a typo'd flag was indistinguishable from a
tripped M-5 guardrail. These tests pin the boundary from both sides. They also pin
that gh subprocess calls carry a timeout (a hung gh must fail Phase 0 fast, not block
it forever) and that --offline starts without gh while keeping every git-based BASE
invariant.
"""
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "preflight.py"

_spec = importlib.util.spec_from_file_location("preflight", SCRIPT)
preflight = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(preflight)


def run_preflight(*argv, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argv],
        capture_output=True, text=True, cwd=cwd, env=env, timeout=60,
    )


def make_repo(path, default="main", base=None):
    subprocess.run(["git", "init", "-q", "-b", default, str(path)], check=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t.invalid",
         "commit", "--allow-empty", "-q", "-m", "root"],
        check=True,
    )
    if base:
        subprocess.run(["git", "-C", str(path), "branch", base], check=True)


def wrapper(dirpath, name, real):
    """A PATH shim that execs the real binary — safer than a symlink, which can
    break a relocatable binary's own prefix resolution."""
    p = Path(dirpath) / name
    p.write_text(f'#!/bin/sh\nexec "{real}" "$@"\n', encoding="utf-8")
    p.chmod(0o755)
    return p


class TestExitCodeContract(unittest.TestCase):
    """Usage errors are 1; invariant violations are 2. Never the same bucket."""

    def test_unknown_flag_is_usage_exit_1(self):
        r = run_preflight("--bogus-flag")
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_bad_mode_value_is_usage_exit_1(self):
        r = run_preflight("--mode", "wrong")
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_missing_base_is_usage_exit_1(self):
        # Pin: this side of the boundary was already correct.
        r = run_preflight()
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_base_equals_default_is_invariant_exit_2(self):
        # The tripped M-5 guardrail must stay distinguishable from a typo'd flag.
        with tempfile.TemporaryDirectory() as tmp:
            make_repo(tmp)
            r = run_preflight("--offline", "--base", "main", "--default", "main", cwd=tmp)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("DEFAULT_BRANCH", r.stderr)


class TestOfflineStart(unittest.TestCase):

    def test_offline_requires_default(self):
        r = run_preflight("--offline", "--base", "x")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("--default", r.stderr)

    def test_offline_passes_without_gh_on_path(self):
        # A host that STARTS offline: no gh anywhere, git-only invariants still run.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            make_repo(repo, base="integ")
            fakebin = Path(tmp) / "bin"
            fakebin.mkdir()
            wrapper(fakebin, "git", shutil.which("git"))
            env = dict(os.environ, PATH=str(fakebin))
            r = run_preflight("--offline", "--base", "integ", "--default", "main",
                              cwd=str(repo), env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("preflight: OK", r.stdout)


class TestHungGh(unittest.TestCase):

    def test_hung_gh_fails_fast_with_timeout_message(self):
        # merge-serialization.md handles gh dying MID-run; Phase 0 must not hang
        # on a gh that never answers. Stub gh sleeps far past the patched timeout.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            make_repo(repo)
            fakebin = Path(tmp) / "bin"
            fakebin.mkdir()
            hung = fakebin / "gh"
            hung.write_text("#!/bin/sh\nsleep 30\n", encoding="utf-8")
            hung.chmod(0o755)
            err = io.StringIO()
            cwd = os.getcwd()
            os.chdir(repo)
            try:
                with mock.patch.dict(os.environ, {"PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}"}), \
                        mock.patch.object(preflight, "_GH_TIMEOUT", 1):
                    start = time.monotonic()
                    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                        rc = preflight.main(["--base", "whatever"])
                    elapsed = time.monotonic() - start
            finally:
                os.chdir(cwd)
        self.assertEqual(rc, 1, err.getvalue())
        self.assertLess(elapsed, 10, "a hung gh must fail preflight fast, not block Phase 0")
        self.assertIn("timed out", err.getvalue())
        self.assertIn("--offline", err.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
