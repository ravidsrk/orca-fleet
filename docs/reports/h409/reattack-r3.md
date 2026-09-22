# harden-it 409 — round-3 FINAL independent RE-ATTACK of the merged env-scrub tip

**Red team:** task_757b43368636 (did NOT write any of rounds 3–6; the target is the merged tip, not mine).
**Attacked at:** `7e0c6f85` (this worktree's HEAD — PR #494 merged, the F-6 parse-time refusal +
scrubbed control env + N-4 `git_env()` are IN), 2026-09-22, SAFE-LOCAL profile, pack **addy**
(code-review-and-quality lens + debugging-and-error-recovery for the repros). Host: macOS/Darwin
25.6.0, euid 501 (≠0), Python 3.13.15; `/usr/bin /bin /usr/sbin /sbin` root-owned, `/opt/homebrew/{bin,sbin}`
euid-owned (worker-writable); `/private/tmp/...scratchpad` (= `$SP`) confirmed OUTSIDE
`tempfile.gettempdir()` (`/var/folders/...`), so a drop there is isolated to the ownership walk.
**Method:** every attack re-derived from scratch against my OWN harness under `$SP/ra3`: a scratch copy
of `runtime/scripts` (so `verify.py` loads its real siblings); a REAL two-commit mutation repo
(`$SP/ra3/repo`, `build_repo.sh`) whose criterion-bound `check.py` logs the NAMES of the environment it
was launched with and asserts AC-1; the real `verify.py` driven both as a SUBPROCESS (real CLI) and via
a direct `execute_negative_control` / `_Authority` call for the channels the CLI gates behind unrelated
invariants. Throwaway Ed25519 seed via `dispatch-sign.py gen-key` into `$SP/ra3/keys` (0600, out of repo).
No pushes; no network (every sound-lane refusal returns before any fetch); no key bytes read; the only
repo write is this file (not committed). `$V` = `runtime/scripts/verify.py`, `$DS` = `dispatch-sign.py`.

## Verdict table

| # | Attack | Result vs the merged tip |
|---|---|---|
| A5 | forged worker-writable `gh`, sound lane | **REFUSED** — classed `worker-writable`, lane `provenance=ci` set → review leg fails closed; native → advisory |
| R1 | worker-writable `SYSTEM_BINS` trusted by name | **REFUSED** — `/opt/homebrew/sbin` → worker-writable; `/usr/bin`,`/bin` → system |
| C-1 | symlink-to-interpreter in a writable dir | **REFUSED** — worker-writable |
| C-2 | euid-owned 0555 file+dir | **REFUSED** — ownership probe fires before the mode bit |
| N-2 | system binary through cwd via symlink | **REFUSED** — link node under the cwd root → worker-writable |
| B1 | F-6 conjunction refusal (all spellings) | **REFUSED** — space/`=`/repeated/reversed/prefix-abbrev all exit 1, no transcript; no `ORCA_*` env forms it |
| B2 | nc_env escape — every allowed name + interpreter env | **REFUSED** — control env is `{HOME,LANG,LC_*,PATH,TMPDIR}` only; PYTHONPATH/PYTHONSTARTUP/NODE_OPTIONS/BASH_ENV/ENV and all GH_/GITHUB_/ORCA_/GIT_/SSL_ dropped |
| B3 | git_env escape — GIT_* / GIT_CONFIG_GLOBAL | **REFUSED** at env level — every `GIT_*` dropped; real-CLI: planted `GIT_EXTERNAL_DIFF`/`core.fsmonitor` channel never fires through verify's git legs (positive control fires) |
| B4 | HOME → `~/.gitconfig` `core.fsmonitor` | **RESIDUAL (P2, native-lane only)** — the known F-6/N-4 P2; executes under `git_env()` (HOME kept); demonstrated it cannot cross to a sound lane |
| B5 | repo-local `.git/config` `core.fsmonitor` | **RESIDUAL (P2, native-lane only, new characterization)** — env-INDEPENDENT (git_env cannot close it), but the fresh clone a sound lane operates on drops it (`core.fsmonitor` UNSET post-clone) |
| B6 | sign-transcript toolchain re-hash | **REFUSED** — real verdict signs; all-zero / substituted / partial / no-files all exit 1, no envelope; symlinked sibling → fail-closed |
| V2 | own variant — TMPDIR redirect of the NC worktree | **REFUSED (native-lane surface, same class)** — classify treats a redirected tempdir root as worker-writable (launders nothing); worktree lands under worker TMPDIR = native-lane race, boundary-E residual |
| V3 | own variant — LC_* as a data/code channel | **REFUSED** — LC_* passes as a locale STRING only; git/py load no file from it |

**Bottom line: A5, R1, C-1/C-2, N-2 and the whole new-machinery battery (B1–B3, B6) REFUSE. No new false
GREEN on any sound lane; the run does NOT re-loop. Two RESIDUALS, both `core.fsmonitor` code-execution
NATIVE-LANE ONLY, the same containment class the coordinator already tracks as N-4/F-6 P2: B4
(HOME→`~/.gitconfig`, re-confirmed) and B5 (repo-local `.git/config`, a NEW env-independent
characterization of the same class — but clone-gated, so still native-only). Neither produces a
sound-lane false GREEN; both are the coordinator's severity call. GO holds.**

---

## B1 — F-6 parse-time conjunction refusal (`--execute-nc` + `--transcript-key`) — REFUSED

The refusal fires in `main()` BEFORE `_Transcript.seed()` reads the seed and before any control runs.
Every spelling of the conjunction, with a real 0600 out-of-repo seed and `GH_TOKEN` planted:

```
--execute-nc --nc-command true --transcript-out t.json --transcript-key SEED   (space)      -> exit 1
--manifest=M --execute-nc --nc-command=true --transcript-out=t --transcript-key=SEED (= form) -> exit 1
--execute-nc --execute-nc ... --transcript-key SEED --transcript-key SEED   (repeated flags)  -> exit 1
--transcript-key SEED --transcript-out t --nc-command true --execute-nc ...  (reversed order)  -> exit 1
--execute ... --transcript-k SEED   (argparse prefix abbreviation, same dest)                 -> exit 1
```
Each prints `usage: --transcript-key cannot be combined with --execute-nc …` and writes NO transcript
(`ls t.json` → No such file). Prefix abbreviation lands in the same argparse `dest`, so the guard reads
`args.execute_nc`/`args.transcript_key` regardless of the surface spelling. `--transcriptkey` (no dash)
is an unrecognized argument → argparse exit 2, and `transcript_key` stays unset — nothing signed either
way. **Env channel:** `verify-gate.sh` names NO transcript flag and there is no `ORCA_TRANSCRIPT*` var
anywhere, so the conjunction is unreachable through the gate env — the only env-borne control switch is
`ORCA_EXECUTE_NC`, which cannot supply a seed. **REFUSED.**

## B2 — nc_env escape: every allowed name + interpreter-specific env — REFUSED

Authoritative probe: a real `execute_negative_control` run whose `check.py` logs `sorted(os.environ)`,
with the parent env carrying `GH_TOKEN GITHUB_TOKEN GH_HOST ORCA_PROVENANCE ORCA_HEAD PYTHONPATH
NODE_OPTIONS PYTHONSTARTUP BASH_ENV ENV PYTHONDONTWRITEBYTECODE GIT_EXTERNAL_DIFF GIT_SSH_COMMAND
GIT_CONFIG_COUNT SSL_CERT_FILE LANG LC_ALL LC_CTYPE`. The control saw, on BOTH the control and clean runs:

```
CONTROL-ENV HOME LANG LC_ALL LC_CTYPE PATH TMPDIR __CF_USER_TEXT_ENCODING
PYTHONPATH=None NODE_OPTIONS=None PYTHONSTARTUP=None BASH_ENV=None ENV=None LC_ALL='C' HOME='/Users/ravindra'
```
- **All GH_/GITHUB_/ORCA_/GIT_/SSL_ dropped.** `nc_env()` returns exactly `{HOME,LANG,PATH,TMPDIR}`
  (+ `LC_*`) — verified directly with `GH_TOKEN`, `GIT_CONFIG_GLOBAL` planted.
- **Interpreter-honored channels dropped.** `PYTHONPATH`, `PYTHONSTARTUP`, `NODE_OPTIONS`, `BASH_ENV`,
  `ENV` are all `None` in the control. A PYTHONPATH `sitecustomize.py` payload did NOT fire in the
  control (an early SUCCEEDED reading was a false positive — it was verify.py's OWN interpreter, launched
  by me under PYTHONPATH, running sitecustomize; the control, spawned with `env=nc_env()`, never imported
  it). For a coordinator `--nc-command` interpreter in SCRIPT mode, none of the kept names is a code
  channel: python reads `PYTHONSTARTUP`/`~/.pythonrc` only interactively; non-interactive bash reads
  `BASH_ENV` (dropped), not `~/.bashrc`; node reads no `$HOME` file for a script.
- **`__CF_USER_TEXT_ENCODING`** appears but is NOT a scrub leak: macOS libSystem re-injects it below
  `subprocess` even with a fully-replaced `env` (`subprocess.run([...], env={'PATH':'/usr/bin'})` still
  shows it in the child). `nc_env()` never contains it (`'__CF_…' in nc_env()` → False). It is a
  text-encoding hint, not a code/data-steering channel. **REFUSED.**

## B3 — git_env escape: GIT_* / GIT_CONFIG_GLOBAL — REFUSED (at the env level)

`git_env()` = `nc_env()` + constant `GIT_TERMINAL_PROMPT=0`; keys `{GIT_TERMINAL_PROMPT,HOME,LANG,PATH,
TMPDIR}` (+LC_*). `GIT_CONFIG_GLOBAL=/evil`, `GIT_CONFIG_COUNT`, `GIT_EXTERNAL_DIFF`, `GIT_SSH_COMMAND`
are all dropped. **Real-CLI proof** — a full `--execute-nc` run (worktree add/status/diff/revert legs)
under `PATH=<git-wrapper>:…`, `GIT_EXTERNAL_DIFF=<stub>`, `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor
GIT_CONFIG_VALUE_0=<stub>`, `GH_TOKEN`, `ORCA_PROVENANCE`:

```
positive control (bare `git status` with the SAME channels):  FIRED (channel is live on this host)
verify.py's git legs across the whole run:                    channel NEVER fired — scrubbed
```
The stub is reachable by bare git on this host (positive control), so the empty result is the scrub, not
a host without fsmonitor. **REFUSED** for every `GIT_*`.

## B4 — HOME → `~/.gitconfig` `core.fsmonitor` (the tracked P2) — RESIDUAL, native-lane only

`git_env()` keeps `HOME` (the spec allow-list; git needs it for identity/creds). A worker-controlled HOME
with `~/.gitconfig` `[core] fsmonitor = <script>` executes the script on a git leg:

```
git_env HOME = $SP/ra3/fakehome ; verify._git(['status','--porcelain'])  -> $SP/ra3/FSMON_FIRED written
```
This is exactly the residual `fix-r6.md` names ("a worker who controls the launch env can point HOME at a
gitconfig with core.fsmonitor"). **Cannot cross to a sound lane:** on a sound lane the coordinator/CI sets
the environment OFF the worker (`verify-gate.sh` trust boundary: "the coordinator, not the worker, sets
the env"), so the worker cannot set HOME there; the malicious `~/.gitconfig` requires worker-set HOME,
i.e. the native/advisory lane whose breaker is the off-worker re-run. It produces NO sound-lane false
GREEN. Same containment class as N-4/F-6. **RESIDUAL (P2) — coordinator's severity call, not a re-loop.**

## B5 — repo-local `.git/config` `core.fsmonitor` — RESIDUAL, native-lane only (new characterization)

A stronger variant than B4: a `core.fsmonitor` set in the graded repo's OWN `.git/config` executes
INDEPENDENT of the environment — `git_env()` cannot close it, because it is repo state, not an env var:

```
git -C repo config core.fsmonitor <script>;  HOME=/tmp/clean  verify._git(['status'])  -> LOCALCFG_FIRED
```
This fires even with a scrubbed HOME. **Why it is still native-lane only:** a sound lane operates on a
fresh CLONE (CI clones the repo), and a clone does NOT carry the worker's local `core.fsmonitor`:

```
git clone repo repo_clone ;  git -C repo_clone config --get core.fsmonitor  ->  UNSET
```
`.git/config` is untracked local state; it does not survive the clone the off-worker lane runs against.
So B5, like B4, needs the native lane (verify running on the worker's live checkout). The one way it
could reach a sound lane is a coordinator pointing `--git-dir` at a worker's LIVE `.git` rather than a
trusted clone — which is a dirty-off-worker-input assumption, out of SAFE-LOCAL profile (the same class
reattack-r2 ruled out for a dirty coordinator launch env). **RESIDUAL (P2) — new env-independent
characterization of the tracked class; NOT a sound-lane false GREEN, does not re-loop.** A belt of
`-c core.fsmonitor=false -c protocol.ext.allow=never` on every git argv (fix-r6 names it) would close
B4 AND B5 in-process, since it overrides both `~/.gitconfig` and repo `.git/config`; not in the frozen
fix shape, so untouched — coordinator's call.

## B6 — sign-transcript toolchain re-hash — REFUSED

Real post-F-6 lane: `verify.py --transcript-out` (unsigned) then `$DS sign-transcript`. With a throwaway
key (the coordinator seed is out of scope — a worker cannot sign at all):

```
accept  — a REAL verify.py verdict (toolchain.files = the 5 live sibling hashes)  -> rc=0, envelope emitted
T1 all-zero toolchain.files (hand-typed)   -> rc=1, no envelope: "pins verify.py at 000000000000…, not the file beside this signer"
T2 one substituted sibling (diff_scope=aa…) -> rc=1, no envelope: "pins diff_scope.py at aaaaaaaaaaaa…, not the file beside this signer"
T3 partial set (ed25519.py deleted)         -> rc=1, no envelope: "does not name ed25519.py — a partial set binds no verifier"
T4 no toolchain.files at all                -> rc=1, no envelope: "names no toolchain.files — which verifier produced it is unknown"
```
**Symlinked sibling:** `read_bytes` follows a symlink, so a signer whose `ed25519.py` is a symlink to
another file hashes the TARGET (471fd3…→875c7e…); a verdict carrying the real hash then MISMATCHES that
doctored signer → fail-closed. A "doctored set that still matches" is only the real set (the signer
re-hashes its OWN siblings), reachable solely by an attacker who already controls the signer's directory
AND holds the seed — both trusted/out of scope — and `run_report.py` re-binds `toolchain.files` at the
committed pin (F-5) regardless. **REFUSED.**

## A5 / R1 / C-1 / C-2 / N-2 — prior load-bearing refusals, re-derived — REFUSED

`_Authority.classify` / `resolve` at the merged tip, drop dirs under `$SP` (ownership-walk-isolated):

```
A5 forged gh in $SP/ra3/ghdrop, sound (provenance=ci): custody=worker-writable, lane=provenance=ci -> review leg fails closed
   native (no provenance):                             custody=worker-writable, lane=None            -> advisory
R1 classify('/opt/homebrew/sbin') -> worker-writable ;  classify('/usr/bin') -> system ; '/bin' -> system
C-1 writable-dir link -> /bin/sh                     -> worker-writable
C-2 euid-owned 0555 file in owned 0555 dir           -> worker-writable
N-2 ./cwdlink -> /usr/bin/git                         -> worker-writable
```
The custody probe is unchanged from the round-2 target and refuses identically. **REFUSED.**

## V2 / V3 — own variants against the same boundaries

- **V2 TMPDIR redirect of the NC worktree.** The throwaway worktree holder is `tempfile.mkdtemp(prefix=
  "orca-nc-")`, which honors `TMPDIR`, and `TMPDIR` passes through `git_env()`. A worker-set TMPDIR does
  land the worktree under a worker-controlled dir — BUT `classify()` lists `tempfile.gettempdir()` as a
  root, so anything under a redirected TMPDIR classes **worker-writable** (a `gh` dropped there is refused
  on a sound lane); the redirect launders no trust. The residual reach is the boundary-E "worktree path
  mid-run replaceability" — a native-lane race (worker == verify's uid), same containment class, no
  sound-lane false GREEN (sound-lane TMPDIR is the coordinator's).
- **V3 LC_* as a channel.** `LC_*` passes (locale), so `LC_ALL=/etc/passwd` reaches git and the control —
  but as a locale STRING; git treats it as an invalid locale name and loads no file, and on macOS there is
  no `LOCPATH`-style locale-file load (and `LOCPATH` is not in the allow-list anyway). No data-to-code
  escape. **REFUSED.**

---

## Scratch state
`build_repo.sh`, `probe_ctl.py`, the scratch `runtime/scripts` copy, the mutation repo + its clone, the
fake HOME, the forged-gh drop, the git wrapper and stubs, and the throwaway seed all live under `$SP/ra3`
only. No file was planted in a system bin dir; no `~/.orca-fleet` bytes were read; the repo working tree
carries no new file except this report (uncommitted). No network call; no push.
