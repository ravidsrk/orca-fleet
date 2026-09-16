# REFLECTION — pin-it selftest campaign (compound-learn proposal, NOT a merge)

Run: `docs/runs/campaign-2026-09-16-pin-it/` · Terminal: PINNED-WITH-PARKED · 2026-09-16

## Surprises

- A same-build re-pin 7.5h after the morning pin is a pure no-op on the oracle side: 15/15
  guides + 234-command schema byte-identical. The only live deltas were runtime-history counters
  (unscoped worker-list total 458→460), which are activity, not drift. The mission has no
  "short-circuit when build-identical" fast path — every phase still ran, which is correct for a
  selftest but worth naming: the value of a same-build re-pin is the *negative result* (proof of
  no drift), not new coverage.
- The two post-pin mergers (`gate-batch.py`, `watchdog.py`) looked like new claim surface until a
  one-grep check showed zero `orca` CLI calls in both. New-file triage ("does it shell to the
  binary?") is the cheapest step in the pipeline and the one most likely to be skipped.
- Pipeline-order discipline (FREEZE before LOAD before REPLAY) is easy to violate by accident when
  scoping probes are needed to size the inventory. The fix was cheap (re-run everything
  post-freeze), but only because read-only probes are idempotent — a run with sender-bound probes
  could not re-order so freely.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: `Same-build re-pins still run every phase; the deliverable is the dated negative result (guides/schema byte-identical), not new coverage.`
- GOTCHAS: `New-file triage for pin-it is one grep for orca/CLI calls; fleet-only files never enter the inventory (gate-batch.py and watchdog.py, 2026-09-16, both zero-hit).`
- GOTCHAS: `Write CLAIMS.md before the first probe when the inventory can be sized from the prior pin; if scoping probes ran first, re-run the formal pipeline post-freeze and say so.`
- GOTCHAS: `Unscoped worker-list totals drift with runtime activity (+2 rows in 7.5h); compare scope/counts keys, never absolute totals.`

## Prompt / playbook tweaks (fleet-side, optional)

- Backlog item (not an edit): pin-it SKILL could name the build-identity short-circuit explicitly
  ("when installed commit == pinned commit, source anchors hold by identity; record the equality
  receipt instead of re-reading") — this run applied it as a mechanical decision, but the mission
  text currently implies a full re-read every run.
