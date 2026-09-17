# doc-x16 — config:runtime/watchdog.json × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: field-generalized values rationale with the two named cases,
tune-without-edits rule, single-nudge-cap rationale. Confidence: high — rationale is
the _about provenance note plus watchdog.py escalation logic.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only; "field-shaped, not derived" stated honestly.
- Spec: frozen explanation cell for watchdog.json from `runtime/watchdog.json:_about` +
  `runtime/scripts/watchdog.py:19-27`, not invented.
- Test-adequacy: claimcheck GREEN; rename max_nudges_per_dispatch→max_pokes RED with
  both ANCHOR and KEY legs firing (nc-doc-x16.txt).

## Anchors

- claimcheck --cell watchdog.json → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x16.txt` (exit 1, file restored).
