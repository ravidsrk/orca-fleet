# h409 — ROUND-6 fix batch: F-6 (P1) + N-4/O-2.2/O-2.4 same-class items — FROZEN

Sources: `docs/reports/h409/reaudit.md` (F-6 P1, O-2.2/O-2.4 confirmed P2) and
`docs/reports/h409/reattack-r2.md` (N-4 residual). Ruling: `docs/DECISIONS.md`
h409-f6-reloop — all mechanical under the frozen threat-model bar. This is the third re-loop;
convergence so far is P0 → P0 → P0-class → P1.

## F-6 (P1) — the executed control inherits the coordinator's uid, environment and seed reach

`verify.py:976-987` `_run_at` runs the executed negative control (`--execute-nc`) with NO `env=`,
so worker-authored code inherits the verifier's full environment (GH_TOKEN/GITHUB_TOKEN pass
through) and, on the documented `--execute-nc` + `--transcript-key` lane, runs as the same uid
that holds the coordinator seed (path visible in the parent's argv). Repro: reaudit.md §F-6
(stat/env-presence only).

**Required fix shape (all four, from the audit's fix shape):**
1. **Refuse the conjunction** `--execute-nc` + `--transcript-key` at parse time (usage exit 1),
   with guidance: sign after the control in a process that never ran it — `--transcript-out`
   then `dispatch-sign.py sign-transcript`, or a second verify.py invocation without
   `--execute-nc`.
2. **Scrub the control's environment**: `_run_at(…, env=…)` with the same allow-list discipline
   as `gh_env` MINUS the tokens — PATH, HOME, TMPDIR/TMP/TEMP, LANG/LC_* — no `GH_*`, no
   `ORCA_*`, nothing else ambient. The unit's tests do not need the coordinator's credentials.
   The scrubbed NC must still run the suite's real revert-type controls end-to-end (the existing
   executed-NC tests are your regression harness — they must stay green, and a new test must
   prove GH_TOKEN/ORCA_* do not reach the control).
3. **Docs**: `docs/verify-gate.md` §"Signed dispatch" — the in-process key lane and the executed
   control are for DIFFERENT hosts; one sentence.
4. **O-2.4 hardening rides along**: `dispatch-sign.py sign-transcript` re-hashes
   `toolchain.files` against its own siblings and refuses a mismatch; its help/docs say "sign
   only a verdict object you produced".

**Acceptance:** the reaudit.md §F-6 probe observes `gh_token_in_env: False` and
`transcript_key_in_parent_argv` moot (conjunction refused at parse); `--execute-nc` alone still
works with a scrubbed env; `--transcript-key` alone still signs; new tests above the `__main__`
guard, revert-proven.

## N-4 (P2, same class) — git/gitleaks child env is unscrubbed

The R3 scrub closed gh's env but `GIT_EXTERNAL_DIFF` and `GIT_CONFIG_COUNT`+`core.fsmonitor`
execute arbitrary code through verify.py's git legs (native/advisory lane — the worker controls
verify's env there). **Required fix shape:** a `git_env()` allow-list (PATH, HOME, TMPDIR/TMP/
TEMP, LANG/LC_* — plus the minimal git-identity/config passthrough the revert-control genuinely
needs, argued in your report) applied to every git/gitleaks invocation, exactly as `gh_env()` is
applied to gh. **Acceptance:** a planted `GIT_EXTERNAL_DIFF`/`GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=<cmd>` in the ambient env does not reach or
execute through any git leg (logged stub proof); the executed revert-control still works (git
identity via HOME's gitconfig or the repo's config, not env).

## O-2.2 (P2, consistency) — b64decode validate=True

`verify.py:2275` decodes `sig_b64` without `validate=True`; the other two consumers validate.
One-token fix + a malformed-envelope test (the re-audit's probe matrix must refuse at all three
consumers identically).

## AUTONOMY

Spawned session: auto-pick the recommended option at any taste gate; one-way doors (none
expected) block and escalate. Do NOT weaken an acceptance criterion; if one is unachievable,
STOP with a partial report naming why.

## Worker contract

- Exploit-test first per item: the finding's reproduction must REFUSE after your fix, and
  reverting the fix must make each new test fail (red-by-revert).
- Work in this worktree on branch `h409-fix-r6` (created from BASE tip). Commit per finding
  group, NO TRAILERS. Push the branch when done.
- Full suite + `python3 scripts/validate.py` green at your head ON THIS HOST; regenerate badges
  if the test count moves (`python3 scripts/gen-badges.py`). Mind the floor guard: no skip
  literals without a waiver ruling (ask first).
- Write `docs/reports/h409/fix-r6.md` (per-finding root cause, fix, verbatim refusal repro,
  revert-proof, test list) and report
  `worker_done --report-path docs/reports/h409/fix-r6.md --outcome succeeded|failed`,
  OMIT `--to`; every send carries `--from <your handle> --dispatch-capability <capability>`.
- One pack only: addy. Timebox 60 min with partial-report STOP.
