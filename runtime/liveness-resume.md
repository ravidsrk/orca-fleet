# Runtime policy — liveness and crash-resume

The runtime tracks everything needed to keep a long run alive and recoverable, but it only WARNS on
stalls; the fleet must act. Both live-supervision and crash-resume read the same persisted
provenance (tasks, dispatch_contexts with last_heartbeat_at/failure_count, worker_done payloads —
all in SQLite, surviving restarts).

## WATCH (self-healing while alive)

- Poll `check --wait --types worker_done,escalation,heartbeat` ({count:0} timeout is a checkup
  tick, not an error). The `--wait` stream interleaves `_heartbeat` objects with message batches,
  which breaks naive `json.load` — parse saved streams with `runtime/scripts/pm.py <file>`.
- Stale = a `dispatched` task with no heartbeat past ~10 min, OR still null past the first poll
  window. Judge from `dispatch-show` timestamps, not folklore.
- Respawn a dead worker: log the evidence + a doctor-owned attempt count (NOT the runtime failure
  budget) → `task-update → ready` ONLY after the evidence line → FRESH terminal (re-dispatch to a
  used handle is a no-op) → spawn_worker (exit 3 = no heartbeat, loop; exit 1 = infra fail; exit 2 =
  state moved, re-triage uncounted).
- BREAK at 3 doctor attempts OR runtime `circuit_broken` (3 real dispatch failures, carried forward
  per task via MAX(failure_count)) → escalate honestly (gate-classification.md).
- Re-confirm `ORCA_COORD_ALLOW_DANGER` before respawning a danger-profile worker.
- Lost preamble ≠ dead worker: recover the dispatched TASK with `dispatch-show --preamble` and
  re-deliver via `terminal send`. Terminal activity means ALIVE — never kill a live worker on a
  missed heartbeat alone.
- NEVER run `orca orchestration reset` mid-run — it wipes the task/dispatch state every recovery
  path below depends on. There is no mid-run situation it fixes that WATCH/RESUME doesn't.

## The stuck-pending watchdog (a runtime trap)

`task-create` does NOT validate that `--deps` IDs exist, and `promoteReadyTasks` only fires when a
dep COMPLETES. A typo'd dep, or a dep that ends `failed` (not `completed`), strands the child in
`pending` FOREVER — and convergence detection only flags `blocked`, never `pending`. Every fleet
adds a watchdog: any task `pending` with an unmet or nonexistent dep past a threshold is surfaced,
not silently waited on.

## The ledger header (every mission writes it; RESUME depends on it)

The FIRST line of every mission's ledger file is a header, written at run start and updated on
coordinator respawn:

`RUN: <run-id> · COORDINATOR: <terminal handle(s)> · BASE: <integration branch> · T0: <ts> ·
SOURCE: <mission denominator ref + digest>`

A ledger with rows but no header is a resume-orphan — recoverable only by hand.

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
