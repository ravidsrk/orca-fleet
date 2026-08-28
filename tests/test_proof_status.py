#!/usr/bin/env python3
"""Tests for runtime/scripts/proof_status.py against a synthetic three-mission catalog.

Fixtures: a doctrine-only mission, a self-run mission whose proof_evidence resolves,
and a self-run mission whose proof_evidence is missing. Covers the frozen AC-1/2/3.
"""
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "proof_status", ROOT / "runtime" / "scripts" / "proof_status.py"
)
proof_status = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(proof_status)


def _mission(skills_dir, dirname, name, proof, proof_evidence=None):
    d = skills_dir / dirname
    d.mkdir(parents=True)
    lines = ["---", f"name: {name}", "license: MIT", f"proof: {proof}"]
    if proof_evidence is not None:
        lines.append(f"proof_evidence: {proof_evidence}")
    lines += ["autonomy: L3", "---", "", "# body", ""]
    (d / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


class ProofStatus(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        skills = self.root / "skills"
        skills.mkdir()
        # A resolvable evidence report for the good self-run mission.
        runs = self.root / "docs" / "runs"
        runs.mkdir(parents=True)
        (runs / "good-self-run.md").write_text("evidence\n", encoding="utf-8")
        _mission(skills, "alpha-doc", "alpha-doc", "doctrine-only")
        _mission(skills, "beta-good", "beta-good", "self-run",
                 "docs/runs/good-self-run.md")
        _mission(skills, "gamma-bad", "gamma-bad", "self-run",
                 "docs/runs/does-not-exist.md")
        self.records = proof_status.collect(skills, self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def _report(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = proof_status.main(["--root", str(self.root), *argv])
        return code, buf.getvalue()

    def test_ac1_every_mission_appears_once(self):
        # Each of the three fixtures shows up exactly once in the report.
        _, out = self._report()
        for name in ("alpha-doc", "beta-good", "gamma-bad"):
            self.assertEqual(out.count(name), 1, f"{name} should appear exactly once")
        # And the underlying record set has one entry per mission dir.
        self.assertEqual(sorted(r["dir"] for r in self.records),
                         ["alpha-doc", "beta-good", "gamma-bad"])

    def test_ac1_evidence_resolution(self):
        by = {r["dir"]: r for r in self.records}
        self.assertTrue(by["beta-good"]["evidence_resolves"])
        self.assertFalse(by["gamma-bad"]["evidence_resolves"])
        self.assertIsNone(by["alpha-doc"]["proof_evidence"])

    def test_ac2_rollup_counts(self):
        counts = proof_status.rollup(self.records)
        self.assertEqual(counts["doctrine-only"], 1)
        self.assertEqual(counts["self-run"], 2)
        self.assertEqual(counts["external-run"], 0)
        self.assertEqual(counts["total"], 3)
        # Rollup is rendered in the human report.
        _, out = self._report()
        self.assertIn("coverage rollup:", out)
        self.assertIn("total", out)

    def test_ac3_check_nonzero_when_evidence_missing(self):
        code, _ = self._report("--check")
        self.assertNotEqual(code, 0)

    def test_ac3_check_zero_when_all_resolve(self):
        # Fix the bad mission's evidence, then --check must pass.
        (self.root / "docs" / "runs" / "does-not-exist.md").write_text(
            "now here\n", encoding="utf-8")
        code, _ = self._report("--check")
        self.assertEqual(code, 0)

    def test_ac3_default_report_exits_zero(self):
        code, _ = self._report()
        self.assertEqual(code, 0)

    def test_ac3_json_records(self):
        code, out = self._report("--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(len(data), 3)
        by = {r["name"]: r for r in data}
        self.assertEqual(by["alpha-doc"]["proof"], "doctrine-only")
        self.assertIsNone(by["alpha-doc"]["proof_evidence"])
        self.assertTrue(by["beta-good"]["evidence_resolves"])
        self.assertEqual(by["beta-good"]["proof_evidence"], "docs/runs/good-self-run.md")
        self.assertFalse(by["gamma-bad"]["evidence_resolves"])
        # JSON with --check still non-zero (gamma-bad unresolved).
        code_check, _ = self._report("--json", "--check")
        self.assertNotEqual(code_check, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
