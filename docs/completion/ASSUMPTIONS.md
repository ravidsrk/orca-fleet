# Assumption ledger

Decisions taken under R7. Alternatives rejected, with why.

| id | phase | decision | rejected | reason |
|---|---|---|---|---|
| A-01 | P0 | PRODUCT = **orca-fleet**, an OSS catalog of outcome-named autonomous fleet missions for the [Orca](https://github.com/stablyai/orca) runtime (Claude Code plugin + symlink-installable `SKILL.md`s + stdlib Python verifier). Not a SaaS, not a hosted app. | Treat as a multi-tenant web product / payments product | README, `.claude-plugin/plugin.json` `description`, and repo layout (skills/playbooks/runtime) agree. Closest to what the code already is. |
| A-02 | P0 | DOMAIN_HINTS = `oss-devtools` + `agent-skills`. Appendix D India-payments / crypto / VDA do not apply. DPDP/IT Act apply only as *GitHub-hosted OSS with no product-side PII store*. | `fintech-india`, `crypto`, `saas`, `consumer-mobile` | No payment rails, no user accounts, no mobile app, no LLM API calls in this repo (grep of runtime/scripts and skills for provider SDKs: none). |
| A-03 | P0 | MODE = `drive`. TARGET_DATE unset → plan in dependency order, no invented dates. | `audit`/`plan` only | User invoked the full driver with no MODE override. |
| A-04 | P1 | Appendix B published weights sum to **105**, not 100. Completion % is `Σ(w×score/4) / Σ(active w) × 100` after dropping N/A angles. | Silently use the table as if it summed to 100 | Would inflate/deflate the informational score. Logged, not "fixed" in the prompt. |
| A-05 | P1 | Angles **6 Data**, **12 AI/LLM layer**, **13 UX & frontend** are N/A. | Score them 0 | No application DB/migrations/PII store in this repo; no LLM SDK imports in runtime/scripts; no HTML/CSS/JS app. Checkable greps in STATUS.md. Weight redistributed via A-04. |
| A-06 | P1 | Local `orca open` is sandbox, not production (R15). We did **not** launch the Orca GUI this run; CF-05 is evidenced as a *failure path* (runtime not running) and gated by H-01. | Force-open the GUI to complete CF-05 in Phase 1 | Opening a desktop app mid-audit is a Human Action-adjacent interruption; the failure path is itself evidence. Reversible: H-01. |
| A-07 | P3 | Launch-gate default angle minima apply: ≥3 on angles 1–9 (minus N/A), ≥2 on 10–17 (minus N/A). No deviation. | Lower minima to match current scores | R13: cannot lower the definition to fit the score. |
| A-08 | P3 | Nine `doctrine-only` missions are **DEFER** (post-launch proof runs), not S0. Catalog completeness ≠ every mission field-proven; the pack already machine-checks honesty. | Require all 13 at self-run before launch | README's own contract: "will not pretend otherwise". Advancing proof tiers is a mission *run*, not a completion-driver feature. |
| A-09 | P4 | P2 "backup restored" for this product = a fresh clone of `main` reproduces CF-01. Git is the store. | Invent a DB backup drill | No product database. Closest to what the code already does. |
| A-10 | P4 | P2 "rollback rehearsed" = `git revert` of a merge on a scratch clone, not a production deploy. | Staging deploy rollback | No hosted service / no staging environment in-repo. |
| A-11 | P5 | Execution starts only after this audit branch's artifacts are committed. One task branch at a time. | Start source edits during Phase 1 | R2. |
| A-12 | P3 | Angle 9 (observability) minimum lowered to ≥1. GitHub Actions is the alert; there is no product runtime to metric. | Keep ≥3 and block launch | Would force inventing a metrics stack for a Markdown+stdlib catalog. Scoped waiver, not a table-wide lowering. |
| A-13 | P3 | Launch-gate "alert fires" is unmet and **does not block catalog GO**. A green Actions run is not a failure-alert proof; redding `main` to prove email is forbidden (R9). | Treat CI success as the alert proof | Greptile P1 on DEFINITION.md. |
