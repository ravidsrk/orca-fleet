# REFLECTION — document-it self-test (compound-learn proposal, NOT merged)

Run reached DOCUMENTED (32/32 cells, 0 parked). Per compound-learn: a proposal beside
the run report. No AGENTS.md mutation without recorded human approval of exact lines.

## Surprises

- The runtime layer's scripts carry unusually complete header contracts (usage, exits,
  wiring, failure history) — reference cells were mostly transcription with anchors,
  and every explanation rationale was already in-tree. Zero `explanation-needs-author`
  parks on a 16-entity critical set is the surprise, not the plan.
- Raw grep over-counts coverage badly: prerequisite-table one-liners scored as
  tutorial/how-to hits, filename mentions as reference. The judged map (candidate hits
  vs verdicts) was load-bearing, not ceremony.
- A rename containing the original as a substring (`--lens`→`--lens-x`) keeps a
  substring check GREEN — the negative control needs disjoint tokens to prove anything.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: negative-control renames must be substring-disjoint from the original
  (`--lens`→`--omitted`, never `--lens-x`) or a substring check stays GREEN.
- GOTCHAS: coverage-map raw hits are candidates only — a mention in a table or a
  filename hit is not quadrant content until judged against the quadrant definitions.
- NAVIGATION: operator CLI/config reference lives in `docs/runtime-scripts.md`,
  claim-checked by `docs/runs/campaign-2026-09-16-document-it/extractor/claimcheck.py`
  (flags/keys/anchors re-verifiable; rename control via `extractor/nc-run.sh`).
- TEST_STRATEGY: contract tests enumerate git-tracked docs — renaming a tracked run
  artifact without updating its referrers fails `test_docs_navigation` and
  `test_architecture` (this run hit both, fixed pre-close).
- NO-OP STEERING CANDIDATE: none identified — every preamble line used (single-router
  matt discipline held for all 32 cells).

## Prompt / playbook tweaks (fleet-side, optional)

- doc-coverage: consider a worked rule for "mention vs quadrant content" with the
  prerequisite-table and one-clause-mention shapes as negative examples (backlog item,
  not edited from here).
