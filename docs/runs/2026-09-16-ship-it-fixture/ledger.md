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
| S1 | API + store | S0 | matt | MERGED #447 @ 310b2259 (C1 2bee02fa reviewed GO; coord P1 fix 7a1ef399) |
| S2 | UI + F2 | S1 | matt | MERGED #448 @ 216076eb (reviewed 2cc7e0ad GO) |
| S3 | seed + F1 + telemetry + staging | S1 | addy | MERGED #449 @ 2aa870c7 (C1 e73d1b99 GO; coord P1/P2 fixes + dep-union merge) |
| S4 | docs + flaws + CI + pending 0003 | S2, S3 | addy | dispatched (isolated wtree) |

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
- D4 (S1 scope+NC executed-control): (a) `SN-ACn` ids do not match CRIT_ID_RE
  (digit-before-dash), so the taskspec-as-contract yields zero ids — coordinator
  verified S1-AC1..3 ↔ checks mapping manually and re-executed all green.
  S2–S4 close via coordinator-committed JSON contracts (criterion_ids arrays,
  the preferred form) instead. (b) S1's NC diff has bare-empty context lines,
  which verify.py's hunk grammar rejects though git applies it; coordinator
  replayed the mutant manually: RED 3 failed/13 passed, GREEN 16 passed on
  restore. S2–S4 workers instructed: space-prefix every context line in NC diffs.
- D5 (S2 E1/E2/E3 rulings): E1 route collision — S2's runtime router surgery
  REJECTED; coordinator reordered includes statically (pages before API) on the
  slice branch (2cc7e0ad), S1 lines byte-identical, full suite re-verified 41
  green; reviewed_sha = 2cc7e0ad (covers C1 + reorder). E2 detail URL —
  ACCEPTED: `/issues/{id}` JSON smoke satisfies S2-AC2's letter, HTML detail at
  `/issues/{id}/view` (SPEC pins no detail URL). E3 pyproject deps (jinja2,
  python-multipart) — ACCEPTED as necessary extras; S3 also touched pyproject
  (structlog) → coordinator union-merge + re-run.
