You are the clean-sweep FIX worker for unit U387W, review round 7 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387W worktree on branch ravidsrk/u387w-wipsection (must be at the
r6 tip 0fb838c — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387w-wipsection` first and
verify the tip is 0fb838c; refuse a dirty baseline).

VERDICT (round 6, NO-GO, reviewed 0fb838c, review 5209112241): 1 Required open
(TEST R-1: the :520 `line.strip()` guard is unwitnessed), confirmed
independently by the verdict worker (dropping it passes all 83 but fails open).
Everything else stands at its severity and does NOT block: S6-2 (not cheap),
S6-3 and O-1 (accepted Optionals), the FYIs. The STALE PR BODY and the 4 THREAD
REPLIES are Required-CONDUCTOR-side and block the MERGE, not this fix: the
coordinator refreshes the body and answers the threads at your fix close. Do
NOT touch the PR body. Do NOT post thread replies (name your pushed tip
clearly in worker_done).

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) R-1 (Required): witness the :520 `line.strip()` guard — dropping it must
   fail. Failing-first witness test: a wave=2 row after a blank line inside
   a list item's fence is read ([1,2] where HEAD reads [1]);
   markdown-it-py 4.2.0 agrees with HEAD. Show the mutant RED pre-fix
   (drop `line.strip()`, the new test fails), GREEN post-fix. Record the
   mutant as a negative control in the manifest transcript.
2) N-1 (adjacent): the same witness in an OFF-MARGIN (indented) list item —
   the rule is currently witnessed only at the margin. Failing-first.
3) S6-1 (adjacent): fix the `_indent` docstring — it claims tab-stop
   measurement but the helper counts spaces only (the tab rule lives
   caller-side). Say what the helper actually does (and where the tab
   rule lives).
4) F6-2 (adjacent): reconcile prose 'text begins' (attention-budget.md:60)
   vs the checker's word boundary (run_report.py:480) — adjust the
   WORDING minimally (prose budget: file must stay ≤160 lines, now 78)
   and say so; the drift test must keep passing.
5) F6-1 (adjacent): extend nnt[9] to cover headings in block quotes and on
   list-marker lines (currently covers only the list-item column) — a
   manifest-notice extension, test-cited where a test exists, plainly
   marked as untested coverage where none does (no untested generality).

SCOPE: runtime/scripts/run_report.py + tests/test_run_report.py +
runtime/attention-budget.md (item 4 wording ONLY, ≤160 lines) + the unit
manifest + the negctrl transcript ONLY. Do not touch caps, graduation, other
checks, the PR body, or any other file. Badge regen only if YOUR new tests
move the count (same mechanical-commit rule). Never `git add -A`. The
non-batched Nits/Optionals/FYI are NOT in this batch; touch them only if
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
2) Red FIRST: the R-1 witness + N-1 off-margin witness fail pre-fix (show both),
   pass post-fix. Oracle: markdown-it-py CommonMark for disputed shapes (match
   it, don't argue it).
3) Implement 1)+5) above, smallest change.
4) Recorder run of the nc-command + validate.py + FULL suite, all green. ruff on the
   touched modules. gitleaks detect clean. Capture the full-suite summary line
   (tee the log AND grep Ran/OK).
5) Re-run the round-1+2+3+4+5+6 negative controls (record the revert RED
   transcript) at the new tip. Update the unit manifest
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
