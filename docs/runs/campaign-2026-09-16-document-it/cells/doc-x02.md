# doc-x02 — cli:runtime/scripts/deny-hook.sh × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: below-the-model rationale, fail-closed polarity, load-bearing nesting,
deny-vs-ask split, symlink-chain boundary resolver. Confidence: high — rationale is
the header contract.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for deny-hook.sh from
  `runtime/scripts/deny-hook.sh:1-80`, not invented.
- Test-adequacy: claimcheck GREEN; rename permissionDecision→verdictChoice RED
  (nc-doc-x02.txt).

## Anchors

- claimcheck --cell deny-hook.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x02.txt` (exit 1, file restored).
