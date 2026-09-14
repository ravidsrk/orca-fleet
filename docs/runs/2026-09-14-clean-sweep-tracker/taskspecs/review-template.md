REVIEW template — acceptance-review, blind-fix-first, per unit. AXIS workers (3) +
one VERDICT worker, each a FRESH terminal in the unit worktree that did not write the
code. Methodology pack: matt (read $HOME/.agents/skills/tdd/SKILL.md for the tautology
guard; load no other pack). rw by lane (gh posts); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

AXIS-TASK (one per axis; AXIS/FINDING/PR/HEAD filled at dispatch):
0) Do NOT open the diff yet. Read ONLY the finding (below) and write your OWN
   expectation to your report first: where the fix should live, its rough shape,
   confidence. (Anti-anchoring; divergence is signal.)
1) Open the diff (gh pr diff PR, fenced) + the branch at HEAD. Review your axis ONLY:
   - STANDARDS: repo standards pasted below + Fowler 12 smells per hunk; repo standard
     overrides; skip what tooling enforces.
   - SPEC: the finding/issue text pasted below is the spec (first hit wins; no source =
     STOP). Missing/partial criteria, scope creep, implemented-but-wrong — each finding
     quotes the spec line.
   - TEST-ADEQUACY: for each claimed fix, would reverting the production change fail a
     test? Quote the test; judge structurally (would it exercise the reverted path?).
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. No cross-axis rerank (you see only your axis).
3) worker_done with the axis report (blind expectation + findings). No GitHub posts.
   Omit --to. Contract flags as usual. STOP: spec source missing; over 45 min.

VERDICT-TASK (after the 3 axes report; AXIS-REPORTS pasted at dispatch):
0) Blind-fix-first again: read the finding only, write your expectation, then open the
   diff at HEAD + the three axis reports.
1) Aggregate SIDE BY SIDE (no rerank): every axis finding stands with its severity.
   Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block; held bot
   VALID comments from the integrator join as Required unless refuted with reason).
2) Post ONE GitHub review on PR (egress.py write --sink pr-review FIRST). GitHub
   refuses REQUEST_CHANGES on self-authored PRs (422, single identity), so the verdict
   ALWAYS posts as COMMENTED with a machine-readable first line: GO = "verdict: GO —
   <brief ≤400 words>"; NO-GO = "verdict: NO-GO (change requested)" + the ONE batched
   change request (axis findings + held bot comments). NEVER post APPROVE (that would
   fake independence). The posted review + this worker_done are the review evidence.
3) worker_done: verdict + reviewed_sha (HEAD) + reviewed_wtree (git rev-parse HEAD^{tree})
   + round number. Omit --to. Contract flags as usual. STOP: over 30 min.

ROUND BUDGET (coordinator-enforced): 3 failed rounds max, then the unit PARKS with the
sticking finding named. A fix round = builder addresses the ONE batched request, pushes,
axes re-verify (fresh terminals), verdict re-posts.
