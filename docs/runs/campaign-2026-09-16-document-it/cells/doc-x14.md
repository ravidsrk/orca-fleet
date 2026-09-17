# doc-x14 — cli:runtime/scripts/wtree.sh × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: three-properties-vs-HEAD-tree rationale, temp-index rationale, stat-cache
seed with racy-index guard and slow fallback. Confidence: high — rationale is the
header comment.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for wtree.sh from `runtime/scripts/wtree.sh:1-30`,
  not invented.
- Test-adequacy: claimcheck GREEN; rename TMPIDX→SCRATCHIDX RED (nc-doc-x14.txt).

## Anchors

- claimcheck --cell wtree.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x14.txt` (exit 1, file restored).
