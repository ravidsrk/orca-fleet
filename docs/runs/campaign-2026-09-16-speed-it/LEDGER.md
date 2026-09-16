# Ledger — speed-it self-test campaign-2026-09-16-speed-it

RUN: local-single-agent · COORDINATOR: workflow-child · BASE: campaign/speed-it-selftest · FORK_POINT: c46d4b3f3371e41408aed19e54476fa194c20b42 · T0: 2026-09-16T13:06:21Z · SOURCE: SCOPE.md journeys+metric-contract digest=TBD-at-close · WIP: builders=1 reviewers=0

PHASE: DONE

Journey park: J1 residual breach (~223 s over) — cause: suite-wide per-test
process fan-out (1490 hermetic tests; no further sharing-safe hotspot) —
gate: human decision on parallel-runner + CI-sharding infra + guard wiring
(`bin/measure-j1.sh --budget 30` retained unwired; wiring it now would red main).

| task_id | hotspot | BASELINE | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | BEFORE_AFTER | WT_CLEAN | lighting | park | evidence |
|---------|---------|----------|------------|---------|-----|----------|--------|--------------|----------|----------|------|----------|
| H1 | deny_hook class-shared read-only fixture + config-fold | t | t | n/a | n/a | t | t | t | t | lit | | H1-review.txt@3383d06; BEFORE{46.24,47.97,48.08} AFTER{42.39,42.52,42.79} 140/140 OK |
REVIEWED=t = author self-review (instructed-isolation, no independence — see H1-review.txt). MERGED=t = local commit 3383d06 on BASE (no-gh lane).
| no-gh: local-merge (task rules forbid PRs/pushes; fixes land as commits on BASE, promotion PR owed) |

## WIP-curve protocol rows

waves=1 (single-agent sequential run; no Orca dispatch waves — see deviations).
Single-agent lane: no parallel builders/reviewers; throughput/latency cells N/A by construction.
