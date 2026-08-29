#!/usr/bin/env python3
"""Smoke tests for runtime/scripts/verify-gate.sh.

The completion-gate hook entrypoint must FAIL CLOSED: block (exit 2) when there is nothing to
verify, no authoritative contract, or the verifier fails; allow (exit 0) only when the manifest
passes against the coordinator-supplied contract.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "runtime" / "scripts"
GATE = SCRIPTS / "verify-gate.sh"


def _src(ids):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    f.write("frozen\n" + "".join(f"- {i}: x\n" for i in ids))
    f.close()
    return f.name


def _digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_text(encoding="utf-8").encode()).hexdigest()


def run_gate(manifest=None, contract_source=None, contract_digest=None, unit_class=None,
             provenance=None, event=None, dispatch_record=None, dispatch_pubkey=None,
             gate=None, cwd=None):
    env = {"PATH": os.environ.get("PATH", "")}
    if manifest is not None:
        env["ORCA_MANIFEST"] = str(manifest)
    if contract_source is not None:
        env["ORCA_CONTRACT_SOURCE"] = contract_source
    if contract_digest is not None:
        env["ORCA_CONTRACT_DIGEST"] = contract_digest
    if unit_class is not None:
        env["ORCA_UNIT_CLASS"] = unit_class
    if provenance is not None:
        env["ORCA_PROVENANCE"] = provenance
    if dispatch_record is not None:
        env["ORCA_DISPATCH_RECORD"] = dispatch_record
    if dispatch_pubkey is not None:
        env["ORCA_DISPATCH_PUBKEY"] = dispatch_pubkey
    argv = [str(gate or GATE)]
    if event is not None:
        argv += ["--event", event]
    return subprocess.run(argv, capture_output=True, text=True, cwd=cwd or ROOT, env=env)


def _sign(digest, unit_class, manifest_id="review-it", lighting=None):
    d = tempfile.mkdtemp()
    signer = str(SCRIPTS / "dispatch-sign.py")
    subprocess.run([sys.executable, signer, "gen-key", "--out", str(Path(d) / "key")],
                   check=True, capture_output=True)
    args = [sys.executable, signer, "sign", "--key", str(Path(d) / "key"),
            "--manifest-id", manifest_id, "--contract-digest", digest, "--unit-class", unit_class]
    if lighting:
        args += ["--lighting", lighting]
    rec = subprocess.run(args, check=True, capture_output=True, text=True).stdout
    rec_path = Path(d) / "rec.json"
    rec_path.write_text(rec, encoding="utf-8")
    return str(rec_path), str(Path(d) / "key.pub")


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _require_born_ambient_head():
    """#163: _manifest pins base_sha/head_sha to the symbolic 'HEAD', resolved by verify.py against
    the AMBIENT repo — outside a git clone the commit-existence leg degrades to a NOTE, and on an
    unborn HEAD 'HEAD' hard-fails as not-a-real-commit. Skip loudly where HEAD cannot resolve."""
    r = subprocess.run(["git", "rev-parse", "--verify", "HEAD^{commit}"],
                       capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise unittest.SkipTest("gate fixtures use head_sha 'HEAD' — needs an ambient git clone "
                                "whose HEAD resolves to a commit")


def _gate_repo(pin_blob=None, pin_worktree=None, remote_head=True):
    """A hermetic git repo hosting a COPY of runtime/scripts, so the gate copy's HERE-relative
    dispatch-pubkey discovery (verify-gate.sh:53-60) reads THIS repo's refs/worktree, never the
    real repo's. pin_blob: pubkey committed as .orca/dispatch-pubkey (worktree copy removed unless
    pin_worktree is also set); pin_worktree: pubkey left in the worktree; remote_head: craft
    refs/remotes/origin/{main,HEAD}."""
    repo = Path(tempfile.mkdtemp())
    _git(repo, "init", "-q", "-b", "main")
    shutil.copytree(SCRIPTS, repo / "runtime" / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__"))
    if pin_blob is not None or pin_worktree is not None:
        pin = repo / ".orca" / "dispatch-pubkey"
        pin.parent.mkdir(exist_ok=True)
        pin.write_text(pin_blob or pin_worktree, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    if pin_blob is not None and pin_worktree is None:
        os.remove(repo / ".orca" / "dispatch-pubkey")  # blob-only: worktree fallback cannot fire
    if remote_head:
        _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    return repo


def _manifest(source, ids_declared, ids_addressed):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump({
            "unit": "review-it", "unit_class": "report-only",
            "base_sha": "HEAD", "head_sha": "HEAD",
            "contract": {"source": source, "digest": _digest(source), "criterion_ids": ids_declared},
            "criteria": [{"id": i, "addressed": True} for i in ids_addressed],
            "pr": {"reviewed_sha": "HEAD"},
        }, fh)
        return fh.name


class VerifyGateFailsClosed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _require_born_ambient_head()

    def test_no_manifest_blocks(self):
        self.assertEqual(run_gate(None).returncode, 2)

    def test_no_contract_blocks(self):
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        self.assertEqual(run_gate(m, unit_class="report-only").returncode, 2)  # scope fail-closed

    def test_good_manifest_allows(self):
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        r = run_gate(m, src, _digest(src), unit_class="report-only")
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")

    def test_scope_shrink_blocks(self):
        src = _src(["AC-1", "AC-2"])
        m = _manifest(src, ["AC-1", "AC-2"], ["AC-1"])
        self.assertEqual(run_gate(m, src, _digest(src), unit_class="report-only").returncode, 2)

    def test_missing_unit_class_gated_as_mutation_blocks(self):
        # #110 fail-safe: without ORCA_UNIT_CLASS the unit is gated as mutation, so a report-only-
        # shaped manifest with no independent GitHub review blocks (exit 2) rather than passing.
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        self.assertEqual(run_gate(m, src, _digest(src)).returncode, 2)

    def test_unknown_unit_class_fails_safe_to_mutation(self):
        # #178: an unknown ORCA_UNIT_CLASS (a typo like "mutatoin") must NOT wedge argparse with a
        # usage error — the gate forwards it verbatim, verify.py reaches the real invariant checks,
        # and _is_mutation's fallback gates the unit as mutation: a report-only-shaped manifest
        # fails a mutation invariant (exit 2), and a NOTE on stdout names the unknown value.
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        r = run_gate(m, src, _digest(src), unit_class="mutatoin")
        self.assertEqual(r.returncode, 2, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertIn("mutatoin", r.stdout)                 # the loud NOTE, not a silent fallback
        self.assertNotIn("invalid choice", r.stderr)        # no argparse wedge
        self.assertIn("mutation unit", r.stderr)            # mutation-strict checks actually ran


class VerifyGateTrustBoundary(unittest.TestCase):
    """#112: the gate is advisory when provenance is in-session, sound when off-worker."""

    @classmethod
    def setUpClass(cls):
        _require_born_ambient_head()

    def test_advisory_note_when_provenance_unset(self):
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        r = run_gate(m, src, _digest(src), unit_class="report-only")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ADVISORY", r.stderr)

    def test_no_note_when_provenance_offworker(self):
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        r = run_gate(m, src, _digest(src), unit_class="report-only", provenance="ci")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("ADVISORY", r.stderr)


class VerifyGateStopScope(unittest.TestCase):
    """#121: Stop fires on every turn end; with no unit in progress it must ALLOW, while
    TaskCompleted (or an explicit manifest) with no manifest still blocks (mis-dispatch)."""

    @classmethod
    def setUpClass(cls):
        _require_born_ambient_head()

    def test_stop_no_manifest_allows(self):
        self.assertEqual(run_gate(None, event="stop").returncode, 0)

    def test_task_no_manifest_blocks(self):
        self.assertEqual(run_gate(None, event="task").returncode, 2)

    def test_stop_with_manifest_still_verifies(self):
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        r = run_gate(m, src, _digest(src), unit_class="report-only", event="stop")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_stop_named_but_missing_manifest_blocks(self):
        # #141 review: a NAMED manifest whose file is deleted/mistyped means an active unit's
        # evidence is gone — Stop must fail closed, not silently treat it like "no unit in progress".
        r = run_gate("/tmp/orca-does-not-exist-" + os.urandom(4).hex() + ".json", event="stop")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("named but missing", r.stderr)


class VerifyGateSignedDispatch(unittest.TestCase):
    """#135: the gate forwards a signed dispatch record to verify.py; the signature is checked and a
    substituted value is blocked. Off-worker (provenance set) it is a soundness boundary; on the native
    path it stays advisory — no in-session anchor is trustworthy."""

    @classmethod
    def setUpClass(cls):
        _require_born_ambient_head()

    def test_signed_dispatch_verified_off_worker(self):
        # ORCA_PROVENANCE=dispatch models an OFF-WORKER context that supplies the key: verify.py checks
        # the signature and the advisory NOTE is suppressed.
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])   # _manifest's unit is "review-it"
        rec, pub = _sign(_digest(src), "report-only")
        r = run_gate(m, src, _digest(src), unit_class="report-only", event="task",
                     provenance="dispatch", dispatch_record=rec, dispatch_pubkey=pub)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("signature verified", r.stdout + r.stderr)
        self.assertNotIn("ADVISORY", r.stderr)

    def test_signed_dispatch_class_substitution_blocks(self):
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        rec, pub = _sign(_digest(src), "mutation")   # coordinator signed 'mutation'
        r = run_gate(m, src, _digest(src), unit_class="report-only", event="task",  # worker downgraded
                     provenance="dispatch", dispatch_record=rec, dispatch_pubkey=pub)
        self.assertEqual(r.returncode, 2)
        self.assertIn("substitution", r.stderr)

    def test_native_hook_stays_advisory_with_record(self):
        # #135 review: no in-session anchor is trustworthy (worker controls ORCA_*), so even with a
        # record + key the NATIVE path (no off-worker provenance) must stay ADVISORY — never claim sound.
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        rec, pub = _sign(_digest(src), "report-only")
        r = run_gate(m, src, _digest(src), unit_class="report-only", event="task",
                     dispatch_record=rec, dispatch_pubkey=pub)   # no provenance → native path
        self.assertIn("ADVISORY", r.stderr)

    def test_worker_set_env_pubkey_honored_with_advisory_note(self):
        # #164: the gate reads ORCA_DISPATCH_PUBKEY unconditionally — a WORKER-SET env key is honored
        # (ORCA_PROVENANCE gates only the NOTE, never the key source). If the env key were ignored the
        # record would be half-configured (no pin exists in this repo) and the gate would fail closed;
        # exit 0 + "signature verified" pins that verification ran AGAINST the env key.
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        rec, pub = _sign(_digest(src), "report-only")
        r = run_gate(m, src, _digest(src), unit_class="report-only", event="task",
                     dispatch_record=rec, dispatch_pubkey=pub)   # worker-set env key, no provenance
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("signature verified", r.stdout + r.stderr)
        self.assertIn("ADVISORY", r.stderr)


class VerifyGateDispatchPinDiscovery(unittest.TestCase):
    """#171: verify-gate.sh:53-60 — when ORCA_DISPATCH_PUBKEY is NOT injected, the gate discovers the
    committed .orca/dispatch-pubkey pin (reviewed remote blob first, working tree as fallback) from
    the repo the script lives in. Each test runs a COPY of the gate inside a hermetic temp git repo
    (_gate_repo), so the real repo's refs are never read or mutated; ORCA_DISPATCH_PUBKEY stays unset.
    Behavior asserted, not argv: a record signed by the pinned key verifies (exit 0 +
    'signature verified') only if the discovery branch actually supplied the key — otherwise
    verify.py fails closed on a half-configured dispatch check."""

    def _run_discovered(self, repo, src, dispatch_record):
        m = _manifest(src, ["AC-1"], ["AC-1"])
        return run_gate(m, src, _digest(src), unit_class="report-only", event="task",
                        provenance="dispatch", dispatch_record=dispatch_record,
                        gate=repo / "runtime" / "scripts" / "verify-gate.sh", cwd=repo)

    def test_remote_blob_hit(self):
        # Pin committed on origin/main (refs/remotes/origin/HEAD resolves) but ABSENT from the
        # worktree — only the remote-blob read can supply the key. Reverting 933765a (dropping the
        # blob read) turns this red: no key is found and the signed record fails closed.
        src = _src(["AC-1"])
        rec, pub = _sign(_digest(src), "report-only")
        repo = _gate_repo(pin_blob=Path(pub).read_text(encoding="utf-8"), remote_head=True)
        r = self._run_discovered(repo, src, rec)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertIn("signature verified", r.stdout + r.stderr)

    def test_worktree_fallback(self):
        # No refs/remotes/origin/HEAD — the blob read cannot fire — but the pin exists in the
        # worktree, so the fallback supplies it. Deleting the fallback lines turns this red.
        src = _src(["AC-1"])
        rec, pub = _sign(_digest(src), "report-only")
        repo = _gate_repo(pin_worktree=Path(pub).read_text(encoding="utf-8"), remote_head=False)
        r = self._run_discovered(repo, src, rec)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertIn("signature verified", r.stdout + r.stderr)

    def test_neither_present_proceeds_without_dispatch_check(self):
        # No remote ref, no worktree pin (HEAD at the real repo matches: the pin is not committed).
        # The gate must pass NO --dispatch-pubkey, so verify.py runs no dispatch check: a clean
        # manifest passes; a signed record with no key anywhere fails closed as HALF-CONFIGURED
        # (missing --dispatch-pubkey) — proof the key stayed undiscovered rather than silently read.
        src = _src(["AC-1"])
        repo = _gate_repo(remote_head=False)
        r = self._run_discovered(repo, src, None)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertNotIn("signature verified", r.stdout + r.stderr)
        rec, _pub = _sign(_digest(src), "report-only")
        r = self._run_discovered(repo, src, rec)
        self.assertEqual(r.returncode, 2)
        self.assertIn("missing --dispatch-pubkey", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
