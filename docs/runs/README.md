# Run archive

Recorded mission runs — the evidence behind each mission's `proof:` status. A run report
is what advances a mission past `doctrine-only`: `self-run` (run against this catalog) or
`external-run` (run against a repo that is not this catalog). Each report carries the fixed
point, the ledger, per-phase evidence, a run-close sha256 integrity inventory (inline, or
retained at a named location when the run's artifacts live outside this repo), and the
deviations that happened — recorded, not hidden.

`Binds?` is the only column that moves a mission's `metadata.proof`: **yes** means
`runtime/scripts/run_report.py` re-derives everything this report rests on — a real
`verify.py … --manifest` invocation in the body, the graded manifest inside this run's own
directory and pinned by the inventory, and every one of this run's artifacts hashing true at the
commit the `RUN:` header names. **no** means the run happened and something it rests on cannot be
re-derived here — history, kept, claiming nothing.

Nothing in the archive currently reads **yes**. That is the honest state, not a broken gate: three
runs kept their artifacts outside this repository, and the fourth kept its artifacts but not its
verifier transcript. The mechanism is exercised by `tests/test_run_report.py`, which builds real
git repositories and includes a fully bound positive case alongside a dozen refused ones.

| Date       | Mission     | Target                        | Ran as       | Binds? | Outcome |
|------------|-------------|-------------------------------|--------------|--------|---------|
| 2026-07-13 | [clean-sweep](2026-07-13-clean-sweep-self-run.md) | this repo (doc-claims) | self-run | no — artifacts in the coordinator run dir | DRY (6 false claims fixed) |
| 2026-07-13 | [review-it](2026-07-13-review-it-external-run.md)  | garrytan/gstack PR #2252 | external-run | no — artifacts in the coordinator run dir | NO-GO (conditional, 0 Critical) |
| 2026-07-16 | [oss-contribute](2026-07-16-oss-contribute-external-run.md) | dodopayments/chimely (tracker) | external-run | no — artifacts in the fork worktree | CONTRIBUTED-WITH-PARKED (5 PRs, 4 assists) |
| 2026-07-17 | [clean-sweep](2026-07-17-clean-sweep-tracker-self-run.md) | this repo (tracker, 26 issues) | self-run | no — no inventory block | DRY-WITH-PARKED (22 closed, 4 parked) |
| 2026-08-28 | [ship-it](2026-08-28-ship-it-self-run.md) | this repo (proof-status slice) | self-run | no — 5/5 hashes re-derive at `748b328`, but the verifier transcript was never recorded | PROMOTION_READY (BUILT + promotion PR open) |
| 2026-09-09 | [clean-sweep](2026-09-09-clean-sweep-tracker.md) | this repo (tracker, 6 issues) | self-run | no — inventory pinned to a moved tree | DRY-WITH-PARKED (5 closed, 1 needs-human) |

Proof status across the catalog is validator-enforced: a mission cannot claim a tier
above `doctrine-only` without a `proof_evidence:` path that resolves to a report here whose
inventory re-hashes at the commit its `RUN:` header names (`runtime/scripts/run_report.py`) —
`scripts/validate.py` also requires the filename to carry the mission name and the body to name
it. Start a new report from [TEMPLATE.md](TEMPLATE.md).

Every mutating self-run records the WIP-curve protocol row from `attention-budget.md`
(WIP setting, builder throughput, verification latency, rework rate, freshness
violations). The 2026-08-28 ship-it self-run above records a first *qualitative* observation
(it reached verified-BUILT, not verified-CLOSED) — not a protocol-compliant point; the caps stay
ASSERTED until ≥3 runs at differing WIP settings measure verified-CLOSED-per-hour throughput.

## Field-proof plan (#212)

Thirteen missions are `doctrine-only`. Each advance is a **mission run** — Orca up, human gates
answered, a report filed from [TEMPLATE.md](TEMPLATE.md) — never a relabel: the scoped
demonstrations under [`docs/reports/`](../reports/) say so themselves. Targets that make each run
concrete, self-run candidates first:

| Mission | Target that exists today | Tier | Terminal to show | What blocks it |
|---|---|---|---|---|
| map-it | this catalog (report-only: planning branch, freeze commit, verified DAG) | self-run | `MAPPED` | Orca only |
| attest-it | this catalog against the agentskills.io spec at a digest — obligations = the spec's required fields, evidence = `scripts/validate.py` checks | self-run | `CONFORMANT` (or `-WITH-GAPS`) | Orca; a frozen catalog digest |
| harden-it | `runtime/scripts/verify.py`, `dispatch-sign.py`, `verify-gate.sh` — audit → PoC scenario → routed profile → fix → re-attack; the [gitleaks control](../reports/harden-it-externalrun/README.md) is one unit | self-run | `CLEAN` | Orca; the PoC-routing gate (human) |
| prove-it | `scripts/validate.py` + `runtime/scripts/verify.py` critical surface — multi-criterion audit + builder wave; the [PF-1 control](../reports/prove-it-selfrun/README.md) is one unit | self-run | `COVERED` | Orca; WIP-curve row (mutating self-run) |
| speed-it | the catalog-gates journey (`validate.py` + `tests/` + `proof_status`), declared budget e.g. ≤30s wall, guard in CI at the declared budget | self-run | `WITHIN-BUDGET` | Orca; a declared budget (human) |
| root-cause | the next real defect filed here, or an open bug in a small OSS repo | self-run or external-run | `DIAGNOSED` | a live bug + Orca |
| access-it | needs a web UI — an external repo with an axe-core baseline | external-run | `CONFORMANT` (or `-WITH-MANUAL-PARKED`) | a target + Orca |
| deflake-it | needs an observed flake — this suite ran flake-free in both audits; an external suite with a known flake | external-run | `STABLE` | a target + Orca |
| modernize-it | needs a lockfile — this catalog has no dependencies; an external repo with one | external-run | `CURRENT` | a target + Orca |
| pin-it | this catalog's `runtime/*.md` + `runtime/scripts/` against the installed Orca CLI — the audit's §2.1 claim inventory is the pre-cut backlog | self-run | `PINNED` (or `-WITH-PARKED`) | Orca (the re-witness oracle) |
| floor-it | this catalog: dimensions = test suite, validate.py, ruff, badge freshness — most are already wired, so the run is prove-fires + GUARD (injected violation must RED each gate; the check_constraints diff-watch is new) | self-run | `FLOORED` | Orca; the freeze gate (human) |
| reshape-it | this catalog's churn-hot modules (`git log --since=90d`) — likely `runtime/scripts/verify.py` / `scripts/validate.py`; characterization net pinned first | self-run | `RESHAPED` | Orca; the CONFIRM-SURFACE gate (human) |
| field-test-it | needs a device/emulator app — an external mobile repo | external-run | `FIELD-PROVEN` | a target + a paired device |

A run's report goes through the same gates as any change (PR, review bot, `validate.py`), and
`proof_status --check` keeps every tier honest until the report lands.
