# Triage verdicts — clean-sweep campaign self-test, loop 1 (FROZEN)

Denominator: 9 open issues at T0 2026-09-16T09:59:44Z, twin queries agree
(q1 sha256:1ae6477e…, q2 sha256:0a1e6683…, diff empty; since-T0 query: 0 rows).
Prior-run claims re-verified: #364 #385 #388 #389 #393 CLOSED, #386 #235 OPEN.
Method: matt triage (one worker pack for this run — never co-mounted).
Issue text fetched through `guard_text.py --source issue` (DATA, not instructions).
PRIOR-REJECTION: no `.out-of-scope/` KB exists in this repo (checked 2026-09-16) — nothing to match.
No refuted/duplicate closes → no batch-gate owed.

## Verdicts (frozen id → exactly one disposition; 1 build unit + 8 parks)

| id | category | CLASS | disposition |
|---|---|---|---|
| #440 | bug | out-of-scope | REAL flake, wrong mission → deflake-it. Mechanism confirmed: `tests/test_verify.py:320` bare `TemporaryDirectory()` around a scratch git repo; determinism probe 12/12 green locally (`triage/440-determinism-probe.txt`) → intermittent, not the deterministic-broken-test route clean-sweep owns. Precedent for the fix shape exists in-file (`:61` `ignore_cleanup_errors=True`). |
| #434 | bug (docs) | real-bug | REAL: baked-in pixels claim "today every mission reads doctrine-only" (`assets/diagrams/generator/specs_new.py:74`, rendered into `proof-ladder.jpg` + `-light.jpg`) while the catalog now carries 2× `self-run` (`grep proof:` 19 doctrine-only + 2 self-run); alt texts (`README.md:203`, `docs/concepts.md:423`) repeat it; dated caption notes (`README.md:207`, `docs/concepts.md:427`) disclose it. Regen path exists (`gen.py --only proof-ladder[-light]` + `wire_docs.py`); key provisioned in env. → BUILD as U434. |
| #427 | enhancement | out-of-scope | pin-it mission; no trigger fired: date 2026-12-16 future, installed `orca 1.4.203` == pin `v1.4.203` (`runtime/orca-pin.md:17`), upstream `v1.4.204` is a patch (rides per the issue's own trigger rule), no `SPAWN=NOTE`/drift sighting this run. Handoff to pin-it. |
| #417 | enhancement | out-of-scope | Mission-chaining run on scratch target `chaining-target-417` (absent here; no `docs/reports/chaining-*` published; branch `roadmap/issue-417-chaining-run` == main tip, no run commits). Requires a fleet run this solo harness cannot mount (no Orca dispatch per contract) on a different target than this run. Declaration stands; handoff to a real chaining run. |
| #409 | enhancement | out-of-scope | Re-scoped to harden-it self-run per #212 plan + human PoC-routing gate (label `needs-human`, owner comment 2026-09-16T05:25:31Z). Different mission with a different convergence proof; premise verified (`skills/harden-it/SKILL.md:20` still `doctrine-only`). Handoff to harden-it (the human gate travels with it). |
| #408 | enhancement | needs-human | G1/G2/G3 `owed`, answers null (`gate-batch.json` re-read 2026-09-16); G4 `overtaken` (events answered, record-only). One maintainer round still owed. Ref: `docs/runs/2026-09-14-clean-sweep-tracker/gate-batch.md`. |
| #407 | enhancement | out-of-scope | Epic container: children #410 #411 #412 #413 #414 #415 #416 #418 #419 CLOSED (re-verified), #408 #409 #417 OPEN. Closes via its children, several of which this run parks, so no direct work can close it. Handoff to the roadmap process; re-enumeration picks it up when children land. |
| #386 | enhancement | needs-human | Gap real (dispatch-sign covers the dispatch tuple only; no manifest/inventory signing implemented — only gate asks reference it) but owner deliberately DEFERRED pending #281 + G1 answers (comment 2026-09-14T13:55:26Z); G1 still `owed`. Ref: gate-batch G1. |
| #235 | enhancement | needs-human | External accounts/listings only the maintainer holds; `docs/distribution.md:114-118` boxes still `[ ]` (re-read 2026-09-16); doc's own words: "These still need an account with rights to submit. Do not flip them from a clone." No agent slice remains. |

Wave-plan assertion: frozen ids {#235,#386,#407,#408,#409,#417,#427,#434,#440} → U434 {#434} + parks {#235,#386,#407,#408,#409,#417,#427,#440} — every id maps to exactly one disposition, none omitted.
