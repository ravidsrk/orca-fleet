You are a clean-sweep STABILIZE worker (methodology pack: matt — read
$HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack).

GOAL: land 4 uncommitted review-feedback hunks in THIS worktree (branch
review/2026-09-14-holistic-fixes) so BASE is green.

SCOPE (exact files — stage ONLY these with named git add paths, never git add -A):
docs/completion/HUMAN_ACTIONS.md, runtime/scripts/deny-hook.sh,
runtime/scripts/run_report.py, runtime/scripts/verify.py, tests/test_deny_hook.py,
tests/test_run_report.py, tests/test_verify.py, assets/badges/tests.json (regenerated),
docs/runs/2026-09-14-clean-sweep-tracker/stabilize-manifest.json (create it).
Do NOT touch docs/runs/2026-09-14-clean-sweep-tracker.md, docs/DECISIONS.md,
docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/, .claude/, .orca/, or any other file.
The dirty baseline IS this unit (clean-baseline rule waived with reason, recorded in
the run ledger).

NON-GOALS: no other fixes, no review verdicts, no push, no rebase.

STEPS:
1) git diff --stat to see the hunks.
2) The 2 RunDirectoryBinding tests currently ERROR (red-first already): fix
   tests/test_run_report.py RunDirectoryBinding._run_dir to pass a Path root —
   run_directory takes Path or None; minimal fix honoring the existing contract.
3) python3 scripts/gen-badges.py to refresh assets/badges/tests.json.
4) Run the criterion-bound tests THROUGH the recorder:
   python3 runtime/scripts/evidence-run.py --label tests \
     --manifest docs/runs/2026-09-14-clean-sweep-tracker/stabilize-manifest.json \
     -- python3 -m unittest tests.test_deny_hook tests.test_run_report tests.test_verify
   — all green required.
5) python3 scripts/validate.py — green required.
6) NEGATIVE CONTROL in a throwaway worktree: git worktree add /tmp/nc-stab HEAD; there,
   restore the 3 production files (deny-hook.sh run_report.py verify.py) to their committed
   versions and run the same 3-module test command — require NONZERO (the new tests fail
   without the production change); then git worktree remove --force /tmp/nc-stab.
   Record the transcript.
7) Commit per-hunk (4 commits: deny-hook plus its test; run_report plus its tests; verify
   plus its tests; HUMAN_ACTIONS plus badges plus manifest; repo-default author, no
   trailers, receipt-style messages naming PR 387 review).
8) Write the evidence manifest JSON at
   docs/runs/2026-09-14-clean-sweep-tracker/stabilize-manifest.json: unit STABILIZE,
   base_sha (commit before your first commit), head_sha, criteria addressed, commands with
   exit codes from step 4, negative_control (tool revert, paths the 3 production files,
   command the exact step-4 test command, result RED with transcript reference), intent
   goal/ruled_out/why all non-empty, lighting lit.

STOP: any red you cannot explain; anything outside scope looks wrong (note it, do not
touch); over 60 minutes.
ESCALATION: blocking ask to the coordinator on STOP.
BUDGET: one unit; never dispatch sub-workers (nesting is forbidden).

WORKER CONTRACT: your preamble carries your --from handle and --dispatch-capability —
put both on every send. Run check --terminal <your-handle> at checkpoints and once
before worker_done; consumer_fenced means stop immediately with no worker_done. Evidence
rides typed flags --report-path and --files-modified, never hand-rolled payload JSON.
worker_done requires --outcome succeeded or failed and OMITS --to. Keep the worktree
comment current at checkpoints.
