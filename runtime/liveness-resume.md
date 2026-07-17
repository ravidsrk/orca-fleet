# Runtime policy — liveness and crash-resume

The runtime tracks everything needed to keep a long run alive and recoverable, but it only WARNS on
stalls; the fleet must act. Both live-supervision and crash-resume read the same persisted
provenance (tasks, dispatch_contexts with last_heartbeat_at/failure_count, worker_done payloads —
all in SQLite, surviving restarts).

## Provenance is `taskId`+`dispatchId`, never the handle

Lifecycle authority is the payload's `taskId`+`dispatchId` verified against the dispatched pane —
NOT a terminal-handle comparison. A pane can receive a new handle after a restart, so never accept
or reject a `worker_done`/`heartbeat` by matching handles; the runtime ignores a lifecycle message
sent from a different pane than the one that owns the dispatch. When a handle returns
`terminal_handle_stale`, re-resolve it with `terminal list --worktree … --json` and continue with
the replacement ONLY — never dual-send to the old and new handles.

## WATCH (self-healing while alive)

- Poll `check --wait --types worker_done,escalation,heartbeat` ({count:0} timeout is a checkup
  tick, not an error). The `--wait` stream interleaves `_heartbeat` objects with message batches,
  which breaks naive `json.load` — parse saved streams with `runtime/scripts/pm.py <file>`.
- Stale = a `dispatched` task with no heartbeat past ~10 min, OR still null past the first poll
  window. Judge from `dispatch-show` timestamps, not folklore.
- Respawn a dead worker: log the evidence + a doctor-owned attempt count (NOT the runtime failure
  budget) → **reflection-before-retry** (below) → `task-update → ready` ONLY after the evidence
  line → FRESH terminal (re-dispatch to a used handle is a no-op) → spawn_worker. Its exit codes
  (the script header is the contract): exit 0 = dispatched, heartbeat observed; exit 1 = a
  spawn/dispatch step failed (infra — doctor loop); exit 2 = usage or policy refusal (bad args,
  unknown agent, task not ready, unmet deps, danger without opt-in) — SURFACE the refusal, never
  retry it as an uncounted re-triage; exit 3 = dispatched but no heartbeat after retries — a
  POSSIBLE false negative (codex workers emit none; slow claude boots outlast the poll window),
  so READ THE PANE before respawning: a live TUI is a working worker, and respawning beside it
  creates a dual-writer (dispatch-lifecycle.md).
- BREAK at 3 doctor attempts OR runtime `circuit_broken` (3 real dispatch failures, carried forward
  per task via MAX(failure_count)) → escalate honestly (gate-classification.md).
- **Identical-error kill:** if the last ≥2 doctor attempts failed on the same error signature
  (same failing command + same primary error token), do NOT retry the same approach — kill,
  reassign to a fresh worker with a rewritten TASK, or park. Counted toward the 3-attempt cap.
- Re-confirm `ORCA_COORD_ALLOW_DANGER` before respawning a danger-profile worker.
- Lost preamble ≠ dead worker: recover the dispatched TASK with `dispatch-show --preamble` and
  re-deliver via `terminal send`. Terminal activity means ALIVE — never kill a live worker on a
  missed heartbeat alone.
- NEVER run `orca orchestration reset` mid-run — it wipes the task/dispatch state every recovery
  path below depends on. There is no mid-run situation it fixes that WATCH/RESUME doesn't.

## Reflection-before-retry (mandatory on doctor respawn)

Before every doctor-owned respawn, append to the unit's evidence / ledger:

```
REFLECTION: what failed? · what specific change would fix it? · am I repeating the same approach?
```

A respawn without that line is invalid — write it first. If the honest answer to the third
question is yes, apply the identical-error kill (reassign or park), do not loop.

## The stuck-pending watchdog (a runtime trap)

`task-create` does NOT validate that `--deps` IDs exist, and `promoteReadyTasks` only fires when a
dep COMPLETES. A typo'd dep, or a dep that ends `failed` (not `completed`), strands the child in
`pending` FOREVER — and convergence detection only flags `blocked`, never `pending`. A **failed**
dep is a permanent strand (not a retry of the child). Every fleet adds a watchdog: any task
`pending` with an unmet, nonexistent, or failed dep past a threshold is surfaced, not silently
waited on. Edges are `deps` only — `parent_id` is unused in CLI fleets (orca-dag-semantics.md).

## Scope is never "the whole database"

`orchestration.db` mixes every run on the machine. WATCH and RESUME operate only on the ledger's
coordinator handle(s) + task-id set. Unfiltered `task-list` is a discovery tool, not the run.

## The ledger header (every mission writes it; RESUME depends on it)

The FIRST line of every mission's ledger file is a header, written at run start and updated on
coordinator respawn:

`RUN: <run-id> · COORDINATOR: <terminal handle(s)> · BASE: <integration branch, or '-' for
report-only/planning missions> · FORK_POINT: <sha BASE was created from, or '-'> · T0: <ts> ·
SOURCE: <mission denominator ref + digest> · WIP: builders=<n> reviewers=<n>`

`RUN` and `COORDINATOR` are always required (RESUME dies without them); fields a mission class
has no value for are recorded as `-`, never omitted (a missing column is indistinguishable from
a truncated header). `WIP` is the run's attention cap (attention-budget.md — class defaults
unless measured); a header without it predates this field, and RESUME writes the class default
back in before dispatching anything.

A ledger with rows but no header is a resume-orphan — recoverable only by hand.

Unit **boolean flags**, park classes (`CODE_CLOSED` / `VERIFY_AT_SCALE`), `docs/DECISIONS.md`,
and the **CONTEXT HANDOFF** block under compaction pressure: ledger-contract.md. RESUME always
re-reads those before trusting memory.

## RESUME (coordinator died)

Run scope is mandatory (state is runtime-global; `task-list` has no run filter): scope = the run's
coordinator handle(s) from the ledger header + the ledger's task ids. Everything else is
counted-but-untouched; no scope → resume ABORTS.

1. FREEZE-check: no other live coordinator.
2. REBUILD from provenance; CROSS-VERIFY every "completed" against git (evidence-manifest.md) —
   provenance-says-done + git-disagrees = SUSPECT (treat as failed).
3. RECONCILE the ledger (git is truth, the ledger is its cache).
4. RE-ENTER the mission loop at the DAG frontier; never re-do a verified-merged unit.

## Inflation post-mortem (re-runs — the Aula lesson)

SUSPECT covers crash-resume inside one run; this covers run N+1. A run re-entering a surface a
PRIOR run reported done starts by re-reading that run's completion report and listing every
claim whose proof was "CI green" rather than a verified end state as the FIRST items of the new
work index, re-confirmed OPEN until the verifier passes them against authoritative state. An
autonomous run will otherwise believe its own green checkmarks — anti-inflation has to be
structural, not a reminder.
