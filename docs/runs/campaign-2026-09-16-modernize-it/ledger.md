# Ledger — modernize-it self-test campaign 2026-09-16

RUN: - (solo coordinator outside any Orca terminal; `orca orchestration run-create` refused `no_active_sender_terminal`; zero dispatches planned) · COORDINATOR: workflow-child session 46f45671 (Muse Code, no Orca terminal handle) · BASE: campaign/modernize-it-selftest-BASE · FORK_POINT: c46d4b3f3371e41408aed19e54476fa194c20b42 · T0: 2026-09-16T12:25:39Z · SOURCE: inventory docs/runs/campaign-2026-09-16-modernize-it/inventory.md @ sha256:161e04fdf5d952f7 · WIP: builders=1 reviewers=0

PHASE: BUILDING

Lane: task-constrained no-gh local-merge (task forbids push/PRs/merge-to-default; gh reads allowed, no PR objects).
Preflight: `python3 runtime/scripts/preflight.py --base campaign/modernize-it-selftest-BASE --fork-point c46d4b3f3371e41408aed19e54476fa194c20b42` → exit 0 (BASE tip == default tip warning, expected for fresh BASE).
Worker TASK pack: addy (deprecation-and-migration) — single router; no second pack mounted. Solo execution: coordinator performs builder steps directly.

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| solo-u1 (no Orca dispatch; solo coordinator) | ci-tools ruff 0.16.5→0.16.7 | f | n/a (no-gh: local-merge) | n/a (no PR → no bot) | f | f | n/a (no unit worktree; solo) | dark-eligible | — | manifest-u1.json |

## Notes

- 2026-09-16T12:25:39Z T0. BASE created at origin/main tip c46d4b3 (Merge PR #445).
- Scope decision (mechanical, logged to docs/DECISIONS.md): mission APPLIES — `.github/ci-tools.lock` (#301, 2026-09-11) postdates the runs-README "no dependencies" row (2026-09-02); that row is stale. Target surface: ci-tools.lock + GH Actions pins + gitleaks pin + python pin. `runtime/pins.json` is OUT of scope (pin-it / upstream-audit owned: different unit + oracle).

- Contract U1 frozen: docs/runs/campaign-2026-09-16-modernize-it/contract.json @ sha256:cf6310703354fae1599e5af1b19374fced91973e4c7aab95f38ee8aad4e44f45 (AC-1..AC-6; AC-6 added pre-commit when test_pins PINNED + CONTRIBUTING call sites were found; inventory corrected in the same pre-freeze pass).
