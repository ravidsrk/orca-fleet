You are a clean-sweep REVIEW worker, SPEC axis, for unit U364, review round 2
(methodology pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for
the tautology guard only (file tools are path-locked to the worktree; do NOT use Read
outside it); load no other pack). Fresh terminal in the U364 worktree; you did not write
the code. rw by lane (gh reads); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #395 at HEAD 6766265 (branch u364-eval-fixtures → BASE; git fetch origin + checkout 6766265 first — your worktree may sit at an older tip; commit NOTHING). SPEC (first hit wins):
C-1 every mission in the dispatch-time catalog (21) has >=1 fixture-backed
behavioral case (files[] non-empty, narration_only absent or false) covering its
riskiest behaviour; C-2 the workspace-state oracle grades resulting state — a passing
trace over a wrong workspace FAILS, fixtures change the verdict; C-3 narration-only
cases stay explicitly labeled and bounded (frozen-list equality), the routing gate still
passes, the full suite stays green. OUT: promoting eval output to proof evidence;
touching the routing suite; new missions' eval files beyond the 21. ROUND 1 ended
NO-GO (review 5203909182 @c5d4bb7) with SPEC R-1 (deflake venv glob) + TEST R1 (teeth
coverage) + TEST R2 (boundary); round 2 re-verifies the landed batch — deflake glob
scoping, 21 violating workspaces, id-4 boundary table, django (?i)/>=/cap, pin-it and
attest-it checks — plus the FULL spec axis. Each riskiest-behaviour pick: does it
faithfully cover that mission's riskiest behaviour, or dodge it? HELD BOT P1 (refuted
— judge this call): Greptile comment 4010681983 says the attest-it access-review
exists:false glob rejects genuine records by name alone. The coordinator refuted with
reason (in-thread reply 4010718894): the case doctrine is GAP-never-fabricate (OB-2
has no record in the tree, so GAP to a human owner) — an agent-authored record IS
fabrication. Judge whether this refutation holds. (The round-1 contradictory-pins P1
refutation was UPHELD and stands — note only.)

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 395, fenced) + the branch at HEAD. SPEC axis ONLY: missing
   criteria, partial criteria, scope creep, implemented-but-wrong. Each finding quotes
   the spec line it violates plus the diff line.
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
