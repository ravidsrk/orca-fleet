# harden-it 409 — audit worker 1 (axes 1 and 5)

**Run:** docs/runs/2026-09-21-harden-409/threat-model.md (frozen) · **Worktree HEAD:** a2033f74 ·
**Pack:** addy (security-and-hardening, audit phase only) · **Profile:** SAFE-LOCAL — scratch repos under
the session scratchpad (`/private/tmp/claude-501/…/scratchpad/h409/`), a stub `gh` on PATH that logs argv and
returns env-shaped pages, one read-only `gh api` call against this repository (S1.1, dot-segment probe), no
key material touched, no writes to this worktree except this file. Every probe ran the real CLI
(`runtime/scripts/verify.py` at a2033f74) or the function under test via `importlib`; excerpts below are
verbatim (long lines cut at ~200 chars, marked `…`). Harness: `mkrepo.sh` (two-commit repo mirroring
`tests/test_verify.py::EndToEndMutationGreen`), `mkmanifest.py` (GREEN-shaped mutation manifest with dotted
overrides), `stubbin/gh`.

**Bottom line:** no P0. Two P1 candidates, both outside the appendix baseline: **F-1** the independent-review
authority's *repository* is inferred from the clone's `origin` URL when `--repo` is omitted — worker-writable
git config picks the judge (S1.1-adjacent); **F-2** a `./`-spelled evidence path is bounded against the
toplevel but looked up by git relative to its cwd, so with the verifier (or `--git-dir`) below the toplevel the
verdict binds a path that does not exist where it was bounded (S5.1 divergence). S1.2, S1.3, S1.4, S5.2 and
S5.3 are clean at the P0/P1 bar; observations with cheap hardenings follow each.

---

## Axis 1 — manifest/evidence spoofing & false-GREEN

### S1.1 Fabricated review pointer (`pr.number` shape) — **refuted for false GREEN; F-1 found beside it**

Baseline (stub gh returns one independent APPROVED at head_sha; manifest `pr.number: 7`):

```
$ PATH=$SCR/stubbin:$PATH python3 verify.py --manifest m.json --contract-source contract.md@HEAD --contract-digest $DIG --repo o/r --unit-class mutation --lighting lit
verify: OK — all required checks passed
exit=0
ARGV: api --paginate repos/o/r/pulls/7/reviews
ARGV: api repos/o/r/pulls/7
```

No shape validation exists (`verify.py:685-690` → `fetch_reviews`/`fetch_pr_author`, f-strings at `:618`, `:626`);
every shape reaches `gh` as endpoint text (stub still answers APPROVED, so all read GREEN *against the stub*):

```
=== pr.number="5/comments"               gh ARGV: api --paginate repos/o/r/pulls/5/comments/reviews
=== pr.number="../../repos/x/y/pulls/1"  gh ARGV: api --paginate repos/o/r/pulls/../../repos/x/y/pulls/1/reviews
=== pr.number="7?per_page=1"             gh ARGV: api --paginate repos/o/r/pulls/7?per_page=1/reviews
=== pr.number="7 --method DELETE"        gh ARGV: api --paginate repos/o/r/pulls/7 --method DELETE/reviews   (one argv element — not an option)
=== pr.number=["7"] / {"$":1} / true / 7.0 / "-7" / "7\n"   → repr()/str() of the value spliced into the path
```

Whether an endpoint confusion can reach ANOTHER repository decides P0. Read-only probe against this repo
(the only network call made):

```
$ gh api 'repos/ravidsrk/orca-fleet/pulls/../../repos/ravidsrk/orca-fleet/pulls/487' --jq '.number'
{"message": "Not Found", … "status": "404"}   gh: Not Found (HTTP 404)
$ gh api 'repos/ravidsrk/orca-fleet/pulls/491?per_page=1/reviews' --jq 'type'
object
```

Dot-segments are sent raw by `gh` (Go `net/url`) and GitHub does not normalize them → 404 → `fetch_reviews`
returns an error → RED. The query-string shape swallows `/reviews` and returns the PR *object*;
`parse_review_pages` refuses a non-array page → RED. The one shape that returns the reviews array from the
first call (`"7/reviews?x="`) makes the second call return an array too, and `fetch_pr_author`'s `.get` on a
list raises — caught by the `collect()` wrapper:

```
=== pr.number=7/reviews?x= ; PR endpoint answers an ARRAY
FAIL: malformed manifest: AttributeError in a verifier check ('list' object has no attribute 'get')
verify: 1 invariant(s) failed — unit is NOT done          exit=2
```

Because the path prefix `repos/{repo}/pulls/` is fixed, `pr.number` can only select a PR *inside* `--repo`;
`review_ok` still demands `commit_id == head_sha` from a non-author, which is the baseline design.
**Verdict: refuted.** *Observation O-1:* validate `pr.number` as a positive `int` (or `^[1-9][0-9]*$`) before it
becomes endpoint text; today a manifest string is spliced into a gh endpoint unvalidated, and one shape trips
an `AttributeError` instead of a typed refusal.

**F-1 (P1, candidate P0) — the review REPOSITORY is worker-selectable when `--repo` is omitted.**
`main()` uses `args.repo or infer_repo()` (`verify.py:2277`); `infer_repo()` reads `git remote get-url origin`
(`:153-159`) — git config, which the graded worker writes in its clone (and, in a shared-`.git` worktree
layout, for every worktree). `verify-gate.sh:55,98` forwards `--repo` only when `ORCA_REPO` is set;
`docs/verify-gate.md:86` and `verify-gate.sh:22` call it "optional; inferred from origin"; the
`ci|mcp|sdk|dispatch` provenance case (`verify-gate.sh:120`) is described as "sound; record is auditable"
with no requirement that `ORCA_REPO` be set there (only the reference CI YAML at `docs/verify-gate.md:141`
pins `--repo "$GITHUB_REPOSITORY"`). Reproduction — `--repo` omitted, origin rewritten by the "worker":

```
$ git remote set-url origin git@github.com:evil/mirror.git
$ PATH=$SCR/stubbin:$PATH python3 verify.py --manifest m53.json --contract-source contract.md@HEAD --contract-digest $DIG --unit-class mutation --lighting lit
verify: OK — all required checks passed
  exit=0
ARGV: api --paginate repos/evil/mirror/pulls/7/reviews
ARGV: api repos/evil/mirror/pulls/7
```

Attack shape (argued, not exercised — needs a live PR): push the same `head_sha` to a repo the worker
controls, open PR #N there, have any second account approve it (author exclusion is by *that* PR's author
login), set `origin` to that repo, name `pr.number: N`. `review_ok` sees an independent APPROVED at `head_sha`
and the unit reads GREEN with no review of the real PR. Acceptance-bar fit: "worker-authored input making
verify.py exit 0 over … substituted evidence" — P0 if any lane documented as sound runs without `ORCA_REPO`
(the gate's own doc says it is optional; `ORCA_PROVENANCE=dispatch` is not gated on it); P1 at minimum
("env … reaching gh as a ref"). Fix shape: make `--repo` REQUIRED whenever a GitHub lookup will happen
(mutation ∧ ¬no-gh ∧ ¬dark-eligible) and fail closed otherwise; if inference must stay, take it from the
signed dispatch record, never from `origin`.

### S1.2 Unbounded evidence (deep nesting / multi-GB artifact) — **clean at the bar; O-2, O-3**

`load_manifest` (`verify.py:170-177`) catches `OSError, JSONDecodeError, UnicodeDecodeError` only; a deeply
nested document raises `RecursionError` inside `json.loads`, which escapes `main()` as a traceback:

```
$ python3 -c "open('deep.json','w').write('['*100000+']'*100000)"
$ python3 verify.py --manifest deep.json … --transcript-out t2.json
RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string
exit=1  transcript=no
$ ORCA_MANIFEST=deep.json bash runtime/scripts/verify-gate.sh --event Stop --manifest deep.json …
RecursionError: …
verify-gate: verifier returned 1 — BLOCKING completion
```

Every caller lane fails closed: the gate blocks on any nonzero (`verify-gate.sh:127-137`), and no transcript is
written so `run_report.py` cannot bind (absence never binds). The crash is exit **1 = usage**, not the
documented exit 2 with a `malformed manifest` line (`verify.py:45`), and `{"unit": [[[…` inside an object
behaves identically. Artifact reads are whole-file (`_read_artifact` → `read_bytes()`, then the redaction
regexes over the text); a 768 MiB pinned artifact, bounded to this process:

```
$ /usr/bin/time -l python3 verify.py --manifest m.json … (artifacts[] pins big/nc.txt, 768 MiB)
verify: OK — all required checks passed
       94.81 real        93.46 user         1.27 sys
          2449620992  maximum resident set size
```

≈3.2× the artifact in RSS and ~95 s; a multi-GB artifact either `MemoryError`s inside `collect()` (→ exit 2)
or is OOM-killed (→ nonzero → BLOCK). Availability only — a worker can wedge its *own* verification, not the
gate for others. **Verdict: refuted as P0/P1** (the bar excludes non-systemic DoS). *O-2:* add
`RecursionError`/`MemoryError` to `load_manifest`'s catch so the exit is the documented 2 and the transcript
still records a RED. *O-3:* cap artifact bytes (e.g. 64 MiB) and manifest size before parsing.

### S1.3 Ledger self-description under exotic quoting (#352 regression trap) — **clean**

Both sides normalize to `shlex.join(shlex.split(·))` (`verify.py:1641-1663`, `_nc_command:744-763`); equal
argv ⇒ identical execution in the replay, so no quoting can split "what the ledger names" from "what runs":

```
=== control: identical                                  verify: OK   exit=0
=== exotic-legal quoting, same argv
  ledger.cmd=…/python3 'check.py'   --nc-command="…/python3" check.py   manifest.nc.command=…/python3 ""check.py
  verify: OK — all required checks passed                exit=0
=== double-space + tab, same argv                       verify: OK   exit=0
=== ledger names the command, manifest names a different one ('true')
  FAIL: --execute-nc: negative_control.command 'true' is not the command the coordinator supplied out of band …   exit=2
=== ledger normalizes equal but wraps via sh -c (different argv)
  FAIL: commands ledger: fresh exit-0 record(s) exist, but none is the coordinator-named proof command …   exit=2
=== ledger unbalanced quote (shlex ValueError)          FAIL: … none is the coordinator-named proof command …   exit=2
=== override with a trailing '# x' (argv, not a comment) verify: OK   exit=0   (coordinator's own choice)
```

**Verdict: no regression.** *O-4 (ledger-integrity nits, not boundaries — the ledger is worker-written by
design):* `_fresh_command_records` uses `c.get("exit") == 0`, so `"exit": false` counts as green; a record
with `cmd_sha256` omitted skips the self-hash assertion (`:1619-1622` `continue`) yet still counts as fresh.

### S1.4 Waiver conjunction (dark-eligible × no-gh × narrated NC) — **clean**

GitHub stub returns NO reviews for the whole matrix; review artifact is untracked and sha-pinned:

```
A dark-eligible + no-gh, no --execute-nc                          FAIL: dark-eligible mutation: … must be EXECUTED …   exit=2
B … + --execute-nc, no --nc-command                               FAIL: --execute-nc requires --nc-command … + waiver FAIL   exit=2
C … + --execute-nc --nc-command <proof> + contract                verify: OK (NOTE: independent review waived — dark-eligible unit …)   exit=0
D as C but --contract-source "" --contract-digest ""              FAIL: oracle scope … + FAIL: … without an out-of-band coordinator contract …   exit=2
E lighting flag omitted (manifest says dark-eligible), --no-gh    FAIL: no-gh mutation unit: … must be EXECUTED …   exit=2
F --unit-class report-only on a production diff                   FAIL: report-only unit changed code ['app.py'] and carries no signed dispatch record …   exit=2
G --unit-class planning                                           FAIL: planning unit changed code ['app.py'] …   exit=2
H class + lighting omitted, --no-gh                               FAIL: no-gh mutation unit: … must be EXECUTED …   exit=2
I dark-eligible, gh lane, no execute                              FAIL: dark-eligible mutation: … must be EXECUTED …   exit=2
J --lighting lit vs manifest dark-eligible                        FAIL: lighting swap: manifest says 'dark-eligible' but dispatch classed the unit 'lit' …   exit=2
K --execute-nc --nc-command true (unsupported proof)              FAIL: unsupported proof command; fail-closed …   exit=2
```

Only C — the sanctioned lane (executed NC + out-of-band contract) — reaches GREEN. **Verdict: no flag
combination reaches GREEN on text.**

## Axis 5 — path/symlink escape & scratch-repo classes

### S5.1 Symlinked evidence, both directions — **out-of-repo refused both ways; F-2 in the git-lookup divergence**

Through `_read_artifact` (`verify.py:292-331`) on a scratch repo (`s51.py`):

```
1 untracked symlink -> OUT of repo (pinned to target bytes)   REFUSED: evidence path escapes the repo toplevel (#267)
2 TRACKED symlink -> OUT of repo                              REFUSED: evidence path escapes the repo toplevel (#267)
3 untracked symlink -> IN-repo target, unpinned               REFUSED: … neither tracked at head_sha nor pinned …
3b same, pinned to TARGET bytes                               BYTES b'mutant m7 was KILLED …'      (= pinning the target itself; no gain)
4 TRACKED symlink -> in-repo nc.txt (git shortcut)            BYTES b'nc.txt'                       (git serves the LINK TEXT, never follows)
5 tracked-as-symlink, working tree = regular file             BYTES b'nc.txt'                       (commit wins; working-tree swap ignored)
6 tracked REGULAR at head, working tree = symlink OUT         REFUSED: evidence path escapes … (#267)   (false RED, not laundering)
7 untracked dir-symlink parent -> in-repo, unpinned           REFUSED: … unpinned evidence (#267)
8 a tracked DIRECTORY as the artifact                         BYTES b'tree 962d77…:docs/reports/u'  (synthetic listing of committed names)
9 './docs/reports/u/nc.txt'                                   BYTES …   ← git accepts `:./path` (cwd-relative)
9 'docs//reports/u/nc.txt' / 'docs/reports/../reports/u/nc.txt' / 'docs/reports/u/./nc.txt'   REFUSED … unpinned (git rejects, fallback needs a pin)
10 pinned then rewritten                                      REFUSED: … hashes cc8657… but artifacts[] pins f3db18… (#267)
```

Every branch reads only commit-pinned or sha-pinned bytes; symlinks launder nothing. `_resolve` bounds the
*resolved* target while git is handed the *manifest string* — and the two disagree exactly for the `./` spelling:

**F-2 (P1) — `./`-spelled evidence binds a path that does not exist where it was bounded.** `_resolve`
maps `./reports/u/nc.txt` to `<toplevel>/reports/u/nc.txt` (`:220-245`); `git cat-file -e head:./reports/u/nc.txt`
resolves `./` against git's cwd (`_git` runs in the process cwd or `-C --git-dir`, `:141-150`). When either is
below the toplevel the verifier grades a file the bound never saw:

```
$ (cwd=A) python3 -c "…v._ROOTS['git']=v._root_arg('--git-dir', root+'/docs')[0]…"
split? False
path='./reports/u/nc.txt'  exists_in_worktree=False -> BYTES b'mutant m7 was KILLED — proof went RED\n'
path='reports/u/nc.txt'    exists_in_worktree=False -> REFUSED: [Errno 2] No such file or directory …
```

End-to-end (manifest names `./reports/u/nc.txt` as NC artifact and `commands[].artifact`; nothing exists at
`<root>/reports/u/nc.txt`):

```
=== (i)  cwd=A, --git-dir A/docs            verify: OK — all required checks passed   exit=0
=== (ii) cwd=A/docs, no --git-dir           verify: OK — all required checks passed   exit=0
=== (iii) control: cwd=A, no --git-dir      FAIL: negative_control.artifact unreadable (./reports/u/nc.txt): [Errno 2] No such file …   exit=2
```

The bytes are still committed at `head_sha` in this repo, so no unpinned/out-of-repo bytes are read — but the
transcript/manifest now binds evidence to a path an auditor re-deriving from the clone root cannot find
("binding a ledger to content that never existed" at that path; the docstring's single-repo identity
"the file I resolved IS the blob git tracks" at `:200-203` is violated). Precondition is coordinator-side
(verifier or `--git-dir` below the toplevel; `_root_arg` accepts any dir inside a work tree, `:2166-2183`).
Fix shape: refuse manifest paths whose `Path.parts` contain `.`, `..` or `""` (and a leading `./`), or hand git
`-C <toplevel>` plus the normalized path so both sides name one file. *O-5:* `git cat-file -e` accepts a
**tree**, so a tracked directory is admitted as an artifact and its synthetic listing scanned (case 8); refuse
non-blob objects (`git cat-file -t`).

### S5.2 Scratch-root escape spellings (#349/#327 re-attack) — **/tmp class holds; O-6 on the class list**

`run_report._is_python_interpreter` (`run_report.py:203-233`) with the checker's own env (`TMPDIR` set):

```
True   python3                     True   /usr/bin/python3
False  /tmp/python3               False  /private/tmp/python3       False  /tmp//python3
False  /tmp/./python3             False  /private/tmp/../tmp/python3
False  /var/tmp/python3           False  /private/var/tmp/python3   False  /dev/shm/python3
False  /var/folders/65/…/T/python3    False  /private/var/folders/65/…/T/python3
False  /tmp/python3.13t           False  /tmp/pythonw
True   /Users/Shared/python3      True   ~/bin/python3              True   ~/.local/bin/python3
TMPDIR UNSET in the checker's env (cron/CI/other user):
True   /var/folders/65/…/T/python3    True   /private/var/folders/65/…/T/python3
```

Every `/tmp`, `/var/tmp`, `/private/…` spelling is refused (both sides resolved — #349 holds). Two spellings
of the same world-writable class pass: `/Users/Shared` (mode `drwxrwxrwt` on every macOS — exactly "no
toolchain installs an interpreter under them") and the macOS per-user temp dir `/var/folders/…/T` whenever the
**checker's** environment lacks `TMPDIR` (the list is built from the checker's env, `:195-200`, not the
run's). Same-uid HOME paths pass by design (the docstring says the check bounds forms, it does not
authenticate the binary; that is #281's signed transcript). Note `.orca/dispatch-pubkey` is **not committed on
this branch** (`git ls-files .orca` is empty), so the unsigned lane — where this check is what `verifier_ran`
rests on — is the live one. **Verdict: no P0/P1** (the design states the bound); *O-6:* add `/Users/Shared`
and `/private/var/folders` (or `confstr(_CS_DARWIN_USER_TEMP_DIR)`) to `_scratch_roots`, and do not let the
refusal depend on the checker's `TMPDIR`.

### S5.3 Split-root confusion (two clones of one project) — **clean**

Clone B = `git clone A`; manifest SHAs live in A; the tracked NC artifact in A says KILLED:

```
a0 control: single root (cwd=A)                                              verify: OK   exit=0
a1 --git-dir A --evidence-root B; B's file says SURVIVED, unpinned            FAIL: … is not pinned by a sha256 … under split roots the SHA repository is never consu…   exit=2
b  file ABSENT in B, tracked in A                                            FAIL: … [Errno 2] No such file or directory: '…/cloneB/docs/reports/u/nc.txt'   exit=2
b2 identical bytes in B but UNPINNED                                         FAIL: … not pinned by a sha256 … (#442)   exit=2
b3 same with the artifacts[] pin                                             verify: OK   exit=0   (B's bytes, by pin)
b4 pinned, B's bytes rewritten after pinning                                 FAIL: … hashes b70db9… but artifacts[] pins 463d5d… (#267)   exit=2
c  cwd NOT a repo, --git-dir A, no --evidence-root                           FAIL: … not inside a git repo — no toplevel to bound the evidence path against (#267)   exit=2
e  --evidence-root A/docs (a SUBDIR of the SHA clone)                        treated as split → pin-only → FAIL … No such file …   exit=2 (conservative)
```

The SHA repo's same-path blob is never consulted under a split; an unresolvable evidence side fails closed;
a subdirectory evidence root degrades to pin-only (fail-closed direction). **Verdict: #442 holds.**

---

## Summary table

| ID | Scenario | Class | Verdict |
|---|---|---|---|
| F-1 | Review repository inferred from worker-writable `origin` when `--repo`/`ORCA_REPO` omitted (documented "optional") | **P1 (P0 if a sound lane omits it)** | repro: stub gh shows `repos/evil/mirror/…`, exit 0 |
| F-2 | `./`-spelled evidence: `_resolve` bound ≠ git lookup path when git cwd is below the toplevel; GREEN binds a path absent at the root | **P1** | repro: exit 0 in (i)/(ii), exit 2 in control (iii) |
| O-1 | `pr.number` unvalidated → arbitrary text in the gh endpoint; one shape raises `AttributeError` | observation | fails closed |
| O-2 | Deep-nesting `RecursionError` escapes `load_manifest` → exit 1 traceback, no transcript | observation | all lanes block |
| O-3 | Whole-file artifact reads: 768 MiB → 2.45 GB RSS / 95 s | observation | self-DoS only |
| O-4 | Ledger nits: `exit: false` counts as 0; omitted `cmd_sha256` skips self-hash | observation | ledger is worker-written anyway |
| O-5 | A tracked directory is admitted as an artifact (`cat-file -e` accepts trees) | observation | listing = committed names |
| O-6 | `_scratch_roots` misses `/Users/Shared`, `/private/var/folders/…/T`; depends on checker's `TMPDIR` | observation | design bound stated |
| S1.3 / S1.4 / S5.3 | quoting regression, waiver conjunction, split roots | — | clean |

**Not done / out of scope for this worker:** F-1's live attack shape (a second-account approval on a mirror
PR) was argued from code, not exercised — creating PRs/reviews is Ask-First under the threat model §2.
Scratch artifacts are under the session scratchpad and can be discarded.
