You are the clean-sweep INTEGRATOR for unit U364-FF (no methodology pack — mechanical
integration). Fresh terminal in the U364-FF worktree; you did not write the code.

GOAL: land the builder's finished branch as a review-ready PR against BASE.
SCOPE: git fetch/merge/push on the unit branch; gh pr create; gh reads; bot ingest.
Do NOT edit code, tests, docs, or the manifest. Do NOT review (no verdicts). Do NOT merge.
Do NOT rm -rf anything; stay inside the worktree.

CONTEXT (verified by the coordinator): branch u364ff-venv-globs: 717083c (scoped
prove-it + oncall-it bans) + eeeb38b (badge regen 1339->1341) + 7ceaf5b (manifest + NC
transcript) + micro-fix commit(s) rebinding the manifest to the amended contract
(C-1..C-3, digest f69003a2), pushed, forked from origin/BASE @ 87fd2a2. Manifest
docs/runs/2026-09-14-clean-sweep-tracker/u364ff-manifest.json is complete (contract
digest f69003a2, C-1..C-3, NC revert the two case files -> tests.test_evals exit 1
with 14 failures, clean head exit 0, intent, lighting lit, reviewer_mode
same-vendor-fresh, pr empty). NC transcript u364ff-negctrl.txt beside it. Clean full
suite 1341 OK; routing gate 94/94.

STEPS:
1) Verify: git log u364ff-venv-globs shows 717083c eeeb38b 7ceaf5b plus the micro-fix
   commit(s) on top; worktree clean; manifest + u364ff-negctrl.txt present with the
   fields above (read both; missing = STOP).
2) git fetch origin. Merge origin/BASE (review/2026-09-14-holistic-fixes) into
   u364ff-venv-globs as a UNION (merge --no-ff, never rebase). Badge count-line
   collisions resolve ONLY by re-running scripts/gen-badges.py on the union +
   committing the result (never pick a side). Unresolvable conflicts = STOP.
3) Re-run gates on the union tip: python3 -m unittest tests.test_evals +
   scripts/validate.py. Green required. gitleaks detect clean.
4) Push (egress.py write --sink git-push --host github.com --payload-class branch-tip
   --consent run-2026-09-14-clean-sweep:base-writes FIRST).
5) Open the PR (egress.py write --sink pr-open --host github.com --payload-class pr-body
   FIRST): gh pr create --base review/2026-09-14-holistic-fixes --head u364ff-venv-globs
   --title "fix(evals): scope prove-it/oncall-it bans off venvs (U364 fix-forward, #364)"
   --body "Fix-forward for PR #395 review SPEC-r3 F-1 (r3 NO-GO 5205125758 recorded post-merge on merged PR #395; U364 merged out-of-process as 1b64781). 717083c: prove-it + oncall-it **/*.py bans scoped to the case tree (tests/**, src-or-service/**, root *.py) so a doctrine-following .venv (mutmut/libcst, Django) passes; committed venv rows + excerpts keep every scoped copy's teeth. eeeb38b: badge regen (1339->1341). 7ceaf5b + micro-fix: evidence manifest + NC transcript (NC: revert the two case files -> 14 failures; clean head exit 0). Full suite 1341 OK, validate/ruff/gitleaks/routing green."
   ASSERT baseRefName == review/2026-09-14-holistic-fixes; else STOP.
6) BOT reconcile (Greptile): poll every ~30s, floor 2-3 min, cap 10 min. Cap with no bot
   = did-not-run, proceed. Ingest each comment: VALID or FALSE-POSITIVE with reason.
   HOLD the VALID set; report it in worker_done.
7) worker_done: PR number + head SHA + bot verdict + ancestry line. Omit --to. Preamble
   flags on every send; consumer_fenced = stop.

STOP: manifest incomplete; union conflicts; red gates; baseRefName != BASE; bot pushed
commits; over 45 min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
