# Run report — review-it external run, 2026-07-13

First **external** run of a mission from this catalog (target is not this repo).
Mission: **review-it**, `source=PR`. Target: **garrytan/gstack PR #2252**
("fix(test): delayed process.exit(0) in 8 test files silently truncates full
bun-test runs"). Proof tier earned: **external-run**.

| field         | value |
|---------------|-------|
| coordinator   | Claude (interactive session), tubeworm |
| target        | garrytan/gstack PR #2252 (external, clone adopted into Orca) |
| fixed point   | merge-base `7c9df1c568a9` ... head `94b7895ab34464f6a11807dd45e09aaa476e21c2` |
| reviewed_sha  | `94b7895ab34464f6a11807dd45e09aaa476e21c2` |
| spec source   | PR #2252 description (bug + two-commit fix + honest caveat) |
| runtime       | Orca orchestration; workers `PROFILE=ro` (report-only permission boundary) |
| workers       | 4 dispatched, all ro claude, isolated fresh contexts, no cross-rerank |
| reviewer_mode | independent-of-author (all four reviewers; none wrote the PR) |
| outcome       | **NO-GO (conditional — 0 Critical, fixable)** |
| permission    | boundary held — zero files changed, nothing posted to the external PR |

## Verdict

**NO-GO (conditional).** The core fix is correct, idiomatic, and high-value — all
four axes affirm the eight time bombs are removed and the `exitFn` seam is real and
exercised. Three Required items block a clean merge; none is Critical, so this is a
fix-and-remerge, not a rejection. Full verdict with per-axis line-quoted findings in
the run artifacts.

| Axis                     | Critical | Required | Nit | Opt/FYI |
|--------------------------|----------|----------|-----|---------|
| Standards                | 0        | 1        | 5   | 1       |
| Spec fidelity            | 0        | 1        | 2   | 2       |
| Test-adequacy            | 0        | 2        | 3   | 2       |
| Security (NEVER_GATE)    | 0        | 0        | 0   | 3 (CLEAN) |

Risk lenses: security ran (never-gate, CLEAN); data-migration N/A (never-gate);
perf + a11y honestly gated off (test-hygiene diff, no render/query/markup surface).

## Blocking Required items (coordinator-verified)

1. **Out-of-scope untested production change** — multi-axis confirmed (Standards R1 +
   Spec Finding 1), both quoting `browse/src/browser-manager.ts:809`. The `closeTab`
   zero-tab invariant changed for every user, rides a `fix(test)` commit, undisclosed
   in the PR body, untested. Coordinator confirmed the changed line at head.
2. **PR-introduced deterministic test failure** — Test-adequacy F1, coordinator-verified
   directly: head sets all three state-dir vars (`gstack-config.test.ts:24-26`), the
   nested test overrides only `GSTACK_STATE_DIR` (`:111`), the script resolves
   `GSTACK_STATE_ROOT` first (`bin/gstack-config:17`); merge-base set only
   `GSTACK_STATE_DIR` so it passed before. This falsifies the PR's "all revealed
   failures are pre-existing" caveat in a concrete case.
3. **Unverified caveat + red local gate** — Test-adequacy F2. The "200+ pre-existing
   failures" claim ships without the control-run receipts the target's own CLAUDE.md
   requires; the local `bun test` gate goes red on merge.

## Pipeline evidence

1. **PIN** (coordinator): fixed point pinned to the PR merge-base → head; spec source =
   PR body; external clone adopted into Orca, worktree on the PR branch.
2. **ACCEPTANCE-REVIEW** (always, 3 isolated ro workers): Standards, Spec fidelity,
   Test-adequacy — parallel, no cross-rerank, anti-FP gate (every finding quotes its
   line or drops to an appendix).
3. **RISK-REVIEW** (scope-gated, NEVER_GATE lenses): Security ran (4th worker) and is
   CLEAN with a full threat model; data-migration recorded N/A; perf/a11y recorded off.
4. **AGGREGATE**: findings side-by-side per axis; three multi-axis confirmations boosted;
   coordinator independently verified the two load-bearing Required findings against git.
5. **VERDICT**: GO/NO-GO bound to `reviewed_sha`; any Critical → default NO-GO (none here;
   the NO-GO is driven by the Required set, explicitly fixable).

## Deviations and lessons (recorded, not hidden)

- Three of four workers exit-3'd at spawn (NO_HEARTBEAT) but were alive per terminal
  titles + spinners; left running per liveness policy. The heartbeat window (3×40s)
  under-waits slow claude starts — same signal as the clean-sweep run; a longer default
  `HB_POLL_SECS` is now twice-observed and worth doing.
- One worker (security) genuinely failed at `dispatch-inject` (rc=1, status=failed) when
  four terminals were created near-simultaneously in one worktree. Doctor path recovered
  it on attempt 1/3 (task-update ready → fresh terminal). Possible contention when
  fanning many injects into a single worktree fast — worth spacing or per-worker worktrees.
- A zsh loop mangled task-id variables on the first spawn attempt (parameter expansion +
  `read`); re-ran with literal IDs. Cosmetic, no orphan terminals (REFUSED exits before
  terminal creation).

## Run-close integrity inventory (sha256)

```
8bdd99c5ca0b725156af565aaaadca8bd2620d214038be59977500ab54f92f18  axis-standards.md
00b288967f8f109a1d8dd0248d9a114801f2102e03c0eb386c62940b328ac845  axis-spec.md
4b519ae8eb15b397a0faa85f369cae6effcc02be4403f10a026af079af274988  axis-test-adequacy.md
0f09064db6e61df54e9d08340baf2b83b1ad3b7a74a027b43eb37ee0a9409bab  axis-security.md
5c7285b54396eecf86c9dbd2a3e3711b62f81944786ef593f18b65785b2afdb1  verdict.md
```

Artifacts in the coordinator run directory; Orca provenance holds the task/dispatch
lifecycle (`task_4548b7f3eb0f`, `task_55b0b2dbf7ee`, `task_662b190c6642`,
`task_5fd0a7baee15`).

## Gate

review-it is report-only and has **no fix authority**. The findings route to the PR
author; nothing was posted to the external repo, and no code was modified. The verdict
is the deliverable.
