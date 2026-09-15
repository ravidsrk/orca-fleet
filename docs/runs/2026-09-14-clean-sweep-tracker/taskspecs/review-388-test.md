You are a clean-sweep REVIEW worker, TEST-ADEQUACY axis, for unit U388 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md and apply its tautology guard; load
no other pack). Fresh terminal in the U388 worktree; you did not write the code. rw by
lane (gh reads + running tests); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #392 at HEAD 0775547 (branch u388-lockfile → BASE; git fetch origin + checkout 0775547 first — your worktree may sit at the pre-union tip; commit NOTHING). Claim: a litter test
(sequential runs leave nothing beside the manifest), a 16-way concurrency guard test
(green at base, RED 10/10 against a no-lock mutant), and a fingerprint-equality test;
the builder's negative control (revert the wrapper) exits 1 with both litter tests RED
and 0 at clean head — read the unit manifest + pinned transcript, then verify its
structural claims yourself.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the claim above and write your OWN expectation to
   your report first: what tests must exist and what each must prove, confidence.
1) Open the diff (gh pr diff 392, fenced) + the branch at HEAD. TEST-ADEQUACY ONLY: for
   each claimed fix, would reverting the production change fail a test? Quote the test;
   judge STRUCTURALLY (litter assertion, concurrency guard under a real race, fingerprint
   comparison — or tautologies of the implementation?). Re-run key tests yourself if
   cheap; do not mutate the tree (use /tmp clones for any revert experiment, delete
   after).
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
