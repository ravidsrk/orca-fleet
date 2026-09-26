#!/usr/bin/env python3
"""Split the unittest suite into N file-level shards for CI matrix fan-out.

The catalog-gates journey (validate + full suite + proof_status) runs ~260 s
sequentially, ~9x over its 30 s budget, and the cost is diffuse per-test
process fan-out no single hotspot fix can remove (see the speed-it self-test
report, docs/runs/campaign-2026-09-16-speed-it/REPORT.md). This script is the
reversible half of that run's parked infra gate: it partitions tests/test_*.py
into N shards so CI runs them in parallel jobs while unittest stays the runner
and no test dependency is added (the suite is stdlib-only by design).

Shards are FILE-level on purpose: splitting a module across processes would
re-run setUpClass fixtures per shard (test_deny_hook shares read-only repos
that way) for no balance gain — LPT over files already lands within ~2% of
the mean at N=4. Weights below are single-pass wall seconds measured on
2026-09-17 (ravindra-mbp, python 3.13, main @ 496815ba); they steer balance
only, never correctness — the partition always covers every discovered module
exactly once, which tests/test_shard_tests.py proves against live discovery.
The reshape_* rows below were measured separately (0.03–0.04 s each) on
speed/j1-sharding and recorded at the 0.1 floor the table uses for fast files.

Usage:
  python3 scripts/shard-tests.py --list [--of N]      print the partition
  python3 scripts/shard-tests.py --shard I --of N     run shard I (1-based)
  python3 scripts/shard-tests.py --check [--of N]     assert full coverage

  --shard takes --with-coverage: the shard's unittest runs wrapped in
  `coverage run --parallel-mode`, one data file per shard for CI to combine.
  Tracing cannot cross into run_shard's unittest subprocess any other way —
  `coverage run` around THIS script would measure the sharder, not the suite.

Adding tests/test_<name>.py: add its measured weight here (one run of
`python3 -m unittest tests.test_<name>` from the repo root, wall seconds).
The weights-freshness test fails until you do, so a new file can neither
silently join the wrong shard nor silently run nowhere.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"
DEFAULT_SHARDS = 4

# Module -> seconds. Single-pass `python3 -m unittest tests.<mod>` walls,
# repo root cwd, 2026-09-17. Balance-only: correctness never reads this.
WEIGHTS = {
    "test_architecture": 6.1,
    "test_bind_check": 2.2,
    "test_bundle": 23.0,
    "test_call_for_runs": 0.1,
    "test_check_reply": 2.4,
    "test_decisions": 1.4,
    "test_deny_hook": 48.9,
    "test_diff_scope": 5.2,
    "test_dispatch_sign": 0.5,
    "test_docs_navigation": 15.8,
    "test_ed25519": 1.3,
    "test_egress": 2.5,
    "test_evals": 3.8,
    "test_evidence_run": 4.5,
    "test_floor_guard": 7.3,
    "test_gate_batch": 0.1,
    "test_governance_commands": 2.7,
    "test_guard_text": 1.1,
    "test_hitl_ask": 3.0,
    "test_hitl_loop": 0.1,
    "test_install_status": 9.9,
    "test_inventory": 0.9,
    "test_migration_walkthrough": 0.1,
    "test_negative_control": 1.1,
    "test_one_way_doors": 2.2,
    "test_orphan_wiring": 0.1,
    "test_pins": 0.1,
    "test_pm": 0.1,
    "test_preflight": 7.1,
    "test_proof_status": 0.1,
    "test_repo_hygiene": 0.4,
    "test_reshape_net_validate": 0.1,
    "test_reshape_net_verify": 0.1,
    "test_reshape_width_validate": 0.1,
    "test_reshape_width_verify": 0.1,
    "test_run_report": 7.5,
    "test_sandbox_doctor": 0.1,
    "test_search_sessions": 3.1,
    "test_send_msg": 1.2,
    "test_shard_tests": 1.0,
    "test_spawn_worker": 48.4,
    "test_spawn_upstream": 19.9,
    "test_task_ops": 2.5,
    "test_terminal_ops": 3.1,
    "test_validate": 1.6,
    "test_verdict_check": 0.1,
    "test_verify_gate": 10.1,
    "test_verify": 38.7,
    "test_vfbench_gate": 0.1,
    "test_vfbench": 22.5,
    "test_watchdog": 0.4,
    "test_wire_docs": 0.2,
    "test_worker_ops": 3.0,
    "test_worktree_ops": 1.9,
}


def discover_modules():
    """Every tests/test_*.py module stem, sorted. The partition input."""
    return sorted(p.stem for p in TESTS_DIR.glob("test_*.py"))


def partition(modules, n, weights=None):
    """LPT assignment of modules to n shards; deterministic, total coverage.

    Greedy longest-processing-time: heaviest module first onto the currently
    lightest shard, ties broken by shard index then module name, so the same
    inputs always produce the same shards. Unknown modules take the median
    known weight — balance degrades gracefully, coverage never does.
    """
    if n < 1:
        raise ValueError(f"shard count must be >= 1, got {n}")
    weights = WEIGHTS if weights is None else weights
    ordered = sorted(weights.values())
    fallback = ordered[len(ordered) // 2]
    loads = [0.0] * n
    shards = [[] for _ in range(n)]
    for mod in sorted(modules, key=lambda m: (-weights.get(m, fallback), m)):
        i = min(range(n), key=lambda j: (loads[j], j))
        shards[i].append(mod)
        loads[i] += weights.get(mod, fallback)
    return shards


def predicted_wall(shard, weights=None):
    weights = WEIGHTS if weights is None else weights
    ordered = sorted(weights.values())
    fallback = ordered[len(ordered) // 2]
    return round(sum(weights.get(m, fallback) for m in shard), 1)


def check(shards, modules):
    """Coverage errors: anything missing, doubled, or an empty shard."""
    errors = []
    seen = {}
    for i, shard in enumerate(shards, start=1):
        if not shard:
            errors.append(f"shard {i} is empty — a CI job that runs zero tests and passes")
        for mod in shard:
            if mod in seen:
                errors.append(f"{mod} is in shards {seen[mod]} and {i}")
            seen[mod] = i
    for mod in sorted(set(modules) - set(seen)):
        errors.append(f"{mod} is in no shard — it would silently stop running")
    for mod in sorted(set(seen) - set(modules)):
        errors.append(f"{mod} is sharded but no longer exists under tests/")
    return errors


def shard_command(shard, with_coverage=False):
    """The argv run_shard executes: unittest over the shard's modules, optionally
    wrapped in `coverage run --parallel-mode` (one data file per shard; CI
    combines them before the report). A pure function so the contract test can
    pin the wrap shape without coverage installed — the suite is stdlib-only."""
    # Repo-root cwd with tests.-prefixed ids: tests assume root cwd (running
    # from tests/ reds test_inventory), and this matches the suite contract.
    cmd = [sys.executable, "-m", "unittest"] + [f"tests.{m}" for m in shard]
    if with_coverage:
        cmd = ([sys.executable, "-m", "coverage", "run", "--parallel-mode"]
               + cmd[1:])
    return cmd


def run_shard(index, n, with_coverage=False):
    modules = discover_modules()
    shards = partition(modules, n)
    errors = check(shards, modules)
    if errors:
        for e in errors:
            print(f"shard-tests: {e}", file=sys.stderr)
        return 1
    shard = shards[index - 1]
    wall = predicted_wall(shard)
    print(f"shard {index}/{n}: {len(shard)} modules, predicted ~{wall}s: "
          + " ".join(shard), flush=True)
    r = subprocess.run(shard_command(shard, with_coverage), cwd=ROOT)
    return r.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description="shard the unittest suite for CI fan-out")
    parser.add_argument("--of", type=int, default=DEFAULT_SHARDS,
                        help="shard count (must match the CI matrix)")
    parser.add_argument("--list", action="store_true", help="print the partition")
    parser.add_argument("--check", action="store_true", help="assert full coverage")
    parser.add_argument("--shard", type=int, help="1-based shard to run")
    parser.add_argument("--with-coverage", action="store_true",
                        help="wrap the shard run in `coverage run --parallel-mode`")
    args = parser.parse_args(argv)
    if args.of < 1:
        print(f"shard-tests: --of must be >= 1, got {args.of}", file=sys.stderr)
        return 2
    modules = discover_modules()
    if args.list or args.check:
        shards = partition(modules, args.of)
        if args.list:
            for i, shard in enumerate(shards, start=1):
                print(f"shard {i}/{args.of}: ~{predicted_wall(shard)}s: "
                      + " ".join(shard))
        errors = check(shards, modules)
        for e in errors:
            print(f"shard-tests: {e}", file=sys.stderr)
        return 1 if errors else 0
    if args.shard is not None:
        if not 1 <= args.shard <= args.of:
            print(f"shard-tests: --shard {args.shard} out of range for --of {args.of}",
                  file=sys.stderr)
            return 2
        return run_shard(args.shard, args.of, args.with_coverage)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
