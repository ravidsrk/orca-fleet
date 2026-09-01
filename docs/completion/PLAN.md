# PLAN

Dependency order. No dates (TARGET_DATE unset). Only above-the-line gaps.

## Phase skeleton

| Phase | name | purpose | exit criteria | status |
|---|---|---|---|---|
| **P1** | Green baseline | Reproducible env; stale branches gone; CI pin | Cold start still passes; stale #207 worktree/branch gone; CI Python pinned | pending (T-01, T-04) |
| **P2** | Safety | Disclosure path; gate env example | SECURITY.md on default branch; `.env.example` lists ORCA_* | pending (T-03, T-05) |
| **P3** | Critical flows | CF-05 happy path | H-01 done + `CF-05-happy-review-it.txt` | blocked on H-01 (T-08) |
| **P4** | Operability | — | N/A / DEFER G-10 | skipped (A-12) |
| **P5** | Compliance surfaces | SECURITY.md is the legal/security surface | same as P2 T-03 | folded into P2 |
| **P6** | Launch surfaces | Marketplace | H-02 — does not gate | deferred |
| **P7** | Launch rehearsal | Stranger Test already met for CF-01/04; re-eval gate | Gate GO or CONDITIONAL GO | after P3 |

Order of phases not changed. P4/P5 merged/skipped with A-12 and fold-into-P2.

## Tasks

| id | phase | gaps | description | acceptance | size | depends_on | owner | status |
|---|---|---|---|---|---|---|---|---|
| T-01 | P1 | G-05 | Remove the leftover `orca-fleet-pr-comments` worktree and delete local branch `ravidsrk/address-sweep-pr-comments` (remote already gone). | `git worktree list` shows only main + this audit worktree; branch gone. `evidence/T-01-worktree-clean.txt` | S | — | agent | todo |
| T-03 | P2 | G-02 | Add `SECURITY.md` with a disclosure address (GitHub private vuln reporting + `ravidsrk@gmail.com` already in plugin.json). Link from README. | file exists; README points to it; `evidence/T-03-security-md.txt` | S | — | agent | todo |
| T-04 | P1 | G-03 | Pin CI `python-version` to `3.13` (matches local 3.13.15; still in bugfix per R-02). Mention the pin in getting-started Requirements. | workflow pin + getting-started sentence; tests still green. `evidence/T-04-python-pin.txt` | S | — | agent | todo |
| T-05 | P2 | G-04 | Add `.env.example` listing every `ORCA_*` `verify-gate.sh` reads, comments pointing at `docs/verify-gate.md`. No secrets. | file exists; names match the script's env reads (same contract as `test_verify_gate_doc_enumerates_every_orca_env_read`). `evidence/T-05-env-example.txt` | S | — | agent | todo |
| T-08 | P3 | G-01 | After H-01: capture CF-05 happy-path evidence. | `evidence/CF-05-happy-review-it.txt` | S | H-01 | human:H-01 | blocked |

T-02 unused (number hole — keep ids stable).

## Counts

- Above-the-line gaps: 5 (G-01..G-05)
- Tasks: 5 (4 agent, 1 human)
- S: 5 · M: 0 · L: 0
- Longest chain: H-01 → T-08
- Launch-gating Human Actions: 1 (H-01)

## P1 start order

T-01 (no source risk) → T-04 (CI) → then P2 T-03, T-05. Never two task branches at once.
