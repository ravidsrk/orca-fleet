# Frozen execution map (freeze-PREPARED; human sign-off parked as D-0)

G-09 field-proof completion: advance all 19 doctrine-only missions to a bound proof tier.
Source tree: orca-fleet @ `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip, 2026-09-16).
Planning branch: `campaign/map-it-selftest` (this run; no PR per campaign rules — deviation recorded).

## Objectives

O-1. Every doctrine-only mission has a run card (target, tier, terminal, gates, blockers) a
  consumer can execute without re-grilling.
O-2. Runs order into waves: in-catalog self-runs before external selections (premise P-2,
  pending D-19).
O-3. Every human gate is named up front with its ticket (D-0..D-20, T-1..T-3); nothing that
  needs a human is silently agent-decided.
O-4. The prepared DAG verifies mechanically and ships with a task-id ↔ mission table.

## Acceptance criteria (per run card; identical bar, F-2)

Each mission's proof run closes at its named terminal AND binds: `RUN:` header, manifest in
the run's own `docs/runs/<date>-<mission>…/` dir, pasted `verify.py … --manifest` invocation
+ exit, inventory re-hash at inventory_at with the graded manifest hashed, `validate.py` +
`tests/` + `proof_status --check` green, frontmatter `proof:`/`proof_evidence:` set.
A terminal without binding is history, not a tier (per `docs/runs/README.md`).

## Run cards (9 self-run-first, 10 selection-gated)

Self-run wave (target exists in-catalog; ordered by blocker weight, lightest first):

| # | Mission | Target (in-catalog) | Tier | Terminal | Human gate |
|---|---|---|---|---|---|
| 1 | pin-it | runtime/*.md + scripts/ vs installed Orca | self-run | PINNED (-WITH-PARKED) | D-20 timing; T-1 paid-trust budget |
| 2 | floor-it | suite + validate.py + ruff + badges | self-run | FLOORED | D-13 freeze-gate approach |
| 3 | reshape-it | churn-hot modules (verify.py / validate.py) | self-run | RESHAPED | D-14 CONFIRM-SURFACE |
| 4 | harden-it | verify.py, dispatch-sign.py, verify-gate.sh | self-run | CLEAN | D-15 PoC-routing gate |
| 5 | speed-it | catalog-gates journey | self-run | WITHIN-BUDGET | D-12 budget declaration |
| 6 | document-it | runtime/scripts/ zero-coverage cells | self-run | DOCUMENTED | D-17 frozen surface |
| 7 | attest-it | catalog vs agentskills.io spec @ digest | self-run | CONFORMANT (-WITH-GAPS) | D-18 frozen digest |
| 8 | ship-it | next mutating slice here | self-run | BUILT min | D-16 lane (2nd identity vs executed-control) |
| 9 | map-it | this self-test's successor: next foggy epic here | self-run | MAPPED | D-1 scope (this map is doctrine-only: campaign dir binds no tier) |

Selection-gated wave (each opens with a research-brief slate unit at run time, then the run):

| # | Mission | Selection ticket | Tier | Terminal |
|---|---|---|---|---|
| 10 | access-it | D-2 target repo | external-run | CONFORMANT (-WITH-MANUAL-PARKED) |
| 11 | deflake-it | D-3 flaky suite | external-run | STABLE |
| 12 | modernize-it | D-4 lockfile repo | external-run | CURRENT |
| 13 | field-test-it | D-5 app + T-2 device | external-run | FIELD-PROVEN |
| 14 | migrate-it | D-6 live-migration repo | external-run | MIGRATED |
| 15 | oncall-it | D-7 staging + T-3 alerts | external-run | OPERABLE (-WITH-PARKED) |
| 16 | oss-contribute | D-8 upstream tracker | external-run | CONTRIBUTED (-WITH-PARKED) |
| 17 | review-it | D-9 live PR | external-run | NO-GO / GO |
| 18 | root-cause | D-10 live bug | self/external | DIAGNOSED |
| 19 | absorb-it | D-11 queue | external-run | ABSORBED (-WITH-PARKED) |

Trigger-gated (no polling; run when the trigger fires): review-it (live PR), root-cause
(live bug), absorb-it (queue exists). If D-1 phases scope, wave 1 = cards 1–9.

## Boundaries (explicit NOT-in-scope)

- No production code is written by any map ticket (map-it produces decisions, not deliverables).
- No external target is selected by the fleet (D-2..D-11 are human calls; slates inform, never pick).
- No proof-tier advance is claimed by THIS run (campaign dir is not a bindable run dir; map-it stays doctrine-only).
- No mission-chain dispatch (degraded until #441–#444 close; each card is directly consumable).
- No re-grill by consumers: ship-it adopts cards + DAG unchanged (re-decomposing orphans task ids).

## Test strategy

Machine-verified per run card (the F-2 bar): binding audit via `run_report.py`, inventory
re-hash via `inventory.py check --at`, verifier transcript present, `proof_status --check`
tier flip. No human taste gate stands between a run's evidence and its tier — the gates are
all up front (D/T tickets).

## Seam list (highest seam first; decided before this spec)

1. Binding-audit seam (`run_report.py` + `inventory.py`) — the single highest seam: every
   card's done-ness reduces to it.
2. Unit-verifier seam (`verify.py` transcript per run) — supports seam 1, never replaces it.
3. Tier-flip seam (`proof_status --check`) — the catalog-side reflection of seam 1.

## Ordering

Wave 1 (cards 1–9) serial-per-mission, parallel-across-missions up to attention-budget caps;
wave 2 (cards 10–19) starts per-mission when its selection ticket resolves — selections are
independent, so wave 2 is a fan, not a sequence. Trigger-gated cards wait regardless of wave.
DAG foundation = per-mission research-slate units (wave 2) + gate resolutions; slices = runs.

## Constraints

- C-1 (#441–#444): no inter-mission promotion lane; consume per-mission, not chained.
- C-2: pin-it proof timing follows D-20 (now vs #427 cadence 2026-12-16).
- C-3: spawned/headless sessions park every D/T ticket; no agent-side resolution is valid.

## Review report (plan-review — TERMINAL section; coordinator-run, see deviation DV-2)

Lenses (in order; expectation written before each read):

- Scope — expectation: a strong plan names the right problem, collapses proxies, maps
  already-solved sub-problems, states premises. Status: RAN. Findings: (S-1) G-09 IS the
  right denominator (validator-enforced tiers, machine-checked bar — no proxy); (S-2)
  nothing-to-do case is real pain, not hypothetical (19/21 missions checkable-claimless);
  (S-3) already-solved: clean-sweep + prove-it tiers are mapped, not re-planned; delivery
  path is per-mission direct consumption (C-1), explicitly deferred chaining. Premises P-1..P-4
  emitted (ledger); agreement parked (Q-0).
- Design — SKIPPED: the plan changes no user-facing surface (planning artifact).
- DX — expectation: a strong plan's handoff is consumable without re-derivation. Status: RAN.
  Findings: (X-1) run cards carry target+tier+terminal+gate — consumable; (X-2) task-id ↔
  mission table ships with the DAG (O-4). No DX blockers.
- Engineering (LAST, on the amended plan) — expectation: architecture, data flow, edges,
  failure modes, test strategy. Status: RAN. Findings: (E-1) DAG edges are per-mission
  independent (fan) except wave-2 slate→run deps — no cycles by construction, verified at
  prepare; (E-2) failure mode = parked selection stalls one card, never the wave (fan
  isolation); (E-3) test strategy is the machine bar (F-2), no taste oracle. Amendment
  applied: trigger-gated cards explicitly wait (was implicit).

Alternatives (mandatory; recommendation tied to O-1..O-4):

- Minimal (fewest runs, ships signal soonest): wave-1 only (cards 1–9); wave 2 unticketed
  until a selection lands. Effort: 9 runs. Risk: G-09 stays open longest. Reuses: in-catalog
  targets only. RECOMMENDED IF D-1 answers "phased".
- Ideal (best long-term trajectory): all 19 ticketed now (this plan); selections resolve
  async, trigger-gated wait. Effort: 19 runs over time. Risk: ticket maintenance. Reuses:
  field-proof plan as the card source. RECOMMENDED IF D-1 answers "all-19" (default).
- Lateral (trigger-only): ticket nothing; run each mission only when its natural trigger
  fires. Effort: least planning. Risk: external missions never trigger; no DAG to consume.
  REJECTED: fails O-1/O-4 (no consumable map).

Decisions classified (gate-classification): S-1/S-2/S-3, X-1/X-2, E-1/E-2/E-3 mechanical
(coordinator-taken, logged); scope/ordering/selections = queued human tickets (D/T set).
USER CHALLENGES: none — the review follows the maintainer-authored field-proof plan and
challenges no stated human direction. Urgency interrupts: none.

VERDICT: PLAN SOUND, PENDING HUMAN GATES (D-0..D-20, T-1..T-3, P-1..P-4)

Unresolved decisions: D-0 (freeze sign-off), D-1..D-20, T-1..T-3 — all queued in
`handoff-questionnaire.md` (one gate, Q-0..Q-21). NO OTHER UNRESOLVED DECISIONS beyond that block.
