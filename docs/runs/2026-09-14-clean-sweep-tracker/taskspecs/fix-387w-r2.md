You are the clean-sweep FIX worker for unit U387W, review round 2 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387W worktree on branch ravidsrk/u387w-wipsection (must be at the
union tip d94c6c1 — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387w-wipsection` first and
verify the tip is d94c6c1; refuse a dirty baseline).

VERDICT (round 1, NO-GO, reviewed d94c6c1, review 5206177974): C-2/C-3 met, but four
Required items are open (two axis findings + one held bot + one adjacent verdict find),
each reproduced. Everything else stands at its severity and does NOT block: S4 is a
conductor-side record item; S1/S3/M2/M15/Optionals are accepted non-blocking; FYIs
stand. Do NOT post thread replies (the coordinator answers bot P2 4012319774 at the
fix close).

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) Anchor _WIP_SECTION_RE (run_report.py:482) to the canonical 'WIP-curve protocol
   row' heading so look-alike sections no longer bind (F-1=R1). Thread real-report
   variance deliberately: migrate the 13 '## WIP curve' fixtures ONLY where they
   encode the old breadth (each migration justified in the commit message), and add
   refused look-alike cases: a '## WIP-curve example (from another run)' section with
   complete rows and NO canonical section must refuse; a '## Deviations — WIP-curve
   cap raised' section must not bind.
2) Test the CommonMark fence-close clause (run_report.py:494-497) with mixed and
   shorter fences so R2's 'any fence line closes' replacement fails (R2).
3) Reject a backtick fence opener whose info string holds a backtick (bot P2
   4012319774): the '```text`example``' repro must not swallow a canonical row; add
   the repro as a committed test.
4) Close the adjacent setext-heading leak the verdict found: a 'Deviations' line +
   '---' underline AFTER the section must end the section (rows under it must not
   bind); add a test.
5) Align the prose (attention-budget.md:60) with the anchored check (F-2/S2 adjacent —
   your heading change moves the match; the prose must name exactly what the check
   matches, no drift either way). File stays ≤ 160 lines.

SCOPE: runtime/scripts/run_report.py + tests/test_run_report.py +
runtime/attention-budget.md (WIP-curve prose only) + the unit manifest + the negctrl
transcript ONLY. Do not touch caps, graduation, other checks, or any other file. Badge
regen only if YOUR new tests move the count (same mechanical-commit rule). Never `git
add -A`. The non-batched Nits/Optionals/FYI are NOT in this batch; touch them only if
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
2) Red FIRST: the look-alike refusals + fence-close tests + info-string repro + setext
   test fail pre-fix (show all), pass post-fix.
3) Implement 1)+5) above, smallest change.
4) Recorder run of the nc-command + validate.py + FULL suite, all green. ruff on the
   touched modules. gitleaks detect clean.
5) Re-run the round-1 negative controls (record the revert RED transcript) at the new
   tip. Update the unit manifest
   (docs/runs/2026-09-14-clean-sweep-tracker/u387w-manifest.json): new head_sha (:= the
   tip you push, INCLUDING the manifest commit — name the pushed tip, not its parent),
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
