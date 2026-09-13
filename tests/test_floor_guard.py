#!/usr/bin/env python3
"""Contract tests for runtime/scripts/floor_guard.py.

Every test builds a real, hermetic git repo in a temp dir: the guard's whole job
is reading a diff, so a fake diff would test nothing. The exit contract is the
load-bearing part — a 2 that reads as a 0 is the failure mode this script exists
to prevent — so every could-not-run path is asserted explicitly.
"""
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "runtime" / "scripts" / "floor_guard.py"
_spec = importlib.util.spec_from_file_location("floor_guard", GUARD)
floor_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(floor_guard)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)


def write(repo, rel, text):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def run_guard(repo, *args):
    return subprocess.run(
        [sys.executable, str(GUARD), "--repo", str(repo), *args],
        capture_output=True, text=True,
    )


BASE_CONSTRAINTS = """# CONSTRAINTS

| id | dimension | floor |
|----|-----------|-------|
| D1 | coverage | 85 |
| D2 | latency-ms | 250 |

## Exceptions

(none)
"""

BASE_TEST = """def test_thing():
    assert compute() == 4
    assert other() == 5
"""


class FloorGuardBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="floorguard-")
        self.repo = Path(self.tmp) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.invalid")
        git(self.repo, "config", "user.name", "t")
        write(self.repo, "CONSTRAINTS.md", BASE_CONSTRAINTS)
        write(self.repo, "FLOOR.md", "| D1 | coverage | 85 |\n")
        write(self.repo, "tests/test_thing.py", BASE_TEST)
        write(self.repo, "src/thing.spec.js", "it('x', () => {\n  expect(a).toBe(1);\n  expect(b).toBe(2);\n});\n")
        write(self.repo, "src/app.py", "def compute():\n    assert True\n    return 4\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")
        git(self.repo, "checkout", "-q", "-b", "work")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit(self, message="change"):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", message)


class TestCleanAndExitCodes(FloorGuardBase):
    def test_no_changes_is_clean(self):
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("clean", r.stdout)

    def test_benign_change_is_clean(self):
        write(self.repo, "src/app.py", "def compute():\n    return 4\n\n\ndef extra():\n    return 1\n")
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_not_a_git_repo_exits_2(self):
        plain = Path(self.tmp) / "plain"
        plain.mkdir()
        r = run_guard(plain, "--base", "main")
        self.assertEqual(r.returncode, 2)
        self.assertIn("could not run", r.stderr)

    def test_unresolvable_base_exits_2_not_0(self):
        r = run_guard(self.repo, "--base", "origin/does-not-exist")
        self.assertEqual(r.returncode, 2, "a base that does not resolve must never read as clean")
        self.assertIn("not resolvable", r.stderr)

    def test_help_exits_zero(self):
        r = subprocess.run([sys.executable, str(GUARD), "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("--base", r.stdout)

    def test_exit_codes_are_documented_in_the_docstring(self):
        text = GUARD.read_text(encoding="utf-8")
        for token in ("0  clean", "1  at least one", "2  the guard could not run"):
            self.assertIn(token, text)


class TestDiffAcquisition(FloorGuardBase):
    def test_disappearing_untracked_file_is_exit_2(self):
        path = write(self.repo, "disappearing.py", "value = 1\n")
        real_run = subprocess.run
        comparisons = []

        def disappear_before_comparison(argv, **kwargs):
            if "--no-index" in argv:
                path.unlink()
                result = real_run(argv, **kwargs)
                comparisons.append(result)
                return result
            return real_run(argv, **kwargs)

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(floor_guard.subprocess, "run", side_effect=disappear_before_comparison), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = floor_guard.main(["--repo", str(self.repo), "--base", "main"])
        self.assertEqual(len(comparisons), 1)
        self.assertEqual(comparisons[0].returncode, 1)
        self.assertEqual(comparisons[0].stdout, "")
        self.assertTrue(comparisons[0].stderr)
        self.assertEqual(rc, 2, out.getvalue() + err.getvalue())
        self.assertIn("untracked diff acquisition failed", err.getvalue())
        self.assertNotIn("floor-guard: clean", out.getvalue())

    def test_benign_untracked_file_is_clean(self):
        write(self.repo, "new.py", "value = 1\n")
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("floor-guard: clean", r.stdout)

    def test_each_failed_required_read_is_exit_2(self):
        write(self.repo, "new.py", "value = 1\n")
        real_run = subprocess.run
        for phase in ("tracked", "untracked-list", "untracked-diff"):
            for failure in (128, subprocess.TimeoutExpired("git", 60), OSError("unavailable")):
                with self.subTest(phase=phase, failure=failure):
                    def failing_read(argv, **kwargs):
                        target = ("untracked-list" if "ls-files" in argv else
                                  "untracked-diff" if "--no-index" in argv else
                                  "tracked" if "diff" in argv else None)
                        if target == phase:
                            if isinstance(failure, Exception):
                                raise failure
                            return subprocess.CompletedProcess(argv, failure, "", "read failed")
                        return real_run(argv, **kwargs)

                    out, err = io.StringIO(), io.StringIO()
                    with mock.patch.object(floor_guard.subprocess, "run", side_effect=failing_read), \
                            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        rc = floor_guard.main(["--repo", str(self.repo), "--base", "main"])
                    self.assertEqual(rc, 2, out.getvalue() + err.getvalue())
                    self.assertNotIn("floor-guard: clean", out.getvalue())

    def test_external_diff_and_textconv_cannot_hide_violations(self):
        git(self.repo, "config", "diff.hidden.command", "false")
        git(self.repo, "config", "diff.hidden.textconv", "true")
        write(self.repo, ".gitattributes", "*.py diff=hidden\n")
        for stage in (False, True):
            with self.subTest(staged=stage):
                write(self.repo, "src/app.py", "value = 1  # noqa\n")
                write(self.repo, "new.py", "value = 1  # noqa\n")
                if stage:
                    git(self.repo, "add", "src/app.py")
                with mock.patch.dict(os.environ, {"GIT_EXTERNAL_DIFF": "false"}):
                    r = run_guard(self.repo, "--base", "main")
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("src/app.py", r.stderr)
                self.assertIn("new.py", r.stderr)

    def test_empty_untracked_file_is_clean(self):
        write(self.repo, "empty.py", "")
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 0, r.stderr)


class TestSuppressions(FloorGuardBase):
    def _flags(self, line, path="src/app.py"):
        existing = (Path(self.repo) / path).read_text(encoding="utf-8") if (Path(self.repo) / path).exists() else ""
        write(self.repo, path, existing + line + "\n")
        self.commit()
        return run_guard(self.repo, "--base", "main")

    def test_added_noqa_is_flagged(self):
        r = self._flags("x = broken()  # noqa: E501")
        self.assertEqual(r.returncode, 1)
        self.assertIn("silenced-checker", r.stderr)

    def test_added_eslint_disable_is_flagged(self):
        r = self._flags("// eslint-disable-next-line no-unused-vars", path="src/app.js")
        self.assertEqual(r.returncode, 1)
        self.assertIn("silenced-checker", r.stderr)

    def test_added_ts_ignore_is_flagged(self):
        r = self._flags("// @ts-ignore", path="src/app.ts")
        self.assertEqual(r.returncode, 1)
        self.assertIn("silenced-checker", r.stderr)

    def test_added_type_ignore_is_flagged(self):
        r = self._flags("y = thing()  # type: ignore[arg-type]")
        self.assertEqual(r.returncode, 1)
        self.assertIn("silenced-checker", r.stderr)

    def test_added_pragma_no_cover_is_flagged(self):
        r = self._flags("if never():  # pragma: no cover")
        self.assertEqual(r.returncode, 1)
        self.assertIn("silenced-checker", r.stderr)

    def test_finding_names_rule_and_file_and_line(self):
        r = self._flags("z = 1  # noqa")
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stderr, r"\[silenced-checker\] src/app\.py:\d+")

    def test_report_never_echoes_the_suppressed_content(self):
        secret = "AKIAQQQQQQQQQQQQQQQQ"
        r = self._flags(f'token = "{secret}"  # noqa')
        self.assertEqual(r.returncode, 1)
        self.assertNotIn(secret, r.stderr + r.stdout,
                         "the guard must report the rule and location, never the matched text")


class TestSkipsAndStubs(FloorGuardBase):
    def _append_test(self, line):
        write(self.repo, "tests/test_thing.py", BASE_TEST + line + "\n")
        self.commit()
        return run_guard(self.repo, "--base", "main")

    def test_pytest_skip_marker_is_flagged(self):
        r = self._append_test("@pytest.mark.skip(reason='flaky')")
        self.assertEqual(r.returncode, 1)
        self.assertIn("test-made-easier", r.stderr)

    def test_dot_skip_is_flagged(self):
        r = self._append_test("it.skip('later', () => {})")
        self.assertEqual(r.returncode, 1)
        self.assertIn("test-made-easier", r.stderr)

    def test_xit_is_flagged(self):
        r = self._append_test("xit('broken', () => {})")
        self.assertEqual(r.returncode, 1)
        self.assertIn("test-made-easier", r.stderr)

    def test_unittest_skip_is_flagged(self):
        r = self._append_test("@unittest.skip('todo later')")
        self.assertEqual(r.returncode, 1)
        self.assertIn("test-made-easier", r.stderr)

    def test_todo_marker_is_unfinished_work(self):
        write(self.repo, "src/app.py", "def compute():\n    return 4\n\n\ndef later():\n    # TODO: implement\n    return None\n")
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unfinished-work", r.stderr)

    def test_not_implemented_stub_is_unfinished_work(self):
        write(self.repo, "src/app.py", "def compute():\n    return 4\n\n\ndef later():\n    raise NotImplementedError\n")
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unfinished-work", r.stderr)

    def test_swallowed_exception_is_unfinished_work(self):
        write(self.repo, "src/app.py", "def compute():\n    try:\n        return 4\n    except Exception: pass\n")
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unfinished-work", r.stderr)


class TestAssertionRemoval(FloorGuardBase):
    def test_removed_assertion_in_a_surviving_test_is_flagged(self):
        write(self.repo, "tests/test_thing.py", "def test_thing():\n    assert compute() == 4\n")
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("assertion-removed", r.stderr)
        self.assertIn("tests/test_thing.py", r.stderr)

    def test_removed_expect_in_a_spec_file_is_flagged(self):
        write(self.repo, "src/thing.spec.js", "it('x', () => {\n  expect(a).toBe(1);\n});\n")
        self.commit("weaken spec")
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("assertion-removed", r.stderr)

    def test_removed_assertion_in_non_test_code_is_not_flagged(self):
        write(self.repo, "src/app.py", "def compute():\n    return 4\n")
        self.commit("drop the assert from production code")
        r = run_guard(self.repo, "--base", "main")
        self.assertNotIn("assertion-removed", r.stderr)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_adding_an_assertion_is_silent(self):
        write(self.repo, "tests/test_thing.py", BASE_TEST + "    assert third() == 6\n")
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 0, "tightening is silent, loosening is loud")


class TestConstraintsFile(FloorGuardBase):
    def test_lowered_threshold_is_flagged(self):
        write(self.repo, "CONSTRAINTS.md", BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 60 |"))
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("threshold-lowered", r.stderr)
        self.assertIn("85 -> 60", r.stderr)

    def test_raised_threshold_is_silent(self):
        write(self.repo, "CONSTRAINTS.md", BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 95 |"))
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_new_exception_row_is_flagged(self):
        write(self.repo, "CONSTRAINTS.md", BASE_CONSTRAINTS + "\n| W101 | ignore the lint on legacy | until Q3 |\n")
        self.commit()
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("new-exception", r.stderr)

    def test_a_differently_named_constraints_file_is_honored(self):
        write(self.repo, "FLOOR.md", "| D1 | coverage | 10 |\n")
        self.commit("lower floor")
        r = run_guard(self.repo, "--base", "main", "--constraints", "FLOOR.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("threshold-lowered", r.stderr)


class TestUntrackedAndWaivers(FloorGuardBase):
    def test_untracked_file_is_in_scope(self):
        write(self.repo, "src/new.py", "value = 1  # noqa\n")
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1, "a guard that reads only git diff misses the new file")
        self.assertIn("src/new.py", r.stderr)

    # ---- Waivers (#313, then three rounds of PR #308 review) ----
    #
    # A waiver is a DECISIONS record whose ID carries its scope —
    # `floor-waiver:<rule>:<path-or-glob>` — and whose answer grants. Scope in the id is what lets
    # the ledger retire it: a later `superseded` row ends this waiver and no other.

    ID = "floor-waiver:silenced-checker:src/new.py"

    def _decisions(self, *lines):
        write(self.repo, "src/new.py", "value = 1  # noqa\n")
        write(self.repo, "docs/DECISIONS.md", "".join(l + "\n" for l in lines))
        return run_guard(self.repo, "--base", "main")

    def _row(self, ident, answer="allow", ts="2026-09-10T00:00:00Z", why="while the parser lands"):
        return f"{ts} · {ident} · taste · {answer} · {why} · t-1"

    def test_a_granting_waiver_exempts_the_finding(self):
        r = self._decisions(self._row(self.ID))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 waived", r.stdout)

    def test_a_waiver_for_a_different_path_does_not_exempt(self):
        r = self._decisions(self._row("floor-waiver:silenced-checker:src/other.py"))
        self.assertEqual(r.returncode, 1)

    def test_a_waiver_for_a_different_rule_does_not_exempt(self):
        r = self._decisions(self._row("floor-waiver:threshold-lowered:src/new.py"))
        self.assertEqual(r.returncode, 1)

    def test_a_superseded_waiver_stops_granting(self):
        # PR #308 review, P1. Every waiver used to share the id `floor-waiver`, so a later
        # `superseded` row named no particular waiver and an `allow` stayed live forever. A
        # supersede record does not restate the scope — that is the whole point of superseding —
        # so the waiver has to have an identity of its own for the ledger to retire.
        r = self._decisions(
            self._row(self.ID, ts="2026-09-01T00:00:00Z"),
            self._row(self.ID, answer="superseded", ts="2026-09-02T00:00:00Z",
                      why="the vendored parser landed"))
        self.assertEqual(r.returncode, 1, f"a retired waiver still granted: {r.stdout}")

    def test_a_later_denial_overrides_an_earlier_grant(self):
        r = self._decisions(
            self._row(self.ID, ts="2026-09-01T00:00:00Z"),
            self._row(self.ID, answer="deny", ts="2026-09-02T00:00:00Z", why="refused on review"))
        self.assertEqual(r.returncode, 1, f"an older allow beat a newer deny: {r.stdout}")

    def test_a_later_grant_overrides_an_earlier_denial(self):
        # Newest-wins runs both ways, or it is not newest-wins.
        r = self._decisions(
            self._row(self.ID, answer="deny", ts="2026-09-01T00:00:00Z", why="refused"),
            self._row(self.ID, ts="2026-09-02T00:00:00Z", why="reinstated: the parser slipped"))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_denied_waiver_does_not_grant(self):
        r = self._decisions(self._row(self.ID, answer="deny", why="refused on review"))
        self.assertEqual(r.returncode, 1, f"a DENIED waiver was granted: {r.stdout}")

    def test_an_explicit_glob_waives_the_subtree(self):
        r = self._decisions(self._row("floor-waiver:silenced-checker:src/**"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 waived", r.stdout)

    def test_a_bare_directory_does_not_sweep_the_tree(self):
        # #313 claimed a bare `src/` swept the tree. It never could: the old test was
        # `finding["path"] in line`, so the LINE had to contain the whole path. Kept as a guard for
        # the semantics the issue asked for, not as evidence of the bug it described.
        r = self._decisions(self._row("floor-waiver:silenced-checker:src/"))
        self.assertEqual(r.returncode, 1, f"a bare directory swept the tree: {r.stdout}")

    def test_a_glob_over_everything_is_not_a_waiver(self):
        r = self._decisions(self._row("floor-waiver:silenced-checker:**"))
        self.assertEqual(r.returncode, 1, f"`**` is a blanket, not a waiver: {r.stdout}")

    def test_a_longer_token_containing_the_rule_id_does_not_waive(self):
        r = self._decisions(self._row("floor-waiver:silenced-checkers:src/new.py"))
        self.assertEqual(r.returncode, 1, f"`silenced-checkers` is not the rule id: {r.stdout}")

    def test_a_longer_token_containing_the_path_does_not_waive(self):
        r = self._decisions(self._row("floor-waiver:silenced-checker:src/new.pyc"))
        self.assertEqual(r.returncode, 1, f"`src/new.pyc` is not `src/new.py`: {r.stdout}")

    def test_prose_naming_the_rule_and_path_is_not_a_waiver(self):
        # No prose is parsed at all now. A sentence that mentions both — including a line
        # recording that the team REFUSED the waiver, which the substring round granted — is a
        # note, not a decision about this finding.
        for why in ("silenced-checker on src/new.py",
                    "we will NOT waive silenced-checker on src/new.py",
                    "see notes/silenced-checker.md before touching src/new.py"):
            with self.subTest(why=why):
                r = self._decisions(self._row("mechanical", why=why))
                self.assertEqual(r.returncode, 1, f"prose granted a waiver: {r.stdout}")

    def test_a_waiver_in_the_old_shape_is_named_not_silently_dropped(self):
        # PR #308 review, P1. Moving scope into the id turns any pre-existing `floor-waiver` record
        # off, and a silent turn-off shows up as a red build with no reason. The old shape is NOT
        # honoured — scope-in-prose is the matching #313 removed as unsound, and a fallback would
        # restore the hole where "we will NOT waive X" grants X — but it is named, with the id to
        # write instead.
        r = self._decisions(self._row("floor-waiver", why="silenced-checker on src/new.py"))
        self.assertEqual(r.returncode, 1, "the old shape must not grant")
        self.assertIn("NOT a usable waiver", r.stderr, r.stderr)
        self.assertIn("floor-waiver:<rule>:<path>", r.stderr, r.stderr)

    def test_a_malformed_scoped_id_is_named(self):
        r = self._decisions(self._row("floor-waiver:silenced-checker"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("not `floor-waiver:<rule>:<path-or-glob>`", r.stderr, r.stderr)

    def test_a_well_formed_waiver_draws_no_migration_note(self):
        r = self._decisions(self._row(self.ID))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("NOT a usable waiver", r.stderr, r.stderr)

    def test_missing_waiver_file_is_not_a_could_not_run(self):
        r = run_guard(self.repo, "--base", "main", "--waivers", "docs/NOPE.md")
        self.assertEqual(r.returncode, 0)


class TestScriptShape(unittest.TestCase):
    def test_executable_and_shebanged(self):
        self.assertTrue(os.access(GUARD, os.X_OK), "floor_guard.py must be executable")
        self.assertTrue(GUARD.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"))

    def test_stdlib_only(self):
        text = GUARD.read_text(encoding="utf-8")
        for third_party in ("import requests", "import yaml", "import git\n"):
            self.assertNotIn(third_party, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
