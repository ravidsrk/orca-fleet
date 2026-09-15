You are a clean-sweep BUILD worker for unit U364 (methodology pack: matt — read
$HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack).

GOAL · SCOPE · NON-GOALS · STOP · EVIDENCE · ESCALATION · BUDGET: build-change.
Work on branch u364-eval-fixtures in THIS worktree (forked from origin/BASE
review/2026-09-14-holistic-fixes @ c53fac479a96e5bf7abe2ef5d1932c0414f1134a — verify with git log before starting;
refuse a dirty baseline or a wrong base). If the worktree branch is not
u364-eval-fixtures, create it from origin/review/2026-09-14-holistic-fixes first.

FINDING (agent-brief, verified by triage; Q1 direction: fixtures + workspace-state
oracle):
CATEGORY: enhancement (S1). All 63 per-mission behavioral eval cases carry empty file
sets flagged narration-only, and the behavioral runner materializes file sets into a
temporary workspace but grades only the agent's trace, discarding the workspace — so
even fixture-backed cases would be graded on prose, never on resulting state.
DESIRED: at least one fixture-backed behavioral eval per mission covering its
highest-risk behaviour, plus a post-run workspace-state oracle so fixtures change the
verdict: a case passes only when the workspace reaches the asserted state. The routing
suite and its gate are untouched. Existing narration-only labels stay honest where no
fixture exists yet (no silent narration grading returns).
OUT OF SCOPE: promoting eval output to proof evidence (the tooling's declaration in
scripts/eval.py stands); touching the routing suite; new missions' eval files beyond
the catalog present at dispatch (21 missions). NOTICED-BUT-NOT-TOUCHED otherwise.

HOT FILES (re-derived at dispatch): scripts/eval.py, skills/*/evals/evals.json (the 21
present at dispatch), tests/test_evals.py. Touch nothing else. Never `git add -A`.

CONTRACT (coordinator-issued — copy EXACTLY into the manifest; the dispatch binding
prepended to your TASK resolves both lines — copy the BINDING values, not these
placeholders):
contract.source = docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-364.md
at the dispatch commit named in your binding.
contract.digest = sha256:__DIGEST_364__ (of THIS task spec file).
criterion_ids = [C-1, C-2, C-3].
C-1: every mission in the dispatch-time catalog has >=1 fixture-backed behavioral case
(files[] non-empty, narration_only absent or false) covering its riskiest behaviour.
C-2: the workspace-state oracle grades resulting state — a passing trace over a wrong
workspace FAILS; fixtures change the verdict.
C-3: narration-only cases stay explicitly labeled and bounded (frozen-list equality);
the routing gate still passes at its threshold; the full suite stays green.
NC-COMMAND: python3 -m unittest tests.test_evals

STEPS:
1) Red FIRST: (a) a per-mission coverage test proving >=1 mission has zero
   fixture-backed cases today (must fail pre-fix, pass post-fix); (b) an oracle test
   with a synthetic workspace proving a passing trace over a wrong workspace passes
   today (the defect) and fails post-fix; (c) a frozen-list test naming exactly the
   narration-only cases that remain (fails on silent growth or silent shrinkage).
   Expected values from the brief above (independent source), never recomputed the
   runner's way.
2) Smallest change: (a) each fixture-backed case names its asserted end-state in the
   case record, machine-readable — the oracle reads the record, not prose (exact field
   shape is your TDD choice, reviewed on the spec axis); (b) the runner gains the
   post-run workspace-state check in its materialize-then-grade flow (wrong workspace
   fails the case even when the trace grades clean); (c) the oracle is deterministic
   with no model calls (no tokens in the pass/fail path); (d) 21 cases, one per
   mission, each covering that mission's riskiest behaviour (your tasteful pick per
   mission, defended in the commit message; the spec-axis reviewer checks the picks).
   Oracle logic is unit-tested in tests/test_evals.py with synthetic workspaces.
3) Recorder run of the nc-command + validate.py + FULL suite green. ruff on touched
   files. commands[].artifact null everywhere (scratchpad transcripts are inlined
   summaries, never /tmp paths).
4) NEGATIVE CONTROL: tool=revert on the scripts/eval.py oracle path; nc-command
   NONZERO reverted, ZERO clean. Transcript recorded.
5) gitleaks detect clean before pushing.
6) Commit on u364-eval-fixtures (bisectable, maintainer author, no trailers, named
   staging). Push (egress.py write --sink git-push --host github.com --payload-class
   branch-tip --consent run-2026-09-14-clean-sweep:base-writes FIRST). No PR
   (integrator opens it). No merge/rebase onto BASE.
7) Manifest at docs/runs/2026-09-14-clean-sweep-tracker/u364-manifest.json (commit on
   branch): unit U364, base SHA + head_sha := your last CONTENT commit
   (pre-manifest — a commit cannot name its own SHA; the manifest commit follows
   with a manifest-only delta and you name the pushed tip separately in
   worker_done; the conductor re-binds head_sha to the reviewed tip at close),
   contract above, C-1..C-3 with witnesses, commands, negative_control (revert,
   oracle path, NC-COMMAND verbatim, RED), intent non-empty, lighting lit,
   reviewer_mode same-vendor-fresh. Leave pr EMPTY.

STOP: unexplained red; out-of-scope rot (note, do not touch); over 120 minutes.
ESCALATION: blocking ask. No sub-dispatch.

WORKER CONTRACT: preamble --from + --dispatch-capability on every send. check
--terminal <handle> at checkpoints + pre-worker_done; consumer_fenced = stop, no
worker_done. --report-path + --files-modified. worker_done --outcome, omit --to.
Worktree comment current.
