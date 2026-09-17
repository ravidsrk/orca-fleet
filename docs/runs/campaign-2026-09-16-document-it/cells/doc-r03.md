# doc-r03 — cli:runtime/scripts/diff_scope.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: SCOPE_* classifier, 12 flags, union changed-set (committed + worktree +
untracked), shell-safe output + --json, exits 0/2 with three SCOPE_ERROR kinds.
Confidence: high — full file read (308 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; flag table summarized as the 12-name list (full
  path/content rules stay in the docstring — reference points, not duplicates).
- Spec: frozen reference cell for diff_scope.py from `runtime/scripts/diff_scope.py:1-75`
  + argparse `:249-261` + resolve order `:155-168`. No creep.
- Test-adequacy: claimcheck GREEN; rename --strict→--rigid RED (nc-doc-r03.txt).

## Anchors

- claimcheck --cell diff_scope.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r03.txt` (exit 1, file restored).
