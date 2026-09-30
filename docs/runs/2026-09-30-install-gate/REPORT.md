# D-CI — install workflow skips main SHAs, so release gate 4 cannot bind (BUILT)

Unit D-CI of clean-sweep run `run_fb923397d46a` (task `task_359fd36a5993`, dispatch
`ctx_6efe391a4af1`). Pack: Matt build-change. Base `e7089cbf` → head `6092315` on the worker's own
checkout, branch `codex/install-every-main-sha-20260930` (renamed from
`ravidsrk/install-every-main-sha-20260930`, the prefix the checkout was created with).
Contract: [`contract.json`](contract.json), a byte copy of the coordinator's `ci-build-contract.json`, digest in the manifest; reviewer mode `same-vendor-fresh`. **State: BUILT.** Not CLOSED: no independent GitHub approver exists, and
nothing was pushed, opened as a PR or merged.

## Defect

`scripts/release_check.py:273-294` (`check_workflow_green_at_head`, called for gate 4 at `:545`)
passes only when the latest `install` run on main succeeded at the exact HEAD. `install.yml` had
a `push.paths` filter. GitHub documents that when both `branches` and `paths` are set, "the
workflow will only run when both filters are satisfied" ([workflow syntax][gh]). The video-only
e7089cbf (`assets/orca-fleet-reel.mp4`) matched no listed path, so no run started. The newest
install success stayed at 284a3d81, which leaves gate 4 unsatisfiable at that HEAD.

## Change (commit 6092315)

- `.github/workflows/install.yml`: removed `push.paths` only and kept `push.branches: [main]`.
  Added `workflow_dispatch:` for retries and backfills, and updated the header comment.
  `pull_request.paths`, `permissions` and `jobs` are byte-identical to the base.
- `tests/test_install_workflow_triggers.py` (new, 7 tests, stdlib-only): parses the `on:` block
  and applies GitHub's documented branch-AND-path semantics. It checks that unrelated main pushes
  start the workflow (the real e7089cbf file set, `docs/runs/README.md`, and badge + report
  paths), that push is main-only with no path filter, that the PR path list is frozen and still
  rejects video-only PRs, and that `workflow_dispatch` exists with no other triggers.
- `scripts/shard-tests.py`: one WEIGHTS line (`0.1`, measured at 0.04 s). This file is outside
  the TASK's owned list. The coordinator approved the addition (msg_b9eca6f68051 and the `ask`
  reply) as required runner wiring, because the shard freshness test fails without it.
- `assets/badges/tests.json`: regenerated, 2241 → 2248 test functions in source.
- The exact-SHA checker is not modified. The existing
  `tests/test_release_check.py::GitHubAnswersAreVerdicts::test_a_workflow_run_is_green_only_at_this_head`
  already rejects a stale-SHA success. It was re-run and passed; see `commands[]`.

## Evidence

| What | Result |
|---|---|
| Failing-first: new test against base `install.yml` | exit 1, 6 failures (`tests.txt`) |
| Negative control, revert `install.yml` to base | exit 1, 6 failures (`negctrl.txt`) |
| Negative control, hand mutant re-adding only `push.paths` | exit 1, 4 failures: all 3 unrelated main pushes rejected, plus `paths` present (`negctrl.txt`) |
| Focused test at head, via `evidence-run.py` | exit 0, wtree = `6092315^{tree}` |
| Stale-SHA checker test at head, via `evidence-run.py` | exit 0 (the first attempt used a wrong class name and exited 1; that record is kept in the ledger) |
| `python3 scripts/validate.py` at head, via `evidence-run.py` | exit 0 |
| Full suite: 4 concurrent CI-equivalent shards, `env -u ORCA_TERMINAL_HANDLE`, pre-commit tree with the same content | 447 / 760 / 646 / 560 tests, all exit 0 (`tests.txt`) |

`release_check.py` was deliberately not re-run: it re-runs the whole suite and needs GitHub
receipts that an unmerged branch cannot have. Raw logs are in
`/tmp/orca-fleet-sweep-20260930/ci-build/` and are not tracked. Manifest:
[`manifest.json`](manifest.json), with `lighting: lit`.

## Parked

- **Live main evidence** (needs-human, gate: human merge). Main Actions have not been observed
  green, and gate 4 has not been observed passing, after this fix. The fix only corrects
  trigger wiring for future pushes. After merge, the merge SHA itself should start `install`,
  because its push is no longer path-filtered. `workflow_dispatch` can backfill a skipped SHA.
- Noticed, not touched: `alert-on-failure.yml` watches workflows by name, and this unit did not
  check whether it covers `install`.

[gh]: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
