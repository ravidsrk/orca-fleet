# Runtime policy — dispatch lifecycle + the operational gotchas that are the product

The mechanics of turning a task into a worker, and the hard-won specifics that made clean-sweep /
spec-to-ship reliable. These are not incidental; they are the value.

## Worker unit = worktree + agent + fresh terminal (PR-per-unit)

`orca worktree create --no-parent --base-branch <BASE> --agent <id> --prompt "<TASK>"` — one unit,
off the integration BASE (NOT off a feature branch; `--no-parent` = Orca lineage, `--base-branch` =
git base, independent axes). Read the handle from `startupTerminal.handle`. Then verify readiness
before injecting (`terminal wait --for tui-idle`), because injecting into a booting TUI loses the
prompt. `scripts/spawn_worker.sh` bakes the fail-closed sequence: create → wait → verify task ready
(never force `ready` — the DAG stays authoritative) → dispatch --inject → Enter (claude pastes but
does not submit; codex auto-submits) → verify heartbeat, respawn-signal exit 3 on none.

## Wrong-base detection (M-5 guardrail)

`preflight.py --base <BASE>` before the first PR: BASE must NOT equal the default branch (compared
on CANONICAL refs so `origin/main` can't alias past it), must be a real branch (not a tag/SHA), must
fork from the default's history. Every per-unit PR merges into BASE; if BASE is the default, fixes
land straight on production and bypass the human promotion review. Report-only fleets use
`preflight.py --mode readonly`.

## Bot-autofix non-convergence

A PR review bot with Autofix ON pushes commits AFTER the reviewer's PASS, and keeps pushing in
response to your normalization — non-convergent. Ask the user to set Autofix to comment-only for the
run (comment-only findings are just as useful, the branch stays stable). If it must stay on: the
integrator normalizes bot commits (author→maintainer, strip trailers, NEVER squash), re-verifies,
and the merge worker polls the bot to a TERMINAL state before merging; a rider that lands between
force-push and merge is handled by force-push-then-immediately-merge (merging deletes the branch,
ending the loop), retry ≤3×, then confirm the merge commit's second parent has the reviewed tree.

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
