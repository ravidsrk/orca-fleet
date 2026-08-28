#!/usr/bin/env python3
"""Negative-path tests for runtime/scripts/verify.py (#76).

verify.py is the separate-process, deterministic re-derivation of an evidence manifest.
Its deterministic checks (no git, no network) must each fail closed — a verifier that
can't fail is not a gate.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "verify", ROOT / "runtime" / "scripts" / "verify.py"
)
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


class ScopeCheck(unittest.TestCase):
    def test_scope_shrink_fails(self):
        m = {"contract": {"criterion_ids": ["AC-1", "AC-2"]}, "criteria": [{"id": "AC-1"}]}
        self.assertTrue(any("scope shrunk" in e for e in verify.check_scope(m)), verify.check_scope(m))

    def test_full_scope_passes(self):
        m = {"contract": {"criterion_ids": ["AC-1"]}, "criteria": [{"id": "AC-1"}]}
        self.assertEqual(verify.check_scope(m), [])

    def test_empty_scope_fails(self):
        self.assertTrue(any("scope undefined" in e for e in verify.check_scope({})))


class FreshnessCheck(unittest.TestCase):
    def test_stale_review_fails(self):
        m = {"head_sha": "abc123", "pr": {"reviewed_sha": "def456"}}
        self.assertTrue(any("stale review" in e for e in verify.check_freshness(m)))

    def test_fresh_review_passes(self):
        m = {"head_sha": "abc123", "pr": {"reviewed_sha": "abc123"}}
        self.assertEqual(verify.check_freshness(m), [])


class NegativeControlCheck(unittest.TestCase):
    def test_mutation_unit_missing_nc_fails(self):
        m = {"unit": "ship-it"}
        self.assertTrue(any("negative_control" in e for e in verify.check_negative_control(m)))

    def test_mutation_unit_with_nc_passes(self):
        m = {"unit": "ship-it", "negative_control": {"tool": "mutmut", "result": "KILLED"}}
        self.assertEqual(verify.check_negative_control(m), [])

    def test_report_only_unit_skips_nc(self):
        m = {"unit": "review-it", "unit_class": "report-only"}
        self.assertEqual(verify.check_negative_control(m), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
