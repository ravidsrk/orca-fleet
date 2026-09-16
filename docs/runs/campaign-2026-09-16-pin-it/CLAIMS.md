# Frozen claim inventory — pin-it selftest campaign 2026-09-16

FREEZE-TIME: 2026-09-16T13:05:00Z (claim SET fixed here; replay receipts captured after this file was written)
BASE: `campaign/pin-it-selftest` · FORK_POINT: `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip at T0)
INSTALLED ORACLE: `orca 1.4.203` build `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec` (same build as the live pin; upstream HEAD `0b28d354` recorded, not chased)
PRIOR PIN: v1.4.203 `54eaa147` (2026-09-16, `docs/runs/2026-09-16-pin-it-416/`) — this run re-witnesses at the same build, ~7.5h later.

## Scope cut (mission §SCOPE CUT — NOT claims, never re-witnessed against the binary)

Fleet-policy invariants enforced by `preflight.py`/`verify.py` are a category error against the
control plane: BASE ≠ default, ledger flags, reviewed-SHA freshness, `ledger-contract.md`,
`attention-budget.md`, `mission-chaining.md`, `reviewed-sha-freshness.md` (fleet-only),
`evidence-manifest.md` §1 protocol (only its `--report-path` CLI-shape cite is a claim: C24),
`gate-batch.py` + `watchdog.py` (NEW since the pin; verified fleet-only: no `orca` CLI calls —
see classification notes), and all other `runtime/scripts/` entries with no Orca surface
(`decisions.py`, `diff_scope.py`, `ed25519.py`, `evidence-run.py`, `floor_guard.py`,
`guard_text.py`, `hitl-loop.template.sh`, `inventory.py`, `preflight.py`, `proof_status.py`,
`run_report.py`, `wtree.sh`, `dispatch-sign.py`, `egress.py`, `verify-gate.sh`, `verify.py`).
Prior parks (OS/remote/paid-trust/isolated-runtime) carry over unchanged — re-owed, not re-probed.

## Claim records (id · source · verbatim claim · probe · expected receipt · receipt path · disposition)

Disposition at freeze is OWED for all; verdicts live in CLASSIFICATION.md (this file never shrinks).

| ID | Source file:line @ HEAD | Claim text (verbatim, trimmed) | Probe command | Expected receipt shape | Receipt path | Disp |
|---|---|---|---|---|---|---|
| C01 | `runtime/dispatch-lifecycle.md:15` | "The normal supervised spawn is `orca orchestration worker-start` with `--task --worktree --name --agent --setup run --json`" | `agent-context.json`: flags of `orchestration worker-start` | task, worktree, name?, agent, setup, json present | `receipts/agent-context.json` | OWED |
| C02 | `runtime/dispatch-lifecycle.md:43` | "`worker_done` requires `--outcome succeeded\|failed` and omits `--to`" | schema `orchestration send` usage/notes + `orchestration-worker-contract.md` | `--outcome` required; `--to` omitted→Run mailbox | `receipts/agent-context.json` + `guides/orchestration-worker-contract.md` | OWED |
| C03 | `runtime/dispatch-lifecycle.md:117` | "A consuming `check` returns the bound Run's oldest FIFO Delivery — up to 50 messages in one batch — and replays that exact batch until you `--ack`" | BEHAVIOR replay in scratch Run (sender-bound) | Delivery ≤50, replay-until-ack | PARKED (B02) | OWED |
| C04 | `runtime/dispatch-lifecycle.md:72` | "only `release_unknown` exits 1" (`retained`, `release_pending`, `already_released` exit 0) | BEHAVIOR replay per exit branch (sender-bound) | exit codes per branch | PARKED (B09) | OWED |
| C05 | `runtime/dispatch-lifecycle.md:111` | "`run-create --objective` — the returned run id IS the fleet's scope: `task-list --run`, `worker-list --run`, and the coordinator `check` all honor it" | `worker-list --run <id>` (read-only half) + BEHAVIOR half (sender-bound) | `scope.source=flag` + scoping behavior | `receipts/worker-list-bound.json` + PARKED (B01) | OWED |
| C06 | `runtime/dispatch-lifecycle.md:146` | "terminals first with `terminal close --worktree <selector> --all` … then `worktree rm --worktree id:<repoId>::<path>`" | schema flags `terminal close`/`worktree rm` + `--help` | `--all` exists; `stop` deprecated | `receipts/agent-context.json` + `receipts/terminal-stop-deprecated.txt` | OWED |
| C07 | `runtime/dispatch-lifecycle.md:112` | "`orchestration run` / `coordinator-start` are retired scheduler aliases returning the recovery action" | `orca orchestration run --help` | retired page, recovery action | `receipts/retired-run-alias.txt` | OWED |
| C08 | `runtime/liveness-resume.md:18` | "`worker-list` is the ENUMERATING command … Each row carries `projection.liveness`, `projection.attention.categories`, `projection.attention.requiresAction`, and a literal `projection.nextAction.argv`" | `worker-list --json` (unscoped) shape | projection keys present | `receipts/worker-list-unscoped.json` | OWED |
| C09 | `runtime/liveness-resume.md:50` | "End-of-run gate: `worker-list --run <id> --terminal-state reclaimable`" | `worker-list --terminal-state reclaimable --json` | exit 0 | `receipts/worker-list-reclaimable.json` | OWED |
| C10 | `runtime/liveness-resume.md:30` | "`outcome_unknown` — the start neither proved nor disproved the worker" + `unverifiable` vocab (`missing_status`, …) | shape rows in worker-list receipts | enum values live | `receipts/worker-list-*.json` | OWED |
| C11 | `runtime/liveness-resume.md:94` | "`task-create` DOES validate `--deps` … `Dependency task <id> must belong to run <run>`" | BEHAVIOR replay (sender-bound) | refutation receipt | PARKED (B04) | OWED |
| C12 | `runtime/gate-classification.md:16` | "`ask --options` takes a CSV … `gate-create --options` takes a JSON array" | schema usage of `ask`/`gate-create` + source anchor (same build → holds by identity) | CSV vs JSON-array | `receipts/agent-context.json` | OWED |
| C13 | `runtime/gate-classification.md:8` | "Times out (600 000 ms default, 1 800 000 ms cap) … resume the SAME message id (`ask --resume <msg_id>`)" | schema `ask --resume` + BEHAVIOR half (sender-bound) | `--resume` exists; timeout behavior parked | `receipts/agent-context.json` + PARKED (B08) | OWED |
| C14 | `runtime/gate-classification.md:20` | "`gate-resolve` does NOT inject the resolution into the next dispatch preamble" | BEHAVIOR replay (sender-bound) | preamble lacks gate context | PARKED (B05) | OWED |
| C15 | `runtime/sandbox-policy.md:22` | "Orca has no read-only tier for ANY agent — its maps are `YOLO_TUI_AGENT_ARGS` plus a small `YOLO_TUI_AGENT_ENV` env map" | source anchor at build commit (same build → holds by identity) + `launch.effective` (sender-bound probe owed) | map shape; effective recorded at spawn | PARKED (B06, live half) | OWED |
| C16 | `runtime/sandbox-policy.md:74` | "`doctor` is clear only with no `fail` AND no `warn`. `ok:true` on its own proves nothing" | `orca-per-workspace-env` guide doctor-verdict section | verdict rule text | `guides/orca-per-workspace-env.md` | OWED |
| C17 | `runtime/merge-serialization.md:17` | "`--to` is optional from an active Dispatch — an omitted recipient defaults to the owning Run mailbox" + "A `merge_ready` to a group is NOT rejected" | schema `send` notes | default-recipient + group-fanout notes | `receipts/agent-context.json` | OWED |
| C18 | `runtime/merge-serialization.md:11` | "`merge_ready` is a first-class Orca message type with NO built-in behavior — the runtime delivers it and stops" | schema `send --type` values | `merge_ready` listed, no behavior note | `receipts/agent-context.json` | OWED |
| C19 | `runtime/orca-dag-semantics.md:58` | "`--types` is only the WAKE condition — the Delivery still carries the whole FIFO batch" | BEHAVIOR replay (sender-bound) | mixed-batch wake | PARKED (B02) | OWED |
| C20 | `runtime/orca-dag-semantics.md:25` | "DAG edges are `deps`, not `parent_id` … the fleet does not set it" | schema `task-create --deps/--parent` | both flags exist; fleet sets deps only | `receipts/agent-context.json` | OWED |
| C21 | `runtime/worker-supervision.md` | "CLI shapes `worker-read --dispatch`, `run-use --from`, `send --to`" + `stable_pane_required`/`terminal_handle_stale` | schema flags | flags exist | `receipts/agent-context.json` | OWED |
| C22 | `runtime/mission-scheduling.md` | "every `automations create` flag schema-verified" + precheck skip | schema `automations create` + `automations list` | flags exist; list runs | `receipts/agent-context.json` + `receipts/automations-list.txt` | OWED |
| C23 | `runtime/scripts/spawn_worker.sh` | "YOLO map, release contract, readiness turn-start, refusal codes — every relied behavior holds" | `--help`/schema + source anchors (same build → holds by identity) | shapes hold | `receipts/agent-context.json` | OWED |
| C24 | `runtime/evidence-manifest.md:12` | "the typed `--report-path` flag" | schema `send --report-path` | flag exists | `receipts/agent-context.json` | OWED |
| C25 | `runtime/scripts/pm.py` | "Keepalives go to stderr every 15 s (`_keepalive`, `_heartbeat` alias)" | `--help`/source (same build → holds by identity) | keepalive contract | (source-held) | OWED |
| C26 | `runtime/scripts/deny-hook.sh` | "Denies `orca orchestration reset` by command string; the verb still exists" | schema has `orchestration reset` | verb exists | `receipts/agent-context.json` | OWED |
| C27 | `runtime/scripts/sandbox_doctor.py` | "Structural parse over generic finding/status keys — no pinned upstream shape" | inspection (no CLI reliance) | no drift surface | (inspection) | OWED |
| C28 | mission preambles (all) | worker-contract preamble: `--from/--dispatch-capability`, typed flags, `check --terminal` checkpoints, `consumer_fenced`→stop | `orchestration-worker-contract.md` guide + schema | contract text | `guides/orchestration-worker-contract.md` | OWED |
| C29 | `skills/pin-it/SKILL.md:41` | "control-plane probes — run-create, worktree create, worker-start — MUTATE Orca state" | substrate receipts (refused BEFORE effects for lack of sender) | `no_active_sender_terminal`/`no_active_terminal` | `receipts/substrate-*.json` | OWED |
| C30 | guide 1.4.203 `messaging-and-gates` | group-address scoping ("every group but `@worktree:<id>` reaches the live Dispatches of the sender's own Run…") | BEHAVIOR replay in scratch Run (sender-bound) | scoping behavior | PARKED (B03) | OWED |
| C31 | `runtime/dispatch-lifecycle.md:25` | "Refusals are typed codes — branch on `error.code` … `task_not_found`, `task_not_startable`, …" | `--from` refusal receipt (typed-code shape) | `invalid_argument` typed envelope | `receipts/worker-list-from-no-run.json` | OWED |
| C32 | `runtime/dispatch-lifecycle.md:32` | "`--inject` SUBMITS the preamble … `--json` returns `result.prompt{requestId, stages}`" | BEHAVIOR replay (sender-bound) | prompt shape | PARKED (B07) | OWED |

## Parked behavior families (BLOCKED-BY-SUBSTRATE pre-registered; each names its exact probe)

| Park | Probe (from a live Orca terminal, scratch Run, full teardown) |
|---|---|
| B01 Run scope verbs | `run-create --objective` → `run-current` → `run-use --id` on a second terminal; `task-list --run` / `check` honor the scope |
| B02 Consuming check | Mixed-batch `check --wait` → Delivery ≤50 → replay-until-`--ack`; `--types` wakes on other types |
| B03 Group send | `send --to @all --type merge_ready` in a scratch Run (1.4.203 guide documents scoping; replay owed) |
| B04 Task deps | `task-create --deps '["bogus"]'` → archive the refutation; failed-dep stuck-pending strand |
| B05 Gates | `gate-create` → `gate-resolve` → `dispatch-show --task --preamble`: is the resolution there? |
| B06 Worker start roster | `worker-start` per roster agent — `state`, `stage`, `launch.effective`, `turnStart`, host `agentDefaultArgs` mode |
| B07 Inject receipt | `dispatch --inject --json` → `prompt.{requestId, stages}` inspected, never replayed; `request_mismatch` on regenerated replay |
| B08 Live ask | `ask` blocks, timeout PENDINGs, `ask --resume <same id>` resumes; `reply --id` answers |
| B09 Release/retain | `worker-release --dispatch` exit contract (`release_unknown`→1, rest→0); `worker-retain` |
| B10 Danger lane | `vm recipe doctor <id>` verdict shapes through `sandbox_doctor.py` (needs recipe + placement binding) |

Freeze binding: the sha256 of THESE BYTES is recorded externally in `manifest.json`
`contract.digest` + `artifacts[]` and in `README.md` SOURCE (never self-embedded — a hash
inside the hashed bytes chases itself). The SET above is frozen: classification may flip
OWED→verdict, never add/remove rows.
