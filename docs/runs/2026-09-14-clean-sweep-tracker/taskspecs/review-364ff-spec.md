You are a clean-sweep REVIEW worker, SPEC axis, for unit U364-FF (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U364-FF worktree; you did not write the
code. rw by lane (gh reads); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #397 at HEAD 2967804 (branch u364ff-venv-globs → BASE; git fetch origin + checkout 2967804 first — your worktree may sit at an older tip; commit NOTHING). SPEC (first hit wins):
C-1 prove-it id-4's two **/*.py bans are scoped to the case tree (tests/**,
app-or-src/**, root *.py) and a committed libcst-venv row (mutmut/libcst in .venv
beside the fix) PASSES, with committed excerpts proving the bans still hit real
tautologies; C-2 oncall-it id-4's two **/*.py bans are scoped the same way with a
committed venv row passing; C-3 the full suite stays green, the routing gate passes,
and the V2 violating-workspace rows for prove-it/oncall-it still fail (any updated
row must disclose why). OUT: any other case file; the oracle engine; the routing
suite. CONTEXT: this is a fix-forward for PR #395's recorded r3 NO-GO (SPEC F-1: the
unscoped prove-it ban failed a doctrine-following .venv holding mutmut) — U364 is
already merged; judge only whether THIS spec is met, not U364's history.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 397, fenced) + the branch at HEAD. SPEC axis ONLY:
   missing criteria, partial criteria, scope creep, implemented-but-wrong. Each finding
   quotes the spec line it violates plus the diff line.
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
