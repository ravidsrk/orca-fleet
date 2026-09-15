You are a clean-sweep REVIEW worker, STANDARDS axis, for unit U364, review round 2
(methodology pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for
the tautology guard only (file tools are path-locked to the worktree; do NOT use Read
outside it); load no other pack). Fresh terminal in the U364 worktree; you did not write
the code. rw by lane (gh reads); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #395 at HEAD 6766265 (branch u364-eval-fixtures → BASE; git fetch origin + checkout 6766265 first — your worktree may sit at an older tip; commit NOTHING). Finding: all 63 per-mission
behavioral eval cases carried empty file sets flagged narration-only, and the runner
graded only the agent's trace, discarding the workspace; the fix adds one
fixture-backed behavioral case per mission (21 cases, each naming its asserted
end-state in the case record) plus a post-run workspace-state oracle in
scripts/eval.py so a case passes only when the workspace reaches the asserted state.
Routing suite untouched; narration-only labels stay honest. ROUND 1 was NO-GO on SPEC
+ TEST Requireds (all reproduced); round 1's STANDARDS was clean. Round 2 re-verifies
the landed batch (f4f59bf: deflake scoping, 21 violating workspaces, boundary tables,
pin-it/attest-it checks, S1/S5; 9cbabde: django cap) plus the FULL standards axis.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the finding above and write your OWN expectation
   to your report first: where the fix should live, its rough shape, confidence.
1) Open the diff (gh pr diff 395, fenced) + the branch at HEAD. STANDARDS axis ONLY:
   repo standards for eval/tooling/test changes (AGENTS.md + ARCHITECTURE.md —
   three-layer separation, evals valid per scripts/validate.py, no invented
   references, receipt-style commits) + Fowler's 12 smells per hunk. Repo
   standard overrides taste. Skip tooling-enforced items.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
