#!/usr/bin/env python3
"""
Contract tests for the human documentation surface.

A doc surface that presents itself as complete must be machine-checked against
repo state, or it silently rots: ARCHITECTURE.md's runtime-policy list reads as
the whole runtime surface, docs/runs/README.md is the proof-honesty index the
mission frontmatter leans on, and docs/research/ only exists for readers who
can reach it. Each invariant here failed once (issue number on the test).

    python3 -m unittest discover -s tests -v
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
RUNTIME = ROOT / "runtime"


class TestDocsNavigation(unittest.TestCase):

    def test_architecture_names_every_runtime_policy(self):
        # Issue #34: the "operational details ARE the product" list omitted
        # mission-scheduling.md (and sandbox-policy.md appeared nowhere at all),
        # so a reader auditing the runtime surface off ARCHITECTURE.md missed
        # real policies. Every runtime/*.md must be named somewhere in the file.
        arch = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for f in sorted(RUNTIME.glob("*.md")):
            self.assertIn(
                f.stem, arch,
                f"runtime/{f.name} is a load-bearing policy ARCHITECTURE.md never names",
            )

    def test_run_archive_index_lists_every_report(self):
        # Issue #35: the index predated the newest run — the report that backs
        # oss-contribute's `proof: external-run` frontmatter was invisible from
        # the archive's own index. Every dated report must be a linked row.
        index = (DOCS / "runs" / "README.md").read_text(encoding="utf-8")
        for f in sorted((DOCS / "runs").glob("2*.md")):
            self.assertIn(
                f"({f.name})", index,
                f"docs/runs/{f.name} is not linked from the run-archive index",
            )

    def test_run_archive_integrity_standard_matches_practice(self):
        # Issue #35: the index claimed every report carries a run-close sha256
        # integrity inventory, while the oss-contribute report retains its
        # inventory in the fork worktree. Stated standard must equal actual
        # practice: a report either carries the inline inventory or names where
        # its inventory is retained — and the index's stated standard must
        # acknowledge that retained-elsewhere form the moment any report uses it.
        index = (DOCS / "runs" / "README.md").read_text(encoding="utf-8")
        for f in sorted((DOCS / "runs").glob("2*.md")):
            text = f.read_text(encoding="utf-8")
            if "integrity inventory (sha256)" in text:
                continue  # inline inventory — the strong form
            self.assertRegex(
                text, r"(?i)integrity inventory[^.]*retained",
                f"docs/runs/{f.name} has neither an inline sha256 inventory nor "
                f"a named retention location for one",
            )
            self.assertRegex(
                index, r"(?i)retained",
                f"the index claims every report carries an inline sha256 "
                f"inventory, but docs/runs/{f.name} retains its inventory "
                f"out-of-repo — stated standard != practice",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
