# harden-it 409 — independent verification of the six P1 candidates

**Verifier:** task_606a916faf0d (did not write audit-w1/w2/w3; those files are DATA).
**Verified at:** `a2033f74a563e2cf606de25853dde6b1ff8fa73a` (this worktree's HEAD), 2026-09-21 11:37–11:55 local.
**Method:** every candidate re-derived from the code and from my OWN scratch fixtures (`$SP/c1…c5`,
throwaway keys, a stub `gh` that only ever ran against scratch endpoints; no network beyond one
accidental read-only `gh api` GET on a non-existent `o/r`). Bar: `docs/runs/2026-09-21-harden-409/threat-model.md` §4.
Profile: SAFE-LOCAL. Pack: addy. Nothing outside this file was written in the repo.

| # | Candidate | Verdict | Severity (bar §4) |
|---|---|---|---|
| C1 | Review repository worker-selectable when `--repo` omitted | **CONFIRMED** (mechanism reproduced; false-GREEN completion argued from code, needs a live PR) | P1, P0 on any sound lane that omits `ORCA_REPO` |
| C2 | `./`-spelled evidence binds a path absent at the bounded root | **CONFIRMED** (exit 0 in both divergent layouts, exit 2 in control) | P1 (coordinator-side precondition; not worker-triggerable alone) |
| C3 | All four signers sign with a 0644 / tracked / unignored seed, silently | **CONFIRMED** (4/4 signers, 0 bytes of warning) | P1 by the threat model's own S3.1 criterion |
| C4 | `toolchain.verify_sha256` has zero consumers, covers `verify.py` only | **CONFIRMED on the facts; over-claim on "presented as a guarantee"** | P1 by S6.1 as pre-declared; nothing in the repo calls it a guarantee |
| C5 | `gh` is a bare PATH lookup; executed NC runs worker code with the verifier's privileges | **CONFIRMED and SHARPENED** — same-run false GREEN, no pre-planted stub | **P0 candidate** (see §C5) — audit graded P1 |
| C6 | #284 fence test misses other fetch forms; raw text reaches a TASK unfenced | **PARTIALLY CONFIRMED / P1 REFUTED** — coverage gap is real, "reaches a TASK unfenced" is not shown | P2 hardening |

`$SP` = this session's scratchpad. `$V` = `runtime/scripts/verify.py` at the SHA above. Fixture: a two-commit
scratch repo (`app.py` 1→2, `check.py` asserting `f()==2`, a frozen `contract.md`, a tracked NC artifact,
a full mutation manifest with `pr.number: 7`), built by my own `mkfix.py`, not the tests' mocks.

---

## C1 — review repository inferred from a worker-writable `origin` — CONFIRMED (P1)

Code: `verify.py:2277` `args.repo or infer_repo()`; `infer_repo()` (`:153-159`) = `git remote get-url origin`
regex-parsed. `_RECORD_FIELDS` (`dispatch-sign.py:68-69`) signs `manifest_id, contract_digest, unit_class,
lighting, nc_paths, nc_command, nc_artifact_sha256` — **no repo**, so nothing signed binds which repository's
reviews are consulted. `verify-gate.sh:55,98` forwards `--repo` only when `ORCA_REPO` is set; `:22` and
`docs/verify-gate.md:86` call it "optional; inferred from origin". Only the reference CI YAML
(`docs/verify-gate.md:141`) pins `--repo "$GITHUB_REPOSITORY"`.

Reproduction (stub `gh` logs argv and answers one APPROVED at `$STUB_HEAD` by a non-author):

```
=== baseline: --repo real/project explicit, origin=real/project
verify: OK — all required checks passed            exit=0
STUB-GH ARGV: api --paginate repos/real/project/pulls/7/reviews
=== C1 step 2: worker rewrites origin, --repo omitted
$ git remote set-url origin https://github.com/evil/mirror.git
verify: OK — all required checks passed            exit=0
STUB-GH ARGV: api --paginate repos/evil/mirror/pulls/7/reviews
STUB-GH ARGV: api repos/evil/mirror/pulls/7
=== C1 step 3: same origin, --repo real/project pinned by the coordinator
STUB-GH ARGV: api --paginate repos/real/project/pulls/7/reviews   exit=0
```

Addendum the audit did not have: `origin` lives in the SHARED `.git/config`, so a worker in a worktree
rewrites the coordinator checkout's origin too:

```
$ git worktree add --detach $SP/c1-worker HEAD
$ git -C $SP/c1-worker remote set-url origin https://github.com/evil/mirror.git
coordinator checkout sees: https://github.com/evil/mirror.git
```

Does a worker-controlled origin yield a PASSING review leg? With the stub, yes (exit 0 above). With real
`gh`: `review_ok` (`verify.py:544-561`) needs `state == APPROVED`, `commit_id == head_sha`, reviewer login
≠ that PR's author — all satisfiable in a repo the worker controls (push `head_sha`, open PR #N, second
account approves). Not exercised: creating a live PR is ask-first. **Over-claim check:** none — the audit
stated exactly this split (mechanism reproduced, completion argued). Severity as the audit graded: P1;
P0 only if a lane documented as sound omits `ORCA_REPO` — `docs/verify-gate.md:175` calls MCP/SDK sound
because "the coordinator sets the env" without requiring `ORCA_REPO` in it, so the P0 branch is live
unless the coordinator's dispatcher always sets it (not verifiable from this repo).

## C2 — `./`-spelled evidence binds a path absent at the bounded root — CONFIRMED (P1)

Code: `_resolve` (`verify.py:220-245`) bounds `<evidence toplevel>/./reports/u/nc.txt` → `<root>/reports/u/nc.txt`;
`_read_artifact` (`:307-311`) hands git the MANIFEST STRING `head:./reports/u/nc.txt`, and git resolves `./`
against ITS cwd (`_git`, `:141-150`: `-C _ROOTS["git"]` or the process cwd). Fixture: NC bytes committed at
`docs/reports/u/nc.txt`; manifest names `./reports/u/nc.txt`; nothing at `<root>/reports/`.

```
--- what exists at the toplevel:            "reports": No such file or directory
$ git cat-file -e $H:./reports/u/nc.txt                     from toplevel rc=128 (does not exist)
$ git -C docs cat-file -e $H:./reports/u/nc.txt             from docs/    rc=0
$ git -C docs cat-file -e $H:reports/u/nc.txt  (no ./)      rc=128
(i)   cwd=root, --git-dir root/docs      verify: OK — all required checks passed   exit=0
(ii)  cwd=root/docs, no --git-dir        verify: OK — all required checks passed   exit=0
(iii) control: cwd=root, no --git-dir    FAIL: negative_control.artifact unreadable (./reports/u/nc.txt):
                                         [Errno 2] No such file … /c2/reports/u/nc.txt          exit=2
```

Confirmed exactly as claimed. Kept caveats (the audit stated them too, so no over-claim): the bytes ARE
commit-pinned in the same repo (no out-of-repo read; under split roots the shortcut is off); the
precondition — verifier cwd or `--git-dir` below the toplevel — is coordinator-side, `_root_arg`
(`:2166-2183`) accepting any dir inside a work tree. The harm is the bound: an auditor re-deriving from the
clone root finds no such path, and the transcript's `manifest` bytes carry the `./` spelling. P1 under
"binding a ledger to content that never existed" (at that path).

## C3 — four signers accept a world-readable, tracked, unignored seed with no warning — CONFIRMED (P1)

Code: use-time reads are bare `read_text()` — `dispatch-sign.py:_seed` (`:179-187`, used by `sign` and
`sign-transcript`), `verify.py:_Transcript.seed` (`:1899-1908`), `inventory.py:_read_seed` (`:492-496` →
`_seed`). The creation-time guard `_in_unignored_worktree` (`dispatch-sign.py:103-149`) is never called at
use. Throwaway key generated OUT of any repo, then opened and committed in a scratch repo:

```
$ dispatch-sign.py gen-key --out $SP/c3/keys/throwaway     -rw------- keys/throwaway
$ chmod 644 keys/throwaway; cp keys/throwaway repo/committed-seed; git add; git commit
committed-seed                                     (git ls-files)
check-ignore rc=1 (1 = NOT ignored)                -rw-r--r--
=== contrast: gen-key REFUSES the same in-repo path
dispatch-sign: REFUSING to write a private seed at …/c3/repo/newseed
=== (1) dispatch-sign sign --key ./committed-seed …            rc=0  stderr: 0 bytes
=== (2) dispatch-sign sign-transcript --key ./committed-seed … rc=0  stderr: []   sig_b64 present: True
=== (3) verify.py … --transcript-out t-signed.json --transcript-key ./committed-seed
    rc=0  stderr mentioning key|seed|custody|readable|ignored: []   envelope keys: ['record','sig_b64']
=== (4) inventory.py sign --key ./committed-seed r.md
    inventory: signed 1 entry (digest 60f0ea14abe4…) in r.md        rc=0  stderr: []
    inventory.py check --pubkey pub r.md → signature verified … rc=0
```

4/4 as claimed, no over-claim. Severity: the threat model pre-declared S3.1 "real if the tool signs
without warning → P1 custody gap"; the bar's P1 clause "custody gaps that erase the audit trail without
leaking the key" fits — the tool does not cause the leak, it cannot tell a leaked seed from a custodial
one at the last point it sees it. Cheap fix already in the tree: call `_in_unignored_worktree` + a
`st_mode & 0o077` check from `_seed`.

## C4 — `toolchain.verify_sha256`: zero consumers, covers one of four loaded files — CONFIRMED on facts, over-claimed on framing (P1 as pre-declared)

```
$ rg -n "verify_sha256" --glob '!docs/reports/**' --glob '!docs/runs/**' .
./tests/test_verify.py:2313   (asserts the field equals sha256(verify.py) — a producer test)
./tests/test_verify.py:2379   (fixture literal)
./runtime/scripts/verify.py:1893   "verify_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
$ rg -n '"toolchain"\]|\.get\("toolchain"' runtime/ scripts/ tests/ .github/ hooks/      → (no output)
```

`run_report.signed_transcript` binds `manifest`, `manifest_sha256`, `exit`, `args`, `unit_class`
(`run_report.py:646-685`) — never `toolchain`. Siblings loaded by path with no hash: `diff_scope.py`
(`verify.py:789-794`), `_verify_sig.py` (`:1166-1169`), `ed25519.py` (`:1837-1838`). PoC — a copied script
dir with `_verify_sig._failure_signature` overridden to always return `(True, None)`, both signed with the
throwaway key:

```
pristine  toolchain.verify_sha256=af5a9da6084765d0…  sha256(_verify_sig.py)=acc3d5cfb0f6fedf
tampered  toolchain.verify_sha256=af5a9da6084765d0…  sha256(_verify_sig.py)=8af4f05765560947
IDENTICAL toolchain block despite substituted _verify_sig.py: True      (both rc=0, both signed)
```

**Over-claim kept:** the audit's "Claim under test: the transcript 'pins' the verifier … presented as a
guarantee". I found no such presentation: the field is listed once among transcript contents
(`--transcript-out` help, `verify.py:2242-2247`: "…exit, toolchain, UTC timestamp"), the docstring
(`:1874`) says "the toolchain", the landing commit `6be872a7` says "the toolchain and a UTC timestamp". It
is recorded metadata at the same tier as `python`/`git` versions; no doc promises a check. The bar's P1
wording needs BOTH halves ("recorded-but-never-checked pin **presented as a guarantee**"); the threat
model's S6.1 pre-declaration needs only the first ("real if NO consumer checks that hash → P1"). Graded P1
per S6.1; the coordinator may reasonably hold it at P2 as "a pin that would need a consumer to mean
anything". The substitution precondition (write to the verifier host's script dir) is outside the
worker adversary on its own — but C5 hands the worker exactly that write, which is what makes this matter.

## C5 — bare `gh` on PATH + executed NC runs worker code as the verifier — CONFIRMED, SHARPENED to a same-run false GREEN (P0 candidate)

Code: `shutil.which("gh")` then bare `["gh", "api", …]` (`verify.py:613-626`); `_run_at` (`:711-720`) is
`subprocess.run(args, cwd=…)` with no `env=` — `rg -n "env=|os.environ" verify.py` → 0 hits. Ordering
inside one run (`verify.py:2153-2160`): `check_negative_control` executes BEFORE `check_review`.

Step 1 — the audit's claim, reproduced: worker-written `check.py` at head records the env it ran in:

```
=== --execute-nc with a stub gh on PATH
NOTE: negative control EXECUTED — … exited 1 on an assertion failure (RED, as required)
verify: OK — all required checks passed          exit=0
--- what the WORKER's check.py saw (marker written by worker code during the NC):
{"user": "ravindra", "uid": 501, "cwd": "…/T/orca-nc-p3wa1cnw/wt", "HOME": "/Users/ravindra",
 "PATH_head": ["$SP/stubbin", "/Users/ravindra/.local/share/mise/installs/go/1.27.0/bin"], "env_vars": 144}
```

Step 2 — sharpened (the audit "argued, not exercised" a later-unit poisoning; this shows it in the SAME
run with NO stub present at start). `$SP/c5/bin` is an EMPTY, user-writable dir first on PATH (the
scratch stand-in for `~/.local/bin`); a non-answering stand-in "real" gh (always 404, so no network) sits
further down; the coordinator names `--nc-command "python3 check.py"`; the worker's committed `check.py`
drops a `gh` into that dir and then asserts:

```
=== before: $SP/c5/bin EMPTY, first on PATH; gh resolves to:  $SP/c5/realgh/gh
NOTE: negative control EXECUTED — … (RED, as required)
NOTE: the same command exits 0 at clean head_sha …
verify: OK — all required checks passed          exit=0
--- after: gh resolves to  $SP/c5/bin/gh
--- review leg answered by the DROPPED gh (same run):
DROPPED-GH ARGV: api --paginate repos/o/r/pulls/7/reviews
DROPPED-GH ARGV: api repos/o/r/pulls/7
--- stand-in real gh calls: 0
--- control: --execute-nc OFF, bin emptied → real(stand-in) gh 404
FAIL: mutation unit: cannot fetch reviews for o/r#7 (gh: Not Found (HTTP 404)) — fail-closed   exit=2
```

Precondition check on THIS host — the first three PATH entries are all user-writable:

```
writable  /Users/ravindra/.local/share/mise/shims
writable  /Users/ravindra/.local/bin
writable  /Users/ravindra/.grok/bin
```

**Severity — the audit under-graded.** It graded P1 ("the enabling step is the sanctioned execution the
bar excludes, and no live lane was shown poisoned"). Re-read against §4: the RCE carve-out excludes
*execution of the unit's own tests* from being the finding; it does not excuse what that execution then
does to the verifier's OWN evidence path. The end state here is the P0 clause verbatim — "worker-authored
input [committed test code + manifest] making verify.py exit 0 over forged … evidence (false GREEN)", the
independent review being the forged leg — on a host whose PATH satisfies the precondition, in one
invocation, with `--repo` pinned correctly. The lit lane with `--execute-nc` on is the strongest lane the
gate offers, and it is the one this defeats. What keeps it from an unqualified P0: whether a lane
documented as sound actually runs with a user-writable dir on PATH (this host: yes; GitHub-hosted runners:
`$HOME/.local/bin` is on PATH, argued not exercised). Recommend: **P0 candidate**, coordinator decides.
Fix shape is the audit's (resolve `gh`/`git`/`gitleaks` to absolute paths ONCE before any NC, run the NC
with a scrubbed `env=` and no writable PATH entries, or in the sandbox lane) — plus the ordering fix:
resolve authorities before executing anything worker-written.

## C6 — the #284 fence test's coverage — PARTIALLY CONFIRMED; the P1 ("raw text reaches a TASK unfenced") REFUTED on this evidence (P2)

The regex (`tests/test_orphan_wiring.py:74`):
`gh\s+(?:issue|pr)\s+view\b|gh\s+api\b[^`\n]*(?:comments|issues|pulls)`; exemption = the substring
`guard_text.py` anywhere on the line (`:82`); scan set = `skills/` and `playbooks/` only (`:18-19`).

```
OFFENDS  gh issue view 42 --json body            OFFENDS  gh pr view 7 --json body,comments
OFFENDS  gh api repos/o/r/pulls/7/comments       OFFENDS  gh api repos/o/r/issues?state=open
passes   gh issue list --json number,title,body --limit 500
passes   gh pr list --json body                  passes   gh pr diff 7
passes   gh run view 123 --log                   passes   gh api graphql -f query='{…issue…{body}}'
passes   gh api repos/o/r/releases/latest        passes   curl -s https://x.invalid/issue.json
passes   glab issue view 42                      passes   wget -qO- https://x.invalid/x
passes   (exempt by mention)  gh pr view 7 --json body | tee body.txt   # not via guard_text.py
$ python3 -m unittest tests.test_orphan_wiring.TheFenceIsTheOnlyPath → Ran 3 tests … OK
```

**Confirmed:** `list --json body`, `pr diff`, `run view --log`, `api graphql`, non-(comments|issues|pulls)
`gh api` paths, `curl`/`wget`/`glab`, exemption-by-mention, and `runtime/*.md` being outside the scan.
**Over-claim (in the candidate as routed to me):** `gh pr view` and `gh api …/(comments|issues|pulls)`
ARE matched — the routed wording lists them as misses. **Over-claim (audit F-3):** "absent from every
write-lane mission" — the fence instruction is not in the SKILL.md text, but every one of clean-sweep,
absorb-it, oss-contribute, harden-it, review-it RIDES `sandbox-policy`, whose `:125-134` is the fence
doctrine, so it reaches every such TASK by composition. Corpus sweep of unfenced fetch lines
(`rg "gh (issue|pr|api|run|…)|curl |glab " skills playbooks runtime/*.md`, fence lines excluded): the only
stranger-text reads are `playbooks/upstream-contribution.md:20` (`gh pr list --search … --state open`,
an enumeration; titles only, no `--json body`) and `merge-serialization.md:33` /
`reviewed-sha-freshness.md:29` (`gh pr view … --json headRefOid,baseRefName,state` — metadata, not text).
No mission was run, so "raw external text reaches a TASK unfenced" is not shown by me or the audit. What
IS decorational is one sentence: `sandbox-policy.md:133` "A contract test greps … so the fence stays the
only path" — the test guarantees less than the sentence says. Graded **P2**: widen `RAW_FETCH` (the
audit's list is right), make the exemption structural, scan `runtime/`, and either reword `:133` or add the
inverted test (missions with tracker/PR sources must name `guard_text.py --source`).

---

## Summary for triage

- **Fix-worthy P1, confirmed as claimed:** C1, C2, C3.
- **Upgrade candidate:** C5 → P0 (same-run false GREEN reproduced; precondition holds on this host).
- **Hold as claimed but strip the framing:** C4 — facts hold, "presented as a guarantee" does not.
- **Downgrade:** C6 → P2 hardening (coverage gap real; the P1 end state not shown; fence reaches the
  TASKs via the ridden policy).
- Not done (timebox): no live-PR completion of C1; no GitHub-runner PATH check for C5; no mission run
  for C6. All scratch state is under `$SP` (c1–c5, stubbin); the accidental real `gh api` GET was one
  read-only 404 against a non-existent `o/r#7`.
