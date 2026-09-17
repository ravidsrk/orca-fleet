# doc-r02 — cli:runtime/scripts/deny-hook.sh × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: PreToolUse guard, stdin event JSON → stdout decision object, HIGH-tier deny
list (destructive rm, default-branch force-push/deletion, orchestration reset),
Never-list ask, worktree boundary via ORCA_UNIT_WORKTREE, exits always 0, --settings
registration printer. Confidence: high — header contract read first.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: page template kept; no secrets; no matched text quoted (redaction-first
  spirit — only shapes named).
- Spec: frozen reference cell for deny-hook.sh. Claims drawn from
  `runtime/scripts/deny-hook.sh:1-80` + usage `:101-148`. No how-to creep.
- Test-adequacy: claimcheck GREEN; rename --settings→--opts RED (nc-doc-r02.txt).

## Anchors

- claimcheck --cell deny-hook.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r02.txt` (exit 1, file restored).
