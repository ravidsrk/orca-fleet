# harden-it 409 — audit W2: axes 2 (signatures/replay) and 3 (key custody / at-rev key)

**Worker:** task_fadc1417879c, pack addy, profile SAFE-LOCAL. **Audited rev:** `a2033f74`
(this worktree). **Threat model:** `docs/runs/2026-09-21-harden-409/threat-model.md` (frozen).
**Method:** every scenario reproduced or refuted against the real scripts in-process or in scratch
git repos under the session scratchpad, with THROWAWAY keys only (`dispatch-sign.py gen-key`
into the scratch dir; K1 plays the coordinator, K2 the worker). No real key material was read,
copied or placed anywhere; no network; no write to this worktree except this file.
**Timebox:** 45 min — every scenario on both axes was exercised; nothing was left unprobed.

## Verdict

| Scenario | Result | Grade |
|---|---|---|
| S2.1 small-order / malleability re-attack | REFUTED — every crafted signature/key refused | — |
| S2.2 type-confusion across sign/verify | REFUTED — every edit of a signed record breaks the signature or fails the comparison | observation (b64 decode asymmetry) |
| S2.3 record/transcript replay across re-runs | REFUTED — path, bytes, exit and args all bind; unsigned-field substitution finds nothing the record is meant to bind | — |
| S2.4 transcript field-subset / falsy confusions | REFUTED — partial args, `false`/`0.0`/`""` swaps and stray keys all refuse | observation (blind `sign-transcript`) |
| S3.1 seed-read discipline | **CONFIRMED — P1** (threat-model bar: "signs without warning → P1 custody gap") | **P1** |
| S3.2 pubkey pin substitution via refs | REFUTED as P0/P1 — the swapped pin is honoured in-session, but nothing records the pass as sound | observation (cross-axis S4.2) |
| S3.3 ancestry fork confusion | REFUTED where a grading base resolves; the `HEAD` fallback lets the pin choose its judge | observation |
| S3.4 unsigned lane re-entry with the key committed | REFUTED — unsigned block refused; signature line outside every block refused | — |

One P1, no P0. The 2026-09-20 signing path held on every forgery/canonicalization/replay probe.

## P1 — S3.1: every seed consumer signs with a world-readable, git-tracked seed and says nothing

Custody is guarded at creation only (`dispatch-sign.py:165-171` — 0600 at `os.open`; `gen_key`
refuses an unignored in-repo path). At USE, four paths read the seed with `read_text()` and no
`stat`/location check: `dispatch-sign.py:_seed` (`:179-187`, used by `sign` and
`sign-transcript`), `verify.py:_Transcript.seed` (`:1899-1908`), and `inventory.py:_read_seed`
(`:492-493`, delegates to `_seed`). Reproduced with a throwaway seed `chmod 644`, then the same
seed `git add`ed and committed, NOT ignored, inside a scratch repo:

```
$ ls -l $S/keys/k2-open | cut -c1-11
.rw-r--r--@
$ python3 runtime/scripts/dispatch-sign.py sign --key $S/keys/k2-open --manifest-id u-1 --contract-digest sha256:aa --unit-class mutation
{
  "record": {
exit=0
$ git ls-files committed-seed; git check-ignore -q committed-seed; echo "check-ignore rc=$?"
committed-seed
check-ignore rc=1 (1 = NOT ignored)
$ python3 runtime/scripts/dispatch-sign.py sign --key ./committed-seed ...            → envelope printed, exit=0, no warning
$ python3 runtime/scripts/dispatch-sign.py sign-transcript --key ./committed-seed ... → envelope printed, exit=0, no warning
$ python3 runtime/scripts/verify.py --manifest m.json --transcript-out t.json --transcript-key ./committed-seed
  (stderr filtered for key|seed|custody|readable: NOTHING)      envelope written, sig_b64 present: True
$ python3 runtime/scripts/inventory.py sign --key ./committed-seed r.md
inventory: signed 1 entry (digest de38108bb094…) in r.md         exit=0
# contrast — the SAME path is refused at creation:
$ python3 runtime/scripts/dispatch-sign.py gen-key --out $S/s3/newseed
dispatch-sign: REFUSING to write a private seed at …/s3/newseed   exit=2
```

Why P1 under the frozen bar (§4): a custody gap that erases the audit trail without leaking the
key — a seed that has ALREADY been committed or opened to the world keeps producing valid
signatures, so the enforcement lane keeps binding verdicts with a key that no longer proves
off-worker origin, and nothing in the toolchain's own output says so. The gate does not lie by
itself; it stops being able to tell. Fix shape (no semantics change, so not an ask-first item):
a shared `_seed_custody(path)` in `dispatch-sign.py` that the three callers run — refuse (or
`--unsafe-seed-ok`) when `stat().st_mode & 0o077`, when the path resolves inside a git work tree
and `git check-ignore` is not 0, and when the resolved path is under the graded repo root; add a
negative-control test per caller. Also worth a one-line refusal: a seed whose file is a symlink.

## Axis 2 — evidence

### S2.1 — checkvalid re-attack (in-process, `runtime/scripts/ed25519.py`, throwaway key)

```
$ python3 $S/s21.py runtime/scripts/ed25519.py
baseline valid          : True
(R, S+L) malleated      : False
(R, S+2L) malleated     : False
identity pubkey forgery : False        # (s·B, s) under A = (0,1)
order-2 pubkey forgery  : False        # A = (0,-1)
order-4 pubkey forgery  : False        # A = (sqrt(-1), 0)
y>=q identity pubkey    : False        # non-canonical encoding of (0,1)
y>=q R (non-canon R)    : False
x=0,sign=1 identity pub : False        # RFC 8032 "x=0 with sign bit" case
63-byte sig / 65-byte sig / 33-byte pub : False / False / False
mixed-order A+T accepts real sig?: False   # torsion-added key, non-cofactored eq.
```
Kill held through #386's refactors. Residual as documented: not constant-time (accepted).

### S2.2 — type confusion across the sign/verify pair

Signed a record with the throwaway key (`manifest_id "7"`, digest, `mutation`, `lit`,
`nc_paths [src/a.py, src/b.py]`, `nc_command "pytest -k AC_1"`), then edited the envelope /
argv / manifest and ran `verify.check_dispatch_provenance` from inside a scratch repo:

```
ACCEPT control (unedited)                           -> NOTE: dispatch record signature verified …
REFUSE manifest_id "7" -> 7 (int)                   -> signature INVALID
REFUSE manifest_id "7" -> 7, manifest unit 7 (int)  -> signature INVALID
REFUSE contract_digest upper-cased in record        -> signature INVALID
REFUSE contract_digest upper-cased on argv only     -> dispatch substitution: the run used contract_digest='SHA256:…' (false RED)
REFUSE contract_digest argv without sha256: prefix  -> dispatch substitution (false RED — no normalisation on either side, so no false GREEN)
REFUSE unit_class mutation -> report-only in record -> signature INVALID
REFUSE unit_class argv report-only vs signed mutation -> dispatch substitution
REFUSE lighting deleted from record, argv dark-elig -> signature INVALID
REFUSE lighting -> null in record, argv lit         -> signature INVALID
REFUSE nc_paths list -> tuple-string                -> signature INVALID
REFUSE nc_paths duplicated entry                    -> signature INVALID
ACCEPT nc_paths reordered                           -> NOTE (set semantics, by design #311)
REFUSE nc_paths NFD unicode swap                    -> signature INVALID
REFUSE nc_command trailing space / quoting variant  -> signature INVALID
ACCEPT extra unsigned field injected                -> NOTE (ignored: verify.py reads only _DISPATCH_FIELDS — verify.py:1999-2022)
REFUSE sig_b64 with trailing garbage                -> malformed (Incorrect padding)
REFUSE record wrapped: record.record                -> signature INVALID
REFUSE manifest nc_paths dup vs signed set          -> dispatch substitution
REFUSE manifest drops nc_command (signed)           -> record signs nc_command but the manifest carries no value
REFUSE manifest nc_command '' vs signed             -> dispatch substitution
```
`[7]` vs `["7"]` in `nc_paths` canonicalise identically (`str(x)` both sides) — no semantic
difference since paths are compared as strings both sides.

**Observation O-2.2 (not P0/P1):** `verify.py:1992` decodes `sig_b64` with
`base64.b64decode()` and no `validate=True`, while `run_report.py:634` and `inventory.py:304`
validate. Non-alphabet bytes inside the envelope's `sig_b64` are silently dropped by verify.py:
```
verify.py-style b64decode(mangled)==clean: True
validate=True (run_report/inventory): refused -> Only base64 data is allowed
```
Same 64 signature bytes, so no forgery — but the three consumers disagree on what a malformed
envelope is (#386 round 2 said "malformed sig_b64 always refuses"). One-token fix.

### S2.3 — replay across re-runs

Through `run_report.signed_transcript` in the scratch repo (K1 on `main`, run r1 on `feat`):
```
REFUSE replayed as run r2 (run_dir=r2)              -> transcript is outside this run's own directory docs/runs/r2/
REFUSE header says RED, transcript says exit 0      -> its exit 0 disagrees with RUN: verifier=RED
REFUSE manifest re-run (bytes change), old transcript kept -> its manifest_sha256 994017846e84… is not the graded manifest's bytes
REFUSE record unchanged, body shows different contract ref -> signed argument tuple … matches no verify.py invocation the body shows
```
Dispatch record: signs (unit id, contract digest, class, lighting, nc_*), not `head_sha` — a
record for unit U replays onto every re-run of U with the same contract, by design (the code
binding is the executed NC + review at `head_sha`). With a CHANGED contract the old record only
passes if the run also uses the old digest, and on the sound lanes `--contract-source/--digest`
are coordinator argv (#442-style); in-session it is advisory. Unsigned fields a worker can
substitute (`base`, `repo`, `execute_nc`, `no_gh`, `git_dir`, `evidence_root`) are all
coordinator argv off-worker; the waiver combinations are axis 1 (S1.4). No surviving substitution
on this axis.

### S2.4 — transcript field-subset / falsy confusions (`_Transcript.build` + both signers)

```
BINDS  control (K1-signed, key K1 on main, pin on feat)
REFUSE exit 0 -> false (== 0 in Python)             -> signature INVALID   (json: 0 ≠ false)
REFUSE exit 0 -> 0.0                                -> signature INVALID
REFUSE fatal [] -> "" (falsy)                       -> signature INVALID
REFUSE args: drop dispatch_record key               -> signature INVALID
REFUSE args: add extra key                          -> signature INVALID
REFUSE args: execute_nc true -> "true"              -> signature INVALID
REFUSE manifest_sha256 upper-cased                  -> signature INVALID
REFUSE unit "u-1" -> ""                             -> signature INVALID
BINDS  extra top-level unsigned field               -> (ignored; run_report reads only signed keys)
REFUSE sig_b64 with an embedded newline             -> sig_b64 is malformed (Only base64 data is allowed)
REFUSE record unchanged, body shows NO --execute-nc -> signed argument tuple matches no invocation the body shows
```
`run_report.py:640` `record.get("exit") != want` would treat a signed `false` as `0`, but no
signer emits it (`build` writes the int) and a worker cannot re-sign. Both signers refuse a
`None` field (`dispatch-sign.py:227`, `verify.py:1919`); a partial `args` dict is signable by
`sign-transcript` but refused by the binder (`run_report.py:667-676`) — fail-closed.

**Observation O-2.4 (not P0/P1 — needs a trusted party's mistake):** `sign-transcript` is a
blind signer: it checks field PRESENCE only. It signed my hand-typed `verdict.json` (exit 0,
`toolchain.verify_sha256 = "00"`) without running or hashing anything. Under the documented
offline-seed model ("verify.py runs without it, the maintainer signs the verdict afterwards",
`dispatch-sign.py:31-34`) nothing forces the verdict object to be the maintainer's OWN run; a
worker-produced `verdict.json` handed to the maintainer signs just as well. Cheap hardening:
refuse `exit == 0` with non-empty `fatal`, and refuse a `toolchain.verify_sha256` that is not
the sibling `verify.py`'s hash unless `--foreign-verifier-ok` (ties into S6.1).

## Axis 3 — evidence

### S3.2 — pin substitution via refs (`verify-gate.sh:63-73`)

Scratch repo with `runtime/scripts/` copied in at the same depth, a worker-controlled `origin`
(bare repo) whose `origin/HEAD` carries K2 at `.orca/dispatch-pubkey`, and a K2-self-signed
record:
```
pin at origin/HEAD = 26540b5dfed3161b… ; K2.pub = 26540b5dfed3161b…
== S3.2a no provenance
1:verify-gate: NOTE — native in-session hook is ADVISORY: … (incl. ORCA_PROVENANCE and any dispatch key) …
12:NOTE: dispatch record signature verified against the supplied key (#135) — a soundness boundary only if that key is trusted …
13:verify-gate: verifier returned 2 — BLOCKING completion            (other invariants; the record check itself PASSED)
== S3.2b ORCA_PROVENANCE=ci self-asserted
11:NOTE: dispatch record signature verified against the supplied key (#135) — …   (the gate's ADVISORY line is gone)
== S3.2d verify-gate.sh / hooks/hooks.json never request a transcript: (rg: no match)
```
The swapped pin IS honoured in-session — as `verify-gate.sh:74-77` and `docs/verify-gate.md:166-177`
state. Nothing records the pass as sound: the hook writes no transcript, an in-session transcript
would be unsigned (`S3.2c: signed envelope? False`) and refused once the key is committed, and
the verify.py NOTE carries its own caveat. Off-worker, `run_report.enforcement_key` reads the
key at the coordinator's grading base, not the pin. **Cross-axis note for S4.2:** with
`ORCA_PROVENANCE=ci` the only in-band "ADVISORY" statement disappears while "signature verified"
stays — a log reader sees a verified record with no caveat. Suggest the verify.py NOTE name the
key SOURCE (`…@origin/HEAD` = worker-reachable ref) so the caveat survives provenance suppression.

### S3.3 — ancestry fork confusion (`run_report.py:key_rev/enforcement_key`)

Scratch history: `C0` (pre-key) → `C1` (K1 lands on main); `feat` from C1 with a K1-signed
transcript; `fork-pre` from C0 carrying K2 as its own pin and a K2-signed transcript.
```
REFUSE fork-pre pin, K2-signed (base auto)          -> signature INVALID for the .orca/dispatch-pubkey committed at d37b2f78 (= C1, K1)
REFUSE fork-pre pin, --base main                    -> signature INVALID …
   key_rev: (C1, 'the grading base d37b2f78ba1b — the pin a627b5d2ff44 is not an ancestor of it, so the key is read where the pin cannot choose')
   [main renamed to trunk, checkout = fork-pre; GRADING_BASES falls through to HEAD]
   key_rev: (FP, 'the pin, an ancestor of the grading base a627b5d2ff44')
BINDS  fork-pre pin, base unresolvable -> HEAD fallback     <-- the pin chose its own judge
REFUSE same, with --base trunk                      -> signature INVALID …
```
The pin cannot choose its judge whenever any of `origin/HEAD, origin/main, origin/master, main,
master` resolves or `--base` is given; CI (`validate.yml:91`, `fetch-depth: 0`) always has
`origin/main`, and `bind_check.py` passes `--base`. **Observation O-3.3:** the last-resort `HEAD`
fallback (`run_report.py:500`) turns the enforcement switch into the checkout's own pin — in a
checkout whose default branch is not main/master and has no `origin`, a self-pinned K2 report
binds. Not reachable by a worker on the sound lanes; suggest `HEAD` be dropped from
`GRADING_BASES` when a `.orca/dispatch-pubkey` exists anywhere reachable (fail closed: "name
--base"), or at least emit `why` on the bound line. Related by design, noted not graded: a pin on
main's ancestry reads the key AT the pin, so after a key rotation a report merged under the old
key keeps binding under it (the grandfather lane; only matters if rotation was for a leak).

### S3.4 — unsigned-lane re-entry with the key committed (`inventory.py:find_signature`)

```
REFUSE unsigned block, key committed                -> .orca/dispatch-pubkey is committed at d37b2f78 … so an UNSIGNED integrity inventory no longer binds
BINDS  K1 signature INSIDE block (control)
REFUSE K1 signature OUTSIDE block (after ## other)  -> inventory-signature line at line 12 sits outside every inventory block — not an envelope; refused
REFUSE K1 sig placed BEFORE the inventory heading   -> … line 3 sits outside every inventory block … refused
REFUSE K2 (self) signature inside block             -> signature INVALID for this pubkey
REFUSE K2 sig inside block, pin on pre-key fork     -> signature INVALID (key read at main = K1)
REFUSE two K1 signatures inside block               -> 2 inventory-signature lines — a document carries one signature
BINDS  K1 sig inside a nested ``` fence in the section   (within the block range — by design, the section IS the block)
```
Both halves of S3.4 refuse. Neither passes → not P0.

## Scratch / cleanup

All PoCs live under the session scratchpad (`s21.py`, `s22.py`, `s3.sh`, `s3.py`, scratch repos
`scr/`, `s3/`, `bare/`, throwaway keys `keys/`). The committed-seed fixture was removed from the
scratch repo after the probe. Nothing outside the scratchpad and this file was written.
