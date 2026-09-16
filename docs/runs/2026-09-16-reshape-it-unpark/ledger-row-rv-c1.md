# RV-C1 ledger row (CHARACTERIZE scripts/validate.py) — fragment for the run ledger

`RUN: reshape-it-unpark-2026-09-16 · UNIT: RV-C1 · PHASE: CHARACTERIZE · TARGET: scripts/validate.py (count-lint seam)`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-C1 | count-lint seam net (7 tests) + M1/M2 kills | t | t | n/a (dark-eligible) | waived (dark-eligible lane; executed NC is the oracle) | f (coordinator) | t | dark | - | contract-rv-c1.json v3@b7ddfab6, manifest-rv-c1.json, rv-c1-negctrl-r2.txt (M1), rv-c1-m2-r2.txt, rv-c1-m3.txt, rv-c1-verifier.txt |

- Branch: `reshape/validate-characterize` → PR #462 → base `main`.
- Round 1: base C0 `bb396297` · head H1 `e4bc2b91` (test-only net) · E1 `64da3d2d` (evidence) · E2 `8d79a9ba` (badge 1497) · E3 `6e3cc045` (close). H1 reds (2): both the stale test-count badge, fixed at tip by E2; tip suite Ran 1497 OK.
- Round 2 (Greptile P2: pin `*`/`_` emphasis joints): base E3 `6e3cc045a5169a1f1a72c4eaec970ed7253f4a54` · head H2 `c5e09b9bb220b3ab641960621ce8a12761621542` (test-only amendment; 7 methods, count unchanged). H2 fully green (suite Ran 1497 OK); criteria text byte-identical to the v1 freeze (verified against C0 bytes).
- Pinned mutant M1: `scripts/validate.py:905` `_SEP` hyphen-blind — KILLED at both heads (net RED exit 1, FAILED failures=1, AssertionError); re-kill anchor for RV-D1 carve-out (a) after re-anchor to `scripts/_countlint.py`. Supporting M2 (backtick-blind) + M3 (star-blind, round 2): KILLED.
- verify.py: GREEN (exit 0, `--lighting dark-eligible --execute-nc`), see rv-c1-verifier.txt.
- Round-2b fix: NC artifacts renamed to `-r2` names — the verifier reads the blob TRACKED at head (round-1 bytes in H2's ancestry), so round-2 bytes must live at an untracked path + artifacts[] pin (prove-it PF-2 `negctrl-rerun.txt` precedent). Contract v3 bytes authorize the r2 content (sha unchanged by the rename).
- E6 (Greptile P2s 4030446451/4030446455): contract v4 fixes filename pointers to the -r2 names (criteria/coords/sha unchanged); the exit-2 verifier-round-2 record removed (its artifact bytes were overwritten by the GREEN re-run — explained absence beats a dangling pointer; see removed_records).
