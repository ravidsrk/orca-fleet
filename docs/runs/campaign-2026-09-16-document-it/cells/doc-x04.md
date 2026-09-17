# doc-x04 — cli:runtime/scripts/ed25519.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: stdlib-only vendoring rationale, slow-but-correct scope limit,
checkvalid hardening delta, backend-swap seam. Confidence: high — rationale is the
module docstring.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for ed25519.py from
  `runtime/scripts/ed25519.py:1-21`, not invented.
- Test-adequacy: claimcheck GREEN; rename hashlib→hashmagic RED (nc-doc-x04.txt).

## Anchors

- claimcheck --cell ed25519.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x04.txt` (exit 1, file restored).
