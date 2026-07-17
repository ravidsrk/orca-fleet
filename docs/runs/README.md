# Run archive

Recorded mission runs — the evidence behind each mission's `proof:` status. A run report
is what advances a mission past `doctrine-only`: `self-run` (run against this catalog) or
`external-run` (run against a repo that is not this catalog). Each report carries the fixed
point, the ledger, per-phase evidence, a run-close sha256 integrity inventory (inline, or
retained at a named location when the run's artifacts live outside this repo), and the
deviations that happened — recorded, not hidden.

| Date       | Mission     | Target                        | Tier         | Outcome |
|------------|-------------|-------------------------------|--------------|---------|
| 2026-07-13 | [clean-sweep](2026-07-13-clean-sweep-self-run.md) | this repo (doc-claims) | self-run     | DRY (6 false claims fixed) |
| 2026-07-13 | [review-it](2026-07-13-review-it-external-run.md)  | garrytan/gstack PR #2252 | external-run | NO-GO (conditional, 0 Critical) |
| 2026-07-16 | [oss-contribute](2026-07-16-oss-contribute-external-run.md) | dodopayments/chimely (tracker) | external-run | CONTRIBUTED-WITH-PARKED (5 PRs, 4 assists) |
| 2026-07-17 | [clean-sweep](2026-07-17-clean-sweep-tracker-self-run.md) | this repo (tracker, 26 issues) | self-run | DRY-WITH-PARKED (22 closed, 4 parked) |

Proof status across the catalog is validator-enforced: a mission cannot claim a tier
above `doctrine-only` without a `proof_evidence:` path that resolves to a report here.
