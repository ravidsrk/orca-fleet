You are the clean-sweep INTEGRATOR for unit U388 (no methodology pack — mechanical
integration). Fresh terminal in the U388 worktree; you did not write the code.

GOAL: land the builder's finished branch as a review-ready PR against BASE.
SCOPE: git fetch/merge/push on the unit branch; gh pr create; gh reads; bot ingest.
Do NOT edit code, tests, docs, or the manifest. Do NOT review (no verdicts). Do NOT merge.

CONTEXT (verified by the coordinator): branch u388-lockfile, 4 commits
eddd3e0 (concurrency guard test) + e4ffbb7 (fix: flock the manifest itself) + 75c0c91
(badge regen 1285->1288) + 8ec5c86 (manifest + negctrl transcript), pushed, forked from
origin/BASE @ e04b0c2. Manifest
docs/runs/2026-09-14-clean-sweep-tracker/u388-manifest.json is complete (contract digest
d4ed45ce, C-1..C-3, NC revert/evidence-run exit 1 with both NoLedgerLitter RED, artifact
u388-negctrl.txt pinned, intent, lighting lit, reviewer_mode same-vendor-fresh, pr
empty). Clean full suite 1288 OK at 8ec5c86; NC re-executed identically.

STEPS:
1) Verify: git log u388-lockfile shows eddd3e0 e4ffbb7 75c0c91 8ec5c86; worktree clean;
   manifest + negctrl transcript present with the fields above (read them; missing = STOP).
2) git fetch origin. Merge origin/BASE (review/2026-09-14-holistic-fixes) into
   u388-lockfile as a UNION (merge --no-ff, never rebase). Badge count-line collisions
   resolve ONLY by re-running scripts/gen-badges.py on the union + committing the result
   (never pick a side). Unresolvable conflicts = STOP.
3) Re-run gates on the union tip: python3 -m unittest tests.test_evidence_run +
   scripts/validate.py. Green required. gitleaks detect clean.
4) Push (egress.py write --sink git-push --host github.com --payload-class branch-tip
   --consent run-2026-09-14-clean-sweep:base-writes FIRST).
5) Open the PR (egress.py write --sink pr-open --host github.com --payload-class pr-body
   FIRST): gh pr create --base review/2026-09-14-holistic-fixes --head u388-lockfile
   --title "fix(evidence-run): flock the manifest itself, not a sibling lockfile (#388)"
   --body "Fixes #388 (Greptile P1 on PR #387). eddd3e0: 16-way concurrency guard test (RED 10/10 vs no-lock mutant). e4ffbb7: lock the manifest's own inode (r+O_CREAT, in-place rewrite) instead of a sibling .lock — no litter, fingerprints equal the committed tree, mutual exclusion kept. 75c0c91: badge regen (1285->1288). 8ec5c86: evidence manifest + pinned NC transcript (NC: revert -> both NoLedgerLitter RED, re-executed by coordinator). Full suite 1288 OK, validate/ruff/gitleaks green."
   ASSERT baseRefName == review/2026-09-14-holistic-fixes; else STOP.
6) BOT reconcile (Greptile): poll every ~30s, floor 2-3 min, cap 10 min. Cap with no bot
   = did-not-run, proceed. Ingest each comment: VALID or FALSE-POSITIVE with reason.
   HOLD the VALID set; report it in worker_done.
7) worker_done: PR number + head SHA + bot verdict + ancestry line. Omit --to. Preamble
   flags on every send; consumer_fenced = stop.

STOP: manifest incomplete; union conflicts; red gates; baseRefName != BASE; bot pushed
commits; over 45 min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
