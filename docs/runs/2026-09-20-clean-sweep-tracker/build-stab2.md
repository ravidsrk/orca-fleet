# BUILD SPEC — STAB-2 (frozen at dispatch)

CATEGORY: bug (run-own regression)
SUMMARY: the run's STABILIZE commits (296f100b, 3833c88e) broke 5 pre-existing suite tests on
BASE: the new run ledger has no row in the run-archive index, and README.md drifted off the
doc-wiring script's fixed point. Coordinator-verified: 39 tests OK at e8ddbd98 (origin/main),
5 failures at a58bf71a (BASE tip), byte-identical at U-CHAIN's head.

Failing tests (all reproduced by coordinator at BASE tip a58bf71a):
- tests.test_docs_navigation.TestDocsNavigation.test_run_archive_index_lists_every_report
- tests.test_docs_navigation (run_archive_integrity_standard_matches_practice)
- ReleaseCutWalkthrough.test_next_release_preparation_cut_tag_and_provenance
- ReleaseRehearsalIsolation.test_inherited_git_selection_cannot_mutate_another_repository
- tests.test_wire_docs.WiringScriptAnchors.test_the_committed_docs_are_the_scripts_fixed_point
  ("would wire README.md: img 15->15, picture blocks 10")

AUTONOMY:
- goal: make the full suite green on BASE again with the SMALLEST doc-side change.
- scope: `docs/runs/README.md` (add the missing archive row(s) for the 2026-09-20 run) and
  `README.md` (re-wire by RUNNING `python3 assets/diagrams/generator/wire_docs.py` and
  committing what it writes — never hand-editing around the script).
- non-goals: do not touch `docs/runs/2026-09-20-clean-sweep-tracker.md` or any file of units
  U-CHAIN / U-442; do not edit the wiring script or the tests; no other doc "improvements".
- stop: if the wiring script rewrites files beyond README.md, or the index tests demand
  metadata the run cannot honestly carry yet, STOP and ask.
- evidence: the five named tests green plus the FULL suite green at head
  (`python3 -m unittest discover -s tests`), output pasted in the worker_done report;
  lighting=lit.
- escalation: ask on any ambiguity; never guess.
- budget: 2 doctor attempts, then escalate.

DESIRED BEHAVIOUR: `python3 -m unittest discover -s tests` exits 0 at head; the run-archive
index lists the 2026-09-20 run (ledger file and/or run directory — match the table's existing
conventions; the run is IN PROGRESS, so its terminal state cell says so honestly, e.g.
"in progress", mirroring how the table records non-binding ledgers); the wiring script's
`--dry-run` prints no "would wire" lines.

GIT: work in this worktree on a branch cut from the BASE tip
(`git checkout -b stab-2 origin/review/2026-09-20-tracker-sweep` — if the worktree already
carries a branch from that ref, use it). Author = maintainer, no trailers, stage only the two
named files. Do NOT open a PR and do NOT push — the conductor lands the branch fast-forward.
Leave the worktree clean.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`; every
send carries `--from <your handle> --dispatch-capability <capability>`; the report rides typed
`--report-path`. Run `orca orchestration check --terminal <your own handle>` once before
`worker_done` — `consumer_fenced` means STOP and send nothing. Timebox: report-by 25 minutes;
past it, report what is green and what remains with SHAs — do not go silent.
