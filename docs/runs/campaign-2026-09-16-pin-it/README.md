# pin-it selftest campaign — Orca 1.4.203 afternoon re-pin (2026-09-16)

**PINNED-WITH-PARKED.** Not PINNED. Installed binary is the oracle. This is a bounded
re-witness in the morning pin's shape (`docs/runs/2026-09-16-pin-it-416/`), not a proof-tier
bid: pin-it stays `doctrine-only`, and this directory is campaign evidence, not an archive row.

| | |
|---|---|
| RUN | `-` (no Run created — read-only session, no sender terminal; see Park register) |
| COORDINATOR | `-` (plain shell; orchestration mutations refuse with `no_active_sender_terminal`/`no_active_terminal` here) |
| BASE | `campaign/pin-it-selftest` |
| FORK_POINT | `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip at T0) |
| T0 | 2026-09-16T13:02:36Z |
| FREEZE | 2026-09-16T13:05:00Z (`CLAIMS.md` — 32 claims + 10 parks; set never changed after) |
| SOURCE | `CLAIMS.md` digest `34ed75e5…` + CLI 1.4.203 `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec` |
| WIP | builders=0 reviewers=0 (coordinator-only re-witness; zero packs mounted — one-router rule vacuous) |
| HEAD (evidence) | `1892ef9ab218645555eee90ae9349ed8d4ac7daa` (frozen evidence; report layer closes in the follow-up commit) |

## Oracle

- CLI `orca --version` → `1.4.203` ([receipt](receipts/installed-version.txt),
  sha256 `e714f547…` — identical to the morning pin's recorded hash)
- `orca-local-build.json` commit `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec`, daemon
  protocol 36 — IDENTICAL to the live pin (build-identity holds all source anchors; no re-read theater)
- Upstream HEAD at witness time: `0b28d354fefada8e3a9eb720af0fe53d15fffe8d` — moved since
  the pin's `feb04ec`; recorded, not chased (pin-it pins the installed build)
- Guides archived under [guides/](guides/): `orchestration` + 7 references, `orca-cli` + 3
  references, plus `orca-per-workspace-env` — 15/15 byte-identical to the morning pin
- Machine schema [receipt](receipts/agent-context.json): `orca agent-context --json`
  (234 commands, sha256 `4b17e5d2…` — identical to the pin's) — every CLI-shape claim replayed against it
- Runtime `orca status --json` → `runtime.reachable: true`, app 1.4.203

## Guide diff (morning pin → this run, same build)

Zero. All 15 archived references byte-identical (`cmp` clean, and our fresh sha256 match the
pin's `inventory.txt` line-for-line through an independent re-hash). No doctrine contradicts
anything because nothing moved; the `@all` replay probe stays owed (B03).

## Drift table — policies (in-scope re-witnessed; fleet-only cut)

| Policy | Verdict | Evidence |
|---|---|---|
| `dispatch-lifecycle.md` | CURRENT | C01/C02/C05–C07/C31: schema + live receipts; behavior halves (C03/C04) PARKED with substrate proof. Post-pin diff IS the pin's own fix commits — no new sentences. |
| `liveness-resume.md` | CURRENT | C08/C09/C10: projection shapes + reclaimable gate live; C11 PARKED. |
| `orca-dag-semantics.md` | CURRENT | C20 schema-verified; C19 PARKED (B02). |
| `merge-serialization.md` | CURRENT | C17/C18 schema notes live. |
| `gate-classification.md` | CURRENT | C12/C13 shapes live; behavior halves PARKED (B05/B08). |
| `sandbox-policy.md` | CURRENT | C15 map held by build-identity; C16 doctor text matches the identical guide bytes. |
| `mission-scheduling.md` | CURRENT | C22: 27-flag `automations create` schema + live `list`. |
| `worker-supervision.md` | CURRENT | C21 shapes live; the +21 post-pin watchdog section is fleet tooling, no Orca mechanics. |
| `evidence-manifest.md` | CURRENT (cite only) | C24 `--report-path` in schema; the protocol itself is fleet SCOPE-CUT. |
| `reviewed-sha-freshness.md` | SCOPE-CUT | Fleet-only, no Orca surface. Never in inventory. |
| `ledger-contract.md` | SCOPE-CUT | Fleet-only. |
| `attention-budget.md` | SCOPE-CUT | Fleet-only. |
| `mission-chaining.md` | SCOPE-CUT | Fleet-only. |

## Drift table — scripts (new files triaged; fleet-only cut)

| Script | Verdict | Evidence |
|---|---|---|
| `spawn_worker.sh` | CURRENT | C23: relied shapes schema-verified, anchors held by build-identity. |
| `sandbox_doctor.py` | CURRENT | C27: inspection — no pinned shape to drift. |
| `pm.py` | CURRENT | C25: held by build-identity (untouched since the pin's re-confirm). |
| `deny-hook.sh` | CURRENT | C26: `orchestration reset` still a real verb. |
| `gate-batch.py` (NEW) | SCOPE-CUT | Zero `orca`/orchestration hits — fleet JSON store, correctly out of inventory. |
| `watchdog.py` (NEW) | SCOPE-CUT | Zero `orca` CLI calls — fleet classifier, correctly out. |
| 16 other scripts | SCOPE-CUT | Fleet-only, no Orca surface (see CLAIMS.md scope cut). |

## Live classifications this run

24 CURRENT · 0 STALE · 0 SUPERSEDED · 10 parks re-owed. Full table: [CLASSIFICATION.md](CLASSIFICATION.md).

| Claim | Receipt | Class |
|---|---|---|
| Installed version vs `runtime/pins.json` | [installed-version.txt](receipts/installed-version.txt) `1.4.203` | CURRENT (pin already at this build — no rewrite; see Deviation D3) |
| `worker-list --run <id>` scopes to that Run | [worker-list-bound.json](receipts/worker-list-bound.json) `scope.source=flag`, total 159 | CURRENT |
| Unscoped `worker-list` enumerates runtime history | [worker-list-unscoped.json](receipts/worker-list-unscoped.json) `scope.source=all`, total 460 (+2 live rows vs pin — activity, not drift) | CURRENT |
| `worker-list --from` | [worker-list-from-no-run.json](receipts/worker-list-from-no-run.json) `invalid_argument` | CURRENT |
| `worker-list --terminal-state reclaimable` | [worker-list-reclaimable.json](receipts/worker-list-reclaimable.json) exit 0, total 25 | CURRENT |
| `projection.liveness/attention/nextAction` rows | shape rows (`unverifiable/missing_status`, `exited`, `release` argv) | CURRENT |
| All CLI-shape claims | [agent-context.json](receipts/agent-context.json) byte-identical (234 cmds, 0 flag diffs) | CURRENT |
| `orchestration run` retired alias | [retired-run-alias.txt](receipts/retired-run-alias.txt) | CURRENT |
| `terminal stop` deprecated | [terminal-stop-deprecated.txt](receipts/terminal-stop-deprecated.txt) | CURRENT |
| Control-plane MUTATES (pin-it preamble) | [substrate-run-create.json](receipts/substrate-run-create.json) + [substrate-check-peek.json](receipts/substrate-check-peek.json) | CURRENT (refusals-before-effects prove the guarded live surface) |
| Sender-bound behaviors (10 families) | substrate receipts (precondition proof) | PARKED — [PARK.md](PARK.md) |

## Convergence proof (mission §Convergence proof, clause by clause)

- Every claim accounted: 24 CURRENT with captured receipts, 0 PATCHED (nothing stale), 0
  REMOVED, 8 claims with PARKED behavior halves naming probes B01–B10 ([CLASSIFICATION.md](CLASSIFICATION.md)). Inventory set frozen in [CLAIMS.md](CLAIMS.md) == classified set — no row added, none removed.
- Claim-level negative control (§1 carve-out): VACUOUS — zero patches means zero refutation
  receipts owed ("a patch whose old text still probes GREEN" cannot exist when nothing was
  patched). Recorded in [manifest.json](manifest.json) `negative_control` as explicit N/A, not omitted.
- Receipts name the CLI version: all captured from 1.4.203 ([installed-version.txt](receipts/installed-version.txt)); build commit independently re-read from `orca-local-build.json`.
- Verifier ≥10% sample: exceeded — 100% of probes were re-executed post-freeze in the formal
  pipeline (pre-freeze survey discarded for order; see Deviation D1). Every probe is a re-runnable
  one-liner in [manifest.json](manifest.json) `commands[]`.
- Repo gates green at the landing SHA: `scripts/validate.py` exit 0; `python3 -m unittest
  discover -s tests` exit 0; `proof_status.py --check` exit 0 (19 doctrine-only, 2 self-run —
  recorded below).

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| FREEZE | wrote `CLAIMS.md` (32+10, scope cut declared) | 2026-09-16T13:05:00Z, digest `34ed75e5…` | [CLAIMS.md](CLAIMS.md) |
| BASE | `preflight.py --base campaign/pin-it-selftest --fork-point c46d4b3f…` | OK (exit 0) | [transcripts/preflight.txt](transcripts/preflight.txt) |
| LOAD | `skills get <orchestration\|orca-cli> --references` + every `--reference` + `orca-per-workspace-env` | 15 files, all byte-identical to pin | [guides/](guides/) |
| RE-WITNESS | schema + 8 read-only probes + 2 substrate probes (post-freeze) | 8 green, 2 substrate-refused (pre-effects) | [receipts/](receipts/) |
| CLASSIFY | receipt-only verdicts | 24/0/0/10 | [CLASSIFICATION.md](CLASSIFICATION.md) + [transcripts/classification-checks.txt](transcripts/classification-checks.txt) |
| PATCH | remediate-finding: zero findings | NO-OP (documented) | CLASSIFICATION.md §PATCH |
| REVIEW | acceptance-review: no diff | VACUOUS (documented, solo-run honesty note) | CLASSIFICATION.md §REVIEW |
| LAND | merge-serialization: no PR | NOTHING TO LAND | CLASSIFICATION.md §LAND |
| VERDICT | PINNED-WITH-PARKED | 10 parks re-owed to #427 | [PARK.md](PARK.md) |
| REFLECT | compound-learn proposal | 4 GOTCHAS lines (unapproved) + 1 backlog item | [REFLECTION.md](REFLECTION.md) |

## Deviations (recorded, not hidden)

- D1 (corrected in-run): scoping probes ran before the freeze file existed. Corrected by
  re-executing the full BASE→LOAD→REPLAY pipeline post-freeze with fresh captures
  (`ls -laT` order: CLAIMS.md 18:35:22 → guides 18:35:45 → receipts 18:35:46+); the survey
  captures were overwritten, not kept.
- D2: probes ran via direct shell with transcripts, not `evidence-run.py` (its wtree
  fingerprint binds code content; these captures bind the *binary*, and the receipts themselves
  are the artifacts). Commands + exits recorded in [manifest.json](manifest.json).
- D3: `orca-pin.md` + `pins.json` NOT rewritten at close (same build + zero drift ⇒ a rewrite
  is a no-op date bump; the sanctioned rewrite lane is issue #427). The pin record stays
  authoritative and correct — this run corroborates it instead of churning it.

## Teardown

Nothing to tear down: no Orca state created (substrate probes refused pre-effects; all other
probes read-only). No `reset`, no push, no upstream change of any kind.

## Integrity inventory (sha256)

Per-file hashes of this run's evidence: [inventory.txt](inventory.txt) (generated post-freeze;
`inventory.py`-style `sha256  path` lines over guides/ + receipts/ + records).

## Gates (exact output)

- `python3 scripts/validate.py` → exit 0 ("All 21 missions valid; three-layer separation holds; evals valid.")
- `python3 -m unittest discover -s tests` → exit 0 (full suite green; badge-writer lines are suite self-output, working tree left clean)
- `python3 runtime/scripts/proof_status.py --check` → exit 0 (coverage rollup: doctrine-only 19, self-run 2, external-run 0, total 21)
