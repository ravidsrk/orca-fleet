You are the clean-sweep VERDICT worker for unit U364, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U364 worktree; you wrote neither the code nor
the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #395 at HEAD c5d4bb7 (branch u364-eval-fixtures → BASE). Finding (#364):
per-skill behavioral evals ship zero fixtures — the 63 cases carry empty file sets
flagged narration-only, and the runner grades only the agent's trace, discarding the
workspace. C-1 every mission in the dispatch-time catalog (21) has >=1 fixture-backed
behavioral case covering its riskiest behaviour; C-2 the workspace-state oracle grades
resulting state (passing trace over wrong workspace FAILS); C-3 narration-only cases
stay explicitly labeled and bounded, the routing gate still passes, the full suite
stays green. OUT: promoting eval output to proof evidence; touching the routing suite;
new missions' eval files beyond the 21. A bot-findings fix round already landed (F1
fixed in b23a96c with guard exemption + passability test, F2 withdrawn by Greptile);
round 1 verdicts the fixed tip.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 395, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status: F1 fixed with in-thread fix reply; F2 withdrawn by Greptile;
   the NEW P1 (comment 4010263920, contradictory pins pass the id-4 regex) was REFUTED
   WITH REASON by the coordinator (in-thread reply 4010303922) and does NOT auto-join —
   but the SPEC axis was asked to judge the call: if SPEC sustains it as Required,
   aggregate it as Required (it becomes the batched request). Greptile posted no
   APPROVED — note that, do not treat it as a finding.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #395 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA c5d4bb7);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA c5d4bb7) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (c5d4bb7) + reviewed_wtree (git rev-parse
   HEAD^{tree} at c5d4bb7) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1 — PASTED AT DISPATCH) ---

[SPEC R364]
I reviewed PR #395 at c5d4bb7 on the SPEC axis (my expectation was written before I opened the diff, and all PR reads went through the guard fence), re-ran the gates (1330 tests OK, validate 0, routing 94/94, evals/ untouched), and pushed crafted workspaces through the real id-4 cases with the real oracle. C-1, C-2 and C-3 are met: the oracle is plain file reads, the model grader cannot rescue a failed state, and the frozen list is checked by set equality. The Greptile P1 refutation holds because the agent never sees the checks (eval.py:1101-1102), a legitimate pin like >=2.32.4,<3 passes, and a mass bump still fails. One Required: the deflake-it **/*.py retry glob fails a doctrine-following agent that makes a .venv in the workspace, since pip's vendored urllib3 has Retry(. Nits: pin-it passes C-2 relabelled SUPERSEDED in place, attest-it passes forged evidence plus an OB-2 VERIFIED line, and the modernize-it django regex fails django>=5.2.6,<5.3 and Django==5.2.7. Optional: regex-edge evasions in migrate, floor, harden, prove, access and document-it. What's left is the coordinator's call on a fix round for R-1 and the nits; I committed nothing, HEAD is still c5d4bb7, the tree is clean, and 0 commits in git log --all carry this session.

[TEST-ADEQUACY R364]
I reviewed PR #395 at c5d4bb7 on the test-adequacy axis only: I wrote my expectation before opening the diff (both PR reads fenced, exit 0), then ran the NC and 16 targeted mutations in a throwaway /tmp clone, now deleted. The claims hold: C-1 is RED 21/21 against the base catalog and green at head, the oracle-flip test fails at base with 0 != 1, the frozen list catches both grow and shrink, the id-4 test fails untouched and passes fixed, the NC gives exactly failures=21 errors=35 then 89 OK, every oracle mutation (M1-M5, M15, M16) trips a behavioural test, and no assertion is tautological. Two gaps are Required: R1, C-1's 'riskiest behaviour' has no committed test in 20 of 21 missions (gutting review-it id-4 to exists:true, or every id-4 case to vacuous checks, leaves the suite green apart from the modernize-it test), and R2, the F1 regex boundary rests on one sample (dropping the fixed-pin check or accepting 2.32.3 stays 89 OK), plus Nits on the unenforced AGENT_MUST_EDIT rule and untested text output, an Optional mission-list cross-check, and an FYI that 35 of the 56 NC failures are missing-symbol errors. I committed nothing: no commit in 506a059..c5d4bb7 carries this session, and git status is empty.

[STANDARDS R364]
I reviewed PR #395 at c5d4bb7 on the STANDARDS axis only, with the pre-diff expectation recorded first (it matched eval.py oracle + per-mission evals.json cases). Standards checks that hold: validate.py passes (three-layer separation, evals valid; the schema reaches the build gate through validate.py's import of eval.py); all 21 rule quotes in 218bab6 exist verbatim in each mission's SKILL.md; commits use semantic prefixes with no trailers; 89 eval tests OK; ruff clean. Findings, each with its verbatim line: Nit S1 stray 'ROOT =Path(' whitespace regression at eval.py:46; Nit S2 commits 2827496, 218bab6 and b23a96c each fail validate.py alone (stale tests badge) against CONTRIBUTING's each-commit-builds-alone rule; Nit S3 predicate lookup duplicated at eval.py:957/991; Nit S5 the non-list workspace_state guard at eval.py:942 has no test, and mutating it out leaves all 89 tests green; Optional S4 the runner's originals snapshot is re-implemented in two tests with a different path resolution; Optional S6 run_behavioral_eval now has a fourth copy of its refuse block; FYI S7 AGENT_MUST_EDIT keeps must-edit knowledge outside the case record; FYI S8 len(expected)==63 is a literal self-check but not a code tautology. Nothing is left on this axis. I committed nothing: HEAD is still c5d4bb7, the tree is clean, and no PR commit carries this session. I made no GitHub posts.
