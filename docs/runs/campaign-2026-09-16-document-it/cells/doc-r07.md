# doc-r07 — cli:runtime/scripts/gate-batch.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: typed JSON store + rendered .md view, nine subcommands, owed→terminal-once
state machine, G-ids, --run/--file targeting, exits 0/2. Confidence: high —
docstring + schema consts + full argparse table read.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; placeholder store path unbackticked (HTML entity) so the
  existence check does not false-RED on a path with a placeholder in it.
- Spec: frozen reference cell for gate-batch.py from
  `runtime/scripts/gate-batch.py:1-20` + argparse `:393-540`. All 20 flags named; no
  creep.
- Test-adequacy: claimcheck GREEN; rename --question-file→--qfile RED (nc-doc-r07.txt).

## Anchors

- claimcheck --cell gate-batch.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r07.txt` (exit 1, file restored).
