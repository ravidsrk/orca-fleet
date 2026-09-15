You are the clean-sweep VERDICT worker for unit U364, review round 3 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U364 worktree; you wrote neither the code nor
the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with
git log that no commit carries your session, and say so in worker_done.

TARGET: PR #395 at HEAD 8323c98 (branch u364-eval-fixtures → BASE). Finding (#364):
per-skill behavioral evals ship zero fixtures — the 63 cases carry empty file sets
flagged narration-only, and the runner grades only the agent's trace, discarding the
workspace. C-1 every mission in the dispatch-time catalog (21) has >=1 fixture-backed
behavioral case covering its riskiest behaviour; C-2 the workspace-state oracle grades
resulting state (passing trace over wrong workspace FAILS); C-3 narration-only cases
stay explicitly labeled and bounded, the routing gate still passes, the full suite
stays green. OUT: promoting eval output to proof evidence; touching the routing suite;
new missions' eval files beyond the 21. ROUND 2 ended NO-GO (review 5204457473
@6766265) with 4 Requireds (harden-it venv glob, django rows, per-check teeth, 2
undemonstrated positives); round 3 re-verifies the landed batch (7c9c243: harden-it
scoping + _pytest excerpts + venv row, 4 DJANGO_ROWS, per-check violating rows,
field-test-it/oss-contribute passing rows, N3 every-copy assert) plus the full axes on
top. NOTE: PR #395 has ALREADY been merged out-of-process (1b64781) while this round
was in flight — your verdict posts as the review RECORD (naming what is open), not as a
merge gate. Judge strictly but only on what is actually open — do not invent new
Requireds from Nits, and do not re-litigate refutations prior SPEC axes upheld.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 395, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status: every Greptile thread has an in-thread reply (2 fixed, 3
   refuted-with-reason and UPHELD by prior SPEC axes); Greptile's re-review of the r4
   tip added 0 comments. No held bot finding this round. Greptile posted no APPROVED —
   note that, do not treat it as a finding.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #395 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 8323c98);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 8323c98) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (8323c98) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 8323c98) + round 3 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 3 — PASTED AT DISPATCH) ---

[SPEC R364r3]
Reviewed PR #395 at 8323c98 on the SPEC axis only (fenced gh reads, 21/21 riskiest-behaviour picks read, suite re-run: Ran 1339 tests OK, routing gate 94/94 exit 0, no routing file touched, no proof promotion, r2 batch re-verified: harden-it scoping, 4 _pytest excerpts, +4 DJANGO_ROWS, 55 violating rows with every regex check covered, field-test-it/oss-contribute passing rows present). One Required finding, F-1, is r2 F-1's class left open: prove-it id-4's unscoped glob **/*.py tautology ban fails a doctrine-following workspace once a .venv holds mutmut (its dependency libcst ships 'assert True' in its tests); reproduced through the real check_workspace_state (doctrine test alone -> [], same + real venv -> fails), which breaks C-2/C-1 by the PR's own 'a workspace venv is doctrine-following' standard. Left open: rescope prove-it's two bans, and on the same pass oncall-it's two **/*.py bans (probed at 0 hits, FYI), to the case tree with a libcst venv row; this session made no commits (git log --grep on the session id -> 0, worktree clean) and posted nothing to GitHub.

[TEST-ADEQUACY R364r3]
I wrote my expectation first, then reviewed PR #395 at 8323c98 on the test-adequacy axis only, all PR reads fenced, and verified every claim in scratch clones since deleted. The NC reproduced exactly (eval.py @506a059: 23F+160E exit 1; clean: 98 OK) and C-1 is RED 21/21 on the base catalog. Frozen-list grow/shrink and the coverage mutants are killed, and reverting any harden/deflake ban glob to **/*.py fails the venv tests; the _pytest excerpts are verbatim pytest 9.1.1 and are what give the harden test its teeth. A 150-mutant catalog survey leaves 1 survivor (deflake root *.py over-strict, already in the manifest) with 0 vacuous, so R-B and R-C are CLOSED; all three R-A django mutants now die, and 19/25 eval.py code mutants are killed. Findings: Critical and Required none. O-1 Optional: DJANGO_ROWS pins only the 6.x edge, so any-5.x floor mutants survive and a django==5.1.9 downgrade has no row. N-1 Nit: 4 schema refusal branches are shadowed in their subtests because assertTrue(errors) accepts any error (test_evals.py:1270/:1275/:1259, blank path). N-2 Nit: the CLI state text lines (eval.py:1204/:1215) are untested. N-3 Nit: the requests pre-release/case rows and a deflake root .py passing row are still missing. FYI: 'fails on it ALONE' is untrue for 4 regex checks (reddening still holds via exact lists), label collisions, AGENT_MUST_EDIT backstopped by the requests-substring assert. Nothing is left on this axis (no rerank or verdict); I committed NOTHING (HEAD 8323c98, porcelain empty; the only newer commits, b6c4f5c and 532a273, are the coordinator's ledger commits on review/2026-09-14-holistic-fixes) and made no GitHub posts.

[STANDARDS R364r3]
I reviewed PR #395 at 8323c98 on the STANDARDS axis only, with the pre-diff expectation written first and all PR reads fenced. Every CI gate passed when I ran it (validate 0, full suite 1339 OK, routing 94/94, proof_status/run_report/bundle 0, ruff check clean), and the no-invented-references check is clean: all 23 quoted mission rules exist in their own SKILL.md and the pip 26.2.1 / pytest 9.1.1 excerpts match real installs line for line. Findings: S-1 Nit is the one with a reproduced consequence (the deflake-it id-4 retry-ban regex is copied across 3 globs, and dropping @flaky from the src/**/*.py copy alone still passes Ran 98 OK in a scratch copy, a TEST-axis sensitivity question); S-2..S-5 are Nits (repeated predicate lookup at eval.py:957/991, the fixture snapshot written 4 ways, run_behavioral_eval at 149 lines with a fifth refusal block at :1080, opaque R364r2/S5 codes in test comments), S-6 is Optional (_labels parses prose at test_evals.py:90), S-7 is FYI (empty-body badge commits, default merge subjects); no commit carries my session, HEAD 8323c98 is unchanged and clean, and nothing is left for this axis.
