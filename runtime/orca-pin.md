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
| Installed version | **v1.4.204** (`orca --version`) |
| Build commit | `357c9780f8bffa10a21d004449d8d6d9846a9310` (`orca-local-build.json`, arm64) |
| Witnessed | 2026-09-20 (`live`: installed binary + version-matched guides + scratch-Run probes) |
| Upstream HEAD then | `bd5177801bde74a3cc8073c50e7d6fbad14c305e` (main, 2026-09-20) |
| Run record | docs/runs/2026-09-20-pin-it-427.md (ledger + park register) + docs/runs/2026-09-20-pin-it-427/ (receipts) |
| Prior pin | v1.4.203 `54eaa147` (2026-09-16, docs/runs/2026-09-16-pin-it-416/) |
| Verdict | **PINNED-WITH-PARKED** — doctor verdict shapes need a per-workspace-env recipe (none on this host); the legacy-takeover live replay needs a legacy Run |

## What moved since v1.4.203 (diff summary)

- Guides: **15 of 15 served files byte-identical** (both kernels, all 7 orchestration
  references, all 3 orca-cli references, orca-per-workspace-env). No guide drift at all.
- Live at 1.4.204 (scratch Run + workers; worktrees retired, tasks settled, probe runs
  settled-but-retained — runs are not deletable): every claim the 1.4.203 session parked
  for want of a live terminal replayed and held — bogus-dep refusal, gate-create
  auto-block, gate-resolve absent from the preamble, ask timeout → PENDING → same-id
  `--resume`, `--retry-request` dedup/cross-method `request_mismatch`,
  `nested_worker_depth_exceeded` from a worker's own Run, the group-address contrast.
- One doctrine patch: the worker-release unknown-dispatch code is **`dispatch_not_found`**
  at 1.4.204 (refutation receipt docs/runs/2026-09-20-pin-it-427/receipts/p09-release-bogus.json).
- Drift fixed in the re-pin: the pin itself and that one line. Nothing else moved.

## Re-pin cadence + owner

A re-pin fires on whichever comes first:

1. Each Orca **minor** release (patch bumps ride unless a drift NOTE or guide diff says otherwise).
2. **Quarterly** at minimum — the date trigger keeps a quiet upstream honest.
3. A `SPAWN=NOTE … run pin-it` sighting in the field, or any dispatch-doc drift report.

Owner: the **pin-it** mission (its coordinator runs the loop; the maintainer files the issue).
Next trigger: **2026-12-20** (quarterly from the 2026-09-20 re-pin), filed as issue #488 —
it inherits this run's park register (docs/runs/2026-09-20-pin-it-427.md).

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
