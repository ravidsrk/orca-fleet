# harden-it 409 — audit worker 3: axes 4 (hook/env injection) and 6 (supply chain)

Threat model: `docs/runs/2026-09-21-harden-409/threat-model.md` (frozen). Pack: addy. Profile:
SAFE-LOCAL — every probe ran in scratch git repos under the session scratch dir with THROWAWAY
keys (`dispatch-sign.py gen-key` into scratch); no real key material touched; no network beyond
this repo; the only write to this worktree is this file. Audited at `a2033f74`
(`git rev-parse HEAD` in the worktree). Timebox 45 min from 11:17; report written 11:29–11:40.

Verdict summary — **3 × P1, 0 × P0, 4 scenarios refuted, 4 observations.**

| Scenario | Result | Grade |
|---|---|---|
| S4.1 env → git option injection | refuted (options refused / argparse-blocked); ref *expressions* pass through | observations O-1, O-2, O-3 |
| S4.2 ORCA_PROVENANCE self-assertion | refuted — sole consumer is the NOTE `case` in verify-gate.sh:119 | — |
| S4.3 Stop-lane manifest-unset asymmetry | exists, advisory lane only, documented in-band | observation O-4 |
| S6.1 sibling substitution / `verify_sha256` consumer | **confirmed — pin has zero consumers and covers verify.py only** | **P1 — F-1** |
| S6.2a stub `gh` → fabricated review | accepted in-process; off-worker inheritance via the NC run argued from code | **P1 — F-2** |
| S6.2b gitleaks absent/stub | refuted — built-in floor fires regardless | — |
| S6.3 unguarded fetch forms | **confirmed — fence invoked twice in the corpus; test satisfied by silence** | **P1 — F-3** (P0 on write lanes if a run shows raw text in a TASK — not demonstrated) |

---

## Axis 4 — hook / env injection (Boundary C)

### S4.1 — env-to-git option injection through ORCA_CONTRACT_SOURCE / ORCA_BASE / ORCA_SYMBOL

Trace: `verify-gate.sh:52-107` forwards each env value as ONE argv element (`set -- "$@" --base "$BASE"`),
so whitespace/newline never splits. In verify.py: `read_source` (`:248-266`) refuses a leading `-`
on either half of `path@ref` and absolute paths; `check_ancestry` (`:1745-1754`) prefixes
`origin/` so the value can never start with `-`; `check_symbol_on_base` (`:1757-1768`) passes the
symbol after `-e`. Option-shaped values that survive the shell are rejected by argparse (exit 2 →
gate BLOCK).

Probe (scratch repo with a local bare `origin`, a fork commit `4342aab` NOT on `origin/main`, and
`origin/main@{1}` repointed at that fork via `git update-ref`; verify.py loaded by path from this
worktree, cwd = the scratch repo):

```
S4.1 --base 'main'                   -> ['head_sha is not an ancestor of origin/main (not merged / wrong base)']
S4.1 --base 'main@{1}'               -> []                                   # <-- reflog expression PASSES ancestry for an unmerged fork tip
S4.1 --base 'main~1'                 -> ['head_sha is not an ancestor of origin/main~1 (not merged / wrong base)']
S4.1 --base 'main..fork'             -> ['NOTE: origin/main..fork not found — ancestry check skipped']
S4.1 --base '--output=/tmp/pwn'      -> ['NOTE: origin/--output=/tmp/pwn not found — ancestry check skipped']
S4.1 --base 'main\nfoo'              -> ['NOTE: origin/main\nfoo not found — ancestry check skipped']
S4.1 source 'contract.md@-x'         -> None refusing option-like ref/path (leading '-') — see git-option-injection guard
S4.1 source '-x@main'                -> None refusing option-like ref/path (leading '-') — see git-option-injection guard
S4.1 source 'contract.md@main@{1}'   -> b'contract v1\n' None                # reflog-old blob read; digest check still catches it
S4.1 source 'contract.md@'           -> b'contract v2\n' None                # trailing '@' silently reads the WORKING TREE
S4.1 source 'contract.md@main..fork' -> None None                            # git show exit 0 with EMPTY stdout -> (b'', None)
S4.1 source '@main'                  -> b'tree main:\n\ncontract' None       # tree listing returned as "contract" bytes
S4.1 source '/etc/passwd@main'       -> None absolute path refused in a path@ref source (#267): /etc/passwd
S4.1 symbol '-e'  base 'main'        -> ["symbol '-e' not found on origin/main (change may not be on base)"]
S4.1 symbol '.'   base 'main'        -> []                                   # regex '.' matches every file -> trivial pass
$ ls -la /tmp/pwn  ->  "/tmp/pwn": No such file or directory        # no option ever reached git
```

End-to-end through the hook (`sh runtime/scripts/verify-gate.sh --event task`, scratch repo,
`ORCA_CONTRACT_DIGEST` = real sha256 of `contract.md`, one hostile variable per run):

```
== ORCA_SYMBOL=-x
verify.py: error: argument --symbol: expected one argument          # argparse exit 2 -> gate BLOCK
== ORCA_BASE=--output=/tmp/pwn2
verify.py: error: argument --base: expected one argument
== ORCA_CONTRACT_SOURCE=-x@main
verify.py: error: argument --contract-source: expected one argument
== ORCA_CONTRACT_SOURCE=contract.md@main@{1}
FAIL: scope: authoritative source does not match --contract-digest (sha256:6ea6486a… != sha256:033b7e4a…)
== ORCA_BASE=main@{1}
FAIL: head_sha is not an ancestor of origin/main@{1} (not merged / wrong base)
verify-gate: verifier returned 2 — BLOCKING completion
$ ls /tmp/pwn2 -> No such file or directory
```

**Refuted as P0/P1**: no env value reaches git or gh as an *option*; every caller of `read_source`
(`check_scope:430`, `check_oracle_scope:1048`, `check_dispatch_provenance:1983/1986`) digest-compares
the bytes, so the empty-read and wrong-blob shapes fail closed.

- **O-1 (observation, cheap #382-style fix):** `--base` is documented as a *branch* but is a full
  git revision expression after `origin/`. `main@{1}` made `check_ancestry` pass for a commit that
  is NOT on `origin/main` (a force-pushed-away tip is exactly what the reflog keeps). Same for the
  `ref` half of `path@ref` (`contract.md@main@{1}` read a superseded blob). Only the in-session
  (advisory) lane lets the worker set it; the CI snippet's `$GITHUB_BASE_REF` is a GitHub branch
  name and cannot carry `@{`. Recommend: refuse `@{`, `~`, `^`, `..`, `:` and whitespace in
  `--base`, `--symbol`, and the ref half of every `path@ref` (`read_source`), the way #382 refuses a
  leading `-`.
- **O-2 (observation):** `read_source("x@a..b")` and `read_source("x@..")` return `(b'', None)` —
  `git show` exits 0 with empty stdout for a range-shaped ref — and `read_source("x@")` silently
  falls back to the working tree. All current callers digest-compare, so it is a fail-open-*shaped*
  primitive, not a fail-open. Recommend: treat empty stdout as an error in `read_source`, and refuse
  a trailing `@`.
- **O-3 (observation):** `--symbol` is a regex (`git grep -e`): `.` or `^` passes trivially.
  Recommend `-F` (fixed string) — the check is "this symbol is on base", never a pattern.

### S4.2 — ORCA_PROVENANCE self-assertion

```
$ rg -n "ORCA_PROVENANCE" --glob '!docs/reports/**' --glob '!docs/runs/**' .
./runtime/scripts/verify-gate.sh:119:case "${ORCA_PROVENANCE:-}" in
./runtime/scripts/verify-gate.sh:122:          "ORCA_PROVENANCE and any dispatch key), so nothing here is a soundness boundary. A signed" \
./tests/test_verify_gate.py:58:        env["ORCA_PROVENANCE"] = provenance
./docs/verify-gate.md:217:   `ORCA_PROVENANCE` decides only whether the advisory `NOTE` is emitted, never whether the key is
(+ .env.example and doc lines 123/169/177/219, all saying the same)
```

verify-gate.sh never forwards it to verify.py; verify.py, run_report.py, inventory.py,
dispatch-sign.py contain no reference; `_Transcript.ARGS` (`verify.py:1860`) is a fixed tuple that
does not include it, so it never enters a signed record. **Refuted**: the only effect is the
advisory-NOTE suppression, and `docs/verify-gate.md:217` says exactly that. Nothing records a
`ci` assertion as off-worker evidence.

### S4.3 — Stop-lane asymmetry (manifest unset while work is outstanding)

`verify-gate.sh:79-87`: `Stop` + `ORCA_MANIFEST` unset ⇒ exit 0; `TaskCompleted` + unset ⇒ exit 2.
"Unit in progress" has exactly one source of truth — that env var — and nothing in the repo sets
it for a spawned worker:

```
$ rg -n "ORCA_MANIFEST" runtime/ hooks/ docs/ops.md skills/*/SKILL.md playbooks/*.md
runtime/scripts/verify-gate.sh:19,52,83,86   (the consumer only)
$ rg -n "ORCA_MANIFEST|export ORCA" runtime/scripts/spawn_worker.sh
(no output — spawn_worker.sh never exports it)
```

A Claude Code hook inherits the session's launch env, which the worker's Bash calls cannot
mutate, so in-session the asymmetry is not worker-*triggerable*; it is simply that on every
spawned native worker the `Stop` gate is a no-op for the whole session. The sound lanes (CI /
MCP-Task / SDK subprocess, `docs/verify-gate.md:129-150`) are invoked per unit with an explicit
manifest and have no `Stop` semantics. **Not P0/P1** — the native lane is advisory by contract and
the carve-out is stated in-band (`docs/verify-gate.md:40-49`, `getting-started.md:122-125`).

- **O-4 (observation):** nothing tells a coordinator to *set* `ORCA_MANIFEST` when spawning a
  native worker, so the documented "mid-unit Stop is refused" behaviour is unreachable from the
  catalog's own spawn path. Either `spawn_worker.sh` should accept/export a manifest path, or
  `docs/verify-gate.md` should say the `Stop` lane only fires when the operator exports it by hand.

---

## Axis 6 — supply chain of the toolchain's own inputs (Boundaries A, D, F)

### F-1 (P1) — S6.1: `toolchain.verify_sha256` is signed, never checked, and covers one of four files

**Claim under test:** the transcript "pins" the verifier. **Fact:** the pin is `sha256(verify.py)`
alone (`verify.py:1893`), and no consumer reads it.

```
$ rg -n "verify_sha256" --glob '!docs/reports/**' --glob '!docs/runs/**' .
./tests/test_verify.py:2313:        self.assertEqual(rec["toolchain"]["verify_sha256"],
./tests/test_verify.py:2379:               "toolchain": {"python": "3", "verify_sha256": "cd" * 32},
./runtime/scripts/verify.py:1893:                "verify_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
$ rg -n "verify_sha256|\[\"toolchain\"\]|\.get\(\"toolchain\"" runtime/ scripts/ .github/
(no output)
```

`run_report.signed_transcript` (`run_report.py:593-694`) verifies the signature, then binds
`manifest`, `manifest_sha256`, `exit`, `args` and `unit_class` — `toolchain` is never read. Meanwhile
verify.py loads three siblings by path with no hash: `ed25519.py` (`:1836`, `checkvalid`),
`diff_scope.py` (`:789`, test-path classification for the NC binding), and `_verify_sig.py`
(`:1166-1173`) — the module that decides whether an executed control's RED is a real assertion
failure or a stillborn mutant (`_failure_signature`, used at `:1447`).

PoC (scratch: `pristine/` = a copy of the five scripts; `tampered/` = same, with `_verify_sig.py`
overridden so `_failure_signature` always returns `(True, None)`; throwaway seed):

```
$ python3 $S/pristine/verify.py --manifest m.json --unit-class report-only --transcript-out $S/t-pristine.json --transcript-key $S/throwaway.seed
$ python3 $S/tampered/verify.py --manifest m.json --unit-class report-only --transcript-out $S/t-tampered.json --transcript-key $S/throwaway.seed
sha256(_verify_sig.py): pristine=acc3d5cfb0f6fedf tampered=574e159031f9fddd
pristine verify_sha256: af5a9da6084765d0 signed: True
tampered verify_sha256: af5a9da6084765d0 signed: True
IDENTICAL toolchain pin despite substituted _verify_sig.py: True
```

Both envelopes verify against the throwaway pubkey; the tampered run's record is byte-for-byte
the same in `toolchain`. A coordinator (or auditor) whose script directory carries a substituted
sibling produces a signed transcript indistinguishable from a sound one, and even a substituted
`verify.py` itself would be *recorded* but never *compared* to anything.

**Grade: P1** — "a recorded-but-never-checked pin presented as a guarantee" (acceptance bar §4;
`--transcript-out` help at `verify.py:2241-2247` lists `toolchain` among the signed verdict's
contents). Not P0: the attacker must already write to the verifier host's script dir; the pin's
job was to *detect* that and it cannot.

**Fix shape:** (1) in `run_report.signed_transcript`, compare `record.toolchain.verify_sha256`
with `blob_at(<grading base or rev>, runtime/scripts/verify.py)` and refuse on mismatch (decide
which rev is authoritative — the pinned `inventory_at` vs the grading base — with the same
ancestry rule PR #489 uses for the key); (2) widen the pin to the loaded set: sha256 over
`verify.py` + `_verify_sig.py` + `diff_scope.py` + `ed25519.py` (e.g. `toolchain.scripts_sha256`
over the sorted `name\0sha\n` lines), computed from the same `Path(__file__).parent` the loaders use;
(3) add the negative-control test: a transcript whose `verify_sha256` differs from the blob at rev
must not bind.

### F-2 (P1) — S6.2a: the review authority is a PATH-resolved `gh`, reachable from the executed NC

`fetch_reviews`/`fetch_pr_author` (`verify.py:612-631`) resolve `gh` with `shutil.which` and
invoke it by bare name; nothing pins an absolute path, a hash, or checks `gh auth status`'s host.
In-process demonstration (a stub `gh` prepended to `PATH`, logging argv and answering with an
APPROVED review by a non-author at `head_sha`):

```
$ cat $S/bin/gh
#!/bin/sh
# AUDIT STUB (S6.2) — logs argv, returns attacker-shaped pages. Never a real gh.
echo "stub-gh argv: $*" >> "$(dirname "$0")/gh.log"
case "$*" in
  *"/reviews"*) printf '[{"state":"APPROVED","commit_id":"%s","user":{"login":"independent-reviewer"}}]\n' "$STUB_HEAD" ;;
  *"/pulls/"*)  printf '{"user":{"login":"worker-author"}}\n' ;;
esac
$ python3 - … (check_review(m, "stablyai/orca-fleet", is_mutation=True) with PATH=$S/bin:$PATH)
PATH with stub gh  -> []                      # review check PASSES on fabricated pages
which gh -> …/scratch/s62/bin/gh
stub-gh argv: api --paginate repos/stablyai/orca-fleet/pulls/409/reviews
stub-gh argv: api repos/stablyai/orca-fleet/pulls/409
```

In-session that is the documented advisory lane. The off-worker question ("does a sound lane
inherit worker-controlled PATH?") is answered by the executed negative control: `_run_at`
(`verify.py:711-720`) runs the coordinator-named command (`pytest …`) in a throwaway worktree at
`head_sha` **with the verifier's full environment** — no `env=`, no PATH/HOME scrub
(`rg -n "env=|os.environ" runtime/scripts/verify.py` → no hits) — executing the worker's own test
code at the SHA under grading. That code runs as the verifier user and can drop a stub `gh` into
any user-writable PATH directory (`~/.local/bin`, a Homebrew prefix), after which *every later
unit's* review lookup on that host is fabricated. Argued from code, deliberately not exercised
(sandbox-policy.md: no persistence PoCs on this host).

**Grade: P1** — the independent-review control becomes decorational once one NC has run, and the
lane docs (`docs/verify-gate.md:174-176`) call CI/MCP/SDK "SOUND" because the coordinator sets the
*env*, without noting that the NC step hands that env to worker code. Not P0: the enabling step is
the sanctioned execution the bar explicitly excludes, and no live lane was shown poisoned.

**Fix shape:** resolve `gh`/`gitleaks`/`git` ONCE at verifier start (before any NC run) to absolute
paths and reuse them; run the NC with a scrubbed env (`env={"PATH": <fixed>, "HOME": <tmp>, …}`)
and, on the sound lanes, in the ephemeral sandbox the danger profile already defines; record the
resolved `gh` path + `gh --version` in `toolchain` so F-1's check can bind it.

### S6.2b — gitleaks absent vs present: refuted

`check_redaction` (`verify.py:1690-1743`) always runs `REDACTION_PATTERNS`; `_gitleaks_scan`
(`:1668-1686`) can only ADD a `gitleaks-rule` hit. Probe with a `ghp_…` token in a pinned artifact:

```
== gitleaks-absent      (PATH=/usr/bin:/bin:/usr/local/bin)
FAIL: redaction: credential shape(s) ['github-token'] found in artifact leak.txt — …
== stub-gitleaks-exit0  (PATH=$S/bin:… ; stub is `#!/bin/sh` / `exit 0`)
FAIL: redaction: credential shape(s) ['github-token'] found in artifact leak.txt — …
```

The floor holds with gitleaks absent and with a stub that always reports clean. A stub can only
suppress the *ceiling* (gitleaks-only rules) — accepted.

### F-3 (P1) — S6.3: the fence is invoked twice in the corpus; the #284 test is satisfied by silence

The doctrine (`runtime/sandbox-policy.md:125-134`, ridden by 15 missions): "Fetch it through the
fence, never raw … A contract test greps missions and playbooks for raw `gh issue view` outside
that script, so the fence stays the only path (#284)." The test
(`tests/test_orphan_wiring.py:65-93`, `RAW_FETCH`) matches `gh issue|pr view` and `gh api …
(comments|issues|pulls)`, and exempts any line containing the substring `guard_text.py`.

```
$ rg -c "guard_text.py --source" skills/ playbooks/ runtime/*.md | rg -v ":0$"
runtime/sandbox-policy.md:1              # the policy sentence itself
playbooks/upstream-contribution.md:2     # the oss-contribute WATCH loop — the ONLY mission-level use
$ rg -c guard_text skills/absorb-it/SKILL.md skills/clean-sweep/SKILL.md skills/oss-contribute/SKILL.md skills/harden-it/SKILL.md skills/review-it/SKILL.md
0 0 0 0 0
```

The four missions that ingest the most stranger-written text name no fetch at all — clean-sweep
`source=tracker` ("every open issue in scope (paginated to the end)", `SKILL.md:63-67`),
oss-contribute's enumeration (`SKILL.md:55-57`), absorb-it (inbound PR bodies/comments/diffs;
`SKILL.md:72-80`, and `:130` lists "Treating PR text as instructions" as a failure mode with no
fence named), harden-it (audit surfaces) — so a worker or coordinator following them types the
raw `gh issue view` / `gh pr view` themselves, and the grep-test, which fires only on a *literal*
raw command in the doc, passes. Forms the regex also misses, verified against `RAW_FETCH`:

```
OFFENDS  gh issue view 42 --json body
passes   gh issue list --json number,title,body --limit 500          # issue bodies, raw
passes   gh pr list --repo up/stream --search 'x in:body' --json body  # PR bodies (upstream-contribution.md:20 uses this form)
passes   gh pr diff <n>                                              # stranger diff
passes   gh run view <id> --log                                      # CI log text a PR controls
passes   gh api graphql -f query='{repository{issue(number:1){body}}}'
passes   gh api repos/o/r/releases/latest                            # release notes
passes   curl -s https://example.invalid/issue.json
passes   glab issue view 42
passes   gh pr view 7 --json body | tee body.txt   # not via guard_text.py   <-- exempt by mere mention
passes   Read every open issue in scope (paginated to the end).      # no command at all
```

**Grade: P1** — a control the doctrine presents as "the only path" is enforced on the one form
nobody writes, and is absent from every write-lane mission that consumes tracker/PR text
(clean-sweep, absorb-it merge PRs). The bar's P0 clause ("raw external text reaches a TASK
unfenced … on a write lane") needs a run showing it in a dispatched TASK; I did not run a mission,
so this stays P1 on the corpus evidence. Not exercised: `guard_text.py` itself — its argv-only
fetch, exit-3, and forged-banner tests all pass in `tests/test_guard_text.py` and are baseline.

**Fix shape:** (1) invert the test — for each mission whose `metadata.unit`/source is tracker, PR
or audit text (clean-sweep, oss-contribute, absorb-it, harden-it, review-it), require the string
`guard_text.py --source` in the SKILL.md or a playbook it composes; (2) widen `RAW_FETCH` to
`gh (issue|pr) (view|list|diff)`, `gh run view … --log`, `gh api graphql`, `curl`, `wget`,
`glab`, and any `gh api` path; (3) make the exemption structural — the match must be *inside* a
`guard_text.py … --fetch` invocation, not merely share a line with the word; (4) add the missing
fetches to absorb-it / clean-sweep / harden-it explicitly (`guard_text.py --source issue --fetch
gh issue list …`, `--source pr --fetch gh pr view <n> --json body,comments`).

---

## Not done / out of timebox

- S6.2 persistence vector (NC test code writing onto the verifier's PATH) argued from
  `verify.py:711-720`, not executed — by policy.
- F-3's P0 clause needs an actual dispatched TASK transcript from a clean-sweep `source=tracker`
  or absorb-it run; none exists in `docs/runs/` to read.
- I did not re-verify Boundary B canonicalization or Boundary E worktree classes — other workers' axes.

Scratch artifacts (throwaway keys, stub `gh`/`gitleaks`, scratch repos) live only under the
session scratch dir and were not copied anywhere.
