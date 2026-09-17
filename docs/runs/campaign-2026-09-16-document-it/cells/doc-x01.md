# doc-x01 — cli:runtime/scripts/decisions.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: parser-without-writer origin, reclassification refusal rationale, human-source
rule, committed-state tallies, never-gate trio rationale — all anchored to docstring +
consts. Confidence: high — rationale is in-tree.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block form; no new flags/paths beyond anchors.
- Spec: frozen explanation cell for decisions.py; rationale drawn from
  `runtime/scripts/decisions.py:1-63` + `:81-90`, not invented.
- Test-adequacy: claimcheck GREEN (3 symbol anchors bound); rename
  NEVER_GATE→ALWAYS_GATE RED (nc-doc-x01.txt).

## Anchors

- claimcheck --cell decisions.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x01.txt` (exit 1, file restored).
