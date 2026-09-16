# doc-x12 — cli:runtime/scripts/spawn_worker.sh × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: exit-per-past-mistake rationale, dual-writer rule, typed-refusal branching,
never-force-ready, profile gates, ro-lane exclusion. Confidence: high — rationale is
the header contract.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for spawn_worker.sh from
  `runtime/scripts/spawn_worker.sh:1-80`, not invented.
- Test-adequacy: claimcheck GREEN; rename MARK_READY→FLAG_READY RED (nc-doc-x12.txt).

## Anchors

- claimcheck --cell spawn_worker.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x12.txt` (exit 1, file restored).
