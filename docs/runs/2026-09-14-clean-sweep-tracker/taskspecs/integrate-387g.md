INTEGRATOR U387G — land the builder's finished branch as a review-ready PR.
Instantiated from integrate-template.md. Fresh terminal in the UNIT's worktree
(/Users/ravindra/orca/workspaces/orca-fleet/u387g-evalglobs, branch
ravidsrk/u387g-evalglobs). Methodology: none (mechanical integration) — no
pack. rw by lane (posts to GitHub); commits NOTHING except a BASE-merge union
when needed.

UNIT: U387G (#387 threads 4011878433, 4011878440, 4011297664). BRANCH (local):
ravidsrk/u387g-evalglobs. PUSH NAME (bare): u387g-evalglobs — push the bare
branch; the ravidsrk/-prefixed worktree branch stays local (U388 precedent):
`git push origin ravidsrk/u387g-evalglobs:u387g-evalglobs` (egress FIRST).
PR-TITLE: "fix(evals): central dependency-dir exclusion, fail closed on empty
globs (#387)". MANIFEST:
docs/runs/2026-09-14-clean-sweep-tracker/u387g-manifest.json. NC-COMMAND:
`python3 -m unittest tests.test_evals`.
BUILDER TIP: 191d248 (manifest commit); CODE TIP 0a3f4ab (head_sha, option A).
BASE: review/2026-09-14-holistic-fixes (moved since the fork — union WILL be
needed; expect ledger-only, conflict-free).

GOAL: land the builder's branch as a review-ready PR against BASE.
SCOPE: git fetch/merge/push on the unit branch; gh pr create; gh reads; bot
ingest. Do NOT edit code, tests, docs, or the manifest. Do NOT review (no
verdicts). Do NOT merge.

STEPS:
1) Verify: git log shows 8750a76 (C-1 red tests), 8e77c3b (C-1 fix), 7e2e7f7
   (C-2 tests), 519da9c (C-2 fix), a2562bc (badge), 0a3f4ab (M4-survivor test
   hardening), 191d248 (manifest) on ravidsrk/u387g-evalglobs; worktree clean;
   the manifest exists with commands green + NC + intent (read it; a missing
   piece is a STOP, not a fix-it-yourself).
2) git fetch origin. Merge origin/BASE into the branch as a UNION preserving
   both intents (merge --no-ff, never rebase — the branch's history is
   evidence). Conflicts you cannot resolve as a clean union = STOP (escalate).
3) Re-run gates on the union tip: the NC-COMMAND + scripts/validate.py. Green
   required. gitleaks detect clean.
4) Push the BARE branch name (egress.py write --sink git-push --host
   github.com --payload-class branch-tip --consent
   run-2026-09-14-clean-sweep:base-writes FIRST).
5) Open the PR (egress.py write --sink pr-open --host github.com
   --payload-class pr-body --consent run-2026-09-14-clean-sweep:tracker-writes
   FIRST): gh pr create --base review/2026-09-14-holistic-fixes --head
   u387g-evalglobs --title "PR-TITLE" --body <short receipt: finding,
   commits, tests, NC result>. ASSERT baseRefName ==
   review/2026-09-14-holistic-fixes from the create output; anything else is a
   STOP.
6) BOT reconcile (Greptile): poll gh pr checks + review comments every ~30s,
   floor 2-3 min, cap 10 min. Cap elapsed with no bot = log did-not-run,
   proceed. Ingest each bot comment: VALID or FALSE-POSITIVE with a recorded
   reason. HOLD the VALID set (do not change code); report it in worker_done
   for batching with the internal review.
7) worker_done: PR number + head SHA + bot verdict (did-not-run | none | held
   VALID list) + merge-base ancestry line. Omit --to. Preamble --from +
   --dispatch-capability on every send; consumer_fenced = stop, no worker_done.

STOP: manifest incomplete; union conflicts; red gates; baseRefName != BASE;
bot pushed commits (autofix — report, do not normalize); over 45 min.
ESCALATION: blocking ask. No sub-dispatch. Worktree comment current.
