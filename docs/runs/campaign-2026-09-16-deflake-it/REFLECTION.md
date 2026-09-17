# REFLECTION — deflake-it self-test, campaign-2026-09-16-deflake-it

Per `compound-learn`: a PROPOSAL, not a merge. No worker may commit these lines without a
recorded human approve of the exact text.

## Surprises

- The CI failure that started this run (OSError 39 on `.git` teardown @ ec917f50) was a RECURRENCE
  of #340 through a site the #340 fix did not cover — the second fix on one seam. The exposure audit
  (bare `TemporaryDirectory` + temp git repo, per site) found all four remaining sites in minutes;
  the original fix covered only the base class it happened to touch.
- Natural local rate was 0/500 (macOS never reproduces a Linux-CI teardown race), yet the mechanism
  loop (concurrent writer vs teardown) raised the construct failure rate to 200/200 — the mission's
  "loop that raises the rate" does not have to be the natural suite; a faithful construct pair counts
  when the natural distribution is environment-bound. The pinning regression test then made the
  red-by-revert ratchet executable (0/20 vs 20/20).
- `test_docs_navigation` archive gates only glob `2*` names — the `campaign-` prefix keeps campaign
  evidence out of the dated-report convention automatically. Convenient, but implicit.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: `tempfile.TemporaryDirectory` holding a fixture git repo MUST use `ignore_cleanup_errors=True`
  (use `_temp_repo()` in `tests/test_verify.py`) — a late writer in the gitleaks-PATH CI leg races
  teardown and fails it with OSError 39 (#340, CI run 35074600535).
- TEST_STRATEGY: when a flake's natural local rate is 0, pin the CONSTRUCT (faithful minimal pair +
  raced condition) as the regression test — revert-the-fix must re-arm it at high rate, or the test
  proves nothing.
- GOTCHAS: `docs/runs/campaign-*` directories are invisible to the run-archive index/inventory gates
  (those glob `2*`); dated `docs/runs/<YYYY-MM-DD>-*` reports must be index-linked with an inventory.
- ARCH_DECISIONS: two fixes on one seam is the reshape-it tripwire's yellow light (third fix = handoff):
  the temp-repo teardown seam now has RepoCase + `_temp_repo()` carrying the same flag — a third
  occurrence should unify the seam, not add a third mitigation.

## Prompt / playbook tweaks (fleet-side, optional)

- deflake-it SKILL: name the construct-pair + pinning-test pattern explicitly for environment-bound
  flakes (natural rate 0 locally) — currently the pipeline reads as if the natural suite loop is the
  only admissible oracle. (Backlog item; do not edit orca-fleet from this run — this run IS orca-fleet,
  so file as a maintainer proposal instead.)
