# doc-r05 — cli:runtime/scripts/egress.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: hash-chained JSONL receipts, content-free record shape, write/verify/grants,
0600 ledger, --expect-head anchor, exits 0/2/3, dormant-until-called status note.
Confidence: high — docstring + argparse + write/verify paths read.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; status caveat carried verbatim in spirit (not oversold).
- Spec: frozen reference cell for egress.py from `runtime/scripts/egress.py:1-73` +
  argparse `:313-342`. No creep.
- Test-adequacy: claimcheck GREEN; rename --payload-class→--kind RED (nc-doc-r05.txt).

## Anchors

- claimcheck --cell egress.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r05.txt` (exit 1, file restored).
