#!/usr/bin/env python3
"""Contract tests for runtime/scripts/inventory.py.

Both real inventory shapes in this repo are exercised directly, because a parser
that only handles the fixtures it was written against is a parser that will
silently skip the next report. The exit-2 case matters most: an inventory whose
paths have all moved verified nothing, and "nothing verified" must not read as
"all verified".
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "runtime" / "scripts" / "inventory.py"
SHIP_RUN = ROOT / "docs" / "runs" / "2026-08-28-ship-it-self-run.md"
NEGCTRL = ROOT / "demo" / "negative-control" / "README.md"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


EXIT_MISMATCH = 1   # inventory.py's own mismatch code; asserted against the script in test_script_shape


def run_inv(*args):
    return subprocess.run([sys.executable, str(INVENTORY), *args], capture_output=True, text=True)


class InventoryBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="inventory-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def artifact(self, rel, text):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def fenced_report(self, entries, heading="## Run-close integrity inventory (sha256)"):
        body = "\n".join(f"{h}  {p}" for p, h in entries)
        report = self.tmp / "report.md"
        report.write_text(
            f"# Run\n\nsome prose\n\n{heading}\n\n```\n{body}\n```\n\n## Gates\n\n- none\n",
            encoding="utf-8")
        return report

    def table_report(self, entries):
        rows = "\n".join(f"| `{p}` | `{h}` |" for p, h in entries)
        report = self.tmp / "README.md"
        report.write_text(
            "# demo\n\n## Integrity inventory (sha256)\n\n"
            "| Artifact | sha256 |\n|----------|--------|\n" + rows + "\n\n(note)\n",
            encoding="utf-8")
        return report


class TestFencedBlock(InventoryBase):
    def test_matching_hashes_verify(self):
        self.artifact("a.txt", "alpha\n")
        report = self.fenced_report([("a.txt", sha("alpha\n"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 verified", r.stdout)

    def test_a_changed_artifact_is_a_mismatch(self):
        self.artifact("a.txt", "beta\n")
        report = self.fenced_report([("a.txt", sha("alpha\n"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 1)
        self.assertIn("MISMATCH", r.stderr)
        self.assertIn("a.txt", r.stderr)

    def test_several_entries_are_all_read(self):
        self.artifact("a.txt", "alpha\n")
        self.artifact("sub/b.txt", "beta\n")
        report = self.fenced_report([("a.txt", sha("alpha\n")), ("sub/b.txt", sha("beta\n"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("2 verified", r.stdout)

    def test_a_retired_path_is_missing_not_mismatched(self):
        self.artifact("a.txt", "alpha\n")
        report = self.fenced_report([("a.txt", sha("alpha\n")), ("gone.txt", sha("x"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MISSING", r.stdout)
        self.assertIn("1 verified", r.stdout)

    def test_no_listed_path_exists_is_exit_2(self):
        report = self.fenced_report([("gone.txt", sha("x")), ("also-gone.txt", sha("y"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 2, "a verification that examined nothing is not a pass")
        self.assertIn("nothing was verified", r.stderr)

    def test_heading_with_extra_words_is_found(self):
        self.artifact("a.txt", "alpha\n")
        report = self.fenced_report([("a.txt", sha("alpha\n"))],
                                    heading="### Wave two integrity inventory (sha256)")
        self.assertEqual(run_inv("check", str(report)).returncode, 0)

    def test_no_inventory_heading_is_exit_2(self):
        report = self.tmp / "plain.md"
        report.write_text("# Run\n\nno inventory here\n", encoding="utf-8")
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 2)
        self.assertIn("no '## … integrity inventory", r.stderr)

    def test_an_empty_block_is_exit_2(self):
        report = self.tmp / "empty.md"
        report.write_text("# Run\n\n## Integrity inventory (sha256)\n\n```\n```\n", encoding="utf-8")
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 2)
        self.assertIn("lists no", r.stderr)

    def test_an_unreadable_report_is_exit_2(self):
        r = run_inv("check", str(self.tmp / "does-not-exist.md"))
        self.assertEqual(r.returncode, 2)

    def test_the_block_stops_at_the_next_heading(self):
        self.artifact("a.txt", "alpha\n")
        first, other = sha("alpha\n"), sha("zzz")
        report = self.tmp / "report.md"
        report.write_text(
            "## Integrity inventory (sha256)\n\n```\n"
            + f"{first}  a.txt\n```\n\n"
            + "## Other\n\n```\n"
            + f"{other}  never-read.txt\n```\n", encoding="utf-8")
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 verified", r.stdout)
        self.assertNotIn("never-read.txt", r.stdout + r.stderr)


class TestSecondInventoryBlock(InventoryBase):
    """#315: only the FIRST `## … integrity inventory (sha256)` heading was ever read. A second
    block later in the same document was neither hashed nor compared, so a report could carry an
    honest inventory a tool checks and a fabricated one a human reads."""

    def two_block_report(self, first, second):
        def fence(entries):
            return "```\n" + "\n".join(f"{h}  {p}" for p, h in entries) + "\n```"
        report = self.tmp / "report.md"
        report.write_text(
            "# Run\n\nprose\n\n"
            "## Run-close integrity inventory (sha256)\n\n" + fence(first) + "\n\n"
            "## Appendix\n\nmore prose\n\n"
            "## Second integrity inventory (sha256)\n\n" + fence(second) + "\n\n"
            "## Gates\n\n- none\n",
            encoding="utf-8")
        return report

    def test_a_fabricated_second_block_is_a_mismatch(self):
        self.artifact("a.txt", "alpha\n")
        report = self.two_block_report([("a.txt", sha("alpha\n"))],
                                       [("a.txt", sha("something else entirely\n"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, EXIT_MISMATCH,
                         f"the second block was never checked: {r.stdout}")
        self.assertIn("MISMATCH", r.stderr)

    def test_both_honest_blocks_verify(self):
        self.artifact("a.txt", "alpha\n")
        self.artifact("b.txt", "beta\n")
        report = self.two_block_report([("a.txt", sha("alpha\n"))], [("b.txt", sha("beta\n"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("2 verified", r.stdout)

    def test_write_refreshes_every_block(self):
        self.artifact("a.txt", "alpha\n")
        self.artifact("b.txt", "beta\n")
        report = self.two_block_report([("a.txt", sha("stale\n"))], [("b.txt", sha("stale\n"))])
        r = run_inv("write", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("updated 2 hash(es)", r.stdout)
        self.assertEqual(run_inv("check", str(report)).returncode, 0)


class TestTableBlock(InventoryBase):
    def test_table_rows_are_parsed(self):
        self.artifact("head-to-head.txt", "transcript\n")
        report = self.table_report([("head-to-head.txt", sha("transcript\n"))])
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 verified", r.stdout)

    def test_table_separator_row_is_skipped(self):
        self.artifact("head-to-head.txt", "transcript\n")
        report = self.table_report([("head-to-head.txt", sha("transcript\n"))])
        r = run_inv("check", str(report))
        self.assertNotIn("MISSING  ---", r.stdout)

    def test_table_mismatch_is_exit_1(self):
        self.artifact("head-to-head.txt", "changed\n")
        report = self.table_report([("head-to-head.txt", sha("transcript\n"))])
        self.assertEqual(run_inv("check", str(report)).returncode, 1)

    def test_paths_resolve_relative_to_the_report_directory(self):
        self.artifact("nested/README.md", "x")
        (self.tmp / "nested" / "sibling.txt").write_text("sibling\n", encoding="utf-8")
        digest = sha("sibling\n")
        report = self.tmp / "nested" / "README.md"
        report.write_text(
            "## Integrity inventory (sha256)\n\n| Artifact | sha256 |\n|---|---|\n"
            + f"| `sibling.txt` | `{digest}` |\n", encoding="utf-8")
        r = run_inv("check", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)


class TestWrite(InventoryBase):
    def test_write_refreshes_a_stale_hash(self):
        self.artifact("a.txt", "beta\n")
        report = self.fenced_report([("a.txt", sha("alpha\n"))])
        r = run_inv("write", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(sha("beta\n"), report.read_text(encoding="utf-8"))
        self.assertEqual(run_inv("check", str(report)).returncode, 0)

    def test_write_preserves_the_table_shape(self):
        self.artifact("head-to-head.txt", "changed\n")
        report = self.table_report([("head-to-head.txt", sha("transcript\n"))])
        run_inv("write", str(report))
        text = report.read_text(encoding="utf-8")
        self.assertIn("| `head-to-head.txt` |", text)
        self.assertIn(sha("changed\n"), text)

    def test_dry_run_changes_nothing(self):
        self.artifact("a.txt", "beta\n")
        report = self.fenced_report([("a.txt", sha("alpha\n"))])
        before = report.read_text(encoding="utf-8")
        r = run_inv("write", str(report), "--dry-run")
        self.assertEqual(r.returncode, 0)
        self.assertIn("would update 1", r.stdout)
        self.assertEqual(report.read_text(encoding="utf-8"), before)

    def test_write_refuses_when_a_listed_path_is_gone(self):
        report = self.fenced_report([("gone.txt", sha("x"))])
        r = run_inv("write", str(report))
        self.assertEqual(r.returncode, 1)
        self.assertIn("does not exist", r.stderr)

    def test_write_is_idempotent(self):
        self.artifact("a.txt", "alpha\n")
        report = self.fenced_report([("a.txt", sha("alpha\n"))])
        run_inv("write", str(report))
        first = report.read_text(encoding="utf-8")
        run_inv("write", str(report))
        self.assertEqual(report.read_text(encoding="utf-8"), first)


class TestRealReports(unittest.TestCase):
    """The two shapes that already exist in this repo must both parse."""

    def test_ship_it_run_report_parses_every_entry(self):
        r = run_inv("check", str(SHIP_RUN))
        self.assertIn(r.returncode, (0, 1), r.stderr)
        self.assertNotEqual(r.returncode, 2, "the fenced run-close inventory must parse")
        counts = r.stdout.strip().splitlines()[-1]
        self.assertRegex(counts, r"(\d+) verified, (\d+) mismatched, (\d+) missing")
        total = sum(int(n) for n in counts.replace(",", " ").split()
                    if n.isdigit())
        self.assertEqual(total, 5, f"expected 5 inventory entries, got: {counts}")

    def test_ship_it_immutable_run_artifacts_still_verify(self):
        r = run_inv("check", str(SHIP_RUN))
        for immutable in ("frozen-spec.md", "build-manifest.json", "negctrl.txt"):
            self.assertNotIn(immutable, r.stderr,
                             f"{immutable} is declared immutable and must still hash true")

    def test_negative_control_readme_table_parses_and_verifies(self):
        # The table form (| `file` | `hash` |) must parse, and the demo's own
        # transcript must hash true: its recorded hash drifted from the
        # committed file once (docs/reviews/2026-09-10-review.md 7.4) and the inventory check is what
        # keeps that from recurring silently.
        r = run_inv("check", str(NEGCTRL))
        self.assertEqual(r.returncode, 0,
                         f"the demo inventory must verify:\n{r.stdout}\n{r.stderr}")
        self.assertIn("1 verified", r.stdout + r.stderr)
        self.assertIn("0 mismatched", r.stdout + r.stderr)


class TestScriptShape(unittest.TestCase):
    def test_executable_and_shebanged(self):
        self.assertTrue(os.access(INVENTORY, os.X_OK))
        self.assertTrue(INVENTORY.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"))

    def test_the_mismatch_exit_code_this_module_asserts_is_the_script_s(self):
        # A constant restated in a test is a second source of truth: if inventory.py renumbered
        # its exit codes, every mismatch assertion here would keep passing against the old number.
        src = INVENTORY.read_text(encoding="utf-8")
        self.assertIn(f"EXIT_MISMATCH = {EXIT_MISMATCH}\n", src,
                      "tests assert a mismatch code the script no longer uses")

    def test_help_names_both_subcommands(self):
        r = run_inv("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("write", r.stdout)
        self.assertIn("check", r.stdout)


class TestCheckAtRevision(unittest.TestCase):
    """`--at <rev>` hashes the git blob, not the working tree (issue #259).

    A dated report pins artifacts at the tip it closed on; the tree always moves
    afterwards. Re-hashing at the recorded commit is what keeps the pin meaningful
    — and it is the half a fabricated report cannot produce.
    """

    REPORT = "docs/runs/2026-08-28-ship-it-self-run.md"

    def test_re_derives_at_the_commit_the_report_names(self):
        r = run_inv("check", self.REPORT, "--at", "748b328")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("5 verified, 0 mismatched", r.stdout)

    def test_the_same_inventory_does_not_match_the_moved_tree(self):
        # Not a defect in the report: two of its paths are repo files that changed
        # after the run. Without --at, that is a mismatch; with it, it is not.
        r = run_inv("check", self.REPORT)
        self.assertEqual(r.returncode, 1, r.stdout)

    def test_an_unresolvable_revision_cannot_run(self):
        r = run_inv("check", self.REPORT, "--at", "deadbeef")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("is not a commit", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
