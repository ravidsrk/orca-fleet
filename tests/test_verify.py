#!/usr/bin/env python3
"""Negative-path tests for runtime/scripts/verify.py.

The verifier trusts NOTHING in the worker's manifest it can check against an authority: the
coordinator's frozen contract (scope) and dispatch-supplied unit class, GitHub (review), and the
artifact (negative control). Each check must fail closed.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
    # Mirrors the coordinator's `shasum -a 256` — raw bytes, no newline translation (#180).
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


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
        res = verify.check_review(self._m(), "o/r", True, corroborated=True, dispatch_lighting="dark-eligible")
        self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)

    def test_dark_eligible_uncorroborated_fails_closed(self):
        # #149 review: a dark-eligible waiver on a worker-forgeable oracle (no out-of-band contract)
        # must fail closed — review is waived, but the oracle must be unfakeable.
        res = verify.check_review(self._m(), "o/r", True, corroborated=False, dispatch_lighting="dark-eligible")
        self.assertTrue(any("forgeable" in e and not e.startswith("NOTE:") for e in res), res)


class ReviewPagination(unittest.TestCase):
    """#167: fetch_reviews must follow ALL pages (`gh api --paginate`). Without it GitHub returns
    the first 30 reviews only, so a stale APPROVED on page 1 outranks the same reviewer's later
    CHANGES_REQUESTED, and a fresh APPROVED past page 1 is invisible. A fake `gh` on PATH
    (test_preflight.py pattern) emulates the real CLI: page 1 only without --paginate."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self._page1 = tmp / "page1.json"
        self._page2 = tmp / "page2.json"
        fakebin = tmp / "bin"
        fakebin.mkdir()
        gh = fakebin / "gh"
        gh.write_text(
            '#!/bin/sh\n'
            'case "$*" in\n'
            '  *reviews*)\n'
            '    case " $* " in\n'
            '      *" --paginate "*) cat "$FAKE_GH_PAGE1" "$FAKE_GH_PAGE2";;\n'
            '      *) cat "$FAKE_GH_PAGE1";;\n'
            '    esac;;\n'
            '  *) echo "{\\"user\\":{\\"login\\":\\"pr-author\\"}}";;\n'
            'esac\n',
            encoding="utf-8",
        )
        gh.chmod(0o755)
        self._env = {"PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
                     "FAKE_GH_PAGE1": str(self._page1),
                     "FAKE_GH_PAGE2": str(self._page2)}

    def tearDown(self):
        self._tmp.cleanup()

    def _verdict_with_pages(self, page1, page2):
        self._page1.write_text(json.dumps(page1) + "\n", encoding="utf-8")
        self._page2.write_text(json.dumps(page2) + "\n", encoding="utf-8")
        with mock.patch.dict(os.environ, self._env):
            return verify.check_review(
                {"unit": "ship-it", "head_sha": "H", "pr": {"number": 7}}, "o/r", True)

    @staticmethod
    def _filler(n):
        return [{"state": "COMMENTED", "commit_id": "H",
                 "user": {"login": f"bot{i}"}} for i in range(n)]

    def test_fetches_all_pages_31_review_fixture(self):
        # 31 reviews over two pages; the only APPROVED is review #31 — invisible on page 1 alone.
        res = self._verdict_with_pages(self._filler(30),
                                       [{"state": "APPROVED", "commit_id": "H",
                                         "user": {"login": "carol"}}])
        self.assertEqual(res, [])

    def test_page2_changes_requested_supersedes_page1_approval(self):
        page1 = self._filler(29) + [{"state": "APPROVED", "commit_id": "H",
                                     "user": {"login": "carol"}}]
        page2 = [{"state": "CHANGES_REQUESTED", "commit_id": "H",
                  "user": {"login": "carol"}}]
        res = self._verdict_with_pages(page1, page2)
        self.assertTrue(any("APPROVED" in e for e in res), res)

    def test_approval_only_on_page2_passes(self):
        res = self._verdict_with_pages(self._filler(30),
                                       [{"state": "APPROVED", "commit_id": "H",
                                         "user": {"login": "carol"}}])
        self.assertEqual(res, [])

    def test_gh_error_fails_closed(self):
        self._page1.write_text("not json\n", encoding="utf-8")
        self._page2.write_text("not json\n", encoding="utf-8")
        with mock.patch.dict(os.environ, self._env):
            res = verify.check_review(
                {"unit": "ship-it", "head_sha": "H", "pr": {"number": 7}}, "o/r", True)
        self.assertTrue(any("cannot fetch" in e for e in res), res)


class PaginatedJsonParsing(unittest.TestCase):
    """#167: `gh api --paginate` concatenates one JSON array per page; the parse step merges them
    and fails closed on malformed output."""

    def test_single_array_still_parses(self):
        items, err = verify.parse_review_pages(json.dumps([{"state": "APPROVED"}]))
        self.assertIsNone(err)
        self.assertEqual(items, [{"state": "APPROVED"}])

    def test_concatenated_arrays_merge(self):
        out = json.dumps([{"a": 1}]) + "\n" + json.dumps([{"b": 2}]) + "\n"
        items, err = verify.parse_review_pages(out)
        self.assertIsNone(err)
        self.assertEqual(items, [{"a": 1}, {"b": 2}])

    def test_malformed_output_fails_closed(self):
        items, err = verify.parse_review_pages('[{"a": 1}]\nnot json')
        self.assertIsNone(items)
        self.assertTrue(err)

    def test_non_array_page_fails_closed(self):
        items, err = verify.parse_review_pages('{"unexpected": "object"}')
        self.assertIsNone(items)
        self.assertTrue(err)


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


class RawByteDigest(unittest.TestCase):
    """#180: the scope digest is computed over RAW BYTES, exactly what the coordinator's
    `shasum -a 256` sees — a CRLF contract must verify against its byte digest, and an LF
    contract's digest must be unchanged (byte-identical behavior for LF files)."""

    def _write(self, raw):
        f = tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False)
        f.write(raw)
        f.close()
        return f.name

    def test_crlf_contract_matches_shasum_digest(self):
        raw = b"frozen\r\n- AC-1: x\r\n- AC-2: y\r\n"
        p = self._write(raw)
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()  # the coordinator's shasum digest
        m = {"contract": {"source": p, "digest": digest, "criterion_ids": ["AC-1", "AC-2"]},
             "criteria": _crit("AC-1", "AC-2")}
        fatal = [e for e in verify.check_scope(m, p, digest) if not e.startswith("NOTE:")]
        self.assertEqual(fatal, [])

    def test_lf_digest_unchanged(self):
        raw = b"frozen\n- AC-1: x\n"
        p = self._write(raw)
        # Pinned to the pre-#180 value: LF files must hash byte-identically to before.
        digest = "sha256:07af39c8585de6b596a28a05c0cfe432a25c294bb2166c1ffeef1db4901abf8a"
        m = {"contract": {"source": p, "digest": digest, "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1")}
        fatal = [e for e in verify.check_scope(m, p, digest) if not e.startswith("NOTE:")]
        self.assertEqual(fatal, [])

    def test_crlf_contract_via_git_ref_matches_shasum_digest(self):
        # The coordinator lane: `path@gitref` goes through `_run_bytes(["git", "show", ...])`.
        # Commit a CRLF contract (autocrlf off so the blob keeps its raw bytes) and verify
        # against the shasum digest — text=True capture would normalize CRLF away and wedge.
        raw = b"frozen\r\n- AC-1: x\r\n"
        with tempfile.TemporaryDirectory() as repo:
            Path(repo, "contract.md").write_bytes(raw)

            def git(*args):
                subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True)

            git("init", "-q")
            git("-c", "core.autocrlf=false", "add", "contract.md")
            git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "freeze")
            digest = "sha256:" + hashlib.sha256(raw).hexdigest()
            m = {"contract": {"source": "contract.md@HEAD", "digest": digest,
                              "criterion_ids": ["AC-1"]},
                 "criteria": _crit("AC-1")}
            cwd = os.getcwd()
            os.chdir(repo)  # read_source's `git show` runs in the process cwd
            try:
                res = verify.check_scope(m, "contract.md@HEAD", digest)
            finally:
                os.chdir(cwd)
            fatal = [e for e in res if not e.startswith("NOTE:")]
            self.assertEqual(fatal, [])


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


class ProvenanceCheck(unittest.TestCase):
    """#91 review: a manifest claiming a regulated standard must carry the audit fields, else it is
    incomplete evidence masquerading as an Art-12/50 record."""

    def test_incomplete_provenance_with_standard_fails(self):
        errs = verify.check_provenance({"provenance": {"standard": "EU-AI-Act-Art-12"}})
        self.assertTrue(any("audit fields" in e for e in errs), errs)

    def test_complete_provenance_passes(self):
        prov = {"standard": "SOC2", "spec_version": "v1", "model": "m", "reviewer": "r@t",
                "retention": "s3://audit"}
        self.assertEqual(verify.check_provenance({"provenance": prov}), [])

    def test_no_standard_claim_skips(self):
        self.assertEqual(verify.check_provenance({"provenance": {"standard": "none"}}), [])
        self.assertEqual(verify.check_provenance({}), [])

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

    def test_malformed_manifest_exits_2(self):
        # #149 review: a malformed manifest is an invariant failure (exit 2), not a usage/dep error (1).
        self.assertEqual(verify.main(["--manifest", self._tmp("[1, 2, 3]")]), 2)


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
        self.assertTrue(verify.check_negative_control(self._m(art), True))

    def test_summary_counts_survivor_rejected(self):
        art = self._art("m7: Survived: 1 / Killed: 0\n")
        self.assertTrue(verify.check_negative_control(self._m(art), True))

    def test_zero_mutants_killed_rejected(self):
        art = self._art("m7 ran; 0 mutants killed.\n")
        self.assertTrue(verify.check_negative_control(self._m(art), True))

    def test_pinned_mutant_survived_rejected(self):
        art = self._art("Run over 4 mutants: 3 killed. m7 survived the revert.\n")
        self.assertTrue(any("SURVIVED" in e for e in verify.check_negative_control(self._m(art), True)))

    def test_pinned_survivor_with_delimiter_rejected(self):
        # #152 review: "m7: Survived: 1" (colon-delimited) while OTHER mutants were killed must still
        # reject — the pinned mutant survived. A zero count ("survived: 0") is a kill, not a survivor.
        art = self._art("Run over 4 mutants: 3 killed. m7: Survived: 1.\n")
        self.assertTrue(any("SURVIVED" in e for e in verify.check_negative_control(self._m(art), True)))

    def test_pinned_zero_survivors_passes(self):
        art = self._art("m7 revert applied. m7: survived: 0. 1 killed, RED.\n")
        self.assertEqual(verify.check_negative_control(self._m(art), True), [])

    def test_pinned_zero_survivors_dash_delimited_passes(self):
        # #154 review: the zero-count lookahead must accept the same delimiters as the prefix, so
        # "m7 - survived - 0" (zero survivors) is a kill, not a false survivor.
        art = self._art("m7 revert applied. m7 - survived - 0. 1 killed, RED.\n")
        self.assertEqual(verify.check_negative_control(self._m(art), True), [])

    def test_pinned_survivor_greater_than_zero_rejected(self):
        # #155 review: "m7 survived > 0" is a survivor, not a zero count — must reject.
        art = self._art("Run: 3 killed. m7 survived > 0.\n")
        self.assertTrue(any("SURVIVED" in e for e in verify.check_negative_control(self._m(art), True)))

    def test_multimutant_run_with_pinned_killed_passes(self):
        # #149 review: a multi-mutant run where OTHER mutants survived but the pinned mutant m7 was
        # killed is valid — the whole-artifact survivor scan must not reject it.
        art = self._art("m7 KILLED. Summary: 5 mutants, 2 survived, 3 killed. Proof went RED.\n")
        self.assertEqual(verify.check_negative_control(self._m(art), True), [])

    def test_genuine_kill_still_passes(self):
        art = self._art("m7 KILLED — 1 killed, 0 survived. Proof went RED.\n")
        self.assertEqual(verify.check_negative_control(self._m(art), True), [])


_edspec = importlib.util.spec_from_file_location("ed25519", ROOT / "runtime" / "scripts" / "ed25519.py")
ed = importlib.util.module_from_spec(_edspec)
_edspec.loader.exec_module(ed)
_dsspec = importlib.util.spec_from_file_location("dispatch_sign", ROOT / "runtime" / "scripts" / "dispatch-sign.py")
dispatch_sign = importlib.util.module_from_spec(_dsspec)
_dsspec.loader.exec_module(dispatch_sign)


class DispatchProvenance(unittest.TestCase):
    """#135: a coordinator-signed dispatch record makes the native in-session path sound — a worker
    that substitutes the digest / class / lighting, forges the record, or omits it is caught."""

    def _signed(self, record, seed=None, sign_key=None):
        import base64
        seed = seed or bytes(range(1, 33))
        pub = ed.publickey(seed)
        sig = ed.signature(verify._canonical_dispatch(record), sign_key or seed, ed.publickey(sign_key) if sign_key else pub)
        env = {"record": record, "sig_b64": base64.b64encode(sig).decode()}
        rec = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); rec.write(json.dumps(env)); rec.close()
        pk = tempfile.NamedTemporaryFile("w", suffix=".pub", delete=False); pk.write(pub.hex()); pk.close()
        return rec.name, pk.name

    _M = {"unit": "u"}

    def test_verified_provenance_passes(self):
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation", "lighting": "lit"})
        res = verify.check_dispatch_provenance(self._M, "sha256:a", "mutation", "lit", rec, pk)
        self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)

    def test_substituted_digest_caught(self):
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:REAL", "unit_class": "mutation"})
        res = verify.check_dispatch_provenance(self._M, "sha256:WEAKER", "mutation", None, rec, pk)
        self.assertTrue(any("substitution" in e and not e.startswith("NOTE:") for e in res), res)

    def test_downgraded_class_caught(self):
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation"})
        res = verify.check_dispatch_provenance(self._M, "sha256:a", "report-only", None, rec, pk)
        self.assertTrue(any("substitution" in e for e in res), res)

    def test_flipped_lighting_caught(self):
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation", "lighting": "lit"})
        res = verify.check_dispatch_provenance(self._M, "sha256:a", "mutation", "dark-eligible", rec, pk)
        self.assertTrue(any("substitution" in e for e in res), res)

    def test_replayed_record_from_another_unit_caught(self):
        # #135 review: a valid record for unit 'u' must not certify a different manifest (replay).
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation"})
        res = verify.check_dispatch_provenance({"unit": "other-unit"}, "sha256:a", "mutation", None, rec, pk)
        self.assertTrue(any("does not bind this manifest" in e for e in res), res)

    def test_forged_signature_rejected(self):
        # record signed with a DIFFERENT key than the pinned pubkey → not coordinator-signed.
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation"},
                               seed=bytes(range(1, 33)), sign_key=bytes(range(100, 132)))
        res = verify.check_dispatch_provenance(self._M, "sha256:a", "mutation", None, rec, pk)
        self.assertTrue(any("INVALID" in e for e in res), res)

    def test_half_configured_fails_closed(self):
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation"})
        res = verify.check_dispatch_provenance(self._M, "sha256:a", "mutation", None, rec, None)
        self.assertTrue(any("half-configured" in e for e in res), res)
        res2 = verify.check_dispatch_provenance(self._M, "sha256:a", "mutation", None, None, pk)
        self.assertTrue(any("half-configured" in e for e in res2), res2)

    def test_no_provenance_is_advisory(self):
        self.assertEqual(verify.check_dispatch_provenance(self._M, "sha256:a", "mutation", "lit", None, None), [])

    def test_unsigned_used_field_fails_closed(self):
        # #162 review: a field the run uses but the record didn't sign is unbound — fail closed, don't
        # silently accept it (a worker could set an unsigned lighting freely).
        rec, pk = self._signed({"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation"})
        res = verify.check_dispatch_provenance(self._M, "sha256:a", "mutation", "dark-eligible", rec, pk)
        self.assertTrue(any("did not sign lighting" in e for e in res), res)

    def test_canonicalization_matches_signer(self):
        # cross-tool drift guard: the gate and the signer must canonicalize identically, else every
        # real signature would fail to verify.
        record = {"manifest_id": "u", "contract_digest": "sha256:a", "unit_class": "mutation", "lighting": "lit"}
        self.assertEqual(verify._canonical_dispatch(record), dispatch_sign.canonical_record(record))


if __name__ == "__main__":
    unittest.main(verbosity=2)
