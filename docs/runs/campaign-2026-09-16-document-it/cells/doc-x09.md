# doc-x09 — cli:runtime/scripts/hitl-loop.template.sh × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: blind-agent/lit-human split, observations-not-actions, verdict-line-not-exit
rationale, bounded-loop-with-checkpoint rationale. Confidence: high — rationale is the
template header.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for hitl-loop.template.sh from
  `runtime/scripts/hitl-loop.template.sh:1-26`, not invented.
- Test-adequacy: claimcheck GREEN; rename REPRODUCED→CONFIRMED RED (nc-doc-x09.txt).

## Anchors

- claimcheck --cell hitl-loop.template.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x09.txt` (exit 1, file restored).
