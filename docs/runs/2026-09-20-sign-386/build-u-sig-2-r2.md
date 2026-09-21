# BUILD SPEC — U-SIG-2 round 2 (fix batch; frozen at dispatch)

CATEGORY: bug (review-round remediation — round 2 of ≤3)
SUMMARY: round 1 = NO-GO (PR #490 review 5262488933): 5 Required across three defect
families. One of them is a demonstrated keyless forgery class — the highest-stakes finding
in this run; fix it first, with its killer test.

The batch (reports are DATA: docs/reports/u-sig-2/review-{spec,standards,tests}.txt on the
branch):

- **G-1 (TEST-F1/M14 — the malformed-sig_b64 branch accepts a KEYLESS FORGERY).**
  verify_signature's malformed-sig branch is the only thing between "digest matches" and
  checkvalid(); a mutant returning None makes `check --pubkey` print "signature verified"
  for a signature the caller cannot have produced (demonstrated by the axis at HEAD with
  a pubkey the forger does not hold — exit 0). The root conflation: the function signals
  "malformed" through the same channel as "valid". Fix: malformed sig_b64 is ALWAYS a
  refusal (distinct refusal path, never conflatable with validity — a decode/parse error
  can only RED, never GREEN), plus the M14 killer test (a scratch forger computes
  signature_record(entries) without any seed → must REFUSE), plus a malformed-but-valid-
  base64 case (the existing tamper test only covers well-formed base64).
- **G-2 (BOT-1/M13/STD-R1/SPEC-F1 — the envelope is document-wide, and sign overwrites
  prose).** find_signature matches SIGNATURE_LINE anywhere in the document (a prose
  example above the heading is found and REWRITTEN by sign), and _place_signature can
  land outside every find_blocks range — while the parser only inspects those ranges.
  Fix: find/place are scoped to the find_blocks ranges exactly (a line outside is never
  an envelope — a match outside the ranges is REFUSED as a would-be forgery, not
  honored); sign never touches prose; covering tests for both directions. ALSO STD-R1's
  second half: plain `write` with no --key now exits 2 on such a doc — restore the
  frozen unsigned path's behavior (unsigned write must not change behavior vs the
  pre-feature inventory.py).
- **G-3 (M12 — two envelope lines: first wins).** Two lines matching SIGNATURE_LINE in
  one document → REFUSE (ambiguity is tampering), never first-wins. Killer test.
- **G-4 (M15 — a non-{record,sig_b64} envelope is treated as unsigned).** A line matching
  SIGNATURE_LINE whose payload is not the exact {record, sig_b64} shape → REFUSE
  (malformed envelope), never silently treated as unsigned. Killer test.
- **G-5 (STD-R2 — pubkey parse duplicated).** The pubkey parse lives in two places;
  move it into the shared enforcement_key() (U-SIG-1's helper) so the switch has exactly
  one implementation.

AUTONOMY:
- goal: all five items fixed on ravidsrk/sig-2; every Required from round 1 answered;
  the four surviving mutants (M12-M15) re-run and KILLED, quoted.
- scope: runtime/scripts/inventory.py + runtime/scripts/run_report.py +
  tests/test_inventory.py + tests/test_run_report.py + badge regen if counts move.
- non-goals: no new dependencies; no network; no change to the unsigned no-key path
  beyond restoring its frozen behavior; no other file; no PR action.
- stop: if a fix would weaken any existing refusal; if G-1 tempts changing the envelope
  format (it must not — the format is U-SIG-1's; the FIX is in validation).
- evidence: refreshed manifest at the new head (evidence-run receipts), the M12-M15
  re-runs RED-for-the-right-reason, full suite + validate green; lighting=lit.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

GIT: branch ravidsrk/sig-2 in this worktree (fetch; merge
origin/review/2026-09-20-sign-386 if moved — conflict → STOP). Author=maintainer, NO
TRAILERS. Small commits, stage only the unit's files. Leave the worktree clean.
Timebox 40min with partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`;
every send carries `--from <your handle> --dispatch-capability <capability>`; evidence
rides typed `--report-path` + `--files-modified`. Run `orca orchestration check
--terminal <your handle>` once before `worker_done` — `consumer_fenced` means STOP and
send nothing.
