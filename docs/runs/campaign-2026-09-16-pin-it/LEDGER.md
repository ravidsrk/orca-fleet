# Ledger — pin-it selftest campaign 2026-09-16

RUN: - · COORDINATOR: - (plain shell; no sender terminal) · BASE: campaign/pin-it-selftest · FORK_POINT: c46d4b3f3371e41408aed19e54476fa194c20b42 · T0: 2026-09-16T13:02:36Z · SOURCE: CLAIMS.md (32 claims C01–C32 + 10 parks B01–B10) + CLI 1.4.203 `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec` · WIP: builders=0 reviewers=0

PHASE: ORIENT → FREEZE → BUILDING → PROVING → SHIPPING → REFLECTING → DONE (current: FREEZE; coordinator-only re-witness, no worker TASK dispatched — zero packs mounted, satisfying the one-router rule)

TASK pack: n/a (no worker TASK; coordinator ran read-only probes directly per `sandbox-policy` PROFILE=ro)

## Unit rows (one per claim; boolean gates per `ledger-contract.md`)

Legend: BUILD_DONE=probe captured · PR_OPEN/BOT=n/a (no doctrine patch; no PR) · REVIEWED=classification reviewed · MERGED=n/a (nothing to land) or evidence commit · WT_CLEAN=n/a (coordinator worktree retained for the campaign commit).

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| C01 | worker-start shape | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C02 | worker_done contract | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json + guides/orchestration-worker-contract.md |
| C03 | Delivery ≤50 behavior | f | n/a | n/a | f | n/a | n/a | lit | needs-live-terminal (B02) | receipts/substrate-check-peek.json (substrate proof) |
| C04 | release exit contract | f | n/a | n/a | f | n/a | n/a | lit | needs-live-terminal (B09) | receipts/substrate-run-create.json (substrate proof) |
| C05 | run scope | t | n/a | n/a | t | n/a | n/a | lit | needs-live-terminal (B01, behavior half) | receipts/worker-list-bound.json |
| C06 | teardown verbs | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json + receipts/terminal-stop-deprecated.txt |
| C07 | retired aliases | t | n/a | n/a | t | n/a | n/a | lit | | receipts/retired-run-alias.txt |
| C08 | worker-list projection | t | n/a | n/a | t | n/a | n/a | lit | | receipts/worker-list-unscoped.json |
| C09 | reclaimable gate | t | n/a | n/a | t | n/a | n/a | lit | | receipts/worker-list-reclaimable.json |
| C10 | liveness vocab | t | n/a | n/a | t | n/a | n/a | lit | | receipts/worker-list-*.json |
| C11 | deps validation | f | n/a | n/a | f | n/a | n/a | lit | needs-live-terminal (B04) | receipts/substrate-run-create.json (substrate proof) |
| C12 | ask/gate options shape | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C13 | ask resume | t | n/a | n/a | t | n/a | n/a | lit | needs-live-terminal (B08, behavior half) | receipts/agent-context.json |
| C14 | gate-resolve no-inject | f | n/a | n/a | f | n/a | n/a | lit | needs-live-terminal (B05) | receipts/substrate-run-create.json (substrate proof) |
| C15 | YOLO map | t | n/a | n/a | t | n/a | n/a | lit | needs-live-terminal (B06, live half) | build-identity (same commit) |
| C16 | doctor verdict rule | t | n/a | n/a | t | n/a | n/a | lit | | guides/orca-per-workspace-env.md |
| C17 | send --to default + group | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C18 | merge_ready no-behavior | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C19 | --types wake-only | f | n/a | n/a | f | n/a | n/a | lit | needs-live-terminal (B02) | receipts/substrate-check-peek.json (substrate proof) |
| C20 | deps edges | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C21 | supervision shapes | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C22 | automations flags | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json + receipts/automations-list.txt |
| C23 | spawn_worker.sh behavior | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json + build-identity |
| C24 | --report-path flag | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C25 | pm.py keepalive | t | n/a | n/a | t | n/a | n/a | lit | | build-identity (same commit) |
| C26 | deny-hook reset verb | t | n/a | n/a | t | n/a | n/a | lit | | receipts/agent-context.json |
| C27 | sandbox_doctor structural | t | n/a | n/a | t | n/a | n/a | lit | | inspection (no CLI surface) |
| C28 | preamble contract | t | n/a | n/a | t | n/a | n/a | lit | | guides/orchestration-worker-contract.md |
| C29 | control-plane MUTATES | t | n/a | n/a | t | n/a | n/a | lit | | receipts/substrate-*.json |
| C30 | group scoping behavior | f | n/a | n/a | f | n/a | n/a | lit | needs-live-terminal (B03) | guides/orchestration-messaging-and-gates.md (map only) |
| C31 | typed refusals | t | n/a | n/a | t | n/a | n/a | lit | | receipts/worker-list-from-no-run.json |
| C32 | inject receipt shape | f | n/a | n/a | f | n/a | n/a | lit | needs-live-terminal (B07) | receipts/substrate-run-create.json (substrate proof) |

## DECISIONS log pointer

`docs/runs/campaign-2026-09-16-pin-it/DECISIONS.md` (mechanical auto-resolves; no one-way gates hit — no human grant needed or faked).

## Teardown record

No Orca state created (every sender-bound probe refused before effects; every executed probe
read-only). Nothing to settle, release, or remove. No `reset`, no global change.
