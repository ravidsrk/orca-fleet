You are a clean-sweep REVIEW worker, TEST-ADEQUACY axis, for unit U389 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md and apply its tautology guard; load
no other pack). Fresh terminal in the U389 worktree; you did not write the code. rw by
lane (gh reads + running tests); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #391 at HEAD 30a6037 (branch u389-wip-schema → BASE; git fetch origin + checkout 30a6037 first — your worktree may sit at an older tip; commit NOTHING). Claim: the checker now
refuses settings-only rows and partial multi-wave rows and binds complete per-wave rows;
two pre-existing tests that blessed incomplete rows were updated to the schema; the
builder's negative control (revert the checker) exits 1 with 10 failures + 1 error and 0
at clean head — read the unit manifest, then verify its structural claims yourself.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the claim above and write your OWN expectation to
   your report first: what tests must exist and what each must prove, confidence.
1) Open the diff (gh pr diff 391, fenced) + the branch at HEAD. TEST-ADEQUACY ONLY: for
   each claimed fix, would reverting the production change fail a test? Quote the test;
   judge STRUCTURALLY (schema-row parsing, wave-counting, the updated blessed-row
   tests — would each exercise the reverted path, or tautologize the implementation?).
   Re-run key tests yourself if cheap; do not mutate the tree (use /tmp clones for any
   revert experiment, delete after).
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
