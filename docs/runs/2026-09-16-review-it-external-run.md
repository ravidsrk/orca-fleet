# THROWAWAY — bound review-it fixture to prove #415 bind-check goes GREEN

This file exists only to exercise the `bind-check` CI job added for
https://github.com/ravidsrk/orca-fleet/issues/415 — it binds (every leg
re-derives), it proves no mission ran (there was no mission, no frozen
contract, no dispatch), and the branch carrying it is deleted after the
job output is captured. Do not merge. A bound fixture is still a
fixture: binding proves the evidence is retained and the invocation is
recorded, not that a mission happened.

RUN: mission=review-it tier=external-run inventory_at=067e96121a38f84702303d6f5acd40d27a2b37e1 manifest=docs/runs/2026-09-16-review-it-external-run/manifest.json verifier=RED

| Field | Value |
|---|---|
| Mission | `review-it` — fixture run, no mission executed |
| Tier claimed | `external-run` (fixture claim on a throwaway branch; never promoted) |
| Runner | INTAKE FIXTURE — no mission ran (runner-credit row shape per the submission guide) |
| Run PR | `throwaway/415-green-proof` (URL recorded in #415; branch deleted after capture) |

## Verifier outcome (recorded exactly)

Recorded through `evidence-run.py` against the seed manifest (no frozen
contract exists for a fixture, so the scope legs fail closed — the honest
outcome, kept RED):

```text
python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-16-review-it-external-run/manifest.json --unit-class report-only
FAIL: scope: no authoritative contract (--contract-source/--contract-digest from the dispatch record) — a worker manifest cannot certify its own denominator
FAIL: oracle scope: authoritative contract unreadable or digest mismatch
FAIL: missing required 'base_sha'
FAIL: missing required 'head_sha'
FAIL: report-only unit with no signed dispatch record, and its shape cannot be determined: base_sha and head_sha must both be pinned 40-hex commits before the class claim can be measured against the change. Pin base_sha and head_sha so the claim can be measured against the change, or have the coordinator sign the downgrade (#310)
verify: 5 invariant(s) failed — unit is NOT done
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
exit 2
```

The manifest's `commands[]` ledger carries this same invocation with its
`cmd_sha256` and working-tree fingerprint (see the manifest — the record
`evidence-run.py` wrote, not prose about it).

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| docs/runs/2026-09-16-review-it-external-run/manifest.json | 9eab900bcffe68e78f74dd24370dffa8cf4e923df79f0d4d637d2c407ea8cbdd | evidence-run.py (fixture, 2026-09-16) |
| docs/runs/2026-09-16-review-it-external-run/verifier.txt | cc5952ec1f7d9cfe2b8b963b3fd7482938650859109a54a7d6400457af9a9e8f | verify.py via evidence-run.py (fixture, 2026-09-16) |
| docs/runs/2026-09-16-review-it-external-run/negctrl.txt | 2266c1c98be1a3545d272d35c3ddea26bf140fb4a223124086d72a2e942a1992 | fixture author (2026-09-16) |
