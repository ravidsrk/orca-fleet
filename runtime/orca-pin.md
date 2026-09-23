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
| Installed version | **v1.4.209** (release bundle; the on-PATH app is v1.4.204 — update owed, not blocking: the witness ran against the identical release artifact, extracted at `/tmp/orca-1209`) |
| Build commit | `ee1c52207000c7d70282549c73e9945bd1cec1e8` (`orca-local-build.json`, arm64; tag `v1.4.209` = `e4d8a9dbc2`) |
| Witnessed | 2026-09-23 (`live`: release binary + version-matched guides + read-only probes against the shared datadir) |
| Upstream HEAD then | `dac82f61bc710324f8883b11788869b6cf8a0ce2` (main, 2026-09-23) |
| Run record | docs/runs/2026-09-23-pin-it-488.md (ledger + park register) + docs/runs/2026-09-23-pin-it-488/ (receipts) |
| Prior pin | v1.4.204 `357c9780` (2026-09-20, docs/runs/2026-09-20-pin-it-427.md) |
| Verdict | **PINNED-WITH-PARKED** — doctor verdict shapes still need a per-workspace-env recipe (none on this host); the legacy-takeover live replay still needs a legacy Run |

## What moved since v1.4.204 (diff summary)

- **Upstream fixed the worker-list bury hazard** (v1.4.206, `3336933cc8`): pages are now
  newest-first and the receipt carries `warnings: string[]` on truncation (live-verified:
  `Showing 100 of 551 Dispatches, newest first` — probe-worker-list-209.json).
  `liveness-resume.md` / `orca-dag-semantics.md` reworded to match.
- **`worktree rm` archive-hook gate** (v1.4.205, `f7b2736d6d`): a failed hook now BLOCKS removal
  (`worktree_archive_hook_failed`; new `--allow-failed-archive-hook`, requires `--run-hooks`,
  `--force` does not waive). The fleet's retirement path uses no `--run-hooks` — unaffected.
- **Mailbox delivery is idle-gated** (v1.4.205, `49fba59925`): a busy TUI pane's delivery waits
  for quiescence and is re-offered. Batch/ack semantics (P12/P24) unchanged — timing only.
- **Error text drift, codes unchanged** (v1.4.206): `stale_delivery` names an id-kind mismatch
  when `--ack` is handed a message id; `no_active_sender_terminal` no longer advises another
  pane's handle (live-verified — probe-send-no-sender-209.json).
- **New surface (additive):** `orca search` (agent-session full-text), `terminal create
  --shell` (Windows), `orca browser identity get/set`. **Removed:** `--no-ua-spoof`
  (`tab profile create`) and the `terminal stop` command (dispatch-lifecycle.md updated).
- **`orca status`:** EPERM no longer reads as `stale_bootstrap` (ESRCH-only, `981a4821da`).
- **Remote-runtime:** unreachable `--environment` fails in ~12s with
  `remote_runtime_unavailable` (was ~60s `runtime_timeout`, `2531dc9d5a`); the
  "outage is not a handle-gap verdict" family landed upstream (7 commits).
- **Guides:** 3 of 10 served files differ byte-for-byte — `orca-cli` guide (new Agent Session
  Search section + description), `orchestration` guide (description + newest-first line),
  the `recovery-and-cleanup` reference; both ref-lists byte-identical. Help root gains the
  Agent Sessions group + two usage tokens.
- **Unchanged, re-verified:** gate/blocked-task promotion (P26), `dispatch_not_found` (P09),
  nested-depth counting (P08), bogus-dep refusal (P20), inject staging (P04), readiness
  semantics (P01/P02/P38), keepalives stderr-only (P14), `projection.liveness` (P21/P47),
  `--types` wake + whole-batch delivery (P12/P24), worker-list scope semantics (P05/P22),
  artifacts CLI, worktree create/list/set, the whole sandbox/recipe/doctor surface (P40 stays
  parked — no new probe became possible).

## Re-pin cadence + owner

A re-pin fires on whichever comes first:

1. Each Orca **minor** release (patch bumps ride unless a drift NOTE or guide diff says otherwise).
2. **Quarterly** at minimum — the date trigger keeps a quiet upstream honest.
3. A `SPAWN=NOTE … run pin-it` sighting in the field, or any dispatch-doc drift report.

Owner: the **pin-it** mission (its coordinator runs the loop; the maintainer files the issue).
Next trigger: **2026-12-23** (quarterly from the 2026-09-23 re-pin), filed as the successor
issue — it inherits this run's park register (docs/runs/2026-09-23-pin-it-488.md).

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
