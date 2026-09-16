# doc-x13 — cli:runtime/scripts/watchdog.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: hand-handled origin, mechanized-vs-decision split, presence-not-absence
wedging, settled-to-resume split, tune-without-edits, anti-flap limits.
Confidence: high — rationale is the module docstring.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for watchdog.py from
  `runtime/scripts/watchdog.py:1-53` + `:61-80`, not invented.
- Test-adequacy: claimcheck GREEN; rename SETTLED→FINISHED RED (nc-doc-x13.txt).

## Anchors

- claimcheck --cell watchdog.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x13.txt` (exit 1, file restored).
