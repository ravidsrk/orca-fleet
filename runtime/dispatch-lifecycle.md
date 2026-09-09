# Runtime policy — dispatch lifecycle + the operational gotchas that are the product

The mechanics of turning a task into a worker, and the hard-won specifics that made clean-sweep /
spec-to-ship reliable — not incidental; they are the value.

**Anti-drift rule:** this file describes the CLI the installed binary actually ships. After any Orca
upgrade, the mechanics sections are re-witnessed against `orca skills get orchestration` /
`orca skills get orca-cli` (the version-matched guides the binary serves) — pin-it owns that loop;
hand-editing from memory is how it went stale twice.

## Worker unit = worktree + agent + fresh terminal (PR-per-unit)

When BASE is CREATED, record its fork-point SHA (`git rev-parse <default>`) in the ledger header; every
subsequent preflight passes `--fork-point <that sha>` — a stale BASE is rejected, never silently reused.

The normal supervised spawn is **`worker-start`**: `orca orchestration worker-start --task <id>
--worktree new-child --name <unit-slug> --agent <id> --setup run --json` (compose: worktree create
→ agent terminal → readiness → dispatch). On installed Orca the call exits 0 only when the worker
is **ready**; the receipt is flat (`taskId`, `dispatchId`, `state`, `effects[]` — the agent
terminal is the `effects[]` entry with `kind: terminal, role: agent`). `--worktree current` / an
exact worktree id = a fresh agent terminal, no setup rerun; `--terminal <handle>` = reuse an exact
idle agent (cleanup ownership transfers). Refusals come back as typed codes (`task_not_startable`
with `data.unmetDependencies`, `nested_worker_depth_exceeded`, `consumer_fenced`, …) — branch on
the code, never on scraped exit status or stderr text.

`terminal create` + `dispatch --inject` remains the **low-level, deliberately unsupervised** lane:
no worker-lifecycle row, so `worker-stop`/`worker-release` never touch that process and
`worker-list` accounting does not see it. Use it for custom argv/topology `worker-start` cannot
express (and for `PROFILE=ro` — worker-start would append Orca's YOLO flag, silently upgrading a
read-only reviewer to a bypass one), and record the trade in the ledger. The bounded re-Enter
submit loop stays the live mechanism on current CLIs (spawn_worker.sh); receipted sends
(`--wait-submit` / `turn_started`) exist only in upstream's unreleased source — adopt them after
that upgrade lands, not before.

## Worktree lineage: a subtree per unit

A supervised worker's worktree is a CHILD of the coordinator, not a top-level tree — pass
**`--parent-worktree active`** on the unit's first (builder) worktree (with `worker-start`, that is
`--worktree new-child`). Omitting `--no-parent` relies on Orca inferring the parent from the cwd,
which only works "when it can"; `--no-parent` is the OPPOSITE — a top-level full handoff nobody
supervises — and orphans a coordinated unit's lineage from the run.

Each unit's DEPENDENT workers — its build-blind reviewer, every fix round, the integrator, the
review-bot reconcile — are FRESH agent terminals created INSIDE that unit's own worktree
(`worker-start --worktree <exact id>`), never a new worktree and never `--worktree active` (which
can resolve to the coordinator root). A fresh terminal is a fresh build-blind session that shares
the unit's branch, so parenting to the worktree keeps lineage correct WITHOUT leaking the builder's
conversation. The result: coordinator → unit-A worktree → {unit-A review, fix rounds, integrator}.
Keep chains ≤3–4 deep.

**Nested depth:** workers do not dispatch sub-workers — `nested_worker_depth_exceeded` fires at
depth 1 by default, counted from the issuing terminal. Acceptance-review's axes are dispatched by
the COORDINATOR, one worker per axis — never by a reviewer worker fanning out its own.

Operational specifics: a worktree id is the composite `<repoId>::<worktreePath>` returned by
`worktree create --json` — pass `path:/abs/worktree/path` (unambiguous) or that full id, never the
bare repo id. On Linux, a bare `orca` outside an Orca-managed terminal is usually the GNOME screen
reader — use `orca-ide` there. After an accepted `worker_done`, run **`worker-release --dispatch
<id>`** (Orca preserves inspectable output, then closes only the exact agent terminal that dispatch
owned) — or `worker-retain` at the user's explicit request. The pane that outlived its
`worker_done` under a new handle (the old dual-writer class) is now fenced by the runtime at
settlement; release is still the fleet's hygiene step — never on a timeout, TUI-idle, or a
heartbeat gap (those are liveness questions, liveness-resume.md, not completion).

## Wrong-base detection (M-5 guardrail)

`preflight.py --base <BASE>` before the first PR: BASE must NOT equal the default branch (canonical
refs — `origin/main` can't alias past it), must be a real branch, must fork from the default's
history. Every per-unit PR merges into BASE; if BASE is the default, fixes land straight on
production and bypass the human promotion review. Report-only fleets use `--mode readonly`.

## Third-party review bots — wait → ingest → reconcile

Applies to ANY PR review bot on the repo (Greptile, CodeRabbit, Cursor BugBot, …) — detect the
bot's login dynamically from the repo's app install or prior PRs; never hardcode one. The
integrator (not the coordinator) runs this after opening the PR and after every re-push (a new
commit re-triggers the bot). It is just another dispatch → `worker_done` from the coordinator's
seat.

1. **Wait, bounded:** poll every ~30s, floor ~2–3 min, cap ~10 min. If the cap elapses with no bot
   activity, log a "did-not-run" checkpoint and proceed — never block the loop on an external bot.
2. **Ingest comments:** each is tagged VALID or FALSE-POSITIVE (dismissed with a recorded reason).
   HOLD the VALID set — it is not turned into a change request yet (that happens after the internal
   review, so both finding sets go to the builder as one batch).
3. **Reconcile pushed commits:** a bot with autofix ON pushes commits AFTER the reviewer's PASS and
   keeps pushing in response to your normalization — non-convergent. Prefer asking the user to set
   it to comment-only for the run. If it must push: normalize its commits (author→maintainer, strip
   trailers, NEVER squash), re-verify green, re-run gitleaks; a rider that lands between force-push
   and merge is handled by force-push-then-immediately-merge (merging deletes the branch, ending
   the loop), retry ≤3×, then confirm the merge commit's second parent has the reviewed tree.

Order is strict: reconcile FIRST (steps 1–3, integrator), THEN the internal fresh build-blind
reviewer reviews the RECONCILED branch — it is the final gate and never runs before the bot is
reconciled. Only after that verdict are its findings and the held VALID bot comments assembled into
ONE change request, so the builder addresses both in a single pass on the same branch. Bot rounds
count WITHIN the review round budget (acceptance-review.md); a bot re-push voids the review SHA
(reviewed-sha-freshness.md) and restarts the sequence.

## Builders never open PRs; integrators do

A builder that self-opens a PR gets the DEFAULT branch as base and merges the fix to the WRONG
branch. The build-blind integrator opens the PR against BASE and asserts `baseRefName==<BASE>`.

## Commit hygiene
Author = the maintainer, no Co-authored-by / agent trailers, small logical commits, gitleaks before
every push, no NUL-byte/binary source files. Commits are bisectable and dependency-ordered
(infra→models→controllers→version/changelog last), each building alone — not a blanket "one commit
per task" (a migration is a deliberate multi-commit expand/migrate/contract sequence).

## Run scope: a real Run, not a filtered dump

Create or bind the run's namespace once: `orca orchestration run-create --objective "<text>" --json`
— the returned run id IS the fleet's scope: `task-list --run`, `worker-list --run`, and the
coordinator `check` all honor it. `orchestration run` / `coordinator-start` are retired scheduler
aliases (no effects; they return the recovery action); the loop is the manual coordinator loop
(task-create → worker-start → `check --wait`) under a Run. Record the run id in the ledger header
(liveness-resume.md).

## Coordinator inbox mechanics

- A consuming `check` returns the bound Run's oldest FIFO **Delivery — up to 50 messages in one
  batch** — and replays that exact batch until you `--ack <delivery_id>`. Process EVERY message in
  the batch (reply to `question`s, settle `worker_done`s, release or reuse those workers) and only
  then `check --ack <id> --wait` for the next window.
- Read-marking: `task-list`, `inbox`, and `dispatch-show` do NOT mark messages read; `check`
  (default and `--unread`) CONSUMES the matches it returns — to INSPECT without consuming:
  `check --peek` (unread) or `check --all` (full history). `task-list --brief` collapses
  whitespace and caps each echoed spec at 160 chars (`spec_truncated` marks shortened rows) for
  coordinator DAG sweeps; omit `--brief` when the full spec is needed.
- `check --wait` heartbeats go to **stderr** on current CLIs (`{"_keepalive":true,…}`), NEVER
  stdout — pipe stdout only into parsers (`runtime/scripts/pm.py <file>` for saved streams).
- Mutations accept `--retry-request <id>`: a lost response never risks a duplicate dispatch —
  re-issue with the same request id and the runtime dedupes (`request-show` to inspect). Use it on
  every non-idempotent orchestration call.
- Group addresses (`@all`, `@idle`, `@claude`, `@codex`, `@grok`, `@cursor`, `@opencode`,
  `@gemini`, `@droid`, `@worktree:<id>`, …) are broadcast-only; EVERY lifecycle message
  (`worker_done`, `merge_ready`, `escalation`, `decision_gate` replies) goes to a concrete terminal
  or `dispatch:<id>`, never a group. A `worker_done` for the active `taskId`+`dispatchId`
  auto-completes the task; do NOT follow it with `task-update --status completed` (reserve manual
  status writes for recovery/override).
- No `type=dispatch`/`type=handoff` rows exist (prompt inject is PTY-only). `merge_ready` is
  fleet-written only (merge-serialization.md). Put `reportPath` on `worker_done` so the retained
  DB points at the evidence manifest (orca-dag-semantics.md).

## Progress surface (Orca-native, complements the ledger)

The file ledger is the coordinator's durable brain; the Orca **worktree comment** is the live,
human-glanceable status on the workspace card. Workers update it at checkpoints —
`orca worktree set --worktree active --comment "fix implemented; running integration tests"` — and
set the card lane with `--workspace-status <todo|in-progress|in-review|completed>`. It never
replaces the ledger (comments are best-effort and lossy).

## Worktree retirement (end-of-unit and end-of-run)

Retire each unit's worktree when its unit MERGES, not at run end — tearing down the whole subtree
(its child review / fix / integrator terminals) in one `WT_CLEAN`. Verify first: the PR is
`state=MERGED`, the branch is deleted, and `git status` in the worktree is clean. NEVER remove the
coordinator's own worktree, a dirty worktree, or one whose branch is unmerged; if removal is
refused, archive instead of forcing. Both leak and force-clean classes are ledgered:
`unit · worktree · retired ts`.
