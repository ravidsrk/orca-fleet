You are a clean-sweep REVIEW worker, TEST-ADEQUACY axis, for unit U364, review round
3 (methodology pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash
and apply its tautology guard (file tools are path-locked to the worktree; do NOT use
Read outside it); load no other pack). Fresh terminal in the U364 worktree; you did not
write the code. rw by lane (gh reads + running tests); commit NOTHING — verify with git
log that no commit carries your session, and say so in worker_done.

TARGET: PR #395 at HEAD 8323c98 (branch u364-eval-fixtures → BASE; git fetch origin + checkout 8323c98 first — your worktree may sit at an older tip; commit NOTHING). Claim: a per-mission
coverage test was RED 21/21 at base and is green now; an oracle test proves a passing
trace over a wrong workspace passed at base and fails now; a frozen-list test bounds
the narration-only cases that remain; every fixture-backed case has a committed
violating workspace the oracle FAILS, and every regex check has a violating row
failing on it ALONE (gutting any single check reddens its row — 0/57 vacuous
survivors); table-driven boundary samples pin the requests fixed-release rule and the
django 5.2-only rule in both directions (14 requests rows, 14 django rows); the
negative control (revert the oracle path in scripts/eval.py) makes tests.test_evals
exit 1 with 23 failures + 160 errors and 0 (98 OK) at clean head — read the unit
manifest, then verify its structural claims yourself. ROUND 2 ended NO-GO on TEST R-A
(django rows) + R-B (per-check teeth) + R-C (undemonstrated positives); round 3
re-verifies that batch plus the FULL test-adequacy axis.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the claim above and write your OWN expectation to
   your report first: what tests must exist and what each must prove, confidence.
1) Open the diff (gh pr diff 395, fenced) + the branch at HEAD. TEST-ADEQUACY ONLY: for
   each claimed fix, would reverting the production change fail a test? Quote the test;
   judge STRUCTURALLY (coverage counting, oracle verdict flip, frozen-list bounds,
   per-check violating rows, boundary tables both directions, the django cap, the
   harden-it scoping + _pytest excerpts, the AGENT_MUST_EDIT guard exemption — would
   each exercise the reverted path, or tautologize the implementation?). Re-run key
   tests yourself if cheap; do not mutate the tree (use /tmp clones for any revert
   experiment, delete after).
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
