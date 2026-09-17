# doc-x06 — cli:runtime/scripts/floor_guard.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: green-build-invisible rationale, waiver-identity-via-DECISIONS rationale,
no-prose-parsing rule, redaction-first reporting, off-worker wiring. Confidence: high —
rationale is the module docstring.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for floor_guard.py from
  `runtime/scripts/floor_guard.py:1-68` + waiver code `:348-362`, not invented.
- Test-adequacy: claimcheck GREEN; rename _WAIVER_ID_PREFIX→_EXCUSE_PREFIX RED
  (nc-doc-x06.txt).

## Anchors

- claimcheck --cell floor_guard.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x06.txt` (exit 1, file restored).
