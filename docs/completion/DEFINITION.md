# Definition of Complete — orca-fleet

```
frozen_at: ed6a2f4
product: orca-fleet
frozen_by: completion-driver run 20260901-1336
immutable after freeze (R6 / R13)
text_as_of: 67c1707   # run 1's greptile P1 corrections to items 4-5 (2026-09-01); no content edit since. Annotation added by run 2 (fresh-reviewer RV-04); not a content change.
```

This is a **catalog + verifier**, not a hosted app. Complete means a stranger can install it, trust its honesty claims, reproduce the moat demo, and — when Orca is running — start the documented first mission.

## Critical flows (final)

| id | acceptance evidence |
|---|---|
| CF-01 Catalog gates | Fresh clone (or this worktree) · `python3 scripts/validate.py` exit 0 · `python3 -m unittest discover -s tests` 317 OK · `python3 runtime/scripts/proof_status.py --check` exit 0. Evidence files `CF-01-*`. |
| CF-02 Install | Symlink or plugin path leaves `../../playbooks` resolvable. Evidence: `CF-02-happy-symlink-install.txt` (plugin UI path is H-02-adjacent, not required if symlink works). |
| CF-03 Independent verify | `python3 bench/vf-bench/vfbench.py` sound false-done **0**; valid-control GREEN. Evidence `CF-03-happy-vfbench.txt`. Failure path: any gamed trap RED. |
| CF-04 Negative-control demo | `sh demo/negative-control/run.sh` PASS (self-score GREEN, verify RED). Evidence `CF-04-happy-nc-demo.txt`. |
| CF-05 First Orca mission | With Orca app running: follow getting-started **review-it dry run** to a SHA-bound verdict (GO or NO-GO both count). Happy + one failure (Orca down → documented stop) evidenced. Failure path already captured; **happy path is H-01**. |
| CF-06 Proof honesty | `proof_status.py --check` exit 0; no mission's `proof:` exceeds its report. Evidence in P0 transcript. |

## Launch gate

All of the following, with evidence:

1. Every **S0** closed. (None open at freeze.)
2. Every critical flow E2E-evidenced: happy path + one failure path. **CF-05 happy path outstanding (H-01).**
3. Backup restored once = fresh clone/worktree reproduces CF-01 (A-09). Met by P0 cold start.
4. Rollback rehearsed once = `git revert` of a throwaway commit on a **scratch clone** (not `main`). Evidence: `evidence/P0-rollback-rehearsal.txt`.
5. Alert-on-failure is **not demonstrated**. A green Actions run does not prove a failure notification. G-10 DEFER; A-13: this item does not block catalog GO (proving it would require redding `main`, forbidden by R9).
6. Stranger Test ≤15 min from clone to CF-01+CF-04 using README/getting-started. **Met** this session (~command time + 23s tests).
7. No `ACCEPT` at S0.
8. Launch-gating Human Actions: **H-01** (Orca up + review-it dry run). H-02 (marketplace) does **not** gate catalog complete. H-03 (version bump) does not gate.

## Minimum scores

Default: ≥3 on angles 1–9 except N/A; ≥2 on 10–17 except N/A (A-07).

At freeze the informational score is 52%. The gate is **not** "reach 100% of the score"; it is the list above. Angle 9 (observability) is 1 and is **DEFER G-10**, so the default ≥3 on angles 1–9 is **waived for angle 9 only** as A-12:

> A-12 (Phase 3): angle 9 minimum lowered to ≥1 for this product because there is no runtime to observe; GitHub Actions is the alert. Logged so it is not a silent reinterpretation of the whole table.

## Out of scope (CUT / DEFER / ACCEPT)

- Hosted SaaS, billing, landing site, mobile app, in-product LLM calls.
- Advancing the 9 doctrine-only missions to self-run/external-run (G-09).
- Community marketplace aggregator submissions (G-07 / H-02).
- `skills-ref` as a second validator (G-08).
- ruff-in-CI (G-11).
- Account inventory / incident doc (G-12).
- Shared validator grammar (G-13).
- Service-style rollback drills (G-14 ACCEPT).
- Version bump to 0.6.0 (G-06 / H-03).

Future-you may not re-litigate these without a new freeze.
