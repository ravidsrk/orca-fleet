# REFLECTION — speed-it self-test 2026-09-16 (proposal, NOT merged)

## Surprises

- The catalog-gates journey measured **273.9 s vs a 30 s budget (9.1×)** — the
  field-proof plan's "e.g. ≤30 s" was written unmeasured. Budgets declared
  without a baseline are wishes; this mission's baseline-first pipeline is what
  caught it.
- No sleep, no retry loop, no dominant file (top file 19%, top test 4.6%).
  Suite slowness here is death by a thousand forks — the profile killed three
  theories (sleeps, orca spawns, suite recursion) before landing on fixture
  fan-out. Measure-first is not a slogan; every intuition was wrong.
- Journey-level noise (±15 s run-to-run, one +33 s outlier) dwarfs hotspot gains
  (~5 s). Without a pre-registered decision rule, keep/revert would have been
  vibes. The non-overlap rule earned its place.
- The biggest single-test cost (bundle 12.6 s) is unfixable-by-design: the
  spawns ARE the oracle. Optimizing it would mean testing less — the mission's
  "fast but behaviorally wrong is a bug" clause fired before any code changed.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: `tests/` wall time is ~250 s single-threaded; per-file runs
  (`python3 -m unittest tests.test_<name>`) are the inner loop, full suite for gates.
- GOTCHAS: fixture repos in shell-contract tests are expensive — new matrix
  classes must justify per-test rebuilds; share read-only fixtures via
  setUpClass (see tests/test_deny_hook.py HookBase).
- TEST_STRATEGY: never add a wall-clock assertion to the suite; perf budgets
  live in harnesses (`docs/runs/.../bin/measure-j1.sh` pattern), not in tests.
- STYLE: `git -c user.name/email commit` over persistent `git config` in
  throwaway fixtures — identical bytes, fewer spawns.

## Prompt / playbook tweaks (fleet-side, optional)

- speed-it: add a pre-registered KEEP-OR-REVERT decision rule to the metric
  contract (e.g. non-overlapping ranges) — "inside the noise band" needs an
  operational band before the rebench, not after. Backlog item, not edited here.
