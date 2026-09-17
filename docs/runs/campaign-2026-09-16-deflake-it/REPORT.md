# Run report — deflake-it self-test, 2026-09-16 (campaign)

One CI-only intermittent failure (OSError-39 teardown race, `tests/test_verify.py` gitleaks-PATH leg)
detected in CI history, root-caused with a rate-raising loop, fixed at all four exposed sites, ratcheted
red-by-revert, and streaked locally. CI-leg verification is OWED (task forbade push/PR/merge), so the
mission terminal STABLE is NOT claimed; the run closes FIXED-LOCAL with a promotion-PR-owed OPS item.

RUN: mission=deflake-it tier=doctrine-only inventory_at=05a8b1950ab9466e047d371c34a4380669d6c88f manifest=docs/runs/campaign-2026-09-16-deflake-it/manifest.json verifier=RED waves=1

| Field | Value |
|---|---|
| Mission | `deflake-it` — SKILL unchanged by this run (BASE fork `6390743`) |
| Tier claimed | `doctrine-only` (no catalog promotion: CI leg unverified; this report is recorded history) |
| Target | orca-fleet itself: `tests/` suite (`python3 -m unittest discover -s tests`), main tip `6390743` |
| Fixed point | BASE `campaign/deflake-it-selftest` @ streak head `5bd2672` (fix `c8abd8c` + badge regen) · FORK_POINT `6390743815f8f435181fa410cce374587128b30a` · frozen contract `contract.json@2352cd1` (digest `sha256:c26f40cabe67fb56e8125948d012e6de706702cdae3b6460a6d4ae37199962f1`) · evidence `05a8b19` · report this-file@F (committed last, names E) |
| Coordinator / workers | coordinator session `a4a0c6e3` (Muse Spark), solo in-session, no Orca dispatches · TASK pack `matt` (diagnosing-bugs loop-first + tdd red-first — one router, never co-mounted) |
| Orca | `orca status --json` → `runtime.reachable: true`, app 1.4.203 (live PIN) — checked at BOOTSTRAP (before the fix commit); reachable but undispatched (solo run) |
| Human gates | none taken (no one-way door crossed: test-only fix, no PRs/pushes per task) |

## Terminal state

**FIXED-LOCAL (CI-verify owed)** — not a mission-named terminal: STABLE requires the streak local AND in
CI, and the CI leg cannot run without a push (task constraint). Every detected flake is terminalized
locally (root-caused + fixed + ratcheted + streaked); the CI leg is an explicit OPS item (BACKLOG.md),
never a silent drop. Ledger (deflake canonical row shape):

`RUN n/a-solo · COORDINATOR session a4a0c6e3 · BASE campaign/deflake-it-selftest · FORK_POINT 6390743 · T0 2026-09-16T09:55Z · SOURCE CI-history-200 + local-loops · GREEN_STREAK=10-full + 30-module · WIP builders=1 reviewers=0`

| task_id | flake | RATE_RAISED | ROOT_CAUSE | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | RED_BY_REVERT | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | OSError-39 teardown race, test_verify.py gitleaks-PATH leg (CI 35074600535 @ ec917f50; prior #340 @ 1332614) | t (LOOP-R 200/200 vs 0/200) | t (4 bare TemporaryDirectory temp-repo sites) | t (fix c8abd8c + badges 5bd2672) | n/a (no PRs per task) | n/a | f (solo; oracle = loop + ratchet + gates) | n/a (BASE commit, no merge per task) | t (0/20 vs 20/20) | n/a (solo) | lit | — | `docs/runs/campaign-2026-09-16-deflake-it/` |

## Convergence proof

Mission `## Convergence proof`, clause by clause:

1. *Every detected flake (local AND CI-only) reaches a terminal state: root-caused + fixed + merged
   (with a red-by-revert ratchet) OR quarantined with a human-approved ticket.* F1: root-caused
   (LOOP-R mechanism loop + #340 prior art + exposure audit), fixed (`c8abd8c`: `_temp_repo()` helper +
   4 call-site swaps + pinning regression test; `5bd2672`: badge regen for the +1 test), ratcheted
   (flag-flip 0/20 RED assertion-shaped, restored 20/20 — RATCHET.md). "Merged" is adapted to the task
   constraint: the fix is committed on BASE, not PR-merged; no quarantine needed (no surviving
   undiagnosed flake). Zero other flakes detected (DETECT below).
2. *CI-only flakes: fixed-and-verified-in-CI (green across the same resolved_N consecutive CI triggers,
   `gh run list` pasted) or quarantined.* NOT DISCHARGED — recorded as owed: no CI trigger is possible
   without a push (task constraint). The promotion PR carrying `c8abd8c` must show `validate` green
   (both suite legs) before STABLE is claimable (BACKLOG.md OPS item). Quarantine is the wrong exit:
   the flake is diagnosed and fixed, not surviving.
3. *The streak (timestamps + seeds/orders per run) pasted, local AND CI.* LOCAL streak pasted below
   (module x30 + full-suite x10, all at ONE head SHA, timestamps in streak logs); unittest order is
   fixed (no seed/order axis exists) — recorded, not varied. CI streak: owed (see 2).
4. *Zero retry/rerun wrappers added (grep the diff).* `git diff FORK_POINT..HEAD -- tests/ | grep -inE
   'retry|rerun|retries'` → clean (Pipeline evidence). The fix is teardown-error tolerance on throwaway
   repos (the team's own #340 mitigation), not a retry.
5. *Manifest names STABLE or STABLE-WITH-QUARANTINE.* NOT CLAIMED — manifest names FIXED-LOCAL
   (CI-verify owed). Naming STABLE without the CI leg would be the exact narration-grading the mission
   forbids.

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| DETECT (CI history) | `gh run list --limit 200` + per-run job/step mining | 12 validate failures, all attempt=1 on distinct SHAs; 11 deterministic `validate.py` gate failures (out of scope); 1 test-flake: run 35074600535 @ ec917f50, gitleaks-PATH leg, `test_wtree_equivalence...` teardown OSError 39 | LEDGER.md (detection log) |
| DETECT (local) | LOOP-F1: single suspect test x500 | 500/500 pass, rate 0.0 | `loop-f1-500.log`, `LOOP-F1.sh` |
| DETECT (local) | LOOP-F2: full test_verify module x30 (10:10:25Z→10:27:10Z) | 29/29 valid green; iter 20 invalid (imported the file mid-ratchet; failed exactly as designed) — natural rate 0 | `loop-f2-30.log`, `LOOP-F2.sh` |
| DIAGNOSE | prior-art read (b726431/#340) + exposure audit of bare-TemporaryDirectory temp-repo sites | root cause: 4 bare sites; #340 covered RepoCase only; writer identity still unknown (follow-up) | LEDGER.md, `tests/test_verify.py:52-58` (helper docstring) |
| DIAGNOSE | LOOP-R mechanism loop x200/arm (raced late writer vs teardown) | BARE 200/200 OSError (ENOTEMPTY), FLAGGED 0/200 | `loop-r-200.log`, `loop-r-mechanism.py` |
| BOOTSTRAP | `preflight.py --base campaign/deflake-it-selftest --fork-point 6390743...` | OK (fresh-BASE tip==default warning, expected) | (this section; rerun transcript in manifest commands[]) |
| FIX | `_temp_repo()` + 4 swaps + pinning test | `c8abd8c` (56+/4-, tests/ only); ruff clean; module 244/244 | `git show c8abd8c` |
| FIX (badges) | `gen-badges.py` for the +1 test | `5bd2672` (tests.json 1490→1491); guards green | `git show 5bd2672` |
| RATCHET | flag-flip revert x20 / restore x20 | 0/20 RED (AssertionError) / 20/20 green; restore byte-identical; quoted diff `git apply --check` clean | RATCHET.md + samples |
| RETRY-GREP | `git diff` grep for retry/rerun/retries | clean | (this section) |
| STREAK RESET 1 | full-suite iters 1-2 @ c8abd8c | deterministic RED (failures=2, badge staleness — own change, not a flake); driver killed; 30/30 @ c8abd8c voided; PROVE restarted @ 5bd2672 | `streak-full-10-ABORTED-c8abd8c.log`, `streak-module-30-VOID-c8abd8c.log`, LEDGER.md |
| PROVE (module) | STREAK-module.sh 30 @ 5bd2672 (11:00:55Z→11:16:09Z) | pass=30 fail=0 consecutive_green=30 (244 tests/iter) | `streak-module-30.log`, `STREAK-module.sh` |
| PROVE (full) | STREAK-full.sh 10 @ 5bd2672 (11:17:54Z→11:59:13Z) | pass=10 fail=0 consecutive_green=10 (1491 tests/iter) | `streak-full-10.log`, `STREAK-full.sh` |
| CONFIRM | full suite x1 on evidence content (E + untracked REPORT draft, test-invisible) | exit 0, 1491 tests OK | pasted in Gates (transcript not retained as a file — see Deviations) |
| REFLECT | compound-learn proposal | REFLECTION.md (proposal only, nothing merged) | REFLECTION.md |

## Verifier outcome (recorded exactly)

Graded run (attempt 4, direct — attempts 1-2 went through `evidence-run.py` against the same manifest;
attempts 3-4 direct because a recorder run cannot pre-pin its own tee-target — ordering impossibility,
not a waiver; all four transcripts retained):

`python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-deflake-it/manifest.json --contract-source 'docs/runs/campaign-2026-09-16-deflake-it/contract.json@2352cd124cdacef10f9dff24a252a1f7c7344feb' --contract-digest sha256:c26f40cabe67fb56e8125948d012e6de706702cdae3b6460a6d4ae37199962f1 --unit-class mutation --execute-nc --nc-command 'python3 -m unittest tests.test_verify.FreshnessCheck.test_throwaway_repo_teardown_tolerates_a_late_writer'`

Exit 2 (`verifier-attempt4.txt`, also `verifier.txt` / `verifier-final.txt` / `verifier-attempt3.txt`):

```
FAIL: scope: authoritative criteria not addressed in criteria[] (absent, or addressed != true): ['AC-3']
FAIL: commands ledger: no recorded command with exit 0 whose wtree is head_sha's tree 6d812ca3... — STALE evidence for this head; fail-closed
FAIL: reviewer_mode must be one of [...], got None
FAIL: the hand mutant's diff names 'tests/test_verify.py', which is a TEST path. ... the control must revert the BEHAVIOUR (#280)
FAIL: mutation unit: no pr.number to look up an independent review — unreviewed
verify: 5 invariant(s) failed — unit is NOT done
```

Each FAIL maps to a recorded structural cause (attempts went 9 → 6 → 6 → 5 as pins landed; the five
below are irreducible in this solo/no-PR configuration):

| FAIL | Cause (recorded, not hidden) |
|---|---|
| AC-3 scope | CI leg owed — task forbids push (BACKLOG.md OPS item) |
| wtree STALE | option-A config (fix-step5-headsha precedent): head=code tip `5bd2672`, evidence files in worktree; per-record wtree fingerprints still bind each run to its content |
| reviewer_mode None | solo run, no independent reviewer (DECISIONS.md `deflake-solo-review`); lighting stays `lit`, no waiver taken |
| TEST-path NC bind | file-granularity policy vs a same-file fix+oracle: the flag flip provably preserves the oracle (RED transcript shows the pinning test RAN and asserted — `AssertionError`, not a loader error). Coordinator override with transcript proof; verify.py's re-execution leg refuses on policy. See RATCHET.md. |
| no pr.number | no PRs per task (DECISIONS.md `deflake-no-pr`) |

Attempt history: attempt 1 (recorded): 9 FAILs (4 unreadable-artifact + NC-unreadable — artifacts[]
unfilled); attempt 2 (recorded): 6 (pins landed; mutant-string + TEST-path surfaced); attempt 3
(direct): 6 (mutant-string fixed; verifier-final.txt pin missing); attempt 4 (direct, graded): 5.
A RED is honest — the flagship ship-it run recorded RED for the same solo/no-approver reason.

## WIP-curve protocol row (mutating self-runs)

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations |
|---|---|---|---|---|---|
| `wave=1` | `builders=1 reviewers=0` | `throughput=0.4` | `latency_median=0 latency_max=0` | `rework=0` | `freshness=0` |

Solo serial run, T0 09:55Z → evidence 12:14Z (~2.4h wave wall-clock): one unit (F1) to verified-BUILT
(review leg unfulfillable solo) → throughput 1/2.4 ≈ 0.4/hr. Latency 0/0: no dispatches exist, so no
`worker_done`→verified wait is measurable (degenerate solo value, stated not hidden). No redispatches
(`rework=0`); no PR reviews to void (`freshness=0`). (Not gate-checked: this campaign report is not a
frontmatter-claimed tier report.)

## Deviations and lessons (recorded, not hidden)

- GREEN_STREAK = 10 full-suite + 30 fixed-module instead of the default 30 full-suite (DECISIONS.md
  `deflake-streak-n`): suite wall-clock 4m24s; natural local rate 0 either way; bounds recorded honestly.
  unittest has no seed/order axis — "varied seed/order" is inapplicable, recorded as fixed-order.
- No PR-per-flake pipeline (DECISIONS.md `deflake-no-pr`): task forbids push/PR/merge; fix committed
  directly to BASE; PR_OPEN/BOT/MERGED n/a; CI verification parked as an OPS item, never claimed.
- No build-blind review (DECISIONS.md `deflake-solo-review`): solo run; REVIEWED=f; oracle = mechanism
  loop + executed ratchet + gates; lighting stays `lit` (no waiver taken).
- LOOP-F2 iter 20 invalid: imported the test file mid-ratchet (flag reverted on disk); failed exactly as
  the pinning test is designed to. Discarded with cause, not counted; PROVE streaks supersede DETECT.
- STREAK RESET 1 (deterministic, own change): full-suite iters 1-2 @ `c8abd8c` failed on badge staleness
  (the +1 test); voided the 30/30 module streak @ `c8abd8c` (a guard reads the badge, so suite behavior
  changed) and restarted PROVE @ `5bd2672`. Retained as `*-VOID-c8abd8c.log` / `*-ABORTED-c8abd8c.log`.
- Evidence commits after the streak (`2352cd1` contract freeze, `05a8b19` evidence) are evidence-only:
  `git diff 5bd2672..05a8b19 --name-only` shows run-dir files + `docs/DECISIONS.md` and nothing else,
  and no suite test reads `docs/runs/campaign-*`. The final confirmation full-suite run (exit 0, 1491
  OK) executed on exactly that content; its transcript is pasted in Gates, not retained as a file —
  retaining it would require another commit, regressing forever. The report itself commits last (F),
  naming E in its RUN header.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-deflake-it/BACKLOG.md` | `04d5497ebfcfcd39bae59bcc2c4b819d4fb306718e3b96c968141db93f4ada06` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/LEDGER.md` | `4b03f9e1ddb855431923d70f007ecae7245f7174416b4f7e1603406d8b77254b` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/LOOP-F1.sh` | `76085e7e6cfc4c46fd940e2191870317a81cf8c4ee5ea0b77e6347474450ea27` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/LOOP-F2.sh` | `8cf0af7ff5a3f4bb50bfd7674dae61a19cb590353f3b82fdbcfd370b7fc7b42b` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/RATCHET.md` | `f681fb2e41702e7e273165aecbb1c0bad29bd9c1a13c3d845c817826cac22ced` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/REFLECTION.md` | `9546850d826dc7df11cb148b88aef14e54db3291e991cfe56d58c3f6c783b547` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/STREAK-full.sh` | `608b7c7d0241629d5d9c21970dbf135c2e91ffb596460d6576d0ade16c0f004b` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/STREAK-module.sh` | `6c389c7ee7e6c548d4ac171b9f500b4d755c77ceb7f880114187f9f61be779f2` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/contract.json` | `c26f40cabe67fb56e8125948d012e6de706702cdae3b6460a6d4ae37199962f1` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/loop-f1-500.log` | `51fedfe72ca3fb427d595b4988259dbef85671d80a99c234d50623188e286301` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/loop-f2-30.log` | `4f3f0523b1dfcb1cbf9e2e33434da6570da642bff96417b7f49364e0fd43b5b9` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/loop-r-200.log` | `698c81c0cfe8eda6a4a9aae4696f64e6f951c0e10d83e2005e67350c8870ed2e` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/loop-r-mechanism.py` | `2b58d5c11227f79f091f06ed83b183027242389b578ffc89acd55c3a26d19ed2` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/manifest.json` | `2e8ea600f983f02abdf3ab52b5e0489780c4703d6a59ad1e608f75fe9ca669ca` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/proofstatus.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/ratchet-green-sample.log` | `58d7b5cc014dcb921d12bd4915c8a0a3bd2e8354693a7c6ec1c4c055f2407422` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/ratchet-red-sample.log` | `f7e6c372f1acd0e6aebaff70d3f73918cf69462b9ff05429aa92ba0e41b27f1f` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/streak-full-10-ABORTED-c8abd8c.log` | `659ea88a6faaa3974f4c0c1dcf6daee38294a5691b9e95e7d5dcc63cc4e1bd76` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/streak-full-10.log` | `c432aba50a5ff2ad45093b2fbd9aed4ef77b527e9be05817a46eb06679db6173` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/streak-module-30-VOID-c8abd8c.log` | `a73f666cea6b0d31594fee562ccde9b51f77cd3b4c906d82c73ccd3098a53daf` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/streak-module-30.log` | `07d87625c145fb7bc16901233a818d1bba1b13628765b40310a8d4c5aa6aa9f8` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/tests.txt` | `1eb60a2d1d6531cb4c6758296da181273b46b0166b4a37388e48e989687b4d0a` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/validation.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/verifier-attempt3.txt` | `8e5166a6e47450ac6fc19bbb0184a0dd19aac5f52c34c781fc0cc14ccc43ac25` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/verifier-attempt4.txt` | `14ed4d402dc43238949327571d4ec2873247ee90d2e2c7b0098e9895a2bfaa71` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/verifier-final.txt` | `1127b2a80beb4f360040daa5272eaabbeb560da0a25438b035076cf010af10b6` | run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-deflake-it/verifier.txt` | `e1cb2017455f4c233d757bf36c2000215551ace7445bd449fdc74ebd01414deb` | run 2026-09-16 |

## Gates

Project gates at the evidence content via the installed recorder (same manifest), exact invocations +
exits (transcripts: `validation.txt`, `tests.txt`, `proofstatus.txt`):

`python3 runtime/scripts/evidence-run.py --label validation --manifest docs/runs/campaign-2026-09-16-deflake-it/manifest.json --artifact docs/runs/campaign-2026-09-16-deflake-it/validation.txt -- python3 scripts/validate.py` → exit 0 (`All 21 missions valid; three-layer separation holds; evals valid.`)

`python3 runtime/scripts/evidence-run.py --label tests --manifest docs/runs/campaign-2026-09-16-deflake-it/manifest.json --artifact docs/runs/campaign-2026-09-16-deflake-it/tests.txt -- python3 -m unittest discover -s tests` → exit 0 (`Ran 1491 tests`, `OK`; tree clean after)

`python3 runtime/scripts/evidence-run.py --label proof-status --manifest docs/runs/campaign-2026-09-16-deflake-it/manifest.json --artifact docs/runs/campaign-2026-09-16-deflake-it/proofstatus.txt -- python3 runtime/scripts/proof_status.py --check` → exit 0 (`doctrine-only 19, self-run 2, total 21`)

Final confirmation on exact evidence content E (+ untracked REPORT draft, test-invisible):

`python3 -m unittest discover -s tests` → exit 0 (`Ran 1491 tests in 252.638s`, `OK`)

Secret hygiene: credential-shape grep over the run dir + fix → clean; `gitleaks detect --source .
--log-opts="6390743..HEAD"` → `no leaks found` (re-run after the report commit; see Evidence binding).

## Evidence binding

Evidence commit E: `05a8b1950ab9466e047d371c34a4380669d6c88f` (manifest + all artifacts + LEDGER +
DECISIONS lines). Streak head: `5bd2672f074b6656c6bc7becce43fc50fefd79d1` (fix `c8abd8c` + badges).
`git diff 5bd2672..E --name-only` = run-dir files + `docs/DECISIONS.md` only (verified
DELTA-IS-EVIDENCE-ONLY — no code delta). This report commits last (F) and names E. Secret scans
around F (staged-content pre-F + full-range at F) must read clean; outcomes recorded in the run handoff.
