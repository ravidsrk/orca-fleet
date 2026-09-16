# RV-C2 ledger row (CHARACTERIZE runtime/scripts/verify.py) — fragment for the run ledger

`RUN: reshape-it-unpark-2026-09-16 · UNIT: RV-C2 · PHASE: CHARACTERIZE · TARGET: runtime/scripts/verify.py (outcome-reading seam)`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-C2 | outcome-reading seam net (7 tests) + M2/M2b kills | t | t | n/a (dark-eligible) | waived (dark-eligible lane; executed NC is the oracle) | f (coordinator) | t | dark | - | contract-rv-c2.json@E1, manifest-rv-c2.json, rv-c2-negctrl.txt (M2), rv-c2-m2b.txt, rv-c2-verifier.txt |

- Branch: `reshape/verify-characterize` → PR #464 → base `main`.
- base_sha (C0, frozen contract): `a5a49eb9d7ac8800a10247b186e0154c31237c2e`
- head_sha (H1, test-only net): `de413f7b5d019a9dda3f4fd356ab352d9259a547`
- E1 (evidence): `8284c4c93a6f57fe94a3ed9980c04eb6b95a03dd` · E2 (badge 1510): `c68e4ee5447871f64550a5c88e42b2ed767b080a`
- Pinned mutant M2: `runtime/scripts/verify.py:1166` errors-or-not-failures — KILLED (net RED exit 1, FAILED failures=3, AssertionError); re-kill anchor for RV-D2 carve-out (a) after re-anchor to `runtime/scripts/_verify_sig.py`. Supporting M2b (line 1170): KILLED.
- verify.py: GREEN (exit 0, `--lighting dark-eligible --execute-nc`), see rv-c2-verifier.txt.
- H1 reds (2): both the stale test-count badge, fixed at tip by E2; tip suite Ran 1510 OK.
