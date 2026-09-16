# pin-it for #416 — Orca 1.4.203 live re-pin

**PINNED-WITH-PARKED.** Not PINNED. Installed binary is the oracle.

| | |
|---|---|
| RUN | `-` (no Run created — read-only session, no sender terminal; see Park register) |
| COORDINATOR | `-` (plain shell; orchestration mutations refuse with `no_active_terminal` here) |
| BASE | `roadmap/issue-416-pinit` |
| FORK_POINT | `fff8810cddce880ee51ae1392b1cb7d1a596b33e` |
| T0 | 2026-09-16T05:39:33Z |
| SOURCE | drift table below (13 policies + 20 scripts) + CLI 1.4.203 `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec` |
| WIP | builders=0 reviewers=0 |

## Oracle

- CLI `orca --version` → `1.4.203` ([receipt](receipts/installed-version.txt))
- `orca-local-build.json` commit `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec`
  (2026-09-15), daemon protocol 36; the commit exists upstream, so source anchors
  re-read at exactly the build tree.
- Upstream HEAD at witness time: `feb04ec254585ba69587699d41f80a72dda2cb27`
  (main, 2026-09-16T05:23:22Z) — recorded, not chased: pin-it pins the installed
  build, not upstream HEAD.
- Guides archived under [guides/](guides/): `orchestration` + 7 references,
  `orca-cli` + 3 references, plus `orca-per-workspace-env` (the doctor-verdict rule).
- Machine schema [receipt](receipts/agent-context.json): `orca agent-context --json`
  (234 commands) — every CLI-shape claim below replayed against it.

This continues the 2026-09-13 inventory (`docs/runs/2026-09-13-pin-it-266/`). The
inventory is not shrunk: its 373 unfinished children stay unfinished, and this run's
park register re-owes the sender-bound replays at 1.4.203.

## Guide diff (1.4.200 → 1.4.203)

11 of 12 archived references byte-identical. The one delta is additive text in
`orchestration/messaging-and-gates` documenting group-address scoping: every group but
`@worktree:<id>` reaches the live Dispatches of the sender's own Run; a sender bound
to no Run is refused; `--run` must match the audience and never grants membership; a
Run group excludes its owning coordinator (`send --to @all` in a scratch Run is probe 3
in `dispatch-lifecycle.md` — still owed, now with this text as its map). The same
scoping now appears in the CLI spec notes (`orchestration.ts`). No doctrine contradicts
it, so no doctrine changed for it — and none was ADDED from the guide alone (a guide is
a map, never proof).

## Drift table — policies (13/13, every row a verdict)

| Policy | Verdict | Evidence |
|---|---|---|
| `dispatch-lifecycle.md` | **DRIFT-FIXED** | v1.4.200 mentions → v1.4.203; `:74-76`→`:76-77`, `:102`→`:101`; `runtime-terminal-contracts` disambiguated to `src/shared/`; probe 3 annotated with the new group-scoping map. Shapes re-witnessed via schema; `retired-run-alias`, `terminal-stop-deprecated` receipts. Sender-bound replays PARKED. |
| `liveness-resume.md` | **DRIFT-FIXED** | Re-witness note → this run; three `at v1.4.199` cites → v1.4.203 (guide bytes identical; `task-store` content holds). `projection.liveness/attention/nextAction` re-witnessed LIVE (`worker-list-*.json`: literal `release` argv, `reclaimable` gate, `missing_status` vocab). Refutation replays PARKED. |
| `orca-dag-semantics.md` | **DRIFT-FIXED** | `:134`→`:136`, `:112`→`:114`, `:49,79`→`:49,81`; note → this run. Schema line v40 confirmed (highest migration `migrate-v40.ts`); Delivery 50, wake, nine-type enum confirmed at the build commit. |
| `merge-serialization.md` | CURRENT | `:78` and `:51-58` exact at the build commit; group/`merge_ready` claims consistent with the new guide text. No change. |
| `gate-classification.md` | **DRIFT-FIXED** | `:205,253`→`:205,256` (ask CSV / gate JSON-array confirmed in schema + source). Gate-absence in the live preamble builder source-corroborated (60-line builder, no gate context; retired path still injects). Live probe PARKED. |
| `sandbox-policy.md` | **DRIFT-FIXED** | `cursor :21`→`:25` (4 agents added above it); YOLO map `L7-33` + `YOLO_TUI_AGENT_ENV` sentence (no read-only tier still holds); note → this run. Doctor rule re-confirmed in the 1.4.203 workspace-env guide. |
| `mission-scheduling.md` | **DRIFT-FIXED** | Note → this run only: precheck `:62` exact, every `automations create` flag schema-verified. |
| `worker-supervision.md` | CURRENT | New since the last pin. CLI shapes schema-verified (`worker-read --dispatch`, `run-use --from`, `send --to`); `stable_pane_required` + `terminal_handle_stale` source-confirmed. ASSERTED thresholds are fleet policy, not Orca mechanics — untouched. |
| `evidence-manifest.md` | CURRENT | Fleet protocol; `--report-path` typed flag schema-verified. No change. |
| `reviewed-sha-freshness.md` | CURRENT | Fleet-only, no Orca surface. No change. |
| `ledger-contract.md` | CURRENT | Fleet-only, no Orca surface. No change. |
| `attention-budget.md` | CURRENT | Fleet-only (+ a `worker-list` projection reference, re-witnessed live). No change. |
| `mission-chaining.md` | CURRENT | Fleet-only, no Orca surface. No change. |

## Drift table — scripts (20/20, every row a verdict)

| Script | Verdict | Evidence |
|---|---|---|
| `spawn_worker.sh` | **DRIFT-FIXED (comments only)** | Stale `droid has no flag` comment corrected (`--auto high` is in the YOLO map and the script's own lanes); `cursor :21`→`:25`; launch-defaults/strip/unsupervised tags → v1.4.203; `terminal.ts :126-130`→`:125-129`; `next release flips` → past tense (v1.4.200 shipped it); re-witness header line. Behavior untouched — every relied behavior holds (YOLO map, release contract, readiness, refusal codes all re-read at the build commit; per-code anchors `:13/:18/:52/:49/:117` exact). Pin-coupled `test_spawn_worker.py` assertions → v1.4.203. |
| `sandbox_doctor.py` | CURRENT | Structural parse over generic finding/status keys — no pinned upstream shape to drift. Doctor rule re-confirmed in the 1.4.203 guide. |
| `pm.py` | **DRIFT-FIXED (comment tags)** | Keepalive cites `at v1.4.199` → v1.4.203 (stderr + `_keepalive`/`_heartbeat` re-confirmed in `--help` and source). Parser untouched. |
| `deny-hook.sh` | CURRENT | Denies `orca orchestration reset` by command string; the verb still exists. `ORCA_UNIT_WORKTREE` is fleet env. |
| `dispatch-sign.py` | CURRENT | Fleet crypto; `ORCA_*` names are the fleet's own contract. |
| `egress.py` | CURRENT | Fleet ledger; env name only. |
| `verify-gate.sh` | CURRENT | Fleet env names only. |
| `verify.py` | CURRENT | Fleet verifier; env names only. |
| `decisions.py` | CURRENT | Fleet-only, no Orca surface. |
| `diff_scope.py` | CURRENT | Fleet-only, no Orca surface. |
| `ed25519.py` | CURRENT | Fleet-only, no Orca surface. |
| `evidence-run.py` | CURRENT | Fleet-only, no Orca surface. |
| `floor_guard.py` | CURRENT | Fleet-only, no Orca surface. |
| `guard_text.py` | CURRENT | Fleet-only, no Orca surface. |
| `hitl-loop.template.sh` | CURRENT | Fleet-only template. |
| `inventory.py` | CURRENT | Fleet-only, no Orca surface. |
| `preflight.py` | CURRENT | Fleet + git invariants; no Orca CLI reliance. |
| `proof_status.py` | CURRENT | Fleet-only, no Orca surface. |
| `run_report.py` | CURRENT | Fleet-only, no Orca surface. |
| `wtree.sh` | CURRENT | Pure git fingerprinting; no Orca reliance. |

Also: `pins.json` orca entry → v1.4.203 (this run's core deliverable);
`one-way-doors.json` CURRENT (fleet registry); `orca-pin.md` NEW (the human pin record
+ cadence + owner the issue asked for — the machine pin already existed, the dated
human record did not).

## Live classifications this run

| Claim | Receipt | Class |
|---|---|---|
| Installed version vs `runtime/pins.json` | [installed-version.txt](receipts/installed-version.txt) | STALE pin (was v1.4.200) → **patched** to v1.4.203 live |
| `worker-list --run <id>` scopes to that Run | [worker-list-bound.json](receipts/worker-list-bound.json) `scope.source=flag` | CURRENT |
| Unscoped `worker-list` enumerates runtime history | [worker-list-unscoped.json](receipts/worker-list-unscoped.json) `scope.source=all`, total 458, `hasMore` (rows + cursor redacted per the 2026-09-13 convention) | CURRENT |
| `worker-list --from` | [worker-list-from-no-run.json](receipts/worker-list-from-no-run.json) `invalid_argument` | CURRENT (flag does not exist on this verb) |
| `worker-list --run --terminal-state reclaimable` | [worker-list-reclaimable.json](receipts/worker-list-reclaimable.json) exit 0 | CURRENT (end-of-run gate verb shape live) |
| `projection.liveness/attention/nextAction` rows | shape rows in the above + survey in run notes | CURRENT (`release` argv literal; `missing_status` vocab live) |
| All CLI-shape claims (send/check/ask/reply/task-*/dispatch/gate-*/worker-*/run-*/inbox/reset/worktree/terminal/automations/doctor/serve) | [agent-context.json](receipts/agent-context.json) (234 commands) | CURRENT |
| `orchestration run` retired alias | [retired-run-alias.txt](receipts/retired-run-alias.txt) resolves to the retired page | CURRENT |
| `terminal stop` deprecated | [terminal-stop-deprecated.txt](receipts/terminal-stop-deprecated.txt) | CURRENT |
| Every cited source anchor (34 files read at the build commit) | run notes §Source anchors | CURRENT (content holds; six line pins corrected) |
| `droid` has no Orca autonomous flag (`spawn_worker.sh` comment) | YOLO map `droid: '--auto high'` at the build commit + the script's own lanes | STALE comment (pre-existing, not 1.4.200→1.4.203 drift) → **fixed** |
| New group-scoping guide text vs doctrine | guide diff (additive) + spec notes | NO CONFLICT — recorded as the map for owed probe 3, not as doctrine |

`spawn_worker.sh` already NOTEs when PATH Orca ≠ `runtime/pins.json` (#301). After this
pin update, a matching 1.4.203 is silent; the next bump arms pin-it again.

## Source anchors (build commit `54eaa14`, all content-holds)

Send block L49/71/76-78/81 · ask CSV L205 / gate JSON-array L256 · `--types` wake
L114 · task-create `--parent` L136 · group rejection L51-58 · release contract L101 ·
unsupervised L124 · keepalive stderr+alias · YOLO map L7-33 + env map · cursor L25 ·
launch defaults L10 + strip L5-8 · readiness `unobserved`→`outcome_unknown` ·
refusal 3-code union L8 · dep/parent validation L38-41/L32-35 · skills refs L50-56 ·
inject `sendTerminalAgentPrompt` L155-165 · prompt `{requestId, stages}` shared L221-225
· per-code anchors L13/18/52/49/117 exact · receipt fields L42-69 · `request_mismatch`
on method/payload change · terminal-wait exit 1 L125-129 · legacy `decision_gate`
L101 + migration L81 exact · precheck skip spec L62 · `terminal_handle_stale` ·
`stable_pane_required` in the check path · ask 600s/1800s constants · Delivery batch
50 · schema line v40 (highest migration) · doctor no-fail-no-warn (1.4.203 guide).

## Park register

[PARK.md](PARK.md): sender-bound behavior replays (run-create, check-consume,
task-create, send, gate-create/resolve, worker-start roster, inject receipt,
mixed-batch wake, dep-refutation) — each named with its exact probe. The 2026-09-13
register's OS/remote/paid-trust parks carry over unchanged. Parked claims keep their
1.4.200 live receipts; nothing was reclassified from a substrate refusal.

## Teardown

Nothing to tear down: this session created no Orca state (no Run, no terminal, no
worktree — every probe was read-only from a plain shell). No `reset`, no global
change, no push to upstream, no upstream change of any kind.

## Integrity inventory (sha256)

Per-file hashes of `guides/` + `receipts/`: [inventory.txt](inventory.txt).
