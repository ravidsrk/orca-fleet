"""Execute the guide's populated SQLite migration, with independent phase oracles."""
import re
import sqlite3
import unittest
from contextlib import closing
from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "docs/missions/migrate-it.md"


class TestMigrationWalkthrough(unittest.TestCase):
    def test_populated_table_reaches_contract_without_premature_parity(self):
        blocks = dict(re.findall(r"```sql\n-- phase: ([\w-]+)\n(.*?)```",
                                 GUIDE.read_text(), re.S))
        phases = ("setup", "expand", "dual-write", "backfill", "switch-reads",
                  "contract")
        self.assertEqual(tuple(blocks), phases, "guide needs an executable phase ladder")
        with closing(sqlite3.connect(":memory:")) as db:
            for phase in phases:
                with self.subTest(phase=phase):
                    try:
                        db.executescript(blocks[phase])
                    except sqlite3.Error as exc:
                        self.fail(f"{phase} cannot advance on this populated fixture: {exc}")
                    if phase == "setup":
                        self.assertEqual(db.execute("SELECT * FROM users").fetchall(),
                                         [(1, "Alice"), (2, "Bob")])
                    elif phase == "expand":
                        # Existing application still reads the old column; the new
                        # column is nullable. Full parity here is unattainable.
                        self.assertEqual(db.execute("SELECT name FROM users").fetchall(),
                                         [("Alice",), ("Bob",)])
                        self.assertEqual(db.execute("SELECT full_name FROM users").fetchall(),
                                         [(None,), (None,)])
                    elif phase == "dual-write":
                        self.assertEqual(db.execute("SELECT * FROM users ORDER BY id").fetchall(),
                                         [(1, "Alicia", "Alicia"), (2, "Bob", None),
                                          (3, "Carol", "Carol")])
                    elif phase in ("backfill", "switch-reads"):
                        self.assertEqual(db.execute("SELECT * FROM users ORDER BY id").fetchall(),
                                         [(1, "Alicia", "Alicia"), (2, "Bob", "Bob"),
                                          (3, "Carol", "Carol")])
                    else:
                        self.assertEqual(db.execute("SELECT * FROM users ORDER BY id").fetchall(),
                                         [(1, "Alicia"), (2, "Bob"), (3, "Carol")])
                        columns = [row[1] for row in db.execute("PRAGMA table_info(users)")]
                        self.assertEqual(columns, ["id", "full_name"])
                        # Archived comparison remains queryable after old column removal.
                        self.assertEqual(db.execute("SELECT * FROM parity_receipt ORDER BY id")
                                         .fetchall(), [(1, "Alicia", "Alicia"),
                                                       (2, "Bob", "Bob"),
                                                       (3, "Carol", "Carol")])


if __name__ == "__main__":
    unittest.main()


class TestRetirementPrecedesTheDrop(unittest.TestCase):
    """PR #329 review, P1.

    The playbook ladder put "retire old writers, prove zero use, then DROP" in ONE deploy-gated
    rung. Zero-use telemetry is collected from a running deployment, so a rung that retires the
    writers and drops the shape together leaves no interval in which a writer could be observed —
    the proof it demands is unobtainable by construction. It also contradicted the mission guide
    and the skill contract, which already placed retirement and the zero-use proof before a
    separate DROP deployment.
    """

    ROOT = Path(__file__).resolve().parents[1]
    LADDER = ("EXPAND", "DUAL-WRITE", "BACKFILL", "SWITCH-READS", "ZERO-READERS",
              "RETIRE-WRITES", "ZERO-WRITERS", "CONTRACT")

    def test_the_playbook_ladder_gives_retirement_its_own_rung(self):
        text = (self.ROOT / "playbooks/data-migration.md").read_text()
        ladder = re.search(r"## The phase ladder.*?```\n(.*?)```", text, re.S)
        self.assertIsNotNone(ladder, "the playbook needs its phase ladder block")
        rungs = [line.split()[0] for line in ladder.group(1).splitlines() if line.strip()]
        self.assertEqual(tuple(rungs), self.LADDER)
        contract = next(l for l in ladder.group(1).splitlines() if l.startswith("CONTRACT"))
        # The drop rung carries the drop and nothing that must be observed from a live deploy.
        self.assertIn("DROP", contract)
        for collapsed in ("retire", "zero use", "prove zero"):
            self.assertNotIn(collapsed, contract.lower(), f"{collapsed!r} cannot share the DROP rung")

    def test_every_contract_names_the_same_order(self):
        for relative in ("playbooks/data-migration.md", "skills/migrate-it/SKILL.md",
                         "docs/missions/migrate-it.md"):
            with self.subTest(document=relative):
                text = (self.ROOT / relative).read_text()
                for earlier, later in (("RETIRE-WRITES", "CONTRACT"),
                                       ("ZERO-WRITERS", "CONTRACT"),
                                       ("ZERO-READERS", "RETIRE-WRITES")):
                    # Booleans, not the text: a failed assertIn would dump the whole document.
                    self.assertTrue(earlier in text, f"{relative} never names {earlier}")
                    self.assertTrue(text.index(earlier) < text.rindex(later),
                                    f"{relative}: {earlier} must precede {later}")

    def test_the_skill_says_zero_use_is_observed_from_the_retirement_deploy(self):
        text = (self.ROOT / "skills/migrate-it/SKILL.md").read_text()
        for phrase in ("DEPLOY the retirement", "cannot share a rung with the drop"):
            self.assertTrue(phrase in text, f"the skill must say {phrase!r}")
