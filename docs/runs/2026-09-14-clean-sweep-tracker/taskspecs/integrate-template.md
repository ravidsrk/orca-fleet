INTEGRATOR template — instantiate per unit (UNIT/BRANCH/PR-TITLE/MANIFEST filled at
dispatch). Fresh terminal in the UNIT's worktree. Methodology: none (mechanical
integration) — no pack. rw by lane (posts to GitHub); commits NOTHING except a
BASE-merge union when needed.

GOAL: land the builder's finished branch as a review-ready PR against BASE.
SCOPE: git fetch/merge/push on the unit branch; gh pr create; gh reads; bot ingest.
Do NOT edit code, tests, docs, or the manifest. Do NOT review (no verdicts). Do NOT merge.

STEPS:
1) Verify: git log shows the builder's commits on BRANCH; worktree clean; the unit
   manifest exists on the branch with commands green + NC + intent (read it; a missing
   piece is a STOP, not a fix-it-yourself).
2) git fetch origin. Merge origin/BASE (review/2026-09-14-holistic-fixes) into BRANCH as a
   UNION preserving both intents (merge --no-ff, never rebase — the branch's history is
   evidence). Conflicts you cannot resolve as a clean union = STOP (escalate).
3) Re-run gates on the union tip: the unit's nc-command + scripts/validate.py. Green
   required. gitleaks detect clean.
4) Push (egress.py write --sink git-push --host github.com --payload-class branch-tip
   --consent run-2026-09-14-clean-sweep:base-writes FIRST).
5) Open the PR (egress.py write --sink pr-open --host github.com --payload-class pr-body
   --consent run-2026-09-14-clean-sweep:tracker-writes FIRST): gh pr create --base review/2026-09-14-holistic-fixes --head BRANCH --title
   "PR-TITLE" --body <short receipt: finding, commits, tests, NC result>. ASSERT
   baseRefName == review/2026-09-14-holistic-fixes from the create output; anything else
   is a STOP.
6) BOT reconcile (Greptile): poll gh pr checks + review comments every ~30s, floor 2-3
   min, cap 10 min. Cap elapsed with no bot = log did-not-run, proceed. Ingest each bot
   comment: VALID or FALSE-POSITIVE with a recorded reason. HOLD the VALID set (do not
   change code); report it in worker_done for batching with the internal review.
7) worker_done: PR number + head SHA + bot verdict (did-not-run | none | held VALID list)
   + merge-base ancestry line. Omit --to. Preamble --from + --dispatch-capability on
   every send; consumer_fenced = stop, no worker_done.

STOP: manifest incomplete; union conflicts; red gates; baseRefName != BASE; bot pushed
commits (autofix — report, do not normalize); over 45 min. ESCALATION: blocking ask.
No sub-dispatch. Worktree comment current.
