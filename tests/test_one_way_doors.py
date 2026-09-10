#!/usr/bin/env python3
"""Contract tests for runtime/one-way-doors.json.

The one-way list was a sentence in a policy document. As data it becomes
checkable, and these tests are what keep it honest: every door named in the
classification policy is present, every door carries a usable keyword net, and
the net is specific enough that ordinary prose does not trip it. A net that
cries wolf trains people to ignore the refusal, which is worse than no net.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOORS = ROOT / "runtime" / "one-way-doors.json"
DECISIONS = ROOT / "runtime" / "scripts" / "decisions.py"
GATE_POLICY = ROOT / "runtime" / "gate-classification.md"

# The one-way sentence in runtime/gate-classification.md, as door ids.
EXPECTED_DOORS = {
    "merge-to-default", "deploy", "rollback", "deletion", "spend",
    "scope-change", "secret-rotation", "live-credentials", "freeze",
}

ORDINARY_PROSE = [
    "picked the existing helper, matching the repo precedent",
    "retried once after a transient network failure",
    "named the flag --dry-run to match the sibling script",
    "the lens found nothing on this diff",
    "kept the test at the existing threshold",
    "used the shorter of the two spellings for consistency",
]


def load():
    return json.loads(DOORS.read_text(encoding="utf-8"))


class TestRegistryShape(unittest.TestCase):
    def test_the_registry_is_valid_json(self):
        self.assertIsInstance(load(), dict)

    def test_it_declares_a_version(self):
        self.assertIn("version", load())

    def test_it_explains_what_the_net_is_for(self):
        note = load()["note"].lower()
        self.assertIn("never auto-resolved", note)
        self.assertIn("keyword", note)

    def test_every_expected_door_is_present(self):
        ids = {d["id"] for d in load()["doors"]}
        self.assertEqual(ids, EXPECTED_DOORS)

    def test_every_door_has_a_title_a_reason_and_a_net(self):
        for door in load()["doors"]:
            with self.subTest(door=door["id"]):
                self.assertTrue(door.get("title"))
                self.assertTrue(door.get("why"))
                self.assertTrue(door.get("keywords"))

    def test_door_ids_are_unique_and_slug_shaped(self):
        ids = [d["id"] for d in load()["doors"]]
        self.assertEqual(len(ids), len(set(ids)))
        for door_id in ids:
            self.assertRegex(door_id, r"^[a-z][a-z0-9-]*$")

    def test_keywords_are_lowercase(self):
        for door in load()["doors"]:
            for keyword in door["keywords"]:
                self.assertEqual(keyword, keyword.lower(), f"{keyword!r} in {door['id']}")

    def test_keywords_are_specific_enough_to_be_safe(self):
        for door in load()["doors"]:
            for keyword in door["keywords"]:
                with self.subTest(keyword=keyword):
                    self.assertGreaterEqual(
                        len(keyword), 6,
                        "a short common word would fire on ordinary prose")

    def test_no_keyword_is_claimed_by_two_doors(self):
        seen = {}
        for door in load()["doors"]:
            for keyword in door["keywords"]:
                self.assertNotIn(keyword, seen,
                                 f"{keyword!r} is in both {seen.get(keyword)} and {door['id']}")
                seen[keyword] = door["id"]


class TestPolicyAgreement(unittest.TestCase):
    def test_the_classification_policy_still_names_these_doors(self):
        text = GATE_POLICY.read_text(encoding="utf-8").lower()
        for phrase in ("merge to default", "deploy", "rollback", "deletion", "spend",
                       "scope change", "secret rotation"):
            self.assertIn(phrase, text,
                          f"{phrase!r} left gate-classification.md — the registry has drifted")

    def test_every_door_title_is_a_sentence_not_an_id(self):
        for door in load()["doors"]:
            self.assertGreater(len(door["title"].split()), 2, door["id"])


class TestNetBehaviour(unittest.TestCase):
    """The net is only useful through its consumer, so it is exercised there."""

    def _append(self, tmp, why, klass="mechanical"):
        return subprocess.run(
            [sys.executable, str(DECISIONS), "--file", str(tmp), "append",
             "--id", "gate-x", "--class", klass, "--answer", "yes", "--why", why],
            capture_output=True, text=True)

    def setUp(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp(prefix="doors-")
        self.log = Path(self.tmpdir) / "DECISIONS.md"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_every_keyword_trips_its_own_door(self):
        for door in load()["doors"]:
            for keyword in door["keywords"]:
                with self.subTest(door=door["id"], keyword=keyword):
                    r = self._append(self.log, f"the request is to {keyword} today")
                    self.assertEqual(r.returncode, 1, f"{keyword!r} did not trip the net")
                    self.assertIn(door["id"], r.stderr)

    def test_ordinary_prose_does_not_trip_the_net(self):
        for why in ORDINARY_PROSE:
            with self.subTest(why=why):
                r = self._append(self.log, why)
                self.assertEqual(r.returncode, 0, f"false positive on: {why!r}\n{r.stderr}")

    def test_the_net_is_case_insensitive(self):
        r = self._append(self.log, "We must ROTATE THE SECRET before Friday")
        self.assertEqual(r.returncode, 1)
        self.assertIn("secret-rotation", r.stderr)

    def test_the_net_survives_whitespace_folding(self):
        r = self._append(self.log, "deploy   to    production tonight")
        self.assertEqual(r.returncode, 1)
        self.assertIn("deploy", r.stderr)

    def test_a_net_match_is_accepted_when_classed_and_sourced(self):
        r = subprocess.run(
            [sys.executable, str(DECISIONS), "--file", str(self.log), "append",
             "--id", "gate-y", "--class", "one-way", "--answer", "approved",
             "--why", "deploy to production tonight", "--source", "human:maintainer"],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
