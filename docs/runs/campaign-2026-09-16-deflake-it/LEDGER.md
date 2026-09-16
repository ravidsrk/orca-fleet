# Ledger — deflake-it self-test, campaign-2026-09-16-deflake-it

RUN: n/a-solo (no Orca dispatches; all loops coordinator-run in-session) · COORDINATOR: session a4a0c6e3 (Muse Spark) · BASE: campaign/deflake-it-selftest · FORK_POINT: 6390743815f8f435181fa410cce374587128b30a · T0: 2026-09-16T09:55Z · SOURCE: DETECT=CI-history-200 + local-loops · GREEN_STREAK=10-full + 30-module (deviation from 30-full recorded in report) · target residual per-run flake rate: streak-bound p<=26% (N=10) full-suite, p<=9.5% (N=30) fixed-module, 95% conf · WIP: builders=1 reviewers=0

PHASE: DETECT → DIAGNOSE → FIX → PROVE → REFLECT (solo, serial)

Worker TASK pack: matt (diagnosing-bugs feedback-loop-first for DIAGNOSE; tdd red-first for BUILD) — one router, never co-mounted.

| task_id | flake | RATE_RAISED | ROOT_CAUSE | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | RED_BY_REVERT | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | OSError-39 teardown race on temp git repos in test_verify.py gitleaks-PATH leg (CI run 35074600535 @ ec917f50; prior #340 @ 1332614) | t (LOOP-R: bare 200/200, flagged 0/200) | t (bare TemporaryDirectory on 4 temp-repo sites; #340 mitigation covered RepoCase only) | t (fix c8abd8c + badges 5bd2672) | n/a (task forbids PRs; fix commits to BASE directly) | n/a (no PR) | f (solo: no independent reviewer; mechanism loop + gates are the oracle) | n/a (no merge per task; lands as BASE commit) | t (flag-flip: 0/20; restored: 20/20; RATCHET.md) | n/a (solo worktree) | lit | — | docs/runs/campaign-2026-09-16-deflake-it/ |

## PROVE (all at ONE head SHA 5bd2672, serial fresh processes, HEAD-move abort guard)

- Module `test_verify.py` x30 (11:00:55Z→11:16:09Z): pass=30 fail=0 consecutive_green=30
  (`streak-module-30.log`). Bound: residual per-run module flake rate p<=9.5% at 95% conf.
- Full suite x10 (11:17:54Z→11:59:13Z): pass=10 fail=0 consecutive_green=10, 1491 tests/iter
  (`streak-full-10.log`). Bound: residual per-run suite flake rate p<=26% at 95% conf.
- CI leg: OWED (no push per task) — STABLE not claimed.
- Evidence-only commits after the streak (contract freeze 2352cd1, evidence E): test-invisible
  (no suite test reads `docs/runs/campaign-*`; archive gates glob `2*` only) + full-suite
  confirmation re-run on E-content via evidence-run (`tests.txt`, exit 0, wtree-bound).

## Streak resets (each restarts the streak at the new head)

- RESET 1 (2026-09-16 ~11:00Z): full-suite iters 1-2 @ c8abd8c FAILED deterministically (failures=2:
  badge-freshness guard — the +1 pinning test made `assets/badges/tests.json` stale, 1490 vs 1491).
  Not a flake: own change, deterministic, repo-prescribed remedy (`gen-badges.py`). Streak aborted,
  driver + orphan killed, badges regen'd, committed as 5bd2672. Module 30/30 @ c8abd8c VOID for the new
  head (guard reads the badge → suite behavior changed). Retained: `streak-module-30-VOID-c8abd8c.log`,
  `streak-full-10-ABORTED-c8abd8c.log`. PROVE restarts at 5bd2672.

## Detection log

- CI history (gh run list, 200 runs, 2026-09-15→16): 12 validate failures, all attempt=1, each on a
  distinct SHA (no pass-on-retry at same SHA). 11/12 fail at "Validate missions, playbooks, and evals"
  (deterministic content-gate failures on PR branches → clean-sweep territory, out of scope).
  1/12 (run 35074600535, push @ ec917f50) fails in "Secret scan (gitleaks, pinned)": the embedded
  `test_verify.py` run goes FAILED (errors=1) — `test_wtree_equivalence_relaxes_a_content_identical_head_move`
  teardown: `OSError: [Errno 39] Directory not empty: '/tmp/.../.git'`. The same step's full-suite leg
  (no gitleaks on PATH) passed at the same SHA. tests/test_verify.py identical between ec917f50 and tip
  6390743 (git diff empty) → same code fails once in CI, passes everywhere else: intermittent.
- LOOP-F1 (single suspect test x500, macOS, gitleaks installed): 500/500 pass, rate 0.0.
- LOOP-F2 (full test_verify module x30, 10:10:25Z→10:27:10Z): 29/29 valid green; iter 20 INVALID — it imported
  tests/test_verify.py during the coordinator's own ratchet revert window (flag=False on disk) and
  failed exactly as designed (new pinning test, 10/10 OSError trials). Self-inflicted measurement
  contamination, fully characterized; iter discarded, NOT a second flake. (Accidental end-to-end
  confirmation that the pinning test detects the reverted state inside a full-module run.)
  Iters span pre/post-fix file bytes (243 vs 244 tests); all valid iters green either way.
- Prior art: b726431 (2026-09-13, #340) fixed the same signature after CI failure @ 1332614 via gitleaks
  cwd isolation + RepoCase ignore_cleanup_errors; both fixes are ancestors of ec917f50 → recurrence
  through the remaining bare-TemporaryDirectory sites. Second fix on this seam (not third; no reshape
  handoff owed, but the seam smell is noted in REFLECTION.md).

## Exposure audit (bare TemporaryDirectory + temp git repo in tests/test_verify.py — the only module run with gitleaks on PATH in CI)

- L320 FreshnessCheck.test_wtree_equivalence... — OBSERVED failure site. EXPOSED.
- L880 RawByteDigest.test_crlf_contract... — second temp git repo inside a RepoCase test. EXPOSED.
- L1111 GitAuthorityChecks.setUp — temp git repo per test. EXPOSED.
- L1177 InferRepoFromOrigin.setUp — temp git repo per test. EXPOSED.
- L705 ReviewPagination.setUp — tmp holds JSON + fake bin, no git repo. Not exposed.
- L1401/L488 mkdtemp — already ignore-errors / non-repo. Fine.
- Other test modules never run with gitleaks on PATH in CI → outside the observed distribution.
