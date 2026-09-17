# map-it self-test ledger — campaign-2026-09-16-map-it

RUN: run_b28a7dacdd9e · COORDINATOR: term_0859a28a-bb61-45c2-b054-41169a9e06db · BASE=- · FORK_POINT=- · T0: 2026-09-16T12:26:47Z · SOURCE: G-09 field-proof completion (19 doctrine-only missions @ c46d4b3f3371e41408aed19e54476fa194c20b42; freeze SHA pending human gate) · WIP: builders=3 reviewers=0

PHASE: ORIENT

Session kind: spawned (campaign child). One-way doors park; no human answers are faked.
Worker TASK pack: matt — never co-mount (no workers dispatched this run; see deviations).
Host permission mode: not recorded (no worker-start performed; ro lane never takes worker-start per sandbox-policy).

## Hypothesis (decide-and-freeze grill format, round 0)

What the human wants: a frozen execution map that closes G-09 — every one of the 19
doctrine-only missions advanced to a bound proof tier via its field-proof-plan run, ordered so
self-runs (targets exist in-catalog) precede external-runs (targets TBD), with each run's human
gates named up front so ship-it (or a mission chain) can consume the map without re-grilling.
Confidence: medium — the destination is fixed by the field-proof plan (maintainer-authored), but
scope (all-19 vs phased), ordering, and every external target need human calls.

## Premises (agree / disagree — human confirmation PARKED, see handoff Q-0)

PREMISE 1: The map covers all 19 doctrine-only missions, not a subset — agree / disagree
PREMISE 2: Self-run-capable missions (target exists in-catalog) order before external-target missions — agree / disagree
PREMISE 3: No production code is written by this run; the artifact is decisions + a prepared DAG — agree / disagree
PREMISE 4: External-target selection stays a human call per mission; the map carries sharp tickets, not picks — agree / disagree

## Verified Current State (read from the tree @ c46d4b3, not recalled)

- 21 missions; proof tiers: clean-sweep=self-run, prove-it=self-run, 19 doctrine-only
  (`python3 runtime/scripts/proof_status.py --check`, 2026-09-16).
- Field-proof plan rows exist for all 21 missions (`docs/runs/README.md` §Field-proof plan (#212)).
- Binding gate: `run_report.py` (RUN header, manifest in run's own dir, verifier transcript,
  inventory re-hash at inventory_at) + `validate.py` + `proof_status --check`.
- Orca runtime reachable: v1.4.203, runtimeId 75429d93 (this run's receipts).
- This campaign writes evidence under `docs/runs/campaign-2026-09-16-map-it/` (non-standard path:
  no proof-tier advance is claimed; tier stays doctrine-only).

## Ticket rows (planning shape: orca task id + decision-ticket fields)

| task_id | ticket | kind | question (sharp) | class | status | evidence |
|---|---|---|---|---|---|---|
| n/a (coordinator fact) | F-1 | fact | Which missions are doctrine-only and what does each field-proof row prescribe? | mech | RESOLVED | proof_status output + field-proof table (§Facts) |
| n/a (coordinator fact) | F-2 | fact | What is the binding bar a field-proof run must clear? | mech | RESOLVED | TEMPLATE.md + run_report.py (§Facts) |
| n/a (coordinator fact) | F-3 | fact | Which open tracker issues already decide pieces of the map? | mech | RESOLVED | issues #427 #441-#444 read via fence (§Facts) |
| n/a (coordinator sweep) | R-SWEEP | research-sweep | Does any map decision wait on an external fact (vs a human selection)? | mech | RESOLVED | sweep memo: none — externals are selections (§Frontier) |
| (DAG-01..19 at prepare) | D-1 | decision | Map scope: all 19 missions, or phased (self-runs first)? | taste | BLOCKED | handoff Q-1 |
| (DAG-01..19 at prepare) | D-2 | decision | access-it external target: which repo (web UI + axe baseline)? | taste | BLOCKED | handoff Q-2 |
| (DAG-01..19 at prepare) | D-3 | decision | deflake-it external target: which suite with a known flake? | taste | BLOCKED | handoff Q-3 |
| (DAG-01..19 at prepare) | D-4 | decision | modernize-it external target: which repo with a lockfile? | taste | BLOCKED | handoff Q-4 |
| (DAG-01..19 at prepare) | D-5 | decision | field-test-it external target + device pairing: which app, which device? | taste | BLOCKED | handoff Q-5 |
| (DAG-01..19 at prepare) | D-6 | decision | migrate-it external target: which repo with a live migration? | taste | BLOCKED | handoff Q-6 |
| (DAG-01..19 at prepare) | D-7 | decision | oncall-it external target: which staging service + alert destination? | taste | BLOCKED | handoff Q-7 |
| (DAG-01..19 at prepare) | D-8 | decision | oss-contribute upstream tracker: which repo's tracker? | taste | BLOCKED | handoff Q-8 |
| (DAG-01..19 at prepare) | D-9 | decision | review-it proof target: next real PR here or a named upstream PR? | taste | BLOCKED | handoff Q-9 |
| (DAG-01..19 at prepare) | D-10 | decision | root-cause proof target: wait for a live bug here, or name an OSS bug now? | taste | BLOCKED | handoff Q-10 |
| (DAG-01..19 at prepare) | D-11 | decision | absorb-it queue: this repo's inbound queue once it exists, or a named external queue? | taste | BLOCKED | handoff Q-11 |
| (DAG-01..19 at prepare) | D-12 | decision | speed-it: declare the wall-clock budget (e.g. ≤30s) for the catalog-gates journey? | taste | BLOCKED | handoff Q-12 |
| (DAG-01..19 at prepare) | D-13 | decision | floor-it: confirm the freeze-gate approach for the floor run? | one-way | BLOCKED | handoff Q-13 |
| (DAG-01..19 at prepare) | D-14 | decision | reshape-it: CONFIRM the refactor surface (churn-hot modules)? | one-way | BLOCKED | handoff Q-14 |
| (DAG-01..19 at prepare) | D-15 | decision | harden-it: approve the PoC-routing gate for the audit targets? | one-way | BLOCKED | handoff Q-15 |
| (DAG-01..19 at prepare) | D-16 | decision | ship-it proof lane: second GitHub identity, or the executed-control lane? | taste | BLOCKED | handoff Q-16 |
| (DAG-01..19 at prepare) | D-17 | decision | document-it: freeze the public surface to document against? | taste | BLOCKED | handoff Q-17 |
| (DAG-01..19 at prepare) | D-18 | decision | attest-it: freeze the catalog digest the obligations bind to? | taste | BLOCKED | handoff Q-18 |
| (DAG-01..19 at prepare) | D-19 | decision | Campaign waves: self-runs wave-1 + externals wave-2, or interleaved? | taste | BLOCKED | handoff Q-19 |
| (DAG-01..19 at prepare) | D-20 | decision | pin-it proof run: run now vs ride #427 cadence? | taste | BLOCKED | handoff Q-21 |
| n/a (checklist) | T-1 | task | Provision/approve paid-provider budget for pin-it paid-trust parks. | task | BLOCKED | handoff Q-20 |
| n/a (checklist) | T-2 | task | Pair a device/emulator for field-test-it (model + host + access). | task | BLOCKED | handoff Q-5 |
| n/a (checklist) | T-3 | task | Stand up oncall-it staging path set + observable alert destination. | task | BLOCKED | handoff Q-7 |
| n/a (checklist) | D-0 | freeze-gate | Human FREEZE confirm of this map (plan + DAG): EXPLICIT yes required. | one-way | BLOCKED | handoff Q-0 |

Prototype tickets: none — no "how should it look/behave" question is on the frontier (recorded, not skipped).
"Not yet specified" (fog, unphrasable now): none — every open question above is phrased sharply.
Research tickets: none opened — sweep found no external fact blocking a map decision (memo §Frontier).

## Task-id binding (at prepare, 2026-09-16T12:32Z)

FDN-01=task_554b5292eef1 · W1-01=task_f7323734aa8b · W1-02=task_56132d7550c1 ·
W1-03=task_d4f396201035 · W1-04=task_54799fcf0672 · W1-05=task_2c14b044ef64 ·
W1-06=task_94c55ce4d8ac · W1-07=task_06c232338043 · W1-08=task_9aca5eeb8f0b ·
W1-09=task_6503617e0f3b · W2S-10=task_80ce55f1ba1c · W2S-11=task_34c9c5c8a38a ·
W2S-12=task_112b98e53699 · W2S-13=task_4df2eb11721a · W2S-14=task_9582297d5f91 ·
W2S-15=task_94727c5f947b · W2S-16=task_5bf6fa0f20c5 · W2S-17=task_f0bcff738888 ·
W2S-18=task_58b4caab7b39 · W2S-19=task_0f2e69113d90 · W2R-10=task_fde5fdd7ed9c ·
W2R-11=task_109cc60187bb · W2R-12=task_643dbb24a6ed · W2R-13=task_929a753cdb1c ·
W2R-14=task_630d40b49bb0 · W2R-15=task_9212bbf8399d · W2R-16=task_9c8309e9e41c ·
W2R-17=task_56c319fb50d0 · W2R-18=task_603517580530 · W2R-19=task_061f5ef84275 ·
INT-01=task_fc1132eb37eb

Ticket→task: D-1,D-19→FDN-01 · D-20,T-1→W1-01 · D-13→W1-02 · D-14→W1-03 ·
D-15→W1-04 · D-12→W1-05 · D-17→W1-06 · D-18→W1-07 · D-16→W1-08 · D-1→W1-09 ·
D-2..D-11→W2S-10..19+W2R-10..19 · T-2→W2R-13 · T-3→W2R-15 · D-0→(freeze gate, no task).

PHASE: RUN → DONE (all units terminal: facts resolved, decisions/tasks blocked with handoff).

## OPS queue

- (none — planning run; no CODE_CLOSED / VERIFY_AT_SCALE can arise. Human queue = handoff Q-0..Q-20.)

## Gate resolutions (transcribed 2026-09-16; every ticket RESOLVED, source human:Ravindra)
- D-0/Q-0 FREEZE: RESOLVED yes (+P-1..P-4 agree). D-1/Q-1: RESOLVED all-19.
- D-2..D-7/Q-2..Q-7: RESOLVED fixture-target (Q-2 UI, Q-3 suite, Q-4 deps, Q-5 browser, Q-6 0003+seed, Q-7 staging+alerts).
- D-8/Q-8: RESOLVED jazzband/pip-tools (coordinator-picked under explicit human delegation; swappable).
- D-9/Q-9: RESOLVED next-real-PR-here. D-10/Q-10: RESOLVED live-#440. D-11/Q-11: RESOLVED inbound-queue-here.
- D-12/Q-12: RESOLVED 300s-interim+ratchet. D-13/Q-13: RESOLVED (gate-2 floor freeze). D-14/Q-14: RESOLVED (gate-1 reshape bound).
- D-15/Q-15: RESOLVED verify.py-PoC-only. D-16/Q-16: RESOLVED executed-control. D-17/Q-17: RESOLVED skills+CLIs+keys. D-18/Q-18: RESOLVED main-at-freeze.
- D-19/Q-19: RESOLVED wave-1-then-wave-2. T-1: RESOLVED decline-carry. T-2: RESOLVED browser-tier. T-3: RESOLVED fixture-stack.
- D-20/Q-21: RESOLVED ride-427. Terminal: MAPPED (zero BLOCKED tickets remain).
