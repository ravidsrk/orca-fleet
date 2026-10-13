# Runtime pin — which Orca this doctrine was witnessed against

The fleet's runtime mechanics (`dispatch-lifecycle`, `liveness-resume`, `orca-dag-semantics`,
`merge-serialization`, `gate-classification`, `sandbox-policy`, `mission-scheduling`,
`worker-supervision`, and the scripts that touch the binary) are re-witnessed against the
INSTALLED Orca binary on every pin-it run — never trusted from memory or release notes. This
file is the human-readable pin record: what was witnessed, what moved, when the next re-pin
fires, and who owns it. The machine-readable pin is `pins.json` (same directory):
`spawn_worker.sh` NOTEs when the binary on PATH differs from it, and `tests/test_pins.py`
holds its shape. The two never disagree — a run updates both or neither.

## Current pin

| Field | Value |
|---|---|
| Upstream | `stablyai/orca` (`https://github.com/stablyai/orca`) |
| Installed version | **v1.4.224** (installed app + CLI co-resident 1.4.224 on macOS — app `CFBundleShortVersionString` + `orca --version`, receipt `mac-coresidency.txt`; live mechanics witnessed on the 1.4.224 Linux `orca-ide serve` substrate) |
| Build commit | `2bb20586ebc39d605e16d95f57420e20a16e7485` (tag `v1.4.224` target commit, "release: v1.4.224"; upstream builds from release branches, so the tag IS the release source) |
| Witnessed | 2026-10-13 (`live`: DELTA re-dump — guides + help + agent-context from the installed 1.4.224 binary diffed against the frozen 1.4.215 inventory — plus live replay on Linux serve 1.4.224 under a real manual-terminal Dispatch; receipts in the run record) |
| Upstream HEAD then | `0a1f99fb3a` (main, pulled 2026-10-13; newest tag + latest release both v1.4.224, 2026-10-10) |
| Run record | docs/runs/2026-10-12-pin-it-224.md (ledger + park register) + docs/runs/2026-10-12-pin-it-224/ (starter diff, delta inventory D224-1…10, receipts) |
| Prior pin | v1.4.215 `3eb1adec` (2026-09-28, docs/runs/2026-09-28-pin-it-500.md) |
| Verdict | **PINNED-WITH-PARKED** — two fleet-visible drifts patched (conditional dispatch capability; OMP/OpenCode `--model` roster); fencing paths, `terminal stop`, worker-list, no-sender, and doctor shapes retired live; legacy replay, `caller.orcaSessionId`, agent-owned abandon, send-side `consumer_fenced`, and other-host probes stay parked on named substrates |

## What moved since v1.4.215 (diff summary)

Method: DELTA, not re-derivation — the 1.4.224 guides, help root, and agent-context were
re-dumped from the installed binary and diffed against the frozen 1.4.215 inventory
(`diff-vs-1.4.215.json`); only changed mechanics were classified (D224-1…10 in the run
record's delta inventory), and every mechanics-changed row was replayed live on the Linux
serve substrate. Unchanged fleet-used surface carries the 2026-09-28 receipts.

- **Two fleet-visible drifts, PATCHED:** the canonical worker `send`/`ask` forms now carry
  `--dispatch-capability` only when the dispatch preamble carries one (an older host adds
  it); `dispatch-lifecycle.md` + `decompose-dag.md` taught "every send carries it" and now
  teach the conditional. The flag stays accepted; `dispatch_capability_invalid` stays real.
- **Replayed live at 224 (receipt `dispatch-probes.txt`):** task lifecycle incl.
  `task-update --result <text>` stored verbatim (`task_ops.py` JSON text stays parseable;
  its docstring now says `<text>`); cancel = `--status failed --result cancelled`;
  wrong-party `worker_done` → `worker_identity_changed`; a consuming `check` from an
  unbound terminal and post-takeover Run mutations → `consumer_fenced` (plain `status`
  mail to a Run is NOT fenced — a literal `send`/`ask` → `consumer_fenced` stays parked,
  D224-2); `worker-abandon` on a manual-terminal Dispatch settles and leaves the terminal
  live (worker `unsupervised`) — the agent-owned-terminal settle stays parked on agent
  credentials (D224-4); `terminal stop` EXECUTES (see §correction);
  `worker-list` returns the full projection; sender-less `send` →
  `no_active_sender_terminal`; mail to a `dispatch:<id>` whose terminal now coordinates a
  child Run redirects with `recipient_run_bound_redirect` (the #513 note, shipped v1.4.217);
  `vm recipe doctor` verdicts are `{recipeId, repoPath, ok, checks[{id,status,message,
  remediation?}]}` with `pass`/`warn`/`fail` all observed, and `sandbox_doctor.py` judges
  the real transcripts correctly (P40 retired for shapes; a clean `--provision` pass still
  needs a real provider — offload-it's self-test, not a pin claim).
- **Additive only, no doctrine claims:** agent-context 239 → 249 (10 added, 0 removed —
  `account rm/select`, `environment *`, `repo set`, worktree `--pr/--gitlab-*/--unread`,
  automations `--extra-agent-args`, metadata `surface`/`runMode`); 7 of 14 guides changed.
  `worker-start --model` now also covers OMP, and OpenCode accepts it in an existing
  worktree — the second drift patched this run (the spawn_worker.sh roster comment still
  had both rejecting it; source-verdict at the tag, D224-3/9). `dsh` joined the upstream `--agent` set at
  v1.4.218; the fleet roster does not adopt it.
- **Schema v43** (`contract-constants.ts:23` at the tag): stored `session:<id>` addresses
  respelled `orca_session_id:<id>`; no fleet code or doctrine keys the old spelling
  (D224-10; `orca-dag-semantics.md` schema line advanced).
- **Still parked:** `caller.orcaSessionId` — absent for external CLI and in-terminal shell
  callers at 224 (both receipts on disk); observing it present needs a structured agent
  session. No fleet claim reads it.

## Noted since the pin (inherited by the next re-pin)

Both 2026-09-28 compass points (#513) shipped and were dispositioned in this run:
`recipient_run_bound_redirect` (v1.4.217) replayed live — `dispatch-lifecycle.md`
addressing now names it; `dsh` (v1.4.218) is upstream-available and deliberately not on
the `spawn_worker.sh` roster. New notes at v1.4.224:

- The Linux witness's first `serve` logged `[agent-state-rules] download failed: HTTP 404`
  — witness-first-run noise to watch, not a doctrine claim (relates to #526).
- `caller.orcaSessionId` (D224-6) waits on a structured agent session in the witness VM
  (an agent account signed in there) — the same substrate the self-run programs need.
- A weekly probe (`"$ORCA_FLEET_ROOT/runtime/scripts/upstream_probe.py"`, `.github/workflows/upstream-drift.yml`,
  #516) files an `upstream-drift` issue when a new minor lands or the pin falls ten patches
  behind, so the date trigger below is no longer the only thing keeping a quiet upstream honest.

## Re-pin cadence + owner

A re-pin fires on whichever comes first:

1. Each Orca **minor** release (patch bumps ride unless a drift NOTE or guide diff says otherwise).
2. **Quarterly** at minimum — the date trigger keeps a quiet upstream honest.
3. A `SPAWN=NOTE … run pin-it` sighting in the field, or any dispatch-doc drift report.

Owner: the **pin-it** mission (its coordinator runs the loop; the maintainer files the issue).
Next trigger: **2026-12-28** (the standing quarterly date, kept) or the next minor / drift
sighting, whichever first — the successor run inherits this run's park register
(docs/runs/2026-10-12-pin-it-224.md) and carries #508 forward.

## How to re-pin (so a stranger can reproduce the diff)

1. Resolve the oracle: `orca --version`, the app's `orca-local-build.json` commit, upstream
   HEAD (`git ls-remote https://github.com/stablyai/orca.git HEAD`).
2. Freeze a run dir `docs/runs/<date>-pin-it-<issue>/`; archive `orca skills get
   <orchestration|orca-cli> --references` plus every `--reference`, and diff against the
   prior run's `guides/`.
3. Re-witness: replay every CLI-shape claim against `orca agent-context --json` and
   `--help`; run every read-only probe that needs no sender terminal; re-read cited source
   anchors at the build commit. Sender-bound mutations need a live Orca terminal with full
   teardown — without one, PARK them with the exact probe, never reclassify.
4. Tabulate the drift table (one row per policy + per script entry point, every row a
   verdict), fix drift in place, update this file and `pins.json` together.
5. Refresh the park register, file the next dated re-pin issue, regenerate badges
   (`scripts/gen-badges.py`), and land with `scripts/validate.py` + `tests/` green.

## 2026-09-26 correction — `terminal stop` was never witnessed removed (D1/D10)

The "What moved" line above claims `terminal stop` removed at v1.4.209. That overstates what the
run witnessed: source at the build commit keeps it as a hidden (`core.ts:241`) deprecated
(`core.ts:242,246`) spec with its handler still present (`handlers/terminal.ts:137-142`) — same at
HEAD 4cafa50e. `dispatch-lifecycle.md` now hedges accordingly. Live re-probe parked for the next
pin-it with a live terminal: `orca terminal stop --worktree <selector> --json` (does it execute
or refuse?) plus `orca terminal --help` (does `stop` stay unlisted?). History above untouched.

2026-09-28 resolution (this re-pin): spec + handler confirmed present at the v1.4.215 release
sources (`core.ts:240`, hidden + deprecated; `handlers/terminal.ts:137`); `stop` stays unlisted
in `terminal --help` (terminal-help-1.4.215.txt) — the listing half is answered. The
execute-or-refuse half re-parks: the app was not running, so the probe returned
`runtime_unavailable` (substrate, not mechanism evidence).

2026-10-13 resolution (v1.4.224 re-pin): EXECUTES. On the Linux serve substrate,
`orca-ide terminal stop --worktree path:/tmp/probe-repo --json` returned `{"stopped": 5}`
(and 3 on the second sweep) and `terminal list` came back empty — the hidden deprecated
verb works and stops every terminal in the worktree. Doctrine keeps `terminal close` as
the canonical teardown; `stop` is recorded as a working blunt instrument. D1/D10 closed.
