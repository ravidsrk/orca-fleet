# Run report — speed-it self-test vs orca-fleet, 2026-09-16

Campaign branch: `campaign/speed-it-selftest`. This is a campaign-evidence
report, not a catalog proof-promotion report: speed-it stays `doctrine-only`
(no tier claimed; no `RUN:` header, no `proof_evidence:` change).

| Field | Value |
|---|---|
| Mission | `speed-it` — source revision `c46d4b3f3371e41408aed19e54476fa194c20b42` |
| Tier claimed | `doctrine-only` (run kind: self-run, campaign evidence) |
| Target | orca-fleet itself: J1 catalog-gates journey |
| Fixed point | BASE `campaign/speed-it-selftest` @ `3383d06` · FORK_POINT `c46d4b3f` · frozen scope `SCOPE.md` |
| Coordinator / workers | workflow-child single-agent · TASK pack `gstack benchmark` (sole router; addy NOT co-mounted) |
| Orca | installed 1.4.203; orchestration dispatch NOT used (single-agent lane, D3) |
| Human gates | budget adoption (D1), no-gh lane (task rules), single-agent lane (D3) — all coordinator-adopted, human re-confirm owed |

## Terminal state: OPTIMIZED-WITH-PARKED (degraded)

One fixable hotspot fixed and kept (H1); J1 still ~223 s over its 30 s budget;
residual breach parked with cause + gate (needs infra change beyond scope).
Never reported as WITHIN-BUDGET.

`| task_id | hotspot | BASELINE | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | BEFORE_AFTER | WT_CLEAN | lighting | park | evidence |`
`| H1 | deny_hook shared read-only fixture | t | t | n/a | n/a | t | t | t | t | lit | | H1-review.txt@3383d06; file {46.24,47.97,48.08}->{42.39,42.52,42.79} |`
Journey park: J1 residual — cause: suite-wide per-test process fan-out;
gate: human infra decision (parallel runner + CI sharding + guard wiring).

## Convergence proof (per clause of the mission's proof section)

- Every journey within budget to its contract OR parked with a reason: J1
  PARKED — `DIAGNOSE.md` (cause) + LEDGER park line (gate). No journey silently dropped.
- Every fix PR: measured before→after to its contract: H1 file-level 3+3 runs,
  ranges non-overlapping, 140/140 OK — `REBENCH.md`, `H1-review.txt` axis 3.
- A fresh worker re-measures a sample: single-agent lane — re-measured by the
  full 5-run journey rebench at the landed SHA (no second identity exists; D3).
- No fabricated metrics: every number pasted from harness logs in this directory
  (spot-checkable via the inventory below).
- CI budgets added so wins don't rot: NOT SATISFIED while parked — guard script
  `bin/measure-j1.sh --budget 30` is retained UNWIRED (wiring a 30 s guard at
  252 s would red main). The unwired guard is part of the park gate, and part of
  why the terminal is degraded rather than WITHIN-BUDGET.
- A fix that changes behavior is a bug the review must catch: H1-review.txt
  axes 1–3 (author-review, independence explicitly absent) + suite green 1490/1490 ×5.
- Manifest names the terminal: `H1-manifest.json` (`parked[]` populated) + this report.

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| SCOPE CONFIRM | freeze J1 + 30 s budget + metric contract | frozen (D1) | SCOPE.md |
| BASELINE | `bin/baseline.sh` (5 runs, pinned) | J1 median 273.93 s, BREACH | BASELINE.md, baseline.log, baseline-*.txt |
| DIAGNOSE | `bin/profile.sh` + `bin/pertest.py` | dominant cause: zero fixture reuse | DIAGNOSE.md, profile.log, pertest-*.log |
| BOOTSTRAP BASE | `preflight.py --base campaign/speed-it-selftest --fork-point c46d4b3f` | OK (exit 0) | preflight.txt |
| FIX H1 | class-shared fixture + config-fold | 140/140 OK | commit 3383d06 |
| REVIEW | author self-review, 3 axes | PASS (no independence) | H1-review.txt |
| RUNTIME-PROVE | journey entry points driven; perf-form NC | green + NC ranges | rebench-*.txt, REBENCH.md |
| LAND | local commit on BASE (no-gh lane) | 3383d06 | git log |
| RE-BENCHMARK | `bin/rebench.sh` (5 runs, pinned) | median 252.69 s; KEEP | REBENCH.md, rebench.log, rebench-*.txt |
| REFLECT | compound-learn proposal | REFLECTION.md (unmerged) | REFLECTION.md |

## WIP-curve protocol row (single-agent lane)

waves=1. No Orca dispatch waves (D3); one sequential unit, builders=1 reviewers=0.

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations |
|---|---|---|---|---|---|
| `wave=1` | `builders=1 reviewers=0` | `throughput=0.9/h` (1 unit kept / 1.1 h wave wall) | `latency_median=n/a-single-agent` `latency_max=n/a-single-agent` | `rework=0` | `freshness=0` |

## Deviations (recorded, not hidden)

- D1: 30 s budget coordinator-adopted from the field-proof plan's stated e.g.
  value; human scope-confirm owed (headless run).
- D2: no-gh local-merge lane (task rules forbid PRs/pushes): H1 landed as a
  local commit; PR_OPEN/BOT n/a; promotion PR owed. `gh` is authenticated; the
  lane is forced by task constraints, not by offline state.
- D3: single-agent lane, no Orca dispatch waves: no second identity exists for
  build-blind review or fresh-worker re-measure; review is author-attested and
  re-measure is harness-repeated. Orca 1.4.203 is installed but no Native Agent
  control tools were granted to this run.
- D4: `browser-drive` inapplicable (no rendered-page oracle); not substituted.
- D5: CI guard retained unwired while the journey is parked (see convergence).
- D6: report format is campaign-evidence (`campaign-*/`), not the dated
  `docs/runs/<date>-<mission>-*.md` proof-promotion shape; no tier claimed.

## Gates (final head)

- `python3 scripts/validate.py` → all 21 missions valid (close content, exit 0).
- `python3 -m unittest discover -s tests` → 1490 OK ×5 at H1 head (rebench:
  254.86/250.06/251.74/250.01/254.02 s) + 1490 OK in 253.723 s at close content.
- `python3 runtime/scripts/proof_status.py --check` → exit 0 (×5 in journey runs + close).
- `ruff check scripts runtime/scripts tests bench demo` → All checks passed (close content).

## Evidence binding

All run-owned evidence lives in this directory and is committed on
`campaign/speed-it-selftest`; the inventory below re-hashes it. No tier is
claimed off this report.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-speed-it/ATTEMPTS.md` | `26f70cf31c5dda1d3ff532df27489c191085a556957cc2fa6410ba3f7d48a74f` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/BASELINE.md` | `b4cfda2f4391c3991f6725622e3e0282ce7986800df747fd00772373222d8473` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/DIAGNOSE.md` | `9a6d4787d2f728aa9633aef6da244c2d0b778875b24d78cb11ffc7b1e904c2a5` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/H1-manifest.json` | `851aa4798fa7e0bdfc3bdebc52b2cefbf64d918f5890ee3718964f814e7a0819` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/H1-review.txt` | `fa3afba0f3215de5b1b269a9a997d8908444bb354d6a895f2e39c7dc1a20de76` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/LEDGER.md` | `8e1f9e6efd2d5754fbe4a0dc5994aec7cdbd788330f9a63b2f675f7a2c668b28` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/REBENCH.md` | `46aba3c6ac164d996d81c5982c35136aa95af220c488dc661ef970f655cfb18f` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/REFLECTION.md` | `6232f038ccc88eebd5789c9bcaa6d84a7aa91c7c1cb57c290c042bd1eb261470` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/SCOPE.md` | `75f7c565a2f56ec37378d542547300fca8fbe10a6f782fc15648d7b4379f367b` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-proof-1.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-proof-2.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-proof-3.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-proof-4.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-proof-5.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-tests-1.txt` | `4c0598c48e73f7cc8f5de2931c97cac9d81921c0191ca9b83b1b6e40f64e0bd4` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-tests-2.txt` | `b72957d003285476bf69fcfaaefd4136483135205d09c74dbbc2f29687fb70eb` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-tests-3.txt` | `13a52734bd82fca89b55fdcc31db54e98ad7e61e1927324e4d0f5be3e70ed91b` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-tests-4.txt` | `3e497f41bb7eaf1d4fd6678e5523022c80c99d0b1013b6049443b5d06f38908a` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-tests-5.txt` | `e5984d8d34e21a09670a9b6e7a1bc574448cd1231d185091013e15b8c7000dd6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-validate-1.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-validate-2.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-validate-3.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-validate-4.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline-validate-5.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/baseline.log` | `f41dab33ce8c946c4713273d45c4755d4e1d4899ffa41b6b5fa3a6ae5dff1d8f` | harness log 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/bin/baseline.sh` | `d10ae5231bd45ab35e2ec18355aadb3638e5e72ebdc86c6a6566a673726277f6` | harness 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/bin/measure-j1.sh` | `d476626600c41b0a2d1fffac79e11d5b5276a5357374216fb54a48e4382e7022` | harness 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/bin/pertest.py` | `aa6702365542a2d73e75de5372393046b55e1e2a6cc37839ef7aafe3732fd0d8` | harness 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/bin/profile.sh` | `b1462e530fbea57c4e754d9f96925a65b0476b74e975303f3bb5bdc543dce8d5` | harness 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/bin/rebench.sh` | `71534d1aaf81a6b0e78b87d60fd50c7c49a18bd5c6b383a96772daf9c8a4ab74` | harness 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/pertest-spawn_worker.log` | `7d16c16e204a8ddea2fa98ef50e8494a4f36c3a9246ced4f25c36ccc341b4f43` | harness log 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/preflight.txt` | `3c67e40a7d58fd6abe9780748c98a07f33883d6f8d479cc76f69fccd331cccc7` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/profile.log` | `ce821c9aeffad91e8af9e1b2a84be4c8d2ef5b666755245fa97bd4dfbc09651a` | harness log 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-proof-1.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-proof-2.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-proof-3.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-proof-4.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-proof-5.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-tests-1.txt` | `fdc6befc71feae5587615cf8ec380341299d1a7b95de33c47a04b92d41b3bd59` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-tests-2.txt` | `1df90e8c205eecc22234dbbbcc0c359e255e11f85726ecadeaa61b5f7bf2ae23` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-tests-3.txt` | `3c399038746e77e1f5f61a6c642db437d812c22e5e49066d39b19568ae0e0aad` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-tests-4.txt` | `b8b6058eca4eac8698e6d78a9bc4f018be773d938b7bebd7db1bd582fea18eaf` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-tests-5.txt` | `dfe457f8c80cb50efc7920756d898d2e322eee2ed722e7dac52867ecbd910803` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-validate-1.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-validate-2.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-validate-3.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-validate-4.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench-validate-5.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | suite transcript 2026-09-16 |
| `docs/runs/campaign-2026-09-16-speed-it/rebench.log` | `736a2ef02e8a59b69df38d8d895e34ff29faab157093bf100a38cd03b5ed04a7` | harness log 2026-09-16 |
