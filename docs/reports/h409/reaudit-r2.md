# harden-it 409 — FINAL RE-AUDIT (round 2, fresh full audit at the merged tip)

**Auditor:** task_161f1dfaa60b (wrote none of the fixes; did none of the prior audits — every file under
`docs/reports/h409/` and `docs/runs/2026-09-21-harden-409/` was read as DATA, then the code at HEAD was
read in full). **Audited at:** `7e0c6f85` (merge of #494, round 6), 2026-09-22. **Threat model:**
`docs/runs/2026-09-21-harden-409/threat-model.md`, bar re-derived from §4 against the code at this SHA.
**Profile:** SAFE-LOCAL — hermetic scratch repos under `$SP` built on the suite's own `MutationFixture`,
throwaway keys, marker-only stubs, no key bytes read, no pushes, no live `gh` calls at all this round
(the review seam was the fixture's mock). **Pack:** addy (security-and-hardening lens). Only repo write:
this file. Timebox 60 min — every claim below is one I re-derived; nothing is graded on a prior report's word.

## Verdict: **CLEAN — zero unrefuted P0/P1 at `7e0c6f85`.**

Three tracked residuals dispositioned with evidence (§C): (i) HOME passthrough **CONFIRMED P2, native lane
only — the lane boundary holds**; (ii) post-control lazy loads **GRADED: closed on every `--execute-nc`
path at HEAD (measured: zero post-control sibling loads), incidental on ordering — P3 hygiene**; (iii) the
six-name `nc_env` floor **CONFIRMED hygiene (false RED only, never false GREEN)**. Fresh six-axis hunt
(§B): nothing reaches the bar; two P3 hygiene observations and one documented design limit re-stated so
nobody reads the executed control as a truth oracle.

---

## A — prior rounds' closures, re-verified dead at `7e0c6f85` (file:line at HEAD)

| Closed class | Evidence at HEAD |
|---|---|
| **F-1 / C5** gh re-resolved after the control | `_Authority.resolve()` runs in `main()` (`verify.py:2615`) before `verify()` (`:2617`); `ensure()` pins once, `custody == "absent"` is terminal (`:760-765`); `fetch_reviews` only reaches gh through `_Authority.api` (`:625-636`, `:868-877`) |
| **F-2 / C1** review repo inferred from `origin` | `review_leg` (`:897-921`): `repo_source == "inferred"` is fatal under `cls.lane`, NOTE otherwise; `provenance` sits in the signed args tuple (`:2167-2169`) |
| **F-3 / C2** `./`-spelled evidence | both git lookups hand git `Path(path).as_posix()` — `read_source` `:273`, `_read_artifact` `:319-322` |
| **F-4 / C3** seed custody at use | one `_seed` (`dispatch-sign.py:213-247`: mode `& 0o077` refused, unignored-worktree refused, class named on stderr) loaded by `verify.py _Transcript.seed` (`:2214-2225`) |
| **F-5 / C4** toolchain pin unconsumed | `run_report.signed_transcript` re-hashes all five `TOOLCHAIN_FILES` against the blob at the pin (`run_report.py:697-715`); `sign-transcript` re-hashes them against its own siblings (`dispatch-sign.py:92-117`, `:287-289`) |
| **F-6** control inherits uid/env/seed reach | parse-time refusal of `--transcript-key` + `--execute-nc` at `verify.py:2590-2598`, BEFORE `_Transcript.seed()` (`:2599`) and before `_Authority.resolve()`; the control runs `_run_at(wt, argv, env=_Authority.nc_env())` (`:1742`) over `AMBIENT_KEEP` (`:687-688`, `:854-859`). Re-derived: probe `$SP/probe_ii_b.py` → `exit 1 | usage: --transcript-key cannot be combined with --execute-nc …`, and no sibling module was loaded after the refusal |
| **R1** system-bin dir trusted by name | `classify()` is a probe over every node (`:811-838`); no name list anywhere in the file |
| **R2** git/gitleaks unpinned | `pin_git`/`pin_gitleaks` (`:709-727`), `git_bin()` pins on first use (`:729-735`); `_run`/`_run_bytes`/`_run_at` refuse `args[0] is None` rather than look a name up again (`:116-117`, `:129-130`, `:1006-1007`) |
| **R3 / N-4** gh, git, gitleaks run with ambient env | `gh_env()` (`:849-852`), `git_env()` = `nc_env()` + `GIT_TERMINAL_PROMPT=0` (`:861-866`), applied on every git leg (`_git :149-152`, `_git_bytes :155-158`, `_evidence_toplevel :199`, `_root_arg :2495`, every `_run_at` git leg in `_apply_control :1611-1667`, the worktree add/remove `:1730`, `:1748`, gitleaks `:1979-1981`) |
| **C-1 / C-2** symlink hop, owner-0555 | `_nodes` walks every hop (`:767-789`); `_worker_controls` probes owner/group/other/ACL and never classes a link node on its own bits (`:791-809`) |
| **N-4** exec channels through git legs | as R3 above — no `_run`/`_run_bytes`/`_run_at` call in the file passes `env=None` for git |
| **O-2.2** lenient `b64decode` | `validate=True` at all three consumers: `verify.py:2308`, `run_report.py:639`, `inventory.py:304` |
| **O-2.4** sign-transcript signs any shape | `toolchain_mismatch` refuses a verdict whose `toolchain.files` is absent, partial, or hashes other bytes than the signer's siblings (`dispatch-sign.py:92-117`), called before the envelope is built (`:287-289`) |
| **/bin-symlink node hole** (#493) | `_worker_controls` returns False for a link node — re-pointing it needs a write on its directory, which is the node before it (`:797-802`) |
| checkvalid hardening | `ed25519.py:142-159` unchanged: length gate, `S >= _L` refused (`:152`), cofactor check on `A` (`:155`) |

## B — fresh six-axis hunt at HEAD (what every prior round could still have missed)

**Axis 1 — spoofing / false GREEN.** Every worker-supplied field that reaches git is either HEX40-gated
(`check_real_commits :498-519`, incl. the option-shaped refusal at `:511-514`), passed after `--` with
`--literal-pathspecs` (`:1611-1612`), or bound to the base..head diff before use (`_bind_paths_to_change`,
`_bind_hunks_to_change`). A non-string `head_sha` raises inside a check and lands in the `collect()` wrapper
as a fatal (`:2441-2447`) — fail-closed, never a usage exit. The waiver lanes still require `corroborated AND
nc_executed` (`:934-967`), and `nc_executed` is only ever the executor's own return (`:1877-1878`), admitted
only when `execute_nc and not fatal` (`:2473`). **No text-only path to GREEN.**

**Axis 2 — canonical form / replay.** `_canonical_dispatch` (`verify.py:2146-2151`) and
`dispatch-sign.canonical_subset/canonical_record` (`:113-129`) are the same filter, the same `nc_paths`
set-sort, the same `json.dumps` options; `_Transcript.canonical` (`:2172-2175`) equals `canonical_transcript`
(`:132-135`). Replay of a signed transcript into another run is stopped at `run_report.py:623-625` (transcript
must sit under the run's own directory; a `..` spelling is refused by git itself — verified: `git show
HEAD:docs/reports/../reports/h409/verify.md` → `fatal: … not in 'HEAD'`), `:652-662` (manifest path AND bytes
at the pin), `:664-667` (exit vs header), `:670-688` (full `SIGNED_ARGS` tuple must match an invocation the
body shows), `:697-715` (toolchain hashes at the pin). **Clean.**

**Axis 3 — key custody / at-rev resolution.** F-4 and F-6 above. `enforcement_key` (`run_report.py:541-561`)
reads the key at the pin only when the pin is on the grading base's ancestry; when the base carries no key the
pin's own key is honoured (`:551-552`) — that can only ADD a signature requirement to a lane that would
otherwise be unsigned, never remove one (O-3.3 class, P2, unchanged). `.orca/dispatch-pubkey` is still not
committed at `7e0c6f85` — the signed lane is dormant here, as `docs/verify-gate.md:198` says.

**Axis 4 — hook / env.** `verify-gate.sh:98-113`: each env value is its own argv element; a leading `-` is
swallowed by argparse as an option → usage exit 1 → BLOCK (`:136-143`). `--transcript-out`/`--transcript-key`
are never forwarded from env (`:98-113` has no such line) — the hook cannot be made to sign. `ORCA_PROVENANCE`
self-assertion only makes the lane STRICTER (`_Authority.resolve :737-748` → `lane` set → the worker-writable
and inferred-repo legs turn fatal). **Clean.**

**Axis 5 — path / symlink / scratch.** `_resolve` bounds after `resolve()` and refuses absolute and `..`
(`:227-257`); `_read_artifact` refuses `@` (`:311-312`); `read_source` refuses option-shaped and absolute
`path@ref` (`:266-271`); `_root_arg` refuses a root outside a work tree (`:2484-2502`); the NC worktrees are
`mkdtemp` holders removed with `worktree remove --force` under `git_env()` (`:1726-1749`). **Clean.**

**Axis 6 — supply chain of the toolchain's inputs.** `_verify_sig` is loaded at module import
(`verify.py:1457-1466`), so it is never loaded after worker code ran. `_load_ed25519` and `_load_diff_scope`
re-execute from disk on every call (they never register in `sys.modules`) — graded in §C(ii) with a runtime
measurement. `_Transcript.build` re-reads the five siblings from disk after the control (`:2189-2193`) — that
is the F-5 binding's INPUT: a sibling rewritten by then shows up as a hash that does not match the pin
(`run_report.py:697-715`) or the offline signer's siblings (`dispatch-sign.py:92-117`), so it fails closed.
The #284 fence coverage (`gh api`/`gh pr view`/`curl` forms) is unchanged from w3 — P2, tracked.

**Hygiene found this round (P3, not graded):**
- `dispatch-sign.py:165-178` (`_in_unignored_worktree`) and `run_report.py` (`grading_base :512`, `is_ancestor
  :523`, `blob_at :382`, `tree_of :392`) call a bare `git` from PATH with the ambient env — the R2/N-4
  discipline verify.py now has. Both run on the coordinator/CI host, never in the worker's env, so nothing
  the worker sets reaches them; still, one `git` resolution rule across the toolchain is cheaper than
  arguing lane by lane.
- `_read_artifact`'s tracked-at-head shortcut (`:319-324`) accepts a tracked DIRECTORY (`cat-file -e` is 0
  on a tree; `git show` then prints the listing). Corroboration text only — every artifact is a claim the
  executed control or the review must back — so no GREEN moves; worth one `^{blob}` on the probe.

**Documented design limit, re-stated (outside the bar):** the executed control proves the coordinator-named
command binds to the change; it cannot judge whether the unit's OWN test is a meaningful oracle (a test that
asserts source text rather than behaviour goes RED under revert and GREEN clean). `runtime/evidence-manifest.md:127`
assigns exactly that — the criterion↔test binding audit — to a coordinator/human sample, "not verify.py",
and on the waiver lanes the coordinator's dark-eligible / no-gh decision is the explicit acceptance. §4 sanctions
"execution of the unit's own tests"; nothing to grade, noted so nobody reads `nc_executed` as truth.

## C — the three tracked residuals

### (i) HOME passthrough → `~/.gitconfig core.fsmonitor` on the native lane — **CONFIRMED P2; the lane boundary holds**

**Measured at HEAD** (`$SP/probe_i.py`: a scratch HOME whose `.gitconfig` names a marker-only fsmonitor stub;
the fixture repo is built under the real HOME first, then HOME is swapped for the verifier's legs only):
```
(a) HOME gitconfig fsmonitor fires through verify._git under git_env(): True
(b) with GIT_CONFIG_GLOBAL=/dev/null + NOSYSTEM=1: False
(b) full green executed-revert run under the hardened git_env: exit 0 | fired during run: False
```
So the channel review-r6 named is live (`git_env()` keeps `HOME`, `verify.py:687`, `:861-866`) — and the r6
closure (two constants added to `git_env()`) closes it with the green executed-revert run intact: no leg
needs an identity or a user config (they are `worktree add/remove`, `checkout -- <paths>`, `revert --no-commit`,
`apply --index`, `status`, `diff`, `rev-list`, `merge-base`, `cat-file`, `show`, `grep`). The same
constants also close `$(prefix)/etc/gitconfig`, which is user-writable under Homebrew (the R1 class of dir).

**Crossing it to a sound lane — attempted, refused by the model's own premise.** The sound lanes are defined
as "off the worker's box, where the orchestrator (not the worker) owns any injected env"
(`docs/verify-gate.md:282-286`, `verify-gate.sh:12-18`). There, `HOME` is the coordinator's and its gitconfig is
coordinator state — the same standing `gh_env()` gives gh's `config.yml`. The only way a worker writes THAT
`~/.gitconfig` is to share the coordinator's box AND uid, and on such a host the 0600 seed (`_seed`, F-4) and
the coordinator's checkout of `verify.py` itself are already the worker's — the premise, not this channel, is
what fell. I also looked for a HOME-independent channel that the worker's COMMIT (which it does control on
every lane) could open through the git legs: `.gitattributes` filter/smudge drivers need `filter.*` CONFIG,
hooks come from `$GIT_COMMON_DIR/hooks` or `core.hooksPath` (both config, the coordinator's clone),
`worktree add` does not recurse submodules, and `.gitmodules`/`.mailmap` are not read by any leg here.
None exists. **Holds at P2. Recommend the two constants anyway** — cheaper than the argument.

### (ii) lazy `ed25519.py` / `diff_scope.py` loads after the control — **GRADED: closed at HEAD on every `--execute-nc` path (measured), P3 hygiene for the ordering it rests on**

**Question asked:** can the executed control swap a `.py` the verifier imports LATER? Import order and
`sys.modules` state at control time, measured in-process (`$SP/probe_ii.py`, `$SP/probe_ii_b.py`: every
`importlib.util.spec_from_file_location` call logged with a before/after-control marker; the control's own
`_run_at` flips the marker). Full green executed-revert run with `--transcript-out`:
```
exit 0
   ('pre-control', 'diff_scope', 'diff_scope.py')   × 6      ← _is_test_path during admission + _apply_control
   ('CONTROL-EXECUTED', 'python3', 'sys.modules has ed25519=False diff_scope=False')
   ('CONTROL-EXECUTED', 'python3', 'sys.modules has ed25519=False diff_scope=False')
post-control loads: []
```
With a signed dispatch record + pubkey on the same run: `('pre-control', 'ed25519')` × 2, `('pre-control',
'diff_scope')` × 2, `post-control loads: []` (that run exits 2 on this host — an enforcement lane fails closed
on the Homebrew-owned git/gh, as it should).

**Why it holds, from the code:** the two loaders never cache — each call re-executes the file
(`verify.py:2139-2143`, `:1082-1090`; nothing in `sys.modules`), so the question is purely WHEN they are called.
`check_dispatch_provenance` (the only ed25519 consumer besides `write`) is in the admission `collect()`
(`:2452-2469`), which runs before `check_negative_control` (`:2473`); `_is_test_path` is consulted by the
admission binds and by `_apply_control` — phase "control", before the control's argv runs (`:1733-1742`);
after the control only `check_review` and `check_symbol_on_base` run (`:2477-2480`), neither loads a sibling;
`_Transcript.write` loads ed25519 only with a seed (`:2243`), and F-6 makes a seed and `--execute-nc`
mutually exclusive at parse (`:2590-2598`). **Graded P3:** the guarantee is real but incidental — it rests on
`collect()` ordering and on the F-6 refusal, not on a load-once-at-startup discipline. Load all three siblings
beside `_Authority.resolve()` and hold the module objects; then no reordering can reopen it.

### (iii) the six-name `nc_env` floor false-REDing exotic toolchains — **CONFIRMED hygiene**

`nc_env()` (`verify.py:854-859`) is a projection of the launch env onto `PATH, HOME, TMPDIR, TMP, TEMP, LANG,
LC_*`. A proof command that needs `JAVA_HOME`/`ANDROID_HOME`/`GOPATH`/`CARGO_HOME`/`VIRTUAL_ENV`/`SSL_CERT_FILE`
fails identically in BOTH phases, and the clean phase's non-zero exit is a fatal (`:1764-1767`: "exits … at
CLEAN head_sha too"). False RED, never false GREEN — the right default. One sentence in `docs/verify-gate.md`
when it first bites a real run; not a finding.

## D — not graded / accepted (bar §4 "Not P0/P1 here")
The native hook advisory by design; `ed25519.py` timing; verdict-check's two residual poison cases; whole-file
artifact reads (self-DoS); `AttributeError` exits on odd `pr.number` (fail closed); #284 fence coverage (P2).

## Baseline at `7e0c6f85` (this host: macOS Darwin 25.6.0, Homebrew git, Python 3.13, euid ≠ 0)
`python3 scripts/validate.py` → exit 0, "All 21 missions valid; three-layer separation holds; evals valid."
`python3 -m unittest discover -s tests` → **Ran 2018 tests in 386 s, OK**, exit 0.
Probe scripts: `$SP/probe_i.py`, `$SP/probe_ii.py`, `$SP/probe_ii_b.py` — scratchpad only, not committed.
`git status --short` after the probes: clean apart from this report.
