#!/usr/bin/env python3
"""Contract tests for runtime/scripts/floor_guard.py.

Every test builds a real, hermetic git repo in a temp dir: the guard's whole job
is reading a diff, so a fake diff would test nothing. The exit contract is the
load-bearing part — a 2 that reads as a 0 is the failure mode this script exists
to prevent — so every could-not-run path is asserted explicitly.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "runtime" / "scripts" / "floor_guard.py"


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

    def test_waiver_naming_rule_and_path_exempts(self):
        write(self.repo, "src/new.py", "value = 1  # noqa\n")
        write(self.repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver · taste · allow · "
              "silenced-checker on src/new.py while the vendored parser lands · t-1\n")
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 waived", r.stdout)

    def test_waiver_for_a_different_path_does_not_exempt(self):
        write(self.repo, "src/new.py", "value = 1  # noqa\n")
        write(self.repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver · taste · allow · "
              "silenced-checker on src/other.py · t-1\n")
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)

    def test_waiver_for_a_different_rule_does_not_exempt(self):
        write(self.repo, "src/new.py", "value = 1  # noqa\n")
        write(self.repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver · taste · allow · "
              "threshold-lowered on src/new.py · t-1\n")
        r = run_guard(self.repo, "--base", "main")
        self.assertEqual(r.returncode, 1)

    # ---- #313: a waiver is a parsed claim, not a substring search over prose ----

    def _waive(self, text):
        write(self.repo, "src/new.py", "value = 1  # noqa\n")
        write(self.repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver · taste · allow · " + text + " · t-1\n")
        return run_guard(self.repo, "--base", "main")

    def _decisions_line(self, line):
        """A DECISIONS line written verbatim — no floor-waiver framing added."""
        write(self.repo, "src/new.py", "value = 1  # noqa\n")
        write(self.repo, "docs/DECISIONS.md", line + "\n")
        return run_guard(self.repo, "--base", "main")

    def test_a_bare_directory_does_not_sweep_the_tree(self):
        # #313 claimed a bare `src/` waived everything under it. It did not, and could not: the
        # test was `finding["path"] in line`, so the LINE had to contain the whole path, not the
        # other way round. Kept as a regression guard for the semantics the issue asked for --
        # a directory is not a waiver -- not as evidence of the bug it described.
        r = self._waive("silenced-checker on src/ for now")
        self.assertEqual(r.returncode, 1,
                         f"a bare directory must not waive the files under it: {r.stdout}")

    def test_a_line_refusing_the_waiver_does_not_grant_it(self):
        # The real shape of the defect, and the sharpest case: EVERY line of DECISIONS was scanned
        # for two substrings, so an ordinary log entry recording that the team DECLINED to waive a
        # finding granted it. A waiver has to be a line that declares itself one.
        r = self._decisions_line(
            "2026-09-10T00:00:00Z · mechanical · taste · deny · "
            "we will NOT waive silenced-checker on src/new.py · t-1")
        self.assertEqual(r.returncode, 1,
                         f"a line refusing the waiver granted it: {r.stdout}")

    def test_an_unrelated_mention_does_not_grant_a_waiver(self):
        r = self._decisions_line(
            "2026-09-10T00:00:00Z · mechanical · taste · allow · "
            "see notes/silenced-checker.md before touching src/new.py · t-1")
        self.assertEqual(r.returncode, 1,
                         f"prose that merely mentions both is not a waiver: {r.stdout}")

    def test_an_explicit_glob_waives_the_subtree(self):
        # A sweep is allowed when it is SAID, because then a reviewer sees the blast radius.
        r = self._waive("silenced-checker on src/** while the vendored parser lands")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 waived", r.stdout)

    def test_a_glob_over_everything_is_not_a_waiver(self):
        r = self._waive("silenced-checker on ** everywhere")
        self.assertEqual(r.returncode, 1, f"`**` is a blanket, not a waiver: {r.stdout}")

    def test_a_longer_token_containing_the_rule_id_does_not_waive(self):
        # `finding["rule"] in line` made any superstring a match.
        r = self._waive("silenced-checkers are fine on src/new.py")
        self.assertEqual(r.returncode, 1, f"`silenced-checkers` is not the rule id: {r.stdout}")

    def test_a_longer_token_containing_the_path_does_not_waive(self):
        # Same defect on the other field: src/new.pyc contains src/new.py.
        r = self._waive("silenced-checker on src/new.pyc")
        self.assertEqual(r.returncode, 1, f"`src/new.pyc` is not `src/new.py`: {r.stdout}")

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
