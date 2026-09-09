# Gap register

Every standing finding that sits between HEAD and `DEFINITION.md`. Decisions follow the driver rules: S0 → FINISH or CUT; S1 → FINISH (CUT if not on a critical flow); S2/S3 → DEFER unless small and on a critical flow. Run 2 deviation: G-15 and G-17 are FINISH by a one-line Human Action although off-flow (A-23).

| id | source | angle | flow | sev | decision | rationale |
|---|---|---|---|---|---|---|
| G-01 | F-1-02 F-11-01 F-8-02 | 1,11 | CF-05 | S1 | FINISH | CLOSED T-08: Orca reachable; review-it dry run GO at 6ad0e87. |
| G-02 | F-5-04 F-14-04 F-15-02 | 5,14,15 | — | S1 | FINISH | No SECURITY.md / disclosure address. A stranger reporting a vuln has no path. Small, on trust-critical OSS surface. |
| G-03 | F-3-04 F-7-02 R-02 | 3,7 | CF-01 | S2 | FINISH | CI `python-version: "3.x"` is a moving pin. S-sized; on catalog-gates flow. |
| G-04 | F-5-02 | 5 | CF-03 | S2 | FINISH | No `.env.example` for the documented `ORCA_*` gate surface. S-sized. |
| G-05 | F-17-03 | 17 | — | S3 | FINISH | CLOSED T-01: stale #207 worktree+branch removed. |
| G-06 | F-2-04 F-16-03 | 2,16 | — | S3 | FINISH | CLOSED 2026-09-01: 0.6.0; plugin.json = marketplace.json = CHANGELOG heading. |
| G-07 | F-2-03 F-11-02 F-16-03 R-03 | 16,11 | — | S2 | FINISH | CLOSED #222: index check recorded. Remaining aggregator submits are H-02 only, not this gap. |
| G-08 | R-01 | 14 | CF-02 | S3 | FINISH | CLOSED #221: skills-ref extras allowlisted; a fourth top-level field fails the catalog. |
| G-09 | F-1-03 A-08 | 1 | — | S3 | DEFER | 9 doctrine-only missions. Honesty is already gated; field-proof is post-launch mission runs. Follow-up (#212): `docs/runs/TEMPLATE.md` + a per-mission field-proof plan in the archive index; still one mission run per advance. |
| G-10 | F-9-01 F-9-02 F-9-03 | 9 | — | S3 | FINISH | CLOSED 2026-09-02: T-10 workflow on `main` (#228); T-11 drill run 33626502338 filed and closed `ci-failure` issue #229. Was DEFER. |
| G-11 | F-3-03 | 3 | — | S3 | FINISH | CLOSED #220: CI ruff 0.16.5 on E9/F63/F7/F82 only. |
| G-12 | F-17-01 F-17-02 | 17 | — | S3 | FINISH | CLOSED #219: docs/ops.md inventory + incident process. |
| G-13 | TODOS.md P2 | 3 | — | S3 | FINISH | CLOSED #218: shared `explicit_protocol_refs`. |
| G-14 | F-7-03 A-10 | 7 | — | S3 | FINISH | CLOSED 2026-09-02 (T-12): rollback = `git revert -m 1` of the merge, documented in `docs/ops.md` incident step 4 and rehearsed against a real merge commit on a scratch clone (`T-12-rollback-merge-rehearsal.txt`; the two earlier rehearsals reverted a single-parent commit). Service-style drills are N/A on a checkable fact — no deploy target exists (`.github/workflows` has none; "deploy" is merge to `main`). Was ACCEPT with expiry #226 (A-26); the expiry condition now lives in the ops step itself. |
| G-15 | F-16-05 | 16 | — | S2 | FINISH | Run 2: GitHub **About** description says "10 outcome-named autonomous fleets"; the catalog is 13. Landing truthfulness; a repo-settings change → H-04. |
| G-16 | F-1-04 | 1 | CF-05 | S1 | FINISH | CLOSED 2026-09-09 (T-13): re-witnessed on current `main` — Orca-dispatched ro workers (grok headless, A-30) on PR #231 @ `9e1237f`; verdict NO-GO (0C/3R), which counts per DEFINITION CF-05. Evidence `CF-05-r3-happy-review-it.txt`. Was: run-1 evidence SHA-bound to `6ad0e87`, pre-#225 → H-07. |
| G-17 | F-2-05 | 2,16 | — | S3 | FINISH | Run 2: `[Unreleased]` carries #225 while `plugin.json` is 0.6.0 — the G-06 shape recurs. Version cut → H-05 (A-20). |
| G-18 | F-7-05 | 7 | — | S3 | FINISH | CLOSED T-09 (run 2): G-14's expiry is issue #226. |
| G-19 | CF-05-r3 spec-F2/F3, standards nit | 14 | — | S2 | DEFER | `docs/ops.md` step 4 precision: add the checkable "no deploy job in `.github/workflows`" clause, cite both dated rehearsals, lead with the `-m 1` form. Off critical flow → post-launch issue. |
| G-20 | CF-05-r3 testadeq-F1/F2 | 4 | — | S2 | DEFER | The `-m 1` rollback fix is unbound: no test mentions `revert`; extend the ops/release tests to pin the merge-shaped command. Off critical flow → post-launch issue. |
| G-21 | CF-05-r3 spec-F1, standards nits | 14 | — | S3 | DEFER | Ledger hygiene: stale #212 pointers in STATUS.md, GAPS post-launch "ACCEPT" label, A-26 "rehearsed twice", PLAN/GAPS cut-line drift, ASSUMPTIONS A-24/A-25 hole; PR-body file-set lesson (update the body when scope grows mid-PR). Severity note (S5-B RV-07): spec F1 was **Required at the review axis** (merge-blocking there); it is carried at driver-severity S3 because a stale file-set sentence in an already-merged PR body is not a live product defect — the axis→driver severity mapping is recorded, not dropped. |

## Cut line

**Above (plan):** G-01..G-08, G-11..G-13 (G-06..G-08, G-11..G-13 closed post-launch). Run 2 adds G-14/T-12, G-15..G-18 (T-09 agent; H-04 / H-05 / H-07 human). Run 3 closes G-16 (T-13).

**Below:** G-09 DEFER (register entry unchanged; its tracker issue #212 closed at the maintainer's request — the field-proof plan in `docs/runs/README.md` is the live tracker, A-27). G-10 closed 2026-09-02 (T-10 #228, T-11 drill #229). G-14 closed 2026-09-02 (T-12). Run 3 adds G-19 / G-20 / G-21 DEFER (to be filed in S5-C). No ACCEPT remains.

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
| G-14 (was ACCEPT expiry; closed on evidence 2026-09-02 by T-12) | https://github.com/ravidsrk/orca-fleet/issues/226 |
