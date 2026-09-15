You are a clean-sweep REVIEW worker, SPEC axis, for unit U393R (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U393R worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #404 at HEAD 55ef0704d0498a16c4d3034f537ab3ddffdffdab (branch u393-race → BASE; git fetch origin && git checkout 55ef0704d0498a16c4d3034f537ab3ddffdffdab first — your worktree may sit at the pre-union tip; commit NOTHING. ROUND 2: this tip should contain the r1 verdict batch — F-1 last-attempt write-through killer (adce115), F-2+F-3 post-read sidecar + blocking-join killer (53c4894), F-4 text fixes (bd6b310), badge 1381 (0de1e87), docstring (acdf998), records (55ef070) — verify each item landed, then re-run your axis.. SPEC (first hit wins):
C-1 a DETERMINISTIC regression test forcing the interleaving (new checks absent -> legacy creates+locks+reads -> new reads stale -> legacy writes -> new writes), FAILING on the unfixed code with exactly the lost legacy record and GREEN after, schedule-forced via barriers/events (no bare sleeps on the correctness path), all locking/IO through the real module functions;
C-2 the fix: an append that joined no sidecar looks again before it writes and, if one appeared, releases the manifest lock, joins the sidecar (blocking) and re-reads, bounded retries; preserves #388 no-create, the one lock order (never hold manifest while acquiring sidecar), never-raises, and the steady-state mixed-version test; the RESIDUAL window documented honestly in code + manifest;
C-3 full suite + validate.py green. OUT: lock-free peers (impossible); changing #388; the steady-state protocol.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 404, fenced) + the branch at HEAD. SPEC axis ONLY: missing
   criteria, partial criteria, scope creep, implemented-but-wrong. Each finding quotes
   the spec line it violates plus the diff line.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
