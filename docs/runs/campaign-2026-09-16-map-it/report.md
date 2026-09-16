# Run report — map-it self-test, 2026-09-16 (campaign dir; doctrine-only)

Mission source: `skills/map-it/SKILL.md` @ `c46d4b3f3371e41408aed19e54476fa194c20b42`,
installed location: this worktree (`campaign/map-it-selftest`).
Run kind: self-run against this catalog. Tier claimed: doctrine-only (campaign evidence
dir is not a bindable `docs/runs/<date>-<mission>…/` run dir; see Evidence binding).

```
RUN: mission=map-it tier=doctrine-only inventory_at=31d2490f0ee0a3b812f77b9ff820891924dfe354 manifest=docs/runs/campaign-2026-09-16-map-it/manifest.json verifier=GREEN waves=0
```

| Field | Value |
|---|---|
| Mission | `map-it` — mission source revision `c46d4b3f3371e41408aed19e54476fa194c20b42` |
| Tier claimed | `doctrine-only`; run kind: `self-run` (catalog) |
| Target | orca-fleet itself @ origin/main tip `c46d4b3`; destination: G-09 field-proof completion (19 doctrine-only missions) |
| Fixed point | BASE `-` (planning mission) · FORK_POINT `-` · frozen contract `docs/runs/campaign-2026-09-16-map-it/contract.json` digest `e009989260ffab7f81e3b44bc391fb972dd4ad749deadbf15f20a16f35ce7eff` |
| Coordinator / workers | spawned campaign child · no workers dispatched (prepare-only + coordinator-cleared frontier) · TASK pack `matt` (declared on all 31 DAG specs; never co-mounted) |
| Orca | `orca status --json` → `runtime.reachable: true`, appVersion `1.4.203`, runtimeId `75429d93-a441-4225-9f94-18e893d3212e` · Run `run_b28a7dacdd9e` · coordinator `term_0859a28a-bb61-45c2-b054-41169a9e06db` |
| Human gates | all PARKED (spawned session): D-0 freeze sign-off + D-1..D-20 + T-1..T-3 → `handoff-questionnaire.md` Q-0..Q-21 |

## Terminal state

**MAPPED-WITH-BLOCKED** (degraded; never reported as MAPPED): the map is frozen for what
is known (destination, facts, plan, verified DAG), and 21 decision tickets + 3 task tickets
+ the freeze sign-off are blocked on a human who has not answered; the handoff lists them.

Planning ledger rows (`ledger.md` — orca task id + decision-ticket fields):

- F-1, F-2, F-3 (facts): RESOLVED with tree evidence (`facts.md`).
- R-SWEEP (research sweep): RESOLVED — zero research tickets, memo recorded.
- D-1..D-20, T-1..T-3, D-0: BLOCKED with handoff refs (Q-0..Q-21).
- Prototype tickets: none (no look/behave question); "not yet specified": none (all sharp).

## Convergence proof

Every clause of map-it's `## Convergence proof` with discharging evidence:

1. Destination named → `ledger.md` hypothesis + `plan.md` title (G-09 field-proof completion).
2. Every open question a sharp ticket (resolved/blocked) or explicit "not yet specified" →
   `ledger.md` ticket rows: 4 resolved, 25 blocked, 0 fog (`facts.md`, `research-sweep.md`).
3. Every decision ticket human-resolved or explicitly blocked → all 21 D + 3 T BLOCKED with
   `handoff-questionnaire.md`; agent resolved none (DECISIONS.md carries only
   mechanical/taste coordinator drafts, each vetoable via Q-1/Q-19).
4. Frozen plan/spec exists → `plan.md` on planning branch `campaign/map-it-selftest`,
   freeze-prepared at `4f87dca6fe61eafe90bfca01f6aad721e0cd1279`; human sign-off parked (D-0).
5. Materialized, verified, FROZEN-for-handoff DAG → 31 tasks in run `run_b28a7dacdd9e`,
   `dag-table.md` + `dag-task-list.json`, DAG VERIFY: PASS (31/31, acyclic,
   foundation-first, single-writer hot-file, worker contract + lighting on all); nothing
   dispatched (prepare-only commits by freeze); skeptic verdict SOUND (`skeptic.md`).
6. Handoff checklist complete → freeze commit SHA + plan path (§above), DAG path + table
   (`dag-table.md`), blocked list (`handoff-questionnaire.md`), manifest naming
   MAPPED-WITH-BLOCKED (`manifest.json` claim + parked[]).
7. No production code written → `git diff --stat c46d4b3..HEAD` touches only
   `docs/runs/campaign-2026-09-16-map-it/` (docs + JSON planning artifacts).

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| ORIENT | worktree → origin/main tip; branch `campaign/map-it-selftest` | ok, HEAD `c46d4b3` | ledger header |
| ORIENT | `orca terminal create` + `run-create` | Run `run_b28a7dacdd9e` | `orca-run.json` (see below) |
| NAME | destination + hypothesis + premises P-1..P-4 + Verified Current State | drafted (taste, vetoable) | `ledger.md`, `DECISIONS.md` |
| CHART | 29 tickets charted under fog-of-war rule | 4 sharp-resolved, 25 blocked, 0 fog | `ledger.md` |
| FRONTIER facts | proof_status, field-proof table, fence-read issues #427/#441-444 | F-1..F-3 RESOLVED | `facts.md` |
| FRONTIER research | sweep: any external fact blocking a map decision? | none → 0 tickets + memo | `research-sweep.md` |
| FRONTIER review | plan-review lenses (coordinator-run, DV-2) | VERDICT: sound pending gates | `plan.md` terminal section |
| FREEZE-PREPARE | `decide-and-freeze` publish (objectives, ACs, boundaries, seams) | prepared; sign-off parked (D-0) | `plan.md` @ `4f87dca6` |
| DAG-PREPARE | `task-create` ×31 (topological), no dispatch | 31 materialized | `dag-task-list.json` |
| DAG-VERIFY | decompose-dag verify section (read-only re-derivation) | DAG VERIFY: PASS | `dag-table.md`, transcript below |
| SKEPTIC | 4 questions (coordinator-run, DV-3) | SOUND, no updates | `skeptic.md` |
| HANDOFF | questionnaire Q-0..Q-21 (human-handoff) | filed | `handoff-questionnaire.md` |
| MANIFEST | manifest + signed dispatch + `verify.py` | GREEN (exit 0) | `manifest.json`, `verifier.txt` |
| GATES | `scripts/validate.py`, `unittest discover -s tests`, `proof_status --check` | exit 0 / see below | `validation.txt`, `tests.txt` |

Orca run receipt: `{"run_id": "run_b28a7dacdd9e", "coordinator_handle":
"term_0859a28a-bb61-45c2-b054-41169a9e06db", "created_at": "2026-09-16T12:26:47Z"}`.

DAG verify transcript (read-only, `/tmp/map-it-dag-verify.py`, exit 0):

```
ledger tasks present: 31/31
no cycles: ok
foundation-first: ok
roots: ['FDN-01']
no parent_id: ok
hot-file single-writer: ok
worker contract + lighting + pack on all 31: ok
DAG VERIFY: PASS
```

## Verifier outcome (recorded exactly)

```
python3 runtime/scripts/evidence-run.py --label verifier-green --manifest docs/runs/campaign-2026-09-16-map-it/manifest.json --artifact docs/runs/campaign-2026-09-16-map-it/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-map-it/manifest.json --contract-source docs/runs/campaign-2026-09-16-map-it/contract.json --contract-digest e009989260ffab7f81e3b44bc391fb972dd4ad749deadbf15f20a16f35ce7eff --unit-class planning --lighting lit --dispatch-record docs/runs/campaign-2026-09-16-map-it/dispatch-record.json --dispatch-pubkey docs/runs/campaign-2026-09-16-map-it/dispatch-pubkey.hex
```

Output (exit 0):

```
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: dispatch record signature verified against the supplied key (#135) — a soundness boundary only if that key is trusted (off-worker: CI/MCP/SDK or an auditor)
verify: OK — all required checks passed
```

Earlier RED runs retained in the manifest's `commands[]` ledger: (1) unsupervised planning
downgrade over JSON artifacts (#310) → fixed by the coordinator-signed dispatch record
(`dispatch-record.json` + `dispatch-pubkey.hex`; private seed kept in /tmp, never
committed); (2) transcript self-pinning (the recorder truncates its artifact before the
child runs) → fixed by the tracked-at-head form per `_read_artifact` (prove-it pattern).

Flag provenance: `--contract-source`/`--contract-digest` = coordinator's frozen contract
(Fixed point row); `--unit-class planning` + `--lighting lit` = signed dispatch values;
`--dispatch-record`/`--dispatch-pubkey` = coordinator signature (downgrade lane, #310).

## WIP-curve protocol row

Inapplicable: planning/report-only self-test with zero dispatch waves (`waves=0` in the
`RUN:` header). No builders or reviewers were dispatched; the frontier was cleared by the
coordinator (facts/sweep) and parked (decisions/tasks). No throughput, latency, rework, or
freshness figures exist to plot. (`attention-budget` rows are required for mutating
self-runs; this run mutated no production surface.)

## Deviations and lessons (recorded, not hidden)

- DV-1: evidence lives under `docs/runs/campaign-2026-09-16-map-it/` (campaign mandate),
  not `docs/runs/<date>-<mission>…/`. No proof-tier advance is claimed; map-it stays
  doctrine-only. The DECISIONS log likewise lives in the campaign dir instead of
  `docs/DECISIONS.md` (campaign isolation).
- DV-2: plan-review lenses ran coordinator-side, not as fresh workers (single-session
  self-test; no worker fleet exists yet — the DAG this run prepares would provide it).
  Lens order, expectations-before-reading, premises, alternatives, and the terminal report
  were all honored; only reviewer independence is weaker than the playbook.
- DV-3: decompose-dag's plan skeptic ran coordinator-side for the same reason; recorded in
  `skeptic.md` rather than inline because the plan file's terminal section must stay the
  plan-review report.
- DV-4: no PR was opened for the planning branch (campaign rule: no push, no PRs, no
  merge). The branch `campaign/map-it-selftest` exists locally with the freeze-prepared
  commits; opening the PR is part of unparking (Q-0).
- DV-5: research-brief's verification leg could not run (no second fresh session), so no
  research ticket was opened at all — the sweep memo records why none was needed, and each
  wave-2 run card opens with a slate unit executed with a verification leg at run time.
- Lesson: `verify.py`'s self-output pinning does not converge through `evidence-run.py`
  (truncate-before-run); the tracked-at-head-blob form is the working pattern — matches
  the prove-it close. Lesson: JSON planning artifacts trip the #310 code-shape rule, so a
  planning unit with JSON evidence needs the coordinator-signed dispatch lane up front.

## Evidence binding

`inventory_at` names the evidence commit once cut (C4/C5 below). The manifest's `head_sha`
(`cf290747…`, content commit) differs from `inventory_at` by design (prove-it pattern):
the graded manifest + GREEN transcript land in the evidence commit while the verified
content range stays fixed. Re-verify at the evidence commit with the invocation above.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-map-it/ledger.md` | `038636dbefda7205d3da5625ff09656a5d412d9ccd34aa4cedbce8d6a3c42878` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/plan.md` | `d42f69cd6611129924334924aac25430b2a25a84e8aa32bbdcc20c132ae95eb6` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/facts.md` | `ac8834202df6b2656b720e0ba7fa48f62220f4d345d5325eabe16b5e29d4613e` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/research-sweep.md` | `77ce6c2350b097ac599ca6b08506e05738c4fa4245b0beab656ee67d1b44c6ee` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/handoff-questionnaire.md` | `acdd17cc0b911bf277345db12124ea9074893b5d13edb61b5c3124428341bf05` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/DECISIONS.md` | `cbad0c84457dd5a67282f074c4f81060c8e4e15feb8d58d9ea52447f414fde9a` | decisions.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/dag-table.md` | `ff2ea45603e7e521e6a7b463eb395dd1d258ee1457f4419cac0a22b41ed76039` | dag-verify 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/dag-task-list.json` | `66e4048d553aa7643904ac1ed835d0edf218421d74c6b9dba8647ebe13c11085` | orca task-list 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/skeptic.md` | `fd7186f65ab7f3ee6ee2471c36614906351d0b4d5c834081c9e901e2447a6189` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/contract.json` | `e009989260ffab7f81e3b44bc391fb972dd4ad749deadbf15f20a16f35ce7eff` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/manifest.json` | `84e0b5205a4ccf44f42aed735ca70e76f307b6aab171c0dbce15a62a0c65ce45` | coordinator + evidence-run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/verifier.txt` | `9fa574c6572cc376b2eaa9e1bf49d1305fba36b893b7df8f3fd0e8797226b618` | verify.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/dispatch-record.json` | `80e47393c4c5d962b8d6185a7c1aeae8730ea1ef4c06dfe291c514e38a19d44a` | dispatch-sign.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/dispatch-pubkey.hex` | `a9486f57cb0194b796e18128cacd7fb18567eae2a407adc60f5a19c41c734d04` | dispatch-sign.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/validation.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | validate.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-map-it/tests.txt` | `a66b96ee59263367f403a84554fd0e4a279436d8f758ada8baadec34c577291c` | unittest 2026-09-16 |

## Gates

`python3 scripts/validate.py` → exit 0, "All 21 missions valid" (`validation.txt`).
`python3 -m unittest discover -s tests` → see `tests.txt` (background at report drafting;
exit pasted below before close).
`python3 runtime/scripts/proof_status.py --check` → 19 doctrine-only, 2 self-run
(unchanged — no tier claimed).

Tests gate result: `Ran 1490 tests in 331.665s` → OK, exit 0 (`tests.txt`).
