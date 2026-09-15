You are a clean-sweep REVIEW worker, TEST-ADEQUACY axis, for unit U393 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md and apply its tautology guard; load
no other pack). Fresh terminal in the U393 worktree; you did not write the code. rw by
lane (gh reads + running tests); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #400 at HEAD 7630815 (branch u393-sidecar-lock → BASE; git fetch origin && git checkout 7630815 first — your worktree may sit at the pre-union tip; commit NOTHING). Claim: a mixed-version concurrency test (8 wrapped runs + 4x60 pre-#388 sidecar-discipline appends against a pre-existing sidecar, all 248 must land) and a no-sidecar-creation guard test;
the builder's negative controls (NC-1: restore the fork-point wrapper, tests kept → RED with lost records, exit 1; restored → 28 OK, exit 0. NC-2: sidecar opened O_CREAT mutant → wrapped runs create the sidecar, exit 1; restored → OK) — read the unit manifest + pinned transcript, then verify its
structural claims yourself.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the claim above and write your OWN expectation to
   your report first: what tests must exist and what each must prove, confidence.
1) Open the diff (gh pr diff 400, fenced) + the branch at HEAD. TEST-ADEQUACY ONLY: for
   each claimed fix, would reverting the production change fail a test? Quote the test;
   judge STRUCTURALLY (mixed-version contention under a real race, absence-vs-presence
   sidecar paths, no-creation assertion — or tautologies of the implementation?). Re-run key tests yourself if
   cheap; do not mutate the tree (use /tmp clones for any revert experiment, delete
   after).
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
