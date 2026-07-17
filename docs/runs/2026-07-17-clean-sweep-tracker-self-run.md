# clean-sweep — tracker self-run, 2026-07-17

Source: tracker `ravidsrk/orca-fleet`, 26 open issues (#27-#52) at T0 2026-07-17T01:46:23Z.
BASE: `clean-sweep/integration` (fork-point 8d14974). Coordinator: manual Orca loop.

## Outcome: DRY-WITH-PARKED

Full re-enumeration finds zero non-terminal items: 22 CLOSED with merged, ancestry-verified
evidence; 4 PARKED. New issues since T0: none. Integration is 43 commits ahead of main, green
at 94 tests.

| Bucket | Count | Issues |
|--------|-------|--------|
| CLOSED (merged PR + failing-first test + neg-control) | 22 | #27-#41, #43-#48, #50 |
| PARKED needs-human | 1 | #42 (release cut is the owner's gate) |
| PARKED CODE_CLOSED + VERIFY_AT_SCALE | 1 | #51 (WIP-curve protocol merged; AC-3 first measured data point owed to the next fleet run report) |
| PARKED out-of-scope (handed off) | 2 | #49 (ship-it self-run), #52 (net-new positioning doc) |

## Merge waves

| Wave | Issues | PRs | Notes |
|------|--------|-----|-------|
| 1 | #32, #45, #46 | #54, #55, #53 | #32 foundation (WIP header in 9 mission files); #53 needed a fix-round (Required) |
| 2 | #31, #27/#28/#29, #33/#47/#48 | #57, #58, #59 | Greptile on #57/#59 addressed in-flight |
| 3 | #34/#35/#36, #37-#41, #50/#51 | #60, #61, #62 | UF respawned once (env hang) |
| 4 | #30 | #63 | BUILT→BUILD_DONE per-unit-flag rename; wave-state BUILT kept |
| 5 | #43, #44 | #64 | Re-enumeration catch — dropped from the original plan; coordinator-authored |

Every PR merged with a merge commit; all chained on the generated `assets/badges/tests.json`,
regenerated via `gen-badges.py` at each serial merge.

## What the run exercised (and where it degraded)

- **Two-denominator honesty:** zero refuted, zero duplicates — a genuine backlog.
- **The re-enumeration is load-bearing:** #43/#44 were silently dropped from the wave plan and
  built to zero occurrences on the ledger; only the ledger re-enumeration caught it. This is the
  mission's central guard doing its job.
- **Reviewer/builder env hang:** claude workers intermittently hung at an identical
  `.claude/settings.json` `.env`-permission signature. Per the identical-error-kill rule, after
  two consecutive hangs the wave-2 review degraded to coordinator VERIFIER-role mechanical
  verification (clean-checkout validate+test at each head, acceptance-criterion probes) backed by
  the independent Greptile reviews; the final unit (#43/#44) was coordinator-authored with full
  build-change discipline after two builder hangs. Both degradations are documented, not hidden.
- **Bot reconciliation:** every Greptile thread that posted (#54, #57, #59, #60, #61, #62, #63)
  was addressed and answered; Greptile no-showed on several PRs (bounded wait, logged).
- **Attention budget:** WIP capped at 3 builders / 1 reviewer per wave, recorded in the ledger
  header — the fix this repo shipped in #32's neighbor policy, applied to its own sweep.

## Evidence

Ledger + per-unit manifests: `.clean-sweep/LEDGER.md`, `.clean-sweep/triage-report.md`.
Per-unit SHA-bound evidence manifests live in each PR body (#53-#64); every close links its
merge SHA and its failed-pre-fix test. The run-close sha256 integrity inventory is retained at
`.clean-sweep/` in the coordinator worktree (`redhorse`), alongside the ledger — the artifacts
outlive the disposable unit worktrees, which were verified-and-retired at merge.
Promotion PR #65 carried the closing keywords; merge to main is the owner's one-way gate.
