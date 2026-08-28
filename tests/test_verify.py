#!/usr/bin/env python3
"""Negative-path tests for runtime/scripts/verify.py.

The verifier trusts NOTHING in the worker's manifest it can check against an authority: the
coordinator's frozen contract (scope), GitHub (review), the artifact/replay (negative control).
Each check must fail closed.
"""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("verify", ROOT / "runtime" / "scripts" / "verify.py")
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


def _src(ids):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    f.write("frozen\n" + "".join(f"- {i}: x\n" for i in ids))
    f.close()
    return f.name


def _digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_text(encoding="utf-8").encode()).hexdigest()


class ScopeCheck(unittest.TestCase):
    """Issue 1: the denominator is the coordinator's authoritative contract, not the manifest."""

    def _fatal(self, m, src, dig):
        return [e for e in verify.check_scope(m, src, dig) if not e.startswith("NOTE:")]

    def test_no_authoritative_contract_fails_closed(self):
        m = {"contract": {"criterion_ids": ["AC-1"]}, "criteria": [{"id": "AC-1"}]}
        self.assertTrue(any("no authoritative contract" in e for e in self._fatal(m, None, None)))

    def test_full_scope_passes(self):
        p = _src(["AC-1"])
        m = {"contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1"]},
             "criteria": [{"id": "AC-1"}]}
        self.assertEqual(self._fatal(m, p, _digest(p)), [])

    def test_scope_shrink_fails(self):
        p = _src(["AC-1", "AC-2"])
        m = {"contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1", "AC-2"]},
             "criteria": [{"id": "AC-1"}]}
        self.assertTrue(any("scope shrunk" in e for e in self._fatal(m, p, _digest(p))))

    def test_denominator_swap_fails(self):
        # the reviewer's case: worker points its OWN contract at a shrunken source; the coordinator's
        # authoritative digest is the full contract, so the swap is caught.
        shrunk, full = _src(["AC-1"]), _src(["AC-1", "AC-2"])
        m = {"contract": {"source": shrunk, "digest": _digest(shrunk), "criterion_ids": ["AC-1"]},
             "criteria": [{"id": "AC-1"}]}
        fatal = self._fatal(m, full, _digest(full))
        self.assertTrue(any("swap" in e or "scope shrunk" in e for e in fatal), fatal)

    def test_digest_mismatch_fails(self):
        p = _src(["AC-1"])
        m = {"contract": {"source": p, "criterion_ids": ["AC-1"]}, "criteria": [{"id": "AC-1"}]}
        self.assertTrue(any("does not match --contract-digest" in e
                            for e in self._fatal(m, p, "sha256:deadbeef")))


class FreshnessCheck(unittest.TestCase):
    def test_stale_review_fails(self):
        self.assertTrue(any("stale review" in e for e in
                            verify.check_freshness({"head_sha": "a", "pr": {"reviewed_sha": "b"}})))

    def test_fresh_review_passes(self):
        self.assertEqual(verify.check_freshness({"head_sha": "a", "pr": {"reviewed_sha": "a"}}), [])


class ReviewCheck(unittest.TestCase):
    """Issue 2: mutation review state comes from GitHub, not the manifest; fail-closed."""

    def test_review_ok_pure(self):
        self.assertTrue(verify.review_ok([{"state": "APPROVED", "commit_id": "H"}], "H"))
        self.assertFalse(verify.review_ok([{"state": "COMMENTED", "commit_id": "H"}], "H"))
        self.assertFalse(verify.review_ok([{"state": "APPROVED", "commit_id": "OLD"}], "H"))

    def test_mutation_without_pr_number_fails_closed(self):
        m = {"unit": "ship-it", "unit_class": "mutation", "head_sha": "H"}
        self.assertTrue(any("unreviewed" in e or "pr.number" in e for e in verify.check_review(m, "o/r")))

    def test_report_only_skips_review(self):
        self.assertEqual(verify.check_review({"unit": "review-it", "unit_class": "report-only"}, "o/r"), [])


class NegativeControlCheck(unittest.TestCase):
    def _artifact(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        f.write(text)
        f.close()
        return f.name

    def test_missing_nc_fails(self):
        self.assertTrue(any("negative_control" in e for e in
                            verify.check_negative_control({"unit": "ship-it"})))

    def test_arbitrary_strings_fail(self):
        m = {"unit": "ship-it", "negative_control": {"tool": "x", "result": "y"}}
        self.assertTrue(any("negative_control" in e for e in verify.check_negative_control(m)))

    def test_uncorroborating_artifact_fails(self):
        art = self._artifact("nothing to see here\n")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": art}}
        self.assertTrue(any("artifact does not" in e for e in verify.check_negative_control(m)))

    def test_corroborating_artifact_passes(self):
        art = self._artifact("mutant m#7 was KILLED\n")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": art}}
        self.assertEqual(verify.check_negative_control(m), [])

    def test_report_only_unit_skips_nc(self):
        self.assertEqual(
            verify.check_negative_control({"unit": "review-it", "unit_class": "report-only"}), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
