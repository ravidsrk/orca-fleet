#!/usr/bin/env python3
"""reshape-it RV-C2 CHARACTERIZE net: verify.py's control-outcome seam.

Pins the CURRENT verdicts of runtime/scripts/verify.py's outcome reader
(_counted, _failure_signature + its marker tables) BEFORE the RV-D2
deepening moves the seam to runtime/scripts/_verify_sig.py. Overlap with the
_failure_signature tests in test_verify.py is deliberate: this module is the
seam's pinned, re-runnable net — the RV-C2 negative control runs ONLY this
module, and the RV-D2 carve-out re-kills the pinned mutant against this same
net at the deepened head.

Pinned mutant M2 (hand): runtime/scripts/verify.py:1166
`if errors and not failures:` -> `if errors or not failures:`.
Killed by the mixed-summary case (admitted -> refused) and the
bare-stillborn reason case below.
Supporting mutant M2b (hand): verify.py:1170 `if not failures:` ->
`if failures:`. Killed by the bare-stillborn reason case below.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("verify", ROOT / "runtime" / "scripts" / "verify.py")
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


class OutcomeReadingSeamNet(unittest.TestCase):
    """Current verdicts of _failure_signature + _counted."""

    def test_silent_output_is_not_a_kill(self):
        ok, reason = verify._failure_signature("", "")
        self.assertFalse(ok)
        self.assertIn("NO output", reason)

    def test_errors_only_summary_is_not_a_kill(self):
        ok, reason = verify._failure_signature(
            "ERROR: test_add\nTypeError: unsupported operand\nRan 1 test\n\nFAILED (errors=1)\n", "")
        self.assertFalse(ok)
        self.assertIn("error", reason)

    def test_failures_summary_is_a_kill(self):
        ok, _reason = verify._failure_signature(
            "FAIL: test_add\nAssertionError: 4 != 0\n\nFAILED (failures=1)\n", "")
        self.assertTrue(ok)

    def test_mixed_errors_and_failures_is_a_kill(self):
        ok, _reason = verify._failure_signature(
            "FAILED (failures=1, errors=1)\nAssertionError: x\n", "")
        self.assertTrue(ok)

    def test_bare_stillborn_traceback_is_not_a_kill(self):
        ok, reason = verify._failure_signature(
            "Traceback (most recent call last):\n  File 'check.py'\nImportError: nope\n", "")
        self.assertFalse(ok)
        self.assertIn("STILLBORN", reason)

    def test_bare_assertion_traceback_is_a_kill(self):
        ok, _reason = verify._failure_signature(
            "Traceback (most recent call last):\nAssertionError: AC-1 violated\n", "")
        self.assertTrue(ok)

    def test_counted_sums_reported_counts_and_nones_when_absent(self):
        self.assertIsNone(verify._counted(verify._ERRORS_RE, "no runner summary here"))
        self.assertEqual(verify._counted(verify._FAILURES_RE, "FAILED (failures=1)"), 1)
        self.assertEqual(
            verify._counted(verify._FAILURES_RE, "2 failed, 3 failed"), 5)


if __name__ == "__main__":
    unittest.main()
