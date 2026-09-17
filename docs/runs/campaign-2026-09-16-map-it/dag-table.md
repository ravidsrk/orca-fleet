# DAG task-id <-> slice table (prepare-only, frozen for handoff)

Run: `run_b28a7dacdd9e` · 31 tasks · nothing dispatched (map-it commits by FREEZE, not dispatch).

| slice | task_id | deps |
|---|---|---|
| FDN-01 | `task_554b5292eef1` | — |
| INT-01 | `task_fc1132eb37eb` | W1-01, W1-02, W1-03, W1-04, W1-05, W1-06, W1-07, W1-08, W1-09, W2R-10, W2R-11, W2R-12, W2R-13, W2R-14, W2R-15, W2R-16, W2R-17, W2R-18, W2R-19 |
| W1-01 | `task_f7323734aa8b` | FDN-01 |
| W1-02 | `task_56132d7550c1` | FDN-01 |
| W1-03 | `task_d4f396201035` | FDN-01 |
| W1-04 | `task_54799fcf0672` | FDN-01 |
| W1-05 | `task_2c14b044ef64` | FDN-01 |
| W1-06 | `task_94c55ce4d8ac` | FDN-01 |
| W1-07 | `task_06c232338043` | FDN-01 |
| W1-08 | `task_9aca5eeb8f0b` | FDN-01 |
| W1-09 | `task_6503617e0f3b` | FDN-01 |
| W2R-10 | `task_fde5fdd7ed9c` | W2S-10 |
| W2R-11 | `task_109cc60187bb` | W2S-11 |
| W2R-12 | `task_643dbb24a6ed` | W2S-12 |
| W2R-13 | `task_929a753cdb1c` | W2S-13 |
| W2R-14 | `task_630d40b49bb0` | W2S-14 |
| W2R-15 | `task_9212bbf8399d` | W2S-15 |
| W2R-16 | `task_9c8309e9e41c` | W2S-16 |
| W2R-17 | `task_56c319fb50d0` | W2S-17 |
| W2R-18 | `task_603517580530` | W2S-18 |
| W2R-19 | `task_061f5ef84275` | W2S-19 |
| W2S-10 | `task_80ce55f1ba1c` | FDN-01 |
| W2S-11 | `task_34c9c5c8a38a` | FDN-01 |
| W2S-12 | `task_112b98e53699` | FDN-01 |
| W2S-13 | `task_4df2eb11721a` | FDN-01 |
| W2S-14 | `task_9582297d5f91` | FDN-01 |
| W2S-15 | `task_94727c5f947b` | FDN-01 |
| W2S-16 | `task_5bf6fa0f20c5` | FDN-01 |
| W2S-17 | `task_f0bcff738888` | FDN-01 |
| W2S-18 | `task_58b4caab7b39` | FDN-01 |
| W2S-19 | `task_0f2e69113d90` | FDN-01 |
