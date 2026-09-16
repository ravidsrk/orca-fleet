# REFLECTION — oncall-it self-test 2026-09-16 (`compound-learn`)

## Surprises

- The repo answers the applicability question itself: `docs/ops.md` states
  "no hosted service, staging, or deploy target" outright. The fastest probe
  was reading the target's own ops page, not the filesystem scans.
- The nearest substitute (CI-as-a-job) fails on ALL FOUR hard dependencies at
  once, and the T-11 drill transcript already documents two of the failures
  (unobservable notification delivery; induction prohibited). Prior evidence
  compounding correctly prevented a fabricated path.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- None. Zero merged units, zero target-repo gotchas encountered; per
  `compound-learn`, a run with zero merged units and zero parked learnings
  skips. (The OPS-1 park is campaign-harness-owned, not target-repo
  knowledge.)

## Prompt / playbook tweaks (fleet-side, optional)

- None filed: the mission's HARD-dependency clause and the FREEZE-as-human-gate
  rule produced exactly the honest park they exist to produce. No preamble
  change would have altered the outcome.
