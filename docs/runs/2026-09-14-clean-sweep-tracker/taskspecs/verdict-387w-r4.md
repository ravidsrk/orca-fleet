You are the clean-sweep VERDICT worker for unit U387W, review round 4 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387W worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #401 at HEAD f8a0d87 (branch u387w-wipsection → BASE). Finding (#387
thread 4009895678): the run-report checker's WIP-curve validation bound
complete-looking wave= rows from anywhere in the report; the fix scopes collection
to the canonical WIP-curve section and names the rule in the protocol prose. C-1
rows only inside the canonical section (fences/deviations/other sections ignored);
C-2 per-wave completeness inside enforced; C-3 prose names the rule (≤160 lines);
C-4 suite + validate green. OUT: caps; graduation; other checks; park-class checks.
ROUND 4: this tip carries the R3 verdict batch (content-column fix, mutant kills,
test-cited claims) — the axes below re-verify it.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 401, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status at f8a0d87: all three axes judge NEW P1 4013782318
   FALSE-POSITIVE as a defect (SPEC: truncation only from kept, 15/15 + 151,981-sweep
   clean; STANDARDS: no-op for indented breaks, 15 shapes + 168,416 fuzz agree; TEST:
   9/9 oracle agree) — reconcile with recorded reasons (TEST still Requires a witness
   test for the :551 line). All 4 threads (P2 4012319774 fixed in d52ff42; P1 4012744258
   code fix ac9395d; P1 4013204408; P1 4013782318 FP with reasons) have ZERO replies —
   the in-thread answers are owed from the COORDINATOR lane pre-merge
   (conductor-side record item, NOT a builder fix; exclude with this reason).
   NOTE: the STANDARDS axis did NOT re-run the full suite (disclosed); weigh as
   disclosed, not as a new Required (SPEC re-ran 1376 OK).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #401 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA f8a0d87);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA f8a0d87) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (f8a0d87) + reviewed_wtree (git rev-parse
   HEAD^{tree} at f8a0d87) + round 4 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 4 — worker_done bodies archived at delivery) ---

[SPEC R387W-r4]
I reviewed PR #401 at f8a0d87 (base review/2026-09-14-holistic-fixes) on the SPEC axis only, after writing my expectation first. All five round-4 items landed (de82be7 content-column fix, 19b638f D6/D7/C8/C10/D15 kills, 5accc45 badge 1376, 99b73ca M13h/m/n kills, f8a0d87 manifest with nnt[1] cited test by test). C-1 through C-4 are met: validate.py exits 0, and the full suite ran 1376 tests in 250.8s, OK. attention-budget.md is 78 lines and names the section rule, and a drift test ties the prose, TEMPLATE.md and the checker together. There is no scope creep: the ARCHITECTURE and docs/missions activation-load bumps are gen-badges outputs of the C-3 sentence. FINDING S4-1, Nit, C-1 fail-open ('_wip_rows collects rows ONLY inside the canonical WIP-curve section ... other sections ignored'), at run_report.py:531 'base = item.end() + (gap if rest.strip() and 0 < gap <= 4 else 1)'. An empty list item followed by a blank line keeps its column open, but CommonMark lets an item begin with at most one blank line. So the lead '-' / blank / '  Deviations' / '---', after the section's note, binds [] on the rows under what markdown-it-py 4.2.0 (commonmark) parses as a setext heading 'Deviations'. The '*' / '===' variant does the same. This is the same class as r3 F-1, and it is the only divergence outside indented code in a 151,981-shape oracle sweep. Greptile P1 4013782318 ('List State Drops Early' @551 'items[kept:], para = opened, None') is a FALSE-POSITIVE. The assignment truncates only from kept, and kept already counts every item the break line is indented into, so a break inside an item keeps that item. The state drops only when the break sits left of the item's column, and there CommonMark also closes the list. All 15 of Greptile's shapes agree with the oracle, and the sweep has 0 divergences containing an indented break line. The other 5,906 sweep divergences are the pre-existing indented-code FYI, nnt[2]. What's left: all 4 Greptile threads (4012319774, 4012744258, 4013204408, 4013782318) have NO reply and are owed in-thread answers from the coordinator lane before merge, and S4-1 needs a decision (fix or record as noticed-not-touched). I committed nothing: HEAD is still f8a0d87, the tree is clean, and the only commits made after this session started (3d89b41, 7aeb8df) are coordinator run-log commits on review/2026-09-14-holistic-fixes. I made no GitHub posts.

[TEST-ADEQUACY R387W-r4]
I reviewed test adequacy at f8a0d87: every R3 batch item is in and covered by a test. Items 1-3 went RED on the pre-R4 checker d9f0a2a (15 failures), nnt[1] now cites tests by name and matches them, the D6/D7/C8/C10/D15 and M13h/m/n mutants die when I re-run them, NC-1 (37 failures) and NC-2 (1 failure) reproduce and restore to 81 OK, and the extended protocol fixture is not a tautology (it reads the heading from the prose and fails if either side drifts). Greptile P1 4013782318 is a FALSE-POSITIVE as a defect: on 9 shapes the checker agrees with a markdown-it-py CommonMark oracle 9/9, while a mutant of run_report.py:551 that drops the list items (the mechanism the P1 describes) diverges on 7 and survives all 81 tests, binding [] on an incomplete duplicate. That is R-1 (Required): no test covers that line. Two Nits: the 4-space marker-gap boundary at :531 has no test (MX11 survives, fails open) and rows before any heading have none (MX15 survives, :502). All 4 Greptile threads have no replies and are owed from the coordinator lane before merge; I made no commits (HEAD f8a0d87, tree clean, the 3 new ledger commits on review/2026-09-14-holistic-fixes are not mine), posted nothing to GitHub, and deleted the /tmp clones.

[STANDARDS R387W-r4]
I reviewed PR #401 at f8a0d87 (code tip 99b73ca, merge-base e97b824) on the STANDARDS axis, with my expectation written before opening the diff and all PR reads fenced. Every R3 batch item landed within the 5-file scope: items 1-3 in de82be7, D6/D7/C8/C10/D15 in 19b638f, M13h/m/n in 99b73ca, badges in 5accc45, and in f8a0d87 a manifest whose nnt[1] cites 7 tests that all resolve; I re-ran tests.test_run_report (81 OK), validate.py (green) and ruff (clean) but not the full suite. Greptile P1 4013782318 is FALSE-POSITIVE: at :551 'items[kept:], para = opened, None' is a no-op for a break indented into the item (kept == len(items), opened == []), and 15 targeted shapes plus a 168,416-shape fuzz agree with markdown-it-py CommonMark. S-1 Required: the PR body still states the rejected rule ('An ATX heading whose text begins WIP-curve / WIP curve (case- and whitespace-tolerant...)', 'Ran 69 tests'), a PR-body edit only. S-2 Required (cross-axis, SPEC C-2): an indented-code line arms a setext close (:554 'para = _QUOTED if quote else (base if line[base:].strip() else None)', then :535), so rows 1-2, then '    note' / '---', then an incomplete wave=2 binds [] at HEAD, while base e97b824 refuses it with 2 errors. That is a new fail-open, not the 'pre-existing indented-code FYI' nnt[2] and the builder describe. Also S-3 Optional (Long Function _wip_section_lines :524), S-4 Nit (the _QUOTED=float('inf') sentinel with a truncated comment, :493) and S-5 FYI (headings anchored at the margin :534, disclosed in nnt[9]). Still owed: none of the 4 Greptile threads (4012319774, 4012744258, 4013204408, 4013782318) has an in-thread reply; 3 were resolved without an answer, and all 4 need answers from the coordinator lane before merge. I committed nothing (HEAD f8a0d87, clean tree; git log shows no commit from this session) and made no GitHub posts.
