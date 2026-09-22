# harden-it 409 — RE-AUDIT (fresh full audit at the merged tip)

**Auditor:** task_5c4acd2e0649 (wrote none of the fixes; did not run the first audit — every file under
`docs/reports/h409/` and `docs/runs/2026-09-21-harden-409/` was read as DATA). **Audited at:** `e152304e`
(merge of #493), 2026-09-22 02:58–03:15 UTC. **Threat model:** `docs/runs/2026-09-21-harden-409/threat-model.md`
(6 boundaries, 6 axes, bar §4), re-derived from the code at this SHA. **Profile:** SAFE-LOCAL — scratch repos and
throwaway keys under `$SP`, a stub `gh` that logged argv, two read-only `gh api` GETs against this repository,
no pushes, no key bytes read anywhere (stat/`access(2)`/env-presence only). **Pack:** addy. Only repo write: this file.

## Verdict: **NOT CLEAN — 1 × P1 (custody), 0 × P0.** Three prior observations dispositioned below.

| # | Finding | Severity (bar §4) | Where |
|---|---|---|---|
| **F-6** | The executed negative control runs worker-authored test code with the verifier's **uid and full environment**; with `--transcript-key` the coordinator seed is readable by that uid and its path is in the parent's argv; `GH_TOKEN`/`GITHUB_TOKEN` pass through unscrubbed | **P1** (custody gap — "the whole design fails if the seed reaches the worker"; §4 P0 wording applies if bytes move, which this audit did not demonstrate by the model's own Never rule) | `verify.py:976-987` `_run_at` (no `env=`), `:1711` (NC run), `:2551-2559` (seed read up front, held for the whole run), `dispatch-sign.py:34` |
| O-2.2 | `sig_b64` decoded without `validate=True` in verify.py; the two other consumers validate | **CONFIRMED — reclassified P2** (consistency; the same 64 bytes must still verify under the trusted key, so no false GREEN) | `verify.py:2275` vs `run_report.py:639`, `inventory.py:304` |
| O-2.4 | `sign-transcript` checks field PRESENCE only and signs any verdict object handed to it | **CONFIRMED — P2**, with a note: it is the ONLY seed-safe signing path once F-6 is read (see §F-6) | `dispatch-sign.py:230-259` (`missing = [k … if record.get(k) is None]`, nothing else) |
| O-3.3 | `GRADING_BASES` ends in `HEAD`; a checkout with no `origin` and no `main`/`master` reads the enforcement key AT the pin — the pin chooses its judge | **CONFIRMED — P2** (unreachable on the sound lanes: CI has `origin/main`; a coordinator checkout has `origin`). One prior-report claim corrected: `bind_check.py` does **not** pass `--base` to `check_report` (`scripts/bind_check.py:204,336`) — it binds on `GRADING_BASES` too | `run_report.py:505,529-538,541-561` |

Known-closed classes (F-1..F-5, R1, C-1, C-2) re-verified dead at HEAD: §A. Six axes swept: §B. Baseline at HEAD:
`python3 scripts/validate.py` exit 0 ("All 21 missions valid"); the full `tests/` suite: see the last line of this file.

---

## F-6 — the executed control inherits the coordinator's uid, environment and seed reach (P1)

**Claim.** `--execute-nc` (the sanctioned execution of the unit's own criterion-bound command in a throwaway
worktree) runs that worker-authored code as a child of verify.py with `subprocess.run(args, cwd=wt, …)` and **no
`env=`** (`verify.py:976-987`), so it inherits every variable the verifier holds — including `GH_TOKEN` /
`GITHUB_TOKEN`, which `_Authority.gh_env()` (`:838-840`) scrubs only for the *gh* child, not for the control. When the
same invocation carries `--transcript-key <seed>` (the documented in-process signing lane, `dispatch-sign.py:34`,
verify.py `--transcript-key` help), the seed is read once in `main()` before `verify()` (`:2551-2559`) and the
run continues with a 0600 file owned by the **same uid the control runs as**, its path visible in the parent's argv.
F-4's custody check (`dispatch-sign.py:180-209`) passes it — "mode 0600, outside any unignored work tree" — because
custody is asserted against the FILE, not against who executes in the process that opened it. Nothing in verify.py,
verify-gate.sh or the docs refuses or warns on the `--execute-nc` + `--transcript-key` conjunction.

**Why it is in-scope, not the accepted class.** The threat model sanctions running the unit's tests with the
verifier's privileges (§2 Always; §4 "beyond the sanctioned … execution"). What it does not sanction is the seed
or the review authority's credential being within that code's reach: "the whole design fails if the seed reaches
the worker, so custody is in scope" (§0), S3.1, §4 P1 "custody gaps". A worker holding the coordinator's
`GH_TOKEN` can also satisfy `review_ok` (`:556-574`: APPROVED at head_sha by a login ≠ the PR author) with an
approval posted as the coordinator — the review leg's independence rests on that credential staying off the worker.

**Reproduction (SAFE-LOCAL, stat/env-presence only; `$SP/probeF.py`, built on the suite's `MutationFixture`,
run from the repo root at `e152304e`).** The unit's own `check.py` at head_sha records booleans only:

```
self.write("check.py", "import app, os, stat\n seed = <scratch seed path>\n st = os.stat(seed)\n"
  " log(dict(same_uid=st.st_uid == os.getuid(), r_ok=os.access(seed, os.R_OK), mode=oct(S_IMODE(st.st_mode)),"
  "          gh_token_in_env='GH_TOKEN' in os.environ,"
  "          transcript_key_in_parent_argv=any('--transcript-key' in a for a in `ps -o args= -p <ppid>`.split())))\n"
  " assert app.f() == 2, 'AC-1 violated'\n")
$ GH_TOKEN=dummy-not-a-real-token python3 runtime/scripts/verify.py --manifest manifest.json \
    --contract-source contract.md --contract-digest sha256:… --unit-class mutation --repo o/r --no-gh \
    --execute-nc --nc-command 'python3 check.py' --transcript-out t.json --transcript-key $SP/…/keys/seed
stderr: seed custody: $SP/…/keys/seed mode 0600, outside any unignored work tree      <- F-4 passes it
F verify.py exit 2 | NC executed: True                                                 <- (REDs unrelated: no-gh needs a corroborated lane etc.)
F what the executed control observed (one line per run of check.py — clean head, then the applied control):
     {'same_uid': True, 'r_ok': True, 'mode': '0o600', 'gh_token_in_env': True, 'transcript_key_in_parent_argv': True}
     {'same_uid': True, 'r_ok': True, 'mode': '0o600', 'gh_token_in_env': True, 'transcript_key_in_parent_argv': True}
F transcript written+signed: True
```
The verdict's exit code is not what this changes (it is fixed before `_Transcript.write`); what changes is WHERE the
seed and the token are while worker code executes. Bytes were not read — the model's Never rule — so this is graded
P1 (custody gap), not P0 (disclosure).

**Fix shape (not applied — audit only).** (1) Refuse `--execute-nc` together with `--transcript-key` at parse
time (usage exit 1): "sign after the control, in a process that never ran it — `--transcript-out` then
`dispatch-sign.py sign-transcript`, or a second verify.py invocation without `--execute-nc`". (2) Run the control
under a scrubbed environment (`_run_at(…, env=…)` with the same allow-list discipline as `gh_env`, minus the
tokens) — the token and every `ORCA_*`/`GH_*` value is not something the unit's tests need. (3) Say it in
`docs/verify-gate.md` §"Signed dispatch": the in-process key lane and the executed control are for DIFFERENT hosts.
(4) Note the interaction with O-2.4: after (1), the seed-safe path is `sign-transcript`, which signs what it is
handed — so it should at least re-hash `toolchain.files` against its own siblings and refuse a mismatch, and the
docs should say "sign only a verdict object you produced".

## Prior observations — disposition with evidence

**O-2.2 — CONFIRMED, P2.** `verify.py:2275` `sig = base64.b64decode(envelope["sig_b64"])`; `run_report.py:639` and
`inventory.py:304` pass `validate=True`. In-process at HEAD (`check_dispatch_provenance`, throwaway key, scratch repo):
```
B clean                         verify.py:2275 -> 'NOTE: dispatch record signature verified …' | validate=True -> ACCEPT
B non-alphabet '*' inserted     verify.py:2275 -> 'NOTE: dispatch record signature verified …' | validate=True -> REFUSE (Only base64 data is allowed)
B newline inserted              verify.py:2275 -> 'NOTE: dispatch record signature verified …' | validate=True -> REFUSE
B trailing garbage '!!'         verify.py:2275 -> 'NOTE: dispatch record signature verified …' | validate=True -> REFUSE
```
Same 64 bytes every time, so the trusted key still had to produce them — no false GREEN is reachable, and the bar's
P1 "fail-open on malformed input where the contract says fail-closed" does not bite: no doc states the contract;
only the round-2 report did. One-token fix; the three consumers should agree on what "malformed" means.

**O-2.4 — CONFIRMED, P2 (process assumption, undocumented).** `dispatch-sign.py:249` is the only content check
(`record.get(k) is None`). A hand-typed verdict object — `exit 0`, `fatal []`, every hash `00…00` — signs and verifies:
```
C sign-transcript over a HAND-TYPED verdict: rc=0 signature verifies=True
```
`run_report.signed_transcript` (`run_report.py:698-716`, F-5) would refuse THIS one (zero hashes ≠ files at the
pin), but a verdict copied with the real hashes binds. The control is not decorational — a worker without the seed
still has no path — but the docs (`docs/verify-gate.md:203-206`, `dispatch-sign.py:31-34`) never say the maintainer
must sign only a verdict they produced. See F-6 (4) for why this matters more now.

**O-3.3 — CONFIRMED, P2.** Scratch repo, no `origin`, branch `trunk`, self-pinned `.orca/dispatch-pubkey`:
```
D grading_base -> 995aa9f7…  key_rev -> (995aa9f7…, 'the pin, an ancestor of the grading base 995aa9f7')
D enforcement_key: pub == self-pinned? True
```
Reachability: `validate.yml`/`bind-check.yml` check out with `fetch-depth: 0`, so `origin/main` resolves before
`HEAD`; a coordinator checkout has `origin`. Correction to `audit-w2.md` §S3.3: `bind_check.py` calls
`run_report.check_report(path_text, mission, tier, root=root)` with **no `base`** (`scripts/bind_check.py:204,336`) —
its `--base` feeds only `changed_entries`. Hardening: drop `HEAD` from `GRADING_BASES` when a pubkey exists at any
reachable rev, or emit `why` on the bound line.

## A — known-closed classes, re-verified dead at `e152304e`

| Class | Evidence at HEAD |
|---|---|
| F-1 / C5 (gh re-resolved after the control) | `_Authority.resolve()` in `main()` (`verify.py:2572`) before `verify()`; `ensure()` pins once; `fetch_reviews` uses `_Authority.api` only (`:624-634`); `ABSENT` is terminal (`:668-670`). Probe A: the stub gh was consulted ONLY through the pinned path; PATH set to the scratch tools dir classes it worker-writable → advisory NOTE on the native lane |
| F-2 / C1 (repo from origin) | `review_leg` (`:872-896`): `repo_source == "inferred"` is fatal on a lane claiming soundness, NOTE otherwise; `--provenance` is in the signed args tuple |
| F-3 / C2 (`./` spelling) | `Path(path).as_posix()` on both git lookups (`:273`, `:319`) — the `_resolve`-bounded spelling is the one git sees |
| F-4 / C3 (seed custody at use) | one `_seed` for all four signers (`dispatch-sign.py:180-209`; `verify.py:2181-2191` loads it). Probe F shows the check running and passing on a 0600 out-of-repo seed — and shows its limit (F-6) |
| F-5 / C4 (toolchain pin unconsumed) | `TOOLCHAIN_FILES` re-hashed against `runtime/scripts/<name>` at the pin (`run_report.py:698-716`); probe C's all-zero set would be refused there |
| R1 (system-bin name short-circuit) | `classify()` is a probe over every node (`verify.py:800-836`), no name list |
| C-1 / C-2 (symlink hop, owner-0555) | `_nodes` walks hops (`:756-778`); `_worker_controls` owner/group/other/ACL (`:780-798`); symlink node itself never classes on its bits (#493) |
| checkvalid hardening | `ed25519.py:142-159` unchanged: length, non-canonical S, cofactor check on A |

## B — six-axis sweep at HEAD (what the prior rounds did not cover)

**Axis 1 spoofing / false GREEN.** S1.1 re-probed at HEAD with ten `pr.number` shapes (probe A): every shape is
interpolated raw into `repos/<slug>/pulls/<number>/reviews` (`verify.py:631`, `:640`) — `"7 --hostname evil.example"`
stays ONE argv element (no option injection), `"7/reviews?per_page=1&x"` crashes `fetch_pr_author` into the collect()
wrapper → exit 2 (fails closed), and a `..`-shaped number is NOT normalised by GitHub (read-only GET
`repos/ravidsrk/orca-fleet/pulls/493/../493/reviews` → 404 Not Found). No endpoint other than a PR's own `reviews`
returns an array carrying `state: APPROVED` + `commit_id` + `user.login`, and a different PR number in the same repo
needs a review at `head_sha` by a non-author on THAT PR — a genuine approval of the same code. **Refuted; O-1
stands as hygiene** (validate `^[1-9][0-9]*$`). S1.4: `check_review` (`:898-971`) — dark-eligible and no-gh both
require `corroborated` AND `nc_executed`; `nc_executed` is the executor's own return, and the executor is admitted
only on `execute_nc and not fatal` (`:2440`). No text-only path to GREEN. S1.3: `_fresh_command_records` unchanged.

**Axis 2 canonical form / replay.** Probe E: `dispatch-sign.canonical_record` == `verify._canonical_dispatch` and
`canonical_transcript` == `_canonical_transcript` on int-vs-str ids, `nc_paths` as a bare string, mixed-type lists,
non-ASCII, nested dicts. `sort_keys` + `separators` + `ensure_ascii` identical; `record.get(k) is not None` filter
identical (`dispatch-sign.py:86`, `verify.py:2115`, `:2145`). Envelope `record` is re-canonicalised from the parsed
dict, so no byte-level trick survives the parse. Replay: transcript binds `manifest_sha256`, `exit`, the full
`SIGNED_ARGS` tuple and the run-dir prefix (`run_report.py:618-697`); inventory binds the entry SET digest. **Clean.**
Noted (design, not graded): neither envelope signs the tier or mission, and `check_report` reads the report BODY
from the working tree while every artifact is read at `inventory_at` — the report's prose and its tier label are
unbound by construction (the tier's meaning lives in review, not in the binder).

**Axis 3 key custody.** F-6 above. S3.2/S3.4 unchanged from w2 (in-session pin honoured, nothing records it sound;
signature outside a block refused, `inventory.py:256-285`). No `.orca/dispatch-pubkey` is committed at `e152304e`
(`ls .orca` → absent): the whole signed lane is **dormant** in this repository, as `docs/verify-gate.md:198` says.

**Axis 4 hook / env.** `verify-gate.sh:98-113`: every env value is its own argv element; a leading `-` value is
swallowed by argparse as an option → usage exit → BLOCK (`:136-143`). `--transcript-out/--transcript-key` are never
forwarded from env — a worker cannot make the hook sign. `ORCA_PROVENANCE=ci` self-assertion makes the lane
STRICTER (`_Authority.lane` → fatal on worker-writable gh / inferred repo), never looser. **Clean.**

**Axis 5 path / symlink / scratch.** `_resolve` (`verify.py:227-257`) bounds after `resolve()`; `read_source`'s
`path@ref` branch refuses absolute and option-shaped, and git itself refuses `..` outside the tree. A tracked in-repo
symlink named as an artifact yields its LINK TEXT via `git show` (not the target's bytes) — useless to a forger.
`_root_arg` (`:2451-2468`) refuses roots outside a work tree. **Clean.**

**Axis 6 supply chain of the toolchain's inputs.** gh/git/gitleaks pinned absolute and custody-classed at startup
(A). Remaining lazy loads AFTER the control: `_load_ed25519()` inside `_Transcript.write` (`:2210`, re-executes
`ed25519.py` from disk) and `_load_diff_scope()` on demand — the same ordering class F-1 closed for gh. The in-session
verdict is fixed before `write`, and run_report's F-5 hash binding catches a substituted sibling at the pin, so this
is an **observation** (load every sibling once beside `_Authority.resolve`), not P0/P1. `gh_env` keeps `HOME`, so gh's
own `config.yml` (`http_unix_socket`, hosts) is coordinator state on the sound lanes — fine there; and moot on the
native lane. #284 fence coverage: unchanged from w3 (P2).

## Not graded / accepted (bar §4 "Not P0/P1 here")
`AttributeError` exits on odd `pr.number` (fails closed); whole-file artifact reads (self-DoS); the native hook
advisory by design; `ed25519.py` timing; verdict-check residual poison cases.

## Baseline at HEAD
`python3 scripts/validate.py` → exit 0, "All 21 missions valid; three-layer separation holds; evals valid."
`python3 -m unittest discover -s tests` → **Ran 2001 tests, OK** (365 s), exit 0. Probe scripts: `$SP/probes.py` (A–E), `$SP/probeF.py` (F-6) — scratchpad only, not committed.
