# RV-D1 ledger row (DEEPEN scripts/validate.py) — fragment for the run ledger

`RUN: reshape-it-unpark-2026-09-16 · UNIT: RV-D1 · PHASE: DEEPEN · TARGET: scripts/validate.py (count-lint seam)`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-D1 | engine → _countlint (WIDTH 73→64) | t | t | t | Greptile APPROVED at head (pending) | f (coordinator) | t | lit | - | contract-rv-d1.json@E1, manifest-rv-d1.json, rv-d1-negctrl.txt (revert), rv-d1-carveout-a.txt (M1'), rv-d1-design.md, rv-d1-pre-verify.txt |

- Branch: `reshape/validate-deepen` → PR #463 → base `main`.
- base_sha (C0, frozen contract): `3032e268f9f17893e45b147a0a20df8dab61f848`
- H1 (prod + WIDTH pin): `55ab73a8184add7a0b85fb9fdc21fbb46ff17d16` · E-badge (1492): `13618c86a93d992ad09d2f28570fcc6a344c6e59` · E1 (evidence): `62ef58cab455c4f0825366fe49b841de7b39d696`
- WIDTH: 73 → 64 by the mission probe; zero existing-test edits.
- Behaviour: suite green at base (Ran 1490 OK) and head (Ran 1492 OK); M1 re-killed after re-anchor (carve-out a); revert re-widens 64→73 (carve-out b).
- verify.py: all legs GREEN except the independent-APPROVED review leg, see rv-d1-pre-verify.txt (exit 2, review-only RED). The final GREEN transcript (rv-d1-verifier.txt) lands in the record-only commit after Greptile APPROVED at head — a transcript cannot exist before the run it records.
