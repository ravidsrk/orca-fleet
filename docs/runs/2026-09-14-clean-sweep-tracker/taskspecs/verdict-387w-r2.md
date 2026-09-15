You are the clean-sweep VERDICT worker for unit U387W, review round 2 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387W worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #401 at HEAD 04b780f (branch u387w-wipsection → BASE). Finding (#387
thread 4009895678): the run-report checker's WIP-curve validation bound
complete-looking wave= rows from anywhere in the report; the fix scopes collection
to the canonical WIP-curve section and names the rule in the protocol prose. C-1
rows only inside the canonical section (fences/deviations/other sections ignored);
C-2 per-wave completeness inside enforced; C-3 prose names the rule (≤160 lines);
C-4 suite + validate green. OUT: caps; graduation; other checks; park-class checks.
ROUND 2: this tip carries the R1 verdict batch (anchor+fixtures, fence tests, P2
fix, setext rule) — the axes below re-verify it.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 401, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status at 04b780f: P2 thread 4012319774 (backtick info-string) was
   FIXED in d52ff42 but has ZERO in-thread replies (resolved without a reply — the
   'fixed in' answer is still owed); NEW P1 thread 4012744258 (thematic-break closes
   section @run_report.py:512, fail-closed false refusal) is open and silent — all
   three axes judge it VALID (severity differs: TEST Required, SPEC Nit, STANDARDS
   fail-closed VALID with its Required on the unanswered threads). Reconcile the
   severities with recorded reasons; same issue named twice is ONE fix.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #401 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 04b780f);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 04b780f) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (04b780f) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 04b780f) + round 2 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 2 — PASTED AT DISPATCH) ---

[SPEC R387W-r2]
I reviewed PR #401 on the SPEC axis at 04b780f (base review/2026-09-14-holistic-fixes, merge-base 5a853b2): all 8 R1 SHAs are on the branch, and each R1 item has landed and is witnessed by a killed mutant (F-1 anchor, the 13 fixtures moved with none left, R2 fence-close, bot-P2 backtick fix plus its repro, and the setext rule); C-3 prose names the heading in 78 lines, and C-4 is green (python3 -m unittest discover -s tests: Ran 1359, OK; validate.py exit 0; ruff clean; badge 1359 matches); there is no scope creep, since the docs/missions, ARCHITECTURE.md and badge changes are generated regen, and the tautology guard passes. Greptile P1 4012744258 is VALID, a fail-closed false refusal rated Nit: run_report.py:506 'setext = para and _SETEXT_RE.match(line)' closes the section when '---' follows a list item or blockquote ('- a note\n---' is ul+hr in CommonMark, not a heading), so a complete in-section table is refused as '— none found', which breaks C-2 'complete rows bind' and drifts from the prose 'up to the next heading'; there is also F-2, a Nit where the mutant on the table-row para exclusion at :518 survives, F-3, an FYI that a subsection heading ends the section, and an appendix (indented-code and multi-line HTML-comment rows still bind; a 'row-ish' heading opens the section). Still owed: in-thread replies on both bot threads (P2 4012319774, fixed in d52ff42, and P1 4012744258; neither thread has a reply and the PR has no conversation comments); I committed nothing (HEAD 04b780f, tree clean, every branch commit authored by Ravindra Kumar with no Claude trailer), made no GitHub posts, and left the worktree checked out detached at 04b780f.

[TEST-ADEQUACY R387W-r2]
I verified all R1 items landed at 04b780f (anchor d886a6c + 13 fixtures 1917488, fence-close 15e351a, bot-P2 d52ff42, setext 58dc956, prose 9cc9bee, badges 69->73). HEAD runs 73 OK exit 0, and 18 mutants in a scratchpad git-archive copy reproduce NC-1/NC-3/NC-4 and NC-2/NC-5 line for line, with every fence-close conjunct and both backtick-fence directions each killed by its own subtest. The extended protocol fixture reads the heading from the prose and TEMPLATE.md, not from the checker, so it is not a tautology. Findings: R-1 Required, the paragraph-gate exclusions at run_report.py:511-512 (table row/heading/fence/setext) have no witness, since mutants M7a-e including para=bool(line.strip()) stay green and only the blank-line case is tested. R-2 Required, Greptile P1 4012744258 is VALID: pandoc CommonMark renders a list item/blockquote/indented line followed by --- as an hr, the checker refuses a complete report, and the manifest's 'never bound' is wrong because a list item + --- before an incomplete duplicate wave-2 row binds []. Also N-1 Nit, case-fold and the \\b after 'row' are claimed but unwitnessed (M8/M9 green); N-2 Optional, the heading space/indent guards are unwitnessed; plus 2 FYI. What's left: in-thread replies are STILL OWED on bot P2 4012319774 (no reply exists; the manifest defers it to the coordinator) and on P1 4012744258. This session committed NOTHING (HEAD 04b780f, status clean, scratchpad clone deleted), and there were no GitHub posts.

[STANDARDS R387W-r2]
I reviewed PR #401 at head 04b780f on the STANDARDS axis. Every R1 batch item landed: F-1 anchor (d886a6c), 13 fixtures moved (1917488), look-alikes, R2 fence-close tests (15e351a), bot-P2 backtick fix and repro (d52ff42), setext rule (58dc956), prose (9cc9bee), badges (0ba9a75) and manifest. Monkeypatched mutants turn each new test RED, so the tautology guard passes; validate.py is green and the full suite ran 1359 OK. Findings: R-1 Required, because both bot threads are unanswered in-thread: P2 4012319774 was resolved with zero replies and still owes 'fixed in d52ff42', and P1 4012744258 is open and silent. Greptile P1 4012744258 is VALID: CommonMark renders '- a' followed by '---' as a list then <hr/>, but run_report.py:512 closes the section and falsely refuses with 'none found'. The same happens with a blockquote before '---' and with a list item before '===' (a lazy continuation). It fails closed and never binds foreign rows. Nits: N-1, the refusal message and WIP_SECTION still name the level-2 literal '## WIP-curve protocol row' (residual F-2, heading text duplicated with the regex and not pinned by a test); N-2, the para comment at :515 claims only paragraph text arms the setext rule; N-3, SECTION is declared at test :339, after 13 methods that use it. Optional: O-1, unqualified '(verdict r1)' at :482/:495; O-2, decompose the fence-close conditional. FYI: the manifest has pr null and head_sha 0ba9a75, so the conductor must re-bind to 04b780f and #401 at close. Nothing is left for this axis. This session made no commit: HEAD is still 04b780f, 04b780f..HEAD is empty, the tree is clean, and there were no GitHub posts.
