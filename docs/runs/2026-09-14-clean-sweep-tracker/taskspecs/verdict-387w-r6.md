You are the clean-sweep VERDICT worker for unit U387W, review round 6 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387W worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #401 at HEAD 0fb838c (branch u387w-wipsection → BASE). Finding (#387
thread 4009895678): the run-report checker's WIP-curve validation bound
complete-looking wave= rows from anywhere in the report; the fix scopes collection
to the canonical WIP-curve section and names the rule in the protocol prose. C-1
rows only inside the canonical section (fences/deviations/other sections ignored);
C-2 per-wave completeness inside enforced; C-3 prose names the rule (≤160 lines);
C-4 suite + validate green. OUT: caps; graduation; other checks; park-class checks.
ROUND 6: this tip carries the R5 verdict batch (tab-stop helper, fence close,
mutant witnesses) — the axes below re-verify it.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 401, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status at 0fb838c: Greptile 5/5 clean in the PR body, no new inline
   findings (both tip-anchored comments predate the push — re-anchored old threads).
   All 4 threads (P2 4012319774 fixed in d52ff42; P1 4012744258 code fix ac9395d;
   P1 4013204408; P1 4013782318 FP with reasons) have ZERO replies — the in-thread
   answers are owed from the COORDINATOR lane pre-merge (conductor-side record item,
   NOT a builder fix; exclude with this reason). The STALE PR BODY (still describes
   r4/f8a0d87) is likewise a COORDINATOR-side record item: the coordinator refreshes
   it via gh pr edit at the fix close; exclude it from the builder batch with this
   reason, but keep it Required-conductor-side so it blocks the merge, not the verdict.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #401 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 0fb838c);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 0fb838c) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (0fb838c) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 0fb838c) + round 6 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 6 — worker_done bodies archived at delivery) ---

[SPEC R387W-r6]
I reviewed PR #401 at 0fb838c on the SPEC axis, writing my own expectation before opening the diff. All four R5-batch items landed and match the markdown-it-py 4.2.0 oracle: 92c4a8e (tab stops of 4 through one _indent helper, the '    ' literal gone; a fence ends with its list item), 91e7d29 (T5-2/3/4 witnesses), 861e5ab (M13g re-witness) and 0fb838c (manifest round 6, head_sha 861e5ab, re-bind owed). C-1 through C-4 are met: 83 unit tests OK, full suite 1378 OK in 255 s, validate.py and run_report.py exit 0, ruff clean, attention-budget.md 78 lines. There are no Critical or Required findings. Two findings are carried and disclosed: F6-2 Nit (the prose's 'text begins' vs the checker's word boundary, nnt[8]) and F6-3 FYI (indented-code and HTML-comment rows are still read, nnt[2]). F6-1 FYI is only partly disclosed: headings in a block quote or on a list-marker line do not end the section, and nnt[9] covers only the list-item column. F6-4 FYI: the base moved to 26e5ab0 (docs only), and the PR is still MERGEABLE/CLEAN. Greptile is confirmed 5/5 at 0fb838c with no new inline findings; its two comments anchored at 0fb838c are old threads from 05:41Z and 08:53Z. Still owed from the coordinator lane before merge: the PR body is stale at r4 (f8a0d87, 81/1376 tests, 35 controls), and all four threads (4012319774, 4012744258, 4013204408, 4013782318) have zero replies, although GitHub shows them resolved. I committed nothing: HEAD is 0fb838c, the tree is clean, the tip commit (16:15) predates this session (16:21), and I posted nothing to GitHub.

[TEST-ADEQUACY R387W-r6]
I re-ran the TEST-ADEQUACY axis on PR 401 at 0fb838c, and the R5 batch has landed. The 83 tests pass. My reverts reproduce the manifest: NC-1 44, NC-14 4, NC-2 1, and M15a-c, MT2-4 and M13g are all killed. The heading-less fixture really reads its heading from attention-budget.md:60, no tautologies found. REQUIRED R-1 (conf 0.8): in run_report.py:520 'if line.strip() and indent < col', dropping 'line.strip()' still passes all 83 tests but fails open. A wave-2 row inside a list item's fence after a blank line then binds [] where HEAD refuses it, and markdown-it-py 4.2.0 agrees with HEAD. NIT N-1: the same rule is witnessed only at the margin (the margin-only and col-1 mutants survive, with a false-pass witness). OPTIONAL O-1: the 'yield raw' claim is untested. Still owed by the coordinator lane before merge: the stale PR body (r4, 81 tests, 1376) and replies on all 4 Greptile threads (4012319774, 4012744258, 4013204408, 4013782318), which have 0 replies. There are no new inline findings, Greptile gives 5/5 at 0fb838c and the gates pass. Nothing committed by this session: HEAD is still 0fb838c, its reflog ends at 16:15, before I started, and the /tmp clone is deleted.

[STANDARDS R387W-r6]
Reviewed PR #401 at 0fb838c on the STANDARDS axis after writing my pre-diff expectation (location and shape matched: the run_report.py section scoper plus the attention-budget.md:60 sentence). I verified every R5 batch item landed within the spec's file scope: 92c4a8e (the _indent tab-stop-4 helper at :498 used at :514/:547/:575, which folds in F-3, and the F-2 fence ending with its item at :520), 91e7d29 (T5-2/3/4), 861e5ab (M13g) and 0fb838c (manifest: head_sha 861e5ab, tree 6e897416, artifacts null, 49 distinct controls). Gates re-run here: 83 OK, full suite 1378 OK, validate exit 0, ruff clean. Greptile is 5/5 at 0fb838c with no new inline findings (both tip-anchored comments, 4012319774 and 4013782318, predate the push). Findings: 0 Critical/Required. S6-1 Nit: the _indent docstring claims tab-stop measurement but the helper counts spaces only (probe: tab gives 0 raw, 4 expanded), so the tab rule still lives caller-side at :513. S6-2 Nit: test duplication grew (partial_2 fixture x8, the refused-wave-2 assertion triple x5, +1 each at tests:636-645). S6-3 Optional: three bare 4s. FYIs: the accepted Long Function Optional +7 lines, and unscoped 'verdict rN' comment citations. Still owed coordinator-side before merge: the PR body is two rounds stale (still f8a0d87 / 81 / 1376), and all 4 Greptile threads are isResolved=true with ZERO replies. I made no commits (HEAD 0fb838c unchanged, tree clean; git log shows only the coordinator's ec2d4cf and 26e5ab0 ledger commits on the review branch) and posted nothing to GitHub.
