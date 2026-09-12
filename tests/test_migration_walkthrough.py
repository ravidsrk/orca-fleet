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
