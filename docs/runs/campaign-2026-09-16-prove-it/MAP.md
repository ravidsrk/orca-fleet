# MAP — critical surface, prove-it campaign self-test 2026-09-16

Method: `uvx coverage run --source=scripts,runtime/scripts -m unittest discover -s tests`
at `c46d4b3f` (1490 tests OK, 279-318s), plus call-graph/test-file inspection to
separate genuinely-untested branches from subprocess-exercised ones (coverage.py
traces only the parent process; CLI tests that shell out read as 0% — see below).

## Totals

74% line coverage (6142 statements, 1625 missed). Full report:
`map-coverage-missing.txt`; machine-readable: `map-coverage.json`.

## Surface triage (coverage × call-graph × test inspection)

- `runtime/scripts/guard_text.py` 0% (84 missed) — EXCLUDED as tested: 32 contract
  tests in `tests/test_guard_text.py` exercise every documented property through
  the real CLI in subprocesses (traced 0% is a measurement artifact, not a gap).
  Same artifact class covers large missed ranges in `decisions.py` (51 tests,
  CLI legs via subprocess), `preflight.py`, `evidence-run.py`, `egress.py`,
  `floor_guard.py`, `watchdog.py`, `inventory.py` — each needs per-line
  test-file inspection before any line is claimed untested. Not this wave.
- `runtime/scripts/verify.py` 89% (132 missed) — the oracle every mission's
  evidence depends on; imported directly by `tests/test_verify.py`, so traced
  coverage here is truthful. The missed set includes the whole
  `check_oracle_scope` tail below PF-2's kind gate (frozen by the 2026-09-16
  self-run): lines 997 (coordinates required), 1003 (positive-int coords),
  1005 (target must exist), 1008 (diff error), 1013 (characterization must
  change a test), 1015 (documentation prose-only), 1019 (hand-mutant required),
  1024 (mutant path-set match), plus fail-closed diff-grammar raises
  (1037-1049, 1076-1093). A grep over `tests/test_verify.py` confirms no test
  asserts any of those refusal messages — this tail is the confirmed untested
  load-bearing surface.
- `runtime/scripts/run_report.py` 92% (38 missed), `scripts/validate.py` 78%,
  `scripts/eval.py` 80% — noted, not triaged line-by-line this wave.

## Frozen scope (single criterion)

PF-3: `verify.py` lines 1012-1013 — the characterization must-change-a-test
gate. Rationale: it enforces the lane's core invariant (evidence-manifest.md
§1: characterization changes tests/prose only — a characterization unit MUST
change a test); a broken gate admits production-only changes to the waived-review
lane this run itself rides — the load-bearing uncovered branch of that lane,
mirroring the prior run's PF-2 rationale one gate up. Seam (design-twice):
direct unit call to `check_oracle_scope` in hermetic `RepoCase` repos — the
PF-2 precedent; no interface fork exists, so no triple-design fan-out (that
playbook's Lane-B machinery would be ceremony here).

Siblings (997, 1003, 1005, 1008, 1015, 1019-as-target, 1024, diff-grammar
raises) are named future work, not silent scope — each is one more
single-criterion wave. The 1019 refusal message serves this wave only as the
pass-through expectation (the gate-below, as PF-2's pair gate did), asserted
but not the criterion.
