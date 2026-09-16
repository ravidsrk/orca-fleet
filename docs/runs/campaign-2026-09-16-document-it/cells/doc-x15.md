# doc-x15 — config:runtime/one-way-doors.json × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: single-ownership-after-drift rationale, per-door irreversibility whys,
unregistered-wording net rationale, rewording-cannot-reclassify enforcement.
Confidence: high — rationale is the registry note plus per-door why fields.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only; no invented doors.
- Spec: frozen explanation cell for one-way-doors.json from the registry note + door
  `why` fields + decisions.py enforcement, not invented.
- Test-adequacy: claimcheck GREEN; rename live-credentials→live-tokens RED with both
  the ANCHOR and the KEY legs firing (nc-doc-x15.txt).

## Anchors

- claimcheck --cell one-way-doors.json → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x15.txt` (exit 1, file restored).
