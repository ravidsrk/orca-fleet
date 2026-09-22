# h409 fix — round 4 (review-r3 C-1, C-2, R-1, R-2, R-3, N-1, N-2)

Branch `h409-fix-r3`, continuing from `fb3f68c9` (the round-3 head merged to the review branch;
review: `docs/reports/h409/review-r3.txt`, ruling: `docs/DECISIONS.md` h409-r3-review-reloop).
Pack: addy (debugging-and-error-recovery → test-driven-development). Every finding was
reproduced against the round-3 `verify.py` FIRST (`git show fb3f68c9:runtime/scripts/verify.py`
swapped into a scratch copy of the tree), then fixed, then the same reproduction re-run — and
every new test was run against the round-3 verifier as the negative control. Host: macOS 26
(Darwin 25.6.0), Homebrew, euid ≠ 0, `/usr/bin` `/bin` `/usr/sbin` `/sbin` root-owned 0755;
Python 3.13.15 for the suite, `/usr/bin/python3` 3.9.6 for the gate subprocess on the sound lane
(see R-1). Nothing below is a claim from a trace.

Commits (one per finding group, no trailers):

| SHA | group |
|---|---|
| `b35e6dc2` | C-1 + C-2 + R-2 + R-3 — `classify()` rewrite and `EveryHopAndEveryOwnerIsProbed` |
| `095831d9` | R-1 — gate fixture rebuilt per the ruling; `SoundLaneAuthoritiesAreSystemClass` |
| `b6cddec1` | N-2 — fetch-failure fatal names the scrub; badge regenerated |
| `086d69cf` | test hygiene: the consulted log lives outside the 0555 drop dir (see C-2) |
| `HEAD` (see git log) | test hygiene: `ReviewAuthorityPinnedBeforeTheControl.test_a_system_gh_is_classed_system` used `/usr/bin/gh`, absent here — a node the probe cannot stat is fail-closed; it now picks a binary the host has |

C-1, C-2, R-2 and R-3 share one commit deliberately: they are all one function (`classify()`),
and the R-3 test class is the vehicle that proves the other three on every host.

---

## C-1 (Critical) — a worker-planted symlink whose target is root-owned classed "system"

**Root cause.** `classify()` did `Path(path).resolve()` first and probed only the RESOLVED file
and its parent with `os.access(W_OK)`. The PATH entry's own directory — the one the worker writes
the link into and can re-point — was never probed, and no intermediate symlink hop was either.
`drop/gh -> /bin/sh` therefore classed system, and the sound lane ran `sh api --paginate
repos/o/r/pulls/7/reviews`: `sh` resolves `api` against its cwd, the graded repo.

**Fix** (`runtime/scripts/verify.py` `_Authority._nodes`, `classify`). `classify()` now resolves
the path BY HAND: `_nodes()` walks every directory component from `/` down, `lstat`s each, and at
a symlink yields the link itself, then restarts on the link's target joined with the remaining
components (a `..` after a symlink-free prefix is collapsed exactly as the kernel would). Every
node of every hop is probed (see C-2 for the probe). A node it cannot stat — missing target,
loop, >40 hops — raises and classes worker-writable: a hop that cannot be probed cannot be
trusted. `Path.resolve(strict=True)` is kept beside the walk for the root check.

**Repro, round-3 verifier (false green)** — `test_c1_the_sound_lane_refuses_the_symlinked_interpreter_and_never_runs_the_repo_script`
with the drop dir under `$HOME` (outside temp/cwd/toplevel), `drop/gh -> /bin/sh`, an `api` script
in the graded repo's working tree (the verifier's cwd) that forges an APPROVED at head by carol, `--provenance ci`, `--repo o/r`,
git pinned system:

```
[round-3 verify.py fb3f68c9] rc=0
verify: OK — all required checks passed
consulted?: True ['SH-API ARGV: --paginate repos/o/r/pulls/7/reviews', 'SH-API ARGV: repos/o/r/pulls/7']
```

**Repro, this head (refused):**

```
rc=2
FAIL: review_authority: gh at /Users/ravindra/orca-h409-r4-ucy5uqqf/gh is worker-writable — a lane claiming soundness (provenance=ci) cannot take its independent review from a binary the graded worker could have replaced; fail-closed (h409 F-1)
verify: 1 invariant(s) failed — unit is NOT done
consulted?: False
```

Also at the classify() level, pre-fix → post-fix: `classify($HOME/c1-x/gh -> /bin/sh)`:
`system` → `worker-writable`; a DIRECTORY hop (`drop/sys -> /bin`, entry `drop/sys/sh`, which
resolves to root-owned `/bin/sh`): `worker-writable` now, `system` before.

## C-2 (Critical) — W_OK is a mode probe; a worker-OWNED 0555 dir classed "system"

**Root cause.** `os.access(p, W_OK)` is false for a directory the effective user owns at 0555 —
a mode the owner sets and unsets at will. Ownership was never consulted.

**Fix** (`_Authority._worker_controls`). Every node from C-1's walk is probed for: `st_uid ==
os.geteuid()`; `S_IWOTH`; `S_IWGRP` with `st_gid` in `{os.getegid(), *os.getgroups()}`; and,
for non-links, `os.access(W_OK)` (ACLs). A link's own writability is its directory's, which is
the node before it. `/`, `/usr`, `/usr/bin`, `/usr/bin/git` are root-owned 755 on macOS and on
the ubuntu runners, so a genuine system git still classes system. When the verifier itself runs
as root every node is "owned" — that is fail-closed and the same answer W_OK already gave root.

**Repro, round-3 verifier (false green)** — `test_c2_the_sound_lane_refuses_a_gh_in_a_worker_owned_0555_dir`:
stub gh under `$HOME/orca-h409-r4-*/gh`, file and dir chmod 0555, `st_uid == euid`,
`os.access(dir, W_OK) == False` asserted in the test:

```
[round-3 verify.py fb3f68c9] rc=0
verify: OK — all required checks passed
consulted?: True ['PLANTED-GH ARGV: api --paginate repos/o/r/pulls/7/reviews', 'PLANTED-GH ARGV: api repos/o/r/pulls/7']
```

**Repro, this head (refused):**

```
rc=2
FAIL: review_authority: gh at /Users/ravindra/orca-h409-r4-5isr8uhs/gh is worker-writable — a lane claiming soundness (provenance=ci) cannot take its independent review from a binary the graded worker could have replaced; fail-closed (h409 F-1)
verify: 1 invariant(s) failed — unit is NOT done
consulted?: False
```

(`086d69cf`: the stub's log first lived beside it in the 0555 dir, where the stub could not write
it, so "never consulted" was vacuous on both verifiers; the log now lives in the run's writable
tools dir, and the round-3 transcript above shows the stub consulted twice.)

## R-1 (Required) — the 0555 sysbin gate fixture

**Root cause.** `tests/test_verify_gate.py` hard-linked the host's git/gh/gitleaks into a mkdtemp
dir the effective user owned and chmod'ed it 0555: the C-2 shape as the happy path; RED with
`TMPDIR=/tmp` (the child's `gettempdir()`); a leaked `vgate-sysbin-*` per run (rmtree cannot empty
0555); `chmod` through a hard link onto the host binary.

**Fix** (`095831d9`, per the ruling: review R-1 option b). `run_gate()` decides the lane: a
run that claims soundness (provenance set, or a dispatch record the gate may pair with a
discovered key — verify.py's `enforcement` lane) gets `PATH` = `_system_path()`, the subset of
`/usr/bin:/bin:/usr/sbin:/sbin` that exists AND that `verify._Authority.classify()` — the
production probe, imported from `runtime/scripts/verify.py` — classes system. `_require_system_tools("git",
"python3")` raises `unittest.SkipTest` naming the tool and the reason when git has no instance
there or is not system-class by the probe, or when `python3` (which `verify-gate.sh` runs from
PATH; not an authority, presence suffices) is absent. The native lane keeps the host PATH and
records Homebrew authorities as NOTEs, as before. Nothing is created, linked, chmod'ed or left
behind. `_system_bin()` and its atexit hook are gone.

Evidence on this host: `python3 -m unittest -v tests.test_verify_gate` — the 10 sound-lane tests
(`VerifyGateDispatchPinDiscovery` ×4, `VerifyGateTrustBoundary.test_no_note_when_provenance_offworker`,
`VerifyGateSignedDispatch` ×4 with a record, plus the new class) all `ok`, none skipped; with
`TMPDIR=/tmp` (the Linux temp layout the review reproduced RED) → `Ran 27 tests … OK`; with the
candidate list patched to a nonexistent dir → `skipped 'no root-owned system bin dir on this host
(candidates: /nonexistent-sysdir)'`. `ls $TMPDIR/vgate-sysbin-*` and `ls ~/vgate-owned-*` after
the suite: none. The gate subprocess ran under `/usr/bin/python3` (3.9.6) on the sound lane and
verify.py ran there without change.

Ubuntu CI reasoning: `/usr/bin/{git,gh,python3}` are dpkg-installed, root:root 755, on
`ubuntu-latest`; `/bin` is a root-owned symlink to `usr/bin` (the walk follows it and probes both);
mkdtemp no longer participates at all, so where `/tmp` lands is irrelevant; setup-python's
`/opt/hostedtoolcache` (runner-owned) is off the sound-lane PATH, so the system 3.12 runs
verify.py there — no 3.13-only syntax is used (3.9 runs it here).

New tests (`SoundLaneAuthoritiesAreSystemClass`):
- `test_the_sound_lane_path_is_root_owned_system_dirs_only` — every dir on the sound-lane PATH is
  a candidate, classes system by the probe, and no ancestor is owned by the euid.
- `test_a_worker_owned_0555_dir_first_on_the_sound_lane_path_is_refused` — the round-3 fixture's
  shape planted deliberately (a euid-owned 0555 dir under `$HOME` with a git stub, first on the
  sound-lane PATH; COPIED script, not a link; chmod'ed back to 0755 before rmtree via LIFO
  cleanups) → rc 2 `authority: git at …/vgate-owned-*/git is worker-writable … (h409 R2)`.
  Against the round-3 verifier: `AssertionError: 0 != 2` — the gate let it through.

## R-2 (Required) — cwd `/` made every path worker-writable

**Fix.** In the root loop, a root whose resolved path is its own anchor (`Path("/")`) is skipped;
the per-node ownership probe covers `/` itself (it is lstat'ed as the first node), so a writable
`/` still classes worker-writable through C-2. Test
`test_r2_a_cwd_of_root_does_not_class_a_root_owned_binary_worker_writable`: `os.chdir("/")`,
`classify("/bin/sh") == "system"`; against both older verifiers → `worker-writable` (FAIL).

## R-3 (Required) — the probe branch was never hit by a unit test

**Fix.** `EveryHopAndEveryOwnerIsProbed` builds its drop dir with `tempfile.mkdtemp(dir=Path.home())`,
chmod 0755, and `skipTest`s with the path named if `$HOME` turns out to lie under
temp/cwd/toplevel (`_outside_every_root`), or when euid is 0. Every class in the file therefore
comes from the probe, never from the root check. `SYSTEM_BINS` is patched to `(drop,)` with
`create=True` so the pre-round-3 name-list verifier trusts the dir by name.
`test_r3_a_plain_gh_in_an_owned_0755_dir_outside_every_root_is_worker_writable` and
`test_r3_the_sound_lane_refuses_a_gh_in_an_owned_0755_dir_outside_every_root` — against the
pre-round-3 verifier (`3b5c0ea8`, name list) both FAIL (`system` / rc 0); against the round-3
verifier both pass (0755 is W_OK-writable — they are positive controls for the round-3 branch,
which is what the review asked to be proven present on every host).

## N-1 (Nit) — qualifying the ERROR-on-revert tests

Round 3's three interface-only revert bites are, unchanged:
`ThePinnedGhRunsUnderAScrubbedEnvironment.test_the_allowlist_is_the_whole_environment`,
`EveryPostControlAuthorityIsPinned.test_git_is_pinned_absolute_at_startup_and_every_leg_runs_it`,
`…test_gitleaks_is_pinned_absolute_and_its_custody_recorded` — each ERRORs on the pre-round-3
verifier with `AttributeError` on a new attribute (`GH_ENV_KEEP`, `git`, `gitleaks`): they prove
the interface exists, not the behaviour, and stand beside the nine behavioural FAILs.

This round adds ONE more of that kind:
`EveryHopAndEveryOwnerIsProbed.test_c2_a_worker_owned_0555_file_in_a_root_owned_dir_is_worker_writable`
calls `_worker_controls` directly and ERRORs (`AttributeError`) on both older verifiers. Every
other new test bites behaviourally (table below).

## N-2 (Nit) — the scrub is named in the fatal

`_Authority.SCRUB_NOTE` is appended to the `cannot fetch reviews` fatal whenever a gh was pinned
(not when custody is `absent`, where the cause is already named):
`(gh ran under a scrubbed environment: XDG_CONFIG_HOME, HTTPS_PROXY/NO_PROXY and SSL_CERT_FILE are
dropped with every other steering variable — only PATH, HOME, TMPDIR, TMP, TEMP, GH_TOKEN,
GITHUB_TOKEN pass; h409 R3)`. Test: `test_a_fetch_failure_names_the_scrub` (a gh stub that exits
1 → one fatal carrying the three names). No runtime doc changed (activation-load budget).

---

## Revert proof — the whole table

Scratch copy of the tree with `runtime/scripts/verify.py` swapped for the named commit's; the
tests are this head's. R3 = `fb3f68c9` (round-3 verifier), R2 = `3b5c0ea8` (pre-round-3 name list).

| test | R3 | R2 |
|---|---|---|
| `EveryHopAndEveryOwnerIsProbed` (12) | 8 FAIL, 1 ERROR (interface), 3 pass¹ | 11 FAIL, 1 ERROR (interface) |
| `AuthorityCustodyIsAProbeNotAName.test_a_binary_in_a_dir_this_user_cannot_write_is_still_system` (rewritten: real binaries + a missing node is fail-closed) | FAIL | — |
| `ReviewAuthorityPinnedBeforeTheControl.test_a_system_gh_is_classed_system` (rewritten: an existing binary) | pass (exemplar only) | — |
| `SoundLaneAuthoritiesAreSystemClass.test_a_worker_owned_0555_dir_first_on_the_sound_lane_path_is_refused` | FAIL (`0 != 2`) | — |
| `SoundLaneAuthoritiesAreSystemClass.test_the_sound_lane_path_is_root_owned_system_dirs_only` | pass (fixture self-check) | — |
| `ThePinnedGhRunsUnderAScrubbedEnvironment.test_a_fetch_failure_names_the_scrub` | FAIL² | — |

¹ the three that pass on R3: the two R-3 cases (positive controls for the round-3 W_OK branch,
as designed) and `test_c1_a_link_loop_or_a_dangling_link_fails_closed` (round 3 already
fail-closed a loop via `resolve()` raising, and a dangling link via W_OK on its dir).
² not run separately; `SCRUB_NOTE` does not exist on R3, so the assertion on the fatal text fails.

## Test list (all above the `__main__` guard)

`tests/test_verify.py` — `EveryHopAndEveryOwnerIsProbed`:
`test_c1_a_symlink_in_a_writable_dir_to_a_system_interpreter_is_worker_writable`,
`test_c1_the_sound_lane_refuses_the_symlinked_interpreter_and_never_runs_the_repo_script`,
`test_c1_the_native_lane_records_the_symlinked_interpreter_as_advisory`,
`test_c1_a_symlinked_directory_hop_inside_a_writable_dir_is_worker_writable`,
`test_c1_a_link_loop_or_a_dangling_link_fails_closed`,
`test_c2_a_worker_owned_0555_dir_is_worker_writable`,
`test_c2_the_sound_lane_refuses_a_gh_in_a_worker_owned_0555_dir`,
`test_c2_the_native_lane_records_a_worker_owned_0555_dir_as_advisory`,
`test_c2_a_worker_owned_0555_file_in_a_root_owned_dir_is_worker_writable`,
`test_r3_a_plain_gh_in_an_owned_0755_dir_outside_every_root_is_worker_writable`,
`test_r3_the_sound_lane_refuses_a_gh_in_an_owned_0755_dir_outside_every_root`,
`test_r2_a_cwd_of_root_does_not_class_a_root_owned_binary_worker_writable`;
`AuthorityCustodyIsAProbeNotAName.test_a_binary_in_a_dir_this_user_cannot_write_is_still_system`
(rewritten); `ReviewAuthorityPinnedBeforeTheControl.test_a_system_gh_is_classed_system` (rewritten);
`ThePinnedGhRunsUnderAScrubbedEnvironment.test_a_fetch_failure_names_the_scrub`.
`tests/test_verify_gate.py` — `SoundLaneAuthoritiesAreSystemClass` (2, above).

## Suite and validator at this head, on this host

At `c0194463` (the last code/test commit; this report is the commit after it): `python3
scripts/validate.py` → "All 21 missions valid; three-layer separation holds; evals valid."
`python3 -m unittest discover -s tests` → "Ran 2000 tests in 741.592s … OK" (2026-09-22 01:10 IST;
the 741s is contention with an earlier run, the first pass of the same suite took 321s and failed
only the `/usr/bin/gh` exemplar fixed in `c0194463`). After the suite: no `orca-h409-r4-*` or
`vgate-owned-*` under `$HOME`, no `vgate-sysbin-*` under `$TMPDIR`.
