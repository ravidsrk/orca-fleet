You are a clean-sweep REVIEW worker, STANDARDS axis, for unit U389 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U389 worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #391 at HEAD f642700 (branch u389-wip-schema → BASE). Finding: the run-report
checker's WIP-curve validation accepted any report with one settings-only row; the fix
defines a per-wave row schema (wave identity cell + WIP setting + throughput +
latency_median + latency_max + rework + freshness), requires exactly one complete row per
wave 1..n of a new RUN waves=<n> header field, and names the schema in the
attention-budget protocol prose.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the finding above and write your OWN expectation
   to your report first: where the fix should live, its rough shape, confidence.
1) Open the diff (gh pr diff 391, fenced) + the branch at HEAD. STANDARDS axis ONLY:
   repo standards for checker/protocol-doc/test changes (AGENTS.md + ARCHITECTURE.md —
   three-layer separation, instruction budgets incl. the protocol doc's load ceiling,
   no invented references, receipt-style commits) + Fowler's 12 smells per hunk. Repo
   standard overrides taste. Skip tooling-enforced items.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
