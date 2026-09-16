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
| Installed version | **v1.4.203** (`orca --version`) |
| Build commit | `54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec` (`orca-local-build.json`, 2026-09-15) |
| Witnessed | 2026-09-16 (`live`: installed binary + version-matched guides + build-commit source) |
| Upstream HEAD then | `feb04ec254585ba69587699d41f80a72dda2cb27` (main, 2026-09-16T05:23:22Z) |
| Run record | docs/runs/2026-09-16-pin-it-416/ (guides, receipts, park register) |
| Prior pin | v1.4.200 `2ecde717` (2026-09-13, docs/runs/2026-09-13-pin-it-266/) |
| Verdict | **PINNED-WITH-PARKED** — sender-bound behavior replays need a live Orca terminal |

## What moved since v1.4.200 (diff summary)

- Guides: 11 of 12 archived references byte-identical; only
  `orchestration/messaging-and-gates` gained text — group-address scoping (`@all` et al reach
  the live Dispatches of the sender's own Run; a sender bound to no Run is refused; `--run`
  never grants membership). No doctrine contradicts it; the `@all` replay probe stays owed.
- Source anchors at the build commit: every cited anchor re-read — YOLO agent map, release
  exit contract, readiness turn-start, refusal codes, Delivery batch 50, ask 600s/1800s
  timeouts, schema line v40, precheck skip, keepalive shape. Content all holds; six line pins
  drifted by ≤4 lines and were corrected in place.
- Live at 1.4.203 (plain shell, read-only): scoped/unscoped `worker-list` envelopes,
  `projection.liveness/attention/nextAction` shapes, `--terminal-state reclaimable`,
  `--from` refusal, retired `orchestration run` alias, deprecated `terminal stop`.
- Drift fixed in the re-pin: the pin itself, six line pins, the YOLO env-map sentence, a
  stale droid comment in `spawn_worker.sh`, and the pin-coupled `test_spawn_worker.py`
  assertions. No script behavior changed — every behavior the scripts rely on still holds.

## Re-pin cadence + owner

A re-pin fires on whichever comes first:

1. Each Orca **minor** release (patch bumps ride unless a drift NOTE or guide diff says otherwise).
2. **Quarterly** at minimum — the date trigger keeps a quiet upstream honest.
3. A `SPAWN=NOTE … run pin-it` sighting in the field, or any dispatch-doc drift report.

Owner: the **pin-it** mission (its coordinator runs the loop; the maintainer files the issue).
Next trigger: **2026-12-16**, filed as issue #427 — it inherits the current park register.

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
