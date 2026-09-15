You are the clean-sweep VERDICT worker for unit U387W, review round 5 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387W worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #401 at HEAD fd12ce4 (branch u387w-wipsection → BASE). Finding (#387
thread 4009895678): the run-report checker's WIP-curve validation bound
complete-looking wave= rows from anywhere in the report; the fix scopes collection
to the canonical WIP-curve section and names the rule in the protocol prose. C-1
rows only inside the canonical section (fences/deviations/other sections ignored);
C-2 per-wave completeness inside enforced; C-3 prose names the rule (≤160 lines);
C-4 suite + validate green. OUT: caps; graduation; other checks; park-class checks.
ROUND 5: this tip carries the R4 verdict batch (indented-code fix, :551 witness,
empty-item close, refreshed PR body) — the axes below re-verify it.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 401, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status at fd12ce4: Greptile 5/5 clean in the PR body, no new inline
   findings (both tip-anchored comments predate the push — re-anchored old threads).
   All 4 threads (P2 4012319774 fixed in d52ff42; P1 4012744258 code fix ac9395d;
   P1 4013204408; P1 4013782318 FP with reasons) have ZERO replies — the in-thread
   answers are owed from the COORDINATOR lane pre-merge (conductor-side record item,
   NOT a builder fix; exclude with this reason). The STALE PR BODY (still describes
   r4/f8a0d87 — both SPEC F-3 and STANDARDS F-1 name it) is likewise a COORDINATOR-side
   record item: the coordinator refreshes it via gh pr edit at the fix close (as was
   done for S-1 in r4); exclude it from the builder batch with this reason, but keep
   it Required-conductor-side so it blocks the merge, not the verdict.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #401 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA fd12ce4);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA fd12ce4) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (fd12ce4) + reviewed_wtree (git rev-parse
   HEAD^{tree} at fd12ce4) + round 5 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 5 — worker_done bodies archived at delivery) ---

[SPEC R387W-r5]
I reviewed PR #401 at fd12ce4 (base review/2026-09-14-holistic-fixes, merge-base 1cdb490) on the SPEC axis only: I wrote my expectation before opening the diff, fenced every PR read, and checked the targeted probes plus 2x60k fuzz shapes against markdown-it-py 4.2.0 (pure CommonMark for findings, GFM tables as a cross-check); every R4 batch item landed (06e49ae S-2/S4-1/S-4, ad1eea8 R-1/MX11/MX15, aef6a92 badges 1378, fd12ce4 manifest whose head_sha is aef6a92 under option A, so the conductor must re-bind to fd12ce4), round 5 touches only the 5 in-scope files, and C-1..C-4 are met: test_run_report ran 83 OK, validate.py exit 0, the full suite ran 1378 in 254s OK, and attention-budget.md is 78 lines and names the rule at :60, with the drift test at test_run_report.py:668 tying prose, TEMPLATE.md:80 and the checker together. I found F-1 Required (C-2 fail-open, S-2 fixed only for spaces): run_report.py:562 'base if line[base:].strip() and not line.startswith("    ", base) else None)' and :506 count spaces only, so rows 1-2 / '\tnote' / '---' / incomplete wave=2 BINDS [] at HEAD while base refuses with 2 errors (CommonMark treats '\tnote' as code_block), and '*'/blank/'  \tnote'/'===' is a new r5-only regression that hides a row r4 read; F-2 Nit (pre-existing, not in the batch): a fence opened in a list item never closes with its item (:507-511 'closer = _FENCE_RE.match(line, col)'), so '- a note'/'  ```'/'  example'/blank/'Next paragraph.' then an incomplete wave=2 BINDS [] while base refuses with 2 errors; F-3 Required record (coordinator lane): the live PR body still describes f8a0d87 ('**Tests** (r4 tip f8a0d87, code tip 99b73ca)', 'Ran 81', '1376', no r5 entry), though its Greptile block is intact (5/5, 'Last reviewed commit fd12ce4'); and FYI A-1: the mandated CommonMark oracle and GitHub's GFM disagree on a text line directly after a table row. Still owed: none of the 4 Greptile threads (4012319774, 4012744258, 4013204408, 4013782318) has a reply (all are resolved; 2 are outdated), so in-thread answers are due from the coordinator lane before merge; there is no new Greptile inline finding at fd12ce4 (the 2 comments anchored there were created 05:41Z and 08:53Z, before the 09:39:58Z commit, so they are re-anchored old threads); I committed nothing (HEAD fd12ce4, tree clean, and the only commits made since this session started, c97554a and 23dc6d4, are coordinator run-log commits) and made no GitHub posts.

[TEST-ADEQUACY R387W-r5]
At fd12ce4 I checked that every R4 item landed (S-2, S4-1, S-4 in 06e49ae; R-1, MX11, MX15 in ad1eea8; badges 1376->1378 in aef6a92; manifest in fd12ce4), re-ran tests.test_run_report (83 OK) and validate.py (exit 0), and in a throwaway git-archive copy (deleted afterwards) reproduced NC-1 (41 failures, exit 1), NC-2 (1 failure, exit 1) and M14a/M14b/M14d/MX11/MX15 with exactly the failure sets the transcript pins; all expectations are literal and non-tautological, and the heading-less fixture now reads its heading from the prose, cross-checked against TEMPLATE.md. Findings: T5-1 Required (medium confidence), the S-2 witnesses are all space-indented, and a tab-indented code line followed by --- still closes the section and at HEAD hides an incomplete duplicate wave=2 row (errs=[]), which is the R4 fail-open with a tab; T5-2/3/4 Nit, three of my own mutants on R5 lines survive all tests (3-space threshold at :562, the empty reset at :538, pop vs clear at :519), and each misparses a shape markdown-it's CommonMark parser checks; FYI, the live PR body still describes r4/f8a0d87 (81 tests, 1376), not fd12ce4, while the Greptile block is intact and 5/5 at fd12ce4. Still to do: all 4 Greptile threads (4012319774, 4012744258, 4013204408, 4013782318) have 0 replies and none is new at fd12ce4 (two are re-anchored old threads), so they are owed replies from the coordinator lane before merge; I did not re-run the full suite; no commit carries this session (c97554a and 23dc6d4 in the window are coordinator commits on the review branch, not in the PR head), and I made no GitHub posts.

[STANDARDS R387W-r5]
I reviewed PR #401 at fd12ce4 on the STANDARDS axis, writing my expectation before opening the diff and reading all PR data through guard_text.py; every R4 batch item landed (S-2, S4-1 and S-4 in 06e49ae, R-1/MX11/MX15 in ad1eea8, badges in aef6a92, manifest in fd12ce4, all cited refs resolve), and at fd12ce4 I re-ran tests.test_run_report (83 OK), validate.py (green), the full suite (Ran 1378 tests, OK) and ruff (clean), and I confirmed Greptile is 5/5 at fd12ce4 with no new inline findings (the 2 comments anchored there, 4012319774 and 4013782318, were created before fd12ce4 and are re-anchored old threads). F-1 Required (coordinator-side): S-1 did NOT hold — the live PR body still describes r4 ('Tests (r4 tip f8a0d87, code tip 99b73ca)', 'Ran 81 tests', 'Ran 1376 tests', '35 controls RED at 99b73ca', rounds end at r4) while its intact Greptile block says 83 tests at fd12ce4, so it needs a gh pr edit for r5; F-2 Optional is the carried Long Function in _wip_section_lines ('inside, fence, para, items, empty = ...' :504, one more state variable than at R4), F-3 Nit is the four-column rule spelled three ways (the '    ' literal at :562), F-4 Nit is WIP_SECTION :483 duplicating _WIP_SECTION_RE :484, and F-5 FYI is the disclosed nnt[2] (rows in indented code still bind; my probe returned []). Still owed before merge: all 4 Greptile threads (4012319774, 4012744258, 4013204408, 4013782318) are resolved with ZERO replies and need in-thread answers from the coordinator lane; I committed nothing (HEAD fd12ce4, clean tree, and the only commits since I started, 23dc6d4, 9d11eda and f327243, are coordinator run-log commits on review/2026-09-14-holistic-fixes) and posted nothing to GitHub.
