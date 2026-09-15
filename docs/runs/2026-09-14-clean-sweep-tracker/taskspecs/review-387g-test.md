You are a clean-sweep REVIEW worker, TEST-ADEQUACY axis, for unit U387G (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md and apply its tautology guard; load
no other pack). Fresh terminal in the U387G worktree; you did not write the code. rw by
lane (gh reads + running tests); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #402 at HEAD 15d0eea (branch u387g-evalglobs → BASE; git fetch origin && git checkout 15d0eea first — your worktree may sit at the pre-union tip; commit NOTHING). Claim: TestGlobScope fixtures (venv with the banned pattern IGNORED, app//lib/ modules with it CAUGHT); TestDeleteToPass per at-risk eval (oncall-it and document-it were RED pre-fix, now fail closed; the rest are path-anchored guards with mutant-shown sensitivity); M1-M4 mutants all RED (M4 survived once, killed by test hardening in the tip commit); the builder's negative control (revert eval.py + evals, keep tests → RED; restored → 109 OK) — read the unit manifest + pinned transcript, then verify its
structural claims yourself.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the claim above and write your OWN expectation to
   your report first: what tests must exist and what each must prove, confidence.
1) Open the diff (gh pr diff 402, fenced) + the branch at HEAD. TEST-ADEQUACY ONLY: for
   each claimed fix, would reverting the production change fail a test? Quote the test;
   judge STRUCTURALLY (denylist membership, fail-closed on empty, delete-to-pass per
   eval, M4-killer test — or tautologies of the implementation?). Re-run key tests yourself if
   cheap; do not mutate the tree (use /tmp clones for any revert experiment, delete
   after).
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
