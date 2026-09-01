# Gap register

Every standing finding that sits between HEAD and `DEFINITION.md`. Decisions follow the driver rules: S0 → FINISH or CUT; S1 → FINISH (CUT if not on a critical flow); S2/S3 → DEFER unless small and on a critical flow.

| id | source | angle | flow | sev | decision | rationale |
|---|---|---|---|---|---|---|
| G-01 | F-1-02 F-11-01 F-8-02 | 1,11 | CF-05 | S1 | FINISH | CLOSED T-08: Orca reachable; review-it dry run GO at 6ad0e87. |
| G-02 | F-5-04 F-14-04 F-15-02 | 5,14,15 | — | S1 | FINISH | No SECURITY.md / disclosure address. A stranger reporting a vuln has no path. Small, on trust-critical OSS surface. |
| G-03 | F-3-04 F-7-02 R-02 | 3,7 | CF-01 | S2 | FINISH | CI `python-version: "3.x"` is a moving pin. S-sized; on catalog-gates flow. |
| G-04 | F-5-02 | 5 | CF-03 | S2 | FINISH | No `.env.example` for the documented `ORCA_*` gate surface. S-sized. |
| G-05 | F-17-03 | 17 | — | S3 | FINISH | CLOSED T-01: stale #207 worktree+branch removed. |
| G-06 | F-2-04 F-16-03 | 2,16 | — | S3 | FINISH | CLOSED 2026-09-01: 0.6.0; plugin.json = marketplace.json = CHANGELOG heading. |
| G-07 | F-2-03 F-11-02 F-16-03 R-03 | 16,11 | — | S2 | DEFER | Marketplace/indexer submissions. Requires H-02. |
| G-08 | R-01 | 14 | CF-02 | S3 | DEFER | Independent `skills-ref validate` not run. Our validator already enforces the spec fields we rely on. |
| G-09 | F-1-03 A-08 | 1 | — | S3 | DEFER | 9 doctrine-only missions. Honesty is already gated; field-proof is post-launch mission runs. |
| G-10 | F-9-01 F-9-02 | 9 | — | S3 | DEFER | No metrics/alerts beyond GitHub Actions. Acceptable for an OSS CLI until a service exists. |
| G-11 | F-3-03 | 3 | — | S3 | DEFER | ruff not in CI. Social style; adding a linter is a feature-ish policy change. |
| G-12 | F-17-01 F-17-02 | 17 | — | S3 | DEFER | Account inventory + 3-line incident process. File post-launch. |
| G-13 | TODOS.md P2 | 3 | — | S3 | DEFER | Shared validator grammar. Pre-existing P2. |
| G-14 | F-7-03 A-10 | 7 | — | S3 | ACCEPT | Rollback = git revert. Expiry: next time we host a service. Never S0. |

## Cut line

**Above (plan):** G-01, G-02, G-03, G-04, G-05.

**Below:** G-06..G-13 DEFER (issues filed) · G-14 ACCEPT.

No CUT (nothing half-built to delete). No ACCEPT at S0.

## Post-launch issues (filed 2026-09-01)

| gap | issue |
|---|---|
| G-06 | https://github.com/ravidsrk/orca-fleet/issues/209 |
| G-07 | https://github.com/ravidsrk/orca-fleet/issues/210 |
| G-08 | https://github.com/ravidsrk/orca-fleet/issues/211 |
| G-09 | https://github.com/ravidsrk/orca-fleet/issues/212 |
| G-10 | https://github.com/ravidsrk/orca-fleet/issues/213 |
| G-11 | https://github.com/ravidsrk/orca-fleet/issues/214 |
| G-12 | https://github.com/ravidsrk/orca-fleet/issues/215 |
| G-13 | https://github.com/ravidsrk/orca-fleet/issues/216 |
