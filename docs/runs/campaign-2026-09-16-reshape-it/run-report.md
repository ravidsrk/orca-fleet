# Run report — reshape-it self-test vs orca-fleet, 2026-09-16 (campaign)

Self-test of the `reshape-it` mission against orca-fleet itself at `origin/main` tip.
Tier claimed: `doctrine-only` — this campaign run parks at the CONFIRM-SURFACE human
gate and advances no catalog proof tier; `metadata.proof` is untouched.

| Field | Value |
|---|---|
| Mission | `reshape-it` — mission source revision `c46d4b3f3371e41408aed19e54476fa194c20b42`, installed location `skills/reshape-it/SKILL.md` (in-worktree) |
| Tier claimed | `doctrine-only`; run kind: `self-run` (catalog vs itself) |
| Target | orca-fleet @ `origin/main` tip `c46d4b3f3371e41408aed19e54476fa194c20b42` (2026-09-16) |
| Fixed point | BASE `-` (parked before BOOTSTRAP) · FORK_POINT `-` · frozen surface: none (gate open) |
| Coordinator / workers | workflow-child (headless/spawned) · no workers dispatched · TASK pack: none (router rule untriggered — SCAN ran on the coordinator) |
| Orca | n/a — no dispatch occurred; the run parked before any worker phase |
| Human gates | `CONFIRM-SURFACE` — (awaiting human) @ (open) — (no decision; proposal in confirm-surface-request.md) |

## Terminal state

Not a mission terminal: **PARKED at CONFIRM-SURFACE** (`needs-human`), the SKILL-mandated
headless behavior — "publish the inventory and PARK at the gate". No RESHAPED /
RESHAPED-WITH-PARKED verdict is reachable without a human-bounded surface, and none is
claimed. Nothing was restructured; no characterization net was pinned (correctly — a net
pins at a *confirmed* seam, and no seam is confirmed).

Ledger rows (canonical shape; see [ledger.md](ledger.md)):

`| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |`

`| SCAN-1 | shallowness inventory (73 modules, 90d) | t | n/a | n/a | n/a | n/a | n/a | lit | - | scan.sh, scan-transcript.txt, inventory.md |`

`| GATE-1 | CONFIRM-SURFACE human freeze | f | n/a | n/a | n/a | n/a | n/a | lit | needs-human | confirm-surface-request.md (open) |`

## Convergence proof (per clause — all pending behind the gate, honestly recorded)

- (a) before/after interface-surface measurement per confirmed module: PENDING — no
  confirmed modules; the *before* half is published for all 22 production modules in
  [inventory.md](inventory.md).
- (b) legal negative-control pair (pinned mutant still KILLED at `head_sha`; revert
  enlarges the interface measurement): PENDING — no DEEPEN unit exists to carry one.
- (c) build-blind review at the reviewed SHA: PENDING — no diff exists to review.
- Confirmed surface never grew mid-run: HOLDS VACUOUSLY — the surface was never bounded,
  so nothing grew; no code outside this evidence directory changed.

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| Worktree sync | `git checkout -b campaign/reshape-it-selftest origin/main` | HEAD `c46d4b3f` | git reflog / branch |
| SCAN | `sh scan.sh` (73 × CHURN/WIDTH/DEPTH/FAN-IN probes) | exit 0, 73 probed | [scan.sh](scan.sh), [scan-transcript.txt](scan-transcript.txt), [inventory.md](inventory.md) |
| SCAN corroboration | independent re-probe of top 2 rows | exact match (46/73/1110/50; 58/92/2145/53) | run-report text (this file) |
| CONFIRM-SURFACE | published inventory + gate request; PARKED (one-way, human-only) | parked, `needs-human` | [confirm-surface-request.md](confirm-surface-request.md), [ledger.md](ledger.md) |
| BOOTSTRAP | not entered (gate open) | — | — |
| CHARACTERIZE | not entered (no confirmed seam) | — | — |
| DEEPEN / REVIEW / LAND / RE-SCAN / VERDICT | not entered | — | — |
| Gates | `python3 scripts/validate.py` → exit 0 ("All 21 missions valid"); `python3 -m unittest discover -s tests` → exit 0 (`Ran 1490 tests`, `OK`, 310.6s) | pass | command output (this file) |

## Key findings

1. The mission APPLIES to this repo (no missing-target park): the production surface is
   22 Python modules with real churn, headed by `scripts/validate.py` (score 302.52) and
   `runtime/scripts/verify.py` (248.76) — confirming the catalog's own field-proof
   prediction in `docs/runs/README.md`.
2. The headless gate fired exactly as the SKILL and eval 4 specify: inventory published,
   nothing bounded, nothing moved. `git status` at gate time shows only this evidence
   directory as added.
3. Probe notes for the human: FAN-IN substring inflation on short names (`gen`→109,
   `gate`→96); WIDTH includes module-level constants; YAGNI cut empty (all 73 churned).
   Details in [inventory.md](inventory.md).

## Deviations and lessons

- None from the SKILL pipeline: SCAN ran with verbatim probes; CONFIRM-SURFACE parked
  per the headless clause; later phases correctly not entered.
- Campaign-dir naming (`docs/runs/campaign-2026-09-16-reshape-it/`) follows the campaign
  tasking, not the catalog `YYYY-MM-DD-<mission>-<kind>` archive shape; no `RUN:` header
  or `run_report.py` binding is claimed, and no archive index row was added.

## Integrity

Evidence files (this directory): `scan.sh`, `scan-transcript.txt`, `inventory.md`,
`confirm-surface-request.md`, `ledger.md`, `run-report.md` (this file). Hashes below are
over the committed bytes at the evidence commit recorded in the campaign branch.

```text
b2d3e40b1e13b7d49dc59b5a7a31f69a93eeb3f01c506ed42e5ce9b93e2d283b  scan.sh
0900a820ae6714f582cba69858c06a62cc18967c696e1e393bc4b33e5dad5a4c  scan-transcript.txt
97030ae72898c44f321ff7412a6c1a6897cfbbb062e443e7c14db730a986b660  inventory.md
d67262f2d7f8d460d9d326847ac08bc874f64fdcda1b19ab7a9af2d4bc7de039  confirm-surface-request.md
d066dbc4383f4fed9da8fd2e4a331e9127be4fea501466cbcce7ae9a681fda48  ledger.md
```

Evidence: branch `campaign/reshape-it-selftest`, forked from `origin/main` tip
`c46d4b3f3371e41408aed19e54476fa194c20b42`. The five hashes above verify at the
branch tip — re-hash with `sha256sum` in this directory to confirm. (The report file
itself is intentionally unhashed so this binding line can name the branch tip stably.)
