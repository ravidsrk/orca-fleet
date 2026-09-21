# Threat model — harden-it run 409 (2026-09-21)

**Surface:** the catalog's own evidence toolchain — `runtime/scripts/verify.py` (2309 lines),
`runtime/scripts/dispatch-sign.py` (292), `runtime/scripts/verify-gate.sh` (137), and the signing
path landed 2026-09-20: transcript envelopes in `verify.py` / `run_report.py`, inventory signing in
`runtime/scripts/inventory.py`, the Ed25519 scheme in `runtime/scripts/ed25519.py` /
`dispatch-sign.py` (#281/#386, PR #489–#491).

**Adversary:** primarily the graded worker — an autonomous agent (or a compromised one) that
authors manifests, artifacts, transcripts-adjacent files, and its own environment, and that wants
a RED unit to read GREEN. Secondarily: an external party who can file issues/PRs or serve web
content to an unattended worker; and a supply-chain adversary who tampers with the toolchain's own
inputs (`gh`, `gitleaks`, sibling scripts). The coordinator and its Ed25519 seed are trusted;
the whole design fails if the seed reaches the worker, so custody is in scope.

**Ground rule for the audit:** do not re-prove what the 2026-09-10/11 deep review (#255–#284) and
yesterday's signing work already killed — those fixes are the baseline, not the target. Audit
effort goes to what they did not cover.

## 1. Trust boundaries (STRIDE per boundary)

### Boundary A — worker-authored manifest / transcript / evidence → verify.py
The verifier parses untrusted, worker-written input (manifest JSON, artifacts, the commands[]
ledger, the negative-control artifact, the PR number). STRIDE: chiefly **Tampering** and
**Spoofing**, with **DoS** and **Elevation of privilege** (manifest content reaching
git/gh/subprocess) secondary. Load-bearing: evidence bounds + pinning (`verify.py:220-245`,
`292-333`, #267); split roots are coordinator argv never manifest fields (#442); the criterion
denominator is the coordinator's frozen contract (`verify.py:422-478`, #268/#296); executed NC
in throwaway worktrees, argv-only (`verify.py:1428-1450`, `711-720`, #255); proof command only
from coordinator `--nc-command` (#279); control paths bind to the base..head diff (#280/#306);
option-injection guards (#382); review authority is GitHub with local tree-equivalence
(`verify.py:544-632`, #167); redaction incl. commands[].artifact (#309/#340); class downgrade
measured against the real diff (#310).
**Residual (audit targets):** `pr.number` flows from the manifest into the `gh api` path with no
shape validation (`verify.py:618,685`) — endpoint-confusion class, unprobed; no size/depth
limits on manifest or artifact reads (`verify.py:284-289`, `1725-1742`) — uncharacterized
memory-exhaustion DoS; per-check crash wrappers only cover collect()-routed checks — untrusted
paths that escape them into a usage-error exit a lane could misread; the no-gh review-artifact
substring check holds only via the executed-NC conjunction (`verify.py:674-681`).

### Boundary B — the signing path (seed custody, canonical form, checkvalid, at-rev key resolution)
STRIDE: **Spoofing**, **Tampering** (canonicalization confusion), **Repudiation**,
**Information disclosure** (seed leak). Load-bearing: checkvalid hardening
(`ed25519.py:142-159` — small-order/non-canonical/malleability refused, the keyless-forgery
class dead); one canonical form per record type with cross-tool parity tests
(`dispatch-sign.py:80-100`, `verify.py:1844-1868`); signing an absence refused
(`verify.py:1919-1926`, `dispatch-sign.py:227-231`); a requested-but-unwritten transcript is
exit 1 (`verify.py:2296-2304`); the enforcement switch read ancestry-aware
(`run_report.py:524-556`); absence never binds (`run_report.py:604-617`); the inventory
signature honored only inside a block (`inventory.py:256-285`); malformed sig_b64 always
refuses (#386 round 2); seed written 0600 at creation, in-repo gen-key refused
(`dispatch-sign.py:103-176`, #163/#166).
**Residual:** `--transcript-key` reads the seed from any path with no permission/location check
(`verify.py:1898-1908`) — custody is guarded at creation, not at use; no replay semantics
(nonce/expiry) on dispatch records or transcripts — replay across re-runs uncharacterized;
type-confusion in the canonical JSON (int vs str, digest case, Unicode) unproven; ed25519.py
not constant-time (`ed25519.py:8-16`, accepted offline); the at-rev resolution trusts
origin/HEAD…HEAD as grading base — a moved-base trap test is owed.

### Boundary C — the hook surface (verify-gate.sh consuming host env)
STRIDE: **Tampering** (env substitution), **Spoofing** (provenance self-assertion),
**Elevation of privilege** (env values reaching git/argv). Load-bearing: fail-closed with no
manifest and on any nonzero verifier exit (`verify-gate.sh:79-93`, `127-137`, `49`); the
in-session gate is ADVISORY by design and says so in-band (`verify-gate.sh:13-18`, `116-125`);
pubkey auto-discovery prefers the reviewed remote blob with the worker-controls-refs caveat
(`verify-gate.sh:63-77`).
**Residual:** every `ORCA_*` value is attacker-influenceable in the native lane — the only
breaker is the off-worker re-run; audit whether anything *claims* more than advisory in-session;
positional fallback for ORCA_MANIFEST (`verify-gate.sh:52`); env values forwarded as argv
elements but the path@ref colon/whitespace classes are unprobed.

### Boundary D — issue/PR/CI text and fetched content as DATA
STRIDE: **Elevation of privilege** (prompt injection crossing from data to directive).
Load-bearing: `guard_text.py` is the only sanctioned path (envelope always, exit 3 on failed
fetch, NFKC+Cf detection-only normalization, forged-banner defusal, argv-only fetch); the #284
contract test greps missions/playbooks for raw `gh issue view` outside the fence.
**Residual:** the test's pattern covers only the literal `gh issue view` — `gh api`,
`gh pr view`, `curl` and other fetch forms escape it; English-keyword injection labels miss
non-English/obfuscated directives (accepted by design — the framing is the control).

### Boundary E — test fixtures / scratch repos (git operations in tmp dirs)
STRIDE: **Tampering** (fixture poisoning), **Information disclosure / DoS** (path escapes).
Load-bearing: `_resolve` containment after symlink resolution (`verify.py:238-245`); scratch-root
resolution resolving both sides of the macOS /tmp symlink (`run_report.py:191-200`, #349);
interpreter-path refusal for worker-placed files (`run_report.py:203-233`, #327);
verifier-path pinning to this repo's verify.py (`run_report.py:171-187`).
**Residual:** the NC worktrees inherit the repo's symlinks/hooks and the NC command runs there
with the verifier's privileges — git filters/attributes/smudge drivers partially unmitigated;
cleanup is `worktree remove --force` + rmtree — the worktree path's mid-run replaceability
unprobed.

### Boundary F — CI workflows (egress receipts, verdict-check trust tiers)
STRIDE: **Spoofing** (forged GO verdicts), **Tampering** (fail-poisoning heads),
**Repudiation**. Load-bearing: verdict-check evaluates only GO-marker reviews from trusted
associations, no push triggers, GO-dismissal re-blocks (`scripts/verdict_check.py:40-54`,
#452/#460/#465); egress.py hash-chained content-free receipts, fail-closed.
**Residual:** egress.py has no automated sink — no send path is FORCED to write a receipt (the
test asserts a policy names it, not that sends run it); verdict-check's two residual poison
cases are documented+accepted (stale-sha GO, dismissed-then-replaced GO); confirm no workflow
grants write to a job consuming worker-influenced content.

## 2. Always / Ask-First / Never (per runtime/sandbox-policy.md:98-120)

**Always:** read anything in the repo; run validate.py, the suite, and scripts' self-tests;
static analysis of all scripts; write PoC manifests/contracts/envelopes/fixtures; create scratch
git repos under the system temp dir and run verify.py / run_report.py / inventory.py /
guard_text.py against them locally; exercise ed25519.py in-process against crafted signatures;
run dispatch-sign.py sign/sign-transcript with THROWAWAY keys generated into the scratch dir;
stat-only existence/permission probes of ~/.orca-fleet/* (never read key bytes); local DoS PoCs
bounded to the auditor's own process.

**Ask-First (one-way human gate):** generating/rotating/committing any coordinator keypair or
changing .orca/dispatch-pubkey; any change to signing semantics (_RECORD_FIELDS /
TRANSCRIPT_FIELDS, canonical form, checkvalid acceptance, the ancestry rule); any networked call
beyond read-only `gh api` against this repository (creating test PRs, posting/dismissing
reviews); any change under .github/workflows/ or hooks/hooks.json; merging any resulting fix to
the default branch (the normal PR + review + merge-train is the grant mechanism).

**Never on this host:** destructive or networked exploit PoCs; supply-chain attack simulations
against live package managers; exfiltration demonstrations — those need the danger profile in an
ephemeral per-workspace sandbox, and this host has NO validated ORCA_SANDBOX_RECIPE
(spawn_worker.sh would refuse the lane; the refusal stands). Reading private key material —
never cat/copy/place a seed anywhere (repo, scratch, manifest, artifact, fixture). Any PoC that
could fail-poison live CI state (submitting reviews to a real PR) — those classes are argued
from code, never exercised live.

## 3. Audit axes (waves) — 20 PoC scenarios, written not executed until ROUTED

### Axis 1 — manifest/evidence spoofing & false-GREEN (A)
- S1.1 Fabricated review pointer: `pr.number` non-integer/path-shaped ("5/comments",
  "../../repos/x/y/pulls/1") against a stub gh logging argv and returning attacker-shaped pages.
  Real if an endpoint confusion parses as a review at head_sha → false GREEN.
- S1.2 Unbounded evidence: multi-GB artifact + deeply nested manifest. Real if the crash exits
  as "usage, retry" rather than BLOCK in any caller lane.
- S1.3 Ledger self-description: a correct-hash commands[] record whose --nc-command carries
  exotic-but-legal quoting — regression trap on #352's named-command check.
- S1.4 Waiver conjunction: dark-eligible + no-gh + narrated (unexecuted) NC — real if any flag
  combination reaches GREEN on text → P0.

### Axis 2 — signature canonicalization, replay & keyless forgery (B)
- S2.1 Small-order/malleability re-attack (identity keys, (R,S+L), non-canonical encodings) —
  proves yesterday's kill held through #386's refactors.
- S2.2 Type-confusion across the sign/verify pair (manifest_id 7 vs "7", digest case, Unicode,
  duplicate nc_paths entries). Real if an edited record still verifies → P0.
- S2.3 Record replay across re-runs: a legit record replayed against a re-dispatched unit with
  a changed contract; probe the fields the record does NOT sign for a surviving substitution.
- S2.4 Transcript field-subset: partial args tuple or empty-string/false confusions through
  _Transcript.build and both signers.

### Axis 3 — key custody & at-rev key resolution (B, C)
- S3.1 Seed-read discipline: a world-readable or in-repo seed passed to --transcript-key /
  dispatch-sign sign. Real if the tool signs without warning → P1 custody gap.
- S3.2 Pubkey pin substitution via refs (worker-written pubkey read by verify-gate.sh
  auto-discovery in a scratch repo). Real only if anything RECORDS the resulting pass as sound,
  not advisory.
- S3.3 Ancestry fork confusion: report pinned off the grading base's ancestry with a self-signed
  key at the pin while the base carries the real key. Real if the pin chooses its own judge.
- S3.4 Unsigned-lane re-entry with the key committed: unsigned block, and a signature line
  OUTSIDE the block. Real if either passes → P0.

### Axis 4 — hook/env injection (C)
- S4.1 Env-to-git option injection through ORCA_CONTRACT_SOURCE / ORCA_BASE / ORCA_SYMBOL
  (leading '-', '@', '..', whitespace) traced into read_source/check_ancestry/check_symbol_on_base.
- S4.2 ORCA_PROVENANCE=ci self-assertion: confirm the only effect is NOTE suppression and no
  consumer treats it as off-worker-origin evidence.
- S4.3 Stop-lane asymmetry: whether a unit can end with the manifest unset while work is
  outstanding in any supported host.

### Axis 5 — path/symlink escape & scratch-repo classes (A, E)
- S5.1 Symlinked evidence: out-of-repo target (refused) and IN-repo target (probe whether the
  git-lookup-path vs resolved-target divergence launders an unpinned file past the pin check).
- S5.2 Scratch-root escape spellings (/tmp vs /private/tmp vs $TMPDIR) re-attacking #349/#327.
- S5.3 Split-root confusion: two clones of one project — a same-path blob in the SHA repo must
  never be consulted; unresolvable either side must fail closed as split.

### Axis 6 — supply-chain of the toolchain's own inputs (A, D, F)
- S6.1 Sibling-script substitution: verify.py loads diff_scope.py/_verify_sig.py/ed25519.py by
  path; the transcript pins verify_sha256 — real if NO consumer checks that hash (a recorded
  pin that binds nothing, presented as a guarantee) → P1.
- S6.2 gh/gitleaks authority: a stub gh feeding fabricated review pages; gitleaks absent vs
  present moving the redaction floor. Real if an off-worker lane inherits worker-controlled PATH.
- S6.3 Unguarded fetch forms: grep the corpus for untrusted-text ingestion bypassing
  guard_text.py in forms the #284 test misses (gh pr view, gh api, curl, glab). Real if raw
  external text reaches a TASK unfenced → P1 (P0 on a write lane).

## 4. Acceptance bar — what counts on THIS surface

**P0 — the gate lies, the key leaks, or evidence executes the verifier:** any worker-authored
input making verify.py exit 0 / run_report.py bind over forged, tampered, substituted, or
replayed evidence (false GREEN), incl. canonicalization confusions and unsigned-path acceptance
with the key committed at the read rev; key material disclosure to the worker or into evidence;
RCE from manifest/artifact/envelope CONTENT (beyond the sanctioned coordinator-named
--nc-command execution of the unit's own tests); an enforcement bypass on a lane documented as
sound.

**P1 — the floor drops silently or a control is decorational:** fail-open on malformed input
where the contract says fail-closed; a recorded-but-never-checked pin presented as a guarantee;
evidence/scratch escapes reading out-of-repo bytes as evidence or binding a ledger to content
that never existed; custody gaps that erase the audit trail without leaking the key; env
injection reaching git/gh as options or refs even where the end state fails closed by luck.

**Not P0/P1 here (accepted, documented):** false RED / availability findings short of systemic
gate-wedging DoS; the native in-session hook being advisory (#112, stated in-band); ed25519.py's
non-constant-time arithmetic (accepted offline use); guard_text.py's label coverage (the framing
is the control); verdict-check's two documented residual poison cases (manual re-run hatch by
decision, PR #465).

## Appendix — already hardened (baseline the audit must NOT re-spend on)

| Class | Fix | Mechanism |
|---|---|---|
| Text-only negative control | #255 | executed NC in throwaway worktrees |
| Waiver lanes on paperwork | #256 | executed NC required for dark-eligible / no-gh |
| Out-of-repo / unpinned evidence | #267 | `_resolve` bounds + artifact pinning |
| Prose tokens counted as criteria | #268 | anchored extraction + structural check |
| Worker-chosen proof command | #279 | coordinator-only `--nc-command` |
| Decoy control paths / oracle revert | #280/#306 | static + executed bind to base..head |
| Typed-by-the-worker verdicts | #281/#386 | signed transcript + signed inventory |
| Raw external text into tasks | #284 | guard_text.py fence + contract test |
| Tier advance on prose | #286 | verifier_ran ledger check |
| Hidden/under-declared criteria | #296 | `hidden_criterion_ids` + JSON check |
| Class downgrade via env | #310 | diff-measured class |
| Worker-chosen oracle inputs | #311 | signed nc_paths/nc_command/nc_artifact_sha256 |
| Keyless forgery / malleability | signing path | `checkvalid` hardening |
| Key at creation / in-repo seeds | #163/#166 | 0600-at-creation + worktree refusal |
| /tmp symlink & fake interpreter | #349/#327 | resolved containment |
| Ledger proves nothing named | #352 | named-command freshness |
| Option-shaped SHAs / newline paths | #382 | refusals |
| Cross-repo evidence confusion | #442 | split roots |
| Verdict griefing / self-GO | #460/#465 | trust tiers |
