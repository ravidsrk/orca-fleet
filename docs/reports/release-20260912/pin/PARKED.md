# Complete incomplete-work register

290 records; all remain unproven as complete claims. No absence of a live receipt proves an absent mechanism.

## C001 — runtime/attention-budget.md:26

history stands as measured; the mechanism that produced it no longer has to: liveness now comes
from `worker-list`'s `projection.liveness` and `attention.requiresAction`, not from reading panes
for heartbeats (liveness-resume.md).

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C002 — runtime/dispatch-lifecycle.md:5

**Anti-drift rule:** this file describes the CLI the installed binary ships.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C003 — runtime/dispatch-lifecycle.md:5

 After any Orca upgrade the mechanics are re-witnessed against `orca skills get
orchestration` / `orca skills get orca-cli` — but the compact guide is a KERNEL, not the contract: enumerate `orca skills get <topic> --references` and load
each `--reference <name>` (`--full` on older CLIs), because the worker contract, recovery, and legacy-migration rules live only there (`skills.ts:50-58`).
pin-it owns that loop; hand-editing from memory is how it went stale twice.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C004 — runtime/dispatch-lifecycle.md:15

The normal supervised spawn is **`orca orchestration worker-start`** with `--task --worktree --name --agent --setup run --json` (worktree → terminal →
readiness → dispatch).

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C005 — runtime/dispatch-lifecycle.md:16

 It exits 0 only when the worker is **ready**, read narrowly: at v1.4.199 — the PIN — that means the preamble WRITE WAS ACCEPTED, not
that a turn started (`local-worker-start.ts:263`).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C006 — runtime/dispatch-lifecycle.md:17

 **v1.4.200 changed it**: `worker-start-readiness-settlement.ts:91-129` needs an observed turn-start, else
`outcome_unknown`; the top-level contract is unchanged, so v5 already branches right (#302).

**Unsatisfied:** Ready + observed turn-start witnessed only for the supplied existing native Codex terminal; absence-to-outcome_unknown and fresh launcher roster not exercised. Remaining procedure: Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** helper-start

## C007 — runtime/dispatch-lifecycle.md:18

 Witnessed at both tags; probe owed — pin-it.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C008 — runtime/dispatch-lifecycle.md:20

The receipt carries more than the flat four: `runId, taskId, dispatchId, state, stage, setup, launch{requested,effective}, mode, effects[],
residualResources[]`, and on a bad start `failedStage, lastError, recovery, nextCommands` (`worker-start-receipt.ts:42-69`).

**Unsatisfied:** Success receipt captured; failed-start failure/recovery branches not exercised. Remaining procedure: Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** helper-start

## C010 — runtime/dispatch-lifecycle.md:22

 Read `launch.effective`, never `requested` — a model, effort, or permission flag is only what the host
actually applied. `--worktree current` / an exact worktree id = a fresh agent terminal, no setup rerun; `--terminal <handle>` = reuse an exact idle agent
(cleanup ownership transfers).

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C011 — runtime/dispatch-lifecycle.md:26

**Refusals are typed codes** — branch on `error.code`, never exit status or stderr; `error.data.nextSteps` is the recovery text (older hosts omit it):
`task_not_found`, `task_not_startable` (+`data.unmetDependencies`, `data.retryOf`), `inject_rejected`, `nested_worker_depth_exceeded`, `consumer_fenced`,
`dispatch_inactive` are policy; `runtime_error` is the catch-all: "do not retry unchanged". `orchestration-dispatch-refusal-contract.ts:8` declares the first
three ONLY; the rest sit at their own sites, anchored per code beside POLICY_CODES in spawn_worker.sh (#302); recovery `recovery-and-cleanup:96-108`.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C012 — runtime/dispatch-lifecycle.md:31

`terminal create` + `dispatch --inject` remains the **low-level, deliberately unsupervised** lane: no worker-lifecycle row, so `worker-stop`/`worker-release`
never touch that process.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C013 — runtime/dispatch-lifecycle.md:32

 It is NOT invisible — `worker-list` lists it as `unsupervised` with terminal state `retained` (`orchestration-worker-specs.ts:124`).

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C014 — runtime/dispatch-lifecycle.md:33

Use it for custom argv/topology `worker-start` cannot express (and for `PROFILE=ro`), and record the trade in the ledger.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C015 — runtime/dispatch-lifecycle.md:33

 **`--inject` SUBMITS the preamble**
— it does not merely paste it (`dispatch-methods.ts:155-165`) — and `--json` returns `result.prompt{requestId, stages}` over `input_accepted | turn_started`
(`runtime-terminal-contracts.ts:221-225`).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C017 — runtime/dispatch-lifecycle.md:37

 The bounded re-Enter loop is deleted; an extra
Enter on a started turn is a stray keystroke outside the receipt model.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C018 — runtime/dispatch-lifecycle.md:44

- `worker_done` **requires `--outcome succeeded|failed`** and **omits `--to`** — an active Dispatch defaults to its owning Run mailbox, which is the preferred
  address; a terminal handle is not (`orchestration.ts:74-76`, `orchestration/worker-contract:71`).

**Unsatisfied:** Successful typed worker_done without --to witnessed; missing outcome and alternate sender refusal probes remain owed. Remaining procedure: Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** helper-check-1, helper-tasks-after-done

## C019 — runtime/dispatch-lifecycle.md:46

- Every worker send carries `--from <worker_handle> --dispatch-capability <capability>`, both handed to it in the preamble
  (`orchestration/worker-contract:13,25-27`).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C020 — runtime/dispatch-lifecycle.md:48

- Evidence rides TYPED flags — `--report-path <path>`, `--files-modified <csv>` — not a hand-rolled `--payload` JSON blob, which PowerShell strips quotes from
  (`orchestration.ts:49`).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C021 — runtime/dispatch-lifecycle.md:50

- A worker runs `check --terminal <its own handle>` at checkpoints and once before `worker_done`.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C022 — runtime/dispatch-lifecycle.md:50

 A `consumer_fenced` from that check means **stop**: it no
  longer owns its Dispatch and must not send `worker_done` (`orchestration/worker-contract:40-51`).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C023 — runtime/dispatch-lifecycle.md:55

A supervised worker's worktree is a CHILD of the coordinator, not a top-level tree — pass **`--parent-worktree active`** on the unit's first (builder)
worktree (with `worker-start`, that is `--worktree new-child`).

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C024 — runtime/dispatch-lifecycle.md:56

 Omitting `--no-parent` relies on Orca inferring the parent from the cwd, which only works
"when it can"; `--no-parent` is the OPPOSITE — a top-level full handoff nobody supervises — and orphans a coordinated unit's lineage from the run.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C025 — runtime/dispatch-lifecycle.md:59

Each unit's DEPENDENT workers — its build-blind reviewer, every fix round, the integrator, the review-bot reconcile — are FRESH agent terminals created INSIDE
that unit's own worktree (`worker-start --worktree <exact id>`, an `id:<repoId>::<path>` selector; a bare repo id is rejected), never a new worktree and never
`--worktree active` (which can resolve to the coordinator root).

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C026 — runtime/dispatch-lifecycle.md:61

 A fresh terminal is a fresh build-blind session sharing the unit's branch, so parenting to
the worktree keeps lineage correct WITHOUT leaking the builder's conversation: coordinator → unit-A worktree → {unit-A review, fix rounds, integrator}.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C027 — runtime/dispatch-lifecycle.md:62

 Keep
chains ≤3–4 deep.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C028 — runtime/dispatch-lifecycle.md:65

**Nested depth:** workers do not dispatch sub-workers — `nested_worker_depth_exceeded` fires at depth 1 by default, counted from the issuing terminal (it is
Settings-tunable, so on a raised host this stops being runtime-enforced and stays fleet policy).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C029 — runtime/dispatch-lifecycle.md:66

 Acceptance-review's axes are dispatched by the COORDINATOR,
one worker per axis — never by a reviewer worker fanning out its own.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C030 — runtime/dispatch-lifecycle.md:69

Operational specifics: a worktree id is the composite `<repoId>::<worktreePath>` returned by `worktree create --json` — pass `path:/abs/worktree/path`
(unambiguous) or that full id, never the bare repo id.

**Unsatisfied:** Composite id and path selector witnessed; bare-repo-id rejection was not exercised. Remaining procedure: Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** scratch-create, teardown-remove

## C031 — runtime/dispatch-lifecycle.md:70

 On Linux, a bare `orca` outside an Orca-managed terminal is usually the GNOME screen reader — use
`orca-ide` there.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C032 — runtime/dispatch-lifecycle.md:71

 After an accepted `worker_done`, run **`worker-release --dispatch <id>`** (Orca preserves inspectable output, then closes only the exact
agent terminal that dispatch owned) — or `worker-retain` at the user's explicit request.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C033 — runtime/dispatch-lifecycle.md:72

 Its exit contract: `retained`, `release_pending`, and
`already_released` all exit 0 (it is idempotent); **only `release_unknown` exits 1** and needs the receipt's own recovery action
(`orchestration-worker-specs.ts:102`).

**Unsatisfied:** retained/external_terminal is exit 0 on both calls; release_pending, already_released and release_unknown branches not tested. Remaining procedure: Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** settle-release, settle-release-replay

## C034 — runtime/dispatch-lifecycle.md:74

 The pane that outlived its `worker_done` under a new handle (the old dual-writer class) is now fenced by the runtime at
settlement; release is still the fleet's hygiene step — never on a timeout, TUI-idle, or a heartbeat gap (those are liveness questions, liveness-resume.md,
not completion).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C035 — runtime/dispatch-lifecycle.md:112

Create or bind the run's namespace once: `orca orchestration run-create --objective "<text>" --json` — the returned run id IS the fleet's scope: `task-list
--run`, `worker-list --run`, and the coordinator `check` all honor it. `orchestration run` / `coordinator-start` are retired scheduler aliases returning the
recovery action; the loop is the manual one (task-create → worker-start → `check --wait`).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C036 — runtime/dispatch-lifecycle.md:114

 Record the run id in the ledger header (liveness-resume.md).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C038 — runtime/dispatch-lifecycle.md:119

 Process EVERY message in the batch (reply to `question`s, settle `worker_done`s, release or reuse those workers) and only then `check --ack
  <id> --wait` for the next window.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C039 — runtime/dispatch-lifecycle.md:121

- Read-marking: `task-list`, `inbox`, and `dispatch-show` do NOT mark messages read; `check` (default and `--unread`) CONSUMES what it returns — to inspect
  without consuming use `check --peek` (unread) or `check --all` (history). `task-list --brief` collapses whitespace and caps each echoed spec at 160 chars
  (`spec_truncated` marks shortened rows); omit it when the full spec is needed.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C041 — runtime/dispatch-lifecycle.md:126

- Mutations accept `--retry-request <id>`: a lost response never risks a duplicate dispatch — re-issue with the same request id and the runtime dedupes
  (`request-show --request <id>`; `completed`/`pending`/`absent`).

**Unsatisfied:** Owned inert terminal and original prompt bytes/request receipt. Dispatch-derived equivalence additionally needs coordinator-provided worker fixture. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an owned inert terminal capture an initial original-text --enter request; replay terminal send --terminal <owned> --retry-request <original-id> --wait-submit 1 --json, then correct missing original --text/--enter and compare request ID and terminal effects.

**Expected receipt:** Old shorthand refusal before effects; corrected replay result and original request identity, with no duplicate terminal input.

**Partial observations:** none

## C042 — runtime/dispatch-lifecycle.md:127

 Use it on every non-idempotent orchestration call.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C043 — runtime/dispatch-lifecycle.md:128

- Group addresses (`@all`, `@idle`, `@claude`, `@codex`, `@grok`, `@cursor`, `@opencode`, `@gemini`, `@droid`, `@worktree:<id>`, …) are broadcast-only.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C044 — runtime/dispatch-lifecycle.md:128

 The
  RUNTIME rejects a group address for `worker_done` and `heartbeat` only (`message-send-handler.ts:51-58`) — a `merge_ready` to `@all` really would fan out.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C045 — runtime/dispatch-lifecycle.md:130

  The rest is FLEET policy and it stands: every lifecycle message goes to a concrete terminal or `dispatch:<id>`.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C046 — runtime/dispatch-lifecycle.md:130

 A `worker_done` for the active
  `taskId`+`dispatchId` auto-completes the task; do NOT follow it with `task-update --status completed` (reserve manual status writes for recovery/override).

**Unsatisfied:** Owning-pane success settles task and Dispatch; hostile/foreign or stale attempts not tested. Remaining procedure: Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** helper-tasks-after-done, helper-dispatch-after-done

## C047 — runtime/dispatch-lifecycle.md:132

- The runtime writes no `type=dispatch`/`type=handoff` rows on inject, though both are valid `send --type` values a fleet could write and the retired
  coordinator ignores. `merge_ready` is fleet-written only (merge-serialization.md); point at the evidence manifest with the typed `--report-path <path>`
  flag, never a `reportPath` payload key (orca-dag-semantics.md).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C048 — runtime/dispatch-lifecycle.md:138

The file ledger is the coordinator's durable brain; the Orca **worktree comment** is the live, human-glanceable status on the workspace card.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C049 — runtime/dispatch-lifecycle.md:138

 Workers update
it at checkpoints — `orca worktree set --worktree active --comment "<what is happening>" --workspace-status <todo|in-progress|in-review|completed>`.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C050 — runtime/dispatch-lifecycle.md:139

 It never
replaces the ledger (comments are best-effort and lossy).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C051 — runtime/dispatch-lifecycle.md:147

ledgered: `unit · worktree · retired ts`.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C052 — runtime/dispatch-lifecycle.md:147

 Name the verbs: terminals first with `terminal close --worktree <selector> --all`, the canonical teardown that stops
every process the workspace owns and durably removes its tabs, layouts, and resume records (`terminal-close.ts:8-14`; `terminal stop` is deprecated plumbing)
— then the tree with `worktree rm --worktree id:<repoId>::<path>` (`orca-cli:91`).

**Unsatisfied:** Exact-terminal close and clean worktree removal witnessed; bulk-close failure, archived output, tabs/layout/resume persistence not tested. Remaining procedure: Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** settle-helper-close, teardown-close-coordinator, teardown-close-shell, teardown-remove, teardown-path-absent

## C053 — runtime/dispatch-lifecycle.md:149

 A bulk close that cannot confirm every PTY is `unverifiable`, not clean:
ledger it as a leak, never force it.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C054 — runtime/dispatch-lifecycle.md:154

Each is one receipt away on an installed v1.4.199 and none needs a remote host; until run, these claims are source-witnessed only.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C055 — runtime/dispatch-lifecycle.md:156

1. `worker-start` per roster agent — record `state`, `stage`, `launch.effective`, `turnStart`, and the host's `agentDefaultArgs` permission mode.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C056 — runtime/dispatch-lifecycle.md:157

2. `dispatch --inject --json` receipt `prompt.stages`, then a `--retry-request` replay.

**Unsatisfied:** Owned inert terminal and original prompt bytes/request receipt. Dispatch-derived equivalence additionally needs coordinator-provided worker fixture. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an owned inert terminal capture an initial original-text --enter request; replay terminal send --terminal <owned> --retry-request <original-id> --wait-submit 1 --json, then correct missing original --text/--enter and compare request ID and terminal effects.

**Expected receipt:** Old shorthand refusal before effects; corrected replay result and original request identity, with no duplicate terminal input.

**Partial observations:** none

## C057 — runtime/dispatch-lifecycle.md:158

3.

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C058 — runtime/dispatch-lifecycle.md:158

 Mixed-batch `check` (does a `--types` wake deliver other types?) and `send --to @all --type merge_ready` in a scratch Run.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C061 — runtime/evidence-manifest.md:12

The worker writes it to the path the dispatcher passed as Orca's typed `--report-path` flag, and names that path in
the `worker_done` payload.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C062 — runtime/evidence-manifest.md:13

 Shape (JSON; a mission may add fields):

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C064 — runtime/gate-classification.md:8

 Times out
  (600 000 ms default, 1 800 000 ms cap) leaving the question PENDING — resume the SAME message id
  (`ask --resume <msg_id>`); re-asking under a new id creates a duplicate question.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C066 — runtime/gate-classification.md:11

 On CLI fleets this often writes **no**
  `decision_gates` table row — reply by message id.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C068 — runtime/gate-classification.md:16

**The option lists are spelled differently, and mixing them is a silent refusal:** `ask --options`
takes a **CSV** (`--options "rollback,patch-forward"`), `gate-create --options` takes a **JSON
array** (`--options '["rollback","patch-forward"]'`) (`orchestration.ts:203,253` at v1.4.199).

**Unsatisfied:** Owned scratch Run and task; coordinator-provided independent Dispatch fixture for preamble. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** none

## C069 — runtime/gate-classification.md:20

**`gate-resolve` does NOT inject the resolution into the next dispatch preamble.** That injection
exists only in the RETIRED scheduler path (`coordinator-task-dispatch.ts:130-139`); the live
`worker-start` / `dispatch --inject` preamble builder carries no gate context at all
(`deliver-worker-dispatch-preamble.ts`).

**Unsatisfied:** Live regenerated preamble lacks resolution marker after helper gate resolution; original injected-byte inspection and every launch path not proven. Remaining procedure: orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** helper-preamble, helper-gate, helper-resolve

## C070 — runtime/gate-classification.md:23

 So the resolution reaches the worker only if the
COORDINATOR puts it there: write it into the task spec (or the dispatch preamble) by hand before
re-dispatching.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C071 — runtime/gate-classification.md:25

 Treat the old promise as false until a probe shows otherwise — source-witnessed at
v1.4.199; live probe owed (`gate-create` → `gate-resolve` → `dispatch-show --task --preamble`) —
pin-it.

**Unsatisfied:** Owned scratch Run and task; coordinator-provided independent Dispatch fixture for preamble. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** none

## C072 — runtime/gate-classification.md:27

 A worker that was told "the gate is resolved" and receives no resolution will invent one.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C074 — runtime/gate-classification.md:32

 An ask with **no thread reply** while the unit is still
  dispatched is **always** current inbox work — reply by message id immediately.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C075 — runtime/gate-classification.md:33

 Do not wait for
  task status `blocked`.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C076 — runtime/gate-classification.md:34

 Do not use the unread bit alone (`check` marks read on receive).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C077 — runtime/gate-classification.md:35

- **Historical unanswered ask:** unit already terminal, no waiting worker — retained evidence
  that no answer was stored, **not** a reason to stall the fleet.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C079 — runtime/gate-classification.md:97

`ask` is agent-to-agent (worker→coordinator); a terminal handle is not a human.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C080 — runtime/gate-classification.md:97

 To reach a human:

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C081 — runtime/liveness-resume.md:3

The runtime tracks everything needed to keep a long run alive and recoverable, but it only WARNS on stalls; the
fleet must act.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C082 — runtime/liveness-resume.md:4

 Both live-supervision and crash-resume read the same persisted provenance (tasks,
dispatch_contexts with last_heartbeat_at/failure_count, worker_done payloads — all in SQLite, surviving restarts).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C083 — runtime/liveness-resume.md:9

Lifecycle authority is the payload's `taskId`+`dispatchId` verified against the dispatched pane — NOT a
terminal-handle comparison.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C084 — runtime/liveness-resume.md:10

 A pane can receive a new handle after a restart, so never accept or reject a
`worker_done`/`heartbeat` by matching handles; the runtime ignores a lifecycle message sent from a different
pane than the one that owns the dispatch.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C085 — runtime/liveness-resume.md:12

 When a handle returns `terminal_handle_stale`, re-resolve it with
`terminal list --worktree … --json` and continue with the replacement ONLY — never dual-send to the old and
new handles.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C086 — runtime/liveness-resume.md:18

`worker-list` is the ENUMERATING command and the authority on agent liveness.

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C087 — runtime/liveness-resume.md:18

 Each row carries
`projection.liveness` (the fleet verdict), `projection.attention.categories`,
`projection.attention.requiresAction`, and a literal `projection.nextAction.argv` to run. `worker-show`'s
`observation.status` is **PTY liveness only** — a `live` terminal can still hold an agent that died at a trust
prompt (`orchestration/recovery-and-cleanup:25-31` at v1.4.199).

**Unsatisfied:** Current helper row has projection fields; no agent death/trust prompt or host-loss experiment. Remaining procedure: Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** helper-show-before, helper-workers-bound

## C088 — runtime/liveness-resume.md:22

 The fleet taught this inverted for two runs;
it is the reason pane-reading felt authoritative.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C089 — runtime/liveness-resume.md:25

Always scope it: `worker-list --run <run_id>`.

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C091 — runtime/liveness-resume.md:30

- **`outcome_unknown`** — the start neither proved nor disproved the worker.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C092 — runtime/liveness-resume.md:30

 Inspect, then choose
  `worker-stop` or an explicit `worker-abandon`. `spawn_worker.sh` exits **4** here and prints the receipt's
  `nextCommands`.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C093 — runtime/liveness-resume.md:33

- **`unverifiable`** — absence, not a verdict (`missing_status`, `stale_status`, `restored_unconfirmed`,
  `host_unavailable`, a remote worker with no connection).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C094 — runtime/liveness-resume.md:34

 Absence **authorizes nothing**: never stop,
  abandon, retry, or release on it.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C095 — runtime/liveness-resume.md:35

 Keep waiting or inspect.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C096 — runtime/liveness-resume.md:42

- Poll `check --wait --types worker_done,escalation,question` ({count:0} timeout is a checkup tick, not an
  error). `--types` is only the WAKE condition — the Delivery still carries the whole FIFO batch, so process
  every message before `--ack` (orca-dag-semantics.md).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C097 — runtime/liveness-resume.md:44

 Keepalives (`{"_keepalive":true,…}`) go to **stderr**,
  never stdout — pipe stdout only into parsers (`runtime/scripts/pm.py <file>` for saved stdout streams).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C098 — runtime/liveness-resume.md:46

- **After 3 empty waits, ask the runtime instead of guessing:** `worker-list --run <id> --json`, then act on
  every row whose `attention.requiresAction` is true by executing its literal `nextAction.argv` (`inspect` /
  `release` / `recover`).

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C099 — runtime/liveness-resume.md:48

 That argv is the runtime's own answer; running it beats any heuristic the fleet
  could write.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C100 — runtime/liveness-resume.md:49

 A `nextAction` naming an INSPECTING command is asking for evidence, not authorizing cleanup.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C101 — runtime/liveness-resume.md:52

- Respawn a dead worker: log the evidence + a doctor-owned attempt count (NOT the runtime failure budget) →
  **reflection-before-retry** (below) → `task-update → ready` ONLY after the evidence line → `worker-start --task
  <id> --retry-of <failed dispatch id>` with a fresh placement (`--worktree`/`--agent`/`--terminal`, never the
  dead one). spawn_worker.sh's contract: exit 2 = usage or policy refusal (bad args, unknown agent, unmet deps,
  danger without opt-in) — SURFACE it, never retry as uncounted re-triage; every typed refusal (`task_not_found`,
  `task_not_startable` with `data.unmetDependencies`, `inject_rejected`, `nested_worker_depth_exceeded`,
  `consumer_fenced`, `dispatch_inactive`) branches the same way, carrying `error.data.nextSteps`.

**Unsatisfied:** Two owned scratch Runs and terminal tasks; no dispatch required for basic dependency validation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** none

## C102 — runtime/liveness-resume.md:58

 Exit 5 = a LIVE
  worker whose `launch.effective` does not prove the PROFILE's flag — STOP it, fix the host, never respawn.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C103 — runtime/liveness-resume.md:59

 Exit
  4 (`outcome_unknown`) is INSPECT, never respawn; exit 1 is an outright failed start — nothing live, retry per
  the reflection above.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C104 — runtime/liveness-resume.md:61

 Exit 3 (custom-argv: input accepted, turn unproven) is a POSSIBLE false negative — READ
  THE PANE first (`orca terminal read --terminal <h> --screen` or `worker-read --dispatch <id>`), not by eye: a
  live TUI is a working worker and respawning beside it is a dual-writer (dispatch-lifecycle.md).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C105 — runtime/liveness-resume.md:64

- BREAK at 3 doctor attempts OR the dispatch-context circuit break (3 consecutive failures marks the task

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C106 — runtime/liveness-resume.md:68

  a rewritten TASK, or park.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C107 — runtime/liveness-resume.md:68

 Counted toward the 3-attempt cap.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C108 — runtime/liveness-resume.md:69

- Re-confirm `ORCA_COORD_ALLOW_DANGER` before respawning a danger-profile worker.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C110 — runtime/liveness-resume.md:72

 Receipted sends shipped in v1.4.199
  (`terminal-send.ts:8,19-22`): a timeout returns the input-accepted receipt and never resends.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C111 — runtime/liveness-resume.md:73

 NEVER
  blind-re-Enter — `accepted: true` proves input acceptance, not a started turn, and the rule is never resend
  on silence.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C112 — runtime/liveness-resume.md:76

- A worker blocked on a human prompt shows `observation.agentWait` — a gate-classification problem, not a
  respawn (null and absent differ: absent means the host never reported).

**Unsatisfied:** Owned scratch Run and task; coordinator-provided independent Dispatch fixture for preamble. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** none

## C113 — runtime/liveness-resume.md:78

- NEVER run `orca orchestration reset` mid-run — it wipes the task/dispatch state every recovery path below
  depends on.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C114 — runtime/liveness-resume.md:79

 There is no mid-run situation it fixes that WATCH/RESUME doesn't.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C116 — runtime/liveness-resume.md:95

 The typo'd-dep strand
this file used to warn about cannot happen; a fleet that budgeted for it was defending a closed hole.

**Unsatisfied:** Two owned scratch Runs and terminal tasks; no dispatch required for basic dependency validation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** none

## C118 — runtime/liveness-resume.md:99

 A dep that ends **`failed`** therefore strands the child in `pending` FOREVER
— and convergence detection only flags `blocked`, never `pending`.

**Unsatisfied:** Failed predecessor leaves child pending at observation; indefinite temporal claim and convergence-detection implementation not live-tested. Remaining procedure: task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** fixture2-deps-after

## C119 — runtime/liveness-resume.md:100

 That strand is permanent: it is not a retry
of the child.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C120 — runtime/liveness-resume.md:101

 Every fleet keeps the watchdog for it — any task `pending` past a threshold with an unmet or
failed dep is surfaced, never silently waited on.

**Unsatisfied:** Two owned scratch Runs and terminal tasks; no dispatch required for basic dependency validation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** none

## C121 — runtime/liveness-resume.md:102

 Edges are `deps`; `parent_id` exists but the fleet does not
set it (orca-dag-semantics.md).

**Unsatisfied:** Two owned scratch Runs and terminal tasks; no dispatch required for basic dependency validation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** none

## C122 — runtime/liveness-resume.md:107

The orchestration DB mixes every run on the machine.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C123 — runtime/liveness-resume.md:107

 WATCH and RESUME operate only on the run's scope: the
**Run id** from the ledger header (`task-list --run`, `worker-list --run`, `check` all honor it) plus the
ledger's task ids.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C124 — runtime/liveness-resume.md:109

 Unfiltered `task-list` is a discovery tool, not the run.

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C125 — runtime/liveness-resume.md:137

2.

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C126 — runtime/liveness-resume.md:137

 Bind the run: the new coordinator adopts it with `run-use --id <run>` — and if the run predates an Orca
   contract update (legacy rows, authority labels on its mail), take it over explicitly with `run-use --id
   <run> --takeover-legacy` **from the live coordinator terminal** (upstream's adoption protocol preserves
   live workers' dispatches, processes, and filesystems and routes their later questions to the current
   coordinator — an Orca upgrade mid-run is no longer a hand-recovery).

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C127 — runtime/liveness-resume.md:141

 A dispatch re-attaching under a new
   coordinator shows `consumer_fenced`; the fenced old coordinator's mutations are rejected.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C128 — runtime/liveness-resume.md:142

 Caveats that make
   the takeover safe: never take over while the ORIGINAL coordinator is still active (that is the dual-writer
   class with extra steps); `--from` cannot nominate the taker, so it must be run from the terminal that will
   hold the run; `run_legacy_local` is an empty tombstone, so find the Run whose objective reads `Recovered
   orchestration work from a contract update`; and when authority is unproven, degrade to read-only inspection
   rather than adopting (`orchestration/legacy-contract-migration:19-23,69-83` at v1.4.199).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C129 — runtime/liveness-resume.md:148

3.

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C130 — runtime/liveness-resume.md:148

 REBUILD from provenance; CROSS-VERIFY every "completed" against git (evidence-manifest.md) —

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C131 — runtime/merge-serialization.md:9

Workers/integrators emit `send --to <conductor-handle> --subject "merge_ready <unit>" --type
merge_ready --payload '{"unit":"<id>","pr":123,"branch":"<head>","reviewed_sha":"<sha>","reviewed_wtree":"<tree sha of the reviewed content>","base":"<BASE>"}'`
(`--subject` is mandatory; `--payload` must be real JSON, not shorthand). `merge_ready` is a
first-class Orca message type with NO built-in behavior — the runtime delivers it and stops, so the
fleet owns the queue semantics.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C132 — runtime/merge-serialization.md:17

- **`--to` is optional** from an active Dispatch — an omitted recipient defaults to the owning Run
  mailbox, which is the coordinator inbox and the address upstream prefers (`orchestration.ts:76`).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C133 — runtime/merge-serialization.md:19

  Naming the conductor handle explicitly stays correct and stays this fleet's convention, because a
  merge queue has exactly one owner and the handle says so.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C134 — runtime/merge-serialization.md:21

- **A `merge_ready` to a group is NOT rejected.** The runtime refuses group addresses for
  `worker_done` and `heartbeat` only (`message-send-handler.ts:51-58`); a `merge_ready --to @all`
  would fan out to every worker and put N writers on one BASE.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C135 — runtime/merge-serialization.md:23

 Nothing below the fleet stops that,
  so the rule stands on our discipline alone: **never address a `merge_ready` to a group.**

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C136 — runtime/merge-serialization.md:28

1.

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C137 — runtime/merge-serialization.md:28

 BOARD: `check --wait --types merge_ready,worker_done,escalation` → append in ARRIVAL ORDER.
   `--types` is the WAKE condition only: the Delivery that comes back is the whole FIFO batch, every
   type in it (orca-dag-semantics.md).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C138 — runtime/merge-serialization.md:30

 Process the ENTIRE Delivery — settle the `worker_done`s, reply
   to the `question`s, board the `merge_ready`s — and only then `--ack <delivery_id>`.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C139 — runtime/merge-serialization.md:31

 Acking after

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C140 — runtime/mission-scheduling.md:3

Orca `automations` run a prompt on a schedule (cron / `hourly` / `daily` / `weekdays` / `weekly` /
RRULE) against a fresh per-run worktree or an existing workspace.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C141 — runtime/mission-scheduling.md:4

 A scheduled mission is that: an
UNATTENDED coordinator invocation of a mission on a cadence — a nightly `clean-sweep`, a weekday
`review-it` sweep of open PRs.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C142 — runtime/mission-scheduling.md:11

orca automations create --name "<name>" --trigger daily --time 03:00 --timezone "<IANA zone>" \
  --precheck "<cheap command that exits 0 iff there is work>" \
  --prompt "<the mission invocation, e.g. 'clean-sweep source=tracker on this repo'>" \
  --provider <coordinator agent> --repo id:<repoId> --json

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C143 — runtime/mission-scheduling.md:17

`--repo` gives each run a fresh worktree (preferred for missions — clean BASE per run); `--workspace`
targets an existing one. `--disabled` while testing.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C144 — runtime/mission-scheduling.md:18

 The provider is the COORDINATOR; workers still
spawn per the roster (sandbox-policy.md).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C145 — runtime/mission-scheduling.md:23

**Every scheduled mission passes `--precheck`.** It runs a bounded command before the run; exit 0
continues, anything else records a **skipped** run and spawns nothing (`automations.ts:62` at
v1.4.199).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C146 — runtime/mission-scheduling.md:25

 That is exactly the enumeration question a mission asks in its first phase — and without
it, a nightly sweep of an empty backlog pays a full preflight, a coordinator, and a run report to

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C147 — runtime/mission-scheduling.md:32

Also on `create`/`edit`: `--timezone` (a cron with no zone drifts against the team's day),
`--missed-run-grace-minutes` (how late a missed fire may still run — past it the run is dropped, not
silently deferred), `--reuse-session` / `--fresh-session` (existing-workspace automations only;
prefer `--fresh-session` for missions, since a reused session carries the last run's context into a
run whose whole premise is independence), and `--host runtime:<environment-id>` to place the
scheduled coordinator on a paired Orca server rather than the mortal desktop — pass the id from
`orca environment list`, never the environment's name.

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C148 — runtime/mission-scheduling.md:40

`automations run <id>` fires one now (test a schedule without waiting for it); `automations runs
--id <id>` is the run history, and it is the **cross-run anti-inflation input** the fleet currently
reconstructs by hand from `docs/runs/` — a recurring mission reads it to see how many of the last N
fires were `skipped` before believing a streak of green reports.

**Unsatisfied:** Owned automation fixture; assurance no provider executes and no global scheduling mutation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Create disabled scratch automation after teardown discovery; exercise schedule parsing and precheck-skip without agent launch; inspect runs then delete only owned automation.

**Expected receipt:** Stored schedule fields, skipped precheck receipt with no launched provider, exact teardown.

**Partial observations:** none

## C149 — runtime/orca-dag-semantics.md:3

Ground truth about how Orca's orchestration DAG behaves for fleets that drive it with CLI verbs
(`run-create` / `task-create` / `worker-start` / `check` / `send`).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C150 — runtime/orca-dag-semantics.md:4

 Sourced from live-DB research
plus the version-matched guide the binary serves (`orca skills get orchestration`); treat as
operational contract, not product marketing.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C151 — runtime/orca-dag-semantics.md:6

 Current schema line: v40.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C152 — runtime/orca-dag-semantics.md:10

`run-create` / `run-use` / `run-current` / `run-list` / `run-show` give the fleet a first-class
namespace and coordinator inbox.

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C153 — runtime/orca-dag-semantics.md:11

 Every task belongs to one explicitly bound Run, and the scope
verbs honor it: `task-list --run <id>`, `worker-list --run <id>`, the coordinator's `check`.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C154 — runtime/orca-dag-semantics.md:12

 The
retired scheduler commands (`orchestration run`, `coordinator-start/stop`) perform no effects and
return the current-skill recovery action — never call them.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C155 — runtime/orca-dag-semantics.md:17

Never converge, WATCH, or RESUME against an unfiltered `task-list` — unscoped lists bury live rows
under every past run on the machine (nothing prunes automatically).

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C156 — runtime/orca-dag-semantics.md:18

 A foreign run's completed tasks
are not your wins; a foreign pending is not your stall.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C157 — runtime/orca-dag-semantics.md:21

**Nested depth:** `nested_worker_depth_exceeded` is counted from the ISSUING terminal, not from the
Run — a dispatched worker creating a fresh Run and calling `worker-start` is still a worker, and
still blocked at the default depth of 1 (dispatch-lifecycle.md).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C158 — runtime/orca-dag-semantics.md:27

`tasks.deps` (JSON array of task ids) is the dependency graph the runtime promotes against.
`parent_id` is a decomposition hierarchy that is empty in real CLI fleets **only because the
fleet never sets it** — `task-create --parent <task_id>` and `worker-start --parent` do exist
and do write it, validated to the same Run, and worker-terminal listing/attention queries read
it (`orchestration.ts:134`, `task-store.ts:32-36` at v1.4.199).

**Unsatisfied:** Two owned scratch Runs and terminal tasks; no dispatch required for basic dependency validation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** none

## C159 — runtime/orca-dag-semantics.md:31

 Do not build or verify fleets
on parent/child nesting, but do not call the column unwritable either.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C160 — runtime/orca-dag-semantics.md:39

These `MessageType` values exist in the schema but **nothing writes them** on CLI/agent paths:

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C161 — runtime/orca-dag-semantics.md:41

| Type | Reality |

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C162 — runtime/orca-dag-semantics.md:42

|------|---------|

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C163 — runtime/orca-dag-semantics.md:43

| `dispatch` | Prompt is injected into the worker PTY; no message row.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C164 — runtime/orca-dag-semantics.md:43

 Reconstruct from the dispatch record + `tasks.spec`. |

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C165 — runtime/orca-dag-semantics.md:44

| `handoff` | Unused by the runtime. |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C166 — runtime/orca-dag-semantics.md:46

`merge_ready` is **fleet-written** (merge-serialization.md), not a phantom type — the runtime
delivers it but triggers no built-in merge behavior.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C167 — runtime/orca-dag-semantics.md:47

 Expect it during serialized merges.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C168 — runtime/orca-dag-semantics.md:49

What *is* real and load-bearing: `worker_done`, `merge_ready`, `heartbeat`, `question`,
`escalation`, `status`. `decision_gate`, `dispatch` and `handoff` are all valid `send --type`
values a fleet *could* write (`orchestration.ts:71` lists all nine); the runtime writes a
`decision_gate` only on the legacy direct-ask path (`legacy-ask-operation.ts:101`) and migrates
existing ones to `status` (`message-inbox.ts:81`), and writes no `dispatch` or `handoff` at all.
`decision_gate` sat in the load-bearing list until #302 — not because the CLI refuses it, which is
what that issue supposed, but because the runtime has stopped producing it.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C170 — runtime/orca-dag-semantics.md:59

 So
heartbeats never "bury" lifecycle mail — but a loop that handles only the filtered type and then
`--ack`s has just acknowledged the rest unprocessed.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C171 — runtime/orca-dag-semantics.md:61

 Process the whole Delivery, then ack
(dispatch-lifecycle.md).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C172 — runtime/orca-dag-semantics.md:66

A coordinator `check` returns the Run's oldest FIFO **Delivery** (up to 50 messages) and replays
that exact batch until `--ack <delivery_id>` — the mailbox commits the delivery before waking the
coordinator, so a crash between receive and process never loses mail.

**Unsatisfied:** Batch/replay/ack witnessed; crash durability cannot be probed while parent fleet is live. Remaining procedure: Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** mailbox-delivery, mailbox-replay, mailbox-ack

## C173 — runtime/orca-dag-semantics.md:68

 Process the whole batch,
then ack.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C174 — runtime/orca-dag-semantics.md:69

 Every mutation accepts `--retry-request <id>` (`request-show` inspects): re-issuing with
the same id is deduped, so a lost response never double-dispatches.

**Unsatisfied:** Terminal prompt retry witnessed; every orchestration mutation/restart/pending recovery branch is not covered. Remaining procedure: On an owned inert terminal capture an initial original-text --enter request; replay terminal send --terminal <owned> --retry-request <original-id> --wait-submit 1 --json, then correct missing original --text/--enter and compare request ID and terminal effects.

**Probe owed:** On an owned inert terminal capture an initial original-text --enter request; replay terminal send --terminal <owned> --retry-request <original-id> --wait-submit 1 --json, then correct missing original --text/--enter and compare request ID and terminal effects.

**Expected receipt:** Old shorthand refusal before effects; corrected replay result and original request identity, with no duplicate terminal input.

**Partial observations:** retry-original-exact, effect-original-replay

## C175 — runtime/orca-dag-semantics.md:74

`tasks.status` is overwritten in place by many writers. `pending → ready` promotion is
**silent and untimestamped**.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C176 — runtime/orca-dag-semantics.md:75

 Reconstructible facts: creation, each dispatch attempt
(latest = the active dispatch; `failure_count` carries MAX forward; circuit trips at 3),
completion via `worker_done`.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C177 — runtime/orca-dag-semantics.md:81

from the owning pane auto-completes the task — do not also `task-update --status completed`.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C178 — runtime/orca-dag-semantics.md:82

A dispatch re-attaching after a restart surfaces `consumer_fenced` — the old coordinator is
fenced; only the current binding's calls mutate.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C179 — runtime/orca-dag-semantics.md:87

A run is **converged** only when every task in the **Run's task set** is terminal
(`completed` or `failed`), no live worker ask is waiting on the coordinator (dispatched unit +
ask thread with no reply — not merely unread), and no `gate-create` hold remains for those tasks.

**Unsatisfied:** Owned scratch Run and task; coordinator-provided independent Dispatch fixture for preamble. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** none

## C180 — runtime/orca-dag-semantics.md:90

Not converged:

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C181 — runtime/orca-dag-semantics.md:92

- any `pending` / `ready` / `dispatched` / `blocked` in scope

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C182 — runtime/orca-dag-semantics.md:93

- live ask (dispatched unit, ask without reply) even if the message is already `read`

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C183 — runtime/orca-dag-semantics.md:94

- a `pending` child whose dep **failed** or never existed (never auto-promotes — stuck-pending
  watchdog must surface it; a failed dep is a permanent strand, not a retry)

**Unsatisfied:** Two owned scratch Runs and terminal tasks; no dispatch required for basic dependency validation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** none

## C184 — runtime/orca-dag-semantics.md:103

1.

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C186 — runtime/orca-dag-semantics.md:103

 The worker CLI
   **blocks until reply or timeout**; a timeout leaves the question PENDING — resume it with
   `ask --resume <message_id>` (the same id, never a duplicate ask).

**Unsatisfied:** Ask/reply witnessed; helper timeout and resume branch not exercised because fixture replied immediately. Remaining procedure: Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** helper-check-0, helper-reply

## C188 — runtime/orca-dag-semantics.md:107

2.

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C190 — runtime/orca-dag-semantics.md:113

| **Live ask** | A worker unit is still `dispatched` and its `question` has **no reply** yet (do **not** rely on the unread bit alone — `check` marks read on receive) | **Always blocking inbox work.** Reply by `message id` (`reply --id`) promptly — do not wait for task status `blocked` (it will not come).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C191 — runtime/orca-dag-semantics.md:113

 Ignoring it burns the ask timeout.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C192 — runtime/orca-dag-semantics.md:113

 On RESUME, re-scan threads for asks without replies while the unit is still dispatched. |

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C193 — runtime/orca-dag-semantics.md:114

| **Historical unanswered** | Unit already terminal / no waiting worker; ask with or without a reply left in history | **Not** a fleet stall.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C194 — runtime/orca-dag-semantics.md:114

 Do not spin the run waiting on it. |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C195 — runtime/orca-dag-semantics.md:115

| **DAG hold** | `gate-create` → task `blocked` | DAG blocker until `gate-resolve` or park as one-way human. |

**Unsatisfied:** Owned scratch Run and task; coordinator-provided independent Dispatch fixture for preamble. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** none

## C196 — runtime/orca-dag-semantics.md:123

`worker_done.payload` and `tasks.result` are free-form TEXT.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C197 — runtime/orca-dag-semantics.md:123

 The fleet's SHA-bound evidence
manifest (evidence-manifest.md) is the definition of done; still make retained orchestration
history point at the same artifacts — but via the TYPED flags, `--report-path <path>` and
`--files-modified <csv>`, not a hand-rolled `reportPath` payload key.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C198 — runtime/orca-dag-semantics.md:126

 Upstream's own rule is
"prefer `--task-id`/`--dispatch-id`/etc. over raw `--payload` JSON" (`orchestration.ts:49,79` at
v1.4.199): PowerShell strips JSON quotes, and a typed flag cannot be misspelled silently.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C199 — runtime/sandbox-policy.md:4

tiers use each agent's **fully-autonomous flag** (`src/shared/tui-agent-permissions.ts` — in
[stablyai/orca](https://github.com/stablyai/orca), not this repo; the agent → flag map lives there,
and its contents are re-witnessed, not remembered: pin-it).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C200 — runtime/sandbox-policy.md:6

 The sandboxed middle modes (claude
`acceptEdits`, codex `--sandbox workspace-write`, gemini `auto_edit`) are deliberately NOT used:
they still prompt on shell and network, so a build worker running tests or `npm install` would
block.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C201 — runtime/sandbox-policy.md:11

**Say "by default" precisely.** What a `worker-start` launch actually appends is the host's
`agentDefaultArgs` profile setting, not this map directly.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C202 — runtime/sandbox-policy.md:12

 Its MIGRATED DEFAULT is this map —
`tui-agent-launch-defaults.ts:10` re-exports `YOLO_TUI_AGENT_ARGS` as `DEFAULT_TUI_AGENT_ARGS` — but
a host whose owner chose manual mode carries `''` instead.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C203 — runtime/sandbox-policy.md:14

 Two consequences, opposite in sign: on a
default host a supervised `PROFILE=ro` launch would be silently upgraded to bypass (which is why ro
never takes `worker-start`, dispatch-lifecycle.md); on a manual host, `worker-start` launches
PROMPTING workers while the fleet believes they are autonomous, and the run blocks on invisible
dialogs.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C204 — runtime/sandbox-policy.md:18

 Neither is knowable from source: read `launch.effective` off the start receipt and record
the host's permission mode in the ledger header.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C205 — runtime/sandbox-policy.md:19

 Source-witnessed at v1.4.199
(`tui-agent-launch-defaults.ts:10`); live probe owed — pin-it.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C206 — runtime/sandbox-policy.md:22

`spawn_worker.sh` maps each PROFILE per agent.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C207 — runtime/sandbox-policy.md:22

 **Orca has no read-only tier for ANY agent** — its
only map is `YOLO_TUI_AGENT_ARGS` (`tui-agent-permissions.ts:6-33`), which is autonomous flags and
nothing else.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C208 — runtime/sandbox-policy.md:24

 Every entry in the `ro` column below is that agent's OWN native flag, chosen here; the
dashes are agents for which no such flag has been verified, not agents Orca singles out.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C209 — runtime/sandbox-policy.md:25

 The note
used to read "(no RO in Orca)" beside two of them, which implied Orca supplied the others (#302).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C210 — runtime/sandbox-policy.md:28

| Agent  | `ro` (read-only review) | `rw` = `danger` flag (autonomous, non-blocking) |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C211 — runtime/sandbox-policy.md:29

|--------|-------------------------|--------------------------------------------------|

**Unsatisfied:** Context/delimiter fragment in the conservative frozen extraction; retain its ID and source bytes, do not count it as successful runtime proof. Independent atomization must link it to the surrounding source paragraph without silently shrinking the frozen denominator.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C212 — runtime/sandbox-policy.md:30

| claude | `--permission-mode plan` | `--dangerously-skip-permissions`                |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C213 — runtime/sandbox-policy.md:31

| codex  | `--sandbox read-only`    | `--dangerously-bypass-approvals-and-sandbox`    |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C214 — runtime/sandbox-policy.md:32

| gemini | `--approval-mode plan`   | `--yolo`                                        |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C215 — runtime/sandbox-policy.md:33

| cursor | — none verified → WORKER_CMD | `--yolo` (`tui-agent-permissions.ts:21`)     |

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C216 — runtime/sandbox-policy.md:34

| grok   | — none verified → WORKER_CMD | `--permission-mode bypassPermissions`        |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C217 — runtime/sandbox-policy.md:35

| droid  | WORKER_CMD               | `--auto high`                                   |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C218 — runtime/sandbox-policy.md:36

| opencode / kilo | WORKER_CMD      | WORKER_CMD — Orca **strips** `--dangerously-skip-permissions` from both (`tui-agent-launch-defaults.ts:5-8`) |

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C219 — runtime/sandbox-policy.md:37

| omp / pi | WORKER_CMD             | WORKER_CMD (not in Orca's autonomous-arg map)   |

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C220 — runtime/sandbox-policy.md:39

- **`ro`** is non-blocking because it cannot mutate — nothing to approve.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C221 — runtime/sandbox-policy.md:39

 It is the permission
  boundary for report-only missions (review-it).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C222 — runtime/sandbox-policy.md:67

(`orca-per-workspace-env` recipes: create/suspend/resume/destroy, `orca serve --recipe-json`
pairing, validated by `vm recipe doctor <recipe-id> --provision`; `--connect` is a synonym of
`--provision`).

**Unsatisfied:** Coordinator-provided disposable provider/recipe; no paid or credential provisioning in this unit. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an authorized disposable environment replay vm recipe doctor <owned-recipe> --provision and inspect warn/fail fields; verify pairing identity only with owned noncredential fixture.

**Expected receipt:** Exact doctor schema and warnings plus distinct pairing/placement facts.

**Partial observations:** none

## C223 — runtime/sandbox-policy.md:73

- **`doctor` is clear only with no `fail` AND no `warn`.** `ok:true` on its own proves nothing —
  a warn is a lane that boots and then fails a build halfway through
  (`orca-per-workspace-env:346-348`). `spawn_worker.sh` **runs the doctor itself** (#283):
  `PROFILE=danger` needs `ORCA_COORD_ALLOW_DANGER=1`, a valid `ORCA_SANDBOX_RECIPE`, and `orca` on
  PATH; the script runs `vm recipe doctor <recipe> --provision` and reads the verdict via
  `sandbox_doctor.py`. `ORCA_SANDBOX_DOCTOR` is an **output** path: where that transcript is
  written for the lane ledger.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C224 — runtime/sandbox-policy.md:79

 A transcript the caller names is not evidence.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C225 — runtime/sandbox-policy.md:80

- **Never snapshot a machine on which `orca serve` has already run.** The pairing identity is
  baked in, so every clone of that snapshot claims to be the same Orca server — the fleet then
  cannot tell two sandboxes apart, and remote placement resolves to the wrong host.

**Unsatisfied:** Coordinator-provided disposable provider/recipe; no paid or credential provisioning in this unit. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an authorized disposable environment replay vm recipe doctor <owned-recipe> --provision and inspect warn/fail fields; verify pairing identity only with owned noncredential fixture.

**Expected receipt:** Exact doctor schema and warnings plus distinct pairing/placement facts.

**Partial observations:** none

## C226 — runtime/sandbox-policy.md:82

 Snapshot
  BEFORE `serve`, or not at all.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C227 — runtime/scripts/deny-hook.sh:37

#   4. `orca orchestration reset` — one command that discards a whole fleet's
#      dispatch state
# Git global options between `git` and the subcommand (-C, -c, --git-dir and

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C228 — runtime/scripts/deny-hook.sh:721

  if has '^[[:space:]]*(sudo[[:space:]]+)?orca(-ide)?[[:space:]]+orchestration[[:space:]]+reset([[:space:]]|$)'; then
    decide deny "deny-hook[HIGH]: 'orca orchestration reset' discards the whole fleet's dispatch state.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C229 — runtime/scripts/deny-hook.sh:722

 A worker never resets the orchestration it runs inside."

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C230 — runtime/scripts/pm.py:2

# pm.py — tolerant parser for `orca orchestration inbox/check` JSON output. (v3)
# Keepalives ({"_keepalive":true,...}) arrive on STDERR every 15 s — never on stdout; a capture
# that merged 2>&1 breaks naive json.load.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C231 — runtime/scripts/pm.py:4

 Pipe stdout only, or filter keepalives before parsing.
# This decodes successive JSON objects, skips keepalive-only envelopes STRUCTURALLY (not by line
# filtering, which could drop a mixed keepalive+messages object), and prints each message.
#
# v3 (2026-09-10 upstream re-pin): the skip keys on `_keepalive` FIRST.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C232 — runtime/scripts/pm.py:8

 A keepalive line carries
# both `_keepalive` and `_heartbeat`, but `_heartbeat` is only a deprecated alias retained for
# scripts still filtering it during migration (`check-keepalive.ts:18-26` at Orca v1.4.199) —
# v2 keyed on the alias alone, so it was correct by accident and would start miscounting every

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C233 — runtime/scripts/pm.py:21

# Usage:  orca orchestration inbox --json > inbox.json && python3 pm.py inbox.json

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C234 — runtime/scripts/pm.py:91

        result = obj.get("result")
        batch = result.get("messages") if isinstance(result, dict) else None
        if not isinstance(batch, list):
            batch = None  # a wrong-typed 'messages' (e.g. a string) is not a batch
        if batch is None and _has_messages_key(obj):
            # Message-bearing shape we don't parse — 'messages' misplaced at any depth
            # ({"messages": [...]}, {"data": {"messages": [...]}}, wrong-typed, or riding
            # inside a heartbeat envelope).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C235 — runtime/scripts/pm.py:98

 Checked BEFORE the heartbeat skip so it can't
            # be swallowed; counting it as empty would misread a real inbox as empty.
            unrecognized += 1
            continue
        if ("_keepalive" in obj or "_heartbeat" in obj) and not batch:
            # Keepalive-only envelope; a mixed object still yields its messages below.
            # `_keepalive` is the CURRENT marker and is checked FIRST; `_heartbeat` rides the
            # same line only as a deprecated alias kept "for scripts still filtering it while
            # callers migrate" (`check-keepalive.ts:18-26` at Orca v1.4.199).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C236 — runtime/scripts/pm.py:106

 Keying on the
            # alias alone — as v2 did — starts counting every keepalive as an unrecognized
            # envelope the day upstream drops it.
            continue
        for m in batch or []:
            if isinstance(m, dict):
                msgs.append(m)

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C237 — runtime/scripts/pm.py:114

    print("MESSAGES:", len(msgs))
    for m in msgs:
        print("=" * 60)
        print("ID:", _visible(m.get("id", "?")), "| FROM:", _visible(m.get("from_handle", "?")),
              "| TYPE:", _visible(m.get("type", "?")))
        print("SUBJ:", _visible(m.get("subject", "?")))
        print("BODY:", _visible(m.get("body", "")))
        print("PAYLOAD:", _visible(m.get("payload")))
    if skipped:

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C238 — runtime/scripts/sandbox_doctor.py:2

"""Read an `orca vm recipe doctor <recipe> --provision` transcript and say whether it is CLEAR.

**Unsatisfied:** Coordinator-provided disposable provider/recipe; no paid or credential provisioning in this unit. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an authorized disposable environment replay vm recipe doctor <owned-recipe> --provision and inspect warn/fail fields; verify pairing identity only with owned noncredential fixture.

**Expected receipt:** Exact doctor schema and warnings plus distinct pairing/placement facts.

**Partial observations:** none

## C239 — runtime/scripts/sandbox_doctor.py:4

sandbox-policy.md states the rule the `danger` lane rests on: clear means **no `fail` AND no
`warn`**; `ok:true` on its own proves nothing, because a warn is a lane that boots and then fails
a build halfway through (`orca-per-workspace-env:110-122`).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C240 — runtime/scripts/sandbox_doctor.py:32

# Status/level values that are a doctor telling you something is wrong.

**Unsatisfied:** Coordinator-provided disposable provider/recipe; no paid or credential provisioning in this unit. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an authorized disposable environment replay vm recipe doctor <owned-recipe> --provision and inspect warn/fail fields; verify pairing identity only with owned noncredential fixture.

**Expected receipt:** Exact doctor schema and warnings plus distinct pairing/placement facts.

**Partial observations:** none

## C241 — runtime/scripts/sandbox_doctor.py:33

BAD_STATUS = {"fail", "failed", "failing", "failure", "error", "errored", "warn", "warning"}
# Keys whose CONTENTS are the findings, so an empty one is good news.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C242 — runtime/scripts/sandbox_doctor.py:35

FINDING_KEYS = ("failures", "warnings", "errors", "problems", "issues")
# Keys whose VALUE is a verdict word.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C243 — runtime/scripts/sandbox_doctor.py:37

STATUS_KEYS = ("status", "level", "severity", "state", "result")

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C244 — runtime/scripts/spawn_worker.sh:4

# v5 contract (2026-09-10 upstream re-pin).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C245 — runtime/scripts/spawn_worker.sh:4

 Every mechanism below is source-witnessed at the TAG
#   v1.4.199 — the shipped binary — not at upstream HEAD, which has already moved past it:
#   - supervised lane = `worker-start` (compose: worktree + agent terminal + readiness + dispatch).
#     READINESS SEMANTIC: at v1.4.199 `ready` means the preamble WRITE WAS ACCEPTED, not that the
#     agent started a turn (`local-worker-start.ts:263` marks the dispatch ready straight after the
#     accepted write).

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C246 — runtime/scripts/spawn_worker.sh:9

 The next release flips this to a positive `turn_started`, returning
#     `state: outcome_unknown` otherwise — which is why exit 4 exists below, before that upgrade
#     lands.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C247 — runtime/scripts/spawn_worker.sh:11

 Readiness per agent is source-witnessed at v1.4.199
#     (`local-worker-start.ts:243-263`); live probe owed — pin-it.
#   - typed refusals: branch on `error.code`, NEVER on stderr text, and print `error.data.nextSteps`
#     verbatim — that array is the runtime's own recovery text
#     (`orchestration-dispatch-refusal-contract.ts:8`,
#     `orchestration/recovery-and-cleanup:96-108`).
#   - `state: outcome_unknown` is NOT a failure: it is an unproven outcome.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C248 — runtime/scripts/spawn_worker.sh:17

 Exit 4, print the
#     receipt's `nextCommands`, and INSPECT — never respawn (respawning beside a live pane is the
#     dual-writer class) (`worker-start-receipt.ts:48,60-68`).
#   - Exit 5 = LAUNCHED_UNUSABLE: the start succeeded, so a worker IS live, but `launch.effective`
#     does not prove the PROFILE's flag was applied — it lacks the flag, or the host omitted the
#     field entirely.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C249 — runtime/scripts/spawn_worker.sh:22

 Not a failure (something started) and not unknown (we know it did): STOP the
#     worker, never respawn beside it, then fix the host (sandbox-policy.md:16-20).
#   - custom-argv lane = `terminal create` + `dispatch --inject`.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C250 — runtime/scripts/spawn_worker.sh:24

 The inject ALREADY SUBMITS the
#     preamble (`dispatch-methods.ts:155-165` calls `sendTerminalAgentPrompt`) and `--json` returns
#     `result.prompt{requestId, stages}`, stages drawn from `input_accepted | turn_started`
#     (`runtime-terminal-contracts.ts:221-225`). v4's blind re-Enter/heartbeat loop is DELETED:
#     the guide's rule is "never resend on silence"
#     (`orchestration/recovery-and-cleanup:92-94`).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C251 — runtime/scripts/spawn_worker.sh:29

 When `turn_started` is absent we replay the
#     receipt ONCE with
#     `terminal send --retry-request <requestId> --wait-submit <secs>` — a replay, never a resend
#     ("timeout returns the queued/input-accepted receipt and never resends",
#     `terminal-send.ts:19-22`).

**Unsatisfied:** Owned inert terminal and original prompt bytes/request receipt. Dispatch-derived equivalence additionally needs coordinator-provided worker fixture. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an owned inert terminal capture an initial original-text --enter request; replay terminal send --terminal <owned> --retry-request <original-id> --wait-submit 1 --json, then correct missing original --text/--enter and compare request ID and terminal effects.

**Expected receipt:** Old shorthand refusal before effects; corrected replay result and original request identity, with no duplicate terminal input.

**Partial observations:** none

## C252 — runtime/scripts/spawn_worker.sh:33

 At v1.4.199 that flag pair also REQUIRES `--text` with `--enter`
#     (`terminal-send.ts:17-24` handler), so the exact preamble is recovered first via
#     `dispatch-show --task <id> --preamble` (`dispatch-methods.ts:196-213`); if it cannot be
#     recovered, or the host refuses the replay, the lane reports UNPROVEN rather than resending.
#     Whether the regenerated preamble byte-matches the injected payload the requestId is bound to
#     is source-witnessed only (`dispatch-methods.ts:199-212` omits dispatchCapability);
#     live probe owed — pin-it.
#   - `terminal wait` result is READ: `wait.satisfied:false` is an unsatisfied condition.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C253 — runtime/scripts/spawn_worker.sh:40

 The CLI
#     also sets exit 1 for it (`terminal.ts:126-130`), so v4 failed closed BY ACCIDENT; v5 reads
#     the field, so a host that sets only one of the two still fails closed.
#   - PROFILE=ro NEVER takes worker-start: launch args come from the host's `agentDefaultArgs`
#     profile setting, whose migrated default IS the YOLO map (`tui-agent-launch-defaults.ts:10`
#     re-exports `YOLO_TUI_AGENT_ARGS` as `DEFAULT_TUI_AGENT_ARGS`), so a default host would
#     silently upgrade a read-only reviewer to a bypass one.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C254 — runtime/scripts/spawn_worker.sh:46

 A host set to manual mode has `''`
#     instead — the rationale is host-dependent, not universal. `agentDefaultArgs` is
#     source-witnessed at v1.4.199 (`tui-agent-launch-defaults.ts:10`); live probe owed — pin-it.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C255 — runtime/scripts/spawn_worker.sh:69

#   SP=<dir> [PROFILE=rw] spawn_worker.sh [--mark-ready] <task_id> <worktree_selector> <title> [agent] [effort]
#   agent ∈ claude|codex|cursor|gemini|grok|droid|opencode|omp|pi (default claude)
# Prints:  supervised: HANDLE=<h> READY=<state>, DISPATCH=<id>, and LAUNCH_EFFECTIVE=<json> when the
#          receipt carries it.  custom-argv lane: HANDLE=<h> STAGES=<csv>
#
# Agent × profile coverage (flags are Orca's own autonomous "yolo" args from
# `tui-agent-permissions.ts:6-33`, so workers never block on a prompt; anything else fails closed
# and needs WORKER_CMD):
#   claude/codex/gemini → ro + rw + danger
#   cursor              → rw + danger (`tui-agent-permissions.ts:21` maps cursor to `--yolo`; Orca
#                         has no read-only mode for it) — also one of the three agents that
#                         `--model`/`--effort` can target
#   grok                → rw + danger (Orca has no read-only mode for grok)
#   droid               → rw + danger (Orca appends `--auto high`); ro → WORKER_CMD
#   opencode/omp/pi     → WORKER_CMD. opencode AND kilo are actively STRIPPED of
#                         `--dangerously-skip-permissions` (`tui-agent-launch-defaults.ts:5-8`);
#                         kilo stays off this roster for the same reason opencode fails closed.
# rw and danger use the SAME non-blocking flag; danger only adds the ALLOW_DANGER gate + the
# ephemeral-sandbox requirement (sandbox-policy.md). worker-start's `--effort` requires `--model`
# (a provider model id the fleet does not pin) — the validated `effort` arg applies on the
# override lane's launch command; the supervised path takes the agent's configured default.
#
# NOTE: <worktree_selector> is a RAW orca selector.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C256 — runtime/scripts/spawn_worker.sh:91

 A worktree id is the composite
#   `<repoId>::<worktreePath>` from `worktree create --json` — pass `path:/abs/worktree/path`
#   (unambiguous) or that full id.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C257 — runtime/scripts/spawn_worker.sh:93

 See runtime/dispatch-lifecycle.md.
#

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C258 — runtime/scripts/spawn_worker.sh:137

PY
}

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C259 — runtime/scripts/spawn_worker.sh:217

  # `orca --version` is not source-witnessed as to its exact wording, so take the
  # first version-shaped token anywhere in its output rather than the whole line.
  installed=$(orca --version 2>/dev/null | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -n 1 || true)
  if [ -z "$installed" ]; then

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C260 — runtime/scripts/spawn_worker.sh:273

  doctor_rc=0
  # --json is documented for worker-start / task-list / skills; `src/cli/specs/vm.ts:6-9` lists only
  # [--repo-path] [--provision|--connect] for doctor.

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C261 — runtime/scripts/spawn_worker.sh:275

 So ask for JSON and fall back to the
  # documented plain form when the flag is rejected.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C262 — runtime/scripts/spawn_worker.sh:276

 Source-witnessed, not binary-witnessed — the
  # same limitation pins.json records for itself; re-witness on the next pin-it wave.
  orca vm recipe doctor "$recipe" --provision --json > "$doctor_out" 2>&1 || doctor_rc=$?
  if [ "$doctor_rc" -ne 0 ] && grep -qiE "unknown (option|flag|argument)|unrecognized|invalid option" "$doctor_out"; then
    doctor_rc=0
    orca vm recipe doctor "$recipe" --provision > "$doctor_out" 2>&1 || doctor_rc=$?
  fi
  if [ "$doctor_rc" -ne 0 ]; then

**Unsatisfied:** Coordinator-provided disposable provider/recipe; no paid or credential provisioning in this unit. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an authorized disposable environment replay vm recipe doctor <owned-recipe> --provision and inspect warn/fail fields; verify pairing identity only with owned noncredential fixture.

**Expected receipt:** Exact doctor schema and warnings plus distinct pairing/placement facts.

**Partial observations:** none

## C263 — runtime/scripts/spawn_worker.sh:313

# rw    = autonomous write, non-blocking — the DEFAULT.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C264 — runtime/scripts/spawn_worker.sh:313

 Safety is the isolated worktree +
#         build-blind review + PR gate + no-merge-to-default-without-human, NOT per-command
#         prompts (per the coordinator prompt library's "no per-action permission prompts").
# danger= the SAME autonomous flag as rw, but gated (ORCA_COORD_ALLOW_DANGER) and required to run
#         in an ephemeral per-workspace sandbox (sandbox-policy.md) for destructive / exploit work.
# An (agent, tier) with no Orca-verified flag stays empty → fail-closed to WORKER_CMD below.
cmd_default=""
_cx_effort="-c model_reasoning_effort=\"$effort\""
case "$agent:$PROFILE" in
  claude:ro)                 cmd_default="claude --permission-mode plan" ;;
  claude:rw|claude:danger)   cmd_default="claude --dangerously-skip-permissions" ;;
  codex:ro)                  cmd_default="codex --sandbox read-only $_cx_effort" ;;
  codex:rw|codex:danger)     cmd_default="codex --dangerously-bypass-approvals-and-sandbox $_cx_effort" ;;
  gemini:ro)                 cmd_default="gemini --approval-mode plan" ;;
  gemini:rw|gemini:danger)   cmd_default="gemini --yolo" ;;
  cursor:rw|cursor:danger)   cmd_default="cursor --yolo" ;;
  grok:rw|grok:danger)       cmd_default="grok --permission-mode bypassPermissions" ;;
  droid:rw|droid:danger)     cmd_default="droid --auto high" ;;
  # No Orca-verified non-blocking flag → WORKER_CMD required:
  #   cursor:ro, grok:ro, droid:ro (no read-only modes in Orca's map)
  #   opencode:*, kilo:* (Orca STRIPS --dangerously-skip-permissions from both;
  #                       opencode autonomy is config-driven)
  #   omp:*, pi:* (not in Orca's autonomous-arg map)
esac

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C265 — runtime/scripts/spawn_worker.sh:338

# Generalized launch override: WORKER_CMD (any agent) or the legacy CLAUDE_CMD/CODEX_CMD.
# An override replaces the profile's command entirely, so an inherited env var with bypass
# flags would silently defeat PROFILE=ro — it needs its own opt-in, mirroring the danger guard.
override=""
case "$agent" in
  claude) override="${CLAUDE_CMD:-${WORKER_CMD:-}}" ;;

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C266 — runtime/scripts/spawn_worker.sh:370

    print(unmet)
    print(str(status).replace("\n", " ").replace("\r", " "))
    raise SystemExit(0)

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C267 — runtime/scripts/spawn_worker.sh:375

path, tid = sys.argv[1], sys.argv[2]
d = json.load(open(path))
r = d.get("result", d)
tasks = r.get("tasks") if isinstance(r, dict) else r
tasks = tasks or []
by = {t.get("id"): t for t in tasks}
t = by.get(tid)
if not t:
    emit("not-found", 0)
deps = t.get("deps")
if deps is None:
    deps = []  # absent deps is the ONLY value that legitimately means "no deps"
elif isinstance(deps, str):
    try:
        deps = json.loads(deps)  # "" and garbage both fail here -> refusal below
    except Exception:
        deps = None
if not isinstance(deps, list):
    # Corrupt/unreadable dependency metadata ("", 0, {}, bad JSON) must fail
    # CLOSED, not count as "no deps".
    emit(t.get("status", "unknown"), -1)
unmet = sum(1 for dep in deps if (by.get(dep) or {}).get("status") != "completed")
emit(t.get("status", "unknown"), unmet)
PY
)
# unmet first, status second, one per line. `read -r status unmet` word-split them, so a
# status whose FIRST WORD is a dispatchable one was dispatched: `ready for review` read as
# `ready` (#298). unmet is an int and cannot carry a space; status can, so it
# gets a line to itself and nothing splits it.

**Unsatisfied:** Two owned scratch Runs and terminal tasks; no dispatch required for basic dependency validation. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** task-create in owned Run with nonexistent and owned foreign-Run deps; create parent/child using --deps; complete/fail parent and reread child and run convergence.

**Expected receipt:** Missing/foreign dep refusal without creation; child state after completed versus failed predecessor, scoped Run convergence.

**Partial observations:** none

## C268 — runtime/scripts/spawn_worker.sh:433

esac

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C269 — runtime/scripts/spawn_worker.sh:435

# --- spawn lanes ---------------------------------------------------------------
# Lane selection:
#   override set (WORKER_CMD/legacy)      → custom-argv lane (opt-in checked above)
#   PROFILE=ro                            → custom-argv lane with the profile's ro command.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C270 — runtime/scripts/spawn_worker.sh:438

 A
#                                           worker-start launch takes its args from the host's
#                                           `agentDefaultArgs` setting, whose migrated default IS
#                                           the YOLO map, so on a default host it would silently
#                                           turn a read-only reviewer into a permission-bypass one.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C271 — runtime/scripts/spawn_worker.sh:446

step=spawn
ws="$SP/ws-$safe_title.json"
if [ -z "$override" ] && [ "$PROFILE" != "ro" ]; then
  # The supervised path: one call composes worktree + agent terminal + readiness + dispatch.
  # Creation flags (--name et al.) are REJECTED for current/existing worktrees — pass --name only
  # when the selector asks for a new worktree.
  name_args=()
  case "$sel" in
    new-child|new-top-level) name_args=(--name "$safe_title") ;;
  esac
  # The call's own exit status is NOT the verdict: a typed refusal, a hard failure, and an
  # UNPROVEN outcome (state: outcome_unknown) all exit nonzero.

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C272 — runtime/scripts/spawn_worker.sh:457

 The receipt is the verdict.
  ws_rc=0
  orca orchestration worker-start --task "$task" --worktree "$sel" ${name_args[@]+"${name_args[@]}"} --agent "$agent" --json > "$ws" 2>&1 || ws_rc=$?

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C273 — runtime/scripts/spawn_worker.sh:473

  # Line 1 is the machine verdict; the remaining stdout lines are the caller-facing receipt
  # fields. nextSteps / nextCommands go to stderr verbatim — they are the runtime's own
  # recovery text, not ours to paraphrase.
  ws_out=$(python3 - "$ws" "$profile_flag" <<'PY'
import json, sys

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C274 — runtime/scripts/spawn_worker.sh:479

# Every typed preflight refusal is a POLICY/usage answer, not a transport failure: the
# coordinator must branch, not retry. runtime_error is the documented catch-all and is the
# one code that stays a failure ("do not retry unchanged").
# Anchored per code, because they do NOT share one definition — dispatch-lifecycle.md used to
# cite all six at the contract file, which declares the first three (#302), verified against the
# pinned v1.4.199 tree:
#   task_not_found / task_not_startable / inject_rejected
#                                 orchestration-dispatch-refusal-contract.ts:8
#   nested_worker_depth_exceeded  nested-worker-depth.ts:13
#   dispatch_inactive             dispatch-capability.ts:18
#   consumer_fenced               role-mailbox-delivery.ts:52, decision-gate-store.ts:49

**Unsatisfied:** Owned scratch Run and task; coordinator-provided independent Dispatch fixture for preamble. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** none

## C275 — runtime/scripts/spawn_worker.sh:525

if not isinstance(r, dict):
    r = d
err = d.get("error") or r.get("error") or {}
if not isinstance(err, dict):
    err = {}
code = err.get("code") or ""
data = err.get("data") if isinstance(err.get("data"), dict) else {}
# Older hosts may omit `data` entirely — treat every field as optional.
for s in data.get("nextSteps") or []:
    print(f"nextStep: {s}", file=sys.stderr)
if code in POLICY_CODES:
    print(f"VERDICT=refused CODE={code}")
    raise SystemExit(0)
if code:
    print(f"VERDICT=failed CODE={code}")
    raise SystemExit(0)

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C276 — runtime/scripts/spawn_worker.sh:542

state = r.get("state") or (r.get("worker") or {}).get("state")
did = r.get("dispatchId") or r.get("dispatch_id") or ""
# The agent terminal is the effects[] entry kind=terminal role=agent; agentTerminalHandle is a
# worker-list/worker-show field, kept as a harmless fallback.
h = r.get("agentTerminalHandle") or ""
if not h:
    for e in r.get("effects") or []:
        if isinstance(e, dict) and e.get("kind") == "terminal" and e.get("role") == "agent":
            h = e.get("id") or ""
            break

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C277 — runtime/scripts/spawn_worker.sh:553

if state == "outcome_unknown":
    # NOT a failure: the start neither proved nor disproved the worker.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C278 — runtime/scripts/spawn_worker.sh:554

 The receipt names the
    # exact inspection commands; a respawn here is the dual-writer class.
    for c in r.get("nextCommands") or []:
        print(f"nextCommand: {c}", file=sys.stderr)
    print(f"VERDICT=unknown STATE={state}")
    print(f"HANDLE={h} READY={state}")
    print(f"DISPATCH={did}")
    raise SystemExit(0)
if state is not None and state != "ready":
    print(f"VERDICT=failed STATE={state}")
    raise SystemExit(0)

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C279 — runtime/scripts/spawn_worker.sh:566

if state is None:
    # "The receipt is the verdict" — and a receipt naming no state is not one.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C280 — runtime/scripts/spawn_worker.sh:567

 This read as READY
    # on the call's exit status alone, which the header above says is NOT the verdict, so a
    # changed receipt shape silently disabled the state check (#298).

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C281 — runtime/scripts/spawn_worker.sh:569

 A receipt of
    # `{"result": "surprise"}` reported READY with an empty handle and an empty dispatch id.
    #
    # UNKNOWN, not FAILED: worker-start exited 0, so a worker may well be live, and the one thing
    # a coordinator must not do here is respawn beside it (liveness-resume.md, dual-writer).
    print("VERDICT=unknown STATE=absent")
    print(f"HANDLE={h} READY=absent")
    print(f"DISPATCH={did}")
    raise SystemExit(0)

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C282 — runtime/scripts/spawn_worker.sh:579

launch = r.get("launch") if isinstance(r.get("launch"), dict) else {}
eff = launch.get("effective") if "effective" in launch else None
# (b) The requested PROFILE is a capability grant; `launch.effective` is what the host actually
# launched.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C283 — runtime/scripts/spawn_worker.sh:582

 A worker-start launch takes its args from the HOST's agentDefaultArgs, not from
# anything this script builds, so the two CAN disagree — and when they did, the launch proceeded

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C284 — runtime/scripts/spawn_worker.sh:636

  fi

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C285 — runtime/scripts/spawn_worker.sh:638

  step=verify-ready
  case "$verdict" in
    ready)
      printf '%s\n' "$payload"
      ;;
    refused)
      echo "SPAWN=REFUSED task=${task} worker-start refused: ${verdict_line#VERDICT=refused } (policy/usage — nextSteps above; receipt in $ws)" >&2
      exit 2
      ;;
    unknown)
      printf '%s\n' "$payload"
      case "$verdict_line" in
        *STATE=absent*)
          echo "SPAWN=OUTCOME_UNKNOWN task=${task} — worker-start exited ${ws_rc} but its receipt names no state, so the start neither proved nor disproved the worker.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C286 — runtime/scripts/spawn_worker.sh:651

 A receipt shape this script cannot read is not a success.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C287 — runtime/scripts/spawn_worker.sh:651

 INSPECT (worker-list, then worker-show on anything for this task), NEVER RESPAWN — a second worker beside a live pane is the dual-writer class (liveness-resume.md).

**Unsatisfied:** Owned scratch coordinator identity; second owned Run for cross-Run filtering. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Use run-create/run-current/run-show and task-list/worker-list with and without --run in an independently bound scratch terminal; compare explicit fixture sets across two owned Runs.

**Expected receipt:** Returned scope and rows match the claimed default/explicit Run filtering.

**Partial observations:** none

## C288 — runtime/scripts/spawn_worker.sh:651

 Receipt in $ws" >&2 ;;
        *)
          echo "SPAWN=OUTCOME_UNKNOWN task=${task} — the start neither proved nor disproved the worker.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C289 — runtime/scripts/spawn_worker.sh:653

 Run the nextCommands above (worker-show, then an explicit worker-stop or worker-abandon): INSPECT, NEVER RESPAWN — a second worker beside a live pane is the dual-writer class (liveness-resume.md).

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C290 — runtime/scripts/spawn_worker.sh:653

 Receipt in $ws" >&2 ;;
      esac

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C291 — runtime/scripts/spawn_worker.sh:656

      ;;
    unusable)
      printf '%s\n' "$payload"
      case "$verdict_line" in
        *LAUNCH_EFFECTIVE_ABSENT*)
          _why="its receipt carries no launch.effective at all, so what the host applied cannot be read (sandbox-policy.md: that field is the only way to tell an autonomous worker from a prompting one)" ;;
        *)
          _why="the host's launch.effective does not carry '${profile_flag}'" ;;
      esac
      echo "SPAWN=LAUNCHED_UNUSABLE task=${task} PROFILE=${PROFILE} — a worker IS LIVE (handle above) and ${_why}.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C292 — runtime/scripts/spawn_worker.sh:665

 It cannot do the work this profile grants, and on a manual host it will block on invisible permission dialogs while the fleet believes it is autonomous.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C293 — runtime/scripts/spawn_worker.sh:665

 STOP it (worker-stop / worker-abandon) — NEVER RESPAWN beside it.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C294 — runtime/scripts/spawn_worker.sh:665

 Then fix the host's agentDefaultArgs, or pass WORKER_CMD with ORCA_COORD_ALLOW_CMD_OVERRIDE=1 and own the semantics.

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C295 — runtime/scripts/spawn_worker.sh:665

 Receipt in $ws" >&2
      exit 5
      ;;
    *)
      echo "SPAWN=FAILED task=${task} step=${step} rc=${ws_rc} — worker-start failed: ${verdict_line#VERDICT=failed } (receipt in $ws)" >&2
      exit 1
      ;;
  esac
else
  # --- custom-argv lane (overrides + PROFILE=ro): terminal create + dispatch --inject ----------

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C296 — runtime/scripts/spawn_worker.sh:686

    print(f"terminal create error: {d['error']}", file=sys.stderr)
    raise SystemExit(1)
r = d.get("result", d)
h = (r.get("terminal") or {}).get("handle") or r.get("handle")
if not h or h == "None":
    print("terminal create returned no handle", file=sys.stderr)
    raise SystemExit(1)

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C297 — runtime/scripts/spawn_worker.sh:705

import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("unreadable")
    raise SystemExit(0)
r = d.get("result", d) if isinstance(d, dict) else {}
if isinstance(r, dict) and isinstance(r.get("result"), dict):
    r = r["result"]
w = r.get("wait") if isinstance(r, dict) else None
s = w.get("satisfied") if isinstance(w, dict) else None
print("true" if s is True else "false" if s is False else "absent")

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C298 — runtime/scripts/spawn_worker.sh:741

if isinstance(r, dict) and isinstance(r.get("result"), dict):
    r = r["result"]
# dispatch --inject returns result.prompt; terminal send returns result.send.prompt.
p = r.get("prompt") if isinstance(r, dict) else None
if not isinstance(p, dict):
    send = r.get("send") if isinstance(r, dict) else None
    p = send.get("prompt") if isinstance(send, dict) else None
if not isinstance(p, dict):
    p = {}
stages = p.get("stages")
stages = [s for s in stages if isinstance(s, str)] if isinstance(stages, list) else []
req = p.get("requestId")
print("STAGES=" + ",".join(stages) + " REQUEST=" + (req if isinstance(req, str) else ""))
PY
  }
  rcpt=$(read_stages "$dj")
  stages=${rcpt#STAGES=}
  stages=${stages%% *}
  request=${rcpt#* REQUEST=}

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C299 — runtime/scripts/spawn_worker.sh:761

  case ",$stages," in
    *,turn_started,*) : ;;
    *)
      # No observed turn start.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C300 — runtime/scripts/spawn_worker.sh:764

 Replay the receipt ONCE — never resend, never a bare Enter.
      # --retry-request/--wait-submit require --text with --enter at v1.4.199, and the requestId
      # is bound to the prompt payload, so recover the exact preamble first.
      step=recover-preamble
      pj="$SP/preamble-$safe_title.json"
      pre_rc=0
      orca orchestration dispatch-show --task "$task" --preamble --json > "$pj" 2>&1 || pre_rc=$?
      preamble=$(python3 - "$pj" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))

**Unsatisfied:** Owned inert terminal and original prompt bytes/request receipt. Dispatch-derived equivalence additionally needs coordinator-provided worker fixture. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** On an owned inert terminal capture an initial original-text --enter request; replay terminal send --terminal <owned> --retry-request <original-id> --wait-submit 1 --json, then correct missing original --text/--enter and compare request ID and terminal effects.

**Expected receipt:** Old shorthand refusal before effects; corrected replay result and original request identity, with no duplicate terminal input.

**Partial observations:** none

## C301 — skills/oss-contribute/SKILL.md:76

Run the coordinator as a MANUAL loop (`task-create → spawn (worker-start) → check --wait`) — not
`orchestration run` — to keep the file-ledger gate under your control.

**Unsatisfied:** An independently owned scratch coordinator terminal able to consume its Run without rebinding the parent. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Enqueue mixed status and escalation messages in owned Run; check --wait --types escalation, replay, --ack; use 51-message fixture for batch ceiling; empty wait 16 seconds with separated stdout/stderr.

**Expected receipt:** FIFO whole-type batch, same Delivery on replay, next batch after ack, ceiling 50 and stderr keepalive at 15 seconds.

**Partial observations:** none

## C302 — skills/oss-contribute/SKILL.md:77

 No conductor (nothing merges).

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C303 — skills/pin-it/SKILL.md:14

  HARD dependency: Orca runtime + orchestration skill (Orca CLI) — the binary under audit; `orca
  skills get <name>` must work, and re-witness probes run against the live local runtime from a
  live Orca terminal. git.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C304 — skills/pin-it/SKILL.md:16

 A worker playbook pack (mattpocock, addyosmani, gstack) — one router

**Unsatisfied:** Coordinator-provided independent worker identity; approved provider/trust and placement; no self-dispatch or paid/danger launch. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Coordinator provides independent owned fixture; record worker-start/dispatch launch receipt, worker-list/show, typed refusal/recovery, settlement and release; separately exercise exact assertion in excerpt.

**Expected receipt:** Exact claimed field/code/state transition at orca 1.4.200, with explicit process/Dispatch ownership and teardown.

**Partial observations:** none

## C305 — skills/pin-it/SKILL.md:33

command shapes corrupts real runs.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C306 — skills/pin-it/SKILL.md:33

 **The installed binary is the source of truth; the version-matched
guides it serves (`orca skills get …`) are the map of what to probe — never the proof.** This
mission's job is to make the written doctrine provably equal to the binary's *observed* behaviour.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none

## C307 — skills/pin-it/SKILL.md:40

`liveness-resume`, `gate-classification`, `dispatch-lifecycle`, `sandbox-policy` (repo read probes
are PROFILE=ro; control-plane probes — run-create, worktree create, worker-start — MUTATE Orca
state and run in a scratch Orca worktree with full teardown: settle the run, release workers,
remove the worktree — teardown commands are claims too (re-witness before relying; if unsupported,
archive the worktree, never force-remove); never against the default branch or a live fleet's run

**Unsatisfied:** Owned scratch Run and task; coordinator-provided independent Dispatch fixture for preamble. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** orca orchestration gate-create --task <owned-ready-task> --question <marker> --options <JSON-array> --json; task-show; gate-resolve --id <owned-gate> --resolution <marker> --json; task-show; dispatch-show --task <owned-task> --preamble --json.

**Expected receipt:** Task blocked then ready, durable gate resolution, and preamble marker presence/absence; dispatch preamble test requires an owned Dispatch.

**Partial observations:** none

## C308 — skills/pin-it/SKILL.md:72

  --references`, then `--reference <name>` for EACH (`--full` fallback): the contract lives there, not in the kernel.
→ RE-WITNESS each claim: replay it against the live runtime from a live Orca terminal (a bound
  coordinator terminal or ORCA_TERMINAL_HANDLE — orchestration calls fail with
  no_active_sender_terminal from a plain shell) and capture the verbatim receipt.
→ CLASSIFY per claim, from receipts only: CURRENT (receipt matches) · STALE (binary behaves
  differently — capture the actual receipt) · SUPERSEDED (mechanism gone — capture the
  *mechanism-level* refusal: unknown command, or a retired-alias recovery message naming the
  replacement; task/state refusals like `task_not_startable` are about the unit, not the
  mechanism, and never classify SUPERSEDED) · BLOCKED-BY-SUBSTRATE (the probe's precondition
  failed — no sender terminal, untrusted worktree, expired credentials, absent device: the

**Unsatisfied:** Owned scratch worktree on nondefault branch, no setup or agent process. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Read create, close, rm and archive help first; create minimum scratch worktree, inspect exact id/parent; close only owned inert terminal and archive when removal is unsupported.

**Expected receipt:** Worktree composite selector, parent ownership, close confirmation and remove/archive receipt; no unknown residual resource.

**Partial observations:** none

## C309 — skills/ship-it/SKILL.md:60

`orca status --json` running · orchestration on · Orca CLI + orchestration skill available · git.

**Unsatisfied:** An isolated scratch Run/worktree and any worker, remote host, legacy-state or scheduler fixture required by the source excerpt; no parent-run effects. The complete quoted assertion has not been re-witnessed. Execute its frozen procedure before upgrading this record; no binary absence is inferred.

**Probe owed:** Replay the quoted control-plane assertion on owned scratch fixtures using installed orca 1.4.200; observe every behavior and field in this excerpt. Consult the topic guide for exact argv before execution.

**Expected receipt:** Verbatim stdout/stderr and exit plus authoritative before/after state proving all external-runtime assertions in the source excerpt.

**Partial observations:** none
