# Playbook — build-change  (the BUILD phase, per unit)

Recipe: Matt `tdd` (seams + tautology guard) + Addy `incremental-implementation` / `/build auto`.

## Per-unit contract (the worker's TASK embeds this)

- **Clean baseline:** `git status --porcelain` empty — refuse to absorb unrelated WIP.
- **Failing test FIRST** at a pre-agreed seam: red before green, one vertical slice at a time. The
  expected value comes from an INDEPENDENT source of truth — never recomputed the way the code does
  (the tautology guard). A bug gets a red reproduction; a new capability gets a failing acceptance
  test.
- **Smallest change** to green. Scope discipline: touch only what the unit requires; adjacent issues
  are NOTICED-BUT-NOT-TOUCHED (noted to backlog, not fixed).
- **Commits:** bisectable, dependency-ordered, each building alone, author = maintainer, no trailers,
  staging only the unit's files (never `git add -A` — it breaks clean rollback). A migration is a
  deliberate multi-commit expand/migrate/contract sequence, not one commit.
- **PR sizing seam** (field-validated: diff size drives merge success): one area or one source
  file per PR, target ≤~400 changed lines; a sub-10-line fix folds into a neighboring unit's PR
  instead of its own; never split one file across two PRs; never combine conflict-prone areas.
- **Irreversibility stop-list:** auth/permissions, destructive migration, payments, deletions,
  deploys, secrets, anything not undoable with `git revert` → STOP and escalate (gate-classification.md).
  Never improvised.

## Evidence

The worker emits the evidence manifest (evidence-manifest.md): base→head SHA, criteria addressed,
commands+exit, and a NEGATIVE CONTROL (revert the production change → the test goes RED). No negative
control = the unit is not built.

## Red flags (fail the unit)

`git add -A`; running the same test twice with no intervening change; >100 lines written before a
test run; a green test whose negative control passes.
