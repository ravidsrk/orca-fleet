# RV-D2 ledger row (DEEPEN runtime/scripts/verify.py) — fragment for the run ledger

`RUN: reshape-it-unpark-2026-09-16 · UNIT: RV-D2 · PHASE: DEEPEN · TARGET: runtime/scripts/verify.py (outcome-reading seam)`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-D2 | reader → _verify_sig (WIDTH 92→85) | t | t | t | Greptile APPROVED at head (pending) | f (coordinator) | t | lit | - | contract-rv-d2.json@E1, manifest-rv-d2.json, rv-d2-negctrl.txt (revert), rv-d2-carveout-a.txt (M2'), rv-d2-design.md, rv-d2-pre-verify.txt |

- Branch: `reshape/verify-deepen` → PR #467 → base `main`.
- base_sha (C0, frozen contract): `7ada834e6240887928c99637f30bbc9276f53631`
- H1 (prod + WIDTH pin): `1dfe039a09bc3462916b9a626b49fcbae9363566` · E-badge (1505): `b8e2bed9fba92439c1d09d7555970807e9227ce0` · H1b (keep _counted reachable): `ce0b9a32210c36603ccb758c6ab15c6b3adea3c1` · E1 (evidence): `4a8d7a9c9e85d8331a0bde215918ad77787b6430`
- WIDTH: 92 → 85 by the mission probe; zero existing-test edits. Re-export face: _failure_signature + _counted (H1b: the RV-C2 net pins _counted directly; both lowercase, zero WIDTH cost).
- Criterion text v3 (mechanism phrase corrected, IDs + measurable bar unchanged; C0 bytes in git).
- Behaviour: suite green at base (Ran 1503 OK) and head (Ran 1505 OK); M2 re-killed after re-anchor (carve-out a); revert re-widens 85→92 (carve-out b).
- verify.py: all legs GREEN except the independent-APPROVED review leg, see rv-d2-pre-verify.txt (exit 2, review-only RED). The final GREEN transcript lands in the record-only commit after Greptile APPROVED at head.
