You are the clean-sweep FIX worker for unit U387W, review round 6 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387W worktree on branch ravidsrk/u387w-wipsection (must be at the
r5 tip fd12ce4 — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387w-wipsection` first and
verify the tip is fd12ce4; refuse a dirty baseline).

VERDICT (round 5, NO-GO, reviewed fd12ce4, review 5208471329): 1 Required open
(SPEC F-1 = TEST T5-1: the S-2 fix counts SPACES only, so tab-indented code
still arms a setext close), reproduced by the verdict worker against base
1cdb490 + markdown-it-py 4.2.0. Everything else stands at its severity and does
NOT block: STANDARDS F-2 (accepted Optional), F-4 (Nit outside the fix), A-1
and F-5 (FYI). The STALE PR BODY (still r4) and the 4 THREAD REPLIES are
COORDINATOR-side record items that block the MERGE, not this fix: the
coordinator refreshes the body and answers the threads at your fix close. Do
NOT touch the PR body. Do NOT post thread replies (name your pushed tip
clearly in worker_done).

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) Required (F-1 = T5-1): measure columns with CommonMark TAB STOPS OF 4 at
   all three sites (:506 indent, :535 gap, :562 startswith) THROUGH ONE
   shared helper (this folds in STANDARDS F-3 — the '    ' literal spelled
   three ways must become the one helper). Both tab shapes refused NAMING
   wave 2: (a) rows 1-2 / '\tnote' / '---' / incomplete wave=2; (b) the
   r5-only regression '*'/blank/'  \tnote'/'===' (must read the row r4
   read again). Committed tests for both, red-first, oracle-checked.
2) Adjacent (SPEC F-2 Nit, reproduced): the :511 fence opened in a list item
   never closes when its item ends ('- a note'/'  ```'/'  example'/blank/
   'Next paragraph.' + incomplete wave=2 binds [] at HEAD). Close it on a
   non-blank line left of the content column. Committed test, red-first.
3) Adjacent (TEST T5-2/3/4 Nits): witnesses killing the :562 threshold, the
   :538 empty-reset, and the :519 pop-vs-clear mutants — one subtest each,
   red-first.

SCOPE: runtime/scripts/run_report.py + tests/test_run_report.py + the unit
manifest + the negctrl transcript ONLY. Do not touch the prose (your check
changes must keep matching what attention-budget.md:60 names — if a rule change
drifts from the prose, adjust the WORDING minimally and say so), caps,
graduation, other checks, the PR body, or any other file. Badge regen only if
YOUR new tests move the count (same mechanical-commit rule). Never `git add -A`.
The non-batched Nits/Optionals/FYI are NOT in this batch; touch them only if
your Required fix cannot land without it, and say so in the commit message.

CONTRACT (unchanged): contract.source =
docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-387-wip-section.md@719d997be28476c382660f3f37d829e597130ce9.
contract.digest =
sha256:d7b4e72c070e589df86aca9d57fd667d1227ca9cd72414edbaa6bc6a9f2d317d.
criterion_ids = [C-1, C-2, C-3, C-4] (unchanged). NC-COMMAND unchanged: python3 -m
unittest tests.test_run_report.

STEPS:
1) Union first: merge origin/review/2026-09-14-holistic-fixes into the branch; if ONLY
   badge files conflict, re-regen + continue (mechanical); any other conflict = STOP.
2) Red FIRST: both tab shapes + the F-2 fence shape + all three mutant witnesses
   fail pre-fix (show all), pass post-fix. Oracle: markdown-it-py CommonMark for
   disputed shapes (match it, don't argue it).
3) Implement 1)+3) above, smallest change.
4) Recorder run of the nc-command + validate.py + FULL suite, all green. ruff on the
   touched modules. gitleaks detect clean. Capture the full-suite summary line
   (tee the log AND grep Ran/OK).
5) Re-run the round-1+2+3+4+5 negative controls (record the revert RED transcript)
   at the new tip. Update the unit manifest
   (docs/runs/2026-09-14-clean-sweep-tracker/u387w-manifest.json): new head_sha (:=
   the CODE tip — option-A: a manifest cannot name the SHA of the commit containing
   it, so the manifest-commit tip is named in worker_done and the coordinator
   re-binds at close; see DECISIONS.md fix-step5-headsha / ruling msg_b92468884470),
   new commands block (artifact null everywhere, never a /tmp path), extended NC
   transcript, same contract/criteria/intent/lighting. Commit fix + manifest
   (bisectable, maintainer author, no trailers, named staging, receipt-style
   messages).
6) Push the BARE branch (egress.py write --sink git-push --host github.com
   --payload-class branch-tip --consent run-2026-09-14-clean-sweep:base-writes FIRST):
   `git push origin ravidsrk/u387w-wipsection:u387w-wipsection`. PR #401 exists — do
   NOT open another; your push updates it. No merge, no rebase past step 1. After your
   push Greptile re-reviews: report any NEW findings in worker_done, do not chase them
   (they need a new spec).
7) worker_done with new head SHA + gates + NC transcript. Omit --to. Preamble flags on
   every send; consumer_fenced = stop. STOP: unexplained red; out-of-scope rot; over 60
   min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
