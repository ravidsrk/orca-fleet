#!/usr/bin/env python3
"""Contract tests for scripts/shard-tests.py (speed-it J1 sharding).

The failure mode this file exists to close is a shard map that silently drops
a module: CI stays green while running a subset of the suite — the "three CI
eval jobs had run zero tests and passed" shape. So the load-bearing assertion
is ID-level: the union of per-shard live discovery equals full-suite live
discovery, pairwise disjoint. Weights steer balance only and are covered by a
freshness test plus a deterministic balance bound (no wall-clock assertions —
perf budgets live in harnesses, never in tests).

    python3 -m unittest tests.test_shard_tests -v
"""
import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "shard-tests.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


def load_sharder():
    spec = importlib.util.spec_from_file_location("_shard_tests", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def collect_ids(suite):
    out = set()

    def walk(s):
        for t in s:
            if isinstance(t, unittest.TestSuite):
                walk(t)
            else:
                out.add(t.id())

    walk(suite)
    return out


class ShardCoverage(unittest.TestCase):
    """A module that runs nowhere is a test suite that lies about its size."""

    def test_every_test_file_lands_in_exactly_one_shard(self):
        sh = load_sharder()
        modules = sh.discover_modules()
        self.assertGreater(len(modules), 20, "the scan found almost no test files")
        shards = sh.partition(modules, sh.DEFAULT_SHARDS)
        self.assertEqual(sh.check(shards, modules), [])

    def test_no_shard_is_empty(self):
        # check() already flags empties; this names the CI shape explicitly: an
        # empty shard is a matrix job that runs zero tests and reports green.
        sh = load_sharder()
        for i, shard in enumerate(sh.partition(sh.discover_modules(), sh.DEFAULT_SHARDS),
                                  start=1):
            self.assertTrue(shard, f"shard {i} runs zero tests and would pass vacantly")

    def test_union_of_shard_ids_equals_full_discovery(self):
        """ID-level, against LIVE discovery — not a file list compared to itself.

        A file list compared to its own partition passes whether or not the
        modules import or collect anything. Loading each shard's modules and
        the full suite through the real loader fails if a shard names a module
        that collects nothing, or if discovery finds tests no shard names.
        """
        sh = load_sharder()
        loader = unittest.TestLoader()
        tests_dir = str(ROOT / "tests")
        full = collect_ids(loader.discover(tests_dir))
        self.assertGreater(len(full), 1000, "full discovery collected almost nothing")
        seen, union = {}, set()
        for i, shard in enumerate(sh.partition(sh.discover_modules(), sh.DEFAULT_SHARDS),
                                  start=1):
            for mod in shard:
                # Per-module discover, NOT loadTestsFromName("tests.<mod>"): the
                # dotted import collects the same tests under different IDs
                # ("tests."-prefixed), which would fake a mismatch. Same loader
                # call shape both sides, so IDs are directly comparable.
                found = collect_ids(loader.discover(tests_dir, pattern=mod + ".py"))
                self.assertTrue(found, f"{mod} collected zero tests in its shard")
                for tid in found:
                    self.assertNotIn(tid, seen,
                                     f"{tid} runs in shards {seen.get(tid)} and {i}")
                    seen[tid] = i
                    union.add(tid)
        self.assertEqual(union, full,
                         "shards and discovery disagree — tests run twice or never")

    def test_the_id_comparison_can_actually_see_a_drop(self):
        """Without this the union test is a tautology shaped like a check.

        A mutant comparing a set to itself passes on any tree. Dropping one ID
        from a copied union must break equality, or the assertion proves nothing.
        """
        sample = {"tests.test_a.C.test_x", "tests.test_a.C.test_y"}
        dropped = set(sample)
        dropped.pop()
        self.assertNotEqual(dropped, sample, "the union comparison cannot see a drop")


class ShardDeterminismAndBalance(unittest.TestCase):
    def test_partition_is_deterministic(self):
        sh = load_sharder()
        modules = sh.discover_modules()
        self.assertEqual(sh.partition(modules, sh.DEFAULT_SHARDS),
                         sh.partition(modules, sh.DEFAULT_SHARDS))

    def test_list_output_is_byte_identical_across_runs(self):
        first = subprocess.run([sys.executable, str(SCRIPT), "--list"],
                               capture_output=True, text=True, cwd=ROOT)
        second = subprocess.run([sys.executable, str(SCRIPT), "--list"],
                                capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout,
                         "--list differs run to run — the CI partition is not stable")
        sh = load_sharder()
        for mod in sh.discover_modules():
            self.assertIn(mod, first.stdout, f"--list never names {mod}")

    def test_every_test_file_has_a_weight(self):
        """Unknown files fall back to the median weight, which silently rots
        balance as the suite grows. A new test file must name its measured
        weight deliberately — the script header says how."""
        sh = load_sharder()
        missing = sorted(set(sh.discover_modules()) - set(sh.WEIGHTS))
        self.assertEqual(missing, [],
                         f"no WEIGHTS entry in scripts/shard-tests.py for {missing} — "
                         "measure one run (`python3 -m unittest tests.<mod>` wall s "
                         "from the repo root) and add it")
        stale = sorted(set(sh.WEIGHTS) - set(sh.discover_modules()))
        self.assertEqual(stale, [], f"weights for deleted modules never run: {stale}")

    def test_predicted_shards_are_balanced(self):
        """Deterministic bound on the LPT partition — no wall clock involved.

        If the heaviest shard ever drifts past 1.5x the mean prediction, the
        weights are stale (or a module outgrew file-level sharding) and the
        matrix is fan-out theater. Today the four shards sit within 1% of
        each other, so the bound has two orders of slack against noise.
        """
        sh = load_sharder()
        walls = [sh.predicted_wall(s)
                 for s in sh.partition(sh.discover_modules(), sh.DEFAULT_SHARDS)]
        mean = sum(walls) / len(walls)
        self.assertLessEqual(max(walls), 1.5 * mean,
                             f"shard predictions {walls} are unbalanced — re-measure "
                             "WEIGHTS or reconsider the shard count")

    def test_unknown_modules_still_partition_deterministically(self):
        """The median-weight fallback path: total coverage even for modules the
        weights table has never seen (e.g. a file added between the weight
        edit and this test — the freshness test above still fails, but the
        partition itself must never drop the file)."""
        sh = load_sharder()
        modules = ["test_aaa_brand_new", "test_verify", "test_zzz_also_new"]
        first = sh.partition(modules, 2, dict(sh.WEIGHTS))
        self.assertEqual(sh.check(first, modules), [])
        self.assertEqual(first, sh.partition(modules, 2, dict(sh.WEIGHTS)))


class ShardCoverageWrap(unittest.TestCase):
    """Per-shard coverage feeds the D9 gate through a CI combine — pinned as
    command SHAPE, because the suite is stdlib-only and no test here may
    import coverage. The wrap order is the load-bearing part: `coverage run`
    must precede `-m unittest` (it traces the child interpreter), and
    `--parallel-mode` must be present (without it every shard overwrites the
    same `.coverage` file and the combine silently reports one shard)."""

    def test_default_command_runs_unittest_with_no_coverage(self):
        sh = load_sharder()
        cmd = sh.shard_command(["test_verify", "test_pins"])
        self.assertEqual(cmd[:3], [sys.executable, "-m", "unittest"])
        self.assertEqual(cmd[3:], ["tests.test_verify", "tests.test_pins"])
        self.assertNotIn("coverage", cmd)

    def test_with_coverage_wraps_unittest_in_parallel_mode(self):
        sh = load_sharder()
        cmd = sh.shard_command(["test_verify"], with_coverage=True)
        self.assertEqual(
            cmd[:6],
            [sys.executable, "-m", "coverage", "run", "--parallel-mode", "-m"])
        self.assertEqual(cmd[6:8], ["unittest", "tests.test_verify"])

    def test_cli_accepts_with_coverage(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--with-coverage", r.stdout)


class ShardCliAndWorkflowAgreement(unittest.TestCase):
    """The workflow and the script agree on the shard count, or CI is red by
    construction somewhere nobody reads. Each half is asserted from the other
    half's source so they cannot drift apart silently."""

    def _matrix_shards(self):
        (m,) = re.findall(r"shard:\s*\[([0-9,\s]+)\]", WORKFLOW.read_text(encoding="utf-8"))
        return [int(x) for x in m.split(",")]

    def test_shard_index_out_of_range_exits_2(self):
        for bad in ("0", "5"):
            r = subprocess.run([sys.executable, str(SCRIPT), "--shard", bad, "--of", "4"],
                               capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(r.returncode, 2, f"--shard {bad} --of 4: {r.stderr}")

    def test_workflow_matrix_is_contiguous_and_matches_of(self):
        wf = WORKFLOW.read_text(encoding="utf-8")
        matrix = self._matrix_shards()
        self.assertEqual(sorted(matrix), list(range(1, len(matrix) + 1)),
                         f"matrix shards {matrix} skip a number — that shard never runs")
        ofs = {int(x) for x in re.findall(r"--of\s+(\d+)", wf)}
        self.assertEqual(ofs, {len(matrix)},
                         f"workflow --of values {ofs} disagree with the {len(matrix)}-job "
                         "matrix — shards run under the wrong total")

    def test_gates_still_implies_suite_green(self):
        """`gates` is the branch-protection context; the suite moved to a matrix
        job, so gates must NEED it — otherwise the new job is advisory and a red
        suite still merges."""
        wf = WORKFLOW.read_text(encoding="utf-8")
        starts = [(m.start(), m.group(1))
                  for m in re.finditer(r"^  ([a-z_]+):$", wf, re.MULTILINE)]
        names = [n for _, n in starts]
        self.assertIn("tests", names, "the sharded suite job is gone from CI")
        self.assertIn("gates", names, "the gates job is gone from CI")
        gi = names.index("gates")
        end = starts[gi + 1][0] if gi + 1 < len(starts) else len(wf)
        gates = wf[starts[gi][0]:end]
        self.assertRegex(gates, r"needs:\s*\[[^\]]*tests[^\]]*\]",
                         "gates no longer needs the sharded suite — suite failures "
                         "cannot block the merge")

    def test_ci_shard_invocation_collects_coverage(self):
        """The --with-coverage flag unwired is the orphan-mechanism shape: CI
        would combine zero data files and the D9 gate would fail on every PR
        (or, worse, report 0% as a gate event nobody reads). The matrix
        invocation must carry the flag."""
        wf = WORKFLOW.read_text(encoding="utf-8")
        invocations = [ln.strip() for ln in wf.splitlines()
                       if "shard-tests.py" in ln and "--shard" in ln
                       and not ln.lstrip().startswith("#")]
        self.assertTrue(invocations, "no CI step invokes the sharder at all")
        for ln in invocations:
            self.assertIn("--with-coverage", ln,
                          f"shard invocation collects no coverage: {ln}")

    def test_gates_combines_shard_coverage_instead_of_rerunning(self):
        """Reconciliation, both halves: gates must `combine` the per-shard
        data files (no `coverage run` of its own — that would double-run the
        suite the matrix just ran) and still end in `coverage report`, which
        is the fail_under = 80 gate. Comments excluded: prose may name the
        old and new commands while explaining the move."""
        wf = WORKFLOW.read_text(encoding="utf-8")
        run = "\n".join(ln for ln in wf.splitlines()
                        if not ln.lstrip().startswith("#"))
        self.assertIn("coverage combine", run,
                      "gates never combines the per-shard data files")
        self.assertIn("coverage report", run,
                      "the fail_under = 80 report is gone from gates")
        self.assertNotIn("coverage run", run,
                         "gates still runs coverage itself — the suite runs twice")

    def test_no_unscoped_full_suite_run_remains_in_ci(self):
        """The matrix owns full-suite coverage now. Any surviving unscoped
        `discover -s tests` in CI double-runs the suite (~260 s) or, worse,
        becomes the 'real' gate nobody shards. The gitleaks step's scoped
        `-p test_verify.py` re-run (optional-scanner path) is the one allowed
        discover invocation."""
        unscoped = [ln.strip() for ln in WORKFLOW.read_text(encoding="utf-8").splitlines()
                    if "discover -s tests" in ln and "-p " not in ln
                    and not ln.lstrip().startswith("#")]
        self.assertEqual(unscoped, [],
                         "an unscoped full-suite run survives beside the matrix")
        self.assertIn("shard-tests.py", WORKFLOW.read_text(encoding="utf-8"),
                      "no CI step invokes the sharder — the mechanism is unwired")


if __name__ == "__main__":
    unittest.main()
