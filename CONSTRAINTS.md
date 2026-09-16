# CONSTRAINTS — the orca-fleet quality bar (frozen)

Status: **FROZEN by the human; CI wiring (WIRE) not yet landed.**
This file is the freeze product of the floor-it self-test unpark (phase 1:
CONSTRAINTS). No threshold below moves without a one-way human decision
recorded in docs/DECISIONS.md; the GUARD phase will enforce that mechanically.

- Frozen by: Ravindra (maintainer), 2026-09-16, interactive gate session.
- Freeze source: `campaign/floor-it-selftest` commit `9e574c0b`
  ("docs(floor-it): record FREEZE answers") — Q1 freeze D1–D8 as-written,
  Q2 charter the D9 coverage WIRE unit (line >= 80% on `runtime/scripts` +
  `scripts`, ratchet-only), Q3 confirm D10/D11 parks + D12 fold into D2,
  Q4 confirm the guard surface, Q5 explicit FREEZE yes.
- Proposal measured at: `c46d4b3` (see the parked-run DETECT record).
- CONSTRAINTS committed on: `floor/constraints` from base `10e45f72`
  (origin/main at phase-1 start); measured values below re-verified at base.
- Prove-fires: every enforced dimension was demonstrated RED on a real
  violation and GREEN after revert — see docs/runs/2026-09-16-floor-constraints/PROVE-FIRES.md
  (executed transcripts, not prose). D9 is frozen BELOW the bar; see its row.

## Frozen table (dimension x threshold x tool x gate job x measured)

| ID | Dimension | Threshold (frozen) | Tool (exact command) | CI gate job (WIRE target) | Measured at base | Status |
|---|---|---|---|---|--- |---|
| D1 | suite-green | `unittest` exit 0 (0 failures, 0 errors) | `python3 -m unittest discover -s tests` | validate.yml `gates`: "Run the contract test suite without Gitleaks" | 1490 pass, OK | FROZEN+PROVEN |
| D2 | catalog-valid | `validate.py` exit 0 (21/21 missions, separation holds) | `python3 scripts/validate.py` | validate.yml `gates`: "Validate missions, playbooks, and evals" | 21/21 ok | FROZEN+PROVEN |
| D3 | lint-clean | `ruff check` 0 findings on `scripts runtime/scripts tests bench demo` | `ruff check scripts runtime/scripts tests bench demo` (select E9,F63,F7,F82 per ruff.toml) | validate.yml `gates`: "Ruff (syntax / undefined names)" | 0 findings | FROZEN+PROVEN |
| D4 | secrets-clean | `gitleaks detect` 0 unwaived leaks | `gitleaks detect --redact --no-banner --source .` (pinned 8.30.1) | validate.yml `gates`: "Secret scan (gitleaks, pinned)" | exit 0 on main history; 3 waived fingerprints | FROZEN+PROVEN |
| D5 | routing-eval | score >= 1.0 | `python3 scripts/eval.py run --suite routing --threshold 1.0` | validate.yml `gates`: "Routing eval gate (description-based router)" | 94/94 (100%) | FROZEN+PROVEN |
| D6 | proof-honesty | `proof_status.py --check` AND `run_report.py` exit 0 | both scripts (see row notes) | validate.yml `gates`: "Check proof-evidence honesty" + "Proof tiers bind to artifacts, not filenames" | exit 0; 19 doctrine-only / 2 self-run; 2 bound | FROZEN+PROVEN |
| D7 | bundle-self-contained | `bundle.py --check` exit 0 | `python3 scripts/bundle.py --check` | validate.yml `gates`: "Bundle builds self-contained missions" | 21/21 | FROZEN+PROVEN |
| D8 | verifier-soundness | vf-bench gate PASS: false-done 0, skipped 0 | `python3 bench/vf-bench/gate.py` | validate.yml job `vfbench` | false-done 0/20, valid 3/3, skipped 0 | FROZEN+PROVEN |
| D9 | coverage | line >= 80% on `runtime/scripts` + `scripts`, ratchet-only | `coverage run -m unittest discover -s tests` then `coverage report` (config: .coveragerc) | NEW validate.yml step (WIRE): hash-pinned coverage install + run + report | **75% (6058 stmts, 1541 missed) — BELOW BAR** | FROZEN-BELOW-BAR |

## Row notes (part of the freeze)

- D3: measured locally with ruff 0.16.7; CI installs ruff 0.16.5 from the
  hashed `.github/ci-tools.lock`. Same `ruff.toml` select either way; the
  fires-proof (F821 undefined name) holds under both. WIRE keeps the versions
  aligned or records the skew — it does not silently re-pin.
- D4: `detect` scans git history across refs. Local checkouts that share an
  object store with unpushed campaign branches scan those too; the gate signal
  is main-history-only (exit 0, corroborated by CI). The 3 `.gitleaksignore`
  fingerprints waive only the listed credential-shaped fixtures in
  tests/test_decisions.py — a planted credential in that same file is still
  caught (proven in PROVE-FIRES.md).
- D5: the `ROUTING_MIN_SCORE = 1.0` floor in tests/test_evals.py mirrors this
  threshold in the suite; the two move together or not at all (guard surface).
- D6: two halves, both required. `proof_status.py --check` fails a tier above
  doctrine-only with missing/unresolvable evidence; `run_report.py` fails a
  binding that no longer re-hashes (it re-derives from git objects at
  `inventory_at`, so worktree-only edits to a bound report correctly do NOT
  trip it — demonstrated in PROVE-FIRES.md).
- D8: corpus pinned at vf-bench@0.1 (VERSION + CANARY GUID + traps digest).
  RED means fix the verifier, never the corpus; a corpus change bumps the pins
  in the same PR, explicitly.
- D9: the human froze 80% against an UNMEASURED dimension (no runner existed at
  proposal time). First measurement: 75%. The threshold stands as frozen —
  lowering it to the measurement would be editing the bar to fit the repo, a
  one-way change this phase refuses to make unilaterally. The WIRE unit lifts
  coverage to >= 80% with real tests, then re-proves GREEN plus the canary-PR
  RED. `ratchet-only`: once green, the number moves up only. `fail_under = 80`
  in .coveragerc mirrors this row; the guard must cover it (flagged for GUARD).
- D12 folded into D2: the `agentskills validate` CI step stays as
  defense-in-depth under catalog-valid; it is not a separate dimension and
  carries no separate threshold.

## Parked (not-applicable, human-confirmed)

| ID | Dimension | Disposition | Human gate |
|---|---|---|---|
| D10 | perf-budget | PARKED: no repo-wide perf surface; vf-bench duration is a gate cost, not a product budget. No threshold, no tool — a vacuous check is refused. | perf-sensitive changes reviewed case-by-case |
| D11 | a11y | PARKED: no UI/render surface in this repo. | none needed; re-open if a UI ships |

## Guard surface (frozen, Q4-confirmed)

Any diff touching these fails CI without a recorded DECISIONS waiver
(`floor-waiver:<rule>:<path>` grant): the numbers in this file,
`.gitleaksignore`, the `ruff.toml` select, `ROUTING_MIN_SCORE`, the eval suite
(evals/routing.json), the vf-bench corpus (traps + pins), and — flagged for the
GUARD phase, mirroring this file's D9 number — the `.coveragerc` fail_under.
Waivers live in docs/DECISIONS.md.

## Change policy

Thresholds move by one-way human decision only, recorded in docs/DECISIONS.md
with the freeze entry named. Tightening is a new one-way decision, never
mechanical. D9 is ratchet-only. A dimension dropped for convenience is a
finding, not an edit: the table never shrinks mid-run.
