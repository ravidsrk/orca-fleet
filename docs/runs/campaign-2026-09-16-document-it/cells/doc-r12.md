# doc-r12 — cli:runtime/scripts/spawn_worker.sh × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: two lanes, 9-agent roster with claude default, ro/rw/danger profiles with
env gates, doctor-transcript handoff, six exit codes with inspect/stop rules.
Confidence: high — header contract + arg parsing + roster gate + exit sites read.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; agent default (`claude`) and effort default (`xhigh`)
  verified at `:151`, not taken from the header alone.
- Spec: frozen reference cell for spawn_worker.sh from
  `runtime/scripts/spawn_worker.sh:1-80` + roster `:172-179` + exit 5 `:683-684`.
  No creep.
- Test-adequacy: claimcheck GREEN (source-anchored — the script has no --help);
  rename --mark-ready→--ready2 RED (nc-doc-r12.txt).

## Anchors

- claimcheck --cell spawn_worker.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r12.txt` (exit 1, file restored).
