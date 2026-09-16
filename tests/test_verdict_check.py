"""Tests for scripts/verdict_check.py (#452): GO-at-tip verdict rule."""

import importlib.util
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "verdict_check", _ROOT / "scripts" / "verdict_check.py")
verdict_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verdict_check)
go_reviews_at_tip = verdict_check.go_reviews_at_tip
verdict_at_tip = verdict_check.verdict_at_tip

HEAD = "a" * 40
OTHER = "b" * 40


def review(body, state="APPROVED", login="coord"):
    return {"state": state, "body": body, "submitted_at": "2026-09-16T00:00:00Z",
            "user": {"login": login}}


def go_body(sha):
    return f"Looks good.\n\nVERDICT: GO\nreviewed_sha: {sha}\n"


class VerdictAtTip(unittest.TestCase):
    def test_fresh_go_at_tip_passes(self):
        self.assertTrue(verdict_at_tip([review(go_body(HEAD))], HEAD))

    def test_stale_go_fails(self):
        self.assertFalse(verdict_at_tip([review(go_body(OTHER))], HEAD))

    def test_no_go_fails(self):
        self.assertFalse(verdict_at_tip([review("lgtm"), review("", "COMMENTED")], HEAD))
        self.assertFalse(verdict_at_tip([], HEAD))

    def test_dismissed_go_does_not_count(self):
        self.assertFalse(verdict_at_tip([review(go_body(HEAD), state="DISMISSED")], HEAD))

    def test_short_sha_never_matches(self):
        self.assertFalse(verdict_at_tip([review(go_body(HEAD[:7]))], HEAD))
        self.assertFalse(verdict_at_tip([review(go_body(HEAD[:39] + "zz"))], HEAD))

    def test_sha_comparison_is_case_insensitive(self):
        self.assertTrue(verdict_at_tip([review(go_body(HEAD.upper()))], HEAD))

    def test_verdict_line_case_insensitive_go_word_exact(self):
        self.assertTrue(verdict_at_tip([review(go_body(HEAD).replace("VERDICT", "verdict"))], HEAD))
        self.assertFalse(verdict_at_tip([review("VERDICT: GOAHEAD\nreviewed_sha: " + HEAD)], HEAD))
        self.assertFalse(verdict_at_tip([review("VERDICT: NO-GO\nreviewed_sha: " + HEAD)], HEAD))

    def test_go_counts_on_approval_only(self):
        self.assertTrue(verdict_at_tip([review(go_body(HEAD), state="APPROVED")], HEAD))
        # PR #460 review, P1: COMMENTED is open to any signed-in user, so a
        # drive-by comment must never satisfy this required check.
        for state in ("COMMENTED", "CHANGES_REQUESTED", "DISMISSED", "PENDING"):
            with self.subTest(state=state):
                self.assertFalse(verdict_at_tip(
                    [review(go_body(HEAD), state=state)], HEAD))

    def test_newest_go_wins_among_several(self):
        reviews = [review(go_body(OTHER)), review(go_body(HEAD))]
        hits = go_reviews_at_tip(reviews, HEAD)
        self.assertEqual(len(hits), 1)

    def test_missing_body_is_not_a_go(self):
        self.assertFalse(verdict_at_tip([{"state": "APPROVED"}], HEAD))
        self.assertFalse(verdict_at_tip([{"state": "APPROVED", "body": None}], HEAD))


if __name__ == "__main__":
    unittest.main()
