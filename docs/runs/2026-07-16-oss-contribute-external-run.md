# oss-contribute — external run, 2026-07-16

Target: `dodopayments/chimely` (upstream, READ access) via the fork `ravidsrk/chimely`.
Source: tracker — 10 open issues (#34-#39, #55, #56, #58, #61). T0 2026-07-15T17:40Z.
Coordinator: manual Orca loop (no `orchestration run`). No merge conductor (no merge rights).

This is the run the mission was extracted from. It began as a `clean-sweep` invocation and surfaced,
in flight, why upstream contribution is a distinct mission: `clean-sweep`'s definition of done is a
merged SHA, which is unreachable on a repo you do not control.

## Outcome: CONTRIBUTED-WITH-PARKED

| Issue | Class | Terminal state |
|-------|-------|----------------|
| #34 | buildable | PR #81 (docs) open; parked on a 1-word imprecision, self-noted |
| #55 | already-has-PR | PR #84 (alt to #79) + assist comment on #79 |
| #56 | already-has-PR | PR #85 (alt to #76) + assist comment on #76 |
| #58 | already-has-PR | PR #83 (alt to #77) + assist comment on #77 |
| #61 | already-has-PR | PR #82 (alt to #72) + assist comment on #72 |
| #35, #36 | externally-covered | maintainer PRs #74/#73; no hollow comment |
| #37, #38, #39 | needs-human | product/schema forks named |

Deliverable: 5 upstream PRs (#81-#85) + 4 review-assist comments carrying 10 confirmed findings, each
quoting the target PR's own diff. Merge left to the maintainers (the intended terminal).

## What the run proved about the mission

1. **Two-denominator enumeration is load-bearing.** The initial triage searched code but not the
   upstream OPEN PRs; a parallel contributor already had PRs for 6 of 10 issues, discovered ~2h into
   building. This is why `upstream-contribution` makes the per-issue PR search a FREEZE-gating step.
2. **The contribution decision is real.** `complement, not compete` (assist), `alternative` (cross-
   linked PR), and `stand-down` (`externally-covered`) were all exercised, each logged as a taste gate.
3. **Terminal is PR-open, not merged.** Every unit closed on an open, internally-reviewed,
   etiquette-conformant PR or a quoted assist comment — never a merge the fleet cannot perform.
4. **The two-reviewer pipeline (codex + greptile) earned its cost.** Each caught real defects the
   other passed (a focus-trap tabindex escape; a missing log-scrub boundary test). Both the fixed
   alternative PR and the finding on the parallel PR reached the maintainers.

## Post-open follow-up (the loop this run added to the mission)

Every PR drew a Greptile review after it opened. Treating "PR open" as terminal would have left that
feedback unanswered, so the run added a follow-up loop, now part of `upstream-contribution.md`: watch
each PR, triage every thread against the current head (one was already resolved by an earlier fix
round — answered, not re-fixed), fix the valid ones as fix rounds on the same branch, and answer every
thread. The `FOLLOWED_UP` ledger flag closes a unit only when no thread is left hanging.

## Post-run addendum (2026-07-17): the alternative-PR lesson

A dodopayments maintainer pushed back on #84 the next day: a parallel reimplementation of an open PR
is not a good use of anyone's time — "I'd rather not maintain two competing PRs for the same issue."
All four alternative PRs (#82/#83/#84/#85) were closed in deference the same day, with the findings
already preserved as assist comments and the branches kept for cherry-picking. The protocol change
this feeds: opening an alternative PR is MAINTAINER-gated — offered inside the assist comment, opened
only on invitation — not a self-serve taste gate as this run originally treated it.

## Honest gaps (fed back into the protocol)

- Codex workers emit no Orca heartbeats; `spawn_worker` exit 3 is a false negative for them — verify
  by pane read. Cost two false "no-boot" diagnoses.
- A builder pane survived its own `worker_done` and pushed an out-of-band commit mid-review. Close
  unit panes at `worker_done`, do not merely consume the message.

Evidence: PRs and comments live on `dodopayments/chimely` (#81-#85, comments on #72/#76/#77/#79). The
run's ledger, per-unit SHA-bound manifests, review artifacts, and integrity inventory were retained in
the fork worktree at close.
