# doc-r09 — cli:runtime/scripts/hitl-loop.template.sh × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: copy-and-edit template, step/capture helpers, OBSERVATIONS-not-actions rule,
REPRODUCED-line verdict, bounded --rounds default 3, --dry-run, exits 0/2.
Confidence: high — full file read (60 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; wiring rule (edit between markers only) stated.
- Spec: frozen reference cell for hitl-loop.template.sh from
  `runtime/scripts/hitl-loop.template.sh:1-26` + arg parsing `:28-39`. No creep.
- Test-adequacy: claimcheck GREEN; rename --rounds→--loops RED (nc-doc-r09.txt).

## Anchors

- claimcheck --cell hitl-loop.template.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r09.txt` (exit 1, file restored).
