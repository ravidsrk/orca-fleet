#!/usr/bin/env python3
"""Repo-hygiene contracts (#300).

Three unrelated findings from the supply-chain pass, each a file rather than code, and each
easy to undo silently in a later edit. The assertions are about the FILES, so they hold whoever
changes them next.
"""
import ast
import re
import sys
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class RuntimeStateIsNotCommittable(unittest.TestCase):
    """`.orca/` is the Orca runtime's working directory, not repository content.

    egress.py defaults its ledger to `.orca/egress.jsonl` at mode 0600 and the dispatch key
    lives there too, so an unignored `.orca/` lets a worker commit runtime state — a private
    key among it — by accident.
    """

    def _ignored(self, rel):
        r = subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT)
        return r.returncode == 0

    def test_the_runtime_working_directory_is_ignored(self):
        for rel in (".orca/", ".orca/egress.jsonl", ".orca/keys/dispatch.key",
                    ".orca/anything/nested/deep.json"):
            with self.subTest(path=rel):
                self.assertTrue(self._ignored(rel), f"{rel} would be committable")

    def test_the_ignore_matches_the_path_the_code_actually_uses(self):
        # The rule is only worth anything if it covers the default the runtime writes to.
        egress = (ROOT / "runtime" / "scripts" / "egress.py").read_text(encoding="utf-8")
        m = re.search(r'^DEFAULT_LEDGER = "([^"]+)"', egress, re.M)
        self.assertIsNotNone(m, "egress.py no longer declares DEFAULT_LEDGER")
        self.assertTrue(self._ignored(m.group(1)),
                        f"egress.py writes {m.group(1)} and .gitignore does not cover it")

    def test_the_public_key_is_still_committable(self):
        """The one thing in `.orca/` that MUST be commitable — and the first cut broke it.

        Committing `.orca/dispatch-pubkey` is what turns dispatch-signature enforcement on
        (dispatch-sign.py:127). A blanket `.orca/` swept it up, and test_dispatch_sign.py said
        so; this is the same contract stated from the ignore rule's side, because the two are
        easy to change independently.
        """
        self.assertFalse(self._ignored(".orca/dispatch-pubkey"),
                         "the pubkey is ignored — signature enforcement can no longer be "
                         "turned on by committing it")

    def test_the_rule_excludes_contents_so_the_exception_can_work(self):
        # `.orca/` would read more naturally and would NOT work: git never descends into an
        # excluded directory, so a `!` negation under one is dead. `.orca/*` is what makes the
        # pubkey exception above possible. Same idiom as `.secrets/*` + `!.secrets/*.pub`.
        rules = [ln.strip() for ln in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
                 if ln.strip().startswith((".orca", "!.orca"))]
        self.assertEqual(rules, [".orca/*", "!.orca/dispatch-pubkey"],
                         "the runtime-state rule changed shape — a bare `.orca/` would make "
                         "the pubkey exception silently inert")

    def test_ordinary_repository_paths_are_still_tracked(self):
        for rel in ("runtime/scripts/egress.py", "skills/prove-it/SKILL.md", "README.md"):
            with self.subTest(path=rel):
                self.assertFalse(self._ignored(rel), f"{rel} was swept up by an ignore rule")


class EveryScriptCompilesWithoutWarnings(unittest.TestCase):
    """A SyntaxWarning is a future SyntaxError, and CI was printing two of them.

    `run_report.py` had `\\S` inside plain docstrings, which Python flags as an invalid escape
    sequence. Local runs never showed it — a cached .pyc does not recompile — so it only appeared
    in the CI log, where every file is compiled fresh. Python has announced these become errors.
    """

    def _compile_warnings(self, files):
        import py_compile
        import tempfile
        import warnings
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "c.pyc")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                for f in files:
                    py_compile.compile(str(f), cfile=out, doraise=False)
                return [f"{Path(f).name}: {w.category.__name__}: {w.message}" for w in caught]

    def test_the_compile_check_can_actually_see_a_warning(self):
        """Without this the check is a tautology on a clean tree.

        A mutant replacing `assertEqual(found, [])` with `assertEqual([], [])` survived, because
        both are true when nothing warns — the same vacuity the stdlib-import guard above had.
        """
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad_escape.py"
            bad.write_text('"""a docstring with \\S in it"""\n', encoding="utf-8")
            self.assertTrue(self._compile_warnings([bad]),
                            "the compile scan cannot see an invalid escape sequence")
            good = Path(tmp) / "good_escape.py"
            good.write_text('r"""a raw docstring with \\S in it"""\n', encoding="utf-8")
            self.assertEqual(self._compile_warnings([good]), [],
                             "the compile scan flags a raw string that is perfectly legal")

    def test_no_source_file_compiles_with_a_warning(self):
        roots = ("scripts", "runtime/scripts", "tests", "bench", "demo")
        files = [f for r in roots for f in sorted((ROOT / r).rglob("*.py"))
                 if "__pycache__" not in f.parts]
        self.assertGreater(len(files), 40, "the scan found almost no sources to compile")
        self.assertEqual(self._compile_warnings(files), [],
                         "these are future SyntaxErrors, and CI prints them today")


class TheSecretWaiverCarriesIdentityNotContent(unittest.TestCase):
    """A waiver needs the finding's fingerprint, not the finding.

    The `--baseline-path` baseline this replaced embedded each finding's commit message, author
    name and e-mail address. Measured before switching: gitleaks 8.30.1 compares Email, Author,
    Date, Message, Entropy, Description and Commit when matching a baseline entry, so deleting
    those fields stops a baseline suppressing anything at all. `.gitleaksignore` matches on the
    fingerprint alone, which is why the switch is the fix rather than a trim.
    """

    IGNORE = ROOT / ".gitleaksignore"
    # <40-hex commit>:<path>:<rule-id>:<line>
    FINGERPRINT = re.compile(r"^[0-9a-f]{40}:[^:]+:[A-Za-z0-9._-]+:\d+$")

    def _lines(self):
        text = self.IGNORE.read_text(encoding="utf-8")
        return [ln.strip() for ln in text.splitlines()
                if ln.strip() and not ln.lstrip().startswith("#")]

    def test_the_baseline_that_carried_content_is_gone(self):
        self.assertFalse((ROOT / ".gitleaks-baseline.json").exists(),
                         "the content-carrying baseline is back")

    # The exact set. Widening is the dangerous direction — one more line here silences a real
    # finding with nothing to show for it — and narrowing turns CI red rather than silent, so
    # pinning both ends is what makes this file reviewable at a glance.
    WAIVED = {
        "03e481a106bea9dbe124fd5b5181d5769e28061f:tests/test_decisions.py:generic-api-key:111",
        "03e481a106bea9dbe124fd5b5181d5769e28061f:tests/test_decisions.py:aws-access-token:102",
        "03e481a106bea9dbe124fd5b5181d5769e28061f:tests/test_decisions.py:aws-access-token:115",
    }

    def test_every_waived_entry_is_a_bare_fingerprint(self):
        entries = self._lines()
        self.assertTrue(entries, ".gitleaksignore waives nothing — is the scan still gated?")
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertRegex(entry, self.FINGERPRINT)

    def test_the_waived_set_is_exactly_the_known_fixtures(self):
        self.assertEqual(set(self._lines()), self.WAIVED,
                         "the secret-scan waiver changed — every entry here is a finding "
                         "nobody will see again, so an addition needs its own justification")

    def test_nothing_outside_the_fixture_file_is_waived(self):
        for entry in self._lines():
            with self.subTest(entry=entry):
                self.assertEqual(entry.split(":")[1], "tests/test_decisions.py",
                                 "only the credential-shaped fixtures are waived")

    def test_the_waiver_carries_no_address_and_no_commit_message(self):
        text = self.IGNORE.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                            "an e-mail address is back in the secret waiver")
        for field in ('"Message"', '"Author"', '"Email"', '"Secret"', '"Match"'):
            self.assertNotIn(field, text, f"{field} is finding CONTENT, not its identity")

    def test_the_scan_reads_this_file_and_no_baseline(self):
        # A MENTION is fine — the step explains at length why the baseline went away. What must
        # not survive is an INVOCATION, which would point gitleaks at a file the repo no longer
        # has. (This test caught exactly that distinction on its own comment first.)
        wf = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        invoked = [ln.strip() for ln in wf.splitlines()
                   if "--baseline-path" in ln and not ln.lstrip().startswith("#")]
        self.assertEqual(invoked, [],
                         "the workflow still PASSES a baseline the repo no longer has")
        self.assertIn("gitleaksignore", wf,
                      "nothing in the workflow explains where the waiver lives")

    def test_the_planted_credential_control_still_runs(self):
        """The waiver is only as good as the proof that it waives nothing else.

        Checking for the WORD `canary` was not enough — it survives in the prose after the
        block that plants the key is gone. The control is three things that have to be there
        together: a throwaway clone, a key written into the waived file, and a scan of that
        clone whose SUCCESS fails the build.
        """
        wf = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        body = [ln for ln in wf.splitlines() if not ln.lstrip().startswith("#")]
        run = "\n".join(body)
        self.assertRegex(run, r'git clone --quiet \. "\$canary"',
                         "nothing clones a throwaway repo to plant the key in")
        self.assertRegex(run, r'printf .*AKIA.*>> "\$canary/tests/test_decisions\.py"',
                         "nothing plants a real-shaped key in the waived file")
        self.assertRegex(run, r'(?s)if \(cd "\$canary".{0,200}?detect.{0,400}?exit 1',
                         "a passing scan of the planted key no longer fails the build")


class TheSuiteRunsOnTheStdlibAlone(unittest.TestCase):
    """CI installs no test dependencies, so a third-party import is a red build, not a skip.

    Learned the expensive way: a `yaml.safe_load` in this very file passed locally, where pyyaml
    happens to be installed, and failed on the runner. The repo already believed this —
    test_floor_guard.py uses `import yaml` as its example of a third-party import — but nothing
    enforced it, so the belief was worth exactly one commit.
    """

    # Modules that live in this directory and are imported by path, not by name.
    LOCAL = {"test_pins", "test_evals", "conftest"}

    def _offenders(self, source, name="sample.py"):
        """Every module imported by this source, via `ast` — not a line regex.

        The first cut skipped any line containing a quote (to let test_floor_guard.py's quoted
        examples through) and read only the FIRST name of an import. `import os, yaml` and
        `import yaml  # "parser"` both sailed past it, and so did `from os import ...` on a
        commented line (PR #308 review, P2). A guard with holes is the defect it exists to catch.

        `ast` has neither problem and needs no heuristic: a quoted example parses to a string
        constant, never an Import node, and every alias in a multi-name import is visited.
        """
        stdlib = set(sys.stdlib_module_names)
        found = []
        for node in ast.walk(ast.parse(source, filename=name)):
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                # level > 0 is a relative import — no distributable package behind it.
                mods = [] if node.level else [node.module or ""]
            else:
                continue
            for mod in mods:
                top = mod.split(".")[0]
                if not top or top in stdlib or top in self.LOCAL or top == Path(name).stem:
                    continue
                found.append(f"{name}:{node.lineno}: {top}")
        return found

    def test_the_check_sees_imports_a_line_regex_missed(self):
        """PR #308 review, P2 — the holes in the first cut, each reproduced before fixing.

        All three passed the regex version and would have failed in dependency-free CI.
        """
        for source in ("import os, yaml\n",
                       'import yaml  # "parser"\n',
                       "import json\nimport requests, os\n",
                       "from yaml import safe_load\n",
                       "def f():\n    import yaml\n"):
            with self.subTest(source=source.strip()):
                self.assertTrue(self._offenders(source),
                                "a third-party import slipped past the guard")
        # And a quoted example is still not an import — test_floor_guard.py carries several.
        self.assertEqual(self._offenders('BAD = ["import yaml", "import requests"]\n'), [])
        for relative in ("from . import helpers\n", "from .helpers import thing\n",
                         "from ..pkg.mod import thing\n"):
            with self.subTest(source=relative.strip()):
                self.assertEqual(self._offenders(relative), [],
                                 "a relative import names no distributable package")

    def test_the_check_can_actually_see_a_third_party_import(self):
        """A clean tree makes `assertEqual(offenders, [])` pass whether or not the check works.

        Two negative-control mutants proved that: scanning no files at all, and allowlisting
        everything, both left the suite green. So the detector gets a sample it MUST flag —
        otherwise this is a check that only ever agrees with itself.
        """
        bad = self._offenders("import os\nimport yaml\nfrom requests import get\n")
        self.assertEqual(len(bad), 2, f"the third-party scan missed something: {bad}")
        self.assertTrue(any("yaml" in o for o in bad))
        self.assertTrue(any("requests" in o for o in bad))
        self.assertEqual(self._offenders("import os\nimport json\nfrom pathlib import Path\n"),
                         [], "the scan flagged the standard library")

    def test_no_test_imports_a_package_ci_does_not_install(self):
        offenders = []
        paths = sorted(Path(__file__).resolve().parent.glob("test_*.py"))
        self.assertGreater(len(paths), 20, "the scan found almost no test files to read")
        for path in paths:
            offenders += self._offenders(path.read_text(encoding="utf-8"), path.name)
        self.assertEqual(offenders, [],
                         "CI installs no test dependencies — these imports are a red build on "
                         "the runner and a pass on any machine that happens to have them")


class TheAlertWorkflowCannotBeTrippedByAFork(unittest.TestCase):
    """`branches: [main]` filters the workflow_run's HEAD branch, and a fork's PR branch can be
    named `main` too. No token reaches the fork, so the exposure is issue spam rather than
    credentials — but both halves of the guard are needed and neither is obvious."""

    WF = ROOT / ".github" / "workflows" / "alert-on-failure.yml"

    def _condition(self):
        """The job's `if:` folded scalar, read with the stdlib.

        This used `yaml.safe_load` and CI went red: pyyaml is not on the runner, and the whole
        suite is stdlib-only by design — test_floor_guard.py treats a bare `import yaml` as the
        third-party marker it is. Same folded-scalar shape test_pins.py already reads by hand.
        """
        out, active, indent = [], False, 0
        for line in self.WF.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not active and stripped.startswith("if:"):
                active, indent = True, len(line) - len(line.lstrip())
                rest = stripped[len("if:"):].strip()
                if rest not in (">-", ">", "|", "|-"):
                    out.append(rest)
                continue
            if active:
                if not stripped or stripped.startswith("#"):
                    continue
                if len(line) - len(line.lstrip()) <= indent:
                    break
                out.append(stripped)
        self.assertTrue(out, "the alert job has no `if:` condition at all")
        return " ".join(" ".join(out).split())

    def test_the_run_must_have_come_from_a_push(self):
        self.assertIn("github.event.workflow_run.event == 'push'", self._condition(),
                      "a PR-triggered validate run can still file an issue")

    def test_the_run_must_have_come_from_this_repository(self):
        self.assertIn(
            "github.event.workflow_run.head_repository.full_name == github.repository",
            self._condition(),
            "a fork pushing to its own `main` can still file an issue here")

    def test_the_failure_condition_and_the_drill_both_survive(self):
        cond = self._condition()
        self.assertIn("github.event.workflow_run.conclusion == 'failure'", cond,
                      "the workflow would now alert on a SUCCESSFUL run")
        self.assertIn("github.event_name == 'workflow_dispatch'", cond,
                      "the manual drill path is gone, so the alert can no longer be proven")


if __name__ == "__main__":
    unittest.main()
