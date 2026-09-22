# harden-it 409 — round-2 independent RE-ATTACK of the MERGED custody rewrite

**Red team:** task_af23a392fd97 (did NOT write any of rounds 3–5; the target is the merged tip, not mine).
**Attacked at:** `e152304e` (this worktree's HEAD — PR #493 merged, the classify()/authority rewrite of
rounds 3–5 is IN), 2026-09-22, SAFE-LOCAL profile, pack **addy** (code-review-and-quality lens +
debugging-and-error-recovery for the repros). Host: macOS/Darwin 25.6.0, euid 501 (≠0),
`/usr /usr/bin /bin /usr/sbin /sbin /usr/local/bin` root-owned 0755, `/opt/homebrew/{bin,sbin}`
euid-owned (worker-writable), `/tmp -> private/tmp`.
**Method:** every attack re-derived from scratch against my OWN harness. Classify-level battery
(`$SP/ra2/cls.py`, `cls2.py`) imports the verifier from a scratch copy of `runtime/scripts` (verify.py
loads a sibling `_verify_sig.py`) and calls `_Authority.classify()` directly; end-to-end battery
(`$SP/ra2/e2e.py`) builds a REAL two-commit mutation repo + a full valid manifest and drives
`verify.py` as a SUBPROCESS under a crafted PATH with a real committed **forged gh** (not the suite's
mock). Worker-owned drop dirs live under `$SP` (which is `/private/tmp/...`, confirmed OUTSIDE
`tempfile.gettempdir()` = `/var/folders/...`, outside cwd, outside every git toplevel — so a drop there
is caught ONLY by the ownership walk, isolating that probe exactly as review-r4 used `$HOME`). No pushes;
network limited to none needed (the sound-lane refusals return before any fetch). Nothing was written
in the repo except this file (not committed); `/opt/homebrew/sbin/gh` was never planted; the one temp
symlink for N-1b was removed inside the run (both confirmed absent afterward). `$V` = `runtime/scripts/verify.py`.

## Verdict table

| # | Attack | Result vs the merged tip |
|---|---|---|
| A1 | origin-URL inference of the review repo when `--repo` omitted (F-2) | **REFUSED** — native advisory NOTE; sound lane fails closed |
| A2 | `./`-spelled evidence path binding below the toplevel (F-3) | **REFUSED** — binds to the (absent) toplevel-relative path → RED |
| A3 | world-readable / git-tracked seed across the signers (F-4) | **REFUSED** — both custody legs refuse; out-of-repo 0600 control signs |
| A4 | sibling-script substitution vs the toolchain hash (F-5) | **REFUSED** — producer names 5 files; run_report re-hashes |
| A5 | forged gh at startup, planted in a worker-writable PATH dir (F-1) | **REFUSED** — sound lane F-1 fatal, gh never consulted |
| R1 | worker-writable `SYSTEM_BINS` dir trusted by NAME (round-1 P0) | **REFUSED** — the name-list is gone; custody is a probe |
| C-1 | symlink-to-interpreter + symlinked directory hops | **REFUSED** — every hop probed → worker-writable |
| C-2 | euid-owned 0555 file+dir | **REFUSED** — ownership probe fires before the mode bit |
| N-1 | `_nodes` hop-walker (6 sub-variants) | **REFUSED** — all fail-closed; breach direction unreachable |
| N-2 | a system binary reached THROUGH a root via symlink | **REFUSED** — the link node under the root classes worker-writable |
| N-3 | the gate fixture's system-dir discovery | **REFUSED** — its predicate IS classify(); candidate list not worker-influenced |
| N-4 | GH_ENV_KEEP allowlist / git exec-env | **RESIDUAL (P2, code-exec)** — git/gitleaks run UN-scrubbed; `GIT_EXTERNAL_DIFF` & `GIT_CONFIG_COUNT`+`core.fsmonitor` exec through verify's git legs. Contained to lanes where the worker controls verify's env (native/advisory). NO standalone sound-lane false GREEN under SAFE-LOCAL. Not a re-loop trigger. |
| N-5 | my own variants (fsmonitor, hardlink-to-root, dotdot-target link) | folded into N-1/N-4 above |

**Bottom line: A1–A5, R1, C-1/C-2, and every N-1/N-2/N-3 variant REFUSE. No new false GREEN on any
sound lane; the run does NOT re-loop. One RESIDUAL (N-4): the R3 in-process env-scrub that closed gh's
`GH_HOST` channel was NOT extended to git/gitleaks, which carry strictly stronger CODE-EXECUTION env
vars and run legs after the executed control. Under SAFE-LOCAL this is worker-controllable only where
the worker controls verify's process env (the native/advisory lane, whose breaker is the off-worker
re-run) — the SAME containment class round-1 graded R2/R3, upgraded from data-redirection to arbitrary
code execution. Reported for the coordinator's severity call, not as a sound-lane P0. GO holds.**

---

## A1 — origin inference (F-2) — REFUSED

`git remote add origin https://github.com/evil/mirror.git`, `--repo` OMITTED, real mutation manifest.

```
NATIVE lane:  NOTE: review_repo: advisory ('evil/mirror' inferred from origin, not pinned by the coordinator)
SOUND lane (--provenance ci):  rc=2, fails closed
```
On the native lane the inference is detected and recorded advisory. On the sound lane the run refuses
(rc=2); on this host, with no system gh under the admitted PATH, the F-1 "gh absent" fatal fires first
and masks the F-2 "inferred" fatal, but the refusal is terminal either way. The F-2 fatal itself is
entailed by `review_leg` ($V:889-895: `repo_source=="inferred"` and `cls.lane` set → non-NOTE fatal)
and was confirmed verbatim in round-1 on the same logic. **REFUSED.**

## A2 — `./`-spelled evidence below the toplevel (F-3) — REFUSED

NC artifact committed at `docs/reports/u/nc.txt`; manifest names `./reports/u/nc.txt`; nothing at
`<toplevel>/reports`.

```
FAIL: redaction: artifact ./reports/u/nc.txt unreadable: [Errno 2] No such file or directory:
      .../a2/reports/u/nc.txt
```
Both sides normalise the spelling identically (`Path(path).as_posix()`, $V:239/271), so the git lookup
is handed `reports/u/nc.txt` relative to the toplevel — which does not exist → RED. The `./` spelling
buys no escape from the toplevel bound. **REFUSED.**

## A3 — seed custody across the signers (F-4) — REFUSED

A throwaway `gen-key` seed, copied into a scratch repo and committed.

```
0644 tracked, dispatch-sign sign:            seed custody: committed-seed is mode 0644 — readable
                                             beyond its owner ... refusing
0644 tracked, dispatch-sign sign-transcript: seed custody: ... mode 0644 ... refusing
0600 but tracked+unignored, sign-transcript: seed custody: ... inside a git work tree that does not
                                             ignore it ... refusing
CONTROL 0600 out-of-repo:                    seed custody: <path> mode 0600, outside any unignored work tree  (signs)
```
Both custody classes (mode and worktree) refuse; the custodial 0600 out-of-repo control signs and names
its class. (`dispatch-sign.py`, `inventory.py`, `ed25519.py` are byte-identical to the round-1
refutation target — `git log adb8316a..HEAD` on them is empty — so rounds 3–5 could not have reopened
this; re-derived live anyway.) **REFUSED.**

## A4 — sibling substitution vs the toolchain binding (F-5) — REFUSED

`verify.py --transcript-out` on the real fixture:
```
toolchain.files: ['_verify_sig.py', 'diff_scope.py', 'dispatch-sign.py', 'ed25519.py', 'verify.py']
```
The envelope carries a per-file hash SET over all five loaded siblings (not just `verify_sha256`), and
`run_report.py` re-hashes `blob_at(rev, ...)` at the graded pin (14 toolchain/blob_at sites). The
byte-identical-envelope substitution C4 relied on is dead. **REFUSED.**

## A5 — forged gh at startup, planted in a worker-writable PATH dir (F-1) — REFUSED

Real mutation manifest, `--repo o/r` pinned, a real forged `gh` (returns `APPROVED` by `carol` — a
non-author — at head_sha) in `$SP/ra2/ghdrop` placed FIRST on PATH, real git from `/usr/bin`.

```
SOUND (--provenance ci):  rc=2   gh_consulted=False
   FAIL: review_authority: gh at .../ghdrop/gh is worker-writable — a lane claiming soundness
         (provenance=ci) cannot take its independent review from a binary the graded worker could have
         replaced; fail-closed (h409 F-1)
NATIVE:                    rc=0   NOTE: review_authority: advisory (gh at .../ghdrop/gh is worker-writable)
```
The pinned gh is classed worker-writable and the sound lane refuses BEFORE consulting it. The native
lane records it advisory and passes — the documented advisory behaviour whose breaker is the off-worker
re-run. **REFUSED.**

## R1 — worker-writable SYSTEM_BINS trusted by name (round-1 P0) — REFUSED

`classify('/opt/homebrew/sbin')` → **worker-writable** (round 2 short-circuited to "system" on the name;
the name-list is gone from runtime/). The classifier is now a probe over every node. **REFUSED.**

## C-1 / C-2 — symlink hops and euid-owned 0555 — REFUSED

At the classify() level, drop dir under `$SP` (ownership-walk-isolated):
```
C-1 link in writable dir -> /bin/sh                 -> worker-writable
C-1 dir-hop link (drop/sysdir->/bin), entry .../sh  -> worker-writable
C-2 owned 0555 file in owned 0555 dir (W_OK=False)  -> worker-writable
```
`_worker_controls` returns True on `st_uid==geteuid()` ($V:786) before any mode bit is read, and
`_nodes` yields the link and its target's components so a directory hop cannot smuggle a root target
past a worker-owned link. **REFUSED.**

## N-1 — the `_nodes` hop-walker (6 sub-variants) — REFUSED

| variant | result |
|---|---|
| lexical `..` staying inside a root-owned tree (`/usr/bin/../bin/sh`) | worker-writable (fail-closed; the lexical path `/usr/bin/sh` doesn't exist → `_nodes` OSError) |
| hop through the TEMP dir via a symlink (link under `$TMPDIR` → `/bin/sh`) | worker-writable (link node under the tempdir root) |
| symlink whose TARGET path contains `..` (abs and relative) | worker-writable |
| hard link to a worker-owned file inside a root-owned dir | UNBUILDABLE without root (root-owned dir is non-writable); the buildable inverse — a hardlink to `/bin/sh` inside a worker dir — classes worker-writable (parent dir owned) |
| worker dir bind-mounted below a root-owned one | unmountable here without root; argued from code — a bind mount does not change the mounted dir's `st_uid`, so `_worker_controls` still sees the worker as owner of that node → worker-writable |
| case-insensitive FS trick (`/USR/BIN/git`) | system, CORRECTLY — on APFS `/USR` and `/usr` are the same root-owned inode; the worker cannot create a separate writable `/USR`, so no bypass |

**Breach-direction proof** (`cls2.py`): a sweep of `..`-bearing paths shows every case whose REAL
(kernel-resolved) target is worker-owned classes worker-writable, and every case that classes "system"
has a root-owned real target. The lexical/`resolve(strict=True)` divergence (review-r4 N-1) always
lands fail-closed because the lexical path retains the directory holding any worker-planted link. No
construction made classify return "system" for a target the worker can write. **REFUSED.**

## N-2 — a system binary reached THROUGH a root via symlink — REFUSED

`cwd = $SP/ra2/drop`; `classify('./cwdlink')` where `cwdlink -> /usr/bin/git`:
```
./cwdlink -> /usr/bin/git  ->  worker-writable
```
The link node lies under the cwd root, so the root check ($V:816-819, `any(n==r or r in n.parents ...)`)
classes it worker-writable before the root-owned target is ever credited. The same holds for the
tempdir/toplevel/evidence-toplevel roots. **REFUSED.**

## N-3 — the gate fixture's system-dir discovery — REFUSED

`tests/test_verify_gate.py:_system_path()` admits a candidate ONLY when
`verify._Authority.classify(d) == "system"` — its predicate IS the production probe. The candidate list
is the hardcoded `("/usr/bin","/bin","/usr/sbin","/sbin")`; the worker does not choose it. So poisoning
the admitted PATH reduces to making classify() answer "system" for a writable dir — which every N-1/N-2
variant above shows is unreachable. There is no trusted-dir surface separate from classify to attack.
**REFUSED.**

## N-4 (RESIDUAL — P2, code-execution) — git/gitleaks run with an UN-SCRUBBED environment

**Finding.** F-1/R3 pinned gh and scrubbed ITS environment IN-PROCESS (`api()` passes
`env=gh_env()`, $V:851; `GH_ENV_KEEP` = PATH HOME TMPDIR TMP TEMP GH_TOKEN GITHUB_TOKEN). That in-process
scrub was **not** extended to git or gitleaks: the only `env=` in the whole file is line 851. Every git
and gitleaks `_run` inherits the full ambient environment (`env=None`, $V:112-121), including the git
EXEC channels. Confirmed by running verify's own git runner:

```
verify._git(["diff","HEAD~1","HEAD"])  with GIT_EXTERNAL_DIFF=<script>  ->  script EXECUTED
git status / git diff --name-only / git diff --cached --no-ext-diff  with
    GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=<script>  ->  script EXECUTED (all three)
```

- The content-producing diff legs ($V:1510, 1652) already carry `--no-ext-diff --no-textconv` — the
  builders anticipated `GIT_EXTERNAL_DIFF`/textconv. But `GIT_CONFIG_COUNT`+`core.fsmonitor` is a
  general env→config→exec channel that **bypasses `--no-ext-diff`** and fires on the worktree-touching
  legs ($V:1104/1123 name-only base..head, and the NC-worktree diffs $V:1590/1652 that run UNDER the
  executed control). `GIT_SSH_COMMAND`, `GIT_PROXY_COMMAND`, `GIT_CONFIG_GLOBAL/SYSTEM`, `GIT_ALTERNATE_*`
  are the same class, all un-dropped.
- **Reach / containment.** verify.py's git legs run in whatever env launched it. On a SOUND lane the
  coordinator sets the env (verify-gate.sh header: "the coordinator, not the worker, sets the env"), so
  the worker cannot inject `GIT_CONFIG_COUNT` there — I could NOT produce a sound-lane false GREEN or a
  sound-lane exec under SAFE-LOCAL without assuming a dirty coordinator launch env (out of profile).
  On the NATIVE/advisory lane the worker controls the env and this is arbitrary code execution in the
  verifier's process, but that lane is advisory (the off-worker re-run is its breaker) — the SAME
  containment round-1 assigned to R2/R3.
- **Why it still matters.** R3's own remedy was an *in-process, unconditional* scrub of gh — i.e. the
  team chose defense-in-depth over trusting the launch context. By that same standard git is a gap, and
  a strictly worse one: gh's `GH_HOST` was data redirection (needs a reachable forged host); this is
  arbitrary code execution via a textbook git channel, and the mitigation the builders DID apply
  (`--no-ext-diff`) is demonstrably partial (fsmonitor/`GIT_CONFIG_*` walk straight past it).
- **Severity — P2 residual with a P1 flavor** (bar §4: "a control is decorational / the floor drops"):
  the R3 scrub is half-installed. It is NOT graded a sound-lane P0/P1 because no sound-lane false GREEN
  is reachable under SAFE-LOCAL, so per the acceptance bar **it does not re-loop the run** — it is the
  coordinator's severity call whether to fix now or track.
- **Fix shape (for the fixer, not this red team):** route every git/gitleaks `_run` through a
  `git_env()` mirroring `gh_env()` — drop `GIT_CONFIG_COUNT`/`GIT_CONFIG_*`/`GIT_EXTERNAL_DIFF`/
  `GIT_SSH_COMMAND`/`GIT_PROXY_COMMAND`/`GIT_ALTERNATE_*` (allowlist PATH/HOME/TMPDIR/GIT_TERMINAL_PROMPT=0),
  and/or set `-c core.fsmonitor=false -c protocol.ext.allow=never` on every git argv. Closes both the
  `GIT_EXTERNAL_DIFF` and the `core.fsmonitor` keys shown above.

## N-5 — my own variants (against the same boundaries)

1. **`GIT_CONFIG_COUNT`+`core.fsmonitor` code-exec** (strongest; N-4 above) — bypasses the `--no-ext-diff`
   hardening; fires on `git status`, `git diff --name-only`, `git diff --cached`. Contained to the
   native lane under SAFE-LOCAL.
2. **hardlink to a root-owned file inside a worker dir** — classifies worker-writable (the containing
   dir's node is worker-owned); the dangerous inverse (worker file hardlinked into a root dir) is
   unbuildable without root.
3. **symlink whose relative target climbs via `..` to `/bin/sh`** — worker-writable (link's own dir is
   probed). All three fail-closed / contained; none is a sound-lane false GREEN.

---

## Scratch state
`cls.py`, `cls2.py`, `e2e.py`, the scratch `runtime/scripts` copy, the mutation/seed/dot-path scratch
repos, and the forged-gh drop all live under `$SP/ra2` only. `/opt/homebrew/sbin/gh` absent afterward;
the one `$TMPDIR` symlink (N-1b) removed inside its run; the repo working tree carries no new file
(only the pre-existing report deletions). No network call was made; no push.
