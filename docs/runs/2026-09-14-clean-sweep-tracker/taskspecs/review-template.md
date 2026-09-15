REVIEW template — acceptance-review, blind-fix-first, per unit. AXIS workers (3) +
one VERDICT worker, each a FRESH terminal in the unit worktree that did not write the
code. Methodology pack: matt (read $HOME/.agents/skills/tdd/SKILL.md for the tautology
guard; load no other pack). rw by lane (gh posts); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET (PR/HEAD/BRANCH filled at dispatch; every instantiated spec carries this line):
PR #<n> at HEAD <sha> (branch <unit-branch> → BASE). Before reading anything, run
  git fetch origin && git checkout <sha>
then assert git rev-parse HEAD == <sha> (your worktree may sit at an older or pre-union
tip; the detached HEAD this leaves is expected — leave it detached and say so in
worker_done; whoever commits next reattaches first, per the conductor-close.md reattach
rule).
A checkout that fails or lands elsewhere = STOP. Commit NOTHING.

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
   Omit --to. Follow the WORKER_DONE CONTRACT below. STOP: spec source missing; over 45 min.

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
   + round number + the posted review id. Omit --to. Follow the WORKER_DONE CONTRACT
   below. STOP: over 30 min.

WORKER_DONE CONTRACT (axis and verdict workers alike; every item is required, none implied):
- Preamble: every orca orchestration send / ask / check carries the --from <handle> and
  --dispatch-capability <dcap> from your dispatch preamble, verbatim. Questions go through
  ask, never a local prompt.
- worker_done is sent EXACTLY ONCE, with both lifecycle ids (--task-id and --dispatch-id)
  and an explicit --outcome succeeded|failed: succeeded = your report is complete, whatever
  the verdict; failed = you could not finish (never encode failure in prose only).
- --report-path <your axis or verdict report file>: the durable report the body summarises.
- --files-modified: omit it — a reviewer changes no tracked file. If you did change one,
  name it in --files-modified, say why in the body, and treat it as a STOP.
- --body: three sentences (what you reviewed at which HEAD, what you found by severity,
  what is left). Omit --to. After worker_done: idle — no polling, no new work.
- A consumer_fenced reply on any send = stop; no worker_done.

ROUND BUDGET (coordinator-enforced): 3 failed rounds max, then the unit PARKS with the
sticking finding named. A fix round = builder addresses the ONE batched request, pushes,
axes re-verify (fresh terminals), verdict re-posts.
