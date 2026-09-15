#!/usr/bin/env python3
"""
Contract tests for assets/diagrams/generator/wire_docs.py, the script that embeds the
generated images into the docs.

PR #387 review: the README heading `## Proof status — honesty first` became `## Proof status`
and the script kept the old anchor. Nothing noticed, because an anchor was checked only when
its picture was missing — the committed embed hid the drift, and the documented rerun would
have failed at the next regeneration instead. The script now checks every anchor on every run,
and the committed docs must be its fixed point.

    python3 -m unittest tests.test_wire_docs -v
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "assets" / "diagrams" / "generator" / "wire_docs.py"


def wired_docs():
    """Every file the script edits, relative to the repo root."""
    docs = ["README.md", "docs/concepts.md", "docs/getting-started.md", "docs/verify-gate.md",
            "docs/missions/README.md", "docs/guides/anatomy-of-a-run.md"]
    docs += sorted(f"docs/missions/{d.name}.md" for d in (ROOT / "skills").iterdir()
                   if d.is_dir() and not d.name.startswith((".", "_")))
    return docs


def dry_run(repo):
    return subprocess.run([sys.executable, str(SCRIPT), str(repo), "--dry-run"],
                          capture_output=True, text=True)


class WiringScriptAnchors(unittest.TestCase):
    def test_the_committed_docs_are_the_scripts_fixed_point(self):
        r = dry_run(ROOT)
        self.assertEqual(r.returncode, 0, f"wire_docs.py --dry-run failed:\n{r.stderr}")
        would = [line for line in r.stdout.splitlines() if line.startswith("would wire")]
        self.assertEqual(would, [], "the committed docs are not what the wiring script writes")

    def _copy_docs(self, tmp):
        for rel in wired_docs():
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / rel, dst)

    def test_a_renamed_heading_fails_the_rerun_even_with_the_picture_in_place(self):
        # The first cut checked an anchor only when its picture was absent; with the proof-ladder
        # embed committed, a renamed heading passed and the rerun stayed green.
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            self._copy_docs(tmp)
            readme = tmp / "README.md"
            text = readme.read_text(encoding="utf-8")
            self.assertIn("assets/diagrams/proof-ladder.jpg", text)
            self.assertEqual(text.count("## Proof status\n"), 1)
            readme.write_text(text.replace("## Proof status\n", "## Proof tiers\n", 1),
                              encoding="utf-8")
            r = dry_run(tmp)
            self.assertNotEqual(r.returncode, 0, "a renamed heading passed the rerun")
            self.assertIn("'## Proof status'", r.stderr)
            self.assertIn("'README'", r.stderr)

    def test_the_unchanged_copy_passes(self):
        # The negative case fails for the rename, not for the copy.
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            self._copy_docs(tmp)
            r = dry_run(tmp)
            self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
