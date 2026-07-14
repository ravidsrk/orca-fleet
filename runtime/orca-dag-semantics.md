# Runtime policy — Orca DAG semantics (CLI / agent fleets)

Ground truth about how Orca's orchestration DAG actually behaves for fleets that drive it
with CLI verbs (`task-create` / `dispatch` / `check` / `send`), not Orca's built-in
`Coordinator.run` loop. Sourced from live-DB research (schema v5); treat as operational
contract, not product marketing.

## The database is machine-global and multi-run

One `orchestration.db` per Orca userData, shared across every repo and every past run since
the last manual reset. Nothing prunes automatically. `task-list` returns **every** task on
the machine, not "this mission."

**Fleet rule:** the run scope is the ledger's coordinator handle(s) + the ledger's task-id
set (liveness-resume.md). Never converge, WATCH, or RESUME against an unfiltered `task-list`.
A foreign run's completed tasks are not your wins; a foreign pending is not your stall.

## Run identity is a terminal handle, not `coordinator_runs`

`coordinator_runs` is written only by Orca's built-in `orchestration.run` loop. Agent-driven
fleets leave it **empty**. The real key is `tasks.created_by_terminal_handle` (the coordinator
that ran `task-create`).

**Fleet rule:** record coordinator handle(s) in the ledger header at start. Do not use
`coordinator_runs` for scoping, resume, or "is the run finished." Prefer the **manual**
coordinator loop over `orchestration run`: the built-in loop is **unscoped** — it iterates
every task in the DB and will adopt leftover tasks from other runs.

## DAG edges are `deps`, not `parent_id`

`tasks.deps` (JSON array of task ids) is the dependency graph the runtime promotes against.
`parent_id` is a decomposition hierarchy that is **empty in real CLI fleets** — do not build
or verify fleets on parent/child nesting.

**Fleet rule:** materialize and verify only via `--deps` and returned task ids
(decompose-dag.md). The stuck-pending trap (liveness-resume.md) is about deps, not parents.

## What the message enum lies about

These `MessageType` values exist in the schema but the runtime **does not write them** on
CLI/agent paths (live counts were zero):

| Type | Reality |
|------|---------|
| `dispatch` | Prompt is injected into the worker PTY; no message row. Reconstruct from `dispatch_contexts` + `tasks.spec`. |
| `handoff` | Unused by the runtime. |
| `merge_ready` | **Fleet-owned** convention (merge-serialization.md writes it). Runtime delivers only — no built-in merge behavior. |

What *is* real and load-bearing: `worker_done`, `heartbeat`, `escalation`, `decision_gate`,
`status`. Heartbeats are the majority of traffic — always type-filter `check --wait` or use
`--peek` so they do not bury lifecycle mail (dispatch-lifecycle.md).

## Task status is current-state, not a timeline

`tasks.status` is overwritten in place by many writers. `pending → ready` promotion is
**silent and untimestamped**. Reconstructible facts: creation, each dispatch attempt
(`dispatch_contexts` is one row per attempt; latest = max rowid; `failure_count` carries
MAX forward; circuit trips at 3), completion via `worker_done`.

**Fleet rule:** never grade progress from a reconstructed status history. Ledger + git +
evidence-manifest are the completion oracle. `worker_done` with matching `taskId`+`dispatchId`
from the owning pane auto-completes the task — do not also `task-update --status completed`.

## Convergence (when the DAG is done)

A run is **converged** only when every task in the **ledger task-id set** is terminal
(`completed` or `failed`) and no **blocking** gate remains for those tasks. Not converged:

- any `pending` / `ready` / `dispatched` / `blocked` in scope
- a `pending` child whose dep **failed** or never existed (never auto-promotes — stuck-pending
  watchdog must surface it; a failed dep is a permanent strand, not a retry)

A finished foreign run in the same DB is irrelevant. All-green elsewhere is not your proof.

## Gates: lifecycle state ≠ blocking effect

Two paths (gate-classification.md):

1. Worker / coordinator `ask` → a `decision_gate` **message** (often **no** `decision_gates`
   table row on CLI paths).
2. Coordinator `gate-create` → table row + task `blocked`.

**Fleet rule:**

- Answer worker asks by **message id** (`reply --id`), not by guessing a gate-table id.
- An **unanswered ask** is not automatically a fleet blocker — it blocks only while the named
  task is actually `blocked` (or you intentionally treat it as a one-way park). Do not wait
  forever on historical unanswered asks after the task completed.
- Prefer `gate-create` for human one-way holds you need the DAG to respect; prefer classified
  `ask` for worker→coordinator mechanical/taste questions.

## Completion receipts the DB retains

`worker_done.payload` and `tasks.result` are free-form TEXT. The fleet's SHA-bound evidence
manifest (evidence-manifest.md) is the definition of done; still put `reportPath` (and PR /
branch when present) in the `worker_done` payload so retained orchestration history points at
the same artifacts a post-mortem tool can surface.

## Explicit non-goals (do not import from visualizers)

Wave/idle-gap UI, process-liveness dots, conversation reconstruction, scoreboards — operator
tooling. Fleets own ledger + evidence, not a second event store.
