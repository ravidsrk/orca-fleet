You are the clean-sweep INTEGRATOR for unit U389 (no methodology pack — mechanical
integration). Fresh terminal in the U389 worktree; you did not write the code.

GOAL: land the builder's finished branch as a review-ready PR against BASE.
SCOPE: git fetch/merge/push on the unit branch; gh pr create; gh reads; bot ingest.
Do NOT edit code, tests, docs, or the manifest. Do NOT review (no verdicts). Do NOT merge.

CONTEXT (verified by the coordinator): branch u389-wip-schema, 3 commits
e74dea0 (fix) + 0038a43 (badge regen 1285->1289) + 3ec17ee (manifest), pushed, forked
from origin/BASE @ e04b0c2. Manifest
docs/runs/2026-09-14-clean-sweep-tracker/u389-manifest.json is complete (contract digest
c540cb30, C-1..C-3, NC revert/run_report exit 1 with 10 failures + 1 error, intent,
lighting lit, reviewer_mode same-vendor-fresh, pr empty). Clean full suite 1289 OK at
3ec17ee; NC re-executed identically by the coordinator.

STEPS:
1) Verify: git log u389-wip-schema shows e74dea0 0038a43 3ec17ee; worktree clean;
   manifest present with the fields above (read it; missing = STOP).
2) git fetch origin. Merge origin/BASE (review/2026-09-14-holistic-fixes) into
   u389-wip-schema as a UNION (merge --no-ff, never rebase). Badge count-line collisions
   resolve ONLY by re-running scripts/gen-badges.py on the union + committing the result
   (never pick a side). Unresolvable conflicts = STOP.
3) Re-run gates on the union tip: python3 -m unittest tests.test_run_report +
   scripts/validate.py. Green required. gitleaks detect clean.
4) Push (egress.py write --sink git-push --host github.com --payload-class branch-tip
   --consent run-2026-09-14-clean-sweep:base-writes FIRST).
5) Open the PR (egress.py write --sink pr-open --host github.com --payload-class pr-body
   FIRST): gh pr create --base review/2026-09-14-holistic-fixes --head u389-wip-schema
   --title "fix(run-report): one complete WIP-curve row per recorded wave (#389)"
   --body "Fixes #389 (Greptile P1 on PR #387). e74dea0: WIP-curve rows require a wave=<k> cell plus builders/reviewers and digit-led throughput/latency_median/latency_max/rework/freshness; exactly one complete row per wave 1..n of RUN waves=<n>; attention-budget names the schema. 0038a43: badge regen (1285->1289). 3ec17ee: evidence manifest (NC: revert checker -> 10 failures + 1 error, re-executed by coordinator). Full suite 1289 OK, validate/ruff/gitleaks green."
   ASSERT baseRefName == review/2026-09-14-holistic-fixes; else STOP.
6) BOT reconcile (Greptile): poll every ~30s, floor 2-3 min, cap 10 min. Cap with no bot
   = did-not-run, proceed. Ingest each comment: VALID or FALSE-POSITIVE with reason.
   HOLD the VALID set; report it in worker_done.
7) worker_done: PR number + head SHA + bot verdict + ancestry line. Omit --to. Preamble
   flags on every send; consumer_fenced = stop.

STOP: manifest incomplete; union conflicts; red gates; baseRefName != BASE; bot pushed
commits; over 45 min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
