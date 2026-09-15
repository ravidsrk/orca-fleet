You are a clean-sweep REVIEW worker, SPEC axis, for unit U364 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U364 worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #395 at HEAD c5d4bb7 (branch u364-eval-fixtures → BASE; git fetch origin + checkout c5d4bb7 first — your worktree may sit at an older tip; commit NOTHING). SPEC (first hit wins):
C-1 every mission in the dispatch-time catalog (21) has >=1 fixture-backed
behavioral case (files[] non-empty, narration_only absent or false) covering its
riskiest behaviour; C-2 the workspace-state oracle grades resulting state — a passing
trace over a wrong workspace FAILS, fixtures change the verdict; C-3 narration-only
cases stay explicitly labeled and bounded (frozen-list equality), the routing gate still
passes, the full suite stays green. OUT: promoting eval output to proof evidence;
touching the routing suite; new missions' eval files beyond the 21. NOTE: the builder
chose the asserted-end-state field shape (TDD choice) and one riskiest-behaviour pick
per mission defended in the commit message — judge whether each pick faithfully covers
that mission's riskiest behaviour (a tame pick that dodges the real risk fails C-1),
whether the oracle reads the record rather than prose, and whether the oracle is
deterministic with no model calls in the pass/fail path. HELD BOT P1 (refuted —
judge this call): Greptile comment 4010263920 notes the id-4 positive regex checks
only the first specifier, so contradictory pins (>=2.32.4,<2.32.4) pass every check.
The coordinator refuted with reason (in-thread reply 4010303922): legitimate
multi-specifier pins (>=2.32.4,<3) must pass, distinguishing them needs
specifier-set solving (oracle-engine work), and no realistic agent emits
pip-unsatisfiable pins. Judge whether this refutation holds or the case's threat
model must cover adversarial pins — a Required here means another fix round.

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
