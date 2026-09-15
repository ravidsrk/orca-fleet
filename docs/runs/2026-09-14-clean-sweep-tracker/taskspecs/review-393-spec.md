You are a clean-sweep REVIEW worker, SPEC axis, for unit U393 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U393 worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #400 at HEAD 7630815 (branch u393-sidecar-lock → BASE; git fetch origin && git checkout 7630815 first — your worktree may sit at the pre-union tip; commit NOTHING). SPEC (first hit wins):
C-1 append_record takes LOCK_EX on a pre-existing sibling <manifest>.lock (opened WITHOUT O_CREAT; absent sidecar = skip, no error), then the inode lock; one documented lock order (sidecar first, inode second);
C-2 no wrapped run CREATES a sidecar (#388 invariant kept);
C-3 mixed-version concurrency: N appends via the new code + M via a sidecar-only-discipline writer, pre-existing sidecar, all N+M records land (stable test, no bare sleeps);
C-4 full suite + validate.py green. OUT: lock-free peers (impossible — no lock taken forces others to lock); rollout sequencing docs; operator runbooks.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 400, fenced) + the branch at HEAD. SPEC axis ONLY: missing
   criteria, partial criteria, scope creep, implemented-but-wrong. Each finding quotes
   the spec line it violates plus the diff line.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
