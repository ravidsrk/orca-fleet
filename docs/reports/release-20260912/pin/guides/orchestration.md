---
name: orchestration
description: >-
  Coordinate supervised Orca workers: threaded messages, blocking ask/reply,
  task dispatch, worker_done/escalation waits, task DAGs, decision gates,
  coordinator loops, and decomposing work across agents. Use `orca-cli` for full
  ownership handoffs — "hand off", "handoff", "handover", "give this to another
  agent", "another worktree" — unless asked to supervise, monitor, or coordinate
  a DAG, and for terminal control, lightweight terminal prompts, shell commands,
  Orca worktree management, and reading or waiting on terminals. Use Computer
  Use for external browser windows, webviews, Orca app UI, or desktop UI outside
  Orca's embedded browser only when the task requires OS/window-level control
  such as focus, menus, dialogs, coordinates, or screenshots. Use `orca-cli` for
  Orca's embedded pages and a page-automation tool such as Playwright or CDP for
  external pages.
---

# Orca orchestration

Orchestration is Orca's structured coordination layer. It records who owns work,
which attempt is authoritative, and when supervised work has settled.

## Outcome

**Result:** every in-scope Task has one explicit outcome and every settled worker
terminal has a next owner or cleanup decision. **Next consumer:** the user who
requested supervision. **Done:** all expected Dispatches have settled, every
delivered message was processed before acknowledgment, each settled worker was
reused, explicitly retained, or released, and the turn ends only when the report
to that user names, per Task, its outcome, the evidence behind it, and any
unresolved blocker.

**Safe failure:** preserve work and authority and report the state as unknown or
`unverifiable`. Only positive proof of exit authorizes stop, abandon, or retry,
and only an accepted settlement authorizes release. Every other observation,
absence included, is a checkpoint.

## Classify the role

| Current context                                                                                                                                | Role                    | Route                                                                          |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------ |
| The user explicitly asks to supervise, monitor, wait for results, track completion, coordinate a DAG, use a decision gate, or manage ask/reply | Coordinator             | Use the supervised loop below                                                  |
| The current prompt contains a live injected preamble with Task and Dispatch IDs                                                                | Dispatched worker       | Follow the preamble and the worker obligations below                           |
| The user asks to hand off ownership or start another agent/worktree without supervision                                                        | Handoff owner           | Use `orca-cli`; create no Run, Task, or Dispatch and do not monitor completion |
| A message carries a legacy authority label                                                                                                     | Compatibility operator  | Load the legacy contract reference before any lifecycle mutation               |
| No live preamble and no explicit supervision                                                                                                   | Ordinary terminal agent | Do not emit lifecycle messages; use `orca-cli` for terminal/worktree work      |

Model or effort selection does not make a handoff supervised. Never substitute a
non-Orca subagent tool when Orca orchestration provenance was requested.

## Authority and safety floor

- A Run is a durable namespace and coordinator inbox; it does not schedule or
  place workers. A Task is work. A Dispatch is one authoritative Task attempt.
- Lifecycle authority comes from the active Dispatch, not a terminal title,
  copied ID, old database row, provider transcript, or visible pane.
- Workers use the exact executable, handle, capability, Task ID, and Dispatch ID
  in the live preamble. Never reconstruct, translate, or broaden those arguments.
- After remote start, address the worker by Dispatch ID. The execution host owns
  process, filesystem, transcript, stop, and cleanup facts. Preserve the verdicts
  `live` / `unverifiable` / `exited`; contact loss is not process death.
- Liveness is layered: `worker-list`'s `projection.liveness` is the fleet verdict
  for the agent; `worker-show`'s `observation.status` is PTY liveness only. A live
  terminal can still hold a dead or stuck agent.
- Folder workspaces are valid; never require Git or assume a worktree.
- Clients and remote servers update independently. Treat unknown optional fields
  as absent. A new stream operation requires advertised capability because old
  decoders may silently drop unknown opcodes. Never fall back to local execution
  when remote authority or capability is unproven.
- Use the executable you used to run `skills get` for the entire run. In the
  examples below, replace `ORCA` with it; do not create a shell variable or run
  `ORCA` literally. If it fails, report that exact error instead of switching.
- A successful `orchestration send` proves durable enqueue; its wake or nudge is
  best-effort attention only and does not prove the recipient read or accepted it.

## Worker obligations

The injected preamble is authoritative. A dispatched worker must:

1. Do only the current Task and use the preamble's `ask` command for a blocking
   coordinator question. Never open a local question TUI the coordinator cannot
   answer. Resume the same message ID after an ask timeout.
2. Send heartbeats only at the cadence in the preamble. A heartbeat proves
   liveness, not completion.
3. Read coordinator follow-ups at each natural checkpoint — before starting a
   new file, after a test run — and once more immediately before `worker_done`:
   `ORCA orchestration check --terminal <your_handle> --json`.
4. Send `worker_done` exactly once, from the dispatched terminal, with a
   three-sentence executive summary, both lifecycle IDs, and explicit
   `--outcome succeeded` or `--outcome failed`. Never encode failure only in prose.
5. Append `--files-modified` and `--report-path` only with real values when
   applicable. After `worker_done`, end the dispatched turn and idle; do not poll
   or start new work.

A direct user instruction after completion starts new user-owned work and takes
precedence over the idle rule. Do not reuse the settled lifecycle IDs.

## Canonical supervised loop

Confirm the runtime, bind one Run, and start the full independent wave before
waiting. `worker-start --spec` creates the Task and its attempt in one call:

```text
ORCA status --json
ORCA orchestration run-create --objective "<objective>" --json
ORCA orchestration worker-start --spec "<worker A task>" --worktree current --agent codex --json
ORCA orchestration worker-start --spec "<worker B task>" --worktree current --agent claude --json
ORCA orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 --json
```

If `worker-start` exits non-zero, do not relaunch. Read the receipt's
`failedStage` and `residualResources`, then load
`references/recovery-and-cleanup.md`.

Use `task-create` plus `worker-start --task <task_id>` for planned fan-out with
dependencies or a retry of a known Task. Use dependencies only for real ordering
and prefer parallel waves over chains deeper than three or four steps; nested
workers obey the depth limit, and a new Run does not reset the caller's depth.

A consuming `check` names its caller with `--terminal <handle>`, never `--from`;
omit it inside the coordinator's own Orca terminal. It returns the bound Run's
oldest FIFO Delivery and replays that batch until acknowledged. Process every
message: reply to questions, validate each `worker_done` against the expected
active Dispatch, and decide each settled terminal's next owner before the ack:

```text
ORCA orchestration reply --id <message_id> --body "<answer>" --json
ORCA orchestration worker-release --dispatch <dispatch_id> --json
ORCA orchestration check --ack <delivery_id> --wait --types "worker_done,escalation,question" --timeout-ms 900000 --json
```

Keep waiting until every expected Dispatch settles. A timeout or empty result is
a checkpoint, not a failure. Do not stop, retry, release, or launch a duplicate
editor without the positive proof `## Outcome` requires.

After three consecutive empty waits, stop waiting blindly and enumerate with
`ORCA orchestration worker-list --include-remote --json` (defaults to the bound
Run; `--run <run_id>` overrides; the receipt's `scope` names which), acting on
each row's `projection.attention` categories, `projection.attention.requiresAction`, and literal `projection.nextAction` argv.
A `none` `nextAction` has no argv to run: read `liveness.reason` and keep waiting
with `check --wait`. Absence never earns an argv; settlement and pending work still do.
Leave the wait only on positive proof the agent stopped: `exited` liveness, the
worker's own observation of process exit, or a transcript whose final agent turn
sent no `worker_done`. Then load `references/recovery-and-cleanup.md` and choose
`worker-stop` or `worker-abandon` explicitly. `unverifiable` is absence,
including when `worker-show` reports `agentWait` null. Absence never authorizes
stop, abandon, retry, or release; keep waiting or inspect.

`worker-start` is the normal path, composing placement, terminal readiness,
prompt injection, and supervised resource ownership. `dispatch --inject` leaves
an operator-created process unsupervised and is only for an expressiveness gap.

## Task-spec contract

Every Task spec must be self-contained and name:

- **Target:** the files, component, or environment in scope.
- **Change:** the concrete result to produce.
- **Constraints:** invariants, compatibility rules, and do-not-touch boundaries.
- **Ownership:** what this worker may edit and any coordination boundary.
- **Observable acceptance:** the test, output, or evidence that proves completion.

## Completion accounting

After an accepted success or failure report, immediately do exactly one:

1. Reuse the same proven agent terminal for an immediate follow-up Dispatch.
2. Record user-requested retention with `worker-retain`.
3. Run `worker-release`.

Release is post-settlement cleanup, not cancellation. Only an accepted
settlement authorizes it; no other observation does. If release is uncertain,
follow its exact recovery receipt and never substitute `terminal close`.

A valid `worker_done` settles the Task and Dispatch automatically; do not follow
it with `task-update --status completed`. Enumerate the terminals still owing a
decision with `worker-list --run <run_id> --terminal-state reclaimable --json`,
and do not end the coordinator turn until it returns none.

## Conditional references

This compact guide is sufficient for the normal local loop. At an action gate
below, run `ORCA skills get orchestration --reference references/<file>.md` and
read only that document; `--references` lists the names. If the CLI rejects
`--reference`, run `ORCA skills get orchestration --full` once instead: it
returns this exact kernel and every reference, so read only the named one. If an
older CLI rejects `--full`, keep this kernel's safety floor, use that command's
`--help`, and never guess newer flags.

| Action gate                                                                                                   | Bundled reference                         |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Expanded DAG waves, launch model/effort, same-terminal reuse, or review ownership                             | `references/coordinator-loop.md`          |
| You are a dispatched worker and the live preamble does not answer your question, or `check` returned an error | `references/worker-contract.md`           |
| New worktree, exact workspace, SSH, WSL, or connected-server placement                                        | `references/placement-and-remote.md`      |
| Inbox replay, follow-up messages, group addresses, or decision gates                                          | `references/messaging-and-gates.md`       |
| Failed/stopped/unknown attempts, retry, stop, abandon, retain, or uncertain release                           | `references/recovery-and-cleanup.md`      |
| Custom argv or terminal topology that `worker-start` cannot express                                           | `references/low-level-topology.md`        |
| Any legacy label, adopted Run, compatibility receipt, or takeover                                             | `references/legacy-contract-migration.md` |

Retired scheduler commands are not aliases for Run creation. Recovery commands
must provide their exact next action; follow it with the same selected executable.

---

# Bundled references

These references belong to the version-matched guide above. Read only the documents named by its action gates.

<!-- bundled-reference: references/coordinator-loop.md -->

# Coordinator loop

Load this reference for expanded DAG waves, per-invocation launch preferences,
same-terminal reuse, or review ownership. The compact guide remains the source
of truth for the loop order and completion boundary.

## Ready waves

Create independent Tasks before the first wait. Encode only real dependencies,
then use the ready view as external memory:

```text
ORCA orchestration task-create --spec "<dependent work>" --deps <json_array> --json
ORCA orchestration task-list --ready --brief --json
```

`--brief` collapses whitespace and caps echoed specs at 160 characters;
`spec_truncated` identifies shortened rows. Omit it when full specs are needed or
when an older CLI rejects the flag. A nested worker must respect
`nested_worker_depth_exceeded`; creating another Run does not reset depth.

## Launch preferences

For a fresh Claude, Codex, or Cursor terminal, `--model` accepts an opaque
provider model ID. Pass it only when the user named a model; otherwise omit it
so the worker inherits the user's configured agent default. Add `--effort` only
when that model supports it:

```text
ORCA orchestration worker-start --task <task_id> --worktree current --agent claude --model opus --effort high --json
```

`--effort` requires `--model`; neither option combines with `--terminal`. A
connected worker server must advertise launch-preference support before Orca
forwards either field. Compare `launch.requested` with `launch.effective`; never
claim a model or effort from requested arguments alone.

## Reuse after settlement

Choose the terminal's next owner before acknowledging the Delivery. When the
same exact agent has immediate follow-up work, recover the proven handle and
transfer cleanup ownership to the new Dispatch:

```text
ORCA orchestration worker-show --dispatch <dispatch_id> --json
ORCA orchestration worker-start --task <next_task_id> --terminal <agent_terminal_handle> --json
```

Otherwise explicitly retain or release the settled worker. Do not leave it live
only to inspect output; archived output remains available through `worker-read`.

## Review ownership

A review-only `worker_done` authorizes synthesis of findings, not coordinator
file edits. Dispatch or hand off fixes unless the user explicitly assigned them
to the coordinator. If the user's plan names a next owner, post-review fixes and
PR preparation remain with that owner; the coordinator routes and synthesizes.

<!-- bundled-reference: references/legacy-contract-migration.md -->

# Legacy contract migration

Load this reference only for an authority label, adopted Run, compatibility or
recovery receipt, or explicit legacy takeover. A newly created attempt always
uses the current grammar.

## Authority labels

- `[LEGACY COMPATIBILITY]` is live and attested. Run only the exact supported
  command printed with the message, using the same selected executable and
  arguments supplied by the original prompt.
- `[LEGACY RECOVERY REPLAY — MAY HAVE BEEN SEEN]` is one bounded,
  at-least-once cutover replay. Process it idempotently and acknowledge only
  through the exact displayed guidance.
- `[LEGACY READ-ONLY]` is inspection-only. It has no reply, acknowledgment, or
  lifecycle mutation.
- An unlabeled current message uses the current guide and grammar.

An explicitly selected current Run, attested current binding, current Dispatch,
or federated attachment takes precedence over legacy fallback. A retained
adoption record alone does not grant mutation authority. If liveness, principal
ownership, capability, or the exact legacy contract is unproven, degrade to
read-only inspection and never fall back to local execution.

Adoption preserves the live agent process, PTY/session, terminal handle,
tab/pane, worktree or folder workspace, Task, and Dispatch. It never restarts or
replaces the worker and never revives the retired scheduler. Loss of lifecycle
authority does not invalidate the existing process, assignment, or filesystem
work. Exact recovery may restore the same PTY once in its original inactive
background tab; it must not spawn, write, signal, stop, switch, focus, split, or
inject a terminal.

## Compatibility recovery

When a compatibility response returns structured next-step arguments, execute
those exact arguments with the same selected CLI executable. Do not translate
from memory, broaden the recipient, or retry as a current mutation unless the
receipt explicitly authorizes it.

A pending ask, reply, final Dispatch settlement, and consuming check have
durable recovery identities. Heartbeat and escalation remain at-least-once
across a manual contract-boundary retry. If an ask may already have been
answered, run the exact non-consuming recovery check printed by Orca before
creating any new question. Never guess among identical question threads.

On packaged Windows, a legacy ask uses a two-step commit/resume protocol. The
initial command commits the question, prints its exact
`ask --resume <message_id>` command, and exits with launcher status `75`. Run
that exact resume after the launcher or update boundary. For an attested WSL
launch, preserve the printed `orca-ide` executable and distro route. Older WSL
workers without launch proof remain lifecycle read-only even while their
terminal and filesystem work continue.

## Read-only inspection and takeover

Read-only inspection does not consume mail:

```text
ORCA orchestration run-list --json
ORCA orchestration run-show --id run_legacy_local --json
ORCA orchestration run-show --id <adopted_run_id> --json
ORCA orchestration task-list --run <adopted_run_id> --json
ORCA orchestration inbox --full --json
ORCA orchestration check --terminal <legacy_handle> --peek --format --json
ORCA terminal read --terminal <legacy_handle> --json
ORCA terminal wait --terminal <legacy_handle> --for tui-idle --timeout-ms 60000 --json
```

`run_legacy_local` is an empty audit tombstone after adoption. Find the ordinary
Run whose objective is `Recovered orchestration work from a contract update`.

Only when the original coordinator is unavailable or cannot prove retained
authority may a new live coordinator take over from its own terminal:

```text
ORCA orchestration run-use --id <adopted_run_id> --takeover-legacy --json
ORCA orchestration check --run <adopted_run_id> --json
```

Takeover binds the authenticated invoking terminal; `--from` cannot nominate
another coordinator. It fences only the old coordinator and moves pending mail
into current Run delivery. It preserves live workers, Tasks, Dispatches, processes, and files.
Never take over while the original coordinator is actively coordinating.

Do not launch a replacement editor merely because Orca updated or authority is
unclear. Keep the original worker as the only editor until a stable handoff
point, then use a fresh current Dispatch in a conflict-free placement.

<!-- bundled-reference: references/low-level-topology.md -->

# Low-level topology

Load this reference only when `worker-start` cannot express required custom argv
or terminal topology. It is not the normal supervised loop and is never a full
handoff recipe.

```text
ORCA terminal create --worktree active --title <task_name> --command "<agent_command>" --json
ORCA terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
ORCA orchestration dispatch --task <task_id> --to <handle> --inject --json
```

Wait for readiness only when startup could lose injected input. Prefer
agent-first `worker-start` whenever its argv and topology are sufficient.

`dispatch --inject` creates authoritative Task/Dispatch context but deliberately
keeps an operator-created process unsupervised: it creates no supervised worker
resource row. `worker-show`, `worker-read`, and `worker-list` report the lane as
`unsupervised`; `worker-stop` and `worker-abandon` do not close that process, and
settled retain/release take no process action.

Use `worker-start --terminal <handle>` when lifecycle ownership of an existing
agent terminal is required. Never imply that low-level dispatch retroactively
owns a process, never use it to route around the nested-depth limit, and never
use it for an ownership handoff.

<!-- bundled-reference: references/messaging-and-gates.md -->

# Messaging and gates

Load this reference for inbox replay, attempt-specific guidance, group
addresses, blocking questions, or coordinator-managed DAG decisions.

A successful `send` proves durable enqueue. Wake and nudge are best-effort
attention only: neither proves the recipient read the message, began a turn, or
accepted steering.

## Coordinator delivery loop

`check` names its caller with `--terminal <handle>` and is the only verb that
rejects `--from`. Omit `--terminal` inside an Orca terminal, where Orca resolves
the caller; pass it explicitly from anywhere else, including a dispatched
worker reading coordinator follow-ups.

A consuming coordinator `check` returns the bound Run's oldest FIFO Delivery,
up to 50 messages, and replays that exact batch until acknowledged. Process
every row and required terminal ownership decision before `--ack`. Type filters
decide when a waiter wakes; they do not authorize skipping older actionable
mail. A Delivery therefore always carries the whole FIFO batch whatever its
types, and a `check` without `--wait` hands that batch over unfiltered.
`--peek` and `--all` are read-only inspection, not progress through the
coordinator inbox.

An empty wait or timeout is a checkpoint. Continue rolling waits until every
expected Dispatch settles. Heartbeat or visible activity means alive, not done.

## Addresses

Use a stable Dispatch address for attempt-specific coordinator guidance:

```text
ORCA orchestration send --to dispatch:<dispatch_id> --subject "Follow-up" --body "<guidance>" --json
```

Do not substitute a remote terminal handle. Omit `--from` for ordinary
coordinator calls; a dispatched worker instead copies the exact `--from` and
capability arguments in its preamble. `check` is the exception: it identifies
its caller with `--terminal`, never `--from`.

Group addresses include `@all`, `@idle`, `@claude`, `@codex`, `@opencode`,
`@gemini`, `@droid`, `@grok`, `@cursor`, and `@worktree:<id>`. Use them only for
intentional fan-out status or questions. `worker_done`, heartbeat, and other
Dispatch lifecycle messages never target groups.

## Questions and gates

A worker uses `ask`; its timeout leaves one durable question pending, which the
worker resumes by message ID. The coordinator answers that message with `reply`.

Use a gate only for a coordinator-owned Task-DAG decision:

```text
ORCA orchestration gate-create --task <task_id> --question "<decision>" --options <json_array> --json
ORCA orchestration gate-resolve --id <gate_id> --resolution "<choice>" --json
ORCA orchestration gate-list --task <task_id> --json
```

Pass `json_array` using the quoting rules of the active shell; do not copy POSIX
single-quote syntax into PowerShell or `cmd.exe`.

Do not create a gate merely to answer a worker's `ask`.

<!-- bundled-reference: references/placement-and-remote.md -->

# Placement and remote execution

Load this reference before creating a new worktree or placing work through SSH,
WSL, or another connected Orca server.

## Placement choices

A fresh worker means a fresh agent terminal, not a new Git worktree. Use the
current or an exact existing workspace by default. Create a worktree only when
the user requested one or a concrete checkout or filesystem conflict makes
sharing unsafe.

```text
# Current workspace; setup is not rerun.
ORCA orchestration worker-start --task <task_id> --worktree current --agent codex --json

# Stacked child worktree.
ORCA orchestration worker-start --task <task_id> --worktree new-child --name <name> --agent codex --setup run --json

# Independent top-level worktree.
ORCA orchestration worker-start --task <task_id> --worktree new-top-level --name <name> --agent codex --setup run --json
```

Current and exact existing workspaces create a fresh terminal unless
`--terminal` is explicit. Folder workspaces are first-class; do not invoke Git
or require worktree lineage when the selected workspace is a folder.

Register a folder workspace through project setup. `repo add --path <dir>`
requires a valid Git repository and rejects a plain directory:

```text
ORCA project setup-existing-folder --project <project_id> --host <host_id> --path <abs_path> --kind folder --json
```

Then place work on the returned workspace with an exact selector. A worktree
selector needs the full `<repo-id>::<path>` value Orca returned, passed as
`id:<newFullWorktreeId>`; a bare repo id is not a worktree id. `new-child` and
`new-top-level` are worktree creation and do not apply to a folder.

New worktrees use agent-first creation and run setup by default. Preserve the
repository's startup policy: `start-immediately` can report setup as `running`,
while `wait-for-setup` gates prompt delivery on success. Orca lineage, Git base,
filesystem isolation, coordination parentage, UI grouping, and execution host
are separate decisions.

## Connected servers

The Run and Tasks remain authoritative on the current server. `--on` selects
only the worker's execution server and appears only on `worker-start`:

```text
ORCA orchestration worker-start --task <task_id> --on <environment> --worktree new-top-level --repo <exact_remote_repo_selector> --name <name> --agent codex --setup run --json
```

Remote `current` and `new-child` are invalid because they are ambiguous across
servers. Use an exact discovered remote workspace, or `new-top-level` with an
exact remote repository selector. After start, route every follow-up, read,
stop, and cleanup by Dispatch ID; never repeat `--on` or substitute a remote
terminal handle.

```text
ORCA orchestration worker-show --dispatch <dispatch_id> --json
ORCA orchestration worker-read --dispatch <dispatch_id> --limit 50 --json
ORCA orchestration send --to dispatch:<dispatch_id> --subject "Follow-up" --body "<guidance>" --json
ORCA orchestration worker-list --run <run_id> --include-remote --json
```

`worker-list` reads local fleet state only; enumerate remote workers with
`--include-remote` or every one of them reads `unverifiable`. Scope every list
with `--run <run_id>`: unscoped, it reports every Dispatch this runtime has
recorded, and the workers you are waiting on are lost in that history.

## Execution-host and mixed-version floor

The execution host owns process, filesystem, transcript, stop, and cleanup
facts. Render only `live`, `unverifiable`, or `exited`. Connection loss, relay
absence, missing client inventory, or timeout yields `unverifiable`, never
synthetic exit and never a client-local substitute action.

Clients and servers update independently. Optional response fields may be
absent. Forward model/effort, transcript reads, cleanup, or another new remote
operation only when the peer advertises the relevant capability; unknown stream
opcodes can be silently dropped. A narrow unsupported response may degrade to a
documented older path, but must not broaden the target or cross the execution
boundary. Changing host-published content reaches old clients even without a
wire-shape change, so preserve established semantics or negotiate the behavior.

For WSL, use the exact executable and arguments returned by Orca so the distro
and packaged launcher remain bound. Do not translate a printed `orca-ide`
recovery command into a PATH-resolved local command.

<!-- bundled-reference: references/recovery-and-cleanup.md -->

# Recovery and cleanup

Load this reference only after a failed/stopped/unknown attempt, explicit retry
decision, stop/abandon request, retention request, or uncertain release.

| Proven state            | Safe action                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| `ready` or active       | Keep waiting; optionally read bounded output                       |
| `failed` or `stopped`   | Start a replacement with `--retry-of`; repeat placement explicitly |
| `outcome_unknown`       | Inspect, then choose `worker-stop` or explicit `worker-abandon`    |
| Accepted `worker_done`  | Reuse, retain, or release                                          |
| Remote contact lost     | Preserve `unverifiable`; do not stop or retry from absence alone   |
| `unverifiable` liveness | Keep waiting or inspect; never stop, abandon, retry, or release    |
| Proven `exited` agent   | Enumerate with `worker-list`; follow its `nextAction`              |

## Inspect before acting

```text
ORCA orchestration worker-list --run <run_id> --json
ORCA orchestration worker-list --run <run_id> --include-remote --json
ORCA orchestration worker-show --dispatch <dispatch_id> --json
ORCA orchestration worker-read --dispatch <dispatch_id> --limit 50 --json
```

`worker-list` is the enumerating command and the authority on agent liveness:
each row carries `projection.liveness`, `projection.attention.categories`,
`projection.attention.requiresAction`, and a literal `projection.nextAction`
argv to run. Always scope it with `--run <run_id>`; an unscoped list reports
every Dispatch this runtime has ever recorded and buries the live ones.
`worker-show`'s `observation.status` is PTY liveness only, so a `live` terminal
whose agent died at a trust prompt still reads `live` there.

When the two disagree, the fleet verdict decides — unless the fleet row is
`unverifiable` for a reason that names a gap on this client rather than a fact
about the worker. `missing_status`, `host_unavailable`, and
`capability_unsupported` are such gaps: the first means this runtime holds no
status row, the second that it could not ask the execution host at all, and the
third that a stale peer answered but lacks the fleet-snapshot capability.
Against any of them, a `worker-show` verdict sourced from the execution host is
the better evidence and outranks the row. Only `host_unavailable` is contact
loss; the other two mean the host was never asked or answered without the
capability.

This never promotes absence. `unverifiable` from either command still authorizes
nothing — only a positive `live` or `exited` verdict does.

A worker started with `--on <environment>` reads `unverifiable` until you
enumerate with `--include-remote`, which asks its execution host for the
verdict. Past 100 rows the response pages, so follow `page.nextCursor` with
`--cursor <value>` until `page.hasMore` is false.

## Stall needs positive evidence

Leave the wait only on positive proof the agent stopped: `exited` liveness, the
worker's own observation of process exit, or a transcript whose final agent turn
sent no `worker_done`. Only then choose `worker-stop` or `worker-abandon`.

`unverifiable` is always absence — `missing_status`, `stale_status`,
`restored_unconfirmed`, or a remote worker with no connection — and a null
`agentWait` or an unchanged `worker-read` tail is that same absence seen again.
Absence never authorizes stop, abandon, retry, or release: keep waiting, or
inspect until you hold one of the positive signals above. A `nextAction` that
names an inspecting command is asking for evidence, not for cleanup.

`worker-read --source auto` uses a proven provider transcript when available and
otherwise returns bounded terminal output with a typed `fallbackReason`.
Continue with its top-level cursor, which is pinned to that source. If Orca
reports `source_changed`, restart without the old cursor. A bounded initial
transcript tail can return an EOF cursor that follows only newly appended records;
read `contentComplete`, `clipping`, and `warnings` before assuming omitted older
records are pageable. Never guess a provider session ID, transcript path, or
remote terminal handle.

## Was the mutation applied?

When a mutation's response was lost and named no Dispatch, do not replay blind.
Every orchestration mutation accepts `--retry-request <id>`, which reuses one
operation identity so Orca can replay, join, or recover it instead of starting a
duplicate. Ask what happened first:

```text
ORCA orchestration request-show --request <request_id> --json
```

`completed` means the mutation already took effect; read its recorded receipt
instead of rerunning. `pending` means the original mutation is still running or
Orca restarted before recording its outcome; replay the original command with
`--retry-request <request_id>`. `absent` means this runtime holds no receipt
under your caller identity — that is not proof nothing happened, so inspect the
affected Task, Dispatch, and terminal before deciding whether to retry.

When a worker's terminal accepted input but the submit is unconfirmed, use
`terminal send --wait-submit <seconds>`: it observes the accepted prompt for that
long and, on timeout, returns the input-accepted receipt without resending.

## Refused starts

`dispatch` and `worker-start` refuse the following preflight cases with a stable
`error.code`; read it before choosing a recovery, and treat `error.data.nextSteps`
as the exact recovery text. Older hosts may omit `data`, so treat every field as
optional.

| Code                 | Meaning                                                                                                               | Recovery                                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `task_not_found`     | No Task with that id, or not in the bound Run (`data.taskId`, `data.runId`)                                           | Check `task-list --json`; create the Task with `task-create` if it does not exist                                              |
| `task_not_startable` | Task cannot start now: not `ready`, or invalid `--retry-of` (`data.status`, `data.unmetDependencies`, `data.retryOf`) | Wait for running dependencies with `check --wait`; retry or unblock failed ones; inspect `dispatch-show` if already dispatched |
| `inject_rejected`    | `--inject` refused because no recognized agent runs in the target (`data.terminal`, `data.reason`)                    | Start a recognized agent there or pick another terminal; or dispatch without `--inject` and use `terminal send`                |
| `runtime_error`      | Any other failure, including a target terminal that already owns an active Dispatch                                   | Read the message, inspect state, and do not retry unchanged                                                                    |

## Retry, stop, and abandon

Retry only a positively proven failed or stopped attempt. Name the failed Task
with `--task`, since `--spec` creates a new one. Placement is never silently
inherited:

```text
ORCA orchestration worker-start --task <task_id> --retry-of <dispatch_id> --worktree <explicit_placement> --agent <agent> --json
```

After three consecutive failures for one Task, its dispatch context
circuit-breaks and the Task is failed. Do not route around that boundary with a
new Run or an unrelated Dispatch.

For `outcome_unknown`, inspect first, then make an explicit choice:

```text
ORCA orchestration worker-stop --dispatch <dispatch_id> --json
ORCA orchestration worker-abandon --dispatch <dispatch_id> --json
```

`worker-stop` closes only the exact proven supervised agent terminal. It never
deletes the worktree, setup terminal, configured tabs, or unrelated processes.
`worker-abandon` fences orchestration while accepting that resources may remain
live; it performs no remote, process, or filesystem action.

## Retain and release

```text
ORCA orchestration worker-retain --dispatch <dispatch_id> --json
ORCA orchestration worker-release --dispatch <dispatch_id> --json
```

Retain only when the user explicitly wants the settled terminal kept live.
Release works after succeeded and failed reports, archives readable output, and
closes only the exact terminal owned by that settled Dispatch. Replays may call
release again safely. Reused, pre-existing, setup, coordinator, active,
user-taken-over, and unproven terminals are retained.

A `worker-start` that failed before its agent was ready still owns the terminal
it created. Its receipt names `worker-release`, and `worker-list` reports that
row as `reclaimable`; release it there rather than closing the terminal by hand.

Never release because of timeout, TUI idle, heartbeat, status, question,
escalation, or stale/rejected completion. If the receipt says `release_pending`
or `release_unknown`, follow its exact recovery action. Never substitute
`terminal close`.

`orchestration reset` is destructive recovery. Do not run it during active
coordination unless the user explicitly abandons that state.

<!-- bundled-reference: references/worker-contract.md -->

# Worker contract

The injected preamble is authoritative. Copy its command rather than
reconstructing flags. In particular, preserve the exact executable, worker
handle, Dispatch capability, Task ID, and Dispatch ID.

## Heartbeat

Send heartbeats only at the cadence required by the live preamble. Skip them
while blocked inside `ask` or `check --wait`; those calls are liveness signals.

```text
ORCA orchestration send --from <worker_handle> --dispatch-capability <capability> --type heartbeat --subject "alive" --task-id <task_id> --dispatch-id <dispatch_id> --phase "<investigating|implementing|reviewing|waiting>"
```

Use typed lifecycle flags, not a hand-written JSON payload. A heartbeat proves
liveness, never completion.

## Ask and resume

Use Orca `ask` whenever the coordinator must answer. Never open a local question
TUI the coordinator cannot answer.

```text
ORCA orchestration ask --from <worker_handle> --dispatch-capability <capability> --question "<question>" --options "<choice-a>,<choice-b>" --timeout-ms 600000

ORCA orchestration ask --from <worker_handle> --dispatch-capability <capability> --resume <message_id> --timeout-ms 600000
```

A timeout or disconnect leaves the original question pending. Resume its
message ID; do not create a duplicate question.

## Reading coordinator follow-ups

The coordinator steers a running worker with `send --to dispatch:<id>`. That
enqueue is durable but does not interrupt you, so nothing arrives unless you
look:

```text
ORCA orchestration check --terminal <worker_handle> --json
```

Run it at each natural checkpoint — before starting a new file, after a test
run — and once more immediately before `worker_done`, so a redirect or a
cancellation lands before the Task settles. `check` names its caller with
`--terminal`, never `--from`. Stop checking after `worker_done`.

If `check` returns `consumer_fenced`, this process no longer owns its Dispatch:
the Attempt was re-attached to another worker or settled without you. Stop, do
not send `worker_done`, and do not retry the check. An empty `check` never means
you were replaced; `consumer_fenced` is the only way you learn that.

## Escalation

Escalate only before completion and only when the coordinator must intervene:

```text
ORCA orchestration send --from <worker_handle> --dispatch-capability <capability> --type escalation --subject "Blocked: <reason>" --body "<details>" --task-id <task_id> --dispatch-id <dispatch_id>
```

## Completion

Send exactly one terminal report. `--body` is three sentences: what changed,
what was found, and what remains. Use `--outcome failed` when the requested work
is not complete; never hide failure in prose or silently exit.

Append `--files-modified` or `--report-path` only when applicable, using actual
paths. Do not send documentation placeholders as metadata.

```text
ORCA orchestration send --from <worker_handle> --dispatch-capability <capability> --type worker_done --subject "<short status>" --body "<three sentences: work, findings, remaining>" --task-id <task_id> --dispatch-id <dispatch_id> --outcome succeeded
```

After `worker_done`, end the dispatched turn and idle. Do not poll, close your
own terminal, or begin unrelated work. A later direct user instruction is new
user-owned work and must not reuse settled lifecycle IDs; a supervised follow-up
arrives with a fresh preamble and Task block.
