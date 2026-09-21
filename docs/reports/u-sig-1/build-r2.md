# BUILD — U-SIG-1 round 2 (fix batch G-1..G-5)

Worker task_00e3a32df6df / ctx_6efd2af331c1 · branch ravidsrk/sig-1 · spec docs/runs/2026-09-20-sign-386/build-u-sig-1-r2.md
Base merged in first: origin/review/2026-09-20-sign-386 @ b1c7ad58 (clean merge 235dd2df). Pack: matt (RED-first, then green).
Started 2026-09-20 23:49 IST · report written 00:20 IST.

## Commits (head_sha of the re-recorded manifest = a9a4df32)

- c7b1a4de fix(run-report): ancestry-aware switch + signed args read + None-never-binds (G-1, G-2, G-4 half)
- 7a9db5a1 fix(verify): unwritten transcript is exit 1; in-process signer refuses an absence (G-5, G-4 half)
- a9a4df32 chore(badges): 1763 -> 1775
- (this commit) docs(runs): manifest re-recorded at a9a4df32 (G-3) + artifacts + this report

## G-1 — the fork-dodge (R-1 / F-1 / C3 / BOT-2)

Rule implemented in run_report.py (`grading_base`, `is_ancestor`, `key_rev`, `signed_transcript(..., base=None)`,
`check_report(..., base=None)`, CLI `--base`): the grading base is the default branch's current tip
(origin/HEAD → origin/main → origin/master → main → master → HEAD as last resort; `--base REV` overrides). A pin that is
an ancestor of it reads the key AT the pin — the grandfather lane's only door. A pin OFF that ancestry is judged
against the key at the grading base. Stop-clause check ("never weaken an existing refusal"): when the base carries no
key at all, an off-ancestry pin falls back to its own key, which is exactly today's read — so no refusal that exists
today is lost, and the dormant state (no key anywhere) is byte-identical. Both live self-run reports (clean-sweep
3ea81099, prove-it 4d451d88) are ancestors of origin/main and still bind (LiveCatalog green; run_report.py main = 0).

The three prose sites are rewritten to the true rule: run_report.py module doc, the SignedTranscriptRequired
docstring, docs/verify-gate.md (the dormancy pin's four phrases kept; test_orphan_wiring green). DECISIONS.md gets one
supersession line (2026-09-20T18:28:20Z · ask-msg_6d4bba0a00dc-Q2 · taste · superseded · …); the original Q2 line stays.
The unit manifest's own intent.why/ruled_out, which repeated the false premise, are corrected in the same re-record.

Tests (the TESTS axis's probes, as named): P2 test_a_report_pinned_before_the_key_landed_keeps_the_unsigned_path,
P3 test_a_pre_key_transcript_fails_closed_even_once_the_key_lands_later, P8
test_a_transcript_signed_after_the_pin_does_not_retro_sign_the_pinned_verdict, P4
test_post_key_work_pinned_to_a_pre_key_fork_is_refused, P5 test_a_dangling_pre_key_pin_is_refused_the_same_way, plus
test_an_off_ancestry_report_binds_with_a_transcript_signed_by_the_base_key and
test_a_pre_key_report_still_binds_when_the_base_is_named_explicitly. The fixture gained `_land()` (commit WITHOUT
re-pinning) so blob_at(rev) != blob_at(HEAD) is exercised; the fork helper asserts the pin is NOT an ancestor of main.

RED-first, quoted (before c7b1a4de): "FAILED (failures=3, errors=1)" — test_post_key_work_pinned_to_a_pre_key_fork_is_refused,
test_a_dangling_pre_key_pin_is_refused_the_same_way, test_an_off_ancestry_report_binds_with_a_transcript_signed_by_the_base_key
RED, test_a_pre_key_report_still_binds_when_the_base_is_named_explicitly ERROR (no grading_base). P2/P3/P8 pass on the
old code by design — they are the C3/C14 regression guards, killed below.

Mutants re-run against SignedTranscriptRequired after the fix (in-place edit, class run, file restored — diff -q clean):
- C3 `pin = blob_at("HEAD", PUBKEY_PIN, root)`: FAILED (failures=3) — RED: 
- C14 `raw = blob_at("HEAD", transcript, root)`: FAILED (failures=2) — RED: 
- ancestry check forced true (`if True or is_ancestor(...)`): FAILED (failures=3) — RED: 

## G-2 — the signed args tuple is read (F-2 / BOT-1)

signed_transcript() now (a) refuses a transcript whose `args` is missing/empty; (b) parses every
`verify.py … --manifest <m>` line the report body shows into verify.py's own flag shape (SIGNED_ARGS = _Transcript.ARGS,
switches execute_nc/no_gh) and refuses unless one line equals the signed tuple on every key the tuple carries; (c) refuses
`unit_class != mutation` when the mission is in evidence-manifest.md §3's mutation set (the in-repo oracle, #310).
RED-first quoted: "FAILED (failures=3)" — test_a_transcript_whose_signed_args_disagree_with_the_shown_invocation_is_refused,
test_a_transcript_signing_no_argument_tuple_is_refused, test_hostile_args_on_a_mutation_mission_are_refused_even_when_the_body_agrees (P1).
The fixture's default body invocation gained `--lighting lit` so the default verdict (args lighting=lit) agrees with it.

## G-3 — manifest re-record (F-3)

commands[]: the two round-1 receipts (commit 3e094f35, wtree c50693c7/1079ad63) dropped; `tests` re-recorded by evidence-run.py
on the clean checkout of a9a4df32 — wtree 7005bd0d == a9a4df32^{tree}; `negative-control` re-recorded (exit 1, reverted scratch
worktree). verify.py on the manifest now prints "NOTE: commands ledger FRESH — 1 exit-0 record(s) bound to head_sha's tree
7005bd0dacba" (round 1: "FAIL: commands ledger: no recorded command with exit 0 whose wtree is head_sha's tree"). The three
remaining FAIL lines are the contract flags and pr.number the integrator supplies, as in round 1.

## G-4 — absence never binds (R-2)

run_report: a manifest unreadable at the pin is its own problem; a transcript with manifest_sha256=None is refused ("signs no
manifest_sha256"); no None==None path remains. verify.py: _Transcript.write with a seed refuses any FIELDS value None
("signing an absence binds nothing (dispatch-sign.py refuses the same)") and writes nothing — one rule, two signers.
RED-first quoted: test_the_in_process_signer_refuses_to_sign_an_absence_like_the_offline_one — "'absence' not found in …".
Missing sig with the key present / missing key with a sig named were already refusals (round-1 tests, still green).

## G-5 — requested artifact unwritten is nonzero (R-3)

_Transcript.write returns whether the artifact exists; main() turns a green verdict into exit 1 when it does not (stderr names
it); a RED keeps its 2. Header comment updated. RED-first quoted: "AssertionError: 0 != 1 : verify: could not write transcript
docs/reports/u/blocked/transcript.json: [Errno 17] File exists". The test mocks verify() green (the honest way to reach exit 0
in the fixture) and checks the RED case keeps 2.

## Negative control (round 2, recorded)

Three production scripts restored from base 56d0f7c7 in a scratch worktree at a9a4df32, tests/docs kept, criterion command
`python3 -m unittest tests.test_dispatch_sign tests.test_verify tests.test_run_report tests.test_orphan_wiring tests.test_reshape_width_verify`
→ "Ran 501 tests … FAILED (failures=6, errors=27)": 33 RED = 21 round-1 + 11 of the 12 round-2 tests (the twelfth,
P2, passes at base by design — see manifest negative_control.not_witnessed_note). With the scripts: "Ran 501 tests … OK".
Artifacts: u-sig-1-negctrl.txt, u-sig-1-tests.txt (re-hashed in artifacts[]).

## Gates

- python3 scripts/validate.py → "All 21 missions valid; three-layer separation holds; evals valid." (badges regenerated 1763→1775)
- gitleaks detect → "no leaks found"
- decisions.py check → no complaint on the new line (pre-existing complaints on lines 65/72/73 are the coordinator's earlier records, untouched)
- full suite (python3 -m unittest discover -s tests, the CI runner) at a9a4df32 + this manifest: "Ran 1808 tests in 276.287s / OK" (round 1: 1796)

## Not done / notes for the integrator

- No PR action (integrator owns it). No new dependency, no network path, ed25519.py/_verify_sig.py untouched.
- Standards nits N-1..N-4, N-6 (alias width, FIELDS equality pin, dispatch-sign private loader, effective-vs-flag repo, exit-code
  header line) are NOT in the r2 spec's five items and were left alone; N-5 (verifier_ran's "not yet") was one line and is fixed.
- The C-args mutant I tried (`if False:` on the args guard) only removed the empty-tuple refusal, so it killed 1 test; the
  three G-2 tests' RED-first run is the discrimination evidence for the binding itself.
