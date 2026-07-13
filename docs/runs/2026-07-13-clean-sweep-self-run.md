# Run report — clean-sweep self-run, 2026-07-13

First recorded run of a mission from this catalog. Mission: **clean-sweep**,
`source=doc-claims` ("the README lies — verify and fix it"), target: this repo itself.
Proof tier earned: **self-run** (external-run requires a repo that is not this catalog).

| field       | value |
|-------------|-------|
| coordinator | Claude (interactive session), tubeworm worktree |
| BASE        | `ravidsrk/sweep-base` @ `41fec8f` (preflight.py OK — first live exercise) |
| baseline    | validate.py green; 25/25 tests green |
| runtime     | Orca orchestration (task-create → spawn_worker.sh → dispatch --inject → check --wait) |
| workers     | 4 dispatched: triage (claude, ro) · builder (claude, rw) · reviewer (codex, rw — cross-vendor) · integrator/conductor (claude, rw) |
| reviewer_mode | cross-vendor (codex reviewed claude's fix; blind-fix expectation written pre-diff) |
| outcome     | **DRY** — re-enumeration found zero open claims |

## Findings ledger (final)

| id  | title                                   | VERIFIED        | CLASS    | PR | reviewed_sha | MERGED    | CLOSED |
|-----|------------------------------------------|-----------------|----------|----|--------------|-----------|--------|
| F-1 | README badge: 19 tests (actual 25)       | CONFIRMED-FALSE | real-bug | #9 | `ed540a0`    | `c85bbd3` | yes    |
| F-2 | README badge: v0.1.1 (actual 0.2.0)      | CONFIRMED-FALSE | real-bug | #9 | `ed540a0`    | `c85bbd3` | yes    |
| F-3 | README layout: "25 architecture tests" mislabel | CONFIRMED-FALSE | real-bug | #9 | `ed540a0` | `c85bbd3` | yes |
| F-4 | getting-started: nonexistent `../../playbooks/` mechanism | CONFIRMED-FALSE | real-bug | #9 | `ed540a0` | `c85bbd3` | yes |
| F-5 | getting-started troubleshooting: same stale mechanism | CONFIRMED-FALSE | real-bug | #9 | `ed540a0` | `c85bbd3` | yes |
| F-6 | CHANGELOG: duplicated body-less 0.1.1 heading | CONFIRMED (defect) | real-bug | #9 | `ed540a0` | `c85bbd3` | yes |

All six folded into one PR per the build-change sizing seam (sub-10-line fixes fold into a
neighbor; one file never splits). Closes cite the shared merge SHA `c85bbd3`, ancestry-verified
on `origin/ravidsrk/sweep-base` by the conductor and independently by the coordinator.

## Pipeline evidence

1. **Enumerate** (coordinator): countable claims vs reality; 3 candidates.
2. **Skeptic-triage** (worker, ro): candidates verified with pasted commands; sweep of
   README/ARCHITECTURE/AGENTS/docs found 2 more (S-1/S-2 — install docs described a
   `../../playbooks/` reference mechanism that no longer exists); CHANGELOG defect surfaced as
   an aside and folded in at FREEZE by audited coordinator decision. 0 refuted, 0 needs-human.
3. **Freeze**: F-1..F-6.
4. **Build** (worker, rw, own worktree off BASE): one commit `ed540a0`, author Ravindra Kumar,
   no trailers; negative control = revert reproduced all six false claims, then reset.
5. **Build-blind review** (worker, codex, cross-vendor): blind-fix expectations written BEFORE
   the diff was opened; PASS on spec-fidelity, standards, and truth axes; `reviewed_sha`
   recorded; reviewer artifacts verified non-identical to worker output.
6. **Integrate + conduct** (worker): PR #9 → BASE, `baseRefName` asserted,
   `headRefOid == reviewed_sha` freshness check, merge commit `c85bbd3`, ancestry + grep
   verification, branch deleted.
7. **Re-enumerate** (coordinator): badges = 25/0.2.0, layout label fixed, zero
   `../../playbooks/` claims, exactly one 0.1.1 heading → **DRY**.

## Deviations and lessons (recorded, not hidden)

- `spawn_worker.sh` exit-3'd twice on workers that were actually fine: the first heartbeat can
  land seconds after the third 40s poll. Both were left running per the liveness policy
  (activity = alive); consider a longer default `HB_POLL_SECS` for claude workers.
- One real dispatch failure: the first codex reviewer terminal wedged with no heartbeat
  (dispatch marked failed). Doctor path worked as written: evidence line → task-update → ready →
  fresh terminal → success on attempt 1/3.
- One unrelated global task existed in runtime state; scoped out via the ledger per
  liveness-resume (counted-but-untouched).

## Run-close integrity inventory (sha256)

```
5166ab89c1e60c6f94946d25e498db0037d4337f2e1abf4f6b9b341f284abd24  triage.md
f4d58053900679ace43d6bbd0401c297cfb1e46ee00877cf8ab8f2c65e54a892  build-manifest.json
673d9e6458c4df207e555f8f0e70903fbe6e7751b4bddb263bb25c23b2958476  review-blind-fix.md
121e2aa7cf94e3497977d0131a0f4717c72ccc529aaa01584fd848ea0017cb1d  review.md
3316a4cee0d339869e3c603f872604be5cc883bcb93c40887c8e21d628f6b8a3  merge.md
```

Artifacts live in the coordinator's run directory; Orca provenance holds the task/dispatch
lifecycle (`task_97bda1191e39`, `task_3cba63915e28`, `task_1541d83e1a13`, `task_87cda3091e8f`).

## Gates

- Refuted/duplicate batch gate: not needed (0 refuted, 0 duplicates).
- BASE → main promotion: **open, human-owned** — this run stops at the promotion PR.
