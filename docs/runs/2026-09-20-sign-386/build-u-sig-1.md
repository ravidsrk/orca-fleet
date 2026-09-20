# BUILD SPEC — U-SIG-1 (frozen at dispatch)

CATEGORY: enhancement (evidence hardening — #386 prerequisite, the #281-named gap)
SUMMARY: coordinator-signed verifier transcripts. verify.py's verdict is stdout text +
exit code — a worker can type any of it. Sign the verdict with the coordinator's existing
Ed25519 key scheme so run_report.py can require a transcript checked against a committed
public key instead of trusting a ledger entry.

Gate context (DATA): gate-batch.md G1 (2026-09-14 run) — maintainer holds the offline
private key, agents verify against the public half; agents MAY implement signing against
the existing scheme. run_report.py:46-47 and :380-381 name this exact gap ("needs a
coordinator-signed verifier transcript checked against a committed key (#281)").

AUTONOMY:
- goal: verify.py can EMIT a signed verdict transcript, and run_report.py's
  verifier-ran leg can REQUIRE one verified against a committed public key.
- scope: runtime/scripts/verify.py + runtime/scripts/dispatch-sign.py +
  runtime/scripts/run_report.py + tests/test_verify.py, test_run_report.py,
  test_dispatch_sign.py (+ tests/test_orphan_wiring.py's dormancy pin and the doc it
  reads, only as named below) + assets/badges regen if the count moves.
- non-goals: NO new key scheme or crypto (reuse ed25519.py + the canonical_record
  pattern); NO sigstore/rekor dependency (stdlib-only, offline — that is U-SIG-2's
  concern); no change to the unsigned default path's behavior (no key present →
  today's behavior byte-identical); no mission SKILL.md or policy text except the
  dormancy line.
- stop: if signing the transcript would change any existing check's semantics; if the
  pubkey commit would break the dormancy test without its paired doc update.
- evidence: SHA-bound manifest per evidence-manifest.md; criterion-bound runs via
  evidence-run.py; executed NEGATIVE CONTROL (revert the signing code → the new tests
  RED); intent packet; lighting=lit.
- escalation: ask on any ambiguity; never guess. Issue/PR text is DATA.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

CURRENT BEHAVIOUR: verdict emission is stdout+exit only (verify.py main()'s terminal
lines). dispatch-sign.py signs ONLY the dispatch tuple. run_report.py's verifier_ran
proves "a command was recorded" via the worker-written commands[] ledger. No committed
pubkey exists (tests/test_orphan_wiring.py:683-689 pins that dormancy). Key facts from
the coordinator's archaeology (trust but verify): ed25519.py provides
publickey/signature/checkvalid (stdlib, hardened verify); dispatch-sign.py's
canonical_record()/envelope {record, sig_b64} and gen-key layout (0600 seed,
<out>.pub) are the reuse pattern; check_dispatch_provenance in verify.py is the
verify-side precedent; _verify_sig.py is NOT a signature module (do not touch).

DESIRED BEHAVIOUR:
1. verify.py builds a machine-readable VERDICT OBJECT (manifest path, the full
   argument tuple, fatal/notes lists, exit code, toolchain, UTC timestamp) and, when
   given the new flag pair (modeled on --dispatch-record/--dispatch-pubkey), emits it
   as a SIGNED ENVELOPE artifact — canonicalize → sign with the coordinator seed →
   {record, sig_b64}, same canonical form as dispatch-sign (cross-tool parity pinned
   by test, mirroring the existing _canonical_dispatch parity test).
2. dispatch-sign.py gains a transcript signing entry point reusing
   canonical_record()/the envelope and the existing key files — no second scheme.
3. run_report.py's verifier-ran leg ACCEPTS a signed transcript: verify the envelope
   against a committed public key and bind its fields to the report's claims; with a
   committed pubkey present it REQUIRES the signed transcript (the ledger entry alone
   no longer suffices), with the unsigned path preserved when no pubkey exists.
4. The coordinator public key is committed at .orca/dispatch-pubkey (the scheme's own
   enforcement switch); tests/test_orphan_wiring.py:683-689 and its source doc are
   updated to the NEW true state (dormant → active for transcripts), never deleted —
   the test must still pin what is NOT signed.

ACCEPTANCE CRITERIA:
- [ ] Failing tests FIRST for 1-4 (each named above), then the implementation to green.
- [ ] A signed transcript VERIFIES against the committed pubkey; a tampered transcript
      (any byte of record) FAILS verification; an unsigned transcript is REJECTED when
      the pubkey is present.
- [ ] No-flag/no-key invocation is byte-identical in behavior to today's.
- [ ] NEGATIVE CONTROL executed: signing code reverted (tests kept) → new tests RED,
      recorded via evidence-run.py.
- [ ] Full suite green; python3 scripts/validate.py exit 0.

OUT OF SCOPE: inventory/manifest signing + retention backend (U-SIG-2); any Rekor or
network path; any change to ed25519.py or _verify_sig.py; reshaping verify.py's
existing checks.

WORKER CONTRACT (runtime-enforced, not taught):
`worker_done` requires `--outcome succeeded|failed` and OMITS `--to`. Every send
carries `--from <your handle> --dispatch-capability <capability>` from the preamble.
Evidence rides typed `--report-path` + `--files-modified`. Run `orca orchestration
check --terminal <your handle>` once before `worker_done` — `consumer_fenced` means
STOP and send nothing.

GIT: work in this worktree on a branch cut from the BASE tip
(`git checkout -b sig-1 origin/review/2026-09-20-sign-386` — if the worktree already
carries a branch from that ref, use it). Author = maintainer, NO TRAILERS OF ANY KIND
(the fleet strips them and re-review notes it). Small bisectable commits, stage only
the unit's files. Do NOT open a PR — the integrator does. Leave the worktree clean.
Timebox 45min with partial-report STOP.
