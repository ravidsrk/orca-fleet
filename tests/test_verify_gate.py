#!/usr/bin/env python3
"""Smoke tests for runtime/scripts/verify-gate.sh.

The completion-gate hook entrypoint must FAIL CLOSED: block (exit 2) when there is nothing to
verify, no authoritative contract, or the verifier fails; allow (exit 0) only when the manifest
passes against the coordinator-supplied contract.
"""
import hashlib
import itertools
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


_SRC_SEQ = itertools.count()


def _src(repo, ids):
    """A frozen-contract fixture INSIDE `repo`, named relatively: #267 refuses absolute and
    out-of-repo evidence paths, and verify.py resolves relative ones against the toplevel of the
    process cwd — which is why every gate test runs in a hermetic repo."""
    rel = f"contract-{next(_SRC_SEQ)}.md"
    (repo / rel).write_text("frozen\n" + "".join(f"- {i}: x\n" for i in ids), encoding="utf-8")
    return rel


def _digest(repo, rel):
    return "sha256:" + hashlib.sha256((repo / rel).read_bytes()).hexdigest()


def run_gate(manifest=None, contract_source=None, contract_digest=None, unit_class=None,
             provenance=None, event=None, dispatch_record=None, dispatch_pubkey=None,
             gate=None, cwd=None, execute_nc=None, lighting=None):
    env = {"PATH": os.environ.get("PATH", "")}
    if execute_nc is not None:
        env["ORCA_EXECUTE_NC"] = execute_nc
    if lighting is not None:
        env["ORCA_LIGHTING"] = lighting
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


def _mint_key():
    """Mint an Ed25519 keypair; returns (secret_path, public_hex). The public half is what a repo
    pins as .orca/dispatch-pubkey."""
    d = Path(tempfile.mkdtemp())
    subprocess.run([sys.executable, str(SCRIPTS / "dispatch-sign.py"), "gen-key",
                    "--out", str(d / "key")], check=True, capture_output=True)
    return d / "key", (d / "key.pub").read_text(encoding="utf-8")


def _sign(repo, digest, unit_class, manifest_id="review-it", lighting=None, key=None):
    """Sign a dispatch record and drop it, with its public key, INSIDE `repo` under relative names
    (#267). Returns (record_rel, pubkey_rel) — what a real dispatch would hand the gate."""
    n = next(_SRC_SEQ)
    secret, public = key if key else _mint_key()
    args = [sys.executable, str(SCRIPTS / "dispatch-sign.py"), "sign", "--key", str(secret),
            "--manifest-id", manifest_id, "--contract-digest", digest, "--unit-class", unit_class]
    if lighting:
        args += ["--lighting", lighting]
    rec = subprocess.run(args, check=True, capture_output=True, text=True).stdout
    rec_rel, pub_rel = f".orca/rec-{n}.json", f".orca/key-{n}.pub"
    (repo / ".orca").mkdir(exist_ok=True)
    (repo / rec_rel).write_text(rec, encoding="utf-8")
    (repo / pub_rel).write_text(public, encoding="utf-8")
    return rec_rel, pub_rel


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _git_out(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _hermetic_repo():
    """A one-commit repo the gate can run inside. #163's skip is gone with it: the fixtures used to
    resolve 'HEAD' against the AMBIENT clone (unborn on some CI checkouts); now every gate test
    brings its own repo, so HEAD always resolves and nothing is skipped."""
    repo = Path(tempfile.mkdtemp())
    _git(repo, "init", "-q", "-b", "main")
    (repo / "README").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    return repo


class GateCase(unittest.TestCase):
    """#267 bounds contract / dispatch-record / pubkey paths to the toplevel of the process cwd, so
    the gate runs inside a hermetic repo and every path it is handed is relative to that repo."""

    def setUp(self):
        self.repo = self.make_repo()
        self.addCleanup(shutil.rmtree, self.repo, True)

    def make_repo(self):
        return _hermetic_repo()

    def src(self, ids):
        return _src(self.repo, ids)

    def digest(self, rel):
        return _digest(self.repo, rel)

    def sign(self, digest, unit_class, **kw):
        return _sign(self.repo, digest, unit_class, **kw)

    def manifest(self, source, ids_declared, ids_addressed):
        return _manifest(self.repo, source, ids_declared, ids_addressed)

    def gate(self, manifest=None, *a, **kw):
        kw.setdefault("cwd", self.repo)
        return run_gate(manifest, *a, **kw)


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
        pin.write_text((pin_blob or pin_worktree)[1], encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    if pin_blob is not None and pin_worktree is None:
        os.remove(repo / ".orca" / "dispatch-pubkey")  # blob-only: worktree fallback cannot fire
    if remote_head:
        _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    # #193 review: origin/HEAD and local HEAD must NOT alias the same commit, or a
    # regression that reads the pin from worker-modifiable HEAD still greens
    # test_remote_blob_hit. After origin is pinned at the blob commit, advance
    # HEAD to a pinless commit so only the remote-ref read can supply the key.
    if pin_blob is not None and pin_worktree is None and remote_head:
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "no-pin")
    return repo


def _doc_range(repo):
    """Two real commits whose only difference is a document — the honest report-only shape.

    These fixtures used `HEAD..HEAD`, which is now refused: an empty declared range asserts that
    the unit changed nothing while giving the gate no diff to check that against, and a unit that
    changed code can assert it just as easily (#310, PR #308 review)."""
    base = _git_out(repo, "rev-parse", "HEAD")
    rel = f"docs/report-{next(_SRC_SEQ)}.md"
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text("# report\n", encoding="utf-8")
    _git(repo, "add", rel)
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "report")
    return base, _git_out(repo, "rev-parse", "HEAD")


def _manifest(repo, source, ids_declared, ids_addressed):
    path = repo / f"manifest-{next(_SRC_SEQ)}.json"
    base, head = _doc_range(repo)
    path.write_text(json.dumps({
        "unit": "review-it", "unit_class": "report-only",
        "base_sha": base, "head_sha": head,
        "contract": {"source": source, "digest": _digest(repo, source),
                     "criterion_ids": ids_declared},
        "criteria": [{"id": i, "addressed": True} for i in ids_addressed],
        "pr": {"reviewed_sha": head},
    }), encoding="utf-8")
    return str(path)


class VerifyGateFailsClosed(GateCase):

    def test_no_manifest_blocks(self):
        self.assertEqual(self.gate(None).returncode, 2)

    def test_no_contract_blocks(self):
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        self.assertEqual(self.gate(m, unit_class="report-only").returncode, 2)  # scope fail-closed

    def test_good_manifest_allows(self):
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        r = self.gate(m, src, self.digest(src), unit_class="report-only")
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")

    def test_scope_shrink_blocks(self):
        src = self.src(["AC-1", "AC-2"])
        m = self.manifest(src, ["AC-1", "AC-2"], ["AC-1"])
        self.assertEqual(self.gate(m, src, self.digest(src), unit_class="report-only").returncode, 2)

    def test_missing_unit_class_gated_as_mutation_blocks(self):
        # #110 fail-safe: without ORCA_UNIT_CLASS the unit is gated as mutation, so a report-only-
        # shaped manifest with no independent GitHub review blocks (exit 2) rather than passing.
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        self.assertEqual(self.gate(m, src, self.digest(src)).returncode, 2)

    def test_unknown_unit_class_fails_safe_to_mutation(self):
        # #178: an unknown ORCA_UNIT_CLASS (a typo like "mutatoin") must NOT wedge argparse with a
        # usage error — the gate forwards it verbatim, verify.py reaches the real invariant checks,
        # and _is_mutation's fallback gates the unit as mutation: a report-only-shaped manifest
        # fails a mutation invariant (exit 2), and a NOTE on stdout names the unknown value.
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        r = self.gate(m, src, self.digest(src), unit_class="mutatoin")
        self.assertEqual(r.returncode, 2, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertIn("mutatoin", r.stdout)                 # the loud NOTE, not a silent fallback
        self.assertNotIn("invalid choice", r.stderr)        # no argparse wedge
        self.assertIn("mutation unit", r.stderr)            # mutation-strict checks actually ran


class VerifyGateExecuteNC(GateCase):
    """#255/#256: ORCA_EXECUTE_NC reaches verify.py as --execute-nc, and the two review-waiver
    lanes are RED without it. Asserted through BEHAVIOUR — the messages only verify.py's executed
    path can produce — so a regression that drops the forwarding line cannot pass."""

    def _mutation_manifest(self, src, nc):
        head = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True).stdout.strip()
        path = self.repo / "mutation-manifest.json"
        path.write_text(json.dumps({
            "unit": "ship-it", "base_sha": head, "head_sha": head,
            "contract": {"source": src, "digest": self.digest(src), "criterion_ids": ["AC-1"]},
            "criteria": [{"id": "AC-1", "addressed": True}],
            "negative_control": nc, "lighting": "dark-eligible",
            "reviewer_mode": "cross-vendor",
            "intent": {"goal": "g", "ruled_out": "r", "why": "w"},
        }), encoding="utf-8")
        return str(path)

    def _nc(self):
        rel = "docs/reports/u/nc.txt"
        (self.repo / "docs" / "reports" / "u").mkdir(parents=True, exist_ok=True)
        (self.repo / rel).write_text("mutant m7 KILLED — proof went RED\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "nc")
        return {"tool": "mutmut", "mutant": "m7", "result": "KILLED", "artifact": rel}

    def test_execute_nc_env_reaches_the_verifier(self):
        src = self.src(["AC-1"])
        m = self._mutation_manifest(src, self._nc())
        r = self.gate(m, src, self.digest(src), unit_class="mutation", event="task",
                      lighting="dark-eligible", execute_nc="1")
        self.assertEqual(r.returncode, 2)
        # only the EXECUTED path emits this — proof the env var was forwarded as --execute-nc
        self.assertIn("no replay is implemented", r.stderr)

    def test_dark_lane_without_execute_nc_blocks(self):
        src = self.src(["AC-1"])
        m = self._mutation_manifest(src, self._nc())
        r = self.gate(m, src, self.digest(src), unit_class="mutation", event="task",
                      lighting="dark-eligible")
        self.assertEqual(r.returncode, 2)
        self.assertIn("EXECUTED", r.stderr)
        self.assertNotIn("no replay is implemented", r.stderr)


class VerifyGateTrustBoundary(GateCase):
    """#112: the gate is advisory when provenance is in-session, sound when off-worker."""


    def test_advisory_note_when_provenance_unset(self):
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        r = self.gate(m, src, self.digest(src), unit_class="report-only")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ADVISORY", r.stderr)

    def test_no_note_when_provenance_offworker(self):
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        r = self.gate(m, src, self.digest(src), unit_class="report-only", provenance="ci")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("ADVISORY", r.stderr)


class VerifyGateStopScope(GateCase):
    """#121: Stop fires on every turn end; with no unit in progress it must ALLOW, while
    TaskCompleted (or an explicit manifest) with no manifest still blocks (mis-dispatch)."""


    def test_stop_no_manifest_allows(self):
        self.assertEqual(self.gate(None, event="stop").returncode, 0)

    def test_task_no_manifest_blocks(self):
        self.assertEqual(self.gate(None, event="task").returncode, 2)

    def test_stop_with_manifest_still_verifies(self):
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        r = self.gate(m, src, self.digest(src), unit_class="report-only", event="stop")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_stop_named_but_missing_manifest_blocks(self):
        # #141 review: a NAMED manifest whose file is deleted/mistyped means an active unit's
        # evidence is gone — Stop must fail closed, not silently treat it like "no unit in progress".
        r = self.gate("/tmp/orca-does-not-exist-" + os.urandom(4).hex() + ".json", event="stop")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("named but missing", r.stderr)


class VerifyGateSignedDispatch(GateCase):
    """#135: the gate forwards a signed dispatch record to verify.py; the signature is checked and a
    substituted value is blocked. Off-worker (provenance set) it is a soundness boundary; on the native
    path it stays advisory — no in-session anchor is trustworthy."""


    def test_signed_dispatch_verified_off_worker(self):
        # ORCA_PROVENANCE=dispatch models an OFF-WORKER context that supplies the key: verify.py checks
        # the signature and the advisory NOTE is suppressed.
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])   # _manifest's unit is "review-it"
        rec, pub = self.sign(self.digest(src), "report-only")
        r = self.gate(m, src, self.digest(src), unit_class="report-only", event="task",
                     provenance="dispatch", dispatch_record=rec, dispatch_pubkey=pub)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("signature verified", r.stdout + r.stderr)
        self.assertNotIn("ADVISORY", r.stderr)

    def test_signed_dispatch_class_substitution_blocks(self):
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        rec, pub = self.sign(self.digest(src), "mutation")   # coordinator signed 'mutation'
        r = self.gate(m, src, self.digest(src), unit_class="report-only", event="task",  # worker downgraded
                     provenance="dispatch", dispatch_record=rec, dispatch_pubkey=pub)
        self.assertEqual(r.returncode, 2)
        self.assertIn("substitution", r.stderr)

    def test_native_hook_stays_advisory_with_record(self):
        # #135 review: no in-session anchor is trustworthy (worker controls ORCA_*), so even with a
        # record + key the NATIVE path (no off-worker provenance) must stay ADVISORY — never claim sound.
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        rec, pub = self.sign(self.digest(src), "report-only")
        r = self.gate(m, src, self.digest(src), unit_class="report-only", event="task",
                     dispatch_record=rec, dispatch_pubkey=pub)   # no provenance → native path
        self.assertIn("ADVISORY", r.stderr)

    def test_worker_set_env_pubkey_honored_with_advisory_note(self):
        # #164: the gate reads ORCA_DISPATCH_PUBKEY unconditionally — a WORKER-SET env key is honored
        # (ORCA_PROVENANCE gates only the NOTE, never the key source). If the env key were ignored the
        # record would be half-configured (no pin exists in this repo) and the gate would fail closed;
        # exit 0 + "signature verified" pins that verification ran AGAINST the env key.
        src = self.src(["AC-1"])
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        rec, pub = self.sign(self.digest(src), "report-only")
        r = self.gate(m, src, self.digest(src), unit_class="report-only", event="task",
                     dispatch_record=rec, dispatch_pubkey=pub)   # worker-set env key, no provenance
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("signature verified", r.stdout + r.stderr)
        self.assertIn("ADVISORY", r.stderr)


class VerifyGateDispatchPinDiscovery(GateCase):
    """#171: verify-gate.sh:53-60 — the gate discovers the verifying key from three sources, in
    this order: (1) ORCA_DISPATCH_PUBKEY env, (2) the reviewed remote blob at origin/HEAD, (3) the
    working-tree file. Each test runs a COPY of the gate inside a hermetic temp git repo
    (_gate_repo), so the real repo's refs are never read or mutated. Behavior asserted, not argv:
    a record signed by the expected key verifies (exit 0 + 'signature verified') only if that
    source actually supplied it — otherwise verify.py fails closed.

    #267: the contract, the record and the keys all live INSIDE that repo under relative names, so
    `use_repo` swaps the case's repo for the gate-hosting one BEFORE any fixture is written."""

    def use_repo(self, **kw):
        """Replace this case's hermetic repo with a gate-hosting one, then return a pubkey the
        caller can pin into it. Two keys are minted up front because the pin has to be committed
        when the repo is built, before any fixture can be written into it."""
        pubs = [_mint_key() for _ in range(2)]
        repo = _gate_repo(**{k: (pubs[0] if v is True else v) for k, v in kw.items()})
        self.repo = repo
        self.addCleanup(shutil.rmtree, repo, True)
        return pubs

    def _run_discovered(self, src, dispatch_record, dispatch_pubkey=None):
        m = self.manifest(src, ["AC-1"], ["AC-1"])
        return self.gate(m, src, self.digest(src), unit_class="report-only", event="task",
                         provenance="dispatch", dispatch_record=dispatch_record,
                         dispatch_pubkey=dispatch_pubkey,
                         gate=self.repo / "runtime" / "scripts" / "verify-gate.sh")

    def test_remote_blob_hit(self):
        # Pin committed on origin/main (refs/remotes/origin/HEAD resolves) but ABSENT from the
        # worktree AND from local HEAD (_gate_repo advances HEAD to a pinless commit) — only the
        # remote-blob read can supply the key. Reverting 933765a (dropping the blob read) or
        # reading HEAD instead of origin/HEAD turns this red.
        (pinned, _spare) = self.use_repo(pin_blob=True, remote_head=True)
        src = self.src(["AC-1"])
        rec, _pub = self.sign(self.digest(src), "report-only", key=pinned)
        r = self._run_discovered(src, rec)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertIn("signature verified", r.stdout + r.stderr)

    def test_worktree_fallback(self):
        # No refs/remotes/origin/HEAD — the blob read cannot fire — but the pin exists in the
        # worktree, so the fallback supplies it. Deleting the fallback lines turns this red.
        (pinned, _spare) = self.use_repo(pin_worktree=True, remote_head=False)
        src = self.src(["AC-1"])
        rec, _pub = self.sign(self.digest(src), "report-only", key=pinned)
        r = self._run_discovered(src, rec)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertIn("signature verified", r.stdout + r.stderr)

    def test_env_pubkey_precedes_repo_pin(self):
        # #198 review: env beats a present repo pin. A record signed by the env key verifies
        # even though origin/HEAD carries a *different* pin; a record signed by the pin key
        # fails — so a regression that ignores env and always reads the pin turns this red.
        (pinned, env_key) = self.use_repo(pin_blob=True, remote_head=True)
        src = self.src(["AC-1"])
        rec_env, pub_env = self.sign(self.digest(src), "report-only", key=env_key)
        rec_pin, _pub_pin = self.sign(self.digest(src), "report-only", key=pinned)
        r = self._run_discovered(src, rec_env, dispatch_pubkey=pub_env)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertIn("signature verified", r.stdout + r.stderr)
        r = self._run_discovered(src, rec_pin, dispatch_pubkey=pub_env)
        self.assertEqual(r.returncode, 2, f"stdout={r.stdout} stderr={r.stderr}")

    def test_neither_present_proceeds_without_dispatch_check(self):
        # No remote ref, no worktree pin. The gate must pass NO --dispatch-pubkey, so verify.py
        # runs no dispatch check: a clean manifest passes; a signed record with no key anywhere
        # fails closed as HALF-CONFIGURED (missing --dispatch-pubkey) — proof the key stayed
        # undiscovered rather than silently read.
        self.use_repo(remote_head=False)
        src = self.src(["AC-1"])
        r = self._run_discovered(src, None)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
        self.assertNotIn("signature verified", r.stdout + r.stderr)
        rec, _pub = self.sign(self.digest(src), "report-only")
        r = self._run_discovered(src, rec)
        self.assertEqual(r.returncode, 2)
        self.assertIn("missing --dispatch-pubkey", r.stderr)


class SymlinkInstallGate(unittest.TestCase):
    """Issue #262: the recommended install path shipped no gate at all.

    `hooks/hooks.json` resolves through `${CLAUDE_PLUGIN_ROOT}`, which Claude Code
    sets only for plugin installs. `ln -s` into ~/.claude/skills/ loads no plugin,
    so those two hooks never fire and the missions run ungated — silently. The
    snippet is the fix; these tests keep it wired and keep the README saying so.
    """

    SNIPPET = ROOT / "hooks" / "settings-snippet.json"
    PRINTER = ROOT / "hooks" / "print-settings-snippet.sh"

    def test_plugin_hooks_still_resolve_through_the_plugin_root(self):
        data = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        commands = [
            h["command"]
            for event in data["hooks"].values()
            for matcher in event
            for h in matcher["hooks"]
        ]
        self.assertTrue(commands)
        for command in commands:
            self.assertIn("${CLAUDE_PLUGIN_ROOT}", command)

    def test_the_snippet_wires_the_same_two_events(self):
        plugin = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        snippet = json.loads(self.SNIPPET.read_text(encoding="utf-8"))
        self.assertEqual(sorted(snippet["hooks"]), sorted(plugin["hooks"]))
        for event, entries in snippet["hooks"].items():
            for matcher in entries:
                for hook in matcher["hooks"]:
                    self.assertIn("__ORCA_FLEET_ROOT__", hook["command"])
                    self.assertIn("verify-gate.sh", hook["command"])

    def test_the_printer_resolves_the_placeholder_to_a_real_script(self):
        r = subprocess.run(
            ["sh", str(self.PRINTER)], capture_output=True, text=True, cwd=str(ROOT)
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        emitted = json.loads(r.stdout)
        for event in emitted["hooks"].values():
            for matcher in event:
                for hook in matcher["hooks"]:
                    self.assertNotIn("__ORCA_FLEET_ROOT__", hook["command"])
                    script = hook["command"].split(" --event")[0]
                    self.assertTrue(Path(script).is_file(), script)

    def test_the_printer_check_mode_verifies_the_gate_script(self):
        r = subprocess.run(
            ["sh", str(self.PRINTER), "--check"], capture_output=True, text=True, cwd=str(ROOT)
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("verify-gate.sh", r.stdout)

    def test_the_readme_says_a_symlink_install_has_no_gate(self):
        # The finding was that nothing told the user. A README that stops saying
        # so puts it back.
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("print-settings-snippet.sh", readme)
        self.assertIn("no completion gate", readme)


if __name__ == "__main__":
    unittest.main(verbosity=2)
