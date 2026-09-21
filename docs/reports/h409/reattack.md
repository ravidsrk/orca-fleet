# harden-it 409 — independent RE-ATTACK of the F-1..F-5 fix batch

**Red team:** task_df10a73a7388 (did NOT write the fix; PR #492 / merge `adb8316a` is the target, not mine).
**Attacked at:** `adb8316a02e17a693dce8f3be26025ef28412ae1` (this worktree's HEAD), 2026-09-21, SAFE-LOCAL profile, pack **addy**.
**Method:** every attack re-derived from scratch against my OWN standalone harness
(`$SP/ra/mkfix.py` — a real two-commit mutation repo + a full valid mutation manifest, verify.py
driven as a SUBPROCESS with a crafted PATH; NOT the test suite's mocks). Throwaway keys and stub
binaries live under `$SP` (the session scratchpad) only; the sole network was read-only `gh api`
404s against a non-existent `o/r` and one that never fired (the sound-lane repo-inference refusal
returns before any fetch). Nothing outside this file was written in the repo. `$V` = `runtime/scripts/verify.py`.

## Verdict table

| # | Attack (finding it re-derives) | Result vs the fix |
|---|---|---|
| A1 | origin-URL inference of the review repo when `--repo` omitted (C1 / F-2) | **REFUSED** — sound lane fatal; native records advisory |
| A2 | `./`-spelled evidence path binding below the toplevel (C2 / F-3) | **REFUSED** — REDs at the bounded root |
| A3 | world-readable / git-tracked seed across all four signers (C3 / F-4) | **REFUSED** — 4/4 signers refuse; both custody legs |
| A4 | sibling-script substitution the toolchain hash misses (C4 / F-5) | **REFUSED** — producer names 5 files; consumer re-hash rejects |
| A5 | stub gh at startup **and** planted mid-run + executed NC (C5 P0 / F-1) | **REFUSED** — planted gh never consulted; sound lanes fail closed |
| **R1** | **classify() trusts a user-writable `SYSTEM_BINS` dir by name** (novel) | **SUCCEEDED — sound-lane FALSE GREEN. NEW P0.** |
| R2 | git/gitleaks are not pinned (only gh is) — novel residual | mechanism real; no standalone false GREEN under SAFE-LOCAL |
| R3 | the pinned gh runs with un-scrubbed ambient env (`GH_HOST`/`GH_*`) — novel residual | worker-controllable only on the advisory lane |
| CS | class sweep — evidence path traversal (boundary E) | **REFUSED** — absolute / `..` / symlink-escape all fail closed |

**Bottom line: A1..A5 all hold. One NEW P0 (R1) reopens the same lane C5/F-1 set out to close, by a
different key: the fix pins `gh` to an absolute path but then classes its custody by the PATH
directory's NAME, and two of the names it trusts (`/opt/homebrew/bin`, `/opt/homebrew/sbin`) are
worker-writable on this host. The run re-loops.**

---

## A1 — origin-URL inference (C1 / F-2) — REFUSED

Setup: real mutation repo; worker adds `origin=https://github.com/evil/mirror.git`; `--repo` omitted.

```
=== A1 native lane, --repo OMITTED, origin=evil/mirror
rc= 0
OUT: NOTE: review_repo: advisory ('evil/mirror' inferred from origin, not pinned by the coordinator)
     verify: OK — all required checks passed
=== A1 SOUND lane isolated (system gh so F-1 passes; --provenance ci; --repo OMITTED)
rc= 2
ERR: FAIL: review_repo: 'evil/mirror' was inferred from the clone's origin, which the worker
     controls — a lane claiming soundness (provenance=ci) requires an explicit --repo; fail-closed (h409 F-2)
```

Expected: sound lane refuses inference, native records it advisory. **Actual: exactly that.** The
`review_leg()` fatal (`$V:747-752`) returns before any fetch, so no network. **REFUSED.**

## A2 — `./`-spelled evidence below the toplevel (C2 / F-3) — REFUSED

Setup: NC artifact committed at `docs/reports/u/nc.txt`; manifest names `./reports/u/nc.txt`;
nothing exists at `<root>/reports`. Verifier run from `cwd=<root>/docs` and via `--git-dir <root>/docs`
— the exact divergence C2 exploited (git resolves `./` against its cwd, `_resolve` bounds against the toplevel).

```
what exists at toplevel/reports: False
(i) cwd=docs, no --git-dir           rc=2
(ii) cwd=root --git-dir docs         rc=2
--- full ERR for (i):
   FAIL: redaction: artifact ./reports/u/nc.txt unreadable: [Errno 2] No such file or directory:
         .../repo/reports/u/nc.txt
   FAIL: negative_control.artifact unreadable (./reports/u/nc.txt): [Errno 2] No such file ...
```

Pre-fix this exited 0 (git found `./reports/u/nc.txt` from `docs/`). Now both sides normalise the
spelling identically (`Path(path).as_posix()`, `$V:315`), so the git lookup is handed `reports/u/nc.txt`
relative to the toplevel — which does not exist → RED. The artifact-unreadable FAIL appears ONLY under
the `./` spelling, not the true `docs/reports/u/nc.txt` spelling (control: no such FAIL). **REFUSED.**

## A3 — world-readable / git-tracked seed, all four signers (C3 / F-4) — REFUSED

Setup: a throwaway seed `gen-key` left 0600 out-of-repo, then copied into a scratch repo, `chmod 644`,
`git add && commit` (tracked, `check-ignore` rc=1 = NOT ignored). Every signer invoked against it.

```
=== four signers vs 0644 + tracked ./committed-seed
(1) dispatch-sign sign:            rc=1 :: seed custody: committed-seed is mode 0644 — readable
                                          beyond its owner ... refusing (chmod 0600, or gen-key anew)
(2) dispatch-sign sign-transcript: rc=1 :: seed custody: ... mode 0644 ... refusing
(3) verify.py --transcript-key:    rc=1 :: usage: --transcript-key: seed custody: ... mode 0644 ... refusing
(4) inventory.py sign:             rc=2 :: inventory: could not run: seed custody: ... mode 0644 ... refusing

=== second custody leg: 0600 but tracked+unignored
dispatch-sign sign: rc=1 :: seed custody: seed is inside a git work tree that does not ignore it —
                            one `git add -A` (or a past one) makes it public; refusing

=== CONTROL: 0600 out-of-repo throwaway seed still signs
rc= 0  stderr: seed custody: .../k/tw mode 0600, outside any unignored work tree
```

Both custody classes (mode and worktree) refuse at all four use sites; a custodial 0600 out-of-repo
seed still signs and NAMES its class on stderr. **REFUSED.**

## A4 — sibling-script substitution vs the toolchain binding (C4 / F-5) — REFUSED

Two halves. Producer: verify.py `--transcript-out` now writes a per-file hash SET, not just `verify_sha256`.

```
A4a PRODUCER toolchain.files names: ['_verify_sig.py', 'diff_scope.py', 'dispatch-sign.py',
                                     'ed25519.py', 'verify.py']
     (pre-fix C4 exposed only verify_sha256, covering 1 of 5 loaded files)
```

Consumer: a scratch repo commits pristine `runtime/scripts/*`, an attacker substitutes `_verify_sig.py`
(`_failure_signature` → always `(True, None)`) and commits it at the graded pin; a transcript replays the
PRISTINE hashes. run_report's binding (`run_report.py:702-716`, re-hashing `blob_at(rev, ...)`) is run verbatim:

```
A4b CONSUMER binding result: REFUSED
   - toolchain.files pins runtime/scripts/_verify_sig.py at acc3d5cfb0f6…, not the file at
     dcb732e0 — substituted sibling
```

The byte-identical signed envelope C4 relied on is dead: the envelope now carries per-sibling hashes and
run_report re-derives them from the graded checkout. **REFUSED.**

## A5 — gh at startup AND planted mid-run + executed NC (C5 P0 / F-1) — REFUSED

Setup: `drop/` is an EMPTY user-writable dir FIRST on PATH; the worker's committed `check.py` (run by the
executed negative control) writes a fabricated-APPROVED `gh` into `drop/` and logs every call, THEN asserts
the criterion. Four sub-cases; in EVERY one the NC executed worker code (which DID plant the gh) yet the
planted gh was NEVER consulted:

```
A5.1 stand-in gh at startup, NATIVE lane
   NOTE: negative control EXECUTED ... (RED, as required)
   NOTE: review_authority: advisory (gh at .../realgh/gh is worker-writable)
   FAIL: mutation unit: cannot fetch reviews for o/r#7 (gh: Not Found (HTTP 404)) — fail-closed
   rc=2   planted gh?: True | CONSULTED?: False

A5.2 same, SOUND lane (--provenance ci)
   FAIL: review_authority: gh at .../realgh/gh is worker-writable — a lane claiming soundness
         (provenance=ci) cannot take its independent review from a binary the graded worker
         could have replaced; fail-closed (h409 F-1)
   rc=2   planted gh?: True | CONSULTED?: False

A5.3 G-1: NO gh at startup (git-only PATH), NATIVE lane
   NOTE: review_authority: advisory (gh absent at startup ... never re-resolved — h409 F-1)
   FAIL: ... cannot fetch reviews for o/r#7 (gh absent at startup ...) — fail-closed
   rc=2   planted gh?: True | CONSULTED?: False

A5.4 G-1 SOUND lane, no gh at startup
   FAIL: review_authority: gh absent at startup ... — a lane claiming soundness (provenance=ci)
         has no independent review authority to consult; fail-closed
   rc=2   planted gh?: True | CONSULTED?: False
```

The authority is pinned once before the control; a mid-run PATH write can no longer redirect the review
leg, and "gh absent at startup" is terminal (round-1's re-resolve-after-control hole is closed). **REFUSED.**

---

## R1 (NEW — P0) — classify() trusts a worker-writable `SYSTEM_BINS` dir by NAME → sound-lane FALSE GREEN

**This is the same lane A5 defends, defeated by a different key.** F-1 pins `gh` to an absolute path
(`$V:690`), then classes its custody (`_Authority.classify`, `$V:707-731`). classify decides "system" from
the PATH entry's **directory name** and returns BEFORE it ever probes writability or resolves a symlink:

```python
# $V:713-714
entry = Path(path)
if str(entry.parent) in cls.SYSTEM_BINS:   # <-- early return; the os.access(W_OK) probe below is skipped
    return "system"
```

`SYSTEM_BINS` (`$V:663-665`) includes `/opt/homebrew/bin` and `/opt/homebrew/sbin`. On this host — and on
any macOS/Homebrew dev host or CI image — **those directories are writable by the graded worker:**

```
-- are the trusted SYSTEM_BINS actually non-writable here?
  /usr/bin            writable_by_me=False
  /usr/local/bin      writable_by_me=False
  /opt/homebrew/bin   writable_by_me=True      <-- trusted by name, WRITABLE
  /opt/homebrew/sbin  writable_by_me=True      <-- trusted by name, WRITABLE
```

Two classifier bypasses, confirmed by calling `classify()` directly:

```
-- N2a classify(symlink in a system-bin dir -> worker-writable /tmp target)
  /opt/homebrew/bin: classify -> 'system'   (target=/private/var/folders/.../evil-gh)
-- N2b classify(plain binary placed in a user-writable system-bin dir)
  /opt/homebrew/bin: classify -> 'system'   (dir writable, but classed by NAME)
```

**End-to-end, SOUND lane, verbatim** (stub planted in `/opt/homebrew/sbin`; the real gh in
`/opt/homebrew/bin` was never touched; the probe was removed afterward):

```
which gh (subprocess PATH) -> /opt/homebrew/sbin/gh
SOUND lane (--provenance ci), worker-planted gh in /opt/homebrew/sbin: rc= 0
    verify: OK — all required checks passed
   stub gh CONSULTED?: True | verdict: FALSE GREEN (exit 0)
cleaned up: True
```

Setup: real mutation manifest, `--repo o/r` pinned CORRECTLY by the coordinator, `--provenance ci`. The
graded worker writes a `gh` into a user-writable `SYSTEM_BINS` directory that lands first on PATH; it
returns a fabricated `APPROVED` at `head_sha` by a non-author. classify → "system" → the sound lane
consults it → **exit 0 over a review the worker authored.**

- **Expected (F-1's own acceptance criterion):** "a worker-writable gh → fatal on a sound lane." **Actual:
  exit 0**, because a worker-writable dir is mis-classed "system" whenever its name is on the list.
- **Severity — P0** (threat model §4): "an enforcement bypass on a lane documented as sound" and
  "worker-authored input making verify.py exit 0 over forged … evidence (false GREEN)" — the independent
  review is the forged leg. This is precisely the C5/P0 class the run was convened to close.
- **Root cause:** the fix HAS the right probe (`os.access(p.parent, os.W_OK)`, `$V:727`) but the
  `SYSTEM_BINS` name-match short-circuits past it. The carve-out was a conscious decision in the build
  report ("`/opt/homebrew/bin` included … Homebrew's Cellar is user-owned … carves system bins out by
  convention") — that convention is the hole: it trusts, by name, directories the adversary can write.
- **Precondition & reach:** the worker can write to any listed dir that precedes the real gh on PATH.
  On this host that is `/opt/homebrew/bin` (where the real gh lives — a direct replace) and
  `/opt/homebrew/sbin`. GitHub-hosted runners: `/usr/local/bin` and the Homebrew prefix are commonly
  writable by the runner user — argued from the code (classify trusts by name regardless of host), not
  exercised live (no network).
- **Fix shape (for the fixer, not this red team):** drop the early `return "system"` for a name match and
  ALWAYS apply the `os.access(...W_OK)` / symlink-resolve probe (a genuinely root-owned `/usr/bin` still
  classes system because it is not writable); or remove the user-writable Homebrew dirs from `SYSTEM_BINS`;
  or resolve the symlink before the name check. Any of the three closes both N2a and N2b.

## R2 (novel residual) — git and gitleaks are NOT pinned; only gh is

```
_Authority pins: ['custody','gh'] -> only 'gh'; git/gitleaks are bare shutil.which/_run
git/gitleaks which() sites: 1797: shutil.which("gitleaks") | 2403: shutil.which("git")
```

`git` is a bare-name `_run(["git", ...])` throughout, and several legs run AFTER the executed control —
the review-veto tree computation (`_tree`/`_wtree_bound`/`_equivalent_review_shas`) and
`check_symbol_on_base` (`$V:1890`). A mid-run `git` plant (the same primitive C5 used for gh) reaches those
legs. Under SAFE-LOCAL I could not turn this into a standalone false GREEN: the only lanes I can drive to
exit 0 are the native/advisory lane (already advisory — the off-worker re-run is its breaker) or R1 (which
already yields a full false GREEN without needing git). A sound-lane escalation via git alone would need a
genuine GitHub approval at a stale sha (a live PR — ask-first, out of profile). **Reported as a residual /
class observation, not graded P0/P1 on its own:** the ordering discipline F-1 applied to gh was not
extended to the other worker-influenceable authorities it invokes after the control. Boundary E's own
residual already flags git filters/smudge in the NC worktree; this is the adjacent gap in the main process.

## R3 (novel residual) — the pinned gh runs with un-scrubbed ambient environment

```
verify.py env= / os.environ occurrences: (none — gh runs with ambient env, no scrub)
```

`_run` / `fetch_reviews` invoke the pinned `gh` with no `env=`, so `GH_HOST`, `GH_TOKEN`, `GH_CONFIG_DIR`
etc. pass through. `GH_HOST=attacker.example` would point even a genuine system gh at an attacker's GitHub
Enterprise host returning a forged APPROVED. On a sound lane (ci/mcp/sdk) the environment is coordinator-set,
so this is worker-controllable only on the native/advisory lane (boundary C: "every ORCA_* value is
attacker-influenceable in the native lane"). **Residual, bounded to advisory** — but it is an un-probed
channel through the newly-pinned binary, and pinning the path while leaving the env open is a half-measure
worth closing alongside R1 (invoke gh with a scrubbed `env=`).

## Class sweep — evidence path traversal (boundary E) — REFUSED

```
_resolve('absolute path'  ): REFUSED: absolute evidence path refused — must be repo-relative (#267)
_resolve('dotdot escape'  ): REFUSED: evidence path escapes the repo toplevel (#267): ../secret.txt
_resolve('symlink escape' ): REFUSED: evidence path escapes the repo toplevel (#267): link.txt
_resolve('legit in-repo'  ): allowed -> .../repo/a.txt
```

Absolute, `..`, and an in-repo symlink to an out-of-repo target all fail closed; a legitimate in-repo path
resolves. Boundary E containment holds. **REFUSED.**

---

## Summary for triage

- **A1..A5 REFUSED / fail closed** — the five confirmed fixes hold against re-derived attacks, including
  the C5 P0 same-run gh plant on both the present-at-startup and absent-at-startup paths.
- **R1 is a NEW P0** — `classify()`'s `SYSTEM_BINS` name-match short-circuits the writability probe, so a
  worker-planted gh in a user-writable but trusted-by-name directory (`/opt/homebrew/bin`,
  `/opt/homebrew/sbin` here) is classed "system" and a **sound lane exits 0 over a worker-authored review**.
  Demonstrated end-to-end. This reopens the exact C5/F-1 lane and re-loops the run.
- **R2 (git/gitleaks unpinned)** and **R3 (un-scrubbed gh env)** are novel residuals in the same authority-
  resolution class; neither is a standalone false GREEN under SAFE-LOCAL, but both are the natural next
  moves once R1 is closed and should be fixed in the same pass (pin/scrub every authority verify invokes
  after the control, not only gh).
- **Not done (SAFE-LOCAL / 45-min timebox):** no live-PR confirmation of R1 on a GitHub-hosted runner (the
  writability of `/usr/local/bin` there is argued from the code, not exercised); no live git-plant false
  GREEN for R2. All scratch state is under `$SP/ra`; the sole network was read-only `gh api` 404s against a
  non-existent `o/r`; the `/opt/homebrew/sbin/gh` probe was created and removed within the R1 run and the
  real gh was never touched.
