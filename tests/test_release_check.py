#!/usr/bin/env python3
"""Contract tests for scripts/release_check.py — the 1.0 checklist as a runnable gate (#414).

docs/release-1.0-checklist.md defines the release as commands; the script runs
them. These tests keep the two from drifting apart and the script from lying:

* the script runs against THIS repository once (validate, proof_status,
  run_report, the vf-bench gate and the negative-control demo all execute for
  real, ~12 s) — every check the machine can make must PASS, and the only
  SKIPs are the two the flags ask for;
* each gate that reads repository state runs against a fixture tree that
  violates it, so every check is demonstrably able to FAIL (and to PASS);
* the gh-backed checks SKIP(no gh) with no gh on PATH and never PASS;
* the checklist opens with the run command and shows the commands the script
  runs — the stale grep over the rendered gate-batch.md, the #235 gate and the
  pre-re-scope harden-it bar are gone.
"""
import contextlib
import importlib.util
import io
import json
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
SCRIPT = ROOT / "scripts" / "release_check.py"
CHECKLIST = ROOT / "docs" / "release-1.0-checklist.md"

_spec = importlib.util.spec_from_file_location("release_check", SCRIPT)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

_gb_spec = importlib.util.spec_from_file_location(
    "gate_batch_for_release_check", ROOT / "runtime" / "scripts" / "gate-batch.py")
gb = importlib.util.module_from_spec(_gb_spec)
_gb_spec.loader.exec_module(gb)

STATUS_LINE = re.compile(r"^\s*(PASS|FAIL|INFO)  (\S+): ")
SKIP_LINE = re.compile(r"^\s*SKIP\((.*)\)  (\S+)$")
SUMMARY_LINE = re.compile(
    r"^summary: (\d+) PASS, (\d+) FAIL, (\d+) SKIP, (\d+) INFO -> exit (\d)$", re.M)
ALL_GATES = ("gate0", "gate1", "gate2", "gate3", "gate4", "gate5", "gate6")


def parse(stdout):
    """[(status, skip_reason_or_None, check_name)] from the script's text output."""
    rows = []
    for line in stdout.splitlines():
        m = STATUS_LINE.match(line)
        if m:
            rows.append((m.group(1), None, m.group(2)))
            continue
        m = SKIP_LINE.match(line)
        if m:
            rows.append(("SKIP", m.group(1), m.group(2)))
    return rows


class Completed:
    """What subprocess.run returns, for a main() that ran in this process."""

    def __init__(self, returncode, stdout, stderr):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def run_script(*args, cwd=ROOT, env=None, timeout=900):
    """rc.main() in this process, under the cwd and environment a subprocess would have.

    In-process so the D9 coverage floor sees the script (a subprocess is invisible to the
    shard's tracer); the gates it runs still shell out exactly as before. `env` replaces
    os.environ wholesale when given, as subprocess.run(env=...) would. `timeout` is kept
    for the call sites; the checks bound their own subprocesses."""
    del timeout
    out, err = io.StringIO(), io.StringIO()
    before = os.getcwd()
    with mock.patch.dict(os.environ, env if env is not None else {}, clear=env is not None):
        try:
            os.chdir(str(cwd))
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = rc.main([str(a) for a in args])
                except SystemExit as exc:
                    code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)
        finally:
            os.chdir(before)
    return Completed(code, out.getvalue(), err.getvalue())


class RunsAsAProgram(unittest.TestCase):
    """The one subprocess call: the checklist tells a person to run the file, so it must
    run as a program, not only as an imported main()."""

    def test_help_exits_zero_from_a_subprocess(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True,
                              text=True, cwd=str(ROOT), timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("usage: release_check.py", proc.stdout)


def skill_md(name, proof):
    return f"---\nname: {name}\ndescription: fixture\nmetadata:\n  proof: {proof}\n---\n\n# {name}\n"


def make_fixture(root, *, harden_proof="self-run", witness="live", witnessed="2026-09-28",
                 owed=False, batch=True):
    """The minimal tree the state-reading gates consult, and none of the tools
    the other checks run — those FAIL (a checkout without them is no release),
    which leaves the checks under test as the only thing being read."""
    root = Path(root)
    for mission in ("harden-it", "prove-it", "clean-sweep"):
        d = root / "skills" / mission
        d.mkdir(parents=True)
        proof = harden_proof if mission == "harden-it" else "self-run"
        (d / "SKILL.md").write_text(skill_md(mission, proof), encoding="utf-8")
    (root / "runtime" / "scripts").mkdir(parents=True)
    (root / "runtime" / "pins.json").write_text(json.dumps({
        "orca": {"version": "v9.9.9", "witness": witness, "witnessed": witnessed}}),
        encoding="utf-8")
    # The real CLI, at the path the gate runs it from: it resolves its store
    # relative to its own location, so the copy reads the fixture's docs/runs/.
    shutil.copy(ROOT / "runtime" / "scripts" / "gate-batch.py",
                root / "runtime" / "scripts" / "gate-batch.py")
    if batch:
        run_dir = root / "docs" / "runs" / rc.GATE_BATCH_RUN
        run_dir.mkdir(parents=True)
        path = run_dir / "gate-batch.json"
        data = gb.init_batch(path, run_id="run_fixture", run_title="fixture run")
        gb.add_gate(data, gid="G1", asked="2026-09-14", title="a parked question",
                    question="still owed?")
        if not owed:
            gb.transition(data, "G1", "answered", "answered in the fixture",
                          answered="2026-09-16")
        gb.save_batch(path, data)
    return root


def ctx_for(root):
    return rc.Context(root, fast=True, skip_github=True)


def find(checks, name):
    for check in checks:
        if check[0] == name:
            return check
    raise AssertionError(f"{name} not among {[c[0] for c in checks]}")


class TheScriptAgainstThisRepository(unittest.TestCase):
    """One run of the real thing. It executes validate.py, proof_status.py,
    run_report.py, the vf-bench gate (~7 s) and the demo, so it is ONE test."""

    def test_fast_skip_github_run_passes_every_check_the_machine_can_make(self):
        proc = run_script("--fast", "--skip-github")
        transcript = proc.stdout + "\n--- stderr ---\n" + proc.stderr
        rows = parse(proc.stdout)
        self.assertGreaterEqual(len(rows), 30, transcript)
        names = [name for _, _, name in rows]
        self.assertEqual(len(names), len(set(names)), "a check name repeats")
        for gate in ALL_GATES:
            self.assertTrue(any(n.startswith(gate + "/") for n in names), f"{gate} ran no check")

        # Only the two flags may SKIP. Anything else means this machine cannot
        # make a check the release needs, and the test would pass vacuously.
        skips = {name: reason for status, reason, name in rows if status == "SKIP"}
        gh_backed = [n for n in names if "/gh-" in n]
        self.assertGreaterEqual(len(gh_backed), 8, names)
        self.assertEqual(skips.get("gate0/unittest"), "--fast")
        for name in gh_backed:
            self.assertEqual(skips.get(name), "--skip-github", name)
        self.assertEqual(set(skips), set(gh_backed) | {"gate0/unittest"},
                         f"a SKIP nobody asked for: {skips}")

        # #235 is recorded, never graded.
        infos = [name for status, _, name in rows if status == "INFO"]
        self.assertEqual(infos, ["gate1/issue-235-marketplace"])
        self.assertRegex(proc.stdout, r"INFO  gate1/issue-235-marketplace: #235 .*does not gate")

        # Every remaining line is PASS. The one tolerated FAIL is tree-clean on
        # a developer's uncommitted tree (CONTRIBUTING says run the suite BEFORE
        # committing); CI's checkout is clean, so there it must PASS with exit 0.
        failed = [name for status, _, name in rows if status == "FAIL"]
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            self.assertEqual(failed, ["gate0/tree-clean"], transcript)
            self.assertEqual(proc.returncode, 1, transcript)
        else:
            self.assertEqual(failed, [], transcript)
            # --fast and --skip-github leave SKIPs standing, and a SKIP is not a pass:
            # the run is incomplete (3), never green (0) — PR #509 review.
            self.assertEqual(proc.returncode, 3, transcript)
        passed = [name for status, _, name in rows if status == "PASS"]
        self.assertEqual(set(names) - set(skips) - set(infos) - set(failed), set(passed))

        # The summary agrees with the lines it summarizes.
        m = SUMMARY_LINE.search(proc.stdout)
        self.assertIsNotNone(m, transcript)
        self.assertEqual([int(x) for x in m.groups()],
                         [len(passed), len(failed), len(skips), len(infos), proc.returncode])


class GatesFailOnAFixtureThatViolatesThem(unittest.TestCase):
    """Every state-reading check, shown able to fail — and to pass — on a tree
    built for it, with no network, model or full checkout in between."""

    def test_a_doctrine_only_flagship_fails_gate_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = rc.gate2(ctx_for(make_fixture(tmp, harden_proof="doctrine-only")))
            _, status, detail = find(checks, "gate2/proof-harden-it")
            self.assertEqual(status, rc.FAIL, detail)
            self.assertIn("doctrine-only", detail)
            # The siblings at self-run pass: the check tells the two apart.
            self.assertEqual(find(checks, "gate2/proof-prove-it")[1], rc.PASS)
            self.assertEqual(find(checks, "gate2/proof-clean-sweep")[1], rc.PASS)

    def test_the_re_scoped_bar_is_any_bound_tier(self):
        for proof in rc.PROOF_BAR:
            with self.subTest(proof=proof), tempfile.TemporaryDirectory() as tmp:
                checks = rc.gate2(ctx_for(make_fixture(tmp, harden_proof=proof)))
                _, status, detail = find(checks, "gate2/proof-harden-it")
                self.assertEqual(status, rc.PASS, detail)
                self.assertIn(f"proof: {proof}", detail)

    def test_a_missing_skill_or_proof_key_fails_rather_than_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_fixture(tmp)
            (root / "skills" / "harden-it" / "SKILL.md").write_text(
                "---\nname: harden-it\n---\n", encoding="utf-8")
            shutil.rmtree(root / "skills" / "prove-it")
            checks = rc.gate2(ctx_for(root))
            self.assertEqual(find(checks, "gate2/proof-harden-it")[1], rc.FAIL)
            _, status, detail = find(checks, "gate2/proof-prove-it")
            self.assertEqual(status, rc.FAIL)
            self.assertIn("missing", detail)
            # And the binder a checkout lacks is a FAIL too, never a SKIP.
            self.assertEqual(find(checks, "gate2/run-report")[1], rc.FAIL)

    def test_a_source_witness_or_a_stale_live_one_fails_gate_5(self):
        cases = (("source", "2026-09-28", rc.FAIL),   # read from a clone, not witnessed
                 ("live", "2026-09-13", rc.FAIL),     # the witness #416 replaced
                 ("live", "2026-09-16", rc.PASS),     # the boundary: the re-pin day itself
                 ("live", "2026-09-28", rc.PASS))
        for witness, witnessed, want in cases:
            with self.subTest(witness=witness, witnessed=witnessed), \
                    tempfile.TemporaryDirectory() as tmp:
                root = make_fixture(tmp, witness=witness, witnessed=witnessed)
                _, status, detail = find(rc.gate5(ctx_for(root)), "gate5/orca-pin-live")
                self.assertEqual(status, want, detail)

    def test_an_unreadable_pin_fails_gate_5(self):
        for text in ("{not json", '{"gstack": {}}', '{"orca": "a string"}'):
            with self.subTest(pins=text), tempfile.TemporaryDirectory() as tmp:
                root = make_fixture(tmp)
                (root / "runtime" / "pins.json").write_text(text, encoding="utf-8")
                _, status, detail = find(rc.gate5(ctx_for(root)), "gate5/orca-pin-live")
                self.assertEqual(status, rc.FAIL, detail)
        with tempfile.TemporaryDirectory() as tmp:
            root = make_fixture(tmp)
            (root / "runtime" / "pins.json").unlink()
            self.assertEqual(find(rc.gate5(ctx_for(root)), "gate5/orca-pin-live")[1], rc.FAIL)

    def test_an_owed_gate_fails_gate_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, status, detail = find(rc.gate1(ctx_for(make_fixture(tmp, owed=True))),
                                     "gate1/gate-batch-owed")
            self.assertEqual(status, rc.FAIL, detail)
            self.assertIn("G1", detail)
        with tempfile.TemporaryDirectory() as tmp:
            _, status, detail = find(rc.gate1(ctx_for(make_fixture(tmp, owed=False))),
                                     "gate1/gate-batch-owed")
            self.assertEqual(status, rc.PASS, detail)
            self.assertIn("G1 answered", detail)

    def test_a_missing_gate_batch_store_fails_not_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, status, detail = find(rc.gate1(ctx_for(make_fixture(tmp, batch=False))),
                                     "gate1/gate-batch-owed")
            self.assertEqual(status, rc.FAIL, detail)
            self.assertIn("no batch", detail)

    def test_the_chaining_index_needs_the_report_path_not_the_word(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_fixture(tmp)
            (root / "docs" / "runs" / "README.md").write_text(
                "# Run archive\n\nA chain of custody, but no report named.\n", encoding="utf-8")
            checks = rc.gate5(ctx_for(root))
            self.assertEqual(find(checks, "gate5/chaining-report-published")[1], rc.FAIL)
            self.assertEqual(find(checks, "gate5/chaining-report-indexed")[1], rc.FAIL)
            (root / "docs" / "reports" / "chaining-2026-09-16").mkdir(parents=True)
            (root / "runtime" / "mission-chaining.md").write_text(
                "see docs/reports/chaining-2026-09-16/handoff-log.md\n", encoding="utf-8")
            checks = rc.gate5(ctx_for(root))
            _, status, detail = find(checks, "gate5/chaining-report-published")
            self.assertEqual(status, rc.PASS, detail)
            self.assertIn("docs/reports/chaining-2026-09-16/", detail)
            _, status, detail = find(checks, "gate5/chaining-report-indexed")
            self.assertEqual(status, rc.PASS, detail)
            self.assertIn("runtime/mission-chaining.md", detail)

    def test_gate_6_used_reads_run_artifacts_not_the_tools_presence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_fixture(tmp)  # gate-batch.py + its store; no watchdog, no tests/
            checks = rc.gate6(ctx_for(root))
            self.assertEqual(find(checks, "gate6/watchdog-merged")[1], rc.FAIL)
            _, status, detail = find(checks, "gate6/gate-batch-merged")
            self.assertEqual(status, rc.FAIL)
            self.assertIn("tests/test_gate_batch.py missing", detail)
            _, status, detail = find(checks, "gate6/gate-batch-used")
            self.assertEqual(status, rc.PASS, detail)
            self.assertIn(f"docs/runs/{rc.GATE_BATCH_RUN}/gate-batch.json", detail)
            self.assertEqual(find(checks, "gate6/watchdog-used")[1], rc.FAIL)
            (root / "docs" / "runs" / "some-run").mkdir()
            (root / "docs" / "runs" / "some-run" / "REPORT.md").write_text(
                "ran runtime/scripts/watchdog.py --dry-run over the trace\n", encoding="utf-8")
            _, status, detail = find(rc.gate6(ctx_for(root)), "gate6/watchdog-used")
            self.assertEqual(status, rc.PASS, detail)
            self.assertIn("docs/runs/some-run/REPORT.md", detail)

    def test_gates_3_and_4_read_the_workflow_and_doc_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_fixture(tmp)
            c3, c4 = rc.gate3(ctx_for(root)), rc.gate4(ctx_for(root))
            for checks, name in ((c3, "gate3/ci-runs-vf-bench"),
                                 (c3, "gate3/ci-runs-negative-control"),
                                 (c3, "gate3/vf-bench-gate"),
                                 (c3, "gate3/negative-control-demo"),
                                 (c4, "gate4/install-command-in-readme"),
                                 (c4, "gate4/install-command-in-distribution"),
                                 (c4, "gate4/checklist-exists")):
                self.assertEqual(find(checks, name)[1], rc.FAIL, name)
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "validate.yml").write_text("run: python3 bench/vf-bench/gate.py\n",
                                             encoding="utf-8")
            (wf / "negative-control.yml").write_text("run: sh demo/negative-control/run.sh\n",
                                                     encoding="utf-8")
            (root / "README.md").write_text("git clone … && sh scripts/install.sh\n",
                                            encoding="utf-8")
            (root / "docs" / "distribution.md").write_text("`sh scripts/install.sh`\n",
                                                           encoding="utf-8")
            (root / "docs" / "release-1.0-checklist.md").write_text("# checklist\n",
                                                                    encoding="utf-8")
            c3, c4 = rc.gate3(ctx_for(root)), rc.gate4(ctx_for(root))
            _, status, detail = find(c3, "gate3/ci-runs-vf-bench")
            self.assertEqual(status, rc.PASS, detail)
            self.assertIn("validate.yml", detail)
            self.assertEqual(find(c3, "gate3/ci-runs-negative-control")[1], rc.PASS)
            for name in ("gate4/install-command-in-readme",
                         "gate4/install-command-in-distribution", "gate4/checklist-exists"):
                self.assertEqual(find(c4, name)[1], rc.PASS, name)


FAKE_GH = """#!/bin/sh
# A canned `gh` for tests: every answer comes from the environment, so one script
# plays authenticated, logged-out, offline and wrong-answer GitHub in turn.
case "$1 $2" in
  "auth status")
    [ -n "$GH_AUTH_STDERR" ] && printf '%s\\n' "$GH_AUTH_STDERR" >&2
    exit "${GH_AUTH_EXIT:-0}" ;;
  "issue view") out="$GH_ISSUE_JSON" ;;
  "pr view") out="$GH_PR_JSON" ;;
  "run list") out="$GH_RUN_JSON" ;;
  *) echo "unexpected gh argv: $*" >&2; exit 9 ;;
esac
[ -n "$GH_CMD_STDERR" ] && printf '%s\\n' "$GH_CMD_STDERR" >&2
printf '%s\\n' "$out"
exit "${GH_CMD_EXIT:-0}"
"""


class GitHubAnswersAreVerdicts(unittest.TestCase):
    """With gh present and answering, its answer is a verdict (PASS/FAIL), never a SKIP;
    a machine at fault (logged out, offline) is a SKIP that names why. A canned `gh` on
    PATH plays each role; the fixture is a real git repository so HEAD binds."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = make_fixture(Path(self.tmp.name) / "repo")
        for argv in (["git", "init", "-q"], ["git", "config", "user.email", "t@example.com"],
                     ["git", "config", "user.name", "t"], ["git", "add", "-A"],
                     ["git", "commit", "-q", "-m", "fixture"]):
            subprocess.run(argv, cwd=str(self.root), check=True, capture_output=True)
        self.head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(self.root),
                                   capture_output=True, text=True, check=True).stdout.strip()
        bin_dir = Path(self.tmp.name) / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(0o755)
        self.env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

    def ctx(self):
        return rc.Context(self.root, fast=True, skip_github=False)

    def with_gh(self, **answers):
        env = dict(self.env)
        env.update({k: str(v) for k, v in answers.items()})
        return mock.patch.dict(os.environ, env, clear=False)

    def test_closed_and_merged_answers_pass_open_ones_fail(self):
        with self.with_gh(GH_ISSUE_JSON='{"state": "CLOSED"}', GH_PR_JSON='{"state": "MERGED"}'):
            ctx = self.ctx()
            self.assertEqual(rc.check_issue_closed(ctx, "gate1", 408, "x")[1], rc.PASS)
            self.assertEqual(rc.check_pr_merged(ctx, "gate1", 406, "x")[1], rc.PASS)
        with self.with_gh(GH_ISSUE_JSON='{"state": "OPEN"}', GH_PR_JSON='{"state": "OPEN"}'):
            ctx = self.ctx()
            name, status, detail = rc.check_issue_closed(ctx, "gate1", 408, "x")
            self.assertEqual((name, status), ("gate1/gh-issue-408-closed", rc.FAIL))
            self.assertIn("OPEN", detail)
            _, status, detail = rc.check_pr_merged(ctx, "gate1", 406, "x")
            self.assertEqual(status, rc.FAIL)
            self.assertIn("OPEN", detail)

    def test_a_workflow_run_is_green_only_at_this_head(self):
        at_head = json.dumps([{"conclusion": "success", "headSha": self.head}])
        with self.with_gh(GH_RUN_JSON=at_head):
            name, status, detail = rc.check_workflow_green_at_head(self.ctx(), "gate0", "validate")
            self.assertEqual((name, status), ("gate0/gh-validate-run-green-at-head", rc.PASS))
            self.assertIn(self.head, detail)
        stale = json.dumps([{"conclusion": "success", "headSha": "0" * 40}])
        with self.with_gh(GH_RUN_JSON=stale):
            _, status, detail = rc.check_workflow_green_at_head(self.ctx(), "gate0", "validate")
            self.assertEqual(status, rc.FAIL)
            self.assertIn("stale green", detail)
        with self.with_gh(GH_RUN_JSON="[]"):
            _, status, detail = rc.check_workflow_green_at_head(self.ctx(), "gate0", "validate")
            self.assertEqual(status, rc.FAIL)
            self.assertIn("no `validate` workflow run", detail)

    def test_an_answer_that_is_not_json_fails_the_check(self):
        with self.with_gh(GH_ISSUE_JSON="<html>rate limited</html>"):
            _, status, detail = rc.check_issue_closed(self.ctx(), "gate1", 408, "x")
        self.assertEqual(status, rc.FAIL)
        self.assertIn("printed no JSON", detail)

    def test_a_failing_gh_command_is_a_skip_when_the_machine_is_at_fault_else_a_fail(self):
        cases = (("error: not logged in to any hosts. run gh auth login", rc.SKIP, "gh unauthenticated"),
                 ("dial tcp: lookup api.github.com: no such host", rc.SKIP, "no network"),
                 ("GraphQL: Could not find an Issue with the number of 408 (repository.issue)",
                  rc.FAIL, "exit 1"))
        for stderr, want_status, want_detail in cases:
            with self.subTest(stderr=stderr), self.with_gh(GH_CMD_EXIT=1, GH_CMD_STDERR=stderr):
                _, status, detail = rc.check_issue_closed(self.ctx(), "gate1", 408, "x")
                self.assertEqual(status, want_status, detail)
                self.assertIn(want_detail, detail)

    def test_the_auth_probe_runs_once_and_classifies_the_machine(self):
        with self.with_gh():
            ctx = self.ctx()
            self.assertIsNone(rc.gh_unavailable(ctx))
            self.assertIsNone(rc.gh_unavailable(ctx))  # memoized, not re-probed
        with self.with_gh(GH_AUTH_EXIT=1, GH_AUTH_STDERR="You are not logged in to any GitHub hosts"):
            self.assertEqual(rc.gh_unavailable(self.ctx()), "gh unauthenticated")
        with self.with_gh(GH_AUTH_EXIT=1, GH_AUTH_STDERR="error connecting: could not resolve host"):
            self.assertTrue(rc.gh_unavailable(self.ctx()).startswith("no network: "))
        with self.with_gh(GH_ISSUE_JSON='{"state": "CLOSED"}', GH_PR_JSON='{"state": "MERGED"}',
                          GH_RUN_JSON=json.dumps([{"conclusion": "success", "headSha": self.head}])):
            rows = rc.gate1(self.ctx())
            gh_rows = [r for r in rows if "/gh-" in r[0]]
            self.assertTrue(gh_rows)
            self.assertNotIn(rc.SKIP, {status for _, status, _ in gh_rows})


class SkipsNeverPass(unittest.TestCase):
    def test_skip_github_skips_every_gh_backed_check_with_the_flag_as_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = ctx_for(make_fixture(tmp))
            self.assertEqual(rc.check_issue_closed(ctx, "gate1", 408, "x"),
                             ("gate1/gh-issue-408-closed", rc.SKIP, "--skip-github"))
            self.assertEqual(rc.check_pr_merged(ctx, "gate1", 406, "x"),
                             ("gate1/gh-pr-406-merged", rc.SKIP, "--skip-github"))
            self.assertEqual(rc.check_workflow_green_at_head(ctx, "gate0", "validate"),
                             ("gate0/gh-validate-run-green-at-head", rc.SKIP, "--skip-github"))
            _, status, detail = rc.info_issue_235(ctx)
            self.assertEqual(status, rc.INFO)
            self.assertIn("does not gate", detail)
            self.assertIn("--skip-github", detail)
            gh_checks = [c for gate in (rc.gate0, rc.gate1, rc.gate4, rc.gate5, rc.gate6)
                         for c in gate(ctx) if "/gh-" in c[0]]
            self.assertGreaterEqual(len(gh_checks), 8)
            self.assertEqual({(s, d) for _, s, d in gh_checks}, {(rc.SKIP, "--skip-github")})

    def test_no_gh_on_path_yields_skip_no_gh_never_pass(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as emptybin:
            root = make_fixture(tmp)
            env = dict(os.environ, PATH=emptybin)
            env.pop("GH_TOKEN", None)
            env.pop("GITHUB_TOKEN", None)
            proc = run_script("--fast", "--repo", str(root), cwd=root, env=env)
            self.assertIn(proc.returncode, (1, 3), proc.stderr)  # it ran; a fixture is no release
            rows = parse(proc.stdout)
            gh_rows = [r for r in rows if "/gh-" in r[2]]
            self.assertGreaterEqual(len(gh_rows), 8, proc.stdout)
            for status, reason, name in gh_rows:
                self.assertEqual((status, reason), ("SKIP", "no gh"), name)
            self.assertRegex(proc.stdout,
                             re.compile(r"^\s*SKIP\(no gh\)  gate1/gh-issue-408-closed$", re.M))
            self.assertRegex(proc.stdout, r"INFO  gate1/issue-235-marketplace: .*no gh")
            self.assertIn("SKIP(--fast)  gate0/unittest", proc.stdout)
            # git is off that PATH too: the tree check is a SKIP as well, not a PASS.
            self.assertIn("SKIP(no git)  gate0/tree-clean", proc.stdout)
            self.assertNotRegex(proc.stdout, r"PASS  gate\d/gh-")


class MachineOutputAndExitContract(unittest.TestCase):
    def test_a_standing_skip_is_incomplete_never_green(self):
        # PR #509 review: --fast / --skip-github / a machine without gh used to exit 0
        # when nothing failed, so a release script reading the code could cut 1.0 on a
        # run that never checked the suite, CI at HEAD, or the issue and PR states.
        counts = {"pass": 30, "fail": 0, "skip": 0, "info": 1}
        self.assertEqual(rc.exit_code(counts), 0)
        self.assertEqual(rc.exit_code(dict(counts, skip=1)), 3)
        self.assertEqual(rc.exit_code(dict(counts, skip=1, fail=1)), 1)
        self.assertEqual(rc.exit_code(dict(counts, fail=1)), 1)
        self.assertEqual(rc.EXIT_INCOMPLETE, 3)

    def test_the_summary_line_and_the_exit_carry_a_skip_as_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_fixture(tmp)
            (root / "scripts").mkdir(exist_ok=True)
            proc = run_script("--fast", "--skip-github", "--json", "--repo", str(root), cwd=root)
            data = json.loads(proc.stdout)
            self.assertEqual(data["exit"], proc.returncode)
            if data["summary"]["fail"] == 0:
                self.assertEqual(proc.returncode, 3)
            else:
                self.assertEqual(proc.returncode, 1)

    def test_json_is_one_object_whose_summary_and_exit_agree_with_its_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_fixture(tmp)
            proc = run_script("--fast", "--skip-github", "--json", "--repo", str(root), cwd=root)
            data = json.loads(proc.stdout)
            checks = [c for g in data["gates"] for c in g["checks"]]
            self.assertEqual([g["gate"] for g in data["gates"]], [g for g, _, _ in rc.GATES])
            statuses = [c["status"] for c in checks]
            self.assertTrue(set(statuses) <= set(rc.STATUSES), statuses)
            self.assertEqual(data["summary"],
                             {s.lower(): statuses.count(s) for s in rc.STATUSES})
            self.assertEqual(data["exit"], proc.returncode)
            self.assertEqual(proc.returncode, 1)  # no validate.py in a fixture: FAIL, exit 1
            self.assertTrue(data["fast"] and data["skip_github"])
            self.assertEqual(data["repo"], str(root.resolve()))
            skips = {c["name"]: c["detail"] for c in checks if c["status"] == "SKIP"}
            self.assertEqual(skips["gate0/unittest"], "--fast")
            self.assertEqual(skips["gate1/gh-issue-408-closed"], "--skip-github")

    def test_a_repo_that_is_not_a_directory_is_could_not_run(self):
        proc = run_script("--repo", "/nonexistent/orca-fleet-checkout")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("not a directory", proc.stderr)

    def test_the_header_documents_the_contract(self):
        head = SCRIPT.read_text(encoding="utf-8")[:4000]
        for needle in ("0  every check PASS", "1  any check FAIL", "2  could not run",
                       "3  incomplete", "--fast", "--skip-github", "--repo", "--json",
                       "never PASS"):
            self.assertIn(needle, head, needle)
        self.assertTrue(os.access(SCRIPT, os.X_OK), "scripts/release_check.py is not executable")


class TheChecklistPointsAtTheScript(unittest.TestCase):
    """The doc stays the definition; the script is its executable form. Hold
    them together: the run command up top, one heading per gate the script
    runs, the commands the script runs shown verbatim, the stale ones gone."""

    @classmethod
    def setUpClass(cls):
        cls.text = CHECKLIST.read_text(encoding="utf-8")

    def test_it_opens_with_the_run_command(self):
        self.assertIn("Run it: `python3 scripts/release_check.py`", self.text[:400])

    def test_one_heading_per_gate_the_script_runs(self):
        headings = re.findall(r"^## (Gate \d)", self.text, re.M)
        self.assertEqual(headings, [title.split(" — ")[0] for _, title, _ in rc.GATES])

    def test_the_commands_shown_are_the_ones_the_script_runs(self):
        for needle in (
                "python3 runtime/scripts/gate-batch.py --run "
                f"{rc.GATE_BATCH_RUN} list --status owed",
                "python3 scripts/validate.py",
                "python3 -m unittest discover -s tests",
                "python3 runtime/scripts/proof_status.py --check",
                "python3 runtime/scripts/run_report.py",
                "python3 bench/vf-bench/gate.py",
                "sh demo/negative-control/run.sh",
                "gh run list --workflow validate --branch main",
                "gh run list --workflow install --branch main",
                "gh pr view 406 --json state",
                f"grep -c '{rc.INSTALL_CMD}' README.md docs/distribution.md",
                "runtime/pins.json",
                f"grep -l '{rc.CHAINING_NEEDLE}' " + " ".join(rc.CHAINING_INDEXES),
                "docs/runs/*/gate-batch.json",
                "watchdog",
        ):
            self.assertIn(needle, self.text, needle)
        for number in (408, 386, 416, 417, 418, 419):
            self.assertIn(f"gh issue view {number} --json state", self.text)
        for tool, test in rc.MECHANIZED:
            self.assertIn(tool, self.text)
            self.assertIn(test, self.text)

    def test_the_stale_gates_are_gone(self):
        self.assertNotIn("Status: ANSWERED", self.text)  # the grep over the rendered view
        self.assertNotRegex(self.text, r"gh issue view 235 [^\n]*CLOSED")  # #235 no longer gates
        self.assertIn("does not gate", self.text)
        self.assertNotRegex(self.text, r'"harden-it",\s*"external-run"')  # the pre-re-scope bar
        self.assertIn("#407", self.text)
        self.assertIn("2026-09-21-harden-it-self-run.md", self.text)

    def test_the_bars_in_the_doc_are_the_scripts_bars(self):
        m = re.search(r"^BAR = \((.*?)\)$", self.text, re.M)
        self.assertIsNotNone(m, "Gate 2's python block no longer states BAR")
        self.assertEqual(tuple(re.findall(r'"([^"]+)"', m.group(1))), rc.PROOF_BAR)
        self.assertIn(f'e["witnessed"]>="{rc.PIN_MIN_WITNESSED}"', self.text)


if __name__ == "__main__":
    unittest.main()
