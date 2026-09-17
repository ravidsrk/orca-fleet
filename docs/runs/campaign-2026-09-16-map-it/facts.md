# Frontier facts (coordinator-cleared, AFK) — F-1..F-3

All read from the tree @ `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip).

## F-1: doctrine-only set + field-proof prescription — RESOLVED

`python3 runtime/scripts/proof_status.py --check` (2026-09-16, exit 0):

- self-run (2): clean-sweep, prove-it
- doctrine-only (19): absorb-it, access-it, attest-it, deflake-it, document-it,
  field-test-it, floor-it, harden-it, map-it, migrate-it, modernize-it, oncall-it,
  oss-contribute, pin-it, reshape-it, review-it, root-cause, ship-it, speed-it

Prescription per mission (verbatim from `docs/runs/README.md` §Field-proof plan (#212)):

| Mission | Target | Tier | Terminal | Blocker |
|---|---|---|---|---|
| map-it | this catalog (report-only) | self-run | MAPPED | Orca only |
| attest-it | this catalog vs agentskills.io spec @ digest | self-run | CONFORMANT (-WITH-GAPS) | Orca; frozen catalog digest |
| harden-it | verify.py, dispatch-sign.py, verify-gate.sh | self-run | CLEAN | Orca; PoC-routing gate (human) |
| speed-it | catalog-gates journey, declared budget e.g. ≤30s | self-run | WITHIN-BUDGET | Orca; declared budget (human) |
| root-cause | next real defect here, or open bug in small OSS repo | self/external | DIAGNOSED | live bug + Orca |
| access-it | external repo with axe-core baseline | external-run | CONFORMANT (-WITH-MANUAL-PARKED) | target + Orca |
| deflake-it | external suite with known flake | external-run | STABLE | target + Orca |
| modernize-it | external repo with lockfile | external-run | CURRENT | target + Orca |
| pin-it | runtime/*.md + runtime/scripts/ vs installed Orca CLI | self-run | PINNED (-WITH-PARKED) | Orca (re-witness oracle) |
| floor-it | catalog: suite, validate.py, ruff, badge freshness | self-run | FLOORED | Orca; freeze gate (human) |
| reshape-it | churn-hot modules (verify.py / validate.py) | self-run | RESHAPED | Orca; CONFIRM-SURFACE (human) |
| field-test-it | external mobile repo | external-run | FIELD-PROVEN | target + paired device |
| review-it | next real PR here or upstream | external-run | NO-GO / GO | Orca; live PR + retained artifacts |
| ship-it | next mutating slice here | self-run | BUILT min | Orca; 2nd identity or executed-control lane |
| oss-contribute | next upstream tracker | external-run | CONTRIBUTED (-WITH-PARKED) | Orca; upstream target + retained artifacts |
| absorb-it | own inbound queue once it exists, else external queue | external-run | ABSORBED (-WITH-PARKED) | Orca; queue that exists |
| document-it | catalog zero-coverage doc cells (runtime/scripts/) | self-run | DOCUMENTED | Orca; frozen public surface |
| migrate-it | external repo with live migration | external-run | MIGRATED | target with real data + Orca |
| oncall-it | bounded external staging-service path set | external-run | OPERABLE (-WITH-PARKED) | Orca; staging + alert destination + human gates |

Count check: 9 self-runs with in-catalog targets (map-it, attest-it, harden-it, speed-it,
pin-it, floor-it, reshape-it, ship-it, document-it), 10 needing external/live selection
(root-cause, access-it, deflake-it, modernize-it, field-test-it, review-it,
oss-contribute, absorb-it, migrate-it, oncall-it).

## F-2: binding bar — RESOLVED

From `docs/runs/TEMPLATE.md` §Catalog proof promotion + `runtime/scripts/run_report.py`:

1. `RUN:` header exactly once (mission, tier, inventory_at commit in-repo, manifest in run's
   own `docs/runs/<date>-<mission>…/` dir, verifier GREEN|RED, waves).
2. Body shows the ACTUAL `verify.py … --manifest <same path>` invocation + exit.
3. Integrity inventory re-hashes at inventory_at: zero mismatches, ≥1 verified path in the
   run's own dir, graded manifest among hashed paths, no run-owned artifact absent.
4. `scripts/validate.py` + `python3 -m unittest discover -s tests` +
   `proof_status.py --check` green; mission frontmatter `proof:`/`proof_evidence:` set.

Consequence for the map: every per-mission run card carries this bar verbatim as its
acceptance criterion; a run that keeps artifacts outside its own dir binds nothing.

## F-3: tracker issues deciding map pieces — RESOLVED (via guard_text fence)

- #427 (OPEN): next pin-it re-pin trigger 2026-12-16 / next Orca minor / drift sighting;
  inherits the #416 park register. Map consequence: pin-it proof run timing is a scheduling
  call → new sharp ticket D-20 (run now vs ride #427 cadence).
- #441 (OPEN): mission-chaining has no inter-mission promotion lane (chains park after leg 1).
- #442 (OPEN): verify.py assumes unit repo == evidence repo (breaks chained runs).
- #443 (OPEN): deferral carry has no artifact shape. #444 (OPEN): local-only re-derivability undefined.
- Map consequence: chained consumption of this map is degraded until #441–#444 close; each
  mission run is therefore ticketed as a directly-consumable unit (ship-it adopts per-mission
  without re-grilling; chaining rides only after the lane exists). Recorded as a plan
  constraint, not a ticket — the issues are facts, the workaround is in the DAG shape.
