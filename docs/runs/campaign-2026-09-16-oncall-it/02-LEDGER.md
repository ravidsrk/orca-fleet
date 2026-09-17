# oncall-it self-test — ledger

```
RUN · COORDINATOR · BASE origin/main · FORK_POINT c46d4b3f3371e41408aed19e54476fa194c20b42 · T0 2026-09-16 · SOURCE path-set=EMPTY (0 paths, 0 questions) · WIP 0
```

## Path rows (mission canonical shape)

`| task_id | path | questions | SIGNALS | ALERT | RUNBOOK | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | TEST_FIRED | BLIND_OK | NC_RED | WT_CLEAN | lighting | park | evidence |`

*(zero rows — no path froze; PER PATH never started; no dispatch, no worker,
no PR, no merge.)*

## OPS queue

| # | Item | Artifact | Recipient | Verify-complete | State |
|---|---|---|---|---|---|
| OPS-1 | Mission inapplicable: no production path, no staging, no telemetry backend, no observable alert destination in orca-fleet @ `c46d4b3` | `docs/runs/campaign-2026-09-16-oncall-it/01-FREEZE-ASSESSMENT.md` | campaign owner (mission self-test harness) | re-run the three probes in the assessment; all absent ⇒ park stands | OPEN (standing; closes only if a deploy target ever appears — cf. `docs/ops.md` l210-211) |

## DECISIONS log

1. (mechanical) Target pinned to `origin/main` tip `c46d4b3` before any probe;
   branch `campaign/oncall-it-selftest` created from it.
2. (mechanical) Park recorded at task level (mission does not apply) rather
   than OPERABLE-WITH-PARKED: the latter requires ≥1 frozen path with a named
   blocker; the denominator here is empty.
3. (taste) No human questionnaire filed: with no staging/backend/channel in
   existence, there is no question whose answer unblocks a unit — filing one
   would manufacture toil, not a decision.
