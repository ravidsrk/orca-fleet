# Runtime policy — dispatch lifecycle + the operational gotchas that are the product

The mechanics of turning a task into a worker, and the hard-won specifics that made clean-sweep / spec-to-ship reliable — not incidental; they are the value.

**Anti-drift rule:** this file describes the CLI the installed binary ships. After any Orca upgrade the mechanics are re-witnessed against `orca skills get
orchestration` / `orca skills get orca-cli` — but the compact guide is a KERNEL, not the contract: enumerate `orca skills get <topic> --references` and load
each `--reference <name>` (`--full` on older CLIs), because the worker contract, recovery, and legacy-migration rules live only there (`skills.ts:50-58`).
pin-it owns that loop; hand-editing from memory is how it went stale twice.

## Worker unit = worktree + agent + fresh terminal (PR-per-unit)

When BASE is CREATED, record its fork-point SHA (`git rev-parse <default>`) in the ledger header; every subsequent preflight passes `--fork-point <that sha>`
— a stale BASE is rejected, never silently reused.

The normal supervised spawn is **`worker-start`**: `orca orchestration worker-start --task <id> --worktree new-child --name <unit-slug> --agent <id> --setup
run --json` (compose: worktree create → agent terminal → readiness → dispatch). It exits 0 only when the worker is **ready** — but read `ready` narrowly: at
v1.4.199 it means the preamble WRITE WAS ACCEPTED, not that the agent started a turn (`local-worker-start.ts:263`). The next release demands an observed
`turn_started` and returns `state: outcome_unknown` otherwise. Source-witnessed at v1.4.199 (`local-worker-start.ts:243-263`); live probe owed — pin-it.

The receipt carries more than the flat four: `runId, taskId, dispatchId, state, stage, setup, launch{requested,effective}, mode, effects[],
residualResources[]`, and on a bad start `failedStage, lastError, recovery, nextCommands` (`worker-start-receipt.ts:42-69`). The agent terminal is the
`effects[]` entry with `kind: terminal, role: agent`. Read `launch.effective`, never `requested` — a model, effort, or permission flag is only what the host
actually applied. `--worktree current` / an exact worktree id = a fresh agent terminal, no setup rerun; `--terminal <handle>` = reuse an exact idle agent
(cleanup ownership transfers).

**Refusals are typed codes** — branch on `error.code`, never on exit status or stderr text, and treat `error.data.nextSteps` as the exact recovery text (older
hosts may omit `data`): `task_not_found`, `task_not_startable` (+`data.unmetDependencies`, `data.retryOf`), `inject_rejected`, `nested_worker_depth_exceeded`,
`consumer_fenced`, `dispatch_inactive` are policy answers; `runtime_error` is the catch-all whose recovery is "do not retry unchanged"
(`orchestration-dispatch-refusal-contract.ts:8`, `orchestration/recovery-and-cleanup:96-108`).

`terminal create` + `dispatch --inject` remains the **low-level, deliberately unsupervised** lane: no worker-lifecycle row, so `worker-stop`/`worker-release`
never touch that process. It is NOT invisible — `worker-list` lists it as `unsupervised` with terminal state `retained` (`orchestration-worker-specs.ts:124`).
Use it for custom argv/topology `worker-start` cannot express (and for `PROFILE=ro`), and record the trade in the ledger. **`--inject` SUBMITS the preamble**
— it does not merely paste it (`dispatch-methods.ts:155-165`) — and `--json` returns `result.prompt{requestId, stages}` over `input_accepted | turn_started`
(`runtime-terminal-contracts.ts:221-225`). So: read the receipt; if `turn_started` is absent, replay it ONCE with `terminal send --retry-request <id>
--wait-submit <secs>`, which returns the input-accepted receipt on timeout and never resends (`terminal-send.ts:19-22`). `accepted: true` proves input
acceptance, not a started turn — **never resend on silence** (`orchestration/recovery-and-cleanup:92-94`). The bounded re-Enter loop is deleted; an extra
Enter on a started turn is a stray keystroke outside the receipt model.

## The worker contract (what every dispatch preamble must state)

The runtime enforces this and the fleet had none of it written down. Every mission's preamble says:

- `worker_done` **requires `--outcome succeeded|failed`** and **omits `--to`** — an active Dispatch defaults to its owning Run mailbox, which is the preferred
  address; a terminal handle is not (`orchestration.ts:74-76`, `orchestration/worker-contract:71`).
- Every worker send carries `--from <worker_handle> --dispatch-capability <capability>`, both handed to it in the preamble
  (`orchestration/worker-contract:13,25-27`).
- Evidence rides TYPED flags — `--report-path <path>`, `--files-modified <csv>` — not a hand-rolled `--payload` JSON blob, which PowerShell strips quotes from
  (`orchestration.ts:49`).
- A worker runs `check --terminal <its own handle>` at checkpoints and once before `worker_done`. A `consumer_fenced` from that check means **stop**: it no
  longer owns its Dispatch and must not send `worker_done` (`orchestration/worker-contract:40-51`).

## Worktree lineage: a subtree per unit

A supervised worker's worktree is a CHILD of the coordinator, not a top-level tree — pass **`--parent-worktree active`** on the unit's first (builder)
worktree (with `worker-start`, that is `--worktree new-child`). Omitting `--no-parent` relies on Orca inferring the parent from the cwd, which only works
"when it can"; `--no-parent` is the OPPOSITE — a top-level full handoff nobody supervises — and orphans a coordinated unit's lineage from the run.

Each unit's DEPENDENT workers — its build-blind reviewer, every fix round, the integrator, the review-bot reconcile — are FRESH agent terminals created INSIDE
that unit's own worktree (`worker-start --worktree <exact id>`, an `id:<repoId>::<path>` selector; a bare repo id is rejected), never a new worktree and never
`--worktree active` (which can resolve to the coordinator root). A fresh terminal is a fresh build-blind session sharing the unit's branch, so parenting to
the worktree keeps lineage correct WITHOUT leaking the builder's conversation: coordinator → unit-A worktree → {unit-A review, fix rounds, integrator}. Keep
chains ≤3–4 deep.

**Nested depth:** workers do not dispatch sub-workers — `nested_worker_depth_exceeded` fires at depth 1 by default, counted from the issuing terminal (it is
Settings-tunable, so on a raised host this stops being runtime-enforced and stays fleet policy). Acceptance-review's axes are dispatched by the COORDINATOR,
one worker per axis — never by a reviewer worker fanning out its own.

Operational specifics: a worktree id is the composite `<repoId>::<worktreePath>` returned by `worktree create --json` — pass `path:/abs/worktree/path`
(unambiguous) or that full id, never the bare repo id. On Linux, a bare `orca` outside an Orca-managed terminal is usually the GNOME screen reader — use
`orca-ide` there. After an accepted `worker_done`, run **`worker-release --dispatch <id>`** (Orca preserves inspectable output, then closes only the exact
agent terminal that dispatch owned) — or `worker-retain` at the user's explicit request. Its exit contract: `retained`, `release_pending`, and
`already_released` all exit 0 (it is idempotent); **only `release_unknown` exits 1** and needs the receipt's own recovery action
(`orchestration-worker-specs.ts:102`). The pane that outlived its `worker_done` under a new handle (the old dual-writer class) is now fenced by the runtime at
settlement; release is still the fleet's hygiene step — never on a timeout, TUI-idle, or a heartbeat gap (those are liveness questions, liveness-resume.md,
not completion).

## Wrong-base detection (M-5 guardrail)

`preflight.py --base <BASE>` before the first PR: BASE must NOT equal the default branch (canonical refs — `origin/main` can't alias past it), must be a real
branch, and must fork from the default's history. Every per-unit PR merges into BASE; if BASE is the default, fixes land straight on production and bypass the
human promotion review. Report-only fleets use `--mode readonly`.

## Third-party review bots — wait → ingest → reconcile

Applies to ANY PR review bot (Greptile, CodeRabbit, Cursor BugBot, …) — detect its login from the repo's app install or prior PRs; never hardcode one. The
integrator (not the coordinator) runs this after opening the PR and after every re-push (a new commit re-triggers the bot); it is just another dispatch →
`worker_done`.

1. **Wait, bounded:** poll every ~30s, floor ~2–3 min, cap ~10 min. If the cap elapses with no bot activity, log a "did-not-run" checkpoint and proceed —
   never block the loop on an external bot.
2. **Ingest comments:** tag each VALID or FALSE-POSITIVE (dismissed with a recorded reason). HOLD the VALID set — it becomes a change request only after the
   internal review, so both finding sets reach the builder as one batch.
3. **Reconcile pushed commits:** a bot with autofix ON pushes AFTER the reviewer's PASS and keeps pushing in response to your normalization — non-convergent.
   Prefer asking the user for comment-only. If it must push: normalize its commits (author→maintainer, strip trailers, NEVER squash), re-verify green, re-run
   gitleaks; a rider landing between force-push and merge is handled by force-push-then-immediately-merge (merging deletes the branch, ending the loop), retry
   ≤3×, then confirm the merge commit's second parent has the reviewed tree.

Order is strict: reconcile FIRST (steps 1–3), THEN the internal fresh build-blind reviewer reviews the RECONCILED branch — the final gate, never before the
bot is reconciled. Only after that verdict are its findings and the held VALID bot comments assembled into ONE change request. Bot rounds count WITHIN the
review round budget (acceptance-review.md); a bot re-push voids the review SHA (reviewed-sha-freshness.md) and restarts the sequence.

## Builders never open PRs; integrators do — and commit hygiene

A builder that self-opens a PR gets the DEFAULT branch as base and merges the fix to the WRONG branch. The build-blind integrator opens the PR against BASE
and asserts `baseRefName==<BASE>`. Author = the maintainer, no Co-authored-by / agent trailers, small logical commits, gitleaks before every push, no
NUL-byte/binary source files. Commits are bisectable and dependency-ordered (infra→models→controllers→version/changelog last), each building alone — not a
blanket "one commit per task" (a migration is a deliberate multi-commit expand/migrate/contract sequence).

## Run scope: a real Run, not a filtered dump

Create or bind the run's namespace once: `orca orchestration run-create --objective "<text>" --json` — the returned run id IS the fleet's scope: `task-list
--run`, `worker-list --run`, and the coordinator `check` all honor it. `orchestration run` / `coordinator-start` are retired scheduler aliases returning the
recovery action; the loop is the manual one (task-create → worker-start → `check --wait`). Record the run id in the ledger header (liveness-resume.md).

## Coordinator inbox mechanics

- A consuming `check` returns the bound Run's oldest FIFO **Delivery — up to 50 messages in one batch** — and replays that exact batch until you `--ack
  <delivery_id>`. Process EVERY message in the batch (reply to `question`s, settle `worker_done`s, release or reuse those workers) and only then `check --ack
  <id> --wait` for the next window.
- Read-marking: `task-list`, `inbox`, and `dispatch-show` do NOT mark messages read; `check` (default and `--unread`) CONSUMES what it returns — to inspect
  without consuming use `check --peek` (unread) or `check --all` (history). `task-list --brief` collapses whitespace and caps each echoed spec at 160 chars
  (`spec_truncated` marks shortened rows); omit it when the full spec is needed.
- Keepalives go to **stderr** every 15 s (`{"_keepalive":true,…}`, with `_heartbeat` alongside as a deprecated alias), NEVER stdout — pipe stdout only into
  parsers (`runtime/scripts/pm.py <file>` for saved streams) (`check-keepalive.ts:18-26`).
- Mutations accept `--retry-request <id>`: a lost response never risks a duplicate dispatch — re-issue with the same request id and the runtime dedupes
  (`request-show --request <id>`; `completed`/`pending`/`absent`). Use it on every non-idempotent orchestration call.
- Group addresses (`@all`, `@idle`, `@claude`, `@codex`, `@grok`, `@cursor`, `@opencode`, `@gemini`, `@droid`, `@worktree:<id>`, …) are broadcast-only. The
  RUNTIME rejects a group address for `worker_done` and `heartbeat` only (`message-send-handler.ts:51-58`) — a `merge_ready` to `@all` really would fan out.
  The rest is FLEET policy and it stands: every lifecycle message goes to a concrete terminal or `dispatch:<id>`. A `worker_done` for the active
  `taskId`+`dispatchId` auto-completes the task; do NOT follow it with `task-update --status completed` (reserve manual status writes for recovery/override).
- The runtime writes no `type=dispatch`/`type=handoff` rows on inject, though both are valid `send --type` values a fleet could write and the retired
  coordinator ignores. `merge_ready` is fleet-written only (merge-serialization.md); point at the evidence manifest with the typed `--report-path <path>`
  flag, never a `reportPath` payload key (orca-dag-semantics.md).

## Progress surface (Orca-native, complements the ledger)

The file ledger is the coordinator's durable brain; the Orca **worktree comment** is the live, human-glanceable status on the workspace card. Workers update
it at checkpoints — `orca worktree set --worktree active --comment "<what is happening>" --workspace-status <todo|in-progress|in-review|completed>`. It never
replaces the ledger (comments are best-effort and lossy).

## Worktree retirement (end-of-unit and end-of-run)

Retire each unit's worktree when its unit MERGES, not at run end — tearing down the whole subtree (its child review / fix / integrator terminals) in one
`WT_CLEAN`. Verify first: the PR is `state=MERGED`, the branch is deleted, and `git status` in the worktree is clean. NEVER remove the coordinator's own
worktree, a dirty worktree, or one whose branch is unmerged; if removal is refused, archive instead of forcing. Both leak and force-clean classes are
ledgered: `unit · worktree · retired ts`. Name the verbs: terminals first with `terminal close --worktree <selector> --all`, the canonical teardown that stops
every process the workspace owns and durably removes its tabs, layouts, and resume records (`terminal-close.ts:8-14`; `terminal stop` is deprecated plumbing)
— then the tree with `worktree rm --worktree id:<repoId>::<path>` (`orca-cli:91`). A bulk close that cannot confirm every PTY is `unverifiable`, not clean:
ledger it as a leak, never force it.

## Live probes owed (pin-it)

Each is one receipt away on an installed v1.4.199 and none needs a remote host; until run, these claims are source-witnessed only.

1. `worker-start` per roster agent — record `state`, `stage`, `launch.effective`, `turnStart`, and the host's `agentDefaultArgs` permission mode.
2. `dispatch --inject --json` receipt `prompt.stages`, then a `--retry-request` replay.
3. Mixed-batch `check` (does a `--types` wake deliver other types?) and `send --to @all --type merge_ready` in a scratch Run.
4. `task-create --deps '["bogus"]'` → archive the refutation.
5. `gate-create` → `gate-resolve` → `dispatch-show --task --preamble`: is the resolution there?
