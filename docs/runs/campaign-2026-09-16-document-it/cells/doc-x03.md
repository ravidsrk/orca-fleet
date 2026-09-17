# doc-x03 — cli:runtime/scripts/diff_scope.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: silence-vs-clean rationale, union changed-set rationale, partial-match
information-not-failure tradeoff with --strict opt-in. Confidence: high — rationale is
the docstring plus the #314 comment.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; reuses the real `--strict` flag (bound, no false-RED).
- Spec: frozen explanation cell for diff_scope.py from
  `runtime/scripts/diff_scope.py:1-15` + `:285-292`, not invented.
- Test-adequacy: claimcheck GREEN; rename ScopeError→ScopeFault RED (nc-doc-x03.txt).

## Anchors

- claimcheck --cell diff_scope.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x03.txt` (exit 1, file restored).
