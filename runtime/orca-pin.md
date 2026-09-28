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
| Installed version | **v1.4.215** (release bundle; the on-PATH app is still v1.4.204 — update owed, not blocking: the witness ran against the identical release artifact, extracted at `/tmp/orca-1215`) |
| Build commit | `3eb1adec20ff90503196ebfd1fe6dbaaefaad736` (`orca-local-build.json`, arm64; tag `v1.4.215` = `083f583a53e4c74a65acf420eee4ca2e0efa9df1`) |
| Witnessed | 2026-09-28 (`live`: release binary + version-matched guides + read-only probes; the app was not running, so runtime-bound probes parked on substrate) |
| Upstream HEAD then | `5219b8ada9da6bf625c750e5513c36037464a516` (main, 2026-09-28) |
| Run record | docs/runs/2026-09-28-pin-it-500.md (ledger + park register) + docs/runs/2026-09-28-pin-it-500/ (receipts) |
| Prior pin | v1.4.209 `ee1c5220` (2026-09-23, docs/runs/2026-09-23-pin-it-488.md) |
| Verdict | **PINNED-WITH-PARKED** — no behavioral drift; live re-probes wait on a running app, doctor shapes on a per-workspace-env recipe, legacy replay on a legacy Run |

## What moved since v1.4.209 (diff summary)

- **Nothing behavioral.** Zero drifts, zero removals, zero error-text changes across the
  release-source range (`e4d8a9dbc2..083f583a`, v1.4.210/211/212/214/215 — all patches).
  Every drift row from the v1.4.209 pin re-verified CURRENT (see the run record's table).
- **New surface (additive, no doctrine claims):** `host name`, `profile state exports`,
  `profile state rollback` (profile SQLite recovery, `47ddfbdc0d`/`82412dab8b`).
- **Guides:** 1 of 14 served files differs — `orchestration--coordinator-loop` (`--model`
  now also for Antigravity + Muse terminals; opencode/zcode reject it). Help root: one
  line (`linear` read → read/write, `c2d9d12b1f`). agent-context 236 → 239, nothing
  removed. Our doctrine claims none of these surfaces — noted, no patch.
- **Internals, reviewed:** the structured-session identity theme (creator `orcaSessionId`
  plumbing across depth/check/runs/dispatch, preamble wording + `leadLine`), pane
  reservation (`a375936c04`), worktree listing versioning (`ad6cb0e05c`), relay readiness
  coalescing (`1fc0bfe46d`) — no CLI-contract change in any of them.
- **Method note:** upstream builds from release branches, not main@build-commit (proven:
  `c2d9d12b1f` predates the 209 build yet missed the 209 binary and tag). Verdicts rest on
  the tag range; `ls-remote` tag shas are objects — peel them (run record §Source range).
- **Unchanged, re-verified:** the whole v1.4.209 register — worker-list ordering + scope
  (D1/P05/P22), archive-hook gate (D2), idle-gated delivery (D3), error texts (D4/D5),
  search/--shell/browser-identity (D6–D8), status ESRCH-only (D10), remote 12s fail (D11),
  readiness (P01/P02/P38), inject (P04), depth refusal (P08), release unknown (P09), run
  verbs + Delivery batch + `--types` wake (P10/P12/P24), keepalives (P14), retry/group
  (P15/P16), bogus-dep (P20), projection (P21/P47), gate promotion (P26), ask/gate
  (P30/P32/P33), sandbox/recipe/doctor (P40 stays parked — surface zero-diff),
  terminal-stop hedge (D9 — spec + handler confirmed at release sources; §correction).

## Re-pin cadence + owner

A re-pin fires on whichever comes first:

1. Each Orca **minor** release (patch bumps ride unless a drift NOTE or guide diff says otherwise).
2. **Quarterly** at minimum — the date trigger keeps a quiet upstream honest.
3. A `SPAWN=NOTE … run pin-it` sighting in the field, or any dispatch-doc drift report.

Owner: the **pin-it** mission (its coordinator runs the loop; the maintainer files the issue).
Next trigger: **2026-12-28** (quarterly from the 2026-09-28 re-pin), filed as the successor
issue — it inherits this run's park register (docs/runs/2026-09-28-pin-it-500.md).

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
