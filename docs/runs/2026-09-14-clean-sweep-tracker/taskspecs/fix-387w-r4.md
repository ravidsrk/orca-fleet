You are the clean-sweep FIX worker for unit U387W, review round 4 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387W worktree on branch ravidsrk/u387w-wipsection (must be at the
r3 tip 3ce5825 — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387w-wipsection` first and
verify the tip is 3ce5825; refuse a dirty baseline).

VERDICT (round 3, NO-GO, reviewed 3ce5825, review 5207297740): the R2 batch landed
and is witnessed, but 4 Required items are open (SPEC F-1/F-2/F-3, STANDARDS S-1 =
TEST's two), each reproduced by the verdict worker against a markdown-it-py
CommonMark oracle. Everything else stands at its severity and does NOT block:
SPEC F-4 (disclosed at noticed_not_touched[8]; more prose would cost the
197-token headroom), STANDARDS Nits/Optional/FYI, the pre-existing indented-code
FYI, the TEST suite gap (weighed as disclosed — SPEC re-ran 1371 OK). Do NOT post
thread replies (the coordinator answers all three threads at the fix close —
name your pushed tip clearly in worker_done).

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) Ordinal setext fail-open (SPEC F-2 = Greptile 4013204408 half 1, C-1):
   _CONTAINER_RE at run_report.py:491 takes any ordinal, so 'Deviations / 2. x /
   ---' (a CommonMark setext H2) keeps the section open and rows under it bind.
   Only genuine containers keep the section open across '---'; the setext-H2
   shape must close it. Committed test with the 'Text / 2. x / ---' repro.
2) Indented-paragraph fail-open AND false refusal (SPEC F-1 = Greptile half 2 =
   TEST, C-2): at :524-526 a list item's indented paragraph after a blank reads
   as plain, so with complete rows '---' falsely refuses, while with an
   incomplete duplicate wave=2 after its '---' the report binds []. Both
   directions must be right: thematic break after a true container never closes;
   the incomplete-duplicate shape is refused NAMING the wave, never silent [].
   Committed tests for both directions.
3) Nested-fence bind (SPEC F-3, C-1): _FENCE_RE ' {0,3}' at :488 misses a fence
   nested in a list item at 4+ spaces, so fenced example rows bind — the
   original #387 bug through a container, currently undisclosed. Fences at any
   nesting depth must hide their rows. Committed test with a 4+-space nested
   fence holding a canonical-looking wave= row.
4) Correct noticed_not_touched[1] again: 'fails closed ... none bind' is false
   (same class as the 'never bound' error it replaced — the THIRD claim about
   this shape). This time, state ONLY what the committed tests prove about each
   shape (cite each test by name); no untested generality about open/closed.
5) Adjacent Nits: kill surviving mutants D6 (bullets '+' '*'), D7 (ordered ')'),
   C8/C10 (empty '##', 7+ '#' headings), D15 (setext underline indented 4+) —
   one subtest each, red-first.

SCOPE: runtime/scripts/run_report.py + tests/test_run_report.py + the unit
manifest + the negctrl transcript ONLY. Do not touch the prose (your check
changes must keep matching what attention-budget.md:60 names — if a rule change
drifts from the prose, adjust the WORDING minimally and say so), caps,
graduation, other checks, or any other file. Badge regen only if YOUR new tests
move the count (same mechanical-commit rule). Never `git add -A`. The
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
2) Red FIRST: every item-1/2/3 repro + every item-5 mutant subtest fails pre-fix
   (show all), passes post-fix. Oracle: markdown-it-py CommonMark for the
   disputed shapes (the verdict used it; match it, don't argue it).
3) Implement 1)+5) above, smallest change.
4) Recorder run of the nc-command + validate.py + FULL suite, all green. ruff on the
   touched modules. gitleaks detect clean. Capture the full-suite summary line
   (the r3 TEST axis lost it — do not repeat: tee the log AND grep Ran/OK).
5) Re-run the round-1+2+3 negative controls (record the revert RED transcript) at
   the new tip. Update the unit manifest
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
