#!/usr/bin/env python3
"""Smoke tests for runtime/scripts/verify-gate.sh (#77).

The completion-gate hook entrypoint must FAIL CLOSED: block (exit 2) when there is nothing to
verify or the verifier fails, allow (exit 0) only when the manifest passes.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "runtime" / "scripts" / "verify-gate.sh"


def run_gate(manifest_path=None):
    env = {"PATH": __import__("os").environ.get("PATH", "")}
    args = [str(GATE)]
    if manifest_path is not None:
        env["ORCA_MANIFEST"] = str(manifest_path)
    return subprocess.run(args, capture_output=True, text=True, cwd=ROOT, env=env)


class VerifyGateFailsClosed(unittest.TestCase):
    def test_no_manifest_blocks(self):
        r = run_gate(None)
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_good_manifest_allows(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({
                "unit": "review-it", "unit_class": "report-only",
                "base_sha": "HEAD", "head_sha": "HEAD",
                "contract": {"criterion_ids": ["AC-1"]},
                "criteria": [{"id": "AC-1", "addressed": True}],
                "pr": {"reviewed_sha": "HEAD"},
            }, fh)
            path = fh.name
        r = run_gate(path)
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")

    def test_scope_shrink_blocks(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({
                "unit": "review-it", "unit_class": "report-only",
                "base_sha": "HEAD", "head_sha": "HEAD",
                "contract": {"criterion_ids": ["AC-1", "AC-2"]},
                "criteria": [{"id": "AC-1"}],
            }, fh)
            path = fh.name
        r = run_gate(path)
        self.assertEqual(r.returncode, 2, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
