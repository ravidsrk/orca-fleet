You are the clean-sweep VERDICT worker for unit U387W, review round 7 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387W worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #401 at HEAD 0d55f10 (branch u387w-wipsection → BASE). Finding (#387
thread 4009895678): the run-report checker's WIP-curve validation bound
complete-looking wave= rows from anywhere in the report; the fix scopes collection
to the canonical WIP-curve section and names the rule in the protocol prose. C-1
rows only inside the canonical section (fences/deviations/other sections ignored);
C-2 per-wave completeness inside enforced; C-3 prose names the rule (≤160 lines);
C-4 suite + validate green. OUT: caps; graduation; other checks; park-class checks.
ROUND 7: this tip carries the R6 verdict batch (R-1/N-1 witnesses, docstring,
prose, nnt[9]) — the axes below re-verify it.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 401, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status at 0d55f10: Greptile 5/5 clean in the PR body (last reviewed
   commit 0d55f10, checks SUCCESS), no new inline findings (both tip-anchored comments
   predate the push — re-anchored old threads). All 4 threads (P2 4012319774 fixed in
   d52ff42; P1 4012744258 code fix ac9395d; P1 4013204408; P1 4013782318 FP with
   reasons) have ZERO replies — the in-thread answers are owed from the COORDINATOR
   lane pre-merge (conductor-side record item, NOT a builder fix; exclude with this
   reason). The STALE PR BODY (still describes r4/f8a0d87) is likewise a
   COORDINATOR-side record item: the coordinator refreshes it via gh pr edit at the
   fix close; exclude it from the builder batch with this reason, but keep it
   Required-conductor-side so it blocks the merge, not the verdict.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #401 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 0d55f10);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 0d55f10) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (0d55f10) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 0d55f10) + round 7 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 7 — worker_done bodies archived at delivery) ---

[SPEC R387W-r7]
I reviewed PR #401 at 0d55f10 on the SPEC axis only, writing my expectation before opening the diff and reading every PR surface through guard_text. The R6 batch landed in full: R-1 and N-1 witness subtests (6c23677, literal expected values, not tautological), the S6-1 docstring and F6-2 whole-words prose (47d5867), nnt[9] extended plus MR1/MN1a/MN1b in the manifest (0d55f10). C-1..C-4 are met: I re-ran 1378 tests OK rc=0, validate.py rc=0, ruff clean, and attention-budget.md is 78 lines. Greptile is 5/5 with last reviewed commit 0d55f10, check SUCCESS at 11:29Z after the 11:27Z commit, and no new inline findings; the 2 comments anchored at 0d55f10 (4012319774, 4013782318) predate the push. Findings are FYIs only: container-nested headings don't end the section (already parked as nnt[9]); two same-named sections are both read; the activation-load and badge changes are generated, not scope creep, but they leave clean-sweep ~200 tokens under the 34,000 cap. Still owed from the coordinator lane before merge: replies on all 4 Greptile threads (4012319774, 4012744258, 4013204408, 4013782318, zero replies today) and a PR body update, since it is stale at the fd12ce4/0fb838c narrative. I committed nothing and posted nothing to GitHub: HEAD is unchanged at 0d55f10, and the 4 commits made during this session (0b54b1e, 17ca535, 81a4599, 93022d8) sit only on review/2026-09-14-holistic-fixes, i.e. the coordinator lane.

[TEST-ADEQUACY R387W-r7]
I checked that the R6 batch landed at 0d55f10: R-1/N-1 subtests in 6c23677, S6-1 docstring and F6-2 prose in 47d5867, nnt[9] and the manifest in 0d55f10. The builder's transcript reproduces exactly on a deleted scratch clone: 83 OK, NC-2 1 failure, MR1 2, MN1a 1, MN1b 1; my NC-1 at the base checker gives 46 failures, markdown-it-py 4.2.0 agrees with all three r7 shapes, and the extended protocol fixture takes its heading from the prose, not the checker. Findings: Nit T7-1, a deeper sub-heading keeping the section open survives all 83 tests (a false pass for a row under '### Deviations'); Optional T7-2, the new _FENCE_RE 0-3 space limit is unwitnessed; still owed from the coordinator lane before merge: the stale PR body (r4/81 tests) and replies on all 4 Greptile threads, none of which has one; Greptile is 5/5 at 0d55f10 with no new inline findings (the 2 comments anchored there are re-anchored old threads), and I made no commits: HEAD is 0d55f10, the tree is clean, and no commit carries this session.

[STANDARDS R387W-r7]
I reviewed the STANDARDS axis of PR #401 at pinned HEAD 0d55f10, with the expectation written before opening the diff: all five R6 batch items landed (R-1+N-1 witnesses in 6c23677, S6-1 docstring and F6-2 prose in 47d5867, nnt[9] F6-1 and MR1/MN1a/MN1b RED in 0d55f10); the new witnesses pass the tautology guard (an independent markdown-it-py 4.2.0 probe agrees with all three); tests.test_run_report ran 83 OK, validate.py exited 0 and ruff was clean (I did not re-run the full suite); and Greptile shows 5/5 in the body with the Greptile Review and gates checks passing, while both 0d55f10-anchored comments are old threads re-anchored (originals d94c6c1/f8a0d87), so there are no new inline findings. On this axis there are 0 Critical/Required: three-layer separation, instruction budget, no-invented-references and receipt-style commits all hold, and the findings are ST7-1 Nit (tests/test_run_report.py:665-669 repeats the :641-645 assertion triple exactly; fold it into the method's own dict-loop pattern, cheap, no badge change), ST7-2 Optional (test_a_fence_nested_in_a_list_item_hides_its_rows is now 64 lines, and 2 of its subtests assert a row IS read; subtests were chosen to avoid a badge commit) and ST7-3 FYI (the manifest cites the ':520 guard', but at its own head_sha 47d5867 the guard is at :521; that citation is relative to the verdict). Still owed coordinator-side before merge: the PR body is stale by three rounds (still f8a0d87 / 81 tests / 1376 / 35 controls) and the 4 Greptile threads 4012319774, 4012744258, 4013204408 and 4013782318 have zero replies; the base moved to 17ca535 (docs/runs only, no file overlap); I made no commits (HEAD 0d55f10, clean tree, reflog shows only builder commits) and no GitHub posts.
