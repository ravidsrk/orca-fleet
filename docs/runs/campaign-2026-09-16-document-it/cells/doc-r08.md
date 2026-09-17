# doc-r08 — cli:runtime/scripts/guard_text.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: stdin-or---fetch envelope writer, four sources, five label families, NFKC
detection-only normalization, banner defusing, exits 0/2/3, no-round-trip rule.
Confidence: high — full file read (217 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; label families named without quoting the full regexes.
- Spec: frozen reference cell for guard_text.py from
  `runtime/scripts/guard_text.py:1-57` + argparse `:184-195`. No creep.
- Test-adequacy: claimcheck GREEN; rename --timeout→--pause RED (nc-doc-r08.txt).

## Anchors

- claimcheck --cell guard_text.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r08.txt` (exit 1, file restored).
