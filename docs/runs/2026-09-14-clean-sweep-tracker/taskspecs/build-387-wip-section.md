# T10 — U387W: scope WIP-curve rows to the canonical section

## Problem
Greptile thread 4009895678 on rollup PR #387 (verified live on BASE f66bd20):
`_wip_rows` in runtime/scripts/run_report.py scans EVERY pipe-prefixed line,
so a complete-looking `wave=` row in a deviations table or fenced example
binds as WIP-curve evidence (false pass) or trips duplicate/stray-wave errors
(false fail). U389's criteria (C-1..C-3: settings-only refused, partial
refused, complete bind) did not cover section scoping — a distinct residual,
not a U389 defect. The canonical section EXISTS
(docs/runs/TEMPLATE.md "## WIP-curve protocol row"); the checker ignores it.

## Criteria
- C-1: `_wip_rows` collects rows ONLY inside the canonical WIP-curve section
  (confirm the exact header from TEMPLATE.md + real self-run reports; match
  ATX headings naming the WIP-curve row table, tolerate whitespace; rows in
  fenced blocks, deviations tables, or other sections are ignored).
- C-2: per-wave completeness inside the section still enforced: complete
  section rows bind; incomplete section rows are refused naming the wave;
  all pre-existing run_report tests stay green (guards).
- C-3: the protocol prose (runtime/attention-budget.md WIP-curve section)
  names the section rule, so prose and check cannot drift (U389 precedent).
  attention-budget.md is 78/160 lines — prose ADDS must keep it ≤ 160.
- C-4: `python3 -m unittest discover -s tests` and `scripts/validate.py` green.

## Negative control
`git checkout <base> -- runtime/scripts/run_report.py` (revert checker, keep
tests + prose): the C-1 tests fail (out-of-section rows bind); restore: green.
Both directions quoted in u387w-negctrl.txt.

## Red-first
C-1 tests first: a report whose ONLY complete `wave=` rows live outside the
canonical section (fenced example + deviations table) must be refused, and a
report with complete rows inside must bind — RED pre-fix (out-of-section rows
bind today). Expected values from TEMPLATE.md + real reports (independent
sources), never recomputed the checker's way.

## Hot files (ONLY these)
- `runtime/scripts/run_report.py` (`_wip_rows` + section detection)
- `runtime/attention-budget.md` (WIP-curve prose only; keep ≤ 160 lines)
- `tests/test_run_report.py` (confirm module name in-repo; the U389 nc-command
  was `python3 -m unittest tests.test_run_report`)
- `assets/badges/tests.json` (regen, own commit, only if the count moves)
- `docs/runs/2026-09-14-clean-sweep-tracker/u387w-manifest.json` (new)
- `docs/runs/2026-09-14-clean-sweep-tracker/u387w-negctrl.txt` (new)

## Out of scope
- WIP caps, graduation analysis, other report checks (binding, inventory,
  invocation) — U389's out-of-scope list stands.
- Machine-checking ledger park classes (noticed-not-touched: G-08 candidate).

## Worker protocol (run conventions)
- Ownership: ONLY the hot files above. Commit locally on your unit branch, one
  concern per commit (red tests / fix / prose / badge / manifest). Do NOT push,
  merge, or touch BASE.
- Manifest: follow the u388-manifest.json schema. `contract.source` + `digest`
  are given in your TASK preamble. `head_sha` = your tip (coordinator re-binds
  at close). commands[] via WRAPPED runs on a clean tree.
- worker_done: three-sentence summary + explicit --outcome, tip SHA, quoted
  gate outputs + RED-first evidence, --files-modified, --report-path = manifest.
