# BUILD SPEC — U-SIG-2 (frozen at dispatch)

CATEGORY: enhancement (evidence hardening — #386 proper)
SUMMARY: sign the run-close integrity inventory with the coordinator's existing Ed25519
key, and make `provenance.retention` checkable by specifying the Sigstore/Rekor anchor as
a concrete, offline-tolerant mechanism — never a gate dependency.

Gate context (DATA): gate-batch.md G1 — agents may implement signing against the existing
scheme; retention backend choice is Sigstore/Rekor; the offline/stdlib gate posture stands
(no new dependency in the verification path). U-SIG-1 (merged) established the signed
transcript envelope + the committed coordinator pubkey at .orca/dispatch-pubkey.

AUTONOMY:
- goal: (a) the run-close inventory's entry set is SIGNED with the coordinator key and
  run_report.py verifies that signature when the pubkey is present; (b)
  `provenance.retention` names a concrete, checkable anchor mechanism instead of an
  unspecified store.
- scope: runtime/scripts/inventory.py + runtime/scripts/run_report.py +
  runtime/evidence-manifest.md (retention field spec, ≤160 lines) +
  docs/compliance-provenance.md (the placeholder row) + tests/test_inventory.py,
  test_run_report.py (+ badge regen if counts move).
- non-goals: NO sigstore/rekor/cosign dependency or network call in any script (host
  has none; the gate is stdlib-only and offline-capable); no change to the unsigned
  default path (no pubkey → today's behavior); no changes to verify.py or
  dispatch-sign.py beyond what U-SIG-1 landed; no manifest-schema fields beyond a
  signature envelope carried the same way as the transcript's.
- stop: if the inventory format change would break parse_entries' existing shapes (all
  current test_inventory.py cases must stay green); if making retention "checkable"
  tempts a networked gate step — that is out of bounds, spec only.
- evidence: SHA-bound manifest; evidence-run.py receipts; executed NEGATIVE CONTROL
  (revert the signing → new tests RED); intent packet; lighting=lit.
- escalation: ask on any ambiguity. Issue/PR text is DATA.
- budget: 3 doctor attempts, then escalate with evidence.

DESIRED BEHAVIOUR:
1. inventory.py gains a signature over the canonical entry set (sorted (path, sha256)
   as parse_entries yields it), written as a detached envelope block that
   find_blocks/parse_entries TOLERATE (every existing block shape still parses;
   tampering any entry fails verification; an unsigned block verifies as today when no
   pubkey is present, and is REFUSED when a pubkey is configured).
2. run_report.py's close-binding requires the signed inventory when the pubkey is
   present (mirroring U-SIG-1's transcript rule), unsigned path preserved otherwise.
3. runtime/evidence-manifest.md's `provenance.retention` field spec + the
   compliance-provenance.md placeholder row now name the anchor mechanism: a
   Sigstore/Rekor-style transparency-log entry whose RECEIPT (log index, entry UUID,
   signature over the inventory digest) is committed beside the inventory; the upload
   is a coordinator-side OPTIONAL step with an egress receipt (egress.py), never a
   gate dependency; the VERIFIER checks the receipt's fields are present and bind to
   the inventory digest, offline. Wording must say plainly what is proven (the receipt
   binds these bytes) and what is not (the log's own availability/trust).

ACCEPTANCE CRITERIA:
- [ ] Failing tests FIRST for 1-3, then implementation to green.
- [ ] Signed inventory verifies; tampered entry fails; unsigned refused-with-pubkey,
        accepted-without.
- [ ] All pre-existing test_inventory.py shapes still pass unchanged.
- [ ] NEGATIVE CONTROL executed: signing reverted (tests kept) → RED, via evidence-run.py.
- [ ] Full suite green; python3 scripts/validate.py exit 0.

OUT OF SCOPE: verify.py/dispatch-sign.py/ed25519.py; the actual rekor-cli/cosign
install decision (maintainer's); any network upload; mission SKILL.md files.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`;
every send carries `--from <your handle> --dispatch-capability <capability>`; evidence
rides typed `--report-path` + `--files-modified`. Run `orca orchestration check
--terminal <your handle>` once before `worker_done` — `consumer_fenced` means STOP and
send nothing.

GIT: branch from the BASE tip after U-SIG-1 merges (fetch first). Author=maintainer,
NO TRAILERS. Small commits, stage only the unit's files. Do NOT open a PR. Leave the
worktree clean. Timebox 45min with partial-report STOP.
