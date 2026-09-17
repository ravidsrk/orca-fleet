# doc-r16 — config:runtime/watchdog.json × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: 9 keys tabled with values and meanings, tune-without-edits rule, unknown-key
refusal, null-transport refusal. Confidence: high — full JSON + watchdog.py:116-118 read.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: Keys-table form; threshold semantics match watchdog.py class definitions.
- Spec: frozen reference cell for watchdog.json from the registry + consumer
  `runtime/scripts/watchdog.py:13-33,116-118`. Also carries the README one-hop link
  (reachability leg for the whole page). No creep.
- Test-adequacy: claimcheck GREEN; rename wedge_frozen_s→wedge_idle_s RED
  (nc-doc-r16.txt); README:542 links the page (one hop).

## Anchors

- claimcheck --cell watchdog.json → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r16.txt` (exit 1, file restored).
- Reachability: `README.md:542` → docs/runtime-scripts.md.
