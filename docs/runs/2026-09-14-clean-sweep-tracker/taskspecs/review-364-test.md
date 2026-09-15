You are a clean-sweep REVIEW worker, TEST-ADEQUACY axis, for unit U364 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md and apply its tautology guard; load
no other pack). Fresh terminal in the U364 worktree; you did not write the code. rw by
lane (gh reads + running tests); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #395 at HEAD c5d4bb7 (branch u364-eval-fixtures → BASE; git fetch origin + checkout c5d4bb7 first — your worktree may sit at an older tip; commit NOTHING). Claim: a per-mission
coverage test was RED 21/21 at base and is green now; an oracle test proves a passing
trace over a wrong workspace passed at base and fails now; a frozen-list test bounds
the narration-only cases that remain; a passability test proves the modernize-it
advisory case fails on the untouched vulnerable fixture and passes once requests is
fixed; the negative control (revert the oracle path in scripts/eval.py) makes
tests.test_evals exit 1 with 21 failures + 35 errors and 0 (89 OK) at clean head —
read the unit manifest, then verify its structural claims yourself.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the claim above and write your OWN expectation to
   your report first: what tests must exist and what each must prove, confidence.
1) Open the diff (gh pr diff 395, fenced) + the branch at HEAD. TEST-ADEQUACY ONLY: for
   each claimed fix, would reverting the production change fail a test? Quote the test;
   judge STRUCTURALLY (coverage counting, oracle verdict flip, frozen-list bounds,
   grow/shrink mutations, the id-4 passability both-directions test, the
   AGENT_MUST_EDIT guard exemption — would each exercise the reverted path, or
   tautologize the implementation?). Re-run key tests yourself if cheap; do not mutate the tree (use
   /tmp clones for any revert experiment, delete after).
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
