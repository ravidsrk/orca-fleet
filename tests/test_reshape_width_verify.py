#!/usr/bin/env python3
"""reshape-it RV-D2 WIDTH pin: runtime/scripts/verify.py's interface surface.

Guards the RV-D2 deepening (control-outcome reader moved to
runtime/scripts/_verify_sig.py behind a single _failure_signature
re-export). The count half reads verify.py as TEXT and never imports it, so
the pin stays runnable in every tree shape (including the RV-D2 revert
control, where the importable surface is the pre-deepening one).

WIDTH is the mission's own probe (skills/reshape-it/SKILL.md § SCAN):
count of lines matching ^(def |class |async def |[A-Z_]+ =).
Pre-deepening baseline: 92. Post-deepening pin: 85.
"""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTH_RE = re.compile(r"(?:def |class |async def |[A-Z_]+ =)")
BASELINE_WIDTH = 92
PINNED_WIDTH = 85


def interface_width(path):
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines()
               if WIDTH_RE.match(line))


class VerifyWidthPin(unittest.TestCase):
    def test_interface_width_shrunk(self):
        width = interface_width(ROOT / "runtime" / "scripts" / "verify.py")
        self.assertLess(width, BASELINE_WIDTH,
                        f"verify.py WIDTH {width} is not smaller than the pre-deepening {BASELINE_WIDTH}")
        self.assertEqual(width, PINNED_WIDTH,
                         f"verify.py WIDTH {width} drifted from the RV-D2 pin {PINNED_WIDTH}")

    def test_engine_lives_behind_the_narrow_import(self):
        spec = importlib.util.spec_from_file_location(
            "verify_width_probe", ROOT / "runtime" / "scripts" / "verify.py")
        verify = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verify)
        engine = getattr(verify, "_verify_sig", None)
        self.assertIsNotNone(engine, "verify.py no longer loads runtime/scripts/_verify_sig.py")
        self.assertIs(verify._failure_signature, engine._failure_signature,
                      "the _failure_signature re-export is not the engine's own object")
        for detail in ("_counted", "STILLBORN_MARKERS", "ASSERTION_MARKERS",
                       "STRONG_ASSERTION_RE", "_ERRORS_RE", "_FAILURES_RE"):
            self.assertFalse(hasattr(verify, detail),
                             f"implementation detail {detail} leaked back onto verify")


if __name__ == "__main__":
    unittest.main()
