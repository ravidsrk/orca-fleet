#!/usr/bin/env python3
"""In-repo key-write guard for dispatch-sign.py gen-key (#166).

The private dispatch seed must never be committable by accident: the repo's .gitignore must cover
`.secrets/`, and gen-key must refuse to write a seed at a path that resolves inside a git work tree
unless that path is git-ignored (or the caller explicitly overrides with --in-repo-ok).
"""
import contextlib
import importlib.util
import io
import os
import stat
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "dispatch_sign", ROOT / "runtime" / "scripts" / "dispatch-sign.py")
dispatch_sign = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dispatch_sign)


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True, capture_output=True)


def _gen_key(out: Path, extra=()):
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        rc = dispatch_sign.main(["gen-key", "--out", str(out), *extra])
    return rc, stderr.getvalue()


class GenKeyInRepoGuard(unittest.TestCase):
    def test_ignored_in_repo_path_works(self):
        # (a) an in-repo path covered by .gitignore is safe from `git add -A` — allowed.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _git_init(repo)
            (repo / ".gitignore").write_text(".secrets/\n", encoding="utf-8")
            out = repo / ".secrets" / "dispatch-key"
            rc, _ = _gen_key(out)
            self.assertEqual(rc, 0)
            self.assertTrue(out.exists())
            self.assertTrue(Path(str(out) + ".pub").exists())

    def test_non_ignored_in_repo_path_refused(self):
        # (b) an in-repo path git would happily stage is refused, with a loud stderr reason.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _git_init(repo)
            out = repo / "dispatch-key"
            rc, err = _gen_key(out)
            self.assertNotEqual(rc, 0)
            self.assertIn("inside a git work tree", err)
            self.assertIn("--in-repo-ok", err)
            self.assertFalse(out.exists(), "refusal must happen before any bytes are written")

    def test_in_repo_override_flag_allows(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _git_init(repo)
            out = repo / "dispatch-key"
            rc, err = _gen_key(out, extra=["--in-repo-ok"])
            self.assertEqual(rc, 0, err)
            self.assertTrue(out.exists())

    def test_outside_repo_works(self):
        # (c) no git work tree in the ancestry — the recommended out-of-repo layout.
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dispatch-key"
            rc, _ = _gen_key(out)
            self.assertEqual(rc, 0)
            self.assertTrue(out.exists())

    def test_check_ignore_error_fails_closed(self):
        # In a work tree with an inconclusive `git check-ignore`, gen-key must refuse —
        # an unknown ignore status is not proof of safety.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _git_init(repo)
            out = repo / "dispatch-key"
            real_run = subprocess.run

            def fake_run(cmd, **kw):
                if "check-ignore" in cmd:
                    return subprocess.CompletedProcess(cmd, 128)
                return real_run(cmd, **kw)

            with unittest.mock.patch.object(dispatch_sign.subprocess, "run", side_effect=fake_run):
                rc, err = _gen_key(out)
            self.assertNotEqual(rc, 0)
            self.assertFalse(out.exists())

    def test_git_unavailable_fails_closed(self):
        # In a work tree without a usable git binary the ignore status is unverifiable — refuse.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _git_init(repo)
            out = repo / "dispatch-key"
            with unittest.mock.patch.object(dispatch_sign.subprocess, "run",
                                            side_effect=OSError("git not found")):
                rc, _ = _gen_key(out)
            self.assertNotEqual(rc, 0)
            self.assertFalse(out.exists())

    def test_git_unavailable_out_of_repo_still_works(self):
        # No .git ancestor is PROOF of being outside any work tree — no git binary needed.
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dispatch-key"
            with unittest.mock.patch.object(dispatch_sign.subprocess, "run",
                                            side_effect=OSError("git not found")):
                rc, _ = _gen_key(out)
            self.assertEqual(rc, 0)
            self.assertTrue(out.exists())

    def test_external_git_dir_env_detected(self):
        # A repo resolved via GIT_DIR/core.worktree has no .git ancestor — refuse anyway.
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as b:
            worktree = Path(d)
            bare = Path(b) / "repo.git"
            subprocess.run(["git", "init", "--bare", "-q", str(bare)],
                           check=True, capture_output=True)
            subprocess.run(["git", "--git-dir", str(bare), "config", "core.bare", "false"],
                           check=True, capture_output=True)
            subprocess.run(["git", "--git-dir", str(bare), "config", "core.worktree", d],
                           check=True, capture_output=True)
            out = worktree / "dispatch-key"
            with unittest.mock.patch.dict(os.environ, {"GIT_DIR": str(bare)}):
                rc, _ = _gen_key(out)
            self.assertNotEqual(rc, 0)
            self.assertFalse(out.exists())


class GenKeyFilePermissions(unittest.TestCase):
    """#163: the seed's 0o600 must hold from creation, not from a post-write chmod."""

    def test_seed_created_0600_under_zero_umask_without_chmod(self):
        # umask 0 maximizes the create-then-chmod window (0666); poisoning os.chmod pins that
        # the permission comes from os.open/fchmod, never a racy afterthought.
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dispatch-key"
            old_umask = os.umask(0)
            try:
                with unittest.mock.patch.object(
                        dispatch_sign.os, "chmod",
                        side_effect=AssertionError("post-hoc chmod race window")):
                    rc, err = _gen_key(out)
            finally:
                os.umask(old_umask)
            self.assertEqual(rc, 0, err)
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)

    def test_regeneration_tightens_preexisting_permissive_seed(self):
        # os.open's mode applies only at creation — an existing 0644 seed must still end 0600.
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dispatch-key"
            out.write_text("stale\n", encoding="utf-8")
            os.chmod(out, 0o644)
            with unittest.mock.patch.object(
                    dispatch_sign.os, "chmod",
                    side_effect=AssertionError("post-hoc chmod race window")):
                rc, err = _gen_key(out)
            self.assertEqual(rc, 0, err)
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)


class RepoGitignoreCoversSecrets(unittest.TestCase):
    def test_secrets_dir_is_ignored(self):
        rc = subprocess.run(["git", "check-ignore", ".secrets/dispatch-key"],
                            cwd=ROOT, capture_output=True).returncode
        self.assertEqual(rc, 0, ".gitignore must cover .secrets/ (#166)")

    def test_pub_files_not_ignored(self):
        # The pubkey is meant to be committed as .orca/dispatch-pubkey — never ignore it.
        for path in (".orca/dispatch-pubkey", ".secrets/dispatch-key.pub"):
            rc = subprocess.run(["git", "check-ignore", path],
                                cwd=ROOT, capture_output=True).returncode
            self.assertEqual(rc, 1, f"{path}: the dispatch pubkey must remain committable")


if __name__ == "__main__":
    unittest.main()
