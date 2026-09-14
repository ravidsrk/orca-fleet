You are the clean-sweep VERDICT worker for unit U389, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no
other pack). Fresh terminal in the U389 worktree; you wrote neither the code nor the axis
reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #391 at HEAD 30a6037 (branch u389-wip-schema → BASE). Finding (#389):
the run-report checker's WIP-curve validation passes any mutating run report containing
at least one table row naming builder and reviewer counts. C-1 a settings-only row is
refused; C-2 a multi-wave report with partial or missing wave rows is refused; C-3
complete per-wave rows bind, and the protocol prose names the enforced schema. OUT:
changing WIP caps; the multi-run graduation analysis; other report checks (manifest
binding, inventory, invocation).

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 391, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. There is NO held bot finding this round: Greptile's 3 threads (template
   waves, manifest abs-paths, dup cells) were fixed at 30a6037 with in-thread fix
   replies, and Greptile re-reviewed 30a6037 with 0 comments (it posted no APPROVED —
   note that, do not treat it as a finding). NOTE the reconciled threads in your
   verdict; do not treat them as Required.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #391 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 30a6037);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 30a6037) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (30a6037) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 30a6037) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1) ---

[SPEC R389]
I reviewed PR #391 at 30a6037 on the SPEC axis. I wrote my expectation before opening the diff, fetched the diff fenced (guard_text exit 0), re-verified the build-389 contract digest, and probed edge cases with a scratch script; tests.test_run_report passes 57/57 and run_report.py exits 0. C-1, C-2 and C-3 are all met with no scope creep, and the waves=<n> header field is a faithful, additive definition of 'recorded waves': the spec lets the builder define it, headers with or without waves= both still parse, and it is documented in TEMPLATE.md and attention-budget.md. Four Nits remain: docs/runs/README.md:44 still says 'the WIP-curve protocol row' (singular) with the old field list; the TEMPLATE.md:80 heading is singular; a duplicated header 'waves=3 waves=1' collapses to 1 and lets one row bind; and the run_report.py docstring (lines 12-21) does not list waves= (the builder disclosed this). There are also 6 FYIs, including that waves= is self-declared and not checked against the ledger prose, and that the external-run scoping mismatch dates from #365. I made no commits (0 commits in git log --all carry my session, and the worktree is clean) and posted nothing to GitHub.

[TEST-ADEQUACY R389]
I checked the test-adequacy of PR #391 at 30a6037 in a /tmp clone: clean run 57 OK exit 0, and reverting the checker to e04b0c2 exits 1 with 11 failures + 1 error (the claimed 10+1 is the round-1 count from before the F3 test was added; controls b/c/d reproduce as recorded), the two formerly blessed tests are sound (the old settings row is now asserted refused and the LiveCatalog len==1 WIP-leg check goes RED), and no test is tautological. A 12-mutant battery killed 7, but 2 Required gaps survived: deleting the doubled-wave check (M2) stays green because the 'wave 1 twice, wave 2 never' case is also refused by the absent-wave leg and only assertTrue(errs) is checked, and weakening the digit-led measured-value rule to presence-only (M5/M5b) stays green, so a row like throughput=TBD latency_median=? binds; there are also Nits (builders/reviewers integer rule unwitnessed; non-specific assertTrue) and Optionals (the deviation-row over-refusal pin and the header-only waves= pin are each witnessed only incidentally). Nothing is left on this axis: no files modified, no GitHub posts, /tmp scratch deleted (report kept at /tmp/u389-ta-axis-report.md), and git log --all --grep on this session id returns 0 commits, so no commit carries this session.

[STANDARDS R389]
I reviewed PR #391 at 30a6037 (base e86c42c) on the STANDARDS axis only: I wrote my own expectation first, read the diff through guard_text (exit 0), and checked it against AGENTS.md, ARCHITECTURE.md, CONTRIBUTING.md and Fowler's smells, with mutation probes run in git-archive scratch copies. One Required finding: the new doubled-wave check, run_report.py:530 'doubled = sorted({k for k in named if named.count(k) > 1})', has no negative-path test, which CONTRIBUTING.md:119-121 requires. Deleting it leaves tests.test_run_report GREEN (clean and mutant copies fail the same single git-only test), because the only repeated-wave case also trips the absent check and every subtest asserts only assertTrue(errs); the wave-digit filter (:528, without it a wave=one row crashes the checker with ValueError) and the waves>=1 clause (:522) are also untested. Nits: the throughput assertion at tests:244 passes for any row error; the test comment at :203 credits attention-budget.md with rows that are not in it; the quote at :774 is not verbatim; the docstring's RUN: field list omits waves=; the name 'doubled' is used for two things. Optional: the RUN: header is parsed a second time instead of reusing parse_run_header, _wip_curve_errors is getting long, _WIP_COUNTS and the row tuples are primitive data, and test setup repeats. No finding on three-layer separation, the protocol doc's load ceiling (+19 B, 78/160 lines, gen-badges --check exit 0), bare-name references, receipt-style commits with no trailers, or tautologies (expected values come from independent sources). validate.py and tests.test_run_report pass at HEAD. Nothing is left on this axis. I committed nothing: HEAD is still 30a6037, the worktree is clean, and no commit on any ref carries this session. One unfenced gh pr view call returned only baseRefName/headRefOid metadata.
