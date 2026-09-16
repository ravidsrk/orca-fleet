# doc-r04 — cli:runtime/scripts/ed25519.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: vendored Ed25519 lib, three-function API (publickey/signature/checkvalid),
RFC 8032 vectors, hardening notes, not-constant-time scope limit, the two consumers.
Confidence: high — full file read (159 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: API-line form instead of Flags (import-only); documented honestly.
- Spec: frozen reference cell for ed25519.py from `runtime/scripts/ed25519.py:1-21` +
  defs `:121-159`. No creep.
- Test-adequacy: claimcheck GREEN; rename `def checkvalid(`→`def qcheck(` RED
  (nc-doc-r04.txt).

## Anchors

- claimcheck --cell ed25519.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r04.txt` (exit 1, file restored).
