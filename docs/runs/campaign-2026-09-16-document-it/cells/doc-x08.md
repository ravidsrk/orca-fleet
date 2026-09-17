# doc-x08 — cli:runtime/scripts/guard_text.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: data-not-authority premise, envelope-always + failed-is-not-data rules,
detection-only normalization, banner defusing, labels-as-evidence. Confidence: high —
rationale is the module's design-rules docstring.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for guard_text.py from
  `runtime/scripts/guard_text.py:1-37`, not invented.
- Test-adequacy: claimcheck GREEN; rename FORGED_BANNER→FAKE_BANNER RED
  (nc-doc-x08.txt).

## Anchors

- claimcheck --cell guard_text.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x08.txt` (exit 1, file restored).
