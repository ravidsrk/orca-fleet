You are the clean-sweep VERDICT worker for unit U389, review round 2 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no
other pack). Fresh terminal in the U389 worktree; you wrote neither the code nor the axis
reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #391 at HEAD 50cc4e6 (branch u389-wip-schema → BASE). Finding (#389):
the run-report checker's WIP-curve validation passes any mutating run report containing
at least one table row naming builder and reviewer counts. C-1 a settings-only row is
refused; C-2 a multi-wave report with partial or missing wave rows is refused; C-3
complete per-wave rows bind, and the protocol prose names the enforced schema. OUT:
changing WIP caps; the multi-run graduation analysis; other report checks (manifest
binding, inventory, invocation). ROUND 1 ended NO-GO (review 5202412008 @30a6037)
with a batch (doubled-wave isolated + wave=one + waves=0, placeholder-row,
message assertions, builders=int, doubled waves= header refused, docstring); round 2
re-verifies that batch plus the full axes.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 391, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. There is NO held bot finding this round: Greptile's 3 threads were fixed
   with in-thread fix replies, and its re-reviews at 30a6037 and 50cc4e6 show 0 new
   comments (Greptile check: pass). It posted no APPROVED — note that, do not treat it
   as a finding.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #391 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 50cc4e6);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 50cc4e6) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (50cc4e6) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 50cc4e6) + round 2 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 2) ---

[SPEC R389r2]
I reviewed PR #391 at 50cc4e6 on the SPEC axis only. I wrote my expectation before opening the diff, read the diff, PR body and issue #389 through guard_text.py (all exit 0; one early unfenced gh pr view read was metadata only), and ran probes and 11 mutants in a scratch copy. C-1, C-2 and C-3 are met, and every R1 verdict-batch item landed (R1/R2/a-d): each has a test that only its own mutant fails. The waves=<n> definition implements 'one complete row per recorded wave' without an incompatible schema change: parse_run_header is unchanged, so legacy headers still parse, waves= is enforced only in the WIP leg for mutation-class missions, no live report regresses because no mission claims a tier, and the extension is documented in TEMPLATE.md:16-24, the run_report.py docstring and attention-budget.md:60. What remains is non-blocking: Nit N1 docs/runs/README.md:44-46 still describes the old single-row schema; Nit N2 digit-led values let throughput=3TBD bind; Nit N3 TEMPLATE does not scope waves= to mutating runs; FYI F1 the count is self-declared; F2 any table row carrying wave= is treated as a WIP row; F3 rows inside code fences count; F4 no end-to-end check_report positive test for a mutation-class report. Gates: tests.test_run_report 63 OK, validate.py exit 0, run_report.py CLI clean; full suite not run. I committed nothing: HEAD is still 50cc4e6, the tree is clean, and git log --all finds no commit carrying this session. No GitHub posts.

[TEST-ADEQUACY R389r2]
Reviewed PR #391 at 50cc4e6 (fenced diff + manifest), wrote my expectation first, then ran 20 one-line mutants plus the base revert in a /tmp clone (deleted afterwards). All R1 items landed and each claimed leg is witnessed; the checker revert gives failures=18, errors=1 of 63, matching the manifest (the dispatch's 10+1 is the round-1 figure at 55 tests). REQUIRED RQ1: the integer rule is tested only for builders, and two surviving _WIP_COUNTS mutants (drop reviewers / drop wave, run_report.py:787) let reviewers=2.5 or a wave=1.5 row next to a complete set BIND with 63 OK, which falsifies the manifest claim; NIT N1: nothing tests the non-integer waves= guard (run_report.py:546), and dropping it turns waves=two into a ValueError crash; FYIs F1-F5 cover two tests that don't pin which leg fires, the revert-ERROR, and the over-refusal pins; no commits made (git log --grep for this session = 0, tree clean at 50cc4e6).

[STANDARDS R389r2]
Re-reviewed PR #391 at 50cc4e6 on the STANDARDS axis after writing my expectation first. All seven verdict-r1 items are present (R1 doubled-wave/wave=one/waves=0, R2 placeholder row, message asserts, builders int, doubled waves= refused, docstring), and validate.py, ruff, gen-badges --check and tests.test_run_report (63 OK) are green; the full suite was not re-run. Findings: 0 Critical/Required; 2 Optional (the RUN: header is parsed twice, run_report.py:525 vs :121; _wip_curve_errors is 51 lines doing four jobs); 7 Nit, led by TEMPLATE.md:87 claiming unlabeled cells are refused when the PR's own test binds one, and unresolvable 'F3'/'Verdict r1' labels in code and test comments; FYIs: the protocol doc is within its load ceiling (+19 B, clean-sweep ~251 tokens under the cap), commits are receipt-style, no tautological tests. I committed nothing: HEAD is 50cc4e6 with a clean tree, no commit in e04b0c2..50cc4e6 carries this session, and nothing was posted to GitHub.
