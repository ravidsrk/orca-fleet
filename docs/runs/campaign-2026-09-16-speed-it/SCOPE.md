# speed-it self-test — frozen scope (2026-09-16)

Target: orca-fleet itself @ `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip at T0).
Worktree branch: `campaign/speed-it-selftest` (fork point = same SHA; no-gh lane — no PRs per task rules).

## Frozen critical-journey list (1 journey)

| ID | Journey | Stages (sequential, same shell, repo root) |
|----|---------|--------------------------------------------|
| J1 | catalog-gates | `python3 scripts/validate.py` → `python3 -m unittest discover -s tests` → `python3 runtime/scripts/proof_status.py --check` |

Source: field-proof plan row for speed-it (`docs/runs/README.md`):
"the catalog-gates journey (`validate.py` + `tests/` + `proof_status`), declared budget e.g. ≤30s wall".

## Budgets

| Journey | Budget | Gate |
|---------|--------|------|
| J1 | **≤ 30 s wall** (sum of the three stages) | human-confirmed set: COORDINATOR-ADOPTED from the field-proof plan's stated e.g. value; human re-confirm owed (headless run, recorded as deviation D1) |

## Metric contract (declared BEFORE baselining)

- Metric: lab wall-clock seconds, summed over the three stages, measured with
  `time.time()` deltas around each stage in `bin/baseline.sh`.
- Confirmation: **median of 5 sequential runs** at pinned conditions (mission's lab
  contract: median of ≥5, spread reported). Baseline and candidate share source,
  sample size (n=5), and pinned conditions — no lab-vs-other comparisons.
- Pinned conditions: host `ravindra-mbp`, macOS, python 3.13.15, worktree HEAD
  `c46d4b3f`, nothing else running; `assets/` restored between runs (suite rewrites
  badge files with identical bytes).
- Exit contract: all three stages exit 0 on every run (a fast red run is not a win).
- Noise band: TBD from baseline spread (max−min); KEEP-OR-REVERT applied against it.

## Worker-playbook router (exactly one)

`gstack benchmark` — CLI wall-time measurement + profile-guided hotspot fix.
`addyosmani performance-optimization` is NOT co-mounted (AGENTS.md hard rule).
`browser-drive` is inapplicable: no rendered-page oracle exists for this journey
(recorded, not substituted — no curl/unit-test substitution per that playbook).

## Terminal outcomes in play

- WITHIN-BUDGET: J1 median ≤ 30 s confirmed to this contract + CI guard at the
  DECLARED budget (not at the best run).
- OPTIMIZED-WITH-PARKED: fixable hotspots fixed; residual breach parked with cause + gate.
