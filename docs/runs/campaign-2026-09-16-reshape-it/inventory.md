# reshape-it SCAN — churn-weighted shallowness inventory (self-test vs orca-fleet)

- Mission: `reshape-it` @ catalog HEAD `c46d4b3f3371e41408aed19e54476fa194c20b42`
- Target: orca-fleet itself (self-run), window `--since=90d`, probed 2026-09-16T13:02:07Z
- Probe script: [scan.sh](scan.sh) (committed, re-runnable); raw output: [scan-transcript.txt](scan-transcript.txt)
- Modules probed: 73 (every tracked `*.py`); YAGNI cut: empty — all 73 have churn > 0

## Method (SKILL § SCAN, verbatim probes)

- `CHURN = git log --since=90d --format=%h -- <module> | wc -l` (commits touching the module)
- `WIDTH = grep -cE '^(def |class |async def |[A-Z_]+ =)' <module>` plus `__all__` entry count
  (no probed module defines `__all__`, so WIDTH is the top-level-symbol count throughout)
- `DEPTH = wc -l` on the implementation file
- `FAN-IN = git grep -lE '(from|import|require).*<module-name>' | wc -l` over tracked files
- Rank: `CHURN × WIDTH ÷ max(DEPTH/100, 1)`, FAN-IN breaks ties
- Corroborated by independent re-probe: `scripts/validate.py` → 46/73/1110/50 and
  `runtime/scripts/verify.py` → 58/92/2145/53, both matching the transcript exactly.

Probe limits (the numbers order the inventory; they do not certify it): FAN-IN is a
substring match, so short names inflate (`gen` → 109, `gate` → 96 — mostly words like
"general"/"aggregate", not imports); WIDTH counts module-level `CONSTANT =` assignments as
interface width. Neither affects the head of the production ranking.

## Production surface (the deepen-able set: `scripts/` + `runtime/scripts/`)

`scripts/install.sh` is shell and outside the Python WIDTH probe; it is not ranked.

| Rank | Module | CHURN | WIDTH | DEPTH | FAN-IN | SCORE |
|---|---|---|---|---|---|---|
| 1 | `scripts/validate.py` | 46 | 73 | 1110 | 50 | 302.52 |
| 2 | `runtime/scripts/verify.py` | 58 | 92 | 2145 | 53 | 248.76 |
| 3 | `scripts/eval.py` | 35 | 72 | 1314 | 22 | 191.78 |
| 4 | `runtime/scripts/run_report.py` | 26 | 53 | 871 | 17 | 158.21 |
| 5 | `scripts/gen-badges.py` | 7 | 26 | 277 | 6 | 65.70 |
| 6 | `scripts/bundle.py` | 9 | 26 | 423 | 13 | 55.32 |
| 7 | `runtime/scripts/floor_guard.py` | 8 | 34 | 506 | 2 | 53.75 |
| 8 | `runtime/scripts/decisions.py` | 6 | 33 | 420 | 5 | 47.14 |
| 9 | `runtime/scripts/egress.py` | 6 | 24 | 357 | 8 | 40.34 |
| 10 | `runtime/scripts/evidence-run.py` | 10 | 11 | 292 | 5 | 37.67 |
| 11 | `runtime/scripts/diff_scope.py` | 5 | 22 | 308 | 1 | 35.71 |
| 12 | `runtime/scripts/pm.py` | 9 | 5 | 146 | 12 | 30.82 |
| 13 | `runtime/scripts/inventory.py` | 4 | 22 | 313 | 18 | 28.12 |
| 14 | `runtime/scripts/preflight.py` | 7 | 12 | 323 | 6 | 26.01 |
| 15 | `runtime/scripts/ed25519.py` | 2 | 19 | 159 | 4 | 23.90 |
| 16 | `runtime/scripts/gate-batch.py` | 3 | 39 | 644 | 2 | 18.17 |
| 17 | `runtime/scripts/sandbox_doctor.py` | 3 | 9 | 151 | 0 | 17.88 |
| 18 | `runtime/scripts/dispatch-sign.py` | 4 | 9 | 214 | 2 | 16.82 |
| 19 | `runtime/scripts/proof_status.py` | 3 | 10 | 232 | 2 | 12.93 |
| 20 | `runtime/scripts/watchdog.py` | 2 | 26 | 470 | 4 | 11.06 |
| 21 | `scripts/bind_check.py` | 2 | 17 | 320 | 1 | 10.62 |
| 22 | `runtime/scripts/guard_text.py` | 1 | 18 | 217 | 1 | 8.29 |

The head of the ranking confirms the catalog's own field-proof prediction (`docs/runs/README.md`:
"likely `runtime/scripts/verify.py` / `scripts/validate.py`").

## Out of the deepen-able surface (published, not bounded — the human decides)

- `tests/*.py` (39 files): the characterization net itself, not deepening targets. Reshaping
  a test module is not a module-deepening under this mission (unit = one interface shrink at
  one seam of a lived-in module, oracle = the net). Ranked in the full table for completeness.
- `bench/vf-bench/*.py`, `assets/diagrams/generator/*.py`, `demo/negative-control/*.py`,
  `docs/reports/**/*.py` (12 files): auxiliary tooling and one-off evidence probes, not
  lived-in interfaces. `bench/vf-bench/vfbench.py` scores 111.72 on churn but is benchmark
  harness, not product surface.

## YAGNI cut

Empty. Every tracked Python module changed at least once in the 90-day window (1215 commits
in window), so no module drops out for stability. The cut is recorded, not skipped.

## Full ranked table (all 73 modules; verbatim from scan-transcript.txt)

```text
MODULE                                              CHURN  WIDTH   DEPTH  FAN-IN     SCORE
scripts/validate.py                                    46     73    1110      50    302.52
runtime/scripts/verify.py                              58     92    2145      53    248.76
scripts/eval.py                                        35     72    1314      22    191.78
runtime/scripts/run_report.py                          26     53     871      17    158.21
bench/vf-bench/vfbench.py                              16     28     401       2    111.72
tests/test_verify_gate.py                              20     24     538       0     89.22
tests/test_evals.py                                    43     33    1621       4     87.54
tests/test_verify.py                                   59     40    2982       4     79.14
scripts/gen-badges.py                                   7     26     277       6     65.70
tests/test_architecture.py                             55     13    1093       1     65.42
tests/test_docs_navigation.py                          44     15    1181       3     55.88
tests/test_orphan_wiring.py                            21     19     715       0     55.80
scripts/bundle.py                                       9     26     423      13     55.32
assets/diagrams/generator/wire_docs.py                  4     21     155       0     54.19
runtime/scripts/floor_guard.py                          8     34     506       2     53.75
tests/test_validate.py                                 35     16    1166       0     48.03
runtime/scripts/decisions.py                            6     33     420       5     47.14
runtime/scripts/egress.py                               6     24     357       8     40.34
tests/test_vfbench.py                                  20      9     457       0     39.39
runtime/scripts/evidence-run.py                        10     11     292       5     37.67
runtime/scripts/diff_scope.py                           5     22     308       1     35.71
runtime/scripts/pm.py                                   9      5     146      12     30.82
tests/test_negative_control.py                          5      6      99       0     30.00
runtime/scripts/inventory.py                            4     22     313      18     28.12
tests/test_run_report.py                               40      9    1309       2     27.50
tests/test_evidence_run.py                             12     15     657       2     27.40
runtime/scripts/preflight.py                            7     12     323       6     26.01
tests/test_deny_hook.py                                22     17    1496       0     25.00
tests/test_pins.py                                      4     18     293       1     24.57
runtime/scripts/ed25519.py                              2     19     159       4     23.90
tests/test_floor_guard.py                               7     16     491       1     22.81
tests/test_inventory.py                                 5     15     339       0     22.12
runtime/scripts/gate-batch.py                           3     39     644       2     18.17
runtime/scripts/sandbox_doctor.py                       3      9     151       0     17.88
runtime/scripts/dispatch-sign.py                        4      9     214       2     16.82
assets/diagrams/generator/gen.py                        3      8     153     109     15.69
bench/vf-bench/gate.py                                  2     11     143      96     15.38
tests/test_spawn_worker.py                             16      9     971       0     14.83
tests/test_decisions.py                                 5     12     426       0     14.08
tests/test_preflight.py                                 4     10     284       0     14.08
tests/test_diff_scope.py                                4     13     373       0     13.94
runtime/scripts/proof_status.py                         3     10     232       2     12.93
tests/test_vfbench_gate.py                              2      7     111       0     12.61
runtime/scripts/watchdog.py                             2     26     470       4     11.06
tests/test_gate_batch.py                                3     23     639       0     10.80
scripts/bind_check.py                                   2     17     320       1     10.62
tests/test_pm.py                                        3      7     203       0     10.34
tests/test_ed25519.py                                   2      5     106       0      9.43
docs/reports/chaining-2026-09-16/leg1/seed-notes.py     1     10     112       0      8.93
tests/test_sandbox_doctor.py                            3      4     136       0      8.82
tests/test_wire_docs.py                                 2      5     115       0      8.70
runtime/scripts/guard_text.py                           1     18     217       1      8.29
tests/test_watchdog.py                                  2     16     396       0      8.08
tests/test_bind_check.py                                2     15     391       0      7.67
tests/test_migration_walkthrough.py                     3      3     119       0      7.56
docs/reports/release-20260912/pin/check-correction.py   2      7     205       1      6.83
tests/test_egress.py                                    3      9     399       0      6.77
assets/diagrams/generator/specs.py                      2      6     179      10      6.70
tests/test_proof_status.py                              3      3     135       0      6.67
tests/test_dispatch_sign.py                             2      6     186       0      6.45
tests/test_one_way_doors.py                             1     10     157       0      6.37
tests/test_call_for_runs.py                             1      6      91       0      6.00
tests/test_hitl_loop.py                                 1      7     131       0      5.34
tests/test_repo_hygiene.py                              3      6     343       0      5.25
docs/reports/chaining-2026-09-16/leg1/seed-test_notes.py 1     5      45       0      5.00
tests/test_governance_commands.py                       2      5     203       0      4.93
tests/test_guard_text.py                                1      9     194       0      4.64
assets/diagrams/generator/specs_missions.py             3      3     202       1      4.46
assets/diagrams/generator/specs_new.py                  2      2      91       1      4.00
tests/test_bundle.py                                    5      3     529       0      2.84
assets/diagrams/generator/specs_light.py                1      2      13       1      2.00
demo/negative-control/selfscore.py                      1      1      36       0      1.00
docs/reports/release-20260912/claims/archive-v1-eb7901b/unit/claims_probe.py 1 1    81       0      1.00
```
