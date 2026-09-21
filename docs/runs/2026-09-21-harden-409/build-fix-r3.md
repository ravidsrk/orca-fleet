# h409 — ROUND-3 fix batch: R1 (P0) + R2/R3 residuals — FROZEN

Source: `docs/reports/h409/reattack.md` (independent re-attack, task_df10a73a7388). The re-attack
REFUSED all five original fixes (A1–A5 hold) but found ONE NEW P0 and two residuals in the same
authority-resolution class. This batch closes them. Ruling (coordinator, session-gate delegation):
fixing R1/R2/R3 is **mechanical** under the frozen threat model's acceptance bar — a sound lane
must never take its review authority (or any post-control authority) from something the graded
worker could have replaced or redirected. Recorded in `docs/DECISIONS.md`.

## R1 (P0) — classify() trusts a worker-writable SYSTEM_BINS dir by NAME

`verify.py` `_Authority.classify()` short-circuits `return "system"` when the binary's parent
directory NAME is in `SYSTEM_BINS` (verify.py:713-714), skipping the writability probe and symlink
resolution. `/opt/homebrew/bin` and `/opt/homebrew/sbin` are on that list and are worker-writable on
macOS/Homebrew hosts — a worker-planted `gh` there is classed "system" and a SOUND lane exits 0 over
a worker-authored review (demonstrated end-to-end in reattack.md §R1).

**Required fix shape:** a directory NAME must never be sufficient for "system". Apply the
writability probe (`os.access(resolved_parent, os.W_OK)`) and symlink resolution ALWAYS, for every
path including listed ones — a genuinely root-owned `/usr/bin` still classes "system" because it is
not writable by the effective user. Remove or keep the SYSTEM_BINS list as you see fit (it may
remain as a fast-path ONLY after the writability/symlink probe passes, never before).

**Acceptance (all required):**
- The reattack.md §R1 end-to-end repro FAILS CLOSED on the sound lane: a `gh` planted in
  `/opt/homebrew/sbin` (or any worker-writable listed dir) is classed worker-writable → fatal on
  `--provenance ci`, advisory on native. Drive the real repro (crafted PATH, scratch manifest),
  not only unit tests.
- A symlink in a listed dir pointing at a worker-writable target classes worker-writable (N2a).
- A genuine non-writable system binary (e.g. `/usr/bin` on this host) still classes "system" — do
  not break the real-gh happy path (the runtime-prove lanes must still pass).
- New regression tests assert all three, ABOVE the `__main__` guard so pytest collects them, and
  each test is revert-proven (fails when the fix is reverted).

## R2 (residual, same class) — git and gitleaks are not pinned

Only `gh` got F-1's startup pin + custody discipline. `git` is a bare-name `_run(["git", ...])`
throughout, and legs run AFTER the executed negative control (review-veto tree computation,
`check_symbol_on_base`); `gitleaks` is a bare `shutil.which`. A mid-run `git` plant (the C5
primitive) reaches post-control legs.

**Required fix shape:** extend the startup pin to every external authority verify.py invokes after
the control — pin `git` (and `gitleaks` where used) once at startup with the same custody
classification as `gh`; post-control invocations use the pinned absolute path, never a PATH
re-resolve. Sound-lane rule identical: worker-writable authority → fatal; native → advisory.

**Acceptance:** a `git` planted mid-run (NC-written drop dir first on PATH) is never consulted by
any post-control leg (demonstrate with a logged stub); startup-pinned worker-writable git is fatal
on a sound lane. Regression tests above the guard, revert-proven.

## R3 (residual, bounded) — the pinned gh runs with un-scrubbed ambient env

`_run`/`fetch_reviews` invoke gh with no `env=`, so `GH_HOST`/`GH_CONFIG_DIR`/etc. pass through;
`GH_HOST=attacker.example` points even a genuine gh at a forged host.

**Required fix shape:** invoke the pinned `gh` with an explicit scrubbed environment (minimal
allowlist: PATH, HOME, system temp vars; GH_TOKEN only when already present — do not pass through
`GH_HOST`, `GH_CONFIG_DIR`, or other worker-settable `GH_*` by default; a coordinator-pinned
`--repo`/host config may opt in explicitly).

**Acceptance:** `GH_HOST=<attacker>` in the ambient env does not reach the gh subprocess
(demonstrate via a gh wrapper that logs its env, on a scratch run); regression test revert-proven.

## AUTONOMY

Spawned session: auto-pick the recommended option at any taste gate; one-way doors (none expected —
all three fixes are mechanical under the frozen bar) block and escalate. Do NOT weaken an
acceptance criterion to make it pass; if one is unachievable, STOP with a partial report naming why.

## Worker contract

- Exploit-test first per item: the finding's reproduction must REFUSE after your fix, and reverting
  the fix must make the new test fail (red-by-revert).
- Work in this worktree on branch `h409-fix-r3` (already created from BASE tip). Commit per
  finding (`fix(verify): R1 — …` etc.), NO TRAILERS. Push the branch when done.
- Full suite + `python3 scripts/validate.py` must pass at your head (suite currently 1971 tests).
- Write `docs/reports/h409/fix-r3.md` (per-finding: root cause, fix, verbatim refusal repro,
  revert-proof, test list) — report it via
  `worker_done --report-path docs/reports/h409/fix-r3.md --outcome succeeded|failed`, OMIT `--to`;
  every send carries `--from <your handle> --dispatch-capability <capability>`.
- One pack only: addy. Timebox 60 min with partial-report STOP.
