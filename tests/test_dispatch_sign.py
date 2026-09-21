#!/usr/bin/env python3
"""In-repo key-write guard for dispatch-sign.py gen-key (#166).

The private dispatch seed must never be committable by accident: the repo's .gitignore must cover
`.secrets/`, and gen-key must refuse to write a seed at a path that resolves inside a git work tree
unless that path is git-ignored (or the caller explicitly overrides with --in-repo-ok).
"""
import base64
import contextlib
import importlib.util
import io
import json
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


class TranscriptSigning(unittest.TestCase):
    """#281 / #386: the verifier's VERDICT is signed with the same scheme as the dispatch tuple.

    verify.py's verdict used to be stdout text plus an exit code — a worker can type any of it.
    `sign-transcript` wraps a verdict object in the {record, sig_b64} envelope `sign` already
    produces, over the same canonical form, with the same key files. No second scheme."""

    _RECORD = {"unit": "u1", "manifest": "docs/runs/r/manifest.json", "manifest_sha256": "ab" * 32,
               "args": {"unit_class": "mutation", "lighting": "lit"},
               "fatal": [], "notes": ["NOTE: x"], "exit": 0,
               "toolchain": {"python": "3.12.0"}, "timestamp": "2026-09-20T00:00:00+00:00"}

    def _ed(self):
        return dispatch_sign._load_ed25519()

    def test_canonical_transcript_is_field_bounded_and_order_free(self):
        # Only the transcript fields are signed, sorted, no whitespace — a worker-added key is not
        # part of the bytes, and the order a producer happened to emit is not a difference.
        canon = dispatch_sign.canonical_transcript(self._RECORD)
        self.assertEqual(canon, dispatch_sign.canonical_transcript(
            dict(reversed(list(self._RECORD.items())), extra="ignored")))
        self.assertNotIn(b"extra", canon)
        self.assertEqual(json.loads(canon.decode("utf-8")),
                         {k: self._RECORD[k] for k in dispatch_sign.TRANSCRIPT_FIELDS})
        self.assertEqual(set(dispatch_sign.TRANSCRIPT_FIELDS),
                         {"unit", "manifest", "manifest_sha256", "args", "fatal", "notes",
                          "exit", "toolchain", "timestamp"})

    def test_sign_transcript_cli_wraps_the_verdict_in_a_verifying_envelope(self):
        with tempfile.TemporaryDirectory() as d:
            key = Path(d) / "dispatch-key"
            rc, err = _gen_key(key)
            self.assertEqual(rc, 0, err)
            transcript = Path(d) / "verdict.json"
            transcript.write_text(json.dumps(self._RECORD), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = dispatch_sign.main(["sign-transcript", "--key", str(key),
                                         "--transcript", str(transcript)])
            self.assertEqual(rc, 0)
            env = json.loads(out.getvalue())
            self.assertEqual(set(env), {"record", "sig_b64"})
            self.assertEqual(env["record"], self._RECORD)
            ed = self._ed()
            pub = bytes.fromhex(Path(str(key) + ".pub").read_text().strip())
            sig = base64.b64decode(env["sig_b64"])
            self.assertTrue(ed.checkvalid(sig, dispatch_sign.canonical_transcript(env["record"]), pub))
            # any byte of the record flipped -> the signature no longer verifies
            tampered = dict(env["record"], exit=2)
            self.assertFalse(ed.checkvalid(sig, dispatch_sign.canonical_transcript(tampered), pub))

    def test_sign_transcript_refuses_an_incomplete_verdict(self):
        # A verdict missing a signed field would sign an absence — refuse, rather than bind nothing.
        with tempfile.TemporaryDirectory() as d:
            key = Path(d) / "dispatch-key"
            _gen_key(key)
            transcript = Path(d) / "verdict.json"
            transcript.write_text(json.dumps({"unit": "u1", "exit": 0}), encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = dispatch_sign.main(["sign-transcript", "--key", str(key),
                                         "--transcript", str(transcript)])
            self.assertNotEqual(rc, 0)
            self.assertIn("manifest", err.getvalue())

    def test_sign_transcript_writes_to_out_when_asked(self):
        with tempfile.TemporaryDirectory() as d:
            key = Path(d) / "dispatch-key"
            _gen_key(key)
            transcript = Path(d) / "verdict.json"
            transcript.write_text(json.dumps(self._RECORD), encoding="utf-8")
            target = Path(d) / "signed.json"
            rc = dispatch_sign.main(["sign-transcript", "--key", str(key),
                                     "--transcript", str(transcript), "--out", str(target)])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(target.read_text())["record"], self._RECORD)

    def test_the_dispatch_envelope_is_untouched(self):
        # Reusing the envelope must not change what `sign` emits for a dispatch record.
        with tempfile.TemporaryDirectory() as d:
            key = Path(d) / "dispatch-key"
            key.write_text(bytes(range(1, 33)).hex() + "\n")
            os.chmod(key, 0o600)  # F-4: a signer refuses a seed any other reader can see
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = dispatch_sign.main(["sign", "--key", str(key), "--manifest-id", "u",
                                         "--contract-digest", "sha256:a", "--unit-class", "mutation"])
            self.assertEqual(rc, 0)
            env = json.loads(out.getvalue())
            self.assertEqual(env["record"], {"manifest_id": "u", "contract_digest": "sha256:a",
                                             "unit_class": "mutation"})
            ed = self._ed()
            self.assertTrue(ed.checkvalid(base64.b64decode(env["sig_b64"]),
                                          dispatch_sign.canonical_record(env["record"]),
                                          ed.publickey(bytes(range(1, 33)))))


if __name__ == "__main__":
    unittest.main()


class SeedCustodyAtUse(unittest.TestCase):
    """h409 F-4 (C3): custody was guarded at CREATION (gen-key refuses an unignored in-repo path
    and writes 0600) and never at USE — every signer read the seed bare, so a 0644 seed, or one
    committed to a repo, signed silently. At signing time the shared _seed re-asserts gen-key's
    discipline: mode with any group/other bit → refuse; inside an unignored git work tree →
    refuse; and a passing seed's custody class is named on stderr so the trail says what signed.
    The check is custody class, not existence — a 0600 seed outside any repo keeps working."""

    def _sign(self, key):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = dispatch_sign.main(["sign", "--key", str(key), "--manifest-id", "u",
                                     "--contract-digest", "sha256:a", "--unit-class", "mutation"])
        return rc, out.getvalue(), err.getvalue()

    def _sign_transcript(self, key, d):
        transcript = Path(d) / "verdict.json"
        transcript.write_text(json.dumps(TranscriptSigning._RECORD), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = dispatch_sign.main(["sign-transcript", "--key", str(key),
                                     "--transcript", str(transcript)])
        return rc, out.getvalue(), err.getvalue()

    def test_a_world_readable_seed_is_refused_by_both_signers(self):
        with tempfile.TemporaryDirectory() as d:
            key = Path(d) / "dispatch-key"
            _gen_key(key)
            os.chmod(key, 0o644)
            for rc, out, err in (self._sign(key), self._sign_transcript(key, d)):
                self.assertEqual(rc, 1, err)
                self.assertEqual(out, "", "a refused seed must sign nothing")
                self.assertIn("custody", err)
                self.assertIn("0644", err)

    def test_a_seed_committed_in_an_unignored_work_tree_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            repo.mkdir()
            _git_init(repo)
            key = repo / "committed-seed"
            _gen_key(key, extra=["--in-repo-ok"])  # creation was overridden; use must not be
            subprocess.run(["git", "add", "committed-seed"], cwd=repo, check=True, capture_output=True)
            for rc, out, err in (self._sign(key), self._sign_transcript(key, d)):
                self.assertEqual(rc, 1, err)
                self.assertEqual(out, "")
                self.assertIn("custody", err)
                self.assertIn("work tree", err)

    def test_a_0600_out_of_repo_seed_signs_and_names_its_custody_class(self):
        with tempfile.TemporaryDirectory() as d:
            key = Path(d) / "dispatch-key"
            _gen_key(key)
            rc, out, err = self._sign(key)
            self.assertEqual(rc, 0, err)
            self.assertIn("sig_b64", out)
            self.assertIn("custody", err)
            self.assertIn("0600", err)

    def test_an_ignored_in_repo_0600_seed_signs(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            repo.mkdir()
            _git_init(repo)
            (repo / ".gitignore").write_text(".secrets/\n", encoding="utf-8")
            key = repo / ".secrets" / "dispatch-key"
            rc, err = _gen_key(key)
            self.assertEqual(rc, 0, err)
            rc, out, err = self._sign(key)
            self.assertEqual(rc, 0, err)
            self.assertIn("custody", err)
