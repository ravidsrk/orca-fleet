---
name: oss-contribute
description: >-
  Turn a bounded set of issues on a repo you do NOT control into landed open-source contributions.
  Each actionable issue is skeptic-triaged (including a search of the upstream repo's OPEN PRs, not
  just its code), built on a fork with a failing-first test, reviewed build-blind, and opened as an
  etiquette-correct PR against the upstream default branch — or, where a maintainer PR already
  exists, shared as a quoted review-assist comment and/or a cross-linked alternative PR. The loop
  re-enumerates until the actionable set is dry. Merge is the maintainer's; the fleet never merges.
  Use when "contribute to this project", "open PRs for these upstream issues", "help out this OSS
  repo", "send fixes upstream", "we only have a fork". Not for a repo you own and can merge (that is
  clean-sweep — merged-SHA closure) and not for building a net-new project (ship-it).
license: MIT
proof: external-run
proof_evidence: docs/runs/2026-07-16-oss-contribute-external-run.md
compatibility: >-
  HARD dependency: Orca runtime + the orchestration skill (Orca CLI). git + gh, a FORK you can push
  to, and READ on the upstream repo. One worker playbook pack per worker (Matt triage/tdd, or Addy
  build) — never two routers in one worker.
---

# oss-contribute — land upstream contributions on a repo you do not control

You are the **COORDINATOR** of a run that turns a bounded set of upstream issues into landed
contributions and leaves each one at a maintainer-facing terminal state. Thin loop-holder: you
enumerate, dispatch the per-issue pipeline, verify against authoritative state, and keep the ledger
FILE (your memory is compacted; the ledger survives). You never review, code, open PRs, or comment —
every one is a dispatched worker.

Read [ARCHITECTURE.md](../../ARCHITECTURE.md) once. Composes `upstream-contribution`,
`remediate-finding`, `build-change`, `acceptance-review` playbooks; rides `evidence-manifest`,
`dispatch-lifecycle`, `ledger-contract`, `reviewed-sha-freshness`, `liveness-resume`,
`gate-classification`, `orca-dag-semantics` runtime policies. It does NOT ride `merge-serialization`:
there is no merge train, because the fleet has no merge rights on the target.

## Two terminal outcomes

- **CONTRIBUTED** — every actionable issue has an OPEN, internally-reviewed, etiquette-correct PR or a
  posted review-assist; parks are only `externally-covered`, `externally-resolved`, or `out-of-scope`.
- **CONTRIBUTED-WITH-PARKED** (degraded) — the set is exhausted but ≥1 park is `needs-human` (a stuck
  gate: CLA unsigned, design fork). Never reported as CONTRIBUTED.

Merge is NOT the definition of done — you have READ on the target, so `awaiting-maintainer-merge` is a
NORMAL terminal, not a failure. "Backlog to zero" here means the actionable set is drained into
contribution artifacts, never that issues are closed.

## The source (upstream tracker — TWO denominators)

`source=tracker` on a repo you do not control. Record run-start `T0`. The denominator is the upstream
open-issue set (paginated to the end) AND, per upstream-contribution.md, the upstream OPEN PR set per
issue — an issue with an in-flight maintainer PR is `already-has-PR`, not `skip`. Re-enumerate both
each loop; a PR that appears mid-run reclassifies its issue.

## Pipeline

```
SELF-ORIENT → FORK + ENUMERATE (open issues AND their open PRs) → SKEPTIC-TRIAGE (reproduce/refute;
  redundancy = code AND upstream PRs) → FREEZE
  → PER-ISSUE (upstream-contribution): classify {buildable | already-has-PR | needs-human |
      externally-resolved}
      · buildable → build-change (failing-first) → build-blind acceptance-review → fix rounds
          → open PR (fork head → upstream base, base asserted, etiquette body) → reconcile bots
          → FOLLOW UP on post-open review/CI until merged, closed, or feedback is quiet
      · already-has-PR → the contribution decision (assist / alternative / stand-down)
  → CLOSE the unit with evidence (PR url + reviewed_sha + threads answered, or assist comment url)
  → re-ENUMERATE (loop until dry) → FINAL REPORT + human gates
```

Run the coordinator as a MANUAL loop (`task-create → spawn → dispatch --inject → check --wait`), not
`orchestration run` — you want the file-ledger boolean gate under your control. No conductor terminal
is spawned (nothing merges).

## Convergence proof (definition of done)

A full re-enumeration finds ZERO actionable issues that are not (a) CONTRIBUTED — an OPEN PR against
the upstream default (`baseRefName==<default>` asserted, `headRefOid==reviewed_sha` fresh, a
failing-first test with a revert-audited negative control, bots reconciled, etiquette conformant, AND
every post-open review thread answered per upstream-contribution.md follow-up) with the PR url in the
closing note, ledger flags `BUILD_DONE`…`PR_OPEN`…`FOLLOWED_UP` all `t`; or (b) a posted
review-assist whose findings are each quoted from the target PR's diff; or (c) PARKED
(`externally-covered` with the covering PR ref, `needs-human` naming its gate). The final enumeration
is pasted in the ledger. Manifest names CONTRIBUTED or CONTRIBUTED-WITH-PARKED.

## The contribution decision (never silent — gate-classification.md)

For `already-has-PR`, upstream-contribution.md's assist / alternative / stand-down table is a TASTE
gate: draft the choice, log it in `docs/DECISIONS.md`, a human may veto. Default posture is
`complement, not compete`. An alternative PR ALWAYS cross-links the parallel PR and never masquerades
as the only take. A closing keyword goes on a concrete issue only, never an RFC/meta/tracking issue.

## Ledger (header first, then rows)

Header per liveness-resume.md: `RUN · COORDINATOR · BASE=- · FORK_POINT=- · T0 · SOURCE · WIP ·
UPSTREAM · FORK` (BASE/FORK_POINT recorded as `-`, never renamed — there is no integration base;
UPSTREAM and FORK are additive trailing columns). Phase marker + unit flags per ledger-contract.md —
every canonical flag kept except `MERGED` (dropped: merge is the maintainer's, the fleet has none),
extended with `CLASS` and `FOLLOWED_UP`:

`| task_id | issue | title | CLASS | BUILD_DONE | REVIEWED | PR_OPEN | BOT | FOLLOWED_UP | WT_CLEAN | park | evidence |`
CLASS ∈ buildable · already-has-PR · needs-human · externally-resolved · out-of-scope. `PR_OPEN`
carries the PR url + reviewed_sha (or the assist comment url); `FOLLOWED_UP` is `t` only when every
post-open review thread is answered and CI is green-or-explained; `WT_CLEAN` flips when the fork
worktree is retired at the unit's terminal (no merge to wait on). RESUME scopes to header coordinator
+ ledger task ids.

## Gates + supervision

Batch human gate for stand-down/refuted closes. The alternative-vs-assist fork is a per-issue taste
gate (log, do not silently pick). CLA/DCO that needs a human signature → PARK `needs-human`, never
forge. Stalls → liveness-resume WATCH; compaction → CONTEXT HANDOFF then RESUME; death → RESUME.
Never self-merge, never `--admin` — the fleet has no merge authority here by construction.

## Anti-patterns

Enumerating issues but not upstream PRs (you rebuild what a maintainer already has in flight — the
protocol gap this mission exists to close). Opening a silent duplicate of an existing PR. Fire-and-
forget: opening a PR and abandoning it when maintainer/bot review or CI arrives (a contribution that
ignores its review threads rots — follow up until merged, closed, or quiet). Treating an open PR as
"done" before its feedback settles (merge is the maintainer's; a merged claim you cannot perform is a
lie). Ignoring `CONTRIBUTING`/DCO. Closing from worker memory. Owning the merge.

## Related

`clean-sweep` (drain a backlog you OWN, merged-SHA closure — the mission this forked from), `ship-it`
(build net-new), `review-it` (verdict only, no PRs), `harden-it`/`speed-it`/`modernize-it`/`prove-it`/
`deflake-it` (specialist campaigns on your own repo). Chains after `map-it` when the contribution set
needs charting first (mission-chaining.md).
