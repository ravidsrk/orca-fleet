# Ledger — prove-it campaign self-test, 2026-09-16

RUN: - (solo; no Orca dispatch — deviation D1) · COORDINATOR: workflow-child session 46f15471 (Muse Spark) · BASE: campaign/prove-it-selftest · FORK_POINT: c46d4b3f3371e41408aed19e54476fa194c20b42 · T0: 2026-09-16T13:17:19Z (scope freeze) · SOURCE: contract PF-3 sha256:9c1ff32569d64b2ec9f0ab8cec7d8ca026243a1192b97d3c152f3d91ed049a62 · WIP: builders=1 reviewers=1

PHASE: PROVING

- 2026-09-16: BUILD_DONE=t — net `OracleScopeCharacterizationGateTest` (3 tests) committed test-only as `18ee8633` (+54, `tests/test_verify.py` only); class GREEN exit 0 (`audit-clean.txt`); mutation audit 3/3 KILLED at `assertEqual` (`audit-m1/m2/m3-red.txt`, harness intact); `verify.py` restored byte-identical (`cmp` clean).
- 2026-09-16: REVIEWED=t — build-blind cross-vendor review GO round 1 @ `reviewed_sha == 18ee8633` (`review.txt`: blind expectation + judgment, prompts+replies verbatim; G1→sibling-wave follow-up, T1→answered by m2, appendix→corroborated).

TASK pack: matt (`tdd` builder method — one router, never co-mounted).

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| n/a (solo) | PF-3 characterization gate (verify.py:1012-1013) | t (`18ee8633`) | n/a (no-gh: task forbids PRs/push/merge — local commits only) | n/a (no PR) | t (blind GO round 1 @ `18ee8633`) | n/a (no merge per task; branch holds the commits) | n/a (solo worktree) | dark-eligible | — | `docs/runs/campaign-2026-09-16-prove-it/manifest.json` |

Flag advances are edited in the same step as their verify; narration elsewhere does not advance them.
