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

## Run identity is a terminal handle (ledger), not `coordinator_runs` alone

Two coordination patterns write different rows:

| Pattern | `coordinator_runs` | Run scope |
|---------|--------------------|-----------|
| **Manual fleet loop** (`task-create` / `dispatch` / `check` / `send`) | **Empty** — never written | Ledger coordinator handle(s) + ledger task ids |
| **`orchestration run`** (built-in Coordinator loop) | **Has a row** — RPC creates it before the loop | Still **unscoped** over the machine DB (adopts leftover tasks) |

The durable key for fleets is always `tasks.created_by_terminal_handle` + the ledger task-id
set. A `coordinator_runs` row is optional evidence that a built-in loop started — never the
sole scope key, never proof a manual fleet is finished.

**Fleet rule:** record coordinator handle(s) in the ledger header at start. Prefer the **manual**
loop over `orchestration run` because the built-in loop is unscoped (not because the table is
empty — it is empty only for the manual pattern).

## DAG edges are `deps`, not `parent_id`

`tasks.deps` (JSON array of task ids) is the dependency graph the runtime promotes against.
`parent_id` is a decomposition hierarchy that is **empty in real CLI fleets** — do not build
or verify fleets on parent/child nesting.

**Fleet rule:** materialize and verify only via `--deps` and returned task ids
(decompose-dag.md). The stuck-pending trap (liveness-resume.md) is about deps, not parents.

## What the message enum lies about

These `MessageType` values exist in the schema but **nothing writes them** on CLI/agent paths
(live counts were zero):

| Type | Reality |
|------|---------|
| `dispatch` | Prompt is injected into the worker PTY; no message row. Reconstruct from `dispatch_contexts` + `tasks.spec`. |
| `handoff` | Unused by the runtime. |

`merge_ready` is **fleet-written** (merge-serialization.md), not a phantom type — the runtime
delivers it but triggers no built-in merge behavior. Expect it during serialized merges.

What *is* real and load-bearing: `worker_done`, `merge_ready`, `heartbeat`, `escalation`,
`decision_gate`, `status`. Heartbeats are the majority of traffic — always type-filter
`check --wait` or use `--peek` so they do not bury lifecycle mail (dispatch-lifecycle.md).

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
(`completed` or `failed`), no live worker ask is waiting on the coordinator (dispatched unit +
ask thread with no reply — not merely unread), and no `gate-create` hold remains for those tasks.
Not converged:

- any `pending` / `ready` / `dispatched` / `blocked` in scope
- live ask (dispatched unit, ask without reply) even if the message is already `read`
- a `pending` child whose dep **failed** or never existed (never auto-promotes — stuck-pending
  watchdog must surface it; a failed dep is a permanent strand, not a retry)

A finished foreign run in the same DB is irrelevant. All-green elsewhere is not your proof.

## Gates: live ask vs historical vs DAG hold

Two paths (gate-classification.md):

1. Worker / coordinator `ask` → a `decision_gate` **message** (often **no** `decision_gates`
   table row; payload may omit `taskId`). The worker CLI **blocks until reply or timeout**.
   The task usually stays `dispatched` — `ask` does **not** flip it to `blocked`.
2. Coordinator `gate-create` → table row + task status `blocked`; `gate-resolve` unblocks.

**Fleet rule — distinguish live from historical:**

| Case | How you know | Action |
|------|--------------|--------|
| **Live ask** | A worker unit is still `dispatched` and a `decision_gate` / ask in its thread has **no reply** yet (do **not** rely on the unread bit alone — `check --wait` marks read on receive) | **Always blocking inbox work.** Reply by `message id` (`reply --id`) promptly — do not wait for task status `blocked` (it will not come). Ignoring it burns the ask timeout. On RESUME, re-scan threads for asks without replies while the unit is still dispatched. |
| **Historical unanswered** | Unit already terminal / no waiting worker; ask with or without a reply left in history | **Not** a fleet stall. Do not spin the run waiting on it. |
| **DAG hold** | `gate-create` → task `blocked` | DAG blocker until `gate-resolve` or park as one-way human. |

Prefer `gate-create` for human one-way holds the DAG must respect; prefer classified `ask` for
worker→coordinator mechanical/taste questions. Answer asks by **message id**, never by guessing
a gate-table id.

## Completion receipts the DB retains

`worker_done.payload` and `tasks.result` are free-form TEXT. The fleet's SHA-bound evidence
manifest (evidence-manifest.md) is the definition of done; still put `reportPath` (and PR /
branch when present) in the `worker_done` payload so retained orchestration history points at
the same artifacts a post-mortem tool can surface.

## Explicit non-goals (do not import from visualizers)

Wave/idle-gap UI, process-liveness dots, conversation reconstruction, scoreboards — operator
tooling. Fleets own ledger + evidence, not a second event store.
