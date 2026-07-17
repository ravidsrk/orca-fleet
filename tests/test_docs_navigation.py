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
import re
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

    def test_research_archive_reachable_and_dated(self):
        # Issue #36: docs/research/ was reachable only from CHANGELOG.md — no
        # navigated surface linked it, so the analysis was invisible to its
        # readers and its staleness invisible to maintainers. It must be linked
        # from at least one navigated doc, every snapshot must be indexed in the
        # archive's README, and each snapshot must open with a dated-snapshot
        # banner so its counts are read as historical, not current.
        navigated = [ROOT / "README.md", DOCS / "concepts.md", DOCS / "getting-started.md"]
        navigated += sorted((DOCS / "missions").glob("*.md"))
        navigated += sorted((DOCS / "guides").glob("*.md"))
        # an actual link target into research/ — prose that happens to contain
        # the word ("research/decision frontier") must not count as navigation.
        link = re.compile(r"\]\((?:\.\./)*(?:docs/)?research/")
        inbound = [p.name for p in navigated
                   if link.search(p.read_text(encoding="utf-8"))]
        self.assertTrue(
            inbound,
            "docs/research/ is linked from no navigated doc surface (orphan)",
        )
        research_index = (DOCS / "research" / "README.md").read_text(encoding="utf-8")
        for f in sorted((DOCS / "research").glob("2*.md")):
            self.assertIn(
                f.name, research_index,
                f"docs/research/{f.name} is missing from the archive index",
            )
            head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:10])
            self.assertIn(
                "Dated snapshot", head,
                f"docs/research/{f.name} carries no dated-snapshot banner",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
