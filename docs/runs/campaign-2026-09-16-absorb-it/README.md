# Run report — absorb-it self-test, 2026-09-16

RUN: mission=absorb-it tier=doctrine-only inventory_at=cd2c2faa589d14ecf3690537162a529d2e3ae982 manifest=docs/runs/campaign-2026-09-16-absorb-it/manifest.json verifier=GREEN waves=0

Self-test of the `absorb-it` mission against orca-fleet itself: the coordinator ran
the mission pipeline for real (SELF-ORIENT → ENUMERATE → CLASSIFY → re-ENUMERATE →
VERDICT) against the inbound PR queue of `ravidsrk/orca-fleet` at its main tip.
T0 enumeration and T1 re-enumeration both found zero open inbound PRs, so the run
converged **ABSORBED** with zero dispatches, zero closes, and zero gates owed. An
empty queue is the mission's own terminal state — not a missing target, so not a
PARK. `tier=doctrine-only`: recorded history supporting no proof-tier advance (see
Evidence binding); the verifier outcome below is GREEN and is recorded exactly.

| Field | Value |
|---|---|
| Mission | `absorb-it` — SKILL unchanged by this run (mission source @ `6390743`) |
| Tier claimed | `doctrine-only`; run kind: `self-run` (this catalog) |
| Target | this catalog's inbound PR queue: `ravidsrk/orca-fleet`, default branch `main` |
| Fixed point | BASE `-` (no integration BASE: zero absorbable units) · FORK_POINT `-` · frozen contract `queue-digest.md` @ digest `c995722c…` (criterion ids AQ-1..AQ-3) |
| Coordinator / workers | solo coordinator (Muse Spark) · zero workers · TASK pack: none mounted (zero dispatches — the one-router rule holds vacuously) |
| Orca | `orca status --json` → `runtime.reachable: true` (app 1.4.203, state ready) at 2026-09-16T10:00:50Z — reachable but unused: nothing to dispatch |
| Human gates | none opened (no closes, no refutations, no parks — no batch gate owed) |

Authorship carve-out (stated per SKILL): this mission is the documented exception
to dispatch-lifecycle commit hygiene — an absorbed commit keeps its original
`Author:`. This run absorbed zero commits, so no authorship was preserved or
rewritten; every commit on `campaign/absorb-it-selftest` is coordinator-authored.

## Terminal state

**ABSORBED** (not degraded — zero parked). Ledger (`ledger.md`, canonical row shape):

`RUN campaign-2026-09-16-absorb-it · COORDINATOR solo (Muse Spark, file-backed ledger — no Orca dispatch: zero units) · BASE - · FORK_POINT - · T0 2026-09-16T10:00:41Z · SOURCE inbound open-PR queue of ravidsrk/orca-fleet @ T0 (queue-digest.md) · WIP builders=0 reviewers=0`

| task_id | pr | title | CLASS | REPRO | AUTHOR_OK | RECEIPTS | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | CLOSED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| *(no rows — T0 enumeration returned zero open inbound PRs; T1 re-enumeration confirmed dry)* | | | | | | | | | | | | | | | | `t0-enumeration.txt`, `t1-reenumeration.txt` |

## Convergence proof

Mission `## Convergence proof`, clause by clause:

1. *A full re-enumeration finds zero inbound PRs outside a terminal class.*
   T1 re-enumeration (10:00:54–10:00:55Z, 2 routes, exit 0) found zero open;
   opened/closed since T0: none (`t1-reenumeration.txt`). Discharged.
2. *Per absorbed contribution: preserved authorship, RED-on-base/GREEN-on-head
   receipt, complete receipt log, ancestry-verified merge, close with landing SHA
   + credit.* Vacuous: zero absorbed contributions (zero rows). No authorship to
   assert, no receipt owed. Discharged by emptiness.
3. *Per refuted PR: reproduction attempt on main logged, close passed the batch
   gate.* Vacuous: zero refuted PRs, zero closes, no batch gate opened. The most
   recent queue activity (PR #438, merged 09:01:10Z, ~1h before T0) predates the
   run and needed no action. Discharged by emptiness.
4. *The verifier re-derives authorship, re-runs the receipt at the merged SHA and
   re-counts the log.* Vacuous as a per-PR check; the run-level analogue holds:
   `verify.py` GREEN on `manifest.json` against the frozen contract (see Verifier
   outcome), and the inventory below re-hashes every run artifact.

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| SELF-ORIENT | read `skills/absorb-it/SKILL.md` (full), `AGENTS.md`, `ARCHITECTURE.md`; consulted triage-state, evidence-manifest, ledger-contract, liveness-resume, gate-classification, compound-learn | oriented; worktree already at origin/main tip `6390743` | branch `campaign/absorb-it-selftest` |
| ENUMERATE at T0 | 3 routes: `gh pr list --state open --limit 200`, REST `pulls?state=open` paginated, `gh search prs --state open` | all exit 0, all zero open (10:00:41–10:00:44Z) | `t0-enumeration.txt` |
| CLASSIFY | triage-state over the enumerated set | empty set — nothing to classify | `ledger.md` (zero rows) |
| BOOTSTRAP | `preflight.py --mode readonly` (no integration BASE: zero absorbable units); merge policy read (`allow_merge_commit:true` — not squash-only); Orca reachability attested | exit 0; reachable:true, app 1.4.203 | `preflight.txt` |
| RECLASSIFY/ABSORB/RECEIPT/REVIEW/LAND/CLOSE | — | vacuous: no absorbable PRs; no workers, no receipts, no PRs, no closes | `ledger.md` |
| re-ENUMERATE (T1) | 2 routes re-run; reconcile opened/closed since T0 | exit 0, still zero; none opened/closed (10:00:54–10:00:55Z) | `t1-reenumeration.txt` |
| VERDICT + compound-learn | ABSORBED recorded; reflection written | zero merged units, zero parked; 1 backlog candidate noted, not filed | `ledger.md`, `REFLECTION.md` |

Composed playbooks not exercised (no inbound PR existed to drive them):
`remediate-finding`, `acceptance-review`, `resolve-conflict`, `agent-brief`,
`merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle` (write lane),
`sandbox-policy` (no PR text existed to treat as data), `attention-budget`,
`gate-classification` (no one-way decision arose).

## Verifier outcome (recorded exactly)

First invocation (RED — kept as history; causes fixed, see Deviations):

`python3 runtime/scripts/evidence-run.py --label verifier --manifest docs/runs/campaign-2026-09-16-absorb-it/manifest.json --artifact docs/runs/campaign-2026-09-16-absorb-it/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-absorb-it/manifest.json --contract-source docs/runs/campaign-2026-09-16-absorb-it/queue-digest.json@c237f02dfbf072d2738f6d66bfb213b407d3ee21 --contract-digest a49b2d6d95a1701a525258076fb37db616e8f2c82e761516ccc794ad67289df1 --unit-class report-only`

Output (exit 2, preserved in `verifier-red1.txt`): class-downgrade refusal (the
`.json` contract counted as code in the range) + two unpinned-artifact refusals
(`validation.txt`, `tests.txt` named by the ledger but committed in neither E1
nor a pin).

Second invocation (GREEN — the binding record; manifest bytes frozen after it):

`python3 runtime/scripts/evidence-run.py --label verifier --manifest docs/runs/campaign-2026-09-16-absorb-it/manifest.json --artifact docs/runs/campaign-2026-09-16-absorb-it/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-absorb-it/manifest.json --contract-source docs/runs/campaign-2026-09-16-absorb-it/queue-digest.md@5df31bb700b11387541e0072ebe8fddd07819bc6 --contract-digest c995722c7821d088ebf37a3ed57f141ca6d5b9cfa42a819df53ea27507bda011 --unit-class report-only`

Output (exit 0, in `verifier.txt`):

```
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: report-only (unsupervised) — claimed with no signed dispatch record. base_sha..head_sha changes docs/tests only, so the class is consistent with the change, but nothing off-worker authorized it (#310)
verify: OK — all required checks passed
```

Confirmation (bare re-run against the final pinned manifest bytes, exit 0, in
`verifier-confirm.txt`): identical output. The `(unsupervised)` NOTE is the
honest state — a solo run signs no dispatch record — and does not fail the unit.

## WIP-curve protocol row

Inapplicable. `attention-budget` requires one row per dispatch wave of a mutating
self-run; this run dispatched zero waves (`waves=0`: no workers, no builders, no
reviewers — there was no unit to staff). The verified work is report-only
(enumeration + verdict against a frozen contract), so no WIP setting existed to
measure. No rows is the complete record, not a missing one.

## Deviations and lessons (recorded, not hidden)

- Orienting probes superseded: three un-timestamped listings ran before the
  recorded battery (one `gh api -f state=open` 422, retried correctly as a
  query string). The recorded T0/T1 transcripts above supersede them; the probes
  are disclosed here, not bound.
- E1 amended twice (unpushed branch, disclosed): (1) contract rewritten from
  `.json` to prose `.md` after the verifier refused the `.json` as code in a
  report-only range (#310); (2) ledger SOURCE pointer updated to the new name.
  Final E1: `5df31bb700b11387541e0072ebe8fddd07819bc6`.
- RED-then-GREEN verifier: first recorded run failed on the `.json` contract +
  unpinned post-E1 artifacts; fixed by the prose contract and sha256 pins (not by
  a self-signed downgrade, which a solo run cannot honestly manufacture). Both
  transcripts retained (`verifier-red1.txt`, `verifier.txt`).
- Report layout deviates from TEMPLATE.md: the campaign brief prescribed
  directory `docs/runs/campaign-2026-09-16-absorb-it/` holding report +
  artifacts (README.md inside), instead of a top-level
  `<date>-<mission>-self-run.md` + sibling dir. No proof claim rides on the
  layout either way.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-absorb-it/manifest.json` | `a90444a99fd2e6e9bfe9743dead006be4a05d8a1d5ab97d263b098bc420d8890` | coordinator assembly + evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/queue-digest.md` | `c995722c7821d088ebf37a3ed57f141ca6d5b9cfa42a819df53ea27507bda011` | coordinator (frozen T0/T1 denominator) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/ledger.md` | `ece4fe3fac4d8916250c3bec9396236179733a3d3bc737632e2b804579147352` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/REFLECTION.md` | `4b832536e7199560c68b7127c6c530e3ee3210144a19b5e0df494486d64a7933` | coordinator (compound-learn) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/t0-enumeration.txt` | `9d8419dd7473063fc433d19ee4d2701dbdbba27b5ed541c8e0d1291d1ee73d20` | gh CLI transcripts 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/t1-reenumeration.txt` | `25a4e074c92123adcdbc6bc144d0ccf19e624a04f12c9b8a7ce97d84eb0327c5` | gh CLI transcripts 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/preflight.txt` | `e4c3b27d2dd0da6d21aceef05325d62bddf1c8a9a952c6d76172094960b0d7e7` | preflight.py + orca + gh api 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/validation.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | evidence-run.py scripts/validate.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/tests.txt` | `b12869df0267e59de1d1d3ae9be2d17b91c57e236ad32a8cfa6a02351c0da9cf` | evidence-run.py unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/verifier.txt` | `815dfe31d7669df7715a610728308aad13ad548636227a170582c5902f09360a` | evidence-run.py verify.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/verifier-red1.txt` | `dc1ca7bdd7a8abb267e6b60ddb47a77770e93216fcda772ebdff425841b53994` | evidence-run.py verify.py (RED, history) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/verifier-confirm.txt` | `815dfe31d7669df7715a610728308aad13ad548636227a170582c5902f09360a` | verify.py bare re-run 2026-09-16 |
| `docs/runs/campaign-2026-09-16-absorb-it/proof-status.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | evidence-run.py proof_status.py 2026-09-16 |

Freeze: `python3 runtime/scripts/inventory.py write <report>` then
`python3 runtime/scripts/inventory.py check <report>` and
`python3 runtime/scripts/inventory.py check <report> --at <inventory_at>`.

## Gates

Catalog gates at the final head (all via the installed recorder except where
noted; records in `manifest.json` commands[]):

- `python3 scripts/validate.py` → exit 0 (`All 21 missions valid; three-layer
  separation holds; evals valid.`), in `validation.txt`.
- `python3 -m unittest discover -s tests` → `Ran 1490 tests in 281.863s / OK`,
  exit 0, in `tests.txt`.
- `python3 runtime/scripts/proof_status.py --check` → exit 0 (21 missions:
  doctrine-only 19, self-run 2), in `proof-status.txt`.

## Evidence binding

No catalog tier is claimed or advanced: `absorb-it` stays `doctrine-only` and no
frontmatter was touched. Branch `campaign/absorb-it-selftest` (unpushed, no PR,
no merge): E1 `5df31bb7` (enumeration transcripts + frozen contract + ledger +
reflection) → E2 (manifest + gate/verifier transcripts + this report + archive
index row) → E3 (this report's `inventory_at` set to E2 — header-only fixup; all
artifact blobs identical E2..E3). `inventory_at` names E2, the evidence-close
commit whose tree the inventory re-derives against.
