# CONFIRM-SURFACE — human gate request (reshape-it self-test, 2026-09-16)

Status: **PARKED — awaiting explicit human freeze.** Per `skills/reshape-it/SKILL.md`
("Headless/spawned: publish the inventory and PARK at the gate — one-way doors are
human-only, never auto-bounded") and `runtime/gate-classification.md` (one-way: HUMAN ONLY),
this run bounds nothing by itself. Silence is not a freeze.

Gate: `CONFIRM-SURFACE` · class: one-way · session: headless/spawned ·
inventory: [inventory.md](inventory.md) · transcript: [scan-transcript.txt](scan-transcript.txt)

## Verified Current State (read from the tree at `c46d4b3f`, not recalled)

- Target repo is orca-fleet at `origin/main` tip `c46d4b3f3371e41408aed19e54476fa194c20b42`
  (2026-09-16); 1215 commits in the 90-day window; the suite and `scripts/validate.py`
  gates are recorded in [run-report.md](run-report.md).
- SCAN probed all 73 tracked Python modules. Production surface (`scripts/` +
  `runtime/scripts/`, 22 modules) ranks head-first:
  `scripts/validate.py` (302.52) > `runtime/scripts/verify.py` (248.76) >
  `scripts/eval.py` (191.78) > `runtime/scripts/run_report.py` (158.21), then a
  long tail (next: `scripts/gen-badges.py` at 65.70).
- No module defines `__all__`; WIDTH is top-level-symbol count throughout. YAGNI cut is
  empty (all 73 churned in-window). `tests/` (39 files) is the characterization net
  itself, not a deepening target; `bench/`, `assets/`, `demo/`, one-off `docs/reports/`
  probes (12 files) are auxiliary, not lived-in interfaces.
- Nothing has been restructured: no BASE created, no CHARACTERIZE net pinned, no DEEPEN
  unit dispatched, no worker spawned. The only new bytes are this run's evidence
  directory. `git status` at gate time shows only
  `docs/runs/campaign-2026-09-16-reshape-it/` as added.

## Premises (agree / disagree — a disagreed premise loops, never overridden)

- PREMISE 1: The deepen-able surface is production code (`scripts/`, `runtime/scripts/`);
  `tests/` is the oracle, not a target — agree / disagree.
- PREMISE 2: Auxiliary tooling (`bench/`, `assets/diagrams/generator/`, `demo/`,
  one-off `docs/reports/` probes) is out of scope for this run — agree / disagree.
- PREMISE 3: The inventory numbers order candidates; the human bounds the target list —
  agree / disagree.

## Recommended bound (to approve, amend, or reject — not auto-picked)

- ❓ **Which modules enter CHARACTERIZE → DEEPEN this run?**
- ➡️ Recommendation: bound to the top two production seams — `scripts/validate.py`
  (46 churn / 73 width / 1110 depth / 50 fan-in) and `runtime/scripts/verify.py`
  (58 / 92 / 2145 / 53) — one seam at a time, `validate.py` first; everything else
  joins the NEXT scan, not this one. Rationale: both head the ranking by a wide margin,
  both match the catalog's own field-proof prediction, and both already sit under the
  repo's heaviest test coverage (the future characterization net has the most to build on).

## What happens after the freeze

On explicit human `yes` (with the bounded list): BOOTSTRAP integration BASE via
`runtime/scripts/preflight.py` (BASE ≠ default), CHARACTERIZE each confirmed seam per
`characterize` (mutation-audited net, own SHA, own ledger row) BEFORE any restructure,
then DEEPEN one module per unit (rw workers, single TASK pack, build-blind review),
RE-SCAN, VERDICT. Any seam needing a one-way API break parks as RESHAPED-WITH-PARKED
with the decision named.

Record the freeze with reporter identity + timestamp in [ledger.md](ledger.md) and
[run-report.md](run-report.md); until then this run stays parked here.
