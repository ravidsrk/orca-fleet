You are the clean-sweep FIX worker for unit U387W, review round 3 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387W worktree on branch ravidsrk/u387w-wipsection (must be at the
r2 tip 04b780f — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387w-wipsection` first and
verify the tip is 04b780f; refuse a dirty baseline).

VERDICT (round 2, NO-GO, reviewed 04b780f, review 5206786113): the R1 batch landed
and is mutant-witnessed, but Greptile P1 4012744258 reconciles to ONE Required
(the verdict reproduced BOTH a fail-CLOSED false refusal AND a fail-OPEN [] bind
on an incomplete duplicate wave=2 row) plus the surviving paragraph-gate mutants
(TEST R-1 = SPEC F-2; M7e equivalent, do not chase) and surviving case-fold /
word-boundary mutants (M8/M9). Everything else stands at its severity and does
NOT block: SPEC/TEST/ STANDARDS Nits outside the touched lines, accepted
optionals, FYIs. Do NOT post thread replies (the coordinator answers bot P2
4012319774 'fixed in d52ff42' + P1 4012744258 'fixed in <your r3 SHA>' at the
fix close — name your pushed tip clearly in worker_done).

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) Arm the setext rule only after a PLAIN paragraph: list-item/blockquote
   paragraphs and their continuations must NEVER end the section. Committed
   tests: list + ---, ordered-list + ---, blockquote + ---, and list + ===
   all keep binding complete rows; the fail-open shape ('- a note' then '---'
   before an incomplete duplicate wave=2 row inside the section) is refused
   naming wave 2 (not silently []).
2) Witness the paragraph-gate exclusions (kills M7a-d): --- after a table row,
   --- after a heading, --- after a closed fence each keep the section open
   (refused look-alikes stay refused); M7e is equivalent — do not chase it.
3) Look-alike subtests for the anchor: 'WIP-curve protocol rows' (plural) and
   lowercase 'wip-curve protocol row' must NOT open the section.
4) Fix the run_report.py:515 comment to say what actually arms the setext rule.
5) Correct the manifest's 'never bound' claim about the thematic-break shape
   (it binds [] in the fail-open repro — say what is true now).

SCOPE: runtime/scripts/run_report.py + tests/test_run_report.py + the unit
manifest + the negctrl transcript ONLY. Do not touch the prose (no drift: your
check change must keep matching what attention-budget.md:60 names — if the plain-
paragraph rule drifts from the prose, adjust the WORDING minimally and say so),
caps, graduation, other checks, or any other file. Badge regen only if YOUR new
tests move the count (same mechanical-commit rule). Never `git add -A`. The
non-batched Nits/Optionals/FYI are NOT in this batch; touch them only if your
Required fix cannot land without it, and say so in the commit message.

CONTRACT (unchanged): contract.source =
docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-387-wip-section.md@719d997be28476c382660f3f37d829e597130ce9.
contract.digest =
sha256:d7b4e72c070e589df86aca9d57fd667d1227ca9cd72414edbaa6bc6a9f2d317d.
criterion_ids = [C-1, C-2, C-3, C-4] (unchanged). NC-COMMAND unchanged: python3 -m
unittest tests.test_run_report.

STEPS:
1) Union first: merge origin/review/2026-09-14-holistic-fixes into the branch; if ONLY
   badge files conflict, re-regen + continue (mechanical); any other conflict = STOP.
2) Red FIRST: the item-1 binding cases + fail-open refusal + item-2 gate witnesses +
   item-3 look-alikes fail pre-fix (show all), pass post-fix.
3) Implement 1)+5) above, smallest change.
4) Recorder run of the nc-command + validate.py + FULL suite, all green. ruff on the
   touched modules. gitleaks detect clean.
5) Re-run the round-1+2 negative controls (record the revert RED transcript) at the
   new tip. Update the unit manifest
   (docs/runs/2026-09-14-clean-sweep-tracker/u387w-manifest.json): new head_sha (:=
   the CODE tip — option-A: a manifest cannot name the SHA of the commit containing
   it, so the manifest-commit tip is named in worker_done and the coordinator
   re-binds at close; see DECISIONS.md fix-step5-headsha / ruling msg_b92468884470 —
   this supersedes the r1/r2 specs' 'INCLUDING the manifest commit' line), new
   commands block (artifact null everywhere, never a /tmp path), extended NC
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
