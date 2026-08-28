#!/usr/bin/env python3
"""Smoke tests for runtime/scripts/verify-gate.sh.

The completion-gate hook entrypoint must FAIL CLOSED: block (exit 2) when there is nothing to
verify, no authoritative contract, or the verifier fails; allow (exit 0) only when the manifest
passes against the coordinator-supplied contract.
"""
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "runtime" / "scripts" / "verify-gate.sh"


def _src(ids):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    f.write("frozen\n" + "".join(f"- {i}: x\n" for i in ids))
    f.close()
    return f.name


def _digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_text(encoding="utf-8").encode()).hexdigest()


def run_gate(manifest=None, contract_source=None, contract_digest=None, unit_class=None,
             provenance=None, event=None):
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
    argv = [str(GATE)]
    if event is not None:
        argv += ["--event", event]
    return subprocess.run(argv, capture_output=True, text=True, cwd=ROOT, env=env)


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


class VerifyGateTrustBoundary(unittest.TestCase):
    """#112: the gate is advisory when provenance is in-session, sound when off-worker."""

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

    def test_stop_no_manifest_allows(self):
        self.assertEqual(run_gate(None, event="stop").returncode, 0)

    def test_task_no_manifest_blocks(self):
        self.assertEqual(run_gate(None, event="task").returncode, 2)

    def test_stop_with_manifest_still_verifies(self):
        src = _src(["AC-1"])
        m = _manifest(src, ["AC-1"], ["AC-1"])
        r = run_gate(m, src, _digest(src), unit_class="report-only", event="stop")
        self.assertEqual(r.returncode, 0, r.stderr)

if __name__ == "__main__":
    unittest.main(verbosity=2)
