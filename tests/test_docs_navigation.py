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


if __name__ == "__main__":
    unittest.main(verbosity=2)
