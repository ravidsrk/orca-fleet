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
import runpy
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


def run_main(repo, *args):
    """floor_guard.main() in-process with captured output: (exit, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = floor_guard.main(["--repo", str(repo), *args])
    return code, out.getvalue(), err.getvalue()


class TestGuardSurfaceHit(unittest.TestCase):
    """The frozen surface (CONSTRAINTS.md "Guard surface"): what trips, what stays silent."""

    def test_every_whole_file_trips_on_any_line(self):
        for path in floor_guard.GUARD_SURFACE_FILES:
            with self.subTest(path=path):
                self.assertEqual(floor_guard.guard_surface_hit(path, "anything at all"), path)

    def test_trap_dir_members_trip_but_near_miss_dirs_do_not(self):
        self.assertEqual(
            floor_guard.guard_surface_hit("bench/vf-bench/traps/decoy-path.json", "{...}"),
            "bench/vf-bench/traps")
        for path in ("bench/vf-bench/traps-new/x.json", "bench/vf-bench/gate.py",
                     "bench/vf-bench/README.md"):
            with self.subTest(path=path):
                self.assertIsNone(floor_guard.guard_surface_hit(path, "some line"))

    def test_every_keyed_assignment_trips(self):
        cases = [
            ("ruff.toml", 'select = ["E9", "F63"]'),
            ("ruff.toml", '  select= ["E9"]'),
            (".coveragerc", "fail_under = 80"),
            ("tests/test_evals.py", "ROUTING_MIN_SCORE = 1.0"),
            ("bench/vf-bench/gate.py", 'EXPECTED_VERSION = "vf-bench@0.1"'),
            ("bench/vf-bench/gate.py", 'EXPECTED_CANARY_GUID = "05e6"'),
            ("bench/vf-bench/gate.py", 'EXPECTED_CORPUS_SHA256 = "a186"'),
        ]
        for path, line in cases:
            with self.subTest(path=path, line=line):
                self.assertEqual(floor_guard.guard_surface_hit(path, line), path)

    def test_use_sites_and_comments_about_a_key_stay_silent(self):
        cases = [
            ("tests/test_evals.py", '    result["score"], ROUTING_MIN_SCORE,'),
            ("tests/test_evals.py", "    # the ROUTING_MIN_SCORE floor mirrors CONSTRAINTS.md"),
            ("ruff.toml", "# the select key lists the enforced rule families"),
            (".coveragerc", "# fail_under mirrors the frozen D9 number"),
            ("bench/vf-bench/gate.py", "# bump EXPECTED_VERSION with the corpus"),
        ]
        for path, line in cases:
            with self.subTest(line=line):
                self.assertIsNone(floor_guard.guard_surface_hit(path, line))

    def test_surface_keys_in_other_files_stay_silent(self):
        cases = [
            ("docs/notes.md", "ROUTING_MIN_SCORE = 0.5"),
            ("ruff.toml.bak", 'select = ["E9"]'),
            ("sub/.gitleaksignore", "aabbcc"),
            ("evals/routing.jsonl", "{}"),
            ("tests/test_other.py", "ROUTING_MIN_SCORE = 0.5"),
        ]
        for path, line in cases:
            with self.subTest(path=path):
                self.assertIsNone(floor_guard.guard_surface_hit(path, line))

    def test_an_empty_path_is_not_a_hit(self):
        self.assertIsNone(floor_guard.guard_surface_hit("", "select = []"))
        self.assertIsNone(floor_guard.guard_surface_hit(None, "select = []"))


class TestGuardSurfaceEndToEnd(FloorGuardBase):
    def _surface_repo(self, path, content, name="surface"):
        repo = Path(self.tmp) / name
        repo.mkdir()
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.email", "t@example.invalid")
        git(repo, "config", "user.name", "t")
        write(repo, path, content)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "base")
        git(repo, "checkout", "-q", "-b", "work")
        return repo

    def _lowered_floor(self):
        repo = self._surface_repo("tests/test_evals.py", "ROUTING_MIN_SCORE = 1.0\n")
        write(repo, "tests/test_evals.py", "ROUTING_MIN_SCORE = 0.5\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "lower the floor")
        return repo

    def test_a_lowered_routing_floor_is_flagged(self):
        code, _out, err = run_main(self._lowered_floor(), "--base", "main")
        self.assertEqual(code, 1, err)
        self.assertIn("guard-surface", err)
        self.assertRegex(err, r"\[guard-surface\] tests/test_evals\.py:\d+")

    def test_a_use_site_edit_without_touching_the_floor_is_silent(self):
        repo = self._surface_repo("tests/test_evals.py",
                                  "ROUTING_MIN_SCORE = 1.0\n\n\ndef check(score):\n    return score\n")
        write(repo, "tests/test_evals.py",
              "ROUTING_MIN_SCORE = 1.0\n\n\ndef check(score):\n    return score >= ROUTING_MIN_SCORE\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "cite the floor without moving it")
        code, _out, err = run_main(repo, "--base", "main")
        self.assertEqual(code, 0, err)

    def test_each_whole_surface_file_trips(self):
        for path, line in ((".gitleaksignore", "aabbccddeeff00112233445566778899aabbccdd\n"),
                           ("evals/routing.json", '{"prompts": []}\n'),
                           ("bench/vf-bench/VERSION", "vf-bench@0.2\n"),
                           ("bench/vf-bench/CANARY", "canary GUID 00000000-0000-0000-0000-000000000000\n"),
                           ("bench/vf-bench/traps/zz-canary.json", '{"trap": true}\n')):
            with self.subTest(path=path):
                repo = Path(self.tmp) / ("repo-" + path.replace("/", "-"))
                repo.mkdir(parents=True)
                git(repo, "init", "-q", "-b", "main")
                git(repo, "config", "user.email", "t@example.invalid")
                git(repo, "config", "user.name", "t")
                write(repo, "README.md", "base\n")
                git(repo, "add", "-A")
                git(repo, "commit", "-qm", "base")
                git(repo, "checkout", "-q", "-b", "work")
                write(repo, path, line)
                git(repo, "add", "-A")
                git(repo, "commit", "-qm", "touch the surface")
                code, _out, err = run_main(repo, "--base", "main")
                self.assertEqual(code, 1, f"{path} did not trip")
                self.assertIn("guard-surface", err)

    def test_each_keyed_surface_file_trips(self):
        for path, line in (("ruff.toml", 'select = ["E9"]\n'),
                           (".coveragerc", "[report]\nfail_under = 70\n"),
                           ("bench/vf-bench/gate.py", 'EXPECTED_VERSION = "vf-bench@0.2"\n'),
                           ("bench/vf-bench/gate.py", 'EXPECTED_CANARY_GUID = "0000"\n'),
                           ("bench/vf-bench/gate.py", 'EXPECTED_CORPUS_SHA256 = "0000"\n')):
            with self.subTest(path=path, line=line.strip()):
                write(self.repo, path, line)
                self.commit("touch the surface")
                code, _out, err = run_main(self.repo, "--base", "main")
                self.assertEqual(code, 1, f"{path}: {line.strip()} did not trip")
                self.assertIn("guard-surface", err)

    def test_a_granting_waiver_exempts_a_surface_touch(self):
        repo = self._lowered_floor()
        write(repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver:guard-surface:tests/test_evals.py · taste · "
              "allow · the floor moves with the eval · t-1\n")
        code, out, err = run_main(repo, "--base", "main")
        self.assertEqual(code, 0, err)
        self.assertIn("waived", out)

    def test_a_content_preserving_rename_still_trips(self):
        # PR #468 review, P1: with rename detection on, `git mv` renders as
        # metadata with no content lines, and a content-line guard reads that
        # as silence — renaming .coveragerc sideways would unwire D9 untripped.
        for name, (path, content) in enumerate(((".coveragerc", "[report]\nfail_under = 80\n"),
                                                     ("tests/test_evals.py",
                                                      "ROUTING_MIN_SCORE = 1.0\n"))):
            with self.subTest(path=path):
                repo = self._surface_repo(path, content, name=f"surface-{name}")
                git(repo, "mv", path, path + ".moved")
                git(repo, "commit", "-qm", "rename the guarded file")
                code, _out, err = run_main(repo, "--base", "main")
                self.assertEqual(code, 1, f"renaming {path} went silent")
                self.assertIn("guard-surface", err)


class TestScanUnits(FloorGuardBase):
    # Marker fixtures are split across string literals: each half is inert to
    # the guard, and the joined runtime string trips exactly the rule under
    # test. A contiguous marker here would be a self-finding when the guard
    # CI job diff-scans the PR that carries these tests.
    NOQA = "value = 1  # " + "noqa"
    SKIP = "@pytest.mark.sk" + "ip"
    STUB = "# T" + "ODO: later"

    def _scan(self, added=(), removed=(), name="CONSTRAINTS.md", repo=None):
        return floor_guard.scan(list(added), list(removed), name, repo or Path(self.tmp))

    def test_added_markers_flag_their_rules(self):
        findings = self._scan(added=[("src/a.py", 1, self.NOQA),
                                     ("tests/t.py", 2, self.SKIP),
                                     ("src/b.py", 3, self.STUB)])
        self.assertEqual([f["rule"] for f in findings],
                         ["silenced-checker", "test-made-easier", "unfinished-work"])
        self.assertEqual(findings[0]["path"], "src/a.py")
        self.assertEqual(findings[0]["line"], 1)
        self.assertEqual(findings[0]["detail"], "noqa")

    def test_guard_surface_flags_on_added_and_removed_lines(self):
        added = self._scan(added=[(".gitleaksignore", 1, "aabbcc")])
        self.assertEqual([(f["rule"], f["detail"]) for f in added],
                         [("guard-surface", ".gitleaksignore")])
        removed = self._scan(removed=[("evals/routing.json", 9, '  {"p": 1},')])
        self.assertEqual([(f["rule"], f["detail"]) for f in removed],
                         [("guard-surface", "evals/routing.json")])

    def test_a_lowered_number_flags_with_the_before_and_after(self):
        findings = self._scan(added=[("CONSTRAINTS.md", 4, "| D1 | coverage | 60 |")],
                              removed=[("CONSTRAINTS.md", 4, "| D1 | coverage | 85 |")])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["rule"], "threshold-lowered")
        self.assertEqual(findings[0]["detail"], "85 -> 60")

    def test_only_the_lowered_number_in_a_pair_flags(self):
        findings = self._scan(added=[("CONSTRAINTS.md", 4, "| D | a 10 b 15 |")],
                              removed=[("CONSTRAINTS.md", 4, "| D | a 10 b 20 |")])
        self.assertEqual([(f["rule"], f["detail"]) for f in findings],
                         [("threshold-lowered", "20 -> 15")])

    def test_a_raised_an_unmatched_and_a_keyless_row_stay_silent(self):
        raised = self._scan(added=[("CONSTRAINTS.md", 4, "| D1 | coverage | 95 |")],
                            removed=[("CONSTRAINTS.md", 4, "| D1 | coverage | 85 |")])
        self.assertEqual(raised, [])
        unmatched = self._scan(added=[("CONSTRAINTS.md", 9, "| D9 | other | 1 |")],
                               removed=[("CONSTRAINTS.md", 4, "| D1 | coverage | 85 |")])
        self.assertEqual(unmatched, [])
        keyless = self._scan(added=[("CONSTRAINTS.md", 4, "|||")],
                             removed=[("CONSTRAINTS.md", 4, "|||")])
        self.assertEqual(keyless, [])

    def test_a_number_with_no_before_value_stays_silent(self):
        findings = self._scan(added=[("CONSTRAINTS.md", 4, "| D | a 10 b 5 |")],
                              removed=[("CONSTRAINTS.md", 4, "| D | a 10 |")])
        self.assertEqual(findings, [])

    def test_an_exception_row_flags(self):
        findings = self._scan(added=[("CONSTRAINTS.md", 9, "| W101 | legacy | Q3 |")])
        self.assertEqual([f["rule"] for f in findings], ["new-exception"])

    def test_a_bullet_under_an_in_diff_exceptions_heading_flags(self):
        findings = self._scan(added=[("CONSTRAINTS.md", 8, "## Exceptions"),
                                     ("CONSTRAINTS.md", 9, "- legacy stays unlinted")])
        self.assertEqual([f["rule"] for f in findings], ["new-exception"])

    def test_a_bullet_under_an_on_disk_exceptions_heading_flags(self):
        # The hermetic repo's CONSTRAINTS.md carries ## Exceptions on disk (no
        # heading line in the diff), which is the half the in-diff marker alone missed.
        findings = self._scan(added=[("CONSTRAINTS.md", 9, "- legacy stays unlinted")],
                              repo=self.repo)
        self.assertEqual([f["rule"] for f in findings], ["new-exception"])

    def test_a_bullet_with_no_exceptions_heading_stays_silent(self):
        bare = Path(self.tmp) / "bare"
        bare.mkdir()
        findings = self._scan(added=[("CONSTRAINTS.md", 9, "- a plain bullet")], repo=bare)
        self.assertEqual(findings, [])

    def test_an_unreadable_constraints_file_reads_as_no_heading(self):
        blocked = Path(self.tmp) / "blocked"
        blocked.mkdir()
        (blocked / "CONSTRAINTS.md").mkdir()
        findings = self._scan(added=[("CONSTRAINTS.md", 9, "- a plain bullet")], repo=blocked)
        self.assertEqual(findings, [])

    def test_a_plain_line_is_not_an_exception_bullet(self):
        findings = self._scan(added=[("CONSTRAINTS.md", 9, "a plain line")], repo=self.repo)
        self.assertEqual(findings, [])

    def test_a_removed_assertion_in_a_surviving_test_flags(self):
        findings = self._scan(removed=[("tests/test_thing.py", 5, "    assert other() == 5")],
                              repo=self.repo)
        self.assertEqual([f["rule"] for f in findings], ["assertion-removed"])

    def test_a_removed_assertion_in_a_deleted_file_stays_silent(self):
        findings = self._scan(removed=[("tests/gone.py", 1, "    assert gone()")],
                              repo=self.repo)
        self.assertEqual(findings, [])

    def test_a_removed_assertion_outside_test_paths_stays_silent(self):
        findings = self._scan(removed=[("src/app.py", 2, "    assert True")], repo=self.repo)
        self.assertEqual(findings, [])

    def test_a_removed_non_assertion_line_stays_silent(self):
        findings = self._scan(removed=[("tests/test_thing.py", 1, "def test_thing():")],
                              repo=self.repo)
        self.assertEqual(findings, [])

    def test_a_head_deleted_test_file_still_counts_as_surviving(self):
        (self.repo / "tests" / "test_thing.py").unlink()
        findings = self._scan(removed=[("tests/test_thing.py", 5, "    assert other() == 5")],
                              repo=self.repo)
        self.assertEqual([f["rule"] for f in findings], ["assertion-removed"])

    def test_an_uncommitted_test_file_counts_as_surviving(self):
        write(self.repo, "tests/test_fresh.py", "def test_fresh():\n    assert fresh()\n")
        findings = self._scan(removed=[("tests/test_fresh.py", 2, "    assert fresh()")],
                              repo=self.repo)
        self.assertEqual([f["rule"] for f in findings], ["assertion-removed"])


class TestDiffParsingUnits(unittest.TestCase):
    def test_hunk_accounting_pins_added_removed_and_context_lines(self):
        diff = ("--- a/src/app.py\n"
                "+++ b/src/app.py\n"
                "@@ -1,2 +1,3 @@\n"
                " ctx\n"
                "-old\n"
                "+new\n"
                "+more\n")
        added, removed = floor_guard.parse_diff(diff)
        self.assertEqual(added, [("src/app.py", 2, "new"), ("src/app.py", 3, "more")])
        self.assertEqual(removed, [("src/app.py", 2, "old")])

    def test_new_and_deleted_files_resolve_through_dev_null(self):
        added, removed = floor_guard.parse_diff(
            "--- /dev/null\n+++ b/new.py\n@@ -0,0 +1 @@\n+line\n")
        self.assertEqual(added, [("new.py", 1, "line")])
        self.assertEqual(removed, [])
        added, removed = floor_guard.parse_diff(
            "--- a/gone.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-gone\n")
        self.assertEqual(added, [])
        self.assertEqual(removed, [("gone.py", 1, "gone")])

    def test_strip_prefix_handles_prefixes_dev_null_and_bare_paths(self):
        self.assertEqual(floor_guard.strip_prefix("a/src/x.py"), "src/x.py")
        self.assertEqual(floor_guard.strip_prefix("b/src/x.py"), "src/x.py")
        self.assertEqual(floor_guard.strip_prefix("/dev/null"), "")
        self.assertEqual(floor_guard.strip_prefix("plain.py"), "plain.py")

    def test_row_key_is_the_first_nonempty_cell(self):
        self.assertEqual(floor_guard.row_key("| D1 | coverage | 85 |"), "d1")
        self.assertEqual(floor_guard.row_key("- floor: 3"), "floor")
        self.assertEqual(floor_guard.row_key("|||"), "")

    def test_numbers_reads_ints_and_decimals(self):
        self.assertEqual(floor_guard.numbers("v1.2 and 3"), [1.2, 3.0])
        self.assertEqual(floor_guard.numbers("no digits"), [])

    def test_is_constraints_matches_by_filename(self):
        self.assertTrue(floor_guard.is_constraints("CONSTRAINTS.md", "CONSTRAINTS.md"))
        self.assertTrue(floor_guard.is_constraints("docs/CONSTRAINTS.md", "CONSTRAINTS.md"))
        self.assertFalse(floor_guard.is_constraints("OTHER.md", "CONSTRAINTS.md"))
        self.assertFalse(floor_guard.is_constraints("", "CONSTRAINTS.md"))


class TestWaiverUnits(unittest.TestCase):
    def _row(self, ident, answer="allow", ts="2026-09-10T00:00:00Z"):
        return f"{ts} · {ident} · taste · {answer} · why · t-1"

    def _finding(self, rule="silenced-checker", path="src/new.py"):
        return {"rule": rule, "path": path, "line": 1, "detail": "noqa"}

    def test_a_granting_waiver_waives_through_the_sibling_loader(self):
        self.assertTrue(floor_guard.is_waived(
            self._finding(), [self._row("floor-waiver:silenced-checker:src/new.py")]))

    def test_a_preloaded_decisions_module_is_used_as_is(self):
        loaded = floor_guard._load_decisions()
        self.assertTrue(floor_guard.is_waived(
            self._finding(), [self._row("floor-waiver:silenced-checker:src/new.py")],
            decisions=loaded))

    def test_a_denied_a_superseded_and_a_wrong_rule_do_not_waive(self):
        ident = "floor-waiver:silenced-checker:src/new.py"
        self.assertFalse(floor_guard.is_waived(
            self._finding(), [self._row(ident, answer="deny")]))
        self.assertFalse(floor_guard.is_waived(
            self._finding(), [self._row(ident, ts="2026-09-01T00:00:00Z"),
                              self._row(ident, answer="superseded", ts="2026-09-02T00:00:00Z")]))
        self.assertFalse(floor_guard.is_waived(
            self._finding(), [self._row("floor-waiver:threshold-lowered:src/new.py")]))

    def test_prose_and_unscoped_ids_do_not_waive(self):
        self.assertFalse(floor_guard.is_waived(self._finding(), ["just a note"]))
        self.assertFalse(floor_guard.is_waived(
            self._finding(), [self._row("floor-waiver")]))

    def test_a_finding_without_a_path_is_never_waived(self):
        self.assertFalse(floor_guard.is_waived(
            {"rule": "silenced-checker"}, [self._row("floor-waiver:silenced-checker:src/new.py")]))

    def test_an_unloadable_sibling_waives_nothing(self):
        with mock.patch.object(floor_guard, "_load_decisions", side_effect=Exception("boom")):
            self.assertFalse(floor_guard.is_waived(
                self._finding(), [self._row("floor-waiver:silenced-checker:src/new.py")]))

    def test_path_scope_is_segment_wise_never_substring(self):
        hit = floor_guard._path_waived_by
        self.assertTrue(hit("src/new.py", "src/new.py"))
        self.assertTrue(hit("src/**", "src/new.py"))
        self.assertTrue(hit("src/**", "src/a/b.py"))
        self.assertFalse(hit("src", "src/new.py"))
        self.assertFalse(hit("src/", "src/new.py"))
        self.assertFalse(hit("**", "src/new.py"))
        self.assertFalse(hit("/**", "src/new.py"))
        self.assertFalse(hit("src/new.pyc", "src/new.py"))
        self.assertFalse(hit("src/new.py", "src/new.pyx"))
        self.assertFalse(hit("src/**", "srcinternal/x.py"))

    def test_missing_waiver_file_is_no_waivers(self):
        self.assertEqual(floor_guard.load_waivers("/nonexistent/DECISIONS.md"), [])

    def test_an_unreadable_waiver_file_is_a_could_not_run(self):
        with tempfile.TemporaryDirectory(prefix="waivers-") as tmp:
            with self.assertRaises(floor_guard.GuardError):
                floor_guard.load_waivers(tmp)

    def test_malformed_waivers_are_named_with_the_shape_to_write(self):
        notes = floor_guard.malformed_waivers([self._row("floor-waiver")])
        self.assertEqual(len(notes), 1)
        self.assertIn("scope is not in the id", notes[0][1])
        notes = floor_guard.malformed_waivers([self._row("floor-waiver:silenced-checker")])
        self.assertEqual(len(notes), 1)
        self.assertIn("floor-waiver:<rule>:<path-or-glob>", notes[0][1])
        good = floor_guard.malformed_waivers(
            [self._row("floor-waiver:silenced-checker:src/new.py"), "prose"])
        self.assertEqual(good, [])

    def test_malformed_waivers_survive_an_unloadable_sibling(self):
        with mock.patch.object(floor_guard, "_load_decisions", side_effect=Exception("boom")):
            self.assertEqual(floor_guard.malformed_waivers([self._row("floor-waiver")]), [])


class TestMainInProc(FloorGuardBase):
    def test_clean_reports_the_banner_in_process(self):
        code, out, err = run_main(self.repo, "--base", "main")
        self.assertEqual(code, 0, err)
        self.assertIn("floor-guard: clean", out)

    def test_quiet_suppresses_the_clean_banner(self):
        code, out, err = run_main(self.repo, "--base", "main", "--quiet")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "")

    def test_an_omitted_base_falls_back_to_the_local_main(self):
        code, _out, err = run_main(self.repo)
        self.assertEqual(code, 0, err)
        write(self.repo, "CONSTRAINTS.md",
              BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 60 |"))
        self.commit("lower")
        code, _out, err = run_main(self.repo)
        self.assertEqual(code, 1, "the default base did not evaluate main..work")
        self.assertIn("threshold-lowered", err)

    def test_a_violation_names_the_rule_and_the_waiver_shape(self):
        write(self.repo, "CONSTRAINTS.md",
              BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 60 |"))
        self.commit("lower")
        code, _out, err = run_main(self.repo, "--base", "main")
        self.assertEqual(code, 1)
        self.assertIn("[threshold-lowered]", err)
        self.assertIn("floor-waiver:<rule>:<path>", err)

    def test_a_granting_waiver_reports_the_count_in_process(self):
        write(self.repo, "CONSTRAINTS.md",
              BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 60 |"))
        self.commit("lower")
        write(self.repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver:threshold-lowered:CONSTRAINTS.md · taste · "
              "allow · the bar moves deliberately · t-1\n")
        code, out, err = run_main(self.repo, "--base", "main")
        self.assertEqual(code, 0, err)
        self.assertIn("(1 waived)", out)

    def test_an_unresolvable_base_is_exit_2_in_process(self):
        code, _out, err = run_main(self.repo, "--base", "origin/does-not-exist")
        self.assertEqual(code, 2)
        self.assertIn("not resolvable", err)

    def test_a_non_repo_is_exit_2_in_process(self):
        plain = Path(self.tmp) / "plain"
        plain.mkdir()
        code, _out, err = run_main(plain, "--base", "main")
        self.assertEqual(code, 2)
        self.assertIn("not inside a git work tree", err)

    def test_no_resolvable_default_base_is_exit_2(self):
        repo = Path(self.tmp) / "trunk"
        repo.mkdir()
        git(repo, "init", "-q", "-b", "trunk")
        git(repo, "config", "user.email", "t@example.invalid")
        git(repo, "config", "user.name", "t")
        write(repo, "file.txt", "content\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "base")
        code, _out, err = run_main(repo)
        self.assertEqual(code, 2)
        self.assertIn("no base ref could be resolved", err)

    def test_origin_head_wins_over_the_local_branch(self):
        # The distinguishing setup: the remote tip (T1, clean) and the local
        # tip (T2, violation) have different TREES, and work sits at T2. A base
        # of origin/main diffs T1..T2 and sees the violation; a base of the
        # local main diffs T2..T2 and reads clean.
        origin = Path(self.tmp) / "origin.git"
        git(Path(self.tmp), "init", "-q", "--bare", "origin.git")
        seed = Path(self.tmp) / "seed"
        git(Path(self.tmp), "clone", "-q", str(origin), "seed")
        git(seed, "config", "user.email", "t@example.invalid")
        git(seed, "config", "user.name", "t")
        write(seed, "CONSTRAINTS.md", BASE_CONSTRAINTS)
        git(seed, "add", "-A")
        git(seed, "commit", "-qm", "base")
        git(seed, "push", "-q", "origin", "main")
        repo = Path(self.tmp) / "clone"
        git(Path(self.tmp), "clone", "-q", str(origin), "clone")
        git(repo, "config", "user.email", "t@example.invalid")
        git(repo, "config", "user.name", "t")
        head = git(repo, "symbolic-ref", "refs/remotes/origin/HEAD")
        self.assertEqual(head.stdout.strip(), "refs/remotes/origin/main",
                         "the clone has no origin/HEAD to prefer — the setup is wrong, not the code")
        write(repo, "CONSTRAINTS.md",
              BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 60 |"))
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "violation, unpushed")
        git(repo, "checkout", "-q", "-b", "work")
        code, _out, err = run_main(repo)
        self.assertEqual(code, 1, f"the guard read the local tip, not origin/HEAD: {err}")
        self.assertIn("threshold-lowered", err)

    def test_branches_without_a_merge_base_are_exit_2(self):
        git(self.repo, "checkout", "-q", "--orphan", "ghost")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "ghost")
        code, _out, err = run_main(self.repo, "--base", "main")
        self.assertEqual(code, 2)
        self.assertIn("no merge base", err)

    def test_git_failing_to_launch_is_exit_2(self):
        with mock.patch.object(floor_guard.subprocess, "run", side_effect=OSError("no git")):
            code, _out, err = run_main(self.repo, "--base", "main")
        self.assertEqual(code, 2)
        self.assertIn("could not run", err)

    def test_an_old_shape_waiver_is_named_in_process(self):
        write(self.repo, "CONSTRAINTS.md",
              BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 60 |"))
        self.commit("lower")
        write(self.repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver · taste · allow · the old shape · t-1\n")
        code, _out, err = run_main(self.repo, "--base", "main")
        self.assertEqual(code, 1)
        self.assertIn("NOT a usable waiver", err)
        self.assertIn("floor-waiver:<rule>:<path>", err)

    def test_an_unloadable_sibling_grants_no_waiver_and_names_none(self):
        write(self.repo, "CONSTRAINTS.md",
              BASE_CONSTRAINTS.replace("| D1 | coverage | 85 |", "| D1 | coverage | 60 |"))
        self.commit("lower")
        write(self.repo, "docs/DECISIONS.md",
              "2026-09-10T00:00:00Z · floor-waiver · taste · allow · the old shape · t-1\n")
        with mock.patch.object(floor_guard, "_load_decisions", side_effect=Exception("boom")):
            code, _out, err = run_main(self.repo, "--base", "main")
        self.assertEqual(code, 1)
        self.assertIn("[threshold-lowered]", err)
        self.assertNotIn("NOT a usable waiver", err)

    def test_the_module_entry_point_runs_clean_and_exits_zero(self):
        argv = ["floor_guard.py", "--repo", str(self.repo), "--base", "main"]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch.object(sys, "argv", argv):
                with self.assertRaises(SystemExit) as ctx:
                    runpy.run_path(str(GUARD), run_name="__main__")
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("floor-guard: clean", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
