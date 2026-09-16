#!/usr/bin/env python3
"""reshape-it RV-C1 CHARACTERIZE net: the count-lint seam of scripts/validate.py.

Pins the CURRENT behavior of the regex engine (scripts/validate.py _ONES ..
MISSION_CONTEXT_RE) and check_doc_counts' file behavior BEFORE the RV-D1
deepening moves the engine to scripts/_countlint.py. Overlap with
TestCountAgnosticGuards is deliberate: this module is the seam's pinned,
re-runnable net — the RV-C1 negative control runs ONLY this module, and the
RV-D1 carve-out re-kills the pinned mutant against this same net at the
deepened head.

Pinned mutant M1 (hand): scripts/validate.py:905 _SEP drops the hyphen
alternative. Killed by the hyphen cases below.
Supporting mutant M2 (hand): scripts/validate.py:905 _SEP drops the backtick.
Killed by the backtick-jointed-noun case below.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)


class CountLintSeamNet(unittest.TestCase):
    """Current behavior of the count-lint regex engine + file walk."""

    def test_hyphenated_counts_match(self):
        for s in ("the ten-mission set", "an 11-mission catalog"):
            self.assertRegex(s, validate.COUNT_LINT_RE, s)

    def test_compound_spelled_counts_match(self):
        for s in ("twenty-one autonomous fleets", "thirty-one missions",
                  "twenty one missions"):
            self.assertRegex(s, validate.COUNT_LINT_RE, s)

    def test_lone_ones_words_do_not_match(self):
        for s in ("one mission", "two missions", "one router per worker"):
            self.assertIsNone(validate.COUNT_LINT_RE.search(s), s)

    def test_matching_is_case_insensitive(self):
        for s in ("Twenty-one outcome-named fleets", "ELEVEN missions"):
            self.assertRegex(s, validate.COUNT_LINT_RE, s)

    def test_emphasis_joint_counts_match(self):
        # Every _SEP emphasis alternative must pin: a later extraction dropping
        # bold/underscore handling has to turn this net red (Greptile P2, PR #462).
        for s in ("21 `missions`", "21 `doctrine-only`", "seventeen self-run",
                  "Ten **autonomous fleets** for the runtime",
                  "eleven _autonomous_ fleets"):
            self.assertRegex(s, validate.COUNT_LINT_RE, s)

    def test_missing_listed_file_is_skipped(self):
        # check_doc_counts' `not p.exists()` branch: a listed file that is not
        # on disk contributes nothing (no test pinned this before RV-C1).
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(validate, "ROOT", Path(tmp)), \
                 mock.patch.object(validate, "COUNT_LINT_FILES", ("no-such.md",)):
                self.assertEqual(validate.check_doc_counts(), [])

    def test_failure_message_names_the_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text(
                "orca-fleet ships eleven missions.\n", encoding="utf-8")
            with mock.patch.object(validate, "ROOT", Path(tmp)), \
                 mock.patch.object(validate, "COUNT_LINT_FILES", ("README.md",)):
                failures = validate.check_doc_counts()
        self.assertEqual(len(failures), 1)
        self.assertIn("hardcoded catalog count", failures[0])
        self.assertIn("eleven missions", failures[0])


if __name__ == "__main__":
    unittest.main()
