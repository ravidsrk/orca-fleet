You are a clean-sweep REVIEW worker, STANDARDS axis, for unit U393R (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U393R worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #404 at HEAD abaf17502a25f16dbd4cfaf28fafba1e211ab40a (branch u393-race → BASE; git fetch origin && git checkout abaf17502a25f16dbd4cfaf28fafba1e211ab40a first — your worktree may sit at the pre-union tip; commit NOTHING). Finding: the
#393 sidecar join is check-then-act — a legacy wrapper can create and lock
<manifest>.lock after the absence check and overlap the new append under the other
lock, silently losing a record; the fix re-checks before the truncate and, if one
appeared, releases the manifest lock, joins the sidecar (blocking) and re-reads,
bounded, under the one documented lock order, never creating a sidecar (#388 kept).
The wrapper's standing contract: never raises (warn-and-continue), transparent to the
wrapped command.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the finding above and write your OWN expectation
   to your report first: where the fix should live, its rough shape, confidence.
1) Open the diff (gh pr diff 404, fenced) + the branch at HEAD. STANDARDS axis ONLY:
   repo standards for wrapper/test changes (AGENTS.md + ARCHITECTURE.md — three-layer
   separation, instruction budgets, no invented references, receipt-style commits) +
   Fowler's 12 smells per hunk + the wrapper's never-raises/transparency contract. Repo
   standard overrides taste. Skip tooling-enforced items.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
