---
name: ship-it
description: >-
  Turn intent or a frozen spec into a released, verified outcome on Orca. Entry is either a
  frozen spec (validate → decompose) or raw intent (grill → freeze → decompose); after freeze
  both enter one canonical pipeline: decompose → build (tested slices) → acceptance review →
  runtime-prove → land → release → observe, stopping at the highest release state you're
  authorized to reach (BUILT / PROMOTION_READY / RELEASED / DEPLOYED_AND_VERIFIED). Use when
  "build and ship this", "spec to shipped product", "ship this feature", or an autonomous
  build-to-release run. Not for closing an existing backlog (that's clean-sweep) or a foggy
  goal that needs charting first (that's map-it).
license: MIT
proof: doctrine-only
compatibility: >-
  HARD dependency: Orca runtime + the orchestration skill (Orca CLI). git + gh. One worker
  playbook pack per worker (mattpocock/skills for grill/tdd, addyosmani for build/verify, gstack
  for review-army/ship) — never two routers in one worker. Deploy tooling + canary surface for
  the RELEASED/DEPLOYED states.
---

# ship-it — intent or spec → a released, verified outcome

You are the **COORDINATOR**. The outcome is a change built, reviewed, verified, and taken as far
down the release state machine as you are authorized to reach — named explicitly, never overclaimed.
You dispatch, verify against authoritative state, and keep the ledger; you do not write code.

Read [ARCHITECTURE.md](../../ARCHITECTURE.md) once. Composes `decide-and-freeze`, `decompose-dag`,
`build-change`, `acceptance-review`, `risk-review`, `runtime-prove`, `release`, `observe` playbooks;
rides `dispatch-lifecycle`, `merge-serialization`, `reviewed-sha-freshness`, `evidence-manifest`,
`gate-classification`, `liveness-resume`, `orca-dag-semantics`, `ledger-contract` runtime policies.
It does not restate them.
Worker TASK pack: exactly one of matt | addy | gstack (grill/tdd=matt, build/verify=addy|matt,
review/ship=gstack) — never co-mount two routers in one worker.

## Terminal states (name the one you reach)

`BUILT` (all units merged to BASE, ancestry-verified) → `PROMOTION_READY` (promotion PR open with a
traceability table) → `RELEASED` (human merged to default) → `DEPLOYED_AND_VERIFIED` (deployed
revision == released SHA, canary green over its window). Stop at the highest state authorization and
deploy availability allow; the manifest names it and what blocks the next.

If units or criteria are parked with human-approved reasons while the rest landed, append
`-WITH-PARKED` to the highest clean state reached (e.g. `BUILT-WITH-PARKED`,
`PROMOTION_READY-WITH-PARKED`). Allowed parks: `needs-human`, `CODE_CLOSED` + `VERIFY_AT_SCALE`
plan, or human-authorized scope exclusion. Never claim a clean terminal when parked work remains in scope.

## Preflight

`orca status --json` running · orchestration on · Orca CLI + orchestration skill available ·
git. **Repo state:**

- real code → foundation fills gaps; tests green at baseline (else you can't tell regressions)
- empty/near-empty git repo → foundation scaffolds
- no git repo → `git init` + minimal README/.gitignore commit on default, **then create a
  GitHub remote** (`gh repo create` private, or push an existing remote) so write preflight can
  run — pure local-only greenfield is not supported for the full PR pipeline

Then `runtime/scripts/preflight.py --base <BASE> --fork-point <ledger-header sha>` green
(BASE ≠ default — dispatch-lifecycle.md; requires `gh` + a visible remote). If `gh` later dies
mid-run, use merge-serialization no-gh local merge (`PR_OPEN=n/a`). Ledger: header + phase
marker + unit boolean flags (ledger-contract.md).

## Pipeline (one canonical path after freeze)

```
ENTRY ─┬─ frozen spec  → VALIDATE (decide-and-freeze: validate branch) → DECOMPOSE
       ├─ intent/draft → GRILL + FREEZE (decide-and-freeze: grill branch, human gate #1) → DECOMPOSE
       └─ map-it handoff (frozen spec + frozen prepared DAG) → VALIDATE the freeze, re-run
          decompose-dag's VERIFY section on the prepared DAG, ADOPT its task ids — skip DECOMPOSE
          (re-decomposing would duplicate or orphan the prepared tasks)
   → DECOMPOSE (decompose-dag: tracer-bullet slices → Orca DAG) — first two routes only
   → BUILD waves (build-change per slice; foundation serializes, slices parallelize)
   → ACCEPTANCE-REVIEW (build-blind, per slice) [+ RISK-REVIEW lens if the slice triggers one]
   → RUNTIME-PROVE (doubt-driven artifact review + drive the real entry point)
   → LAND (merge-serialization) → BUILT
   → RELEASE state machine (release.md): PROMOTION_READY → [human gate #2] → RELEASED
   → DEPLOYED_AND_VERIFIED phase (release.md): observe.md BASELINE captured first, THEN deploy,
     then observe.md's canary loop — the state is claimed only after the window is green
   → REFLECT (readiness note + backlog + OPS/CODE_CLOSED queue under docs/ — ledger-contract.md)
```

Each phase runs its playbook; each worker emits an evidence manifest; the coordinator verifies each
against authoritative state (evidence-manifest.md) before advancing. Unit flags advance only in the
ledger file (`BUILT`…`WT_CLEAN`).

## Convergence proof (this mission's definition of done)

- Every frozen acceptance criterion maps to a passing test in a TRACEABILITY table, verified on the
  BASE head (the integrated whole, not per-slice-only). The denominator is not worker-chosen and it
  is TWO-LEVEL (evidence-manifest.md): each slice manifest binds to ITS OWN task-spec criteria at
  `contract.digest` (so a narrow slice is completable), and the coordinator verifies the UNION of
  slice contracts equals the frozen spec's criterion set — at decompose verification and again
  here. A criterion no slice claimed is unassigned work; a criterion with no passing test is UNMET
  work. Neither is a waiver.
- Every slice: merged PR, ancestry-verified, reviewed-SHA fresh, negative control passing
  (revert-audited on a ≥10% sample by a fresh worker).
- The manifest names the terminal release state with its evidence (merge SHA / deploy revision /
  canary window verdict). Reaching BASE with an open promotion PR is `PROMOTION_READY`, never RELEASED.
- Noticed-but-not-touched adjacent work is a backlog file (scope discipline made visible).
- Every unit row: boolean flags true or an allowed park (`CODE_CLOSED` + `VERIFY_AT_SCALE` plan
  when acceptance is OPS-only — never a silent full close).

## Gates (only these)

- Human gate #1: FREEZE (intent entry only). Human gate #2: PROMOTION to default (one-way,
  gate-classification.md). Lane B product forks: draft both, then human. Everything else is
  mechanical/taste per the classifier (append the DECISIONS log under docs/). Merge ≠ deploy; the
  fleet never self-merges the promotion or deploys.

## Supervision + resume

Stalls → liveness-resume.md WATCH. Compaction pressure → CONTEXT HANDOFF block then RESUME
(ledger-contract.md). Coordinator death → RESUME (scope = ledger coordinator handle + task ids),
cross-verify completed units against git before trusting them.

## Anti-patterns

Fanning the grill to a worker (HITL leak). Building a moving spec (freeze first). Per-slice green
mistaken for done (runtime-prove the integrated whole). Claiming RELEASED at an open PR. Two playbook
routers in one worker TASK.

## Related

`map-it` (chart a foggy goal into a spec this consumes), `clean-sweep` (close an existing set, not
build new), `review-it` (verdict without building), `mission-chaining` (run this as the gated tail
of a harden-it/prove-it sequence).
