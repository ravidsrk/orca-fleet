You are the clean-sweep VERDICT worker for unit U389, review round 3 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no
other pack). Fresh terminal in the U389 worktree; you wrote neither the code nor the axis
reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #391 at HEAD 51019fb (branch u389-wip-schema → BASE). Finding (#389):
the run-report checker's WIP-curve validation passes any mutating run report containing
at least one table row naming builder and reviewer counts. C-1 a settings-only row is
refused; C-2 a multi-wave report with partial or missing wave rows is refused; C-3
complete per-wave rows bind, and the protocol prose names the enforced schema. OUT:
changing WIP caps; the multi-run graduation analysis; other report checks (manifest
binding, inventory, invocation). ROUND 2 ended NO-GO (review 5202754078 @50cc4e6)
with a batch (reviewers=2.5 + wave=1.5 tests, waves=two test, TEMPLATE:87 claim,
README:44-46 schema); round 3 re-verifies that batch plus the full axes on top of a
conductor union with the merged U388.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 391, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. There is NO held bot finding this round: Greptile's threads were fixed
   with in-thread fix replies, and its re-reviews show 0 new comments (Greptile check:
   pass). It posted no APPROVED — note that, do not treat it as a finding.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #391 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 51019fb);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 51019fb) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (51019fb) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 51019fb) + round 3 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 3) ---

[SPEC R389r3]
I verified PR #391 at 51019fb on the SPEC axis (fenced diff; my pre-diff expectation was written first and matched). All five R2 batch items are in: the reviewers=2.5 subtest, the wave=1.5 test, the waves=two no-crash test, the TEMPLATE:87 claim fix and the README:44-46 schema fix. The union adds only U388/tracker files byte-identical to base parent 3e67ec4, plus the badge (1304 to 1309). C-1, C-2 and C-3 are all MET with literal-message tests (tautology guard passes), and nothing on the OUT list is touched. The waves=<n> definition is additive and not an incompatible change: REQUIRED_FIELDS is unchanged, only mutation-unit WIP legs require it, it is documented in the TEMPLATE header fence, the run_report docstring, attention-budget and README, and every existing machine-header report still parses (the 2026-08-28 ship-it report is now refused on its settings-only row, which is doctrine-only, so main([])=0). Findings: 0 Critical, 0 Required. Nit-1: any table row carrying wave= counts as a WIP row (diff 1018), so an unrelated deviations row naming wave=2 refuses the report, and the prose never names that rule. FYI-1: waves= is self-declared, so an under-declared header binds. FYI-2: a settings row beside complete rows is ignored, not refused. Checks at the tip: test_run_report 65 OK, full suite 1309 OK, ruff clean, validate.py OK. I committed nothing (git log --all shows no commit with this session's ID, HEAD is still 51019fb, the tree is clean); one early read (gh pr view metadata) was unfenced, which the report discloses. Nothing is left on this axis.

[TEST-ADEQUACY R389r3]
Test-adequacy review of PR #391 at 51019fb (fenced diff read, pre-diff expectation written first): the union delta is U388 evidence-run + tracker + badge only (6 files, no U389 file); full suite 1309 OK = badge; the R2 batch landed and each item is killed by its own /tmp-clone mutant (reviewers dropped from the integer rule -> reviewers=2.5 subtest FAIL; wave dropped -> wave=1.5 test FAIL; waves= digit guard dropped -> waves=two test ERROR); TEMPLATE:87 and README:44-46 prose landed. Reverting run_report.py to the PR base gives Ran 65 FAILED (failures=21, errors=1), i.e. 12 methods + 1 ERROR, vs 65 OK clean: this matches the manifest's 21+1, not the dispatch's stale 10+1. 13 of 15 leg mutants are killed by their named test; expected values are literal (no tautology), and the two blessed-row tests were updated without hiding coverage (the old row moved verbatim into the refused subtests). Findings: Critical/Required none; Nit-1 no test uses a bare value, and a probe shows TEMPLATE:87's claim is false for the wave cell (waves=1 + ROW_1 + '| 2 | builders=... |' binds []); Nit-2 LiveCatalog's 'WIP-curve' filter accepts any WIP error kind; Optional: the doubled-cell 'continue' (M8) and the cell-regex lookbehind (M7) mutants survive; FYI: tests call the private _wip_curve_errors and CI's run_report.py gate never reaches a mutating report. Left: nothing on this axis; committed NOTHING (git log --all shows no commit carrying this session), worktree clean at 51019fb, /tmp clone deleted, no GitHub posts.

[STANDARDS R389r3]
I checked PR #391 at 51019fb: every R2 batch item landed (reviewers=2.5 and wave=1.5 integer tests plus the waves=two no-crash test in 0a153d6; the TEMPLATE claim and README schema fixes in 6182dfb), the union merge brings in only U388's changes plus the badge (outside assets/badges it is byte-identical to the base-side diff f094356..3e67ec4, and the only conflict was tests.json resolved to 1309, confirmed by gen-badges --check exit 0), and at that SHA validate, the 65 run_report tests, the full suite (1309 OK) and ruff all pass. STANDARDS axis: nothing Critical or Required, the tautology guard passes, and the protocol doc is 78 of 160 lines and 5,664 B with clean-sweep's activation load at about 33,700 of 34,000; there is one Optional finding (S1, run_report.py:524-525, a second RUN-header parser beside parse_run_header, which still collapses duplicate fields with dict() at :121) and three Nits (S2, _WIP_COUNTS at :474 serves as both the integer rule and the message placeholders; S3, six new 'Verdict rN' comment labels in tests/test_run_report.py where the repo convention is '(PR #NNN review)'; S4, attention-budget.md:60 never states the whole-number rule the checker enforces and the drift test at :345 compares key names only). Nothing is left on this axis; FYI, the PR base branch has moved to c53fac4 since the union, and I committed nothing (0 commits in git log --all carry this session id, HEAD is still 51019fb and the tree is clean) and posted nothing to GitHub.
