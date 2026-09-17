# Diagnose — J1 bottleneck (profile evidence)

## Symptom→cause tree

- J1 median 273.93 s = tests-stage 272.90 s + validate 0.99 s + proof_status 0.04 s
  → the breach lives entirely in the tests stage (`profile.log`, `BASELINE.md`).
- tests stage = 1490 tests, OK, user+sys ≈ 190 s of 273 s → CPU-bound in process
  fan-out, not waiting on sleeps/network (only trivial `sleep(0.002–0.01)` fixtures;
  `SETTLE_SECS` already stubbed to 0 in the suspect file — sleep theory REFUTED).
- Per-file profile (`profile.log`, single pass, Σ ≈ 278 s):
  test_spawn_worker 52.06 s (19%) · test_deny_hook 51.70 s (19%) ·
  test_verify 37.04 s · test_bundle 27.83 s · test_vfbench 21.56 s ·
  test_docs_navigation 15.71 s · rest < 10 s each.
- Per-test profile: no pathological test. Max single test = bundle's
  `test_all_missions_preserve_installed_interfaces` 12.60 s (4.6% of J1) — 63
  `--help` entry-point spawns that ARE the oracle (cannot remove without weakening
  the proof — rejected). spawn_worker top test 4.18 s; cost is a smooth gradient
  of 1–4 s multi-shape matrix tests.

## The one dominant cause

**Zero fixture reuse: every fixture-backed test rebuilds an identical hermetic temp
git repo and re-spawns bash/python3/git per assertion.** ~1300 tests × (git init +
configs + add + commit + ref pins) plus per-assertion `bash`/`sh`/`python3` spawns
in the shell-contract matrices. No sleep, no retry loop, no single file to blame —
the suite's hermetic-everything design is the cost, and it is inherent to its
proof strength except where identical fixtures can be provably shared.

## Fixable hotspot H1 (this run's unit)

`tests/test_deny_hook.py` 51.7 s: 140 tests × identical 6-spawn repo build
(init/config/config/add/commit/update-ref). Audit (`bin/` notes + ledger):
- 88 tests in 8 classes are provably read-only w.r.t. the fixture (no fs writes
  outside setUp; hook invokes only `git symbolic-ref`/`git show-ref` — read-only,
  no config reads).
- 41 tests in 2 classes mutate per-test fixtures (symlink/file matrices) → keep
  fresh fixtures.
- 9 tests in TestScriptShape manage their own tmpdirs → untouched.
Fix: class-shared fixture for read-only classes + fold 2 `git config` spawns into
`commit -c` flags (identical commit bytes). Expected ≈ 30–35 s saving on J1.

## Parked (cause + gate, beyond hotspot scope)

- Residual ~240 s over budget after H1: diffuse fan-out across 40 files; reaching
  ≤30 s needs a parallel runner + CI sharding and/or fixture re-architecture
  (≈9×) — an infra change beyond a hotspot sweep. Gate: human decision on a
  stdlib parallel runner + `assets/badges` race resolution (parallel writers race
  today), tracked as the journey park with this report as ref.
- spawn_worker matrices, verify's mutating RepoCases, bundle's oracle spawns:
  inherent-cost tradeoffs — collapsing them weakens distinct assertions.
