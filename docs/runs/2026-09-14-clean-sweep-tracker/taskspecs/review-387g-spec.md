You are a clean-sweep REVIEW worker, SPEC axis, for unit U387G (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U387G worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #402 at HEAD 15d0eea (branch u387g-evalglobs → BASE; git fetch origin && git checkout 15d0eea first — your worktree may sit at the pre-union tip; commit NOTHING). SPEC (first hit wins):
C-1 _glob_files excludes dependency/tooling dirs by a DOCUMENTED denylist; prove-it + oncall-it evals.json return to **/*.py coverage (one glob per check); EVERY mission's evals.json surveyed for T6-style narrow globs, broadened where fixtures warrant (each verdict listed);
C-2 delete-to-pass survey as committed tests: for every eval with glob checks, deleting/emptying the globbed set still FAILS the workspace; any eval passing post-delete goes fail-closed in eval.py (glob matches/not_matches over empty set fails; exists keeps semantics); already-failing evals keep guards with mutant-shown sensitivity;
C-3 full suite + validate.py green (validate checks evals validity). OUT: eval semantics beyond glob coverage; new missions' evals; behavioral-runner grading.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 402, fenced) + the branch at HEAD. SPEC axis ONLY: missing
   criteria, partial criteria, scope creep, implemented-but-wrong. Each finding quotes
   the spec line it violates plus the diff line.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
