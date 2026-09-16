# doc-r10 — cli:runtime/scripts/pm.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: inbox-JSON parser, single-file argument, no flags, structural keepalive skip,
_visible escaping, MESSAGES output shape, exits 0/1/2. Confidence: high — full file
read (146 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; the no-help-flag trap stated in plain words (unbackticked)
  so the flag check cannot false-RED on it.
- Spec: frozen reference cell for pm.py from `runtime/scripts/pm.py:1-21` + main
  `:132-142`. No creep.
- Test-adequacy: claimcheck GREEN; flagless CLI so the rename control moves the
  anchored `tests/test_pm.py` aside → RED (nc-doc-r10.txt), then restores.

## Anchors

- claimcheck --cell pm.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r10.txt` (exit 1, file restored).
