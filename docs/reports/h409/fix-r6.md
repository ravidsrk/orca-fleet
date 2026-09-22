# h409 fix — round 6 (reaudit F-6 P1 + O-2.4; reattack-r2 N-4; reaudit O-2.2)

Branch `h409-fix-r6` from BASE tip `8d5bf50d` (spec: `docs/runs/2026-09-21-harden-409/build-fix-r6.md`;
evidence: `docs/reports/h409/reaudit.md` §F-6 / O-2.2 / O-2.4, `docs/reports/h409/reattack-r2.md`
§N-4). Pack: addy (debugging-and-error-recovery → test-driven-development). Every item was
exploit-tested first (the new test written and run RED against the pre-fix verifier), then fixed,
then the fix reverted in place and the same test run RED again (revert-proof below). Host: macOS
26 (Darwin 25.6.0), Homebrew git 2.x with a live `core.fsmonitor` hook path, euid ≠ 0, Python
3.13 for the suite. Nothing below is a claim from a trace.

Commits (one per finding group, NO trailers):

| SHA | group |
|---|---|
| `1086d8de` | F-6 (P1) all four fix-shape points + O-2.4 rides along |
| `5f292d6b` | N-4 — `git_env()` on every git/gitleaks leg |
| `7e7ef989` | O-2.2 — `validate=True` |

At the round head: `python3 -m unittest discover -s tests` → **Ran 2018 tests … OK** (17 new test
methods this round); `python3 scripts/validate.py` → all 21 missions valid; badges regenerated
(`assets/badges/tests.json`: 1869 → 1886 definitions in source). No skip literal was added
(floor guard green).

---

## F-6 (P1) — the executed control inherited the coordinator's uid, environment and seed reach

**Root cause.** `_run_at` (`verify.py:976-987` at BASE) ran the control's argv with no `env=`,
so worker-authored `check.py` inherited the verifier's whole environment — the review leg's
`GH_TOKEN`/`GITHUB_TOKEN` (`gh_env()` scrubbed only gh's child) and every `ORCA_*` value. And
`main()` read the seed for `--transcript-key` BEFORE `verify()`, so on the documented in-process
key lane the control ran as the uid holding an open 0600 seed whose path sat in the parent's
argv. F-4 asserts custody against the FILE, never against who executes in the process that opened
it. Nothing refused the conjunction.

**Fix (all four points of the frozen shape).**

1. **Parse-time refusal** (`verify.py main()`): `--execute-nc` + `--transcript-key` is a usage
   error (exit 1) emitted BEFORE `_Transcript.seed()` reads the seed and before `_Authority`
   resolves or any control runs. The message names both seed-safe lanes.
2. **Scrubbed control env**: `_Authority.AMBIENT_KEEP = (PATH, HOME, TMPDIR, TMP, TEMP, LANG)` +
   prefix `LC_`; `nc_env()` is that projection of `os.environ` and nothing else; the control runs
   `_run_at(wt, argv, timeout=NC_TIMEOUT_S, env=_Authority.nc_env())`. No `GH_*`, `GITHUB_*`,
   `ORCA_*`, `GIT_*`, `SSL_CERT_FILE`, proxies. The existing executed-revert tests
   (`EndToEndMutationGreen`, `ReviewAuthorityPinnedBeforeTheControl`,
   `EveryPostControlAuthorityIsPinned`, …) stay green under it.
3. **Docs**: `docs/verify-gate.md` §"Signed dispatch" — the in-process key lane and the executed
   control are for DIFFERENT hosts; verify.py refuses the two together; sign after with
   `sign-transcript`; sign only a verdict object you produced.
4. **O-2.4 rides along** — see below.

One fixture change: `ReviewAuthorityPinnedBeforeTheControl` handed the head sha to the gh it
plants THROUGH `ORCA_HEAD` in the control's environment — exactly the channel this closes. It now
reads a file beside its log. The F-1 tests still prove what they proved.

**Refusal repro, verbatim** (scratch repo, 0600 out-of-repo seed, `GH_TOKEN=dummy-not-a-real-token`
in the launch env — the reaudit §F-6 invocation shape):

```
$ python3 runtime/scripts/verify.py --manifest manifest.json --unit-class report-only \
    --execute-nc --nc-command true --transcript-out t.json --transcript-key $SP/seed
exit 1
stderr: usage: --transcript-key cannot be combined with --execute-nc — the control runs worker code in the process that holds the seed. Sign after the control, in a process that never ran it: --transcript-out alone, then dispatch-sign.py sign-transcript; or a second verify.py invocation without --execute-nc
transcript written: False
```
`transcript_key_in_parent_argv` is moot (no such process exists). For `gh_token_in_env`, the
probe is the test itself: `TheExecutedControlRunsUnderAScrubbedEnvironment` commits a `check.py`
that appends the sorted NAMES of its environment (never a value) to a log outside the worktree
and then asserts AC-1, runs the full green executed revert with `GH_TOKEN`, `GITHUB_TOKEN`,
`GH_HOST`, `ORCA_CONTRACT_DIGEST`, `ORCA_PROVENANCE`, `ORCA_HEAD`, `GIT_CONFIG_COUNT`,
`SSL_CERT_FILE` planted, and asserts on BOTH runs of `check.py` (control, clean): none present,
no name with prefix `GH_`/`GITHUB_`/`ORCA_`/`GIT_`, while `PATH`, `HOME`, `LC_ALL` are.

**Revert-proof** (fix reverted in place, tests kept):
- `_run_at(wt, argv, timeout=NC_TIMEOUT_S)` (env dropped) →
  `FAIL: test_the_coordinators_token_and_orca_values_never_reach_the_control` (1/3 red; the two
  floor tests stay green, as they should — the floor is a subset of the ambient env).
- parse-time block deleted →
  `FAIL: test_execute_nc_with_transcript_key_is_a_usage_refusal_before_any_control_runs` (rc 0 ≠ 1,
  a control executed, a transcript signed).

**Tests** (`tests/test_verify.py`, above the `__main__` guard):
`TheExecutedControlRunsUnderAScrubbedEnvironment` ×3, `TheSeedAndTheControlNeverShareAProcess`
×3 (the refusal; `--execute-nc` alone still runs the control and writes the unsigned verdict which
`dispatch-sign.py sign-transcript` then signs and `ed.checkvalid` verifies — the documented
post-F-6 lane end to end; `--transcript-key` alone still signs).

## O-2.4 (P2) — `sign-transcript` signed whatever it was handed

**Root cause.** `dispatch-sign.py:249` checked shape only (`record.get(k) is None`); the reaudit's
probe C signed a hand-typed verdict with every toolchain hash `00…00`. After F-6 this signer IS the
seed-safe lane for an executed-control verdict, so it must be more than a stamp.

**Fix.** `dispatch-sign.TOOLCHAIN_FILES` (mirrors `verify._Transcript.TOOLCHAIN`, test-pinned) and
`toolchain_mismatch(record)`: every named file is re-hashed against `_HERE/<name>` — the signer's
own siblings — and a mismatch, a partial set, or no `toolchain.files` refuses (exit 1, nothing on
stdout). Docstring, subcommand help and `--transcript` help say "sign only a verdict object you
produced". `run_report.signed_transcript` (F-5) still binds at the PIN; this binds at SIGNING.

**Refusal repro** (the reaudit's probe C shape, via the test):
```
C sign-transcript over a HAND-TYPED verdict (all-zero toolchain.files): rc=1, stdout empty
   dispatch-sign: verdict toolchain.files pins verify.py at 000000000000…, not the file beside this signer (…) — a different verifier produced it; sign only a verdict object you produced (h409 O-2.4)
```
**Revert-proof**: `toolchain_mismatch` call removed → 3/5 red (`…hand_typed_verdict_is_refused`,
`…one_substituted_sibling_is_refused`, `…partial_or_absent_file_set_is_refused`).

**Tests** (`tests/test_dispatch_sign.py`): `SignTranscriptSignsOnlyItsOwnVerifiersVerdict` ×5.
`TranscriptSigning._RECORD` now carries the real `toolchain.files` (`_toolchain_files()`), so the
existing sign-transcript tests keep exercising the accept path.

## N-4 (P2, code-exec) — git/gitleaks ran with the ambient environment

**Root cause.** The R3 scrub was gh-only (`env=` appeared once in the file). Every git and
gitleaks `_run`/`_run_bytes`/`_run_at` inherited the launch env, and git's env is an exec channel:
`GIT_EXTERNAL_DIFF`, `GIT_CONFIG_COUNT`+`core.fsmonitor` (walks past `--no-ext-diff`, fires on
`status`/`diff --name-only`/`diff --cached` — the worktree legs around the executed control),
`GIT_SSH_COMMAND`, `GIT_PROXY_COMMAND`, `GIT_DIR`/`GIT_ALTERNATE_*`.

**Fix.** `_Authority.git_env()` = `nc_env()` + `GIT_TERMINAL_PROMPT=0`, applied unconditionally
(as `gh_env()` is) to every invocation naming the pinned git or gitleaks: `_git`, `_git_bytes`,
`_evidence_toplevel`, `_root_arg`, `_Transcript.build` (`--version`), `_gitleaks_scan`, the
worktree add/remove, and every `_run_at` git leg in `_apply_control` / `execute_negative_control`
(`_run_bytes` and `_run_at` grew an `env` kwarg). **Identity passthrough argued: none.** The legs
that touch a worktree are `revert --no-commit`, `apply --index`, `checkout -- <paths>`,
`worktree add --detach` / `remove --force`, `status`, `diff`, `rev-list`, `merge-base` — none
creates a commit or a tag, so `GIT_AUTHOR_*`/`GIT_COMMITTER_*` are never consulted; if a future leg
needs one, it is `HOME`'s gitconfig (HOME passes) or the repo's config, not env. `GIT_TERMINAL_PROMPT=0`
is a constant, not a passthrough: no leg does network, and a credential prompt would only wedge
the verifier. `--no-ext-diff --no-textconv` on the content diffs stays as belt.

**Refusal repro, verbatim** (`verify._git` under planted channels; the same env handed to bare git
first as the positive control):
```
positive control (bare git status, same env): fired = True
  verify._git(['status', '--porcelain']) -> fired = False
  verify._git(['diff', '--name-only', 'HEAD']) -> fired = False
  verify._git(['diff', 'HEAD~0', 'HEAD']) -> fired = False
  verify._git(['diff', '--cached', '--no-ext-diff']) -> fired = False
  git_env(): ['GIT_TERMINAL_PROMPT', 'HOME', 'LANG', 'PATH', 'TMPDIR']
```
The **logged stub proof** in the suite (`GitLegsRunUnderAScrubbedEnvironment`): a wrapper `git`
and a stub `gitleaks` first on PATH log the NAMES of the environment each leg was launched with,
then exec the real git; `GIT_EXTERNAL_DIFF`, `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor
GIT_CONFIG_VALUE_0=<stub>`, `GIT_SSH_COMMAND`, `GIT_PROXY_COMMAND`, `GH_TOKEN`, `ORCA_PROVENANCE`
are planted; a full green executed-revert run (every worktree leg) leaves the stub's log absent,
and both wrapper logs show `{GIT_TERMINAL_PROMPT}` as the only `GIT_*` name, no `GH_TOKEN`, no
`ORCA_*`, with `PATH`/`HOME` present. `test_the_planted_channels_are_live_on_this_host` is the
positive control (bare `git status` with the same env DOES run the stub) so an empty log is the
scrub, not a host without fsmonitor. The wrapper's dir is worker-writable, so the run carries the
R2 advisory NOTE — asserted, not skipped.

**Revert-proof**: every `env=_Authority.git_env()` → `env=None` (19 sites) →
`FAIL: test_no_planted_exec_channel_fires_through_any_git_leg` (log shows `FIRED: …stub.sh`) and
`FAIL: test_git_and_gitleaks_see_the_allowlist_and_nothing_else`.

**Tests**: `GitLegsRunUnderAScrubbedEnvironment` ×4. Two older `_run` stubs
(`CrossRepoRoots.test_the_symbol_grep_keeps_the_legacy_twenty_second_budget`,
`PinnedEvidenceBytes.test_gitleaks_runs_in_the_evidence_copy_directory`) predated the `env`
kwarg and errored once git legs pass it; they accept it now (no assertion changed).

## O-2.2 (P2) — `b64decode` without `validate=True`

**Root cause / fix.** `verify.py` `check_dispatch_provenance` decoded `sig_b64` leniently;
`run_report.py:639` and `inventory.py:304` validate. One token: `validate=True`; `binascii.Error`
is a `ValueError`, so the existing `malformed` branch catches it before `checkvalid`.

**Refusal matrix** (`MalformedEnvelopeSignaturesRefuseIdentically`): non-alphabet `*` inserted,
newline inserted, trailing `!!` → each returns `dispatch record / pubkey malformed (…)` and never
`INVALID`; and a source-level assertion that every `b64decode(` in the three consumers carries
`validate=True`. **Revert-proof**: token removed → both tests red (the matrix reads
`INVALID`, i.e. a stripped signature reached `checkvalid`).

---

## Residuals named, not fixed (out of this batch's shape)

- `HOME` passes to git (the spec's allow-list). On the native lane a worker who controls the
  launch env can point `HOME` at a gitconfig with `core.fsmonitor` — the same containment class as
  before (advisory lane; breaker is the off-worker re-run). A `-c core.fsmonitor=false -c
  protocol.ext.allow=never` belt on every git argv would close it in-process; not in the frozen
  shape, so not done — coordinator's call.
- `_load_ed25519()` / `_load_diff_scope()` still load lazily after the control (reaudit axis 6
  observation, not graded).
