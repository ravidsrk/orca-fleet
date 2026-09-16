# doc-r13 — cli:runtime/scripts/watchdog.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: four liveness classes with thresholds, snapshot input shape, --dry-run vs
live with transport refusal, rate limits + persisted state, exits 0/1/2.
Confidence: high — docstring + argparse + DEFAULTS read.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; runtime-generated default paths (.orca/...) left
  unbackticked since they need not exist.
- Spec: frozen reference cell for watchdog.py from `runtime/scripts/watchdog.py:1-53`
  + argparse `:420-440` + DEFAULTS `:65-74`. No creep.
- Test-adequacy: claimcheck GREEN; rename --heartbeats→--pulses RED (nc-doc-r13.txt).

## Anchors

- claimcheck --cell watchdog.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r13.txt` (exit 1, file restored).
