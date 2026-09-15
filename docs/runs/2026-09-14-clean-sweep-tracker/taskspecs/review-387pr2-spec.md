You are a clean-sweep REVIEW worker, SPEC axis, for unit U387P (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U387P worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #403 at HEAD 7f52bf6 (branch u387p-process → BASE; git fetch origin && git checkout 7f52bf6 first — your worktree may sit at an older tip; commit NOTHING). ROUND 2: this tip should contain the R1 verdict batch (reattach rule + template ref 708b5a8, M^2 fail-closed fallback 2c029dd, C-1 probe contract+cites+flags+F3/F4 + C-4 probe bodies a632f43, T3-ref→gate-batch G3 c8a52a5; + manifest 7f52bf6) — verify each item landed (NOTE: the builder posted NO thread replies on the 2 held bot P2s — flag whether the in-thread answers are still owed and from which lane), then re-run your axis. Greptile APPROVED 5206614322 @7f52bf6 with no new inline findings — confirm. SPEC (first hit wins):
C-1 T1/T2/T3 park reads needs-human + existing ask + run ref; no other flag changes; T3 evidence cites T6 GO 5205447863; T4 evidence notes the C-2 correction; no proof-park remains in any T-row park cell;
C-2 u385-manifest.json head_tree = 4ee55a0, narrative consistent, verify.py U385 re-run recorded;
C-3 review-template.md carries a TARGET checkout line with correct separator and an explicit worker_done contract (--outcome, --report-path, --files-modified, preamble flags), no "as usual";
C-4 new taskspecs/conductor-close.md documents CLOSE (clean-worktree re-runs at merge tip, coordinator records, re-bind, pr fill, verify.py, chore commit), the option-A rule, the union-invalidates rule, the out-of-process-merge rule;
C-5 full suite + validate.py green. OUT: historical instantiated specs stay FROZEN; no flag changes beyond C-1; no code/evals/badges.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 403, fenced) + the branch at HEAD. SPEC axis ONLY: missing
   criteria, partial criteria, scope creep, implemented-but-wrong. Each finding quotes
   the spec line it violates plus the diff line.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
