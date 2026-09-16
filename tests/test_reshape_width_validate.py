#!/usr/bin/env python3
"""reshape-it RV-D1 WIDTH pin: scripts/validate.py's interface surface.

Guards the RV-D1 deepening (count-lint regex engine moved to
scripts/_countlint.py behind a single COUNT_LINT_RE re-export). Deliberately
reads validate.py as TEXT and never imports it, so the pin stays runnable in
every tree shape (including the RV-D1 revert control, where the importable
surface is the pre-deepening one).

WIDTH is the mission's own probe (skills/reshape-it/SKILL.md § SCAN):
count of lines matching ^(def |class |async def |[A-Z_]+ =).
Pre-deepening baseline: 73. Post-deepening pin: 64.
"""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTH_RE = re.compile(r"(?:def |class |async def |[A-Z_]+ =)")
BASELINE_WIDTH = 73
PINNED_WIDTH = 64


def interface_width(path):
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines()
               if WIDTH_RE.match(line))


class ValidateWidthPin(unittest.TestCase):
    def test_interface_width_shrunk(self):
        width = interface_width(ROOT / "scripts" / "validate.py")
        self.assertLess(width, BASELINE_WIDTH,
                        f"validate.py WIDTH {width} is not smaller than the pre-deepening {BASELINE_WIDTH}")
        self.assertEqual(width, PINNED_WIDTH,
                         f"validate.py WIDTH {width} drifted from the RV-D1 pin {PINNED_WIDTH}")

    def test_engine_lives_behind_the_narrow_import(self):
        spec = importlib.util.spec_from_file_location(
            "validate_width_probe", ROOT / "scripts" / "validate.py")
        validate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate)
        engine = getattr(validate, "_countlint", None)
        self.assertIsNotNone(engine, "validate.py no longer loads scripts/_countlint.py")
        self.assertIs(validate.COUNT_LINT_RE, engine.COUNT_LINT_RE,
                      "the COUNT_LINT_RE re-export is not the engine's own object")
        for detail in ("_SPELLED", "_SEP", "_NUM", "ALL_COUNT_RE", "MISSION_CONTEXT_RE"):
            self.assertFalse(hasattr(validate, detail),
                             f"implementation detail {detail} leaked back onto validate")


if __name__ == "__main__":
    unittest.main()
