# doc-x10 — cli:runtime/scripts/pm.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: stderr-keepalive rationale, structural-not-line-filter skip, untrusted-text
escaping with invisible-category coverage, escape-not-strip rule. Confidence: high —
rationale is the module header.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for pm.py from `runtime/scripts/pm.py:1-21` + `:36-64`,
  not invented.
- Test-adequacy: claimcheck GREEN; rename _INVISIBLE→_HIDDEN RED (nc-doc-x10.txt).

## Anchors

- claimcheck --cell pm.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x10.txt` (exit 1, file restored).
