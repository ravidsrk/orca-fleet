# Classification — from receipts only (2026-09-16T13:10:00Z)

Source-of-truth rule honored throughout: guides are the MAP, receipts are the PROOF. Every
CURRENT below cites a receipt captured from the installed binary (1.4.203) in this run's
`receipts/`; every PARK cites the substrate receipt that proves the precondition failed.
Nothing was classified from guide text alone; nothing substrate-blocked was reclassified.

## Oracle (recorded, not chased)

- CLI: `1.4.203` (`receipts/installed-version.txt`, byte-identical to the morning pin)
- Build: `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec`, daemon protocol 36
  (`/Applications/Orca.app/Contents/Resources/orca-local-build.json`) — IDENTICAL to the live pin
- Upstream HEAD: `0b28d354fefada8e3a9eb720af0fe53d15fffe8d` (moved since the pin's `feb04ec`; the
  pin tracks the installed build, so this is recorded, not chased)
- Guides: 15/15 byte-identical to `docs/runs/2026-09-16-pin-it-416/guides/` (zero guide drift in ~7.5h)
- Schema: `receipts/agent-context.json` byte-identical to the pin's (234 commands, 0 flag diffs)
- Runtime: `orca status --json` → `runtime.reachable: true`, app 1.4.203

## Verdicts (32/32 accounted; inventory set unchanged — no row added, none removed)

| ID | Verdict | Receipt (this run) |
|---|---|---|
| C01 | CURRENT | schema: `worker-start` carries task/worktree/agent/setup/json (`transcripts/classification-checks.txt`) |
| C02 | CURRENT | schema `send` notes: `worker_done requires --outcome`; omitted `--to`→Run mailbox; contract example at `guides/orchestration-worker-contract.md:71` |
| C03 | PARKED (B02) | BEHAVIOR needs a consuming `check` in a scratch Run; plain-shell `check --peek` refuses `no_active_terminal` (`receipts/substrate-check-peek.json`) — precondition verdict, mechanism untouched |
| C04 | PARKED (B09) | BEHAVIOR needs live dispatches; `run-create` refuses `no_active_sender_terminal` (`receipts/substrate-run-create.json`) |
| C05 | CURRENT (read-only half) + PARKED (B01, behavior half) | `scope.source=flag`, total 159, retained 112/released 47 — identical to the morning pin (`receipts/worker-list-bound.json`); scope-behavior replay still owed |
| C06 | CURRENT | schema `terminal close --all` + `worktree rm --worktree`; `terminal stop` still the deprecated page (`receipts/terminal-stop-deprecated.txt`) |
| C07 | CURRENT | `orchestration run --help` resolves to the retired `coordinator-start` page (`receipts/retired-run-alias.txt`, byte-identical to pin) |
| C08 | CURRENT | unscoped `scope.source=all`, total 460 (+2 live rows vs the pin's 458 — runtime activity, not drift); projection keys live (`receipts/worker-list-unscoped.json`) |
| C09 | CURRENT | `--terminal-state reclaimable` exit 0, total 25 (`receipts/worker-list-reclaimable.json`) |
| C10 | CURRENT | `unverifiable/missing_status`, `exited`, `release` argv all live in shape rows (three receipts) |
| C11 | PARKED (B04) | dep-validation replay needs a live terminal (substrate proof: `receipts/substrate-run-create.json`) |
| C12 | CURRENT | schema: `ask --options` + `gate-create --options` both present; CSV-vs-JSON-array spelling held at the same build commit by identity (no re-read theater — the commit is cryptographically identical) |
| C13 | CURRENT (shape) + PARKED (B08, behavior) | schema `ask --resume` + `reply --id` present; block/timeout/resume behavior owed |
| C14 | PARKED (B05) | preamble-inspection replay needs a live terminal (substrate proof: `receipts/substrate-run-create.json`) |
| C15 | CURRENT (map) + PARKED (B06, live half) | YOLO map held at the identical build commit; `launch.effective` recording owed to a live spawn |
| C16 | CURRENT | guide doctor-verdict text matches doctrine verbatim ("clear only with no `fail` and no `warn` … `ok` alone proves nothing"); guide bytes identical |
| C17 | CURRENT | schema `send` notes: omitted-recipient default + group-fanout (`merge_ready` NOT refused) live |
| C18 | CURRENT | `merge_ready` in valid `--type` values with no behavior note — fleet-owned, as taught |
| C19 | PARKED (B02) | `--types` wake-only replay needs a live terminal (substrate proof: `receipts/substrate-check-peek.json`) |
| C20 | CURRENT | schema `task-create --deps/--parent` both exist; fleet-sets-deps-only is policy, unchanged |
| C21 | CURRENT | schema `worker-read --dispatch`, `run-use --from`, `send --to` all present |
| C22 | CURRENT | schema `automations create` (27 flags incl. `precheck`) + `automations list` exit 0 (`receipts/automations-list.txt`) |
| C23 | CURRENT | relied shapes (`worker-start`, release, refusal codes) schema-verified; source anchors held by build-identity |
| C24 | CURRENT | schema `send --report-path` present |
| C25 | CURRENT | keepalive contract held by build-identity (same commit; `pm.py` untouched since the pin's re-confirm) |
| C26 | CURRENT | schema still carries `orchestration reset` — the deny-hook string still matches a real verb |
| C27 | CURRENT | inspection: generic finding/status parse, zero Orca surface — nothing to drift |
| C28 | CURRENT | `guides/orchestration-worker-contract.md` byte-identical; `--from/--dispatch-capability`, typed flags, `check --terminal`, `consumer_fenced`→stop all live in text |
| C29 | CURRENT | substrate receipts PROVE the claim: control-plane calls refuse before effects without a sender (`no_active_sender_terminal` + `no_active_terminal`) — the mutation surface is real and guarded |
| C30 | PARKED (B03) | group-scoping replay owed; the 1.4.203 guide text is the map (byte-identical), never the proof |
| C31 | CURRENT | typed-code envelope live: `invalid_argument` + `validFlags` + `nextSteps` (`receipts/worker-list-from-no-run.json`, byte-identical shape to pin) |
| C32 | PARKED (B07) | inject-receipt replay needs a live terminal (substrate proof: `receipts/substrate-run-create.json`) |

Totals: 24 CURRENT · 0 STALE · 0 SUPERSEDED · 8 claims with PARKED behavior halves (10 parks B01–B10) · 0 substrate misclassifications.

## New-since-pin review (post-`36061cea` mergers)

- `runtime/scripts/gate-batch.py` (644 lines): zero `orca`/orchestration/gate-create hits — a fleet
  gate-batch JSON store (G1..Gn), not Orca DAG gates. Fleet-only, correctly OUT of inventory.
- `runtime/scripts/watchdog.py` (470 lines): zero `orca` CLI calls — a fleet heartbeat classifier
  (`--dry-run` = zero subprocess). Fleet-only, correctly OUT of inventory.
- `runtime/worker-supervision.md` +21 (watchdog section): describes fleet tooling, no Orca mechanics.
- No `runtime/*.md` Orca-mechanics sentence changed after the pin's own doctrine-fix commits
  (`45e21942`, `95444e75`); the `05081149..HEAD` runtime diff IS those pin commits plus the two
  fleet-only scripts above.

## PATCH phase (remediate-finding): NO-OP

Zero STALE + zero SUPERSEDED = zero findings to remediate. No doctrine line was touched, so
remediate-finding's failing-first requirement has no instantiation this run (there is no pre-patch
RED to archive because there is no patch). The one-worker-playbook-router rule is satisfied
vacuously (no worker TASK dispatched).

## REVIEW phase (acceptance-review): VACUOUS

No diff → no review surface. Every CURRENT line traces to a receipt in the table above (the
review's core check, applied to the classification rather than a patch). Solo-run honesty note:
this run had no second identity, so HAD there been a patch, its review could not have been
build-blind and the unit could not have closed without the executed-control lane. There was no
patch, so no gate was waived.

## LAND phase (merge-serialization): NOTHING TO LAND

No doctrine patch → no PR, no conductor queue, no reviewed-SHA to keep fresh. The campaign evidence
commit (this directory) is the run's own record on its own branch, not a doctrine change — it
travels by direct commit, never through the merge train.
