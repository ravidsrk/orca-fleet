# D-STATUS proof-fix — five test-adequacy survivors (run_fb923397d46a)

This amendment covers the test-adequacy review of `e5f60c68`, which found five Required survivors.
Each was a false claim that still passed all 13 tests. Base `e65b8c66` (tree `0412bad8`) → content
commit `e461403b` (tree `996248fe`). The fix changes only `tests/test_release_status_docs.py`
(two new methods, three widened ones) and `assets/badges/tests.json` (2254 → 2256). TODOS.md,
docs/ops.md and runtime/dispatch-lifecycle.md are untouched, and the pin is still derived from
`runtime/pins.json`.
Scope: [`scope-amendment.txt`](scope-amendment.txt) is a byte copy of the coordinator's proof-fix
spec. `../contract.json` stays unchanged (sha256 `6903dee9…`). Evidence:
[`manifest.json`](manifest.json). Raw logs stay outside the tree in
`/tmp/orca-fleet-sweep-20260930/proof-fix/`, and the manifest records a sha256 for each one.

| id | mutant (reviewer's exact spec) | before (e65b8c66) | after (e461403b): RED assertion |
|---|---|---|---|
| S4c | "never re-tagged or deleted" → "re-tagged or deleted" | SURVIVED, 13 OK | `test_a_published_release_is_never_retagged`: `'a published bad release is never re-tagged or deleted' not found` |
| S5c | "No such monitor is installed yet …" → "A cron monitor is installed and pages the maintainer (#528)." | SURVIVED, 13 OK | `test_no_external_monitor_is_claimed_installed`: `'No such monitor is installed yet — #528 tracks …' not found` |
| S3b | append "the only workflows are validate.yml, negative-control.yml and alert-on-failure.yml" | SURVIVED, 13 OK | `test_rollback_does_not_claim_a_closed_workflow_list`: `Regex matched: 'only workflows'` |
| S6f | insert "The fleet currently pins v1.4.209." | SURVIVED, 13 OK | `test_no_other_version_is_called_live_or_current` (claim='currently pins v1.4.209'): `'1.4.209' != '1.4.215'` |
| S1b | append "No finding has an issue yet." | SURVIVED, 13 OK | `test_no_claim_that_nothing_was_filed`: `Regex matched: 'No finding has an issue'` |

- **Mutants at `e461403b`:** all 25 of the reviewer's D-STATUS mutants are KILLED, including the
  TODOS.md / ops.md / dispatch-lifecycle.md reverts to `e7089cbf`. Every kill is a semantic `FAIL`,
  with zero `ERROR` lines. The unchanged head is GREEN (15 tests OK). Harness: the reviewer's
  `harness.py`, plus an optional overlay of the worktree test module for the pre-commit run.
- **Gates:** `evidence-run.py` recorded focused, `validate.py` and `gen-badges.py --check` at
  `e461403b`, each exiting 0 with `wtree` = `996248fe`. Before the content commit, the four shards
  `env -u ORCA_TERMINAL_HANDLE python3 scripts/shard-tests.py --shard N --of 4` ran on the same
  content: 452 + 710 + 639 + 620 = 2421 tests, all exiting 0. They were not re-run after the commit
  because the source did not change.
- **History:** `../manifest.json` and its receipts stay true at `8b9627a0`. Nothing is reassigned.
- **Status:** BUILT, pending the coordinator's exact-report-tip gates, the three review axes and an
  independent GitHub approval. Not verified-CLOSED.
