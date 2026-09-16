# doc-x05 — cli:runtime/scripts/egress.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: produced-vs-sent halves, content-free rationale, chain-proves-continuity
limit (#312), off-writer anchor, observability-not-control threat model.
Confidence: high — rationale is the module docstring.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for egress.py from
  `runtime/scripts/egress.py:1-47`, not invented.
- Test-adequacy: claimcheck GREEN; rename head_digest→tip_digest RED (nc-doc-x05.txt).

## Anchors

- claimcheck --cell egress.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x05.txt` (exit 1, file restored).
