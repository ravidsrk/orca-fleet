`RUN: ship-it-fixture-2026-09-16 · COORDINATOR: interactive session sage-equinox · BASE: ship/fixture-target-app · FORK_POINT: c46d4b3f3371e41408aed19e54476fa194c20b42 · T0: 2026-09-16 · SOURCE: frozen-spec-candidate SPEC.md (grill round 1 answered; FREEZE gate open) · WIP: builders=0 reviewers=0`

`PHASE: DECOMPOSE` (FREEZE granted by human 2026-09-16 — explicit yes; SPEC.md is the fixed point)

## Unit rows

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| GATE-1 | FREEZE (human gate #1) | t | n/a | n/a | n/a | n/a | n/a | lit | — | SPEC.md FROZEN 2026-09-16 (explicit human yes) |

## Slice ↔ id table (coordinator-owned; no Orca Run — see D1)

| id | slice | deps | worker pack | dispatch |
|---|---|---|---|---|
| S0 | foundation scaffold | — | addy | MERGED #446 @ 9890c610 (C1 b75bc019 reviewed GO; coord fix d4103a61) |
| S1 | API + store | S0 | matt | dispatched (isolated wtree) |
| S2 | UI + F2 | S1 | matt | pending |
| S3 | seed + F1 + telemetry + staging | S1 | addy | pending |
| S4 | docs + flaws + CI + pending 0003 | S2, S3 | addy | pending |

DAG: S0 → S1 → {S2, S3} → S4. Frontier = {S0}. Merge-chains: `app/main.py`
regions (# S1/# S2/# S3, append-only, coordinator resolves); `alembic/versions/`
(S1 then S4, ordered); `compose.yaml` (S0 skeleton then S3, ordered); CI workflow
(S0 skeleton then S4, ordered); `app/routers/issues.py::list_issues` query shape
(S1 writes straightforward, S3 owns the F1 N+1 — skeptic note, S1 must not
preempt). Loop: manual wave (coordinator dispatches, reviews, merges per slice).

Plan skeptic (fresh worker, 2026-09-16): SKEPTIC-GO — no orphans (15/15 AC
mapped), no gold, order correct, no stubs. Two non-blocking notes, both applied
(S4 checklist item 5; S1/S3 list-endpoint handoff).

## Deviations

- D1 (dispatch substrate): `orca orchestration run-create` refused
  `no_active_sender_terminal` (plain shell; the one live terminal belongs to a
  foreign run and was not hijacked). Workers dispatch as supervised subagents
  with isolated worktrees; the ledger table above is the DAG of record. Session
  precedent: roadmap units + 2026-09-16 campaign.
- D2 (solo review): single GitHub identity — slice reviews post COMMENTED
  GO/NO-GO (never APPROVE); coordinator merges after CI green (repo DECISIONS
  precedent `review-verdict-form`).
- D3 (S0 scope executed-control): taskspec shipped without machine-readable
  criterion ids (coordinator authoring miss), so verify.py's scope leg cannot
  pass on S0 (denominator-shape mismatch, NOT a worker scope cut). Coordinator
  verified the mapping manually (S0-AC1→check1, AC2→check2, AC3→checks3+4),
  re-executed all 4 checks green in clean worktrees at C1/C2, and replayed the
  NC via verify.py (all other legs pass). S1–S4 specs amended with `## Criteria`
  blocks before dispatch; their scope legs run unmodified.
