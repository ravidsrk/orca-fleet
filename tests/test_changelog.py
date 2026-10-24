#!/usr/bin/env python3
"""CHANGELOG entries as changelog.d/ fragments (scripts/changelog.py; CI speed and bookkeeping).

Every PR used to add its entry at the top of CHANGELOG.md's [Unreleased], so every merge put every
other open PR into conflict on that one spot. These pin the replacement: a fragment's shape is
checked where it sits, CI refuses a new entry in the shared section, and the release cut folds
every fragment (and the entries written before fragments existed) into the dated section once,
newest first, and deletes them. Each guard is shown failing on the shape it exists to refuse.

    python3 -m unittest tests.test_changelog -v
"""
import contextlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "changelog.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


def load(path=SCRIPT, name="_changelog_under_test"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cl = load()

CHANGELOG = """# Changelog

Preamble.

## [Unreleased]

- **Older entry one** (#1). Written straight into the section,
  before fragments existed.
- **Older entry two** (#2).

## [0.1.0] - 2026-01-01

- **First release.**
"""

GOOD = "- **A change** (#9). See [the guide](../docs/guide.md).\n  It continues here.\n"


def git_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    return env


def git(repo, *args, when=None):
    env = git_env()
    if when is not None:
        env.update(GIT_AUTHOR_DATE=f"{when} +0000", GIT_COMMITTER_DATE=f"{when} +0000")
    return subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                           *args], cwd=repo, env=env, capture_output=True, text=True, check=True)


def make_repo(tmp):
    """A repository with the script, a README'd changelog.d/ and CHANGELOG.md, committed."""
    repo = Path(tmp) / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "changelog.py")
    (repo / "changelog.d").mkdir()
    (repo / "changelog.d" / "README.md").write_text("# fragments\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8")
    (repo / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base", when="2026-01-02T00:00:00")
    return repo


def run_cli(repo, *args):
    """changelog.main in this process, its ROOT pointed at `repo`: the CLI's own code path, traced
    by the suite's coverage (a subprocess of a copied script would not be)."""
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(cl, "ROOT", repo), contextlib.redirect_stdout(out), \
            contextlib.redirect_stderr(err):
        rc = cl.main(list(args))
    return subprocess.CompletedProcess(args, rc, out.getvalue(), err.getvalue())


class FragmentsAreWellFormed(unittest.TestCase):
    def test_the_live_fragments_fold_cleanly(self):
        self.assertTrue((ROOT / "changelog.d" / "README.md").is_file())
        self.assertEqual(cl.check_fragments(ROOT / "changelog.d"), [])

    def test_a_good_fragment_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "README.md").write_text("x\n", encoding="utf-8")
            (d / "629-floor-guard.md").write_text(GOOD + "- **A second entry.**\n",
                                                  encoding="utf-8")
            self.assertEqual(cl.check_fragments(d), [])

    def test_each_shape_that_breaks_the_release_list_is_refused(self):
        cases = {
            "Upper.md": (GOOD, "name it <slug>.md"),
            "notes.txt": (GOOD, "name it <slug>.md"),
            "empty.md": ("\n", "empty"),
            "no-newline.md": (GOOD.rstrip("\n"), "does not end with a newline"),
            "crlf.md": (GOOD.replace("\n", "\r\n"), "carriage return"),
            "prose.md": ("A sentence, not an entry.\n", "opens with '- '"),
            "blank.md": ("- **One.**\n\n- **Two.**\n", "blank line"),
            "heading.md": ("- **One.**\n### Added\n", "heading"),
            "unindented.md": ("- **One.**\ncontinuation at column 0\n", "two spaces"),
            "root-link.md": ("- **One** [x](docs/guide.md).\n", "must be written from changelog.d/"),
            "deep-link.md": ("- **One** [x](../../outside.md).\n", "must be written from changelog.d/"),
            "latin1.md": (None, "not readable as UTF-8"),
        }
        for name, (text, why) in cases.items():
            with self.subTest(fragment=name), tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                (d / "README.md").write_text("x\n", encoding="utf-8")
                if text is None:
                    (d / name).write_bytes("- caf\xe9\n".encode("latin-1"))
                else:
                    (d / name).write_bytes(text.encode("utf-8"))
                errors = cl.check_fragments(d)
                self.assertTrue(any(name in e and why in e for e in errors),
                                f"{name}: {errors}")

    def test_absolute_links_and_anchors_need_no_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "README.md").write_text("x\n", encoding="utf-8")
            (d / "links.md").write_text("- **One** [a](https://example.invalid/x) [b](#top).\n",
                                        encoding="utf-8")
            self.assertEqual(cl.check_fragments(d), [])

    def test_a_missing_readme_fails_rather_than_passing_an_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = cl.check_fragments(Path(tmp) / "changelog.d")
        self.assertEqual(len(errors), 1)
        self.assertIn("README.md is missing", errors[0])


class HtmlLinksAreRefused(unittest.TestCase):
    """PR #670 review (P2, PRRT_kwDOTWxN9c6v5pBw): as_released rewrites Markdown links for the
    root-level CHANGELOG.md but not HTML ones, so a relative <a href> passed in changelog.d/ and broke
    once assembled. A fragment holds Markdown links only."""

    def test_a_relative_html_link_is_refused(self):
        for text in ('- **Change** <a href="../docs/ops.md">ops</a>.\n',
                     "- **Change** <a href='../docs/ops.md'>ops</a>.\n",
                     '- **Change** <img src="../assets/x.png">.\n'):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                (d / "README.md").write_text("x\n", encoding="utf-8")
                (d / "html.md").write_text(text, encoding="utf-8")
                errors = cl.check_fragments(d)
                self.assertTrue(any("html.md" in e and "Markdown link" in e for e in errors), errors)


class HtmlSplitAcrossLinesIsRefused(unittest.TestCase):
    """PR #670 review (P2): the HTML check ran per line, so `<a` on one line and its `href=` on
    the next passed and survived assembly. The whole fragment is checked."""

    def test_a_tag_split_across_lines_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "README.md").write_text("x\n", encoding="utf-8")
            (d / "split.md").write_text('- **Change** <a\n  href="../docs/ops.md">ops</a>.\n',
                                        encoding="utf-8")
            errors = cl.check_fragments(d)
            self.assertTrue(any("split.md" in e and "Markdown link" in e for e in errors), errors)

    def test_a_quoted_angle_bracket_does_not_hide_the_link(self):
        # Codex (PR #671): `[^>]*` stopped at a `>` inside a quoted attribute.
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "README.md").write_text("x\n", encoding="utf-8")
            (d / "quoted.md").write_text('- **Change** <a title=">"\n  href="../docs/ops.md">ops</a>.\n',
                                         encoding="utf-8")
            errors = cl.check_fragments(d)
            self.assertTrue(any("quoted.md" in e and "Markdown link" in e for e in errors), errors)


class TheSharedSectionTakesNoNewEntry(unittest.TestCase):
    """`check --base`: the count of [Unreleased] entries may not grow on a pull request."""

    def test_a_new_entry_in_unreleased_fails_and_names_the_fragment_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            text = CHANGELOG.replace("## [Unreleased]\n\n", "## [Unreleased]\n\n- **Mine.**\n")
            (repo / "CHANGELOG.md").write_text(text, encoding="utf-8")
            errors = cl.check_base("HEAD", repo)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("grew from 2 to 3", errors[0])
            self.assertIn("**Mine.**", errors[0])
            self.assertIn("changelog.d/<slug>.md", errors[0])
            r = run_cli(repo, "check", "--base", "HEAD")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("FAIL CHANGELOG.md's [Unreleased] grew", r.stdout)

    def test_an_edited_entry_or_an_emptied_section_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            for text in (CHANGELOG.replace("Older entry one", "Older entry 1"),
                         CHANGELOG.replace("- **Older entry two** (#2).\n", ""),
                         "# Changelog\n\n## [Unreleased]\n\n## [0.2.0] - 2026-02-01\n\n- x\n"):
                with self.subTest(text=text[:60]):
                    (repo / "CHANGELOG.md").write_text(text, encoding="utf-8")
                    self.assertEqual(cl.check_base("HEAD", repo), [])
            (repo / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
            r = run_cli(repo, "check", "--base", "HEAD")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_base_without_a_changelog_cannot_be_compared(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            with self.assertRaises(ValueError):
                cl.check_base("no-such-ref-xyz", repo)
            r = run_cli(repo, "check", "--base", "no-such-ref-xyz")
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_two_unreleased_headings_are_refused_not_guessed(self):
        with self.assertRaises(ValueError):
            cl.unreleased_entries(CHANGELOG + "\n## [Unreleased]\n")
        with self.assertRaises(ValueError):
            cl.unreleased_entries(CHANGELOG.replace("## [Unreleased]\n", ""))

    def test_ci_runs_it_on_every_pull_request_through_env(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        checks = text.split("\n  checks:\n", 1)[1].split("\n  gates:\n", 1)[0]
        step = checks.split("scripts/changelog.py check --base", 1)
        self.assertEqual(len(step), 2, "the checks job does not run changelog.py check --base")
        block = step[0].rsplit("\n      - ", 1)[1] + step[1].split("\n      - ", 1)[0]
        self.assertIn("if: github.event_name == 'pull_request'", block)
        self.assertIn("PR_BASE_SHA: ${{ github.event.pull_request.base.sha }}", block)
        self.assertEqual(step[1].split("\n", 1)[0], ' "$PR_BASE_SHA"')


class TheCutFoldsEverythingOnce(unittest.TestCase):
    def test_fragments_fold_newest_first_then_the_older_entries_and_are_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            frag = repo / "changelog.d"
            (frag / "aaa-first.md").write_text("- **First landed.**\n", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "first", when="2026-01-03T00:00:00")
            (frag / "zzz-second.md").write_text(GOOD, encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "second", when="2026-01-04T00:00:00")
            (frag / "mmm-uncommitted.md").write_text("- **Not committed yet.**\n",
                                                     encoding="utf-8")
            preview = run_cli(repo, "preview")
            self.assertEqual(preview.returncode, 0, preview.stderr)
            r = run_cli(repo, "assemble", "0.2.0", "2026-02-01")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("folds 3 fragment(s) and 2 earlier [Unreleased] entries", r.stdout)
            text = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
            want_body = ("- **Not committed yet.**\n"
                         "- **A change** (#9). See [the guide](docs/guide.md).\n  It continues here.\n"
                         "- **First landed.**\n"
                         "- **Older entry one** (#1). Written straight into the section,\n"
                         "  before fragments existed.\n"
                         "- **Older entry two** (#2).\n")
            self.assertIn("## [Unreleased]\n\n## [0.2.0] - 2026-02-01\n\n" + want_body
                          + "\n## [0.1.0] - 2026-01-01\n", text)
            self.assertEqual(preview.stdout, want_body)
            self.assertTrue(text.startswith("# Changelog\n\nPreamble.\n\n"))
            self.assertEqual(sorted(p.name for p in frag.iterdir()), ["README.md"])
            self.assertEqual(cl.check_released(repo), [])
            self.assertEqual(run_cli(repo, "check", "--released").returncode, 0)
            # The section exists now: a second cut of the same version is refused, unwritten.
            again = run_cli(repo, "assemble", "0.2.0", "2026-02-02")
            self.assertEqual(again.returncode, 2, again.stdout + again.stderr)
            self.assertEqual((repo / "CHANGELOG.md").read_text(encoding="utf-8"), text)

    def test_unfolded_work_fails_the_released_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            errors = cl.check_released(repo)
            self.assertTrue(any("2 entries still under ## [Unreleased]" in e for e in errors), errors)
            (repo / "changelog.d" / "late.md").write_text("- **Late.**\n", encoding="utf-8")
            self.assertTrue(any("not folded" in e and "late.md" in e
                                for e in cl.check_released(repo)))
            self.assertEqual(run_cli(repo, "check", "--released").returncode, 1)

    def test_nothing_is_written_when_anything_is_wrong(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            (repo / "changelog.d" / "bad.md").write_text("no bullet\n", encoding="utf-8")
            for args in (("0.2.0", "2026-02-01"), ("v0.2.0", "2026-02-01"),
                         ("0.2.0", "2026-02-30")):
                with self.subTest(args=args):
                    r = run_cli(repo, "assemble", *args)
                    self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                    self.assertEqual((repo / "CHANGELOG.md").read_text(encoding="utf-8"),
                                     CHANGELOG)
                    self.assertTrue((repo / "changelog.d" / "bad.md").is_file())

    def test_an_empty_release_still_cuts_and_says_so(self):
        # Parity with the cut before fragments: an empty [Unreleased] made an empty section, and
        # the release walkthrough rehearses exactly that from a published cut. It warns.
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            (repo / "CHANGELOG.md").write_text(
                "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-01-01\n\n- x\n",
                encoding="utf-8")
            r = run_cli(repo, "assemble", "0.2.0", "2026-02-01")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("the release section is empty", r.stderr)
            self.assertIn("## [Unreleased]\n\n## [0.2.0] - 2026-02-01\n\n## [0.1.0]",
                          (repo / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_the_release_blocks_fold_and_stage_the_fragments(self):
        ops = (ROOT / "docs" / "ops.md").read_text(encoding="utf-8")
        prepare, cut = (re.search(rf"<!-- release:{name} -->\s*```bash\n(.*?)```", ops, re.S).group(1)
                        for name in ("prepare", "cut"))
        self.assertIn('["scripts/changelog.py", "assemble", version, day]', prepare)
        self.assertNotIn('text.replace("## [Unreleased]"', prepare)
        self.assertRegex(cut, r"git add CHANGELOG\.md changelog\.d ")


class TheScriptRunsAsAProgram(unittest.TestCase):
    def test_check_and_preview_from_a_subprocess(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            (repo / "changelog.d" / "one.md").write_text("- **One.**\n", encoding="utf-8")
            script = str(repo / "scripts" / "changelog.py")
            r = subprocess.run([sys.executable, script, "check"], cwd=repo, env=git_env(),
                               capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("1 fragment(s) well formed", r.stdout)
            r = subprocess.run([sys.executable, script, "preview"], cwd=repo, env=git_env(),
                               capture_output=True, text=True, timeout=60)
            self.assertTrue(r.stdout.startswith("- **One.**\n- **Older entry one**"), r.stdout)


class ValidateRunsTheShapeCheck(unittest.TestCase):
    def test_validate_reports_a_malformed_fragment(self):
        spec = importlib.util.spec_from_file_location("_validate_cl", ROOT / "scripts" / "validate.py")
        validate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate)
        self.assertEqual(validate.check_changelog_fragments(), [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            shutil.copy2(SCRIPT, root / "scripts" / "changelog.py")
            (root / "changelog.d").mkdir()
            (root / "changelog.d" / "README.md").write_text("x\n", encoding="utf-8")
            (root / "changelog.d" / "oops.md").write_text("### Added\n", encoding="utf-8")
            with mock.patch.object(validate, "ROOT", root):
                errors = validate.check_changelog_fragments()
            self.assertTrue(any("oops.md" in e for e in errors), errors)
            shutil.rmtree(root / "scripts")
            with mock.patch.object(validate, "ROOT", root):
                self.assertIn("scripts/changelog.py missing",
                              validate.check_changelog_fragments()[0])


class OnlyACompleteLinkTagIsRefused(unittest.TestCase):
    """Codex at 54fe725bee: the HTML check over-blocked. `x<a` on one line and the words
    `href=value` on a later one, with no tag ever closed, were refused, and so was
    `<span data-href=...>`, which has no link attribute. The check now reads raw HTML as CommonMark
    does: a COMPLETE open tag carrying an attribute named exactly href or src, outside a code span."""

    ACCEPTED = (
        "- **Change** x<a\n  and later the words href=value appear in prose.\n",
        '- **Change** <span data-href="identifier">plain</span>.\n',
        '- **Change** the check now names `<a href="../docs/ops.md">` as code, not a link.\n',
        '- **Change** a double span ``<img src="../x.png">`` is code too.\n',
        '- **Change** `x` and `<a href="../docs/ops.md">ops</a>` are both spans.\n',
        '- **Change** <a name="anchor">no link attribute</a>.\n',
        '- **Change** an escaped \\<a href="../docs/ops.md"> is text.\n',
    )
    REFUSED = (
        '- **Change** <a\n  title="x"\n  href="../docs/ops.md">ops</a>.\n',
        '- **Change** <A HREF=../docs/ops.md>ops</A>.\n',
        '- **Change** <img src="../assets/x.png"/>.\n',
        '- **Change** an unclosed `span, then <a href="../docs/ops.md">ops</a>.\n',
        '- **Change** `code` then <a href="../docs/ops.md">ops</a>.\n',
    )

    def errors(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "README.md").write_text("x\n", encoding="utf-8")
            (d / "entry.md").write_text(text, encoding="utf-8")
            return [e for e in cl.check_fragments(d) if "Markdown link" in e]

    def test_what_renders_as_no_link_is_accepted(self):
        for text in self.ACCEPTED:
            with self.subTest(text=text):
                self.assertEqual(self.errors(text), [])

    def test_a_complete_link_tag_outside_code_is_refused(self):
        for text in self.REFUSED:
            with self.subTest(text=text):
                self.assertEqual(len(self.errors(text)), 1, text)

    def test_the_run_index_check_reads_html_the_same_way(self):
        # scripts/run_index.py carries its own copy (it runs alone: tests copy it into a bare root).
        spec = importlib.util.spec_from_file_location("_run_index_for_changelog",
                                                      ROOT / "scripts" / "run_index.py")
        ri = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ri)
        for text in self.ACCEPTED + self.REFUSED:
            with self.subTest(text=text):
                self.assertEqual(ri.html_link(text), cl.html_link(text))


if __name__ == "__main__":
    unittest.main()
