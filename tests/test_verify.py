#!/usr/bin/env python3
"""Negative-path tests for runtime/scripts/verify.py (#76).

verify.py is the separate-process, deterministic re-derivation of an evidence manifest.
Its deterministic checks (no git, no network) must each fail closed — a verifier that
can't fail is not a gate.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "verify", ROOT / "runtime" / "scripts" / "verify.py"
)
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


class ScopeCheck(unittest.TestCase):
    """Issue 1 fix: scope is re-derived from the FROZEN contract.source, not compared between two
    manifest-controlled fields; fail-closed when the source cannot be re-read."""

    def _src(self, ids):
        fh = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        fh.write("frozen contract\n" + "".join(f"- {i}: x\n" for i in ids))
        fh.close()
        return fh.name

    def _fatal(self, m):
        return [e for e in verify.check_scope(m) if not e.startswith("NOTE:")]

    def test_scope_shrink_fails(self):
        m = {"contract": {"source": self._src(["AC-1", "AC-2"]), "criterion_ids": ["AC-1", "AC-2"]},
             "criteria": [{"id": "AC-1"}]}
        self.assertTrue(any("scope shrunk" in e for e in self._fatal(m)), self._fatal(m))

    def test_full_scope_passes(self):
        m = {"contract": {"source": self._src(["AC-1"]), "criterion_ids": ["AC-1"]},
             "criteria": [{"id": "AC-1"}]}
        self.assertEqual(self._fatal(m), [])

    def test_missing_source_fails_closed(self):
        m = {"contract": {"criterion_ids": ["AC-1"]}, "criteria": [{"id": "AC-1"}]}
        self.assertTrue(any("cannot re-derive" in e for e in self._fatal(m)))

    def test_dropped_from_both_manifest_fields_still_fails(self):
        # the reviewer's exact case: AC-2 dropped from BOTH criterion_ids and criteria; the frozen
        # source still carries it, so re-derivation catches it.
        m = {"contract": {"source": self._src(["AC-1", "AC-2"]), "criterion_ids": ["AC-1"]},
             "criteria": [{"id": "AC-1"}]}
        self.assertTrue(any("scope shrunk" in e for e in self._fatal(m)), self._fatal(m))


class FreshnessCheck(unittest.TestCase):
    def test_stale_review_fails(self):
        m = {"head_sha": "abc123", "pr": {"reviewed_sha": "def456"}}
        self.assertTrue(any("stale review" in e for e in verify.check_freshness(m)))

    def test_fresh_review_passes(self):
        m = {"head_sha": "abc123", "pr": {"reviewed_sha": "abc123"}}
        self.assertEqual(verify.check_freshness(m), [])

    def test_mutation_unit_missing_reviewed_sha_fails(self):
        m = {"unit": "ship-it", "unit_class": "mutation", "head_sha": "abc123"}
        self.assertTrue(any("reviewed_sha" in e for e in verify.check_freshness(m)))


class NegativeControlCheck(unittest.TestCase):
    def test_mutation_unit_missing_nc_fails(self):
        m = {"unit": "ship-it"}
        self.assertTrue(any("negative_control" in e for e in verify.check_negative_control(m)))

    def test_arbitrary_strings_fail(self):
        m = {"unit": "ship-it", "negative_control": {"tool": "x", "result": "y"}}
        self.assertTrue(any("negative_control" in e for e in verify.check_negative_control(m)))

    def test_structured_nc_passes(self):
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "mutmut#7 validate.py:42", "result": "mutant KILLED",
            "artifact": "docs/reports/x/negctrl.txt"}}
        self.assertEqual(verify.check_negative_control(m), [])

    def test_report_only_unit_skips_nc(self):
        m = {"unit": "review-it", "unit_class": "report-only"}
        self.assertEqual(verify.check_negative_control(m), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
