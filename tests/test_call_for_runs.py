#!/usr/bin/env python3
"""The call for runs names every doctrine-only mission, and only those.

`docs/call-for-runs.md` is a static list over a moving catalog: every
promotion shrinks the doctrine-only set, so an unchecked list would rot on
its first promotion. The page carries machine-readable sections (HTML
comment markers bracketing `- [ ] `mission`` rows) and this test holds
their union equal to the catalog's live doctrine-only set — a promotion PR
that forgets the list update fails the build.
"""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "proof_status", ROOT / "runtime" / "scripts" / "proof_status.py"
)
proof_status = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(proof_status)

CALL = ROOT / "docs" / "call-for-runs.md"
ROW = re.compile(r"^-\s*\[\s\]\s*`([^`]+)`")
ISSUE_LINK = re.compile(r"/issues/\d+")


def _section(text, name):
    start = f"<!-- call-for-runs:{name}:start -->"
    end = f"<!-- call-for-runs:{name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise AssertionError(f"want exactly one {start} ... {end} pair")
    body = text.split(start)[1].split(end)[0]
    rows, lineno = [], None
    for i, line in enumerate(body.splitlines()):
        if not line.strip():
            continue
        m = ROW.match(line.strip())
        if not m:
            raise AssertionError(f"call-for-runs {name} line {i}: not a `- [ ] `mission`` row")
        rows.append((m.group(1), line.strip()))
    return rows


class CallForRunsMatchesCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CALL.read_text(encoding="utf-8")
        cls.records = proof_status.collect(ROOT / "skills", ROOT)
        cls.known = {r["name"] or r["dir"] for r in cls.records}
        cls.doctrine_only = {
            r["name"] or r["dir"]
            for r in cls.records
            if r["proof"] == "doctrine-only"
        }

    def test_every_listed_mission_is_a_catalog_mission(self):
        for section in ("open", "in-flight"):
            for mission, _line in _section(self.text, section):
                self.assertIn(mission, self.known,
                              f"`{mission}` is listed but is no catalog mission")

    def test_the_list_union_is_exactly_the_doctrine_only_set(self):
        listed = {m for s in ("open", "in-flight") for m, _ in _section(self.text, s)}
        self.assertEqual(
            listed, self.doctrine_only,
            f"stale call-for-runs: missing {sorted(self.doctrine_only - listed)}, "
            f"extra {sorted(listed - self.doctrine_only)}")

    def test_no_mission_is_listed_twice(self):
        seen = {}
        for section in ("open", "in-flight"):
            for mission, _line in _section(self.text, section):
                self.assertNotIn(
                    mission, seen,
                    f"`{mission}` is listed under both {seen.get(mission)} and {section}")
                seen[mission] = section

    def test_every_in_flight_row_links_its_roadmap_issue(self):
        # The page promises "check the linked issue before running one" — a
        # row without a link breaks the promise it makes in its own sentence.
        for mission, line in _section(self.text, "in-flight"):
            self.assertRegex(line, ISSUE_LINK,
                             f"`{mission}` has no linked roadmap issue")

    def test_the_page_states_what_a_submission_earns(self):
        self.assertIn("run-submission-guide.md", self.text)


if __name__ == "__main__":
    unittest.main()
