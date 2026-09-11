#!/usr/bin/env python3
"""Negative-path tests for runtime/scripts/verify.py.

The verifier trusts NOTHING in the worker's manifest it can check against an authority: the
coordinator's frozen contract (scope) and dispatch-supplied unit class, GitHub (review), and the
artifact (negative control). Each check must fail closed.
"""
import contextlib
import hashlib
import importlib.util
import io
import itertools
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("verify", ROOT / "runtime" / "scripts" / "verify.py")
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


def _crit(*ids):
    return [{"id": i, "addressed": True} for i in ids]


_SRC_SEQ = itertools.count()


def _src(ids):
    """A frozen-contract fixture written into the CURRENT directory and named relatively — #267
    refuses absolute and out-of-repo evidence paths, so every fixture lives in the case's temp repo
    (all callers are RepoCase subclasses, which chdir there)."""
    rel = f"contract-{next(_SRC_SEQ)}.md"
    Path(rel).write_text("frozen\n" + "".join(f"- {i}: x\n" for i in ids), encoding="utf-8")
    return rel


def _digest(rel):
    # Mirrors the coordinator's `shasum -a 256` — raw bytes, no newline translation (#180).
    return "sha256:" + hashlib.sha256(Path(rel).read_bytes()).hexdigest()


class RepoCase(unittest.TestCase):
    """#267 bounds every evidence path to the git toplevel and requires a manifest-named artifact to
    be PINNED, so fixtures live INSIDE a hermetic temp repo and are named relatively — which is also
    how a real manifest names them. The process cwd is the repo for the duration of the test, since
    verify.py's git legs and path resolution both run there."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.repo = Path(self._td.name).resolve()
        self.git("init", "-q", "-b", "main")
        self._cwd = os.getcwd()
        os.chdir(self.repo)
        self.addCleanup(self._leave)

    def _leave(self):
        os.chdir(self._cwd)
        self._td.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message="c"):
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def write(self, rel, text):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
        return rel

    def src(self, ids, rel="contract.md"):
        return self.write(rel, "frozen\n" + "".join(f"- {i}: x\n" for i in ids))

    def digest(self, rel):
        # Mirrors the coordinator's `shasum -a 256` — raw bytes, no newline translation (#180).
        return "sha256:" + hashlib.sha256((self.repo / rel).read_bytes()).hexdigest()

    def artifact(self, text, rel="docs/reports/u/nc.txt"):
        return self.write(rel, text)

    def pin(self, rel):
        """An `artifacts[]` inventory entry pinning an UNTRACKED working-tree artifact (#267)."""
        return {"path": rel, "sha256": hashlib.sha256((self.repo / rel).read_bytes()).hexdigest()}


class ScopeCheck(RepoCase):
    """The denominator is the coordinator's authoritative contract, not the manifest."""

    def _fatal(self, m, src, dig):
        return [e for e in verify.check_scope(m, src, dig) if not e.startswith("NOTE:")]

    def test_no_authoritative_contract_fails_closed(self):
        m = {"contract": {"criterion_ids": ["AC-1"]}, "criteria": _crit("AC-1")}
        self.assertTrue(any("no authoritative contract" in e for e in self._fatal(m, None, None)))

    def test_full_scope_passes(self):
        p = self.src(["AC-1"])
        m = {"contract": {"source": p, "digest": self.digest(p), "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1")}
        self.assertEqual(self._fatal(m, p, self.digest(p)), [])

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


class UnitClassSelection(RepoCase):
    """#110: mutation-class comes from the dispatch, never the manifest; missing => mutation."""

    def test_is_mutation_fail_safe(self):
        self.assertTrue(verify._is_mutation(None))       # missing => mutation
        self.assertTrue(verify._is_mutation("mutation"))
        self.assertTrue(verify._is_mutation("garbage"))  # unknown => mutation
        self.assertFalse(verify._is_mutation("report-only"))
        self.assertFalse(verify._is_mutation("planning"))

    def test_manifest_unit_class_is_ignored(self):
        # #182: drive verify() itself — the selection point (is_mut = _is_mutation(unit_class),
        # the dispatch PARAMETER, never the manifest). A manifest self-declaring report-only,
        # verified with the dispatch parameter omitted (None => fail-safe) or explicit "mutation",
        # must get the mutation-strict verdict: missing pr.number, negative control, and intent
        # all fail. If verify() ever consulted m["unit_class"] this test goes red.
        p = _src(["AC-1"])
        m = {"unit": "slice-2", "unit_class": "report-only",
             "base_sha": "HEAD", "head_sha": "HEAD",
             "contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1")}
        fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(m, fh)
        fh.close()
        for cls in (None, "mutation"):
            out, err = verify.verify(fh.name, p, _digest(p), repo="o/r", unit_class=cls)
            self.assertIsNone(err)
            fatal, _notes = out
            self.assertTrue(any("unreviewed" in e or "pr.number" in e for e in fatal),
                            (cls, fatal))
            self.assertTrue(any("negative_control" in e for e in fatal), (cls, fatal))
            self.assertTrue(any("intent" in e for e in fatal), (cls, fatal))

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

    def _write_manifest(self, m):
        fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(m, fh)
        fh.close()
        return fh.name

    def _mutating_manifest(self):
        p = _src(["AC-1"])
        m = {"unit": "slice-2", "base_sha": "HEAD", "head_sha": "HEAD",
             "contract": {"source": p, "digest": _digest(p), "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1")}
        return p, self._write_manifest(m)

    def test_unknown_unit_class_notes_and_gates_as_mutation(self):
        # #178: an unknown class must reach _is_mutation's fallback — mutation-strict checks run
        # and a NOTE names the unknown value (docs/verify-gate.md: "missing/unknown => mutation").
        p, path = self._mutating_manifest()
        out, err = verify.verify(path, p, _digest(p), repo="o/r", unit_class="mutatoin")
        self.assertIsNone(err)
        fatal, notes = out
        self.assertTrue(any("NOTE:" in n and "mutatoin" in n for n in notes), notes)
        self.assertTrue(fatal, "unknown class must fail safe to mutation strictness")

    def test_unknown_unit_class_cli_is_not_a_usage_error(self):
        # #178: argparse choices= used to wedge the CLI before the fallback ran. main() must now
        # run the checks; the NOTE surfaces on stdout and fatals (not usage) decide the exit.
        p, path = self._mutating_manifest()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = verify.main(["--manifest", path, "--contract-source", p,
                              "--contract-digest", _digest(p), "--unit-class", "mutatoin",
                              "--repo", "o/r"])
        self.assertEqual(rc, 2, "a mutation-invariant failure, not an argparse wedge")
        self.assertIn("mutatoin", buf.getvalue())

    def test_legal_unit_classes_emit_no_unknown_note(self):
        # Legal values behave exactly as before: no unknown-class NOTE.
        for cls in ("mutation", "report-only", "planning", None):
            p, path = self._mutating_manifest()
            out, err = verify.verify(path, p, _digest(p), repo="o/r", unit_class=cls)
            self.assertIsNone(err)
            _fatal, notes = out
            self.assertFalse(any("unknown unit class" in n for n in notes), (cls, notes))


class FreshnessCheck(unittest.TestCase):
    def test_stale_review_fails(self):
        self.assertTrue(any("stale review" in e for e in
                            verify.check_freshness({"head_sha": "a", "pr": {"reviewed_sha": "b"}})))

    def test_fresh_review_passes(self):
        self.assertEqual(verify.check_freshness({"head_sha": "a", "pr": {"reviewed_sha": "a"}}), [])

    def test_wtree_equivalence_relaxes_a_content_identical_head_move(self):
        # reviewed-sha-freshness.md: a head move whose tree is identical to the reviewed content
        # does not void the review. Build two commits with the same tree and check.
        import subprocess, tempfile
        from pathlib import Path as P
        with tempfile.TemporaryDirectory() as tmp:
            env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                   "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin"}
            def g(*a, cwd=tmp):
                return subprocess.run(["git", *a], cwd=cwd, env=env, capture_output=True, text=True)
            g("init", "-q"); P(tmp, "f.txt").write_text("same content")
            g("add", "."); g("commit", "-qm", "one")
            old_head = g("rev-parse", "HEAD").stdout.strip()
            tree = g("rev-parse", "HEAD^{tree}").stdout.strip()
            g("commit", "--amend", "-qm", "one amended")  # same tree, new SHA
            new_head = g("rev-parse", "HEAD").stdout.strip()
            assert old_head != new_head
            m = {"head_sha": new_head,
                 "pr": {"reviewed_sha": old_head, "reviewed_wtree": tree}}
            cwd = __import__("os").getcwd()
            __import__("os").chdir(tmp)
            try:
                self.assertEqual(verify.check_freshness(m), [])
                # a real content change still voids
                P(tmp, "f.txt").write_text("different")
                g("add", "."); g("commit", "-qm", "two")
                m2 = {"head_sha": g("rev-parse", "HEAD").stdout.strip(),
                      "pr": {"reviewed_sha": old_head, "reviewed_wtree": tree}}
                self.assertTrue(any("stale review" in e for e in verify.check_freshness(m2)))
            finally:
                __import__("os").chdir(cwd)


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


class NegativeControlCheck(RepoCase):
    def _m(self, text, **nc):
        """A manifest whose NC artifact is written in-repo and PINNED by artifacts[] (#267)."""
        rel = self.artifact(text)
        return {"unit": "ship-it", "artifacts": [self.pin(rel)],
                "negative_control": {"artifact": rel, **nc}}

    def _errs(self, m, execute=False):
        errs, _executed = verify.check_negative_control(m, True, execute=execute)
        return errs

    def test_missing_nc_fails(self):
        self.assertTrue(any("negative_control" in e for e in self._errs({"unit": "ship-it"})))

    def test_arbitrary_strings_fail(self):
        m = {"unit": "ship-it", "negative_control": {"tool": "x", "result": "y"}}
        self.assertTrue(any("negative_control" in e for e in self._errs(m)))

    def test_uncorroborating_artifact_fails(self):
        m = self._m("nothing to see here\n", tool="mutmut", mutant="m#7", result="KILLED")
        self.assertTrue(any("artifact does not" in e for e in self._errs(m)))

    def test_corroborating_artifact_passes(self):
        m = self._m("mutant m#7 was KILLED\n", tool="mutmut", mutant="m#7", result="KILLED")
        self.assertEqual(self._errs(m), [])

    def test_negation_artifact_fails(self):
        m = self._m("mutant m#7 SURVIVED — it was NOT killed\n",
                    tool="mutmut", mutant="m#7", result="KILLED")
        self.assertTrue(any("SURVIVED" in e for e in self._errs(m)))

    def test_execute_nc_fails_closed_for_an_unreplayable_tool(self):
        # #255: replay exists for `revert` and `hand`. Every other tool under --execute-nc must
        # fail CLOSED — an unreplayable control is not an executed one, and a caller that ASKED
        # for execution must never get a pass built on a text read.
        m = self._m("mutant m#7 was KILLED\n", tool="mutmut", mutant="m#7", result="KILLED")
        errs, executed = verify.check_negative_control(m, True, execute=True)
        self.assertFalse(executed)
        self.assertTrue(any("no replay is implemented" in e for e in errs), errs)

    def test_report_only_unit_skips_nc(self):
        self.assertEqual(verify.check_negative_control({"unit": "review-it"}, False), ([], False))

    def test_hand_nc_without_quoted_diff_fails(self):
        # `hand` carries no pinned mutant id, so an artifact without the diff is unbound evidence.
        m = self._m("the suite went RED\n", tool="hand", result="RED")
        self.assertTrue(any("hand-written diff" in e for e in self._errs(m)))

    def test_hand_nc_with_quoted_diff_passes(self):
        m = self._m("--- a/x.py\n+++ b/x.py\n-old\n+new\nthe suite went RED\n",
                    tool="hand", result="RED")
        self.assertEqual(self._errs(m), [])

    def test_unpinned_working_tree_artifact_is_refused(self):
        # #267: present on disk, inside the repo, but neither tracked at head_sha nor carrying a
        # sha256 in artifacts[] — a file that can be rewritten between the run and the audit.
        rel = self.artifact("mutant m#7 was KILLED\n")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": rel}}
        self.assertTrue(any("unpinned evidence" in e for e in self._errs(m)))

    def test_pinned_hash_mismatch_is_refused(self):
        # #267: the artifact changed after it was inventoried — tamper-evident, as promised.
        m = self._m("mutant m#7 was KILLED\n", tool="mutmut", mutant="m#7", result="KILLED")
        self.artifact("mutant m#7 was KILLED (rewritten after the inventory)\n")
        self.assertTrue(any("artifacts[] pins" in e for e in self._errs(m)))

    def test_artifact_tracked_at_head_needs_no_inventory_entry(self):
        # #267's other leg: a committed artifact is immutable at head_sha, so the blob AT THAT
        # COMMIT is read and no artifacts[] hash is required.
        rel = self.artifact("mutant m#7 was KILLED\n")
        head = self.commit("evidence")
        m = {"unit": "ship-it", "head_sha": head, "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": rel}}
        self.assertEqual(self._errs(m), [])

    def test_absolute_artifact_path_is_refused(self):
        # REVIEW.md A10: the artifact walked out of the repo entirely.
        outside = Path(tempfile.mkdtemp()) / "nc.txt"
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        outside.write_text("killed m#7\n", encoding="utf-8")
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED", "artifact": str(outside)}}
        self.assertTrue(any("absolute evidence path refused" in e for e in self._errs(m)))

    def test_escaping_relative_artifact_path_is_refused(self):
        m = {"unit": "ship-it", "negative_control": {
            "tool": "mutmut", "mutant": "m#7", "result": "KILLED",
            "artifact": "../outside/nc.txt"}}
        self.assertTrue(any("escapes the repo toplevel" in e for e in self._errs(m)))


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
        self.assertTrue(verify.check_lighting({"lighting": "bogus"}, True))
        self.assertEqual(verify.check_lighting({"lighting": "lit"}, True), [])
        self.assertEqual(verify.check_lighting({"lighting": "dark-eligible"}, True), [])
        self.assertEqual(verify.check_lighting({}, False), [])

    def test_missing_lighting_defaults_to_lit(self):
        # #169: doctrine — "Recording nothing means lit" (gate-classification.md).
        self.assertEqual(verify.check_lighting({}, True), [])
        self.assertEqual(verify.check_lighting({}, True, dispatch_lighting="lit"), [])

    def test_null_lighting_is_not_omission(self):
        # An explicit null is a present illegal value, not omission — it must still fail.
        errs = verify.check_lighting({"lighting": None}, True)
        self.assertTrue(any("lighting must be" in e for e in errs), errs)

    def test_missing_lighting_with_dark_dispatch_is_a_swap(self):
        # #169: omission means lit, so a dark-eligible dispatch + omitted manifest lighting
        # implies the run used the dark waiver while the manifest says lit — still a swap.
        errs = verify.check_lighting({}, True, dispatch_lighting="dark-eligible")
        self.assertTrue(any("swap" in e for e in errs), errs)

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

    def test_dark_eligible_waives_review_only_with_an_executed_control(self):
        # #145 + #256: a dark-eligible unit (coordinator dispatch) lands without a human review, so
        # the negative control is the whole oracle — and it must have been EXECUTED. With
        # nc_executed the review leg is a NOTE; without it the lane is RED.
        verify.fetch_reviews = lambda repo, n: ([], None)
        res = verify.check_review(self._m(), "o/r", True, corroborated=True,
                                  dispatch_lighting="dark-eligible", nc_executed=True)
        self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)

    def test_dark_eligible_with_a_read_only_control_fails_closed(self):
        # REVIEW.md A1/A4/A6/A9: this exact lane went GREEN on a text file the worker wrote.
        res = verify.check_review(self._m(), "o/r", True, corroborated=True,
                                  dispatch_lighting="dark-eligible", nc_executed=False)
        self.assertTrue(any("EXECUTED" in e for e in res), res)
        self.assertFalse(any(e.startswith("NOTE:") for e in res), res)

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
    """#126 / #268: extraction catches hyphenated AND compact ids where a contract author DECLARES
    one — at the head of a list item or line, followed by a separator — and nowhere else."""

    def test_extracts_hyphenated_and_compact(self):
        ids = verify.extract_criterion_ids("- AC-1: x\n- SC12: y\n3. REQ-3) z\nREQ-4. w\n")
        self.assertEqual({"AC-1", "SC12", "REQ-3", "REQ-4"}, ids)

    def test_a11_realistic_contract_prose_is_not_a_criterion(self):
        # REVIEW.md A11, the one FALSE RED in the bypass log: a realistic contract whose prose
        # names a hash, a PR, an RFC and a date format. The denominator is exactly {AC-1, AC-2};
        # counting the prose tokens made every real contract unverifiable.
        contract = (
            "# Frozen contract\n\n"
            "- AC-1: the token digest is SHA-256 over the raw bytes\n"
            "- AC-2: see PR-12 and RFC-7519, and emit ISO-8601 timestamps\n"
        )
        self.assertEqual(verify.extract_criterion_ids(contract), {"AC-1", "AC-2"})

    def test_json_criterion_ids_are_preferred(self):
        # A JSON contract declares its denominator outright — no text heuristic runs at all.
        payload = json.dumps({"criterion_ids": ["AC-1", "SC-9"], "notes": "mentions RFC-7519"})
        self.assertEqual(verify.extract_criterion_ids(payload), {"AC-1", "SC-9"})

    def test_indented_and_starred_list_items_still_count(self):
        ids = verify.extract_criterion_ids("  * AC-7: x\n\t- SC-8: y\n")
        self.assertEqual({"AC-7", "SC-8"}, ids)


class RawByteDigest(RepoCase):
    """#180: the scope digest is computed over RAW BYTES, exactly what the coordinator's
    `shasum -a 256` sees — a CRLF contract must verify against its byte digest, and an LF
    contract's digest must be unchanged (byte-identical behavior for LF files)."""

    def _write(self, raw):
        return self.write("crlf-contract.md", raw)

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


class NoGhReviewLane(RepoCase):
    """#118: the offline no-gh lane has a defined, non-silent pass path (a local reviewer artifact)."""

    def _m(self, text, head="HEADSHA123"):
        rel = self.write("docs/reports/u/review.md", text)
        return {"unit": "ship-it", "head_sha": head, "artifacts": [self.pin(rel)],
                "review": {"artifact": rel}}

    def test_no_gh_with_executed_control_passes_as_note(self):
        m = self._m("reviewed HEADSHA123 — approved by a fresh reviewer\n")
        res = verify.check_review(m, None, True, no_gh=True, corroborated=True, nc_executed=True)
        self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)

    def test_no_gh_without_executed_control_fails_closed(self):
        # #256: the no-gh lane replaces the GitHub review with a worker-written file, so the
        # negative control is the only oracle left and it must have been EXECUTED. This is the
        # exact shape of REVIEW.md A2, which landed with a NOTE and exit 0.
        m = self._m("reviewed HEADSHA123 — approved by a fresh reviewer\n")
        res = verify.check_review(m, None, True, no_gh=True, corroborated=True, nc_executed=False)
        self.assertTrue(any("EXECUTED" in e for e in res), res)
        self.assertFalse(any(e.startswith("NOTE:") for e in res), res)

    def test_no_gh_uncorroborated_fails_closed(self):
        # #138: without an out-of-band coordinator contract the local artifact is worker-forgeable.
        m = self._m("reviewed HEADSHA123 — approved by a fresh reviewer\n")
        res = verify.check_review(m, None, True, no_gh=True, corroborated=False, nc_executed=True)
        self.assertTrue(any("forgeable" in e and not e.startswith("NOTE:") for e in res), res)

    def test_no_gh_missing_artifact_fails_closed(self):
        m = {"unit": "ship-it", "head_sha": "H", "review": {}}
        res = verify.check_review(m, None, True, no_gh=True)
        self.assertTrue(any(not e.startswith("NOTE:") for e in res), res)

    def test_no_gh_artifact_not_referencing_head_fails(self):
        m = self._m("reviewed some other sha\n")
        res = verify.check_review(m, None, True, no_gh=True)
        self.assertTrue(any("does not reference head_sha" in e for e in res), res)

    def test_no_gh_artifact_outside_the_repo_fails(self):
        # #267: the reviewer record is manifest-named evidence too — same binding as the NC.
        m = {"unit": "ship-it", "head_sha": "H", "review": {"artifact": "/etc/hostname"}}
        res = verify.check_review(m, None, True, no_gh=True)
        self.assertTrue(any("absolute evidence path refused" in e for e in res), res)


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


class NegativeControlSurvivor(RepoCase):
    """#137: survivor summaries (plural / percentage / count) must be rejected, not accepted."""

    def _errs(self, text):
        rel = self.artifact(text)
        m = {"artifacts": [self.pin(rel)],
             "negative_control": {"tool": "mutmut", "result": "killed", "mutant": "m7",
                                  "artifact": rel}}
        errs, _executed = verify.check_negative_control(m, True)
        return errs

    def test_percentage_survivor_rejected(self):
        self.assertTrue(self._errs("m7 mutation applied. Mutants that survived: 1. 0.0% killed.\n"))

    def test_summary_counts_survivor_rejected(self):
        self.assertTrue(self._errs("m7: Survived: 1 / Killed: 0\n"))

    def test_zero_mutants_killed_rejected(self):
        self.assertTrue(self._errs("m7 ran; 0 mutants killed.\n"))

    def test_pinned_mutant_survived_rejected(self):
        errs = self._errs("Run over 4 mutants: 3 killed. m7 survived the revert.\n")
        self.assertTrue(any("SURVIVED" in e for e in errs))

    def test_pinned_survivor_with_delimiter_rejected(self):
        # #152 review: "m7: Survived: 1" (colon-delimited) while OTHER mutants were killed must still
        # reject — the pinned mutant survived. A zero count ("survived: 0") is a kill, not a survivor.
        errs = self._errs("Run over 4 mutants: 3 killed. m7: Survived: 1.\n")
        self.assertTrue(any("SURVIVED" in e for e in errs))

    def test_pinned_zero_survivors_passes(self):
        self.assertEqual(self._errs("m7 revert applied. m7: survived: 0. 1 killed, RED.\n"), [])

    def test_pinned_zero_survivors_dash_delimited_passes(self):
        # #154 review: the zero-count lookahead must accept the same delimiters as the prefix, so
        # "m7 - survived - 0" (zero survivors) is a kill, not a false survivor.
        self.assertEqual(self._errs("m7 revert applied. m7 - survived - 0. 1 killed, RED.\n"), [])

    def test_pinned_survivor_greater_than_zero_rejected(self):
        # #155 review: "m7 survived > 0" is a survivor, not a zero count — must reject.
        errs = self._errs("Run: 3 killed. m7 survived > 0.\n")
        self.assertTrue(any("SURVIVED" in e for e in errs))

    def test_multimutant_run_with_pinned_killed_passes(self):
        # #149 review: a multi-mutant run where OTHER mutants survived but the pinned mutant m7 was
        # killed is valid — the whole-artifact survivor scan must not reject it.
        self.assertEqual(
            self._errs("m7 KILLED. Summary: 5 mutants, 2 survived, 3 killed. Proof went RED.\n"), [])

    def test_genuine_kill_still_passes(self):
        self.assertEqual(self._errs("m7 KILLED — 1 killed, 0 survived. Proof went RED.\n"), [])


class GitAuthorityChecks(unittest.TestCase):
    """#172: the git-authority legs — check_ancestry, check_symbol_on_base, infer_repo — shell out
    to `git` in the process cwd, so each test runs inside a hermetic temp repo (the
    test_verify_gate.py _gate_repo pattern: refs/remotes/origin/main pinned with update-ref)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

        def git(*args):
            return subprocess.run(["git", *args], cwd=self.repo, check=True,
                                  capture_output=True, text=True)

        git("init", "-q", "-b", "main")
        Path(self.repo, "app.py").write_text("def orca_unit_symbol():\n    return 1\n",
                                             encoding="utf-8")
        git("add", "app.py")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "one")
        self.main_tip = git("rev-parse", "HEAD").stdout.strip()
        git("update-ref", "refs/remotes/origin/main", "HEAD")
        # A parentless second root: a real commit that is NOT an ancestor of origin/main.
        self.side_sha = git("-c", "user.name=t", "-c", "user.email=t@t", "commit-tree",
                            "HEAD^{tree}", "-m", "side").stdout.strip()

    def tearDown(self):
        self._tmp.cleanup()

    @contextlib.contextmanager
    def _inside_repo(self):
        cwd = os.getcwd()
        os.chdir(self.repo)  # verify.py's _git runs in the process cwd
        try:
            yield
        finally:
            os.chdir(cwd)

    def test_ancestry_passes_for_commit_on_base(self):
        with self._inside_repo():
            self.assertEqual(verify.check_ancestry({"head_sha": self.main_tip}, "main"), [])

    def test_ancestry_fails_for_commit_not_on_base(self):
        with self._inside_repo():
            errs = verify.check_ancestry({"head_sha": self.side_sha}, "main")
        self.assertTrue(any("not an ancestor of origin/main" in e for e in errs), errs)

    def test_ancestry_skips_without_base_or_ref(self):
        with self._inside_repo():
            res = verify.check_ancestry({"head_sha": self.main_tip}, None)
            self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)
            res = verify.check_ancestry({"head_sha": self.main_tip}, "no-such-branch")
            self.assertTrue(res and all(e.startswith("NOTE:") for e in res), res)

    def test_symbol_on_base_found(self):
        with self._inside_repo():
            self.assertEqual(verify.check_symbol_on_base("orca_unit_symbol", "main"), [])

    def test_symbol_on_base_missing_fails(self):
        with self._inside_repo():
            errs = verify.check_symbol_on_base("no_such_symbol", "main")
        self.assertTrue(any("not found on origin/main" in e for e in errs), errs)

    def test_symbol_on_base_skips_without_inputs(self):
        with self._inside_repo():
            self.assertEqual(verify.check_symbol_on_base(None, "main"), [])
            self.assertEqual(verify.check_symbol_on_base("orca_unit_symbol", None), [])


class InferRepoFromOrigin(unittest.TestCase):
    """#172: infer_repo parses `git remote get-url origin` into owner/name across the common
    remote URL spellings; without a parseable origin it must return None (fail-soft)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo,
                       check=True, capture_output=True)
        self._cwd = os.getcwd()
        os.chdir(self.repo)  # infer_repo's `git remote get-url origin` runs in the process cwd

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def _origin(self, url):
        subprocess.run(["git", "remote", "add", "origin", url], cwd=self.repo,
                       check=True, capture_output=True)

    def test_ssh_scp_like_url(self):
        self._origin("git@github.com:owner/repo.git")
        self.assertEqual(verify.infer_repo(), "owner/repo")

    def test_ssh_scheme_url(self):
        self._origin("ssh://git@github.com/owner/repo.git")
        self.assertEqual(verify.infer_repo(), "owner/repo")

    def test_https_url(self):
        self._origin("https://github.com/owner/repo")
        self.assertEqual(verify.infer_repo(), "owner/repo")

    def test_https_url_trailing_dot_git(self):
        self._origin("https://github.com/owner/repo.git")
        self.assertEqual(verify.infer_repo(), "owner/repo")

    def test_no_origin_returns_none(self):
        self.assertIsNone(verify.infer_repo())

    def test_unparseable_origin_returns_none(self):
        self._origin("just-a-name-no-path")
        self.assertIsNone(verify.infer_repo())


class EndToEndMutationGreen(RepoCase):
    """#183: a complete mutation manifest must drive verify() to GREEN (exit 0) END-TO-END — every
    mutation lane (scope, SHAs, review, negative control, intent, lighting, reviewer_mode) passing
    simultaneously through the aggregation's NOTE/fatal partition. Only the GitHub fetch seam
    (fetch_reviews / fetch_pr_author) is mocked; every other check re-derives from real authorities
    (a temp git repo for the SHAs, the frozen contract, the NC artifact). Component tests cover
    each lane; this is the only net for their composition — a partition or NOTE-wording regression
    (a pass path that stops starting with "NOTE:") flips these tests red."""

    def setUp(self):
        super().setUp()
        # A REAL unit: a module whose behaviour the fix changes, a criterion-bound proof command
        # that binds to it, the frozen contract, and the NC artifact — all committed, so every
        # evidence path is repo-relative and tracked at head_sha (#267).
        self.write("app.py", "def f():\n    return 1\n")
        self.write("check.py", "import app\nassert app.f() == 2, 'AC-1 violated'\n")
        self.contract = self.src(["AC-1"])
        self.nc_artifact = self.artifact("mutant m7 was KILLED — proof went RED\n")
        self.base_sha = self.commit("base")
        self.write("app.py", "def f():\n    return 2\n")
        self.head_sha = self.commit("head")
        self.head_tree = self.git("rev-parse", "HEAD^{tree}")
        self.digest = RepoCase.digest(self, self.contract)  # shadows the helper; computed once
        self.proof_cmd = f"{shlex.quote(sys.executable)} check.py"

        self._orig_r = verify.fetch_reviews
        self._orig_a = verify.fetch_pr_author
        verify.fetch_reviews = lambda repo_, n: (
            [{"state": "APPROVED", "commit_id": self.head_sha,
              "user": {"login": "carol"}}], None)
        verify.fetch_pr_author = lambda repo_, n: "alice"  # the PR author != the reviewer

        # #204 review: a successful review/NC check returns [] — the same as a skipped
        # one. Spy the two mutation lanes so dropping either from aggregation goes red.
        self.review_calls, self.nc_calls = [], []
        self._orig_check_review = verify.check_review
        self._orig_check_nc = verify.check_negative_control

        def spy_review(*a, **k):
            self.review_calls.append((a, k))
            return self._orig_check_review(*a, **k)

        def spy_nc(*a, **k):
            self.nc_calls.append((a, k))
            return self._orig_check_nc(*a, **k)

        verify.check_review = spy_review
        verify.check_negative_control = spy_nc

    def tearDown(self):
        verify.fetch_reviews = self._orig_r
        verify.fetch_pr_author = self._orig_a
        verify.check_review = self._orig_check_review
        verify.check_negative_control = self._orig_check_nc

    def _assert_mutation_lanes_ran(self):
        self.assertTrue(self.review_calls,
                        "check_review was not invoked — review lane dropped from aggregation")
        self.assertTrue(self.nc_calls,
                        "check_negative_control was not invoked — NC lane dropped from aggregation")
        for args, _kwargs in self.review_calls:
            self.assertTrue(args[2], "review check ran with is_mutation=False")
        for args, _kwargs in self.nc_calls:
            self.assertTrue(args[1], "NC check ran with is_mutation=False")

    def _manifest(self, lighting="lit", nc=None, commands=None):
        m = {"unit": "slice-2",
             "base_sha": self.base_sha, "head_sha": self.head_sha,
             "contract": {"source": self.contract, "digest": self.digest,
                          "criterion_ids": ["AC-1"]},
             "criteria": _crit("AC-1"),
             "pr": {"number": 7, "reviewed_sha": self.head_sha},
             "negative_control": nc or {"tool": "mutmut", "result": "KILLED", "mutant": "m7",
                                        "artifact": self.nc_artifact},
             # The content-bound ledger: an exit-0 run whose wtree is head_sha's tree, carrying the
             # cmd_sha256 evidence-run.py writes. --execute-nc will only replay a command that is
             # in here (PR #277 review): a unit does not get to nominate what proves it.
             "commands": commands if commands is not None else [
                 {"label": "tests", "cmd": self.proof_cmd,
                  "cmd_sha256": hashlib.sha256(self.proof_cmd.encode("utf-8")).hexdigest(),
                  "exit": 0, "wtree": self.head_tree,
                  "artifact": self.nc_artifact}],
             "intent": {"goal": "land the change", "ruled_out": "the alternatives",
                        "why": "the criterion demands it"},
             "reviewer_mode": "cross-vendor"}
        if lighting is not None:  # None = omit the key entirely (#169: omission means lit)
            m["lighting"] = lighting
        path = self.repo / "manifest.json"
        path.write_text(json.dumps(m), encoding="utf-8")
        return str(path)

    def _revert_nc(self):
        """A real, EXECUTABLE negative control: restore app.py from base_sha and the bound proof
        command must go RED."""
        return {"tool": "revert", "result": "RED — the bound test failed under the control",
                "artifact": self.nc_artifact, "command": self.proof_cmd, "paths": ["app.py"]}

    def test_full_pass_mutation_manifest_is_green_end_to_end(self):
        path = self._manifest()
        out, err = verify.verify(path, self.contract, self.digest, repo="o/r",
                                 unit_class="mutation", lighting="lit")
        self.assertIsNone(err)
        fatal, notes = out
        self.assertEqual(fatal, [], fatal)
        self._assert_mutation_lanes_ran()

    def test_main_exits_0_with_verify_ok(self):
        path = self._manifest()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = verify.main(["--manifest", path,
                              "--contract-source", self.contract,
                              "--contract-digest", self.digest,
                              "--repo", "o/r",
                              "--unit-class", "mutation",
                              "--lighting", "lit"])
        self.assertEqual(rc, 0)
        self.assertIn("verify: OK", buf.getvalue())
        self._assert_mutation_lanes_ran()

    def _run_main(self, path, *extra):
        buf, errbuf = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(errbuf):
            rc = verify.main(["--manifest", path,
                              "--contract-source", self.contract,
                              "--contract-digest", self.digest,
                              "--repo", "o/r", "--unit-class", "mutation", *extra])
        return rc, buf.getvalue(), errbuf.getvalue()

    def test_dark_eligible_with_an_executed_revert_is_green(self):
        # #255 + #256, the whole point: the review-waived lane goes GREEN only when the negative
        # control is REALLY EXECUTED — app.py restored from base_sha in a throwaway worktree at
        # head_sha, the bound command RED there and GREEN at clean head_sha.
        path = self._manifest(lighting="dark-eligible", nc=self._revert_nc())
        rc, out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                      "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 0, err)
        self.assertIn("negative control EXECUTED", out)
        self.assertIn("exits 0 at clean head_sha", out)
        self.assertIn("dark-eligible", out)
        self._assert_mutation_lanes_ran()

    def test_dark_eligible_without_execute_nc_is_red(self):
        # REVIEW.md A1/A4/A6/A9 replayed: the same manifest, the control merely READ.
        path = self._manifest(lighting="dark-eligible", nc=self._revert_nc())
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible")
        self.assertEqual(rc, 2)
        self.assertIn("EXECUTED", err)

    def test_tautological_control_is_red(self):
        # The control applies, but the "proof" passes anyway — it does not bind to the change it
        # claims to prove. A gate that reads artifacts can never see this.
        self.write("check.py", "import app\nassert True\n")
        head = self.commit("tautological proof")
        nc = {**self._revert_nc(), "artifact": self.nc_artifact}
        path = self._manifest(lighting="dark-eligible", nc=nc, commands=[
            {"label": "tests", "cmd": self.proof_cmd,
             "cmd_sha256": hashlib.sha256(self.proof_cmd.encode("utf-8")).hexdigest(),
             "exit": 0, "wtree": self.git("rev-parse", "HEAD^{tree}")}])
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        manifest["head_sha"] = head
        manifest["pr"]["reviewed_sha"] = head
        Path(path).write_text(json.dumps(manifest), encoding="utf-8")
        verify.fetch_reviews = lambda repo_, n: (
            [{"state": "APPROVED", "commit_id": head, "user": {"login": "carol"}}], None)
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                       "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 2)
        self.assertIn("TAUTOLOGICAL", err)

    def test_execute_nc_without_a_coordinator_command_is_refused(self):
        # #279. `negative_control.command` is worker-written and so is the `commands[]` ledger that
        # used to justify it, so neither can authorise the other. A12/A15 of the 2026-09-11 review
        # landed exactly here: a worker that writes both nominates its own "proof".
        path = self._manifest(lighting="dark-eligible", nc=self._revert_nc())
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc")
        self.assertEqual(rc, 2)
        self.assertIn("--execute-nc requires --nc-command", err)
        self.assertNotIn("TAUTOLOGICAL", err)  # refused before anything was executed

    def test_a_shell_command_in_the_manifest_is_never_executed(self):
        # The concrete A12 manifest: `sh -c` smuggles arbitrary argv onto the verifier's own host,
        # and the ledger fallback used to accept it as a "criterion-bound proof command". Now the
        # manifest is refused before the worktree is ever built, so the payload never runs.
        holder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, holder, True)
        canary = Path(holder) / "canary"
        smuggled = f"sh -c 'touch {canary}; exit 1'"
        nc = {**self._revert_nc(), "command": smuggled}
        path = self._manifest(lighting="dark-eligible", nc=nc, commands=[
            {"label": "tests", "cmd": smuggled,
             "cmd_sha256": hashlib.sha256(smuggled.encode("utf-8")).hexdigest(),
             "exit": 0, "wtree": self.head_tree}])
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc")
        self.assertEqual(rc, 2)
        self.assertIn("--execute-nc requires --nc-command", err)
        self.assertFalse(canary.exists(), "the manifest's command was executed despite being refused")

    def test_a_ledger_record_whose_sha_does_not_match_is_refused(self):
        # cmd_sha256 that does not hash its own cmd binds nothing; a decorative digest would let a
        # record be edited after the fact. Since #279 the replay no longer reads this ledger, so the
        # integrity check lives in check_commands — where the ledger is actually graded.
        path = self._manifest(lighting="dark-eligible", nc=self._revert_nc(), commands=[
            {"label": "tests", "cmd": self.proof_cmd, "cmd_sha256": "0" * 64,
             "exit": 0, "wtree": self.head_tree}])
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                       "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 2)
        self.assertIn("does not describe its own command", err)

    def test_a_stale_ledger_record_still_fails_the_commands_gate(self):
        # The ledger must still be fresh at head_sha's tree — that check is check_commands' job and
        # is unchanged by #279; only the NC replay stopped depending on it.
        path = self._manifest(lighting="dark-eligible", nc=self._revert_nc(), commands=[
            {"label": "tests", "cmd": self.proof_cmd,
             "cmd_sha256": hashlib.sha256(self.proof_cmd.encode("utf-8")).hexdigest(),
             "exit": 0, "wtree": "0" * 40}])
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                       "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 2)
        self.assertIn("STALE evidence", err)

    def test_coordinator_nc_command_overrides_and_must_agree(self):
        # --contract-source's shape, for the proof command: the coordinator supplies it out of
        # band, and a manifest that names a different one is refused rather than silently obeyed.
        path = self._manifest(lighting="dark-eligible", nc=self._revert_nc())
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                       "--nc-command", "/bin/true")
        self.assertEqual(rc, 2)
        self.assertIn("is not the command the coordinator supplied out of band", err)

    def test_coordinator_nc_command_that_agrees_is_accepted(self):
        path = self._manifest(lighting="dark-eligible", nc=self._revert_nc())
        rc, out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                      "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 0, err)
        self.assertIn("negative control EXECUTED", out + err)

    def test_executed_control_needs_a_bound_command(self):
        nc = {k: v for k, v in self._revert_nc().items() if k != "command"}
        path = self._manifest(lighting="dark-eligible", nc=nc)
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                       "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 2)
        self.assertIn("negative_control.command", err)

    def test_executed_hand_control_applies_the_quoted_diff(self):
        # `hand`'s only binding to a mutation is the diff quoted in its artifact — so EXECUTING it
        # means applying exactly that diff. A fabricated diff (REVIEW.md A4) will not apply.
        diff = self.git("diff", f"{self.head_sha}..{self.base_sha}", "--", "app.py")
        art = self.artifact("hand mutant applied — the bound test went RED\n\n" + diff + "\n",
                            rel="docs/reports/u/hand.txt")
        self.commit("hand nc artifact")
        nc = {"tool": "hand", "result": "RED", "artifact": art, "command": self.proof_cmd}
        path = self._manifest(lighting="dark-eligible", nc=nc, commands=[
            {"label": "tests", "cmd": self.proof_cmd,
             "cmd_sha256": hashlib.sha256(self.proof_cmd.encode("utf-8")).hexdigest(),
             "exit": 0, "wtree": self.git("rev-parse", "HEAD^{tree}")}])
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        head = self.git("rev-parse", "HEAD")
        manifest["head_sha"] = head
        manifest["pr"]["reviewed_sha"] = head
        Path(path).write_text(json.dumps(manifest), encoding="utf-8")
        verify.fetch_reviews = lambda repo_, n: (
            [{"state": "APPROVED", "commit_id": head, "user": {"login": "carol"}}], None)
        rc, out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                      "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 0, err)
        self.assertIn("negative control EXECUTED", out)

    def test_fabricated_hand_diff_does_not_apply(self):
        art = self.artifact(
            "hand mutant applied:\n--- a/app.py\n+++ b/app.py\n@@ -9,9 +9,9 @@\n"
            "-    return something_that_is_not_there\n+    return other\n"
            "the bound test went RED (mutant killed)\n", rel="docs/reports/u/hand.txt")
        self.commit("fabricated hand artifact")
        nc = {"tool": "hand", "result": "RED", "artifact": art, "command": self.proof_cmd}
        path = self._manifest(lighting="dark-eligible", nc=nc, commands=[
            {"label": "tests", "cmd": self.proof_cmd,
             "cmd_sha256": hashlib.sha256(self.proof_cmd.encode("utf-8")).hexdigest(),
             "exit": 0, "wtree": self.git("rev-parse", "HEAD^{tree}")}])
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        manifest["head_sha"] = self.git("rev-parse", "HEAD")
        Path(path).write_text(json.dumps(manifest), encoding="utf-8")
        rc, _out, err = self._run_main(path, "--lighting", "dark-eligible", "--execute-nc",
                                       "--nc-command", self.proof_cmd)
        self.assertEqual(rc, 2)
        self.assertIn("does not apply at head_sha", err)

    def test_stale_commands_ledger_is_red(self):
        # A recorded run on OTHER content does not certify this head (audit §3 item 3).
        path = self._manifest(commands=[{"label": "tests", "cmd": self.proof_cmd, "exit": 0,
                                         "wtree": "0" * 40}])
        rc, _out, err = self._run_main(path)
        self.assertEqual(rc, 2)
        self.assertIn("STALE evidence", err)

    def test_missing_commands_ledger_is_red(self):
        path = self._manifest(commands=[])
        rc, _out, err = self._run_main(path)
        self.assertEqual(rc, 2)
        self.assertIn("no recorded command", err)

    def test_credential_in_an_artifact_fails_the_unit(self):
        # #14: evidence is SHA-pinned and permanent, so a leaked credential in it is permanent.
        self.artifact("mutant m7 was KILLED — proof went RED\n"
                      "run with AKIA" + "Q" * 16 + " exported\n")
        self.commit("leaky artifact")
        path = self._manifest()
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        manifest["head_sha"] = self.git("rev-parse", "HEAD")
        Path(path).write_text(json.dumps(manifest), encoding="utf-8")
        rc, _out, err = self._run_main(path)
        self.assertEqual(rc, 2)
        self.assertIn("redaction", err)

    def test_omitted_lighting_is_lit_end_to_end(self):
        # #169: a mutation manifest with no lighting key verifies clean — omission means lit.
        path = self._manifest(lighting=None)
        out, err = verify.verify(path, self.contract, self.digest, repo="o/r",
                                 unit_class="mutation", lighting="lit")
        self.assertIsNone(err)
        fatal, notes = out
        self.assertEqual(fatal, [], fatal)
        self._assert_mutation_lanes_ran()

    def test_omitted_lighting_with_dark_dispatch_fails_end_to_end(self):
        # #169: the swap interaction — dispatch used the dark waiver but the omitted manifest
        # lighting implies lit, so the aggregate is fatal (exit 2).
        path = self._manifest(lighting=None)
        out, err = verify.verify(path, self.contract, self.digest, repo="o/r",
                                 unit_class="mutation", lighting="dark-eligible")
        self.assertIsNone(err)
        fatal, notes = out
        self.assertTrue(any("swap" in f for f in fatal), fatal)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = verify.main(["--manifest", path,
                              "--contract-source", self.contract,
                              "--contract-digest", self.digest,
                              "--repo", "o/r",
                              "--unit-class", "mutation",
                              "--lighting", "dark-eligible"])
        self.assertEqual(rc, 2)
        self._assert_mutation_lanes_ran()


_edspec = importlib.util.spec_from_file_location("ed25519", ROOT / "runtime" / "scripts" / "ed25519.py")
ed = importlib.util.module_from_spec(_edspec)
_edspec.loader.exec_module(ed)
_dsspec = importlib.util.spec_from_file_location("dispatch_sign", ROOT / "runtime" / "scripts" / "dispatch-sign.py")
dispatch_sign = importlib.util.module_from_spec(_dsspec)
_dsspec.loader.exec_module(dispatch_sign)


class DispatchProvenance(RepoCase):
    """#135: a coordinator-signed dispatch record makes the native in-session path sound — a worker
    that substitutes the digest / class / lighting, forges the record, or omits it is caught."""

    def _signed(self, record, seed=None, sign_key=None):
        import base64
        seed = seed or bytes(range(1, 33))
        pub = ed.publickey(seed)
        sig = ed.signature(verify._canonical_dispatch(record), sign_key or seed, ed.publickey(sign_key) if sign_key else pub)
        env = {"record": record, "sig_b64": base64.b64encode(sig).decode()}
        # #267: read_source refuses absolute paths, so the record and key are named relatively —
        # which is how a real dispatch names them anyway (a repo-pinned `.orca/dispatch-pubkey`).
        return (self.write(".orca/dispatch-record.json", json.dumps(env)),
                self.write(".orca/dispatch-pubkey", pub.hex()))

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
