# Runtime policy — dispatch lifecycle + the operational gotchas that are the product

The mechanics of turning a task into a worker, and the hard-won specifics that made clean-sweep /
spec-to-ship reliable. These are not incidental; they are the value.

## Worker unit = worktree + agent + fresh terminal (PR-per-unit)

When BASE is CREATED, record its fork-point SHA (`git rev-parse <default>`) in the ledger header;
every subsequent preflight passes `--fork-point <that sha>` so a stale BASE from an earlier run is
rejected rather than silently reused.

`orca worktree create --name <unit-slug> --base-branch <BASE> --agent <id> --prompt "<TASK>"` — one
unit (`--name` is required by the CLI), off the integration BASE (NOT off a feature branch;
`--base-branch` is the git base, an axis independent of Orca lineage). Read the handle from
`startupTerminal.handle`. Then verify readiness before injecting (`terminal wait --for tui-idle`),
because injecting into a booting TUI loses the prompt. `scripts/spawn_worker.sh` bakes the
fail-closed sequence: create → wait → verify task ready (never force `ready` — the DAG stays
authoritative) → dispatch --inject → Enter (claude pastes but does not submit; codex auto-submits)
→ verify heartbeat, respawn-signal exit 3 on none.

## Worktree lineage: a subtree per unit

A supervised worker's worktree is a CHILD of the coordinator, not a top-level tree — so **omit
`--no-parent`** on the unit's first (builder) worktree. `--no-parent` is for full handoffs where
nobody supervises; a coordinated unit that goes top-level orphans its lineage from the run.

Each unit's DEPENDENT workers — its build-blind reviewer, every fix round, the integrator, the
review-bot reconcile — are FRESH TERMINALS created INSIDE that unit's own worktree (target it by
the WT id recorded at creation: `terminal create --worktree id:<WT>`), never a new worktree and
never `--worktree active` (which can resolve to the coordinator root). A fresh terminal is a fresh
build-blind session that shares the unit's branch, so parenting to the worktree keeps lineage
correct WITHOUT leaking the builder's conversation. The result is a clean subtree:
coordinator → unit-A worktree → {unit-A review, fix rounds, integrator}. One `WT_CLEAN` on the
unit's worktree then tears the whole subtree down at merge. Keep chains ≤3–4 deep.

Operational specifics the script relies on: worktree selectors are composite `uuid::path` ids —
pass `path:/abs/worktree/path` (unambiguous) or the full composite id, never the bare uuid.
Re-dispatch to an already-used terminal handle is a NO-OP — a dead or silent worker gets a FRESH
terminal, never a re-inject. The bounded re-Enter loop in the submit step is safe because an extra
Enter on an already-submitted claude prompt is an empty submit; the heartbeat check, not the send,
is the authoritative verdict.

## Wrong-base detection (M-5 guardrail)

`preflight.py --base <BASE>` before the first PR: BASE must NOT equal the default branch (compared
on CANONICAL refs so `origin/main` can't alias past it), must be a real branch (not a tag/SHA), must
fork from the default's history. Every per-unit PR merges into BASE; if BASE is the default, fixes
land straight on production and bypass the human promotion review. Report-only fleets use
`preflight.py --mode readonly`.

## Third-party review bots — wait → ingest → reconcile

Applies to ANY PR review bot on the repo (Greptile, CodeRabbit, Cursor BugBot, …) — detect the
bot's login dynamically from the repo's app install or prior PRs; never hardcode one. The
integrator (not the coordinator) runs this inside its dispatched task after opening the PR, and
again after every re-push (a new commit re-triggers the bot). It is just another dispatch →
`worker_done` from the coordinator's seat.

1. **Wait, bounded:** poll every ~30s, floor ~2–3 min (the bot needs time to run), cap ~10 min. If
   the cap elapses with no bot activity, log a "did-not-run" checkpoint and proceed — never block
   the loop forever on an external bot.
2. **Ingest comments:** each becomes a tracked item, VALID or FALSE-POSITIVE (dismissed with a
   recorded reason). VALID items fold into the SAME change request as the internal reviewer's
   findings, so the builder addresses both in one pass.
3. **Reconcile pushed commits:** a bot with autofix ON pushes commits AFTER the reviewer's PASS and
   keeps pushing in response to your normalization — non-convergent. Prefer asking the user to set
   it to comment-only for the run (the branch stays stable; comments are just as useful). If it
   must push: normalize its commits (author→maintainer, strip trailers, NEVER squash), re-verify
   green, re-run gitleaks; a rider that lands between force-push and merge is handled by
   force-push-then-immediately-merge (merging deletes the branch, ending the loop), retry ≤3×, then
   confirm the merge commit's second parent has the reviewed tree.

The internal fresh build-blind reviewer reviews the RECONCILED branch and is the final gate. Bot
rounds count WITHIN the review round budget (acceptance-review.md). A bot re-push voids the review
SHA (reviewed-sha-freshness.md).

## Builders never open PRs; integrators do

A builder that self-opens a PR gets the DEFAULT branch as base and merges the fix to the WRONG
branch. The build-blind integrator opens the PR against BASE and asserts `baseRefName==<BASE>`
before merging.

## Commit hygiene

Author = the maintainer, no Co-authored-by / agent trailers, small logical commits, gitleaks before
every push, no NUL-byte/binary source files. Commits are bisectable and dependency-ordered
(infra→models→controllers→version/changelog last), each building alone — NOT a blanket "one commit
per task" (a migration is a deliberate multi-commit expand/migrate/contract sequence).

## Base-drift skip

`orchestration run` silently skips dispatch (leaves the task ready, no failure) when its worktree is
>20 commits behind base and the spec lacks `allow-stale-base: true`. Sync the coordinator's local
base before each wave; a stale base makes workers build on outdated code and stack shims.

## Coordinator inbox mechanics (learned on real runs)

- `check --wait` returns **ONE message per call**. Three workers finishing means three calls —
  loop until the expected count arrives; a coordinator that assumes a batch silently misses
  finishers.
- Read-marking: `task-list`, `inbox`, and `dispatch-show` do NOT mark messages read;
  `check` (default and `--unread`) CONSUMES them. Plan reads accordingly — an exploratory
  `check` in one loop can eat the `worker_done` another loop was waiting on. `check --all`
  (re-reads consumed messages) exists only on newer CLIs; don't depend on it.
- Group addresses (`@all`, `@idle`, `@claude`, `@worktree:<id>`) are broadcast-only. EVERY
  lifecycle message — `worker_done`, `merge_ready`, `escalation`, `decision_gate` replies — goes
  to a concrete terminal handle, never a group.

## Worktree retirement (end-of-unit and end-of-run)

Retire each unit's worktree when its unit MERGES, not at run end — which tears down the whole
subtree (its child review / fix / integrator terminals) in one `WT_CLEAN`. Verify before removing:
the PR is `state=MERGED`, the branch is deleted, and `git status` in the worktree is clean.
NEVER remove the coordinator's own worktree, a dirty worktree, or one whose branch is unmerged —
that destroys work the ledger still counts on. If removal is refused, archive instead of forcing.
A run that skips retirement leaks a worktree per unit; a run that force-cleans destroys unmerged
evidence. Both are ledgered: `unit · worktree · retired ts`.
