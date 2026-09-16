# floor-it self-test ledger — campaign-2026-09-16-floor-it

RUN: - (run-create refused: no_active_sender_terminal — this shell is not an Orca-managed terminal; zero dispatches, coordinator-only) · COORDINATOR: cli (sandbox shell, no Orca terminal handle) · BASE: campaign/floor-it-selftest · FORK_POINT: c46d4b3f3371e41408aed19e54476fa194c20b42 · T0: 2026-09-16T12:26:37Z · SOURCE: - (no frozen CONSTRAINTS; freeze parked headless, proposal only) · WIP: builders=0 reviewers=0

PHASE: FREEZE (proposal published 2026-09-16; run PARKED at the one-way human gate — no phase re-opens)

Target: orca-fleet itself at origin/main tip c46d4b3 (Merge PR #445).
Mission: floor-it (skills/floor-it/SKILL.md). Session: headless/spawned → FREEZE is human-only; the run PARKS at the freeze per gate-classification (one-way, never auto-resolved).
Worker TASK pack: none dispatched (park precedes WIRE; no pack mounted, none co-mounted).

## Dimension rows (floor-it canonical row shape)

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| (no units dispatched — freeze parked before WIRE; dimensions live in FREEZE-PROPOSAL.md, all pending human freeze) |

## OPS queue (human-handoff parks)

- OPS-1 · needs-human · FREEZE: review FREEZE-PROPOSAL.md and freeze dimension × threshold × tool × gate-job table → ARTIFACT: docs/runs/campaign-2026-09-16-floor-it/FREEZE-QUESTIONNAIRE.md · RECIPIENT: repo maintainer (promotion approver) · VERIFY-COMPLETE: `test -f CONSTRAINTS.md` on BASE successor + DECISIONS log line `class=one-way source=human:<who>` naming the freeze + `git log --oneline -1 -- CONSTRAINTS.md` non-empty. Full text in the questionnaire.

## DECISIONS log

Path: docs/runs/campaign-2026-09-16-floor-it/DECISIONS.md (run-local; target-repo promotion copies grants to docs/DECISIONS.md).
