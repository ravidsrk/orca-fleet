# Run report — floor-it self-test, 2026-09-16 (campaign)

A floor-it mission run against orca-fleet itself at its main tip. Headless session: the run
completed DETECT + BOOTSTRAP, published the freeze proposal, and PARKED at the one-way human
FREEZE gate — the mission's honest headless terminal. No threshold was frozen, no unit dispatched,
no tier claimed. This is recorded history at `tier=doctrine-only`; `bind_check.py` skips it.

```
RUN: mission=floor-it tier=doctrine-only inventory_at=469bc1d1beafd7d3f8f726a36299ea630c0ddd00 manifest=docs/runs/campaign-2026-09-16-floor-it/manifest.json verifier=RED waves=0
```

| Field | Value |
|---|---|
| Mission | `floor-it` — mission source revision `c46d4b3f3371e41408aed19e54476fa194c20b42`, installed location `skills/floor-it/SKILL.md` (this worktree) |
| Tier claimed | `doctrine-only`; run kind: `self-run` (catalog) parked at freeze — advances nothing |
| Target | orca-fleet itself at origin/main tip `c46d4b3` (Merge PR #445) |
| Fixed point | BASE `campaign/floor-it-selftest` @ fork point `c46d4b3f3371e41408aed19e54476fa194c20b42` · frozen spec: none (proposal only — freeze parked) |
| Coordinator / workers | `cli` (sandbox shell, no Orca terminal handle) · zero workers · TASK pack: none mounted |
| Orca | `orca status --json` → `runtime.reachable: true`, appVersion 1.4.203 (transcripts/orca-status.txt); `run-create` refused `no_active_sender_terminal` — coordinator-only run |
| Human gates | FREEZE — UNANSWERED (parked; OPS-1, see FREEZE-QUESTIONNAIRE.md) |

## Terminal state

Mission terminal: **FLOORED-WITH-PARKED (freeze park)** — the run parked AT the freeze (headless),
per floor-it's parking class and gate-classification (one-way is human-only, never auto-resolved
or defaulted on timeout). Zero dimension rows reached WIRE; all 12 proposed dimensions await the
human freeze.

`| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |`
`(no units dispatched — freeze parked before WIRE; see LEDGER.txt)`

## Convergence proof

floor-it's convergence ("every declared dimension has an enforced gate that fails on a deliberate
violation") is NOT met — and the mission names this exact outcome: a headless run PARKS at the
freeze rather than defaulting policy into being. Clause-by-clause accounting:

- Frozen CONSTRAINTS.md with all dimensions: NOT DONE — parked (OPS-1). Proposal published as
  FREEZE-PROPOSAL.md (PROPOSED, NOT FROZEN); no repo-root CONSTRAINTS.md written, honestly absent.
- Wired harness per dimension with throwaway-branch RED + revert GREEN: NOT DONE — blocked on the
  freeze (WIRE runs after FREEZE, in order, per the pipeline).
- Build-blind review + landing per unit: NOT DONE — no units exist.
- ENFORCE (CI blocks) + canary PR RED per gate: NOT DONE — blocked on the freeze.
- GUARD (`floor_guard.py` in target CI): NOT DONE — blocked on the freeze. (The script already
  exists in-catalog at `runtime/scripts/floor_guard.py`; the owed step is CI wiring + its own
  reviewed unit, which needs frozen thresholds to guard.)
- Table never shrank mid-run: HOLDS — the 12-row draft (DETECT.md) is identical to the proposal
  (FREEZE-PROPOSAL.md); D12's fold-in is a labeled proposal for the human, not a deletion.
- Parked-with-reason instead of vacuous checks: HOLDS — D9 (coverage, no tool), D10 (perf, no
  surface), D11 (a11y, no surface) are proposed parks with named human gates, never auto-green.

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| DETECT | 13 repo-own counters via evidence-run.py (validate, unittest×1490, ruff, gitleaks, routing, proof_status, run_report, bundle, vf-bench, coverage-absent, agentskills-absent, orca-status) | all exit as recorded (2 absence probes RED by design) | DETECT.md, transcripts/, manifest.json `commands[]` |
| BOOTSTRAP | `python3 runtime/scripts/preflight.py --base campaign/floor-it-selftest --fork-point c46d4b3…` | exit 0: OK (BASE≠default, fork-point fresh) | transcripts/preflight.txt |
| FREEZE | published FREEZE-PROPOSAL.md + FREEZE-QUESTIONNAIRE.md (human-handoff: questionnaire + recipient + VERIFY-COMPLETE); filed OPS-1; PARKED | parked, nothing frozen | FREEZE-PROPOSAL.md, FREEZE-QUESTIONNAIRE.md, LEDGER.txt |
| WIRE + PROVE-FIRES | not reached (blocked on freeze) | n/a | — |
| REVIEW / LAND / ENFORCE / GUARD | not reached (blocked on freeze) | n/a | — |
| REFLECT | compound-learn proposal (no AGENTS.md mutation) | done | REFLECTION.md |
| VERDICT | FLOORED-WITH-PARKED (freeze park) | terminal, degraded | this report |

## Verifier outcome (recorded exactly)

Invocation (via the installed recorder; manifest as graded):

`python3 runtime/scripts/evidence-run.py --label verifier --manifest docs/runs/campaign-2026-09-16-floor-it/manifest.json --artifact docs/runs/campaign-2026-09-16-floor-it/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-floor-it/manifest.json --contract-source skills/floor-it/SKILL.md@c46d4b3f3371e41408aed19e54476fa194c20b42 --contract-digest 6eab79297529a7ec3c70bf4a5ff6e6fbdd9a4cd5a45c5b9f49dc5cf76b8bbd39 --unit-class report-only --base campaign/floor-it-selftest`

Output (exit 2, RED — kept RED; it certifies no unit completion, which is the honest state of a
parked pre-unit run):

```
FAIL: scope: no criterion ids in the authoritative contract
FAIL: report-only unit declares base_sha == head_sha (c46d4b3f3371e41408aed19e54476fa194c20b42) and carries no signed dispatch record. An empty range asserts that this unit changed nothing and gives the gate no diff to check that against — a claim, not evidence, from the same worker that chose the class. Name the range the report covers, or have the coordinator sign the downgrade (#310)
verify: 2 invariant(s) failed — unit is NOT done
NOTE: origin/campaign/floor-it-selftest not found — ancestry check skipped
```

Why this RED is correct, not a defect to fix: (1) there is no dispatched unit and no signed
dispatch record (no Orca sender terminal in this sandbox), so the gate cannot bind a denominator —
naming a synthetic diff range to satisfy it would be scope theater; the measurements bind to the
single commit they were taken at. (2) The branch is deliberately unpushed (campaign protocol: no
push), hence the ancestry NOTE. Full transcript: `verifier.txt`.

Freshness note: `commands[]` wtree fingerprints bind the full working content including untracked
evidence-in-progress, so no record equals `c46d4b3^{tree}` — STALE by §2's mutation-unit rule, as
expected for a coordinator measurement ledger. The tracked tree at every run was exactly the fork
point's tree (`git status` clean apart from the untracked run dir; the suite is side-effect-clean).

## WIP-curve protocol row (mutating self-runs)

Inapplicable: `waves=0` — zero dispatch waves (coordinator-only run; the park precedes WIRE, so no
builder or reviewer wave ever ran). No per-wave rows exist to record. Attention-budget caps stay
ASSERTED; this run contributes no throughput point.

## Deviations and lessons (recorded, not hidden)

- BASE doubles as the campaign delivery branch (`campaign/floor-it-selftest`) instead of a separate
  `<maintainer>/fleet-integration` branch — satisfies BASE≠default + fork-point freshness while
  keeping evidence and delivery on one branch (DECISIONS.md `base-selection`).
- No Orca Run namespace (`RUN:-`): `run-create` refused `no_active_sender_terminal`; borrowing a
  live foreign terminal as `--from` would impersonate another run's sender (DECISIONS.md
  `run-namespace`). Ledger header records `-` with the witnessed reason.
- Coverage/perf/a11y dispositions are PROPOSALS for the human, not coordinator decisions — the
  freeze decides, including whether a dimension is parked.
- `agentskills validate` (CI gate) has no local install; recorded as CI-ONLY via exit-1 probe
  rather than narrated.
- The ledger is `LEDGER.txt`, not `LEDGER.md`: `bind_check.py` routes every `docs/runs/**/*.md`
  containing a `^RUN:` line as a bindable report, and the ledger-contract header (`RUN: … ·
  COORDINATOR: …`) is a different schema with the same prefix — the first committed shape failed
  bind-check (exit 1) on exactly that. The header bytes are preserved verbatim; only the extension
  changed, because the ledger is not a report. (Pre-#415 run dirs contain ledger-`RUN:` `.md`
  files, but those predate the gate and are dormant unless touched.)

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-floor-it/manifest.json` | `f8163fcff05d3ff2453b28d4ed45cbab5f4f1b4368a8934637cb8c1cb6c51fd9` | evidence-run.py 2026-09-16 + finalize script |
| `docs/runs/campaign-2026-09-16-floor-it/verifier.txt` | `fd243055755835026f75daeb42f37e518dc5f7335efb85e1b6d70fdfc4f1446a` | evidence-run.py verify.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/LEDGER.txt` | `b42696d587f8c43f778eaa8d8e92082c2a5767c75ba773ad560bf93040ab3510` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/DETECT.md` | `53ac18844bc67547deeeee11628d29813b13a2f6457a7e17bbdfe192bd1244af` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/FREEZE-PROPOSAL.md` | `833d722f33d2621136535422371483c6e966f497894e3335d1653eddb000818b` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/FREEZE-QUESTIONNAIRE.md` | `927ab95cb4e8d69a9ada7c2630475c05e31c32061e372c2e7b8b758aa198b1d4` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/DECISIONS.md` | `f4f4eaeb2909097833d6ade73aa8dfff387aa08e542d2f8d2483b28a382c5d9e` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/REFLECTION.md` | `3044faec5a495de946311cb7bf0aa65f6a0ce091317a5c4bbde0b984619039f7` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/validate.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/unittests.txt` | `3840dec722a1ec2e6516628d77a5dd2856e387de8639a83f900ef8004e01b4b0` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/ruff.txt` | `82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/gitleaks.txt` | `1a145b27e2dc6b53d747306046080128010e3b55bad8cc58b27d9c9a5fec8d40` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/routing.txt` | `cf7aef8662b40390466e19c0a2b063df19961e5916b6d516ddc34f141002dc38` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/proof-status.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/run-report.txt` | `8d3a1a04b55019cd2139d4b54cc70aac27dbdc06214760c67fc1c2d44e3ba31d` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/bundle.txt` | `60c5ec0dd1550fcfa204606144dd78efe48939f418ffafb0b53dd6f47e586c00` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/vfbench.txt` | `3e8d0abc965460c9b4b9abe46e409f02081697d982cb985b51a937bbda0b1f29` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/coverage-absent.txt` | `a845f5439846d6ca4f7b589c5c5cfadc83084d8b95547b2aa824353eccdc9c83` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/agentskills-absent.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/orca-status.txt` | `f85b39f7164c34ae532f22f92cc51a5d38488800e9a0998adbc6b99b68b93556` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/preflight.txt` | `dc5517ddd9ff5590971db13e48c2153ee58da5cadf26845a996b486002344651` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/final-validate.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-floor-it/transcripts/final-tests.txt` | `3f15525f9585c95856e32dba2e0b55891fdb5c32ff2837dee8ead553c6e003f7` | evidence-run.py 2026-09-16 |

Inventory commands (run at close; the graded manifest is among the hashed paths; the report itself
is excluded per TEMPLATE):

`python3 runtime/scripts/inventory.py write docs/runs/campaign-2026-09-16-floor-it/REPORT.md`

`python3 runtime/scripts/inventory.py check docs/runs/campaign-2026-09-16-floor-it/REPORT.md`

`python3 runtime/scripts/inventory.py check docs/runs/campaign-2026-09-16-floor-it/REPORT.md --at <inventory_at>`

## Gates

Project gates at the final head (recorded via evidence-run; transcripts above):

- validation: `python3 scripts/validate.py` → exit 0, "All 21 missions valid" (final-validate.txt)
- tests: `python3 -m unittest discover -s tests` → exit 0, 1490 tests OK (final-tests.txt)

## Evidence binding

`inventory_at` names the latest evidence commit, where the manifest and every artifact above
re-hash; each header-binding commit touches only the `RUN:` line (one line, `REPORT.md`). To
verify: `git log --oneline origin/main..HEAD`, confirm each `bind … RUN header …` commit's diff
is that single line, then `python3 runtime/scripts/inventory.py check
docs/runs/campaign-2026-09-16-floor-it/REPORT.md --at <inventory_at>` (want: 23 verified,
0 mismatched). No CONSTRAINTS.md, no tier advance, no push.
