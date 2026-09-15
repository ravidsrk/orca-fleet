You are the clean-sweep VERDICT worker for unit U387W, review round 3 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387W worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #401 at HEAD 3ce5825 (branch u387w-wipsection → BASE). Finding (#387
thread 4009895678): the run-report checker's WIP-curve validation bound
complete-looking wave= rows from anywhere in the report; the fix scopes collection
to the canonical WIP-curve section and names the rule in the protocol prose. C-1
rows only inside the canonical section (fences/deviations/other sections ignored);
C-2 per-wave completeness inside enforced; C-3 prose names the rule (≤160 lines);
C-4 suite + validate green. OUT: caps; graduation; other checks; park-class checks.
ROUND 3: this tip carries the R2 verdict batch (plain-para setext arming,
gate witnesses, look-alikes, note correction) — the axes below re-verify it.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 401, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status at 3ce5825: P2 thread 4012319774 (backtick info-string, FIXED
   in d52ff42) has ZERO replies; P1 thread 4012744258 (thematic-break, code fix
   ac9395d — 3ce5825 is manifest-only, do NOT cite it as the fix) has ZERO replies;
   NEW P1 thread 4013204408 (container boundaries @run_report.py:491) is open and
   judged VALID on both halves by all three axes. The in-thread answers are owed
   from the COORDINATOR lane pre-merge (conductor-side record item, NOT a builder
   fix; exclude with this reason — the coordinator posts them before merging).
   NOTE: the TEST axis did NOT verify the full suite (capture lost the summary
   line — disclosed); SPEC re-ran 1371 OK itself, so suite coverage stands via
   SPEC. Weigh the TEST gap as disclosed, not as a new Required.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #401 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 3ce5825);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 3ce5825) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (3ce5825) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 3ce5825) + round 3 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (round 3 — worker_done bodies as delivered; the orca message
store was purged before re-extraction, so these are transcribed from the
delivered batch; TEST prefix cross-checked against its surviving transcript) ---

[SPEC R387W-r3]
SPEC-axis review of PR #401 at 3ce5825 (fenced gh reads, CommonMark oracle markdown-it-py, own expectation written first): the R2 batch landed (ac9395d, fb6308d, 5cde1f1, 3ce5825; d52ff42 ancestor), C-3 holds (attention-budget.md 78 lines), C-4 green (validate exit 0, ruff clean, full suite Ran 1371 OK exit 0), and scope is clean. Findings: F-1 Required C-2 fail-open at run_report.py:525-526 ('para = "plain"'): a list item's indented paragraph after a blank then column-0 '---' closes the section, so an incomplete duplicate wave=2 row after it is hidden and the report binds []; the round-3 manifest noticed_not_touched[1] calls this shape 'fails closed', which is false in the same way the corrected 'never bound' claim was. F-2 Required C-1 fail-open at :491 (_CONTAINER_RE accepts any ordinal): 'Text / 2. x / ---' is a setext H2, yet the rows under it bind. F-3 Required C-1 NEW at :488 (_FENCE_RE ' {0,3}'): a fenced example nested at 4 or more spaces in a list item binds as evidence, which is the original #387 bug through a container and is not disclosed. F-4 Nit: the prose says 'text begins' while the check uses a word boundary. Greptile P1 4013204408 is VALID: both halves reproduce (half 1 = F-2, half 2 = F-1, fail-closed B1 and fail-open B2). Still owed: NO thread replies exist on PR #401. Pre-merge replies are owed on 4012319774 (fixed in d52ff42), on 4012744258 (the code fix is ac9395d, while 3ce5825 is only the manifest correction, so a reply citing 3ce5825 alone names the wrong commit), and on 4013204408. I committed nothing: HEAD is still 3ce5825 and the tree is clean, and the 4 new commits in the shared .git are on review/2026-09-14-holistic-fixes, not this branch. I made no GitHub posts.

[TEST-ADEQUACY R387W-r3]
DID: wrote my expectation first, read the fenced PR #401 diff and threads, the manifest and the negctrl transcript at 3ce5825, and confirmed the batch landed (ac9395d checker+test, fb6308d tests, 5cde1f1 badges only, 3ce5825 manifest+negctrl only). Also ran 36 mutants in a /tmp clone: baseline 76 OK, every builder NC count reproduced exactly (NC-1 23, NC-2 1, NC-4 3, NC-6 7, NC-7a/b/c 1 each, NC-8 1, NC-9 1, NC-10 7, NC-11 2, NC-7e equivalent), 30 killed, no tautologies, and the extended heading-less protocol fixture reads its heading from the prose and dies under NC-2. FOUND: Greptile P1 4013204408 is VALID on both shapes per a markdown-it CommonMark oracle: 'Text / 2. item / ---' is a setext heading that the checker keeps open, so a wave=2 row under it binds (errors [], fail-open against the PR's own claim), and '- a / blank / indented para / ---' is a thematic break that the checker closes on, giving a false 'none found'; with an incomplete duplicate wave=2 after the break it binds [], so the manifest's round-3 correction (noticed_not_touched[1]: 'fails closed ... none bind') is itself false. That gives Required x2: no test puts a container under plain text or an indented list paragraph after a blank (every lead follows the heading and a blank line), and that manifest claim. Nits: mutants D6 (bullets '+' '*') and D7 (ordered ')'), C8/C10 (empty '##' and 7+ '#' headings) and D15 (setext underline indented 4+) survive at 76 OK. LEFT: no thread replies exist on 4012319774, 4012744258 or 4013204408 — owed from the coordinator lane: P2 fixed in d52ff42, P1 4012744258 fixed in ac9395d (witnesses fb6308d; 3ce5825 is only the tip carrying it), 4013204408 is unanswered. validate.py passes, exit 0. I did NOT verify the full suite, because my capture lost unittest's summary line. The /tmp clone is deleted and the worktree is still clean at 3ce5825; git log shows no commit from this session, and I made no GitHub posts.

[STANDARDS R387W-r3]
I verified that the R3 batch landed at 3ce5825 (ac9395d container and continuation setext arming with the wave-2 fail-open refusal, fb6308d M7a-d and M8/M9 witnesses, 5cde1f1 badges, 3ce5825 manifest correction), re-ran tests.test_run_report (76 OK), validate.py (green) and ruff (clean), and reviewed the STANDARDS axis: 1 Required, 7 Nit, 1 Optional, 3 FYI. S-1 Required: the new noticed_not_touched[1] claim (manifest:250, 'That fails closed: rows after it are refused, and none bind') is false, the same class as the 'never bound' error it replaced, because complete rows plus the list-item, blank, indented-paragraph, --- lead plus an incomplete wave=2 row binds []. Greptile P1 4013204408 is VALID on both halves, confirmed with markdown-it-py commonmark and a checker repro: 'Text / 2. a / ---' and '10)' are setext headings but BIND [] (fail-open), and the list-item indented continuation after a blank binds [] with --- or ===. What's left: all three PR threads have zero replies and are owed pre-merge from the coordinator lane (P2 4012319774 fixed in d52ff42, P1 4012744258 fixed in ac9395d with 3ce5825 as the manifest tip, and new P1 4013204408 unanswered); I committed nothing (HEAD 3ce5825 unchanged, clean tree, no commit carries this session) and posted nothing to GitHub.
