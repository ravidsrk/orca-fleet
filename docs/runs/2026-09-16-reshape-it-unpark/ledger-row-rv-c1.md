# RV-C1 ledger row (CHARACTERIZE scripts/validate.py) — fragment for the run ledger

`RUN: reshape-it-unpark-2026-09-16 · UNIT: RV-C1 · PHASE: CHARACTERIZE · TARGET: scripts/validate.py (count-lint seam)`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-C1 | count-lint seam net (7 tests) + M1/M2 kills | t | t | n/a (dark-eligible) | waived (dark-eligible lane; executed NC is the oracle) | f (coordinator) | t | dark | - | contract-rv-c1.json@64da3d2d, manifest-rv-c1.json, rv-c1-negctrl.txt (M1), rv-c1-m2.txt, rv-c1-verifier.txt |

- Branch: `reshape/validate-characterize` → PR #462 → base `main`.
- base_sha (C0, frozen contract): `bb396297db50c3cc0721d76294d97a144f24781e`
- head_sha (H1, test-only net): `e4bc2b915109c07a63994f4dc5d5cb00af407b83`
- E1 (evidence): `64da3d2d828575f45d1146542cabe0dd7375bd4c` · E2 (badge 1497): `8d79a9baca5ebd892a3a974f42b97f28653cb56b`
- Pinned mutant M1: `scripts/validate.py:905` `_SEP` hyphen-blind — KILLED (net RED exit 1, FAILED failures=1, AssertionError); re-kill anchor for RV-D1 carve-out (a) after re-anchor to `scripts/_countlint.py`.
- verify.py: GREEN (exit 0, `--lighting dark-eligible --execute-nc`), see rv-c1-verifier.txt.
- H1 reds (2): both the stale test-count badge, fixed at tip by E2; tip suite Ran 1497 OK.
