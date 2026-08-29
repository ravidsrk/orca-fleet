#!/usr/bin/env python3
"""Negative-path tests for runtime/scripts/verify.py.

The verifier trusts NOTHING in the worker's manifest it can check against an authority: the
coordinator's frozen contract (scope) and dispatch-supplied unit class, GitHub (review), and the
artifact (negative control). Each check must fail closed.
"""
import hashlib
import importlib.util
import json
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


def _crit(*ids):
    return [{"id": i, "addressed": True} for i in ids]


class ScopeCheck(unittest.TestCase):
    """The denominator is the coordinator's authoritative contract, not the manifest."""

    def _fatal(self, m, src, dig):
        return [e for e in verify.check_scope(m, src, dig) if not e.startswith("NOTE:")]

    def test_no_authoritative_contract_fails_closed(self):
        m = {"contract": {"criterion_ids": ["AC-1"]}, "criteria": _crit("AC-1")}
        self.assertTrue(any("no authoritative contract" in e for e in self._fatal(m, None, None)))

    def test_full_scope_passes(self):
        p = _src(["AC-1"])
        m = {"contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1")}
        self.assertEqual(self._fatal(m, p, _digest(p)), [])

    def test_scope_shrink_fails(self):
        p = _src(["AC-1", "AC-2"])
        m = {"contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1", "AC-2"]},
             "criteria": _crit("AC-1")}
        self.assertTrue(any("not addressed" in e or "scope shrunk" in e
                            for e in self._fatal(m, p, _digest(p))))

    def test_unaddressed_criterion_fails(self):
        # #111: a criterion present but addressed != true is unmet work, not a waiver.
        p = _src(["AC-1"])
        m = {"contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1"]},
             "criteria": [{"id": "AC-1", "addressed": False, "note": "I did NOT do this"}]}
        self.assertTrue(any("not addressed" in e for e in self._fatal(m, p, _digest(p))))

    def test_denominator_swap_fails(self):
        shrunk, full = _src(["AC-1"]), _src(["AC-1", "AC-2"])
        m = {"contract": {"source": shrunk, "digest": _digest(shrunk), "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1")}
        fatal = self._fatal(m, full, _digest(full))
        self.assertTrue(any("swap" in e or "not addressed" in e for e in fatal), fatal)

    def test_digest_mismatch_fails(self):
        p = _src(["AC-1"])
        m = {"contract": {"source": p, "criterion_ids": ["AC-1"]}, "criteria": _crit("AC-1")}
        self.assertTrue(any("does not match --contract-digest" in e
                            for e in self._fatal(m, p, "sha256:deadbeef")))


class UnitClassSelection(unittest.TestCase):
    """#110: mutation-class comes from the dispatch, never the manifest; missing => mutation."""

    def test_is_mutation_fail_safe(self):
        self.assertTrue(verify._is_mutation(None))       # missing => mutation
        self.assertTrue(verify._is_mutation("mutation"))
        self.assertTrue(verify._is_mutation("garbage"))  # unknown => mutation
        self.assertFalse(verify._is_mutation("report-only"))
        self.assertFalse(verify._is_mutation("planning"))

    def test_manifest_unit_class_is_ignored(self):
        # A manifest self-declaring report-only is still gated as mutation when the dispatch says so.
        m = {"unit": "ship-it", "unit_class": "report-only", "head_sha": "H"}
        self.assertTrue(verify.check_review(m, "o/r", True))
        self.assertTrue(verify.check_negative_control(m, True))

    def test_end_to_end_unclassified_manifest_fails_closed(self):
        # A doc-schema-conformant manifest (no pr/nc, no dispatch class) must be gated as mutation.
        p = _src(["AC-1"])
        m = {"unit": "slice-2", "base_sha": "HEAD", "head_sha": "HEAD",
             "contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1")}
        fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(m, fh)
        fh.close()
        out, err = verify.verify(fh.name, p, _digest(p), repo="o/r", unit_class=None)
        self.assertIsNone(err)
        fatal, _notes = out
        self.assertTrue(fatal, "unclassified manifest must be gated as mutation and fail closed")


class FreshnessCheck(unittest.TestCase):
    def test_stale_review_fails(self):
        self.assertTrue(any("stale review" in e for e in
                            verify.check_freshness({"head_sha": "a", "pr": {"reviewed_sha": "b"}})))

    def test_fresh_review_passes(self):
        self.assertEqual(verify.check_freshness({"head_sha": "a", "pr": {"reviewed_sha": "a"}}), [])


class ReviewCheck(unittest.TestCase):
    def test_review_ok_pure(self):
        self.assertTrue(verify.review_ok([{"state": "APPROVED", "commit_id": "H"}], "H"))
        self.assertFalse(verify.review_ok([{"state": "COMMENTED", "commit_id": "H"}], "H"))
        self.assertFalse(verify.review_ok([{"state": "APPROVED", "commit_id": "OLD"}], "H"))

    def test_mutation_without_pr_number_fails_closed(self):
        m = {"unit": "ship-it", "head_sha": "H"}
        self.assertTrue(any("unreviewed" in e or "pr.number" in e
                            for e in verify.check_review(m, "o/r", True)))

    def test_report_only_skips_review(self):
        self.assertEqual(verify.check_review({"unit": "review-it"}, "o/r", False), [])


class NegativeControlCheck(unittest.TestCase):
    def _artifact(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        f.write(text)
        f.close()
        return f.name

    def test_missing_nc_fails(self):
        self.assertTrue(any("negative_control" in e for e in
                            verify.check_negative_control({"unit": "ship-it"}, True)))

    def test_arbitrary_strings_fail(self):
        m = {"unit": "ship-it", "negative_control": {"tool": "x", "result": "y"}}
        self.assertTrue(any("negative_control" in e for e in verify.check_negative_control(m, True)))

    def test_uncorroborating_artifact_fails(self):
        art = self._artifact("nothing to see here\n")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": art}}
        self.assertTrue(any("artifact does not" in e for e in verify.check_negative_control(m, True)))

    def test_corroborating_artifact_passes(self):
        art = self._artifact("mutant m#7 was KILLED\n")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": art}}
        self.assertEqual(verify.check_negative_control(m, True), [])

    def test_negation_artifact_fails(self):
        art = self._artifact("mutant m#7 SURVIVED — it was NOT killed\n")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": art}}
        self.assertTrue(any("SURVIVED" in e for e in verify.check_negative_control(m, True)))

    def test_execute_nc_is_fail_closed(self):
        art = self._artifact("mutant m#7 was KILLED\n")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": art}}
        self.assertTrue(any("execute-nc" in e for e in
                            verify.check_negative_control(m, True, execute=True)))

    def test_report_only_unit_skips_nc(self):
        self.assertEqual(verify.check_negative_control({"unit": "review-it"}, False), [])


class ReadSourceGuard(unittest.TestCase):
    """#116: a leading-dash ref/path must not reach `git show` as an option."""

    def test_option_like_ref_refused(self):
        _, err = verify.read_source("file.md@--output=/tmp/pwn")
        self.assertIn("refusing option-like", err or "")

    def test_option_like_path_refused(self):
        _, err = verify.read_source("--upload-pack=x@HEAD")
        self.assertIn("refusing option-like", err or "")


class MetaChecks(unittest.TestCase):
    """#114: intent packet, lighting legality, reviewer_mode legality — mutation-only."""

    def test_intent_required_for_mutation(self):
        self.assertTrue(verify.check_intent({"unit": "ship-it"}, True))
        self.assertTrue(verify.check_intent({"intent": {"goal": "g", "ruled_out": "", "why": "w"}}, True))
        self.assertEqual(
            verify.check_intent({"intent": {"goal": "g", "ruled_out": "r", "why": "w"}}, True), [])
        self.assertEqual(verify.check_intent({}, False), [])  # report-only skips

    def test_lighting_legal_for_mutation(self):
        self.assertTrue(verify.check_lighting({"lighting": "bright"}, True))
        self.assertTrue(verify.check_lighting({}, True))
        self.assertEqual(verify.check_lighting({"lighting": "lit"}, True), [])
        self.assertEqual(verify.check_lighting({"lighting": "dark-eligible"}, True), [])
        self.assertEqual(verify.check_lighting({}, False), [])

    def test_reviewer_mode_legal_for_mutation(self):
        self.assertTrue(verify.check_reviewer_mode({"reviewer_mode": "self"}, True))
        self.assertTrue(verify.check_reviewer_mode({}, True))
        self.assertEqual(verify.check_reviewer_mode({"reviewer_mode": "cross-vendor"}, True), [])
        self.assertEqual(verify.check_reviewer_mode({}, False), [])


class ReviewLookupBinding(unittest.TestCase):
    """#119 + #126: the GitHub review-lookup path is exercised; self-approval and superseded
    reviews do not count as an independent approval."""

    def setUp(self):
        self._orig_r = verify.fetch_reviews
        self._orig_a = verify.fetch_pr_author
        verify.fetch_pr_author = lambda repo, n: "pr-author"  # a resolved author, distinct from reviewers

    def tearDown(self):
        verify.fetch_reviews = self._orig_r
        verify.fetch_pr_author = self._orig_a

    def _m(self):
        return {"unit": "ship-it", "head_sha": "H", "pr": {"number": 7}}

    def test_approved_at_head_passes(self):
        verify.fetch_reviews = lambda repo, n: ([{"state": "APPROVED", "commit_id": "H",
                                                  "user": {"login": "carol"}}], None)
        self.assertEqual(verify.check_review(self._m(), "o/r", True), [])

    def test_no_approval_fails(self):
        verify.fetch_reviews = lambda repo, n: ([{"state": "COMMENTED", "commit_id": "H",
                                                  "user": {"login": "carol"}}], None)
        self.assertTrue(any("APPROVED" in e for e in verify.check_review(self._m(), "o/r", True)))

    def test_approval_at_wrong_sha_fails(self):
        verify.fetch_reviews = lambda repo, n: ([{"state": "APPROVED", "commit_id": "OLD",
                                                  "user": {"login": "carol"}}], None)
        self.assertTrue(any("APPROVED" in e for e in verify.check_review(self._m(), "o/r", True)))

    def test_fetch_error_fails_closed(self):
        verify.fetch_reviews = lambda repo, n: (None, "gh api failed")
        self.assertTrue(any("cannot fetch" in e for e in verify.check_review(self._m(), "o/r", True)))

    def test_author_self_approval_rejected(self):
        verify.fetch_reviews = lambda repo, n: ([{"state": "APPROVED", "commit_id": "H",
                                                  "user": {"login": "alice"}}], None)
        verify.fetch_pr_author = lambda repo, n: "alice"
        self.assertTrue(any("APPROVED" in e for e in verify.check_review(self._m(), "o/r", True)))

    def test_superseded_approval_not_counted(self):
        verify.fetch_reviews = lambda repo, n: (
            [{"state": "APPROVED", "commit_id": "H", "user": {"login": "bob"}},
             {"state": "COMMENTED", "commit_id": "H", "user": {"login": "bob"}}], None)
        self.assertTrue(any("APPROVED" in e for e in verify.check_review(self._m(), "o/r", True)))

    def test_independent_approval_passes_when_author_differs(self):
        verify.fetch_reviews = lambda repo, n: ([{"state": "APPROVED", "commit_id": "H",
                                                  "user": {"login": "carol"}}], None)
        verify.fetch_pr_author = lambda repo, n: "alice"
        self.assertEqual(verify.check_review(self._m(), "o/r", True), [])

    def test_unresolved_author_fails_closed(self):
        # #142: if the PR-author lookup fails, we cannot exclude a self-approval — fail closed,
        # never let the author's own approval satisfy the independent-review gate.
        verify.fetch_reviews = lambda repo, n: ([{"state": "APPROVED", "commit_id": "H",
                                                  "user": {"login": "alice"}}], None)
        verify.fetch_pr_author = lambda repo, n: None
        res = verify.check_review(self._m(), "o/r", True)
        self.assertTrue(any("cannot resolve" in e.lower() for e in res), res)

    def test_dark_eligible_waives_review(self):
        # #145: a dark-eligible unit (coordinator dispatch) lands without a human review; the
        # verifier waives the review leg (NOTE) — the negative control remains the oracle.
        verify.fetch_reviews = lambda repo, n: ([], None)
        res = verify.check_review(self._m(), "o/r", True, dispatch_lighting="dark-eligible")
        self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)


class ShasBinding(unittest.TestCase):
    """#119: base_sha/head_sha presence is the SHA-binding premise — bind it."""

    def test_missing_sha_fails(self):
        self.assertTrue(verify.check_shas_present({"head_sha": "H"}))
        self.assertTrue(verify.check_shas_present({}))

    def test_both_shas_present_ok(self):
        self.assertEqual(verify.check_shas_present({"base_sha": "a", "head_sha": "b"}), [])

    def test_symbolic_sha_fatal_for_mutation(self):
        errs = verify.check_real_commits({"base_sha": "HEAD", "head_sha": "HEAD"}, is_mutation=True)
        self.assertTrue(any("40-hex" in e and not e.startswith("NOTE:") for e in errs), errs)

    def test_symbolic_sha_advisory_for_report_only(self):
        errs = verify.check_real_commits({"base_sha": "HEAD", "head_sha": "HEAD"}, is_mutation=False)
        self.assertTrue(errs and all(e.startswith("NOTE:") for e in errs), errs)


class CriterionExtraction(unittest.TestCase):
    """#126: extraction catches hyphenated AND compact ids (over-count is fail-safe)."""

    def test_extracts_hyphenated_and_compact(self):
        ids = verify.extract_criterion_ids("- AC-1: x\n- SC12: y\n- REQ-3 z\n")
        self.assertEqual({"AC-1", "SC12", "REQ-3"}, ids)


class NoGhReviewLane(unittest.TestCase):
    """#118: the offline no-gh lane has a defined, non-silent pass path (a local reviewer artifact)."""

    def _artifact(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        f.write(text)
        f.close()
        return f.name

    def test_no_gh_with_reviewer_artifact_passes_as_note(self):
        art = self._artifact("reviewed HEADSHA123 — approved by a fresh reviewer\n")
        m = {"unit": "ship-it", "head_sha": "HEADSHA123", "review": {"artifact": art}}
        res = verify.check_review(m, None, True, no_gh=True, corroborated=True)
        self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)

    def test_no_gh_uncorroborated_fails_closed(self):
        # #138: without an out-of-band coordinator contract the local artifact is worker-forgeable.
        art = self._artifact("reviewed HEADSHA123 — approved by a fresh reviewer\n")
        m = {"unit": "ship-it", "head_sha": "HEADSHA123", "review": {"artifact": art}}
        res = verify.check_review(m, None, True, no_gh=True, corroborated=False)
        self.assertTrue(any("forgeable" in e and not e.startswith("NOTE:") for e in res), res)

    def test_no_gh_missing_artifact_fails_closed(self):
        m = {"unit": "ship-it", "head_sha": "H", "review": {}}
        res = verify.check_review(m, None, True, no_gh=True)
        self.assertTrue(any(not e.startswith("NOTE:") for e in res), res)

    def test_no_gh_artifact_not_referencing_head_fails(self):
        art = self._artifact("reviewed some other sha\n")
        m = {"unit": "ship-it", "head_sha": "HEADSHA123", "review": {"artifact": art}}
        res = verify.check_review(m, None, True, no_gh=True)
        self.assertTrue(any("does not reference head_sha" in e for e in res), res)

class MalformedManifest(unittest.TestCase):
    """#137: a malformed manifest must fail closed as an invariant failure, never crash the gate."""

    def _tmp(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        f.write(text)
        f.close()
        return f.name

    def test_non_object_manifest_rejected(self):
        m, err = verify.load_manifest(self._tmp("[1, 2, 3]"))
        self.assertIsNone(m)
        self.assertIn("JSON object", err)

    def test_non_dict_intent_does_not_crash(self):
        errs = verify.check_intent({"intent": "just a string"}, True)
        self.assertTrue(any("intent packet" in e for e in errs), errs)

    def test_non_scalar_lighting_does_not_crash(self):
        errs = verify.check_lighting({"lighting": ["lit"]}, True)
        self.assertTrue(any("lighting must be" in e for e in errs), errs)

    def test_non_scalar_reviewer_mode_does_not_crash(self):
        errs = verify.check_reviewer_mode({"reviewer_mode": {"x": 1}}, True)
        self.assertTrue(any("reviewer_mode must be" in e for e in errs), errs)

    def test_lighting_swap_detected(self):
        # #145: the dispatch lighting is authoritative; a worker manifest that swaps it fails.
        errs = verify.check_lighting({"lighting": "dark-eligible"}, True, dispatch_lighting="lit")
        self.assertTrue(any("swap" in e for e in errs), errs)

    def test_verify_wraps_check_exceptions(self):
        # A manifest shape that would raise inside a check becomes a fatal invariant, not a traceback.
        path = self._tmp('{"pr": "not-an-object", "head_sha": "H", "base_sha": "B"}')
        (fatal, notes), err = verify.verify(path, unit_class="mutation")
        self.assertIsNone(err)
        self.assertTrue(any("malformed manifest" in f for f in fatal), fatal)


class NegativeControlSurvivor(unittest.TestCase):
    """#137: survivor summaries (plural / percentage / count) must be rejected, not accepted."""

    def _m(self, artifact):
        return {"negative_control": {"tool": "mutmut", "result": "killed", "mutant": "m7",
                                     "artifact": artifact}}

    def _art(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        f.write(text)
        f.close()
        return f.name

    def test_percentage_survivor_rejected(self):
        art = self._art("m7 mutation applied. Mutants that survived: 1. 0.0% killed.\n")
        self.assertTrue(any("SURVIVED" in e for e in verify.check_negative_control(self._m(art), True)))

    def test_summary_counts_survivor_rejected(self):
        art = self._art("m7: Survived: 1 / Killed: 0\n")
        self.assertTrue(any("SURVIVED" in e for e in verify.check_negative_control(self._m(art), True)))

    def test_zero_mutants_killed_rejected(self):
        art = self._art("m7 ran; 0 mutants killed.\n")
        self.assertTrue(any("SURVIVED" in e for e in verify.check_negative_control(self._m(art), True)))

    def test_genuine_kill_still_passes(self):
        art = self._art("m7 KILLED — 1 killed, 0 survived. Proof went RED.\n")
        self.assertEqual(verify.check_negative_control(self._m(art), True), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
