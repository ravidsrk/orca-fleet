# doc-r06 — cli:runtime/scripts/floor_guard.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: six rules named, waiver-via-DECISIONS shape, --base/--constraints/--waivers/
--repo/--quiet, off-worker wiring, exits 0/1/2. Confidence: high — docstring + rule
tables + argparse read.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; CONSTRAINTS.md default left unbackticked (file need not
  exist — the check would false-RED on a backticked path).
- Spec: frozen reference cell for floor_guard.py from
  `runtime/scripts/floor_guard.py:1-68` + argparse `:452-460` + base order `:159-167`
  (verified, not assumed from diff_scope). No creep.
- Test-adequacy: claimcheck GREEN; rename --constraints→--limits RED (nc-doc-r06.txt).

## Anchors

- claimcheck --cell floor_guard.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r06.txt` (exit 1, file restored).
