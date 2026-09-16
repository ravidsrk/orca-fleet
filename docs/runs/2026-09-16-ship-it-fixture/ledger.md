`RUN: ship-it-fixture-2026-09-16 · COORDINATOR: interactive session sage-equinox · BASE: ship/fixture-target-app · FORK_POINT: c46d4b3f3371e41408aed19e54476fa194c20b42 · T0: 2026-09-16 · SOURCE: frozen-spec-candidate SPEC.md (grill round 1 answered; FREEZE gate open) · WIP: builders=0 reviewers=0`

`PHASE: DECOMPOSE` (FREEZE granted by human 2026-09-16 — explicit yes; SPEC.md is the fixed point)

## Unit rows

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| GATE-1 | FREEZE (human gate #1) | t | n/a | n/a | n/a | n/a | n/a | lit | — | SPEC.md FROZEN 2026-09-16 (explicit human yes) |

## Slice ↔ id table (coordinator-owned; no Orca Run — see D1)

| id | slice | deps | worker pack | dispatch |
|---|---|---|---|---|
| S0 | foundation scaffold | — | addy | pending |
| S1 | API + store | S0 | matt | pending |
| S2 | UI + F2 | S1 | matt | pending |
| S3 | seed + F1 + telemetry + staging | S1 | addy | pending |
| S4 | docs + flaws + CI + pending 0003 | S2, S3 | addy | pending |

DAG: S0 → S1 → {S2, S3} → S4. Frontier = {S0}. Merge-chains: `app/main.py`
regions (# S1/# S2/# S3, append-only, coordinator resolves); `alembic/versions/`
(S1 then S4, ordered); `compose.yaml` (S0 skeleton then S3, ordered); CI workflow
(S0 skeleton then S4, ordered). Loop: manual wave (coordinator dispatches,
reviews, merges per slice).

## Deviations

- D1 (dispatch substrate): `orca orchestration run-create` refused
  `no_active_sender_terminal` (plain shell; the one live terminal belongs to a
  foreign run and was not hijacked). Workers dispatch as supervised subagents
  with isolated worktrees; the ledger table above is the DAG of record. Session
  precedent: roadmap units + 2026-09-16 campaign.
- D2 (solo review): single GitHub identity — slice reviews post COMMENTED
  GO/NO-GO (never APPROVE); coordinator merges after CI green (repo DECISIONS
  precedent `review-verdict-form`).
