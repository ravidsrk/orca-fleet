# Chain run report — `clean-sweep[DRY] → harden-it[CLEAN]` (#417)

RUN: chain=clean-sweep[DRY]->harden-it[CLEAN] leg=1 mission=clean-sweep tier=exercise target=scratch:chaining-target-417 base_sha=892eae208b01780a426deecdf9e81380753b30cc head_sha=c5e807cf4e05004f338d2c1a722c4000d888334e terminal=NOT-DRY verifier=UNAVAILABLE

RUN: chain=clean-sweep[DRY]->harden-it[CLEAN] leg=2 mission=harden-it tier=exercise target=scratch:chaining-target-417 terminal=NOT-STARTED gate=LEG1-GATE-UNSATISFIED+G-PROMO-1

## Result

The chain ran one full leg and STOPPED at the leg-1 gate — a stopped chain,
which the protocol counts as a correct outcome, not a failure to hide. No
degraded terminal was hit. Leg 1 exhausted its finding set with zero degraded
parks but cannot claim DRY: the build-blind review leg is owed (G-REVIEW) and
independent verification was environmentally unavailable. Behind that hold sits
a second, doctrine-certain hold: the inter-mission promotion gate (G-PROMO-1),
a one-way human gate the chaining doc never names (filed as the run's principal
protocol gap).

| Link | Mission | Terminal | Verification | Carried forward |
|---|---|---|---|---|
| 1 | clean-sweep (source=audit, 7 frozen findings) | NOT-DRY (EXHAUSTED, review-owed; zero degraded parks; DRY-ready pending human review) | per-unit manifests + executed NCs 3/3; tip 6 passed wtree-bound; review leg PENDING (D1); verify.py N/A cross-repo (manual §2 procedure + transcripts) | H1 H2 H3 → handoff-log.md (PRODUCED, owed — leg 2 not started) |
| 2 | harden-it | NOT-STARTED | — | — (leg-1 gate unsatisfied; G-PROMO-1 behind it) |

## The contract followed

Declared in-issue BEFORE the run (#417 comment 2026-09-16T05:54:51Z), quoted from
`runtime/mission-chaining.md`: declare sequence + per-link allowed terminals
(`mission[TERMINAL] → mission[TERMINAL]`); the gate between missions is the
previous mission's named terminal backed by verified evidence, no "continue
anyway"; degraded terminals (`-WITH-*`, `NO-GO`, `INCONCLUSIVE`) STOP the chain,
advancing past one is a one-way human gate; one mission active per repo, each
link a FULL run with its own BASE (carry-over is explicit-human, never default);
deferral carry feeds N+1 as enumeration input; no cross-repo chains; the report
names per link mission/terminal/verification/carry-forward, and a stopped chain
names its gate.

Freshness: Orca re-pin PR #433 (`36061ce`, v1.4.203) verified in `origin/main`
before anything ran; installed `orca --version` = `1.4.203` agrees with
`runtime/orca-pin.md` + `runtime/pins.json`. Fleet checkout `6390743`, branch
`roadmap/issue-417-chaining-run`. (Declaration named
`roadmap/issue-417-chaining`; the delegation brief named `...-chaining-run` —
brief wins, recorded here.)

## Leg 1 — clean-sweep (full run)

Target: `~/projects/chaining-target-417` (scratch, no remote — no-gh lane),
seed `892eae2` (baseline suite 4 passed). BASE
`chain417/leg1-cleansweep-base` forked at the seed SHA; ledger `leg1/ledger.md`;
denominator frozen as `leg1/enumeration.md` (sha256 `cf899c4f…`, 7 rows from the
declaration comment).

Triage (reproduce-or-refute): F3 reproduced (`delete 1` no-token → `deleted`);
F4 REFUTED (export-empty → exit 0, `[]`); F5/F6/F7 confirmed; F1/F2 classified
real-but-security → parked out-of-scope (a mission must not own security
findings). Wave plan asserted to cover all 7 frozen ids.

Build (failing-first, wtree-bound GREEN records, executed revert NCs with
observed exits): F3 → `b68a7be` (NC 1/0); F5 → `690b79d` (NC 1/0); F6 →
`0ee5a79` (NC grep 0/1, documentation oracle scope). Conductor landed serially
(`eec6505`, `873724d` with kept-both conflict resolution, `4c5c946`), each tip
suite-green; F7 closeout `3a40662` (claim CLI-verified true); F4 closeout
`c5e807c`. Re-enumeration @ `c5e807c` pasted in ledger: 4 closed, 1 refuted, 2
parked-clean, zero degraded, no new findings. Final tip 6 passed, wtree-bound.

Per-unit manifests: `leg1/manifest-f3.json`, `manifest-f5.json`,
`manifest-f6.json`; mission rollup `leg1/manifest-leg1.json`. Re-derivability
for the local-only target: `leg1/seed-*` (seed files) + `leg1/full-diff.txt`
(`892eae2..c5e807c`, 77 lines) reconstruct every byte.

## Why the chain stopped (two holds, in order)

1. **Leg-1 gate unsatisfied (G-REVIEW).** The chain named `clean-sweep[DRY]`;
   leg 1 reached EXHAUSTED with zero degraded parks but DRY requires the
   build-blind review leg (pipeline + evidence-manifest §2: verification
   failing on any required check → NOT done). Independent review was
   environmentally unavailable (fresh-session spawn: 7× capacity-rejected, 2×
   infra-fatal `unknown tool work_stop`; Orca-TUI-worker path assessed and
   declined — ledger G-REVIEW). Terminal: NOT-DRY. Resume: the PR reviewer
   (human second person) reads `leg1/full-diff.txt` (77 lines) and re-derives
   from the SHAs (criterion 5) — GO lifts leg 1 to DRY.
2. **Inter-mission promotion gate (G-PROMO-1, behind the first).** Leg 1 stops
   at its BASE: clean-sweep ("open the promotion PR, stop"),
   merge-serialization no-gh ("stops at BASE"), gate-classification (promotion
   one-way, "recorded human grant, always"). Coordinator-executed promotion
   (D2) was considered and REFUSED. With no landed promotion, leg 2 has no BASE
   to fork that isn't either human-carried (explicit-human, unavailable) or
   stale-`main` (divergent legs = branching, not chaining — rejected). Certain
   by doctrine analysis (three policies agree) even though the run stopped one
   step earlier. So: leg 2 NOT STARTED, carry H1–H3 produced-but-owed. The
   chaining doc specifies degraded stops but never mentions the inter-mission
   promotion gate — every no-gh / headless chain parks here after leg 1.
   Principal gap (filed).

## Deviations and observations

- D1 (ordering + availability): independent build-blind review unavailable
  before AND after the merges (spawn 7× capacity-rejected + 2× infra-fatal;
  Orca-worker path declined — ledger G-REVIEW). Merges rode on recorded
  NON-gating author self-checks. DRY is NOT claimed; terminal is NOT-DRY
  (exhausted, review-owed), resumable by the human PR reviewer.
- D2 (refused): coordinator promotion merge — refused, see above. Recorded as
  evidence the gate held.
- O1 (mission-level): F4's refuted close was ruled MECHANICAL (executed,
  re-derivable repro) without opening the batch human gate the mission text
  offers. Not a chaining gap; noted for clean-sweep.
- L1 (tooling): verify.py never ran — its single-repo assumption (evidence paths
  resolve under the same toplevel as the SHAs) cannot express a fleet-report /
  scratch-target split. The §2 procedure was executed manually with transcripts.
  Filed as a gap against evidence-manifest/verify.py via the chaining run.

## Follow-up issues (protocol gaps)

Listed in `gaps.md` with issue numbers once filed. Zero-gap is NOT claimed: the
run exposed real silences in mission-chaining.md (promotion lane, handoff shape,
local-target re-derivability).

## Integrity inventory

sha256 manifest for every artifact this report references — see
`integrity-inventory.txt` (producer + timestamp per line). RESUME / later audits
reject any artifact whose hash no longer matches.
