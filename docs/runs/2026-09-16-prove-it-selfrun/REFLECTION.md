# REFLECTION — prove-it self-run 2026-09-16 (wave 2 orchestrated rerun)

`compound-learn` proposal. Nothing below is merged anywhere — every proposed
line needs a recorded human approve first.

## Surprises

- A fresh Orca child worktree carried untracked `package.json` +
  `pnpm-lock.yaml` setup debris, and `wtree.sh` fingerprints untracked
  non-ignored files (`git add -A` into a temp index) — "leave them" would
  have silently broken the `tests rerun` content binding. The clean-baseline
  guard + `ask` caught it; the fix was delete, not proceed.
- `worker-start --agent grok` settles `ready/input_accepted` with
  `turnStart: unsupported` (alpha adapter, no turn observation) — the
  `worker-list` liveness projection (`live`, `agent_status`) stayed the
  authority and the dispatch completed normally. Never resend on silence.
- Codex still usage-limited (through Sep 19) — grok-cli 1.0.31 served as the
  cross-vendor reviewer and did a genuinely independent review (own m1 replay
  in a throwaway tree, stricter error-vs-failure reading than the builder's).
- A non-dict characterization kill ERRORS (AttributeError) rather than FAILs
  — inherent to JSON scopes (no non-dict value has `.get`). The class-level
  RED stays verifier-clean via the bogus case's AssertionError, but a
  single-test nc-command on the non-dict test alone would be refused as
  stillborn. The nc-command must stay class-wide.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: after `worker-start --worktree new-child`, `git status` the unit
  tree before recording anything — setup debris is untracked, unfingerprinted
  by HEAD, and POISONS wtree.sh bindings.
- GOTCHAS: `turnStart: unsupported` is not a failed start — check
  `worker-list` liveness before touching the dispatch.
- TEST_STRATEGY: characterization nets over crash-on-absent-guard behavior
  must keep the nc-command class-wide; a per-test command on an erroring test
  fails `_failure_signature` (errors and no failures).
- STYLE: worker TASK specs that push to a PR branch checked out in another
  worktree must use a unit branch + explicit refspec push with an FF check —
  never force, never checkout-the-same-branch.

## Prompt / playbook tweaks (fleet-side, optional)

- Backlog: `spawn_worker.sh` / dispatch templates could pre-flight the unit
  tree (`git status --porcelain` empty) before prompt injection — filed, not
  edited from here.
