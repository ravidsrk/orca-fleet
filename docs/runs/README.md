# Run archive

Recorded mission runs — the evidence behind each mission's `proof:` status. A run report
is what advances a mission past `doctrine-only`: `self-run` (run against this catalog) or
`external-run` (run against a repo that is not this catalog). Each report carries the fixed
point, the ledger, per-phase evidence, a run-close sha256 integrity inventory, and the
deviations that happened — recorded, not hidden.

| Date       | Mission     | Target                        | Tier         | Outcome |
|------------|-------------|-------------------------------|--------------|---------|
| 2026-07-13 | [clean-sweep](2026-07-13-clean-sweep-self-run.md) | this repo (doc-claims) | self-run     | DRY (6 false claims fixed) |
| 2026-07-13 | [review-it](2026-07-13-review-it-external-run.md)  | garrytan/gstack PR #2252 | external-run | NO-GO (conditional, 0 Critical) |

Proof status across the catalog is validator-enforced: a mission cannot claim a tier
above `doctrine-only` without a `proof_evidence:` path that resolves to a report here.
