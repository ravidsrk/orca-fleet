# PROVE-FIRES — floor-it CONSTRAINTS phase 1 (2026-09-16)

Every enforced dimension of CONSTRAINTS.md was demonstrated RED on a real
violation and GREEN after revert, by execution. Each section below names the
constraint, the injection, the RED verdict, the GREEN verdict, observed
cross-fires, and the archived transcripts. Injection diffs are archived beside
the transcripts so any proof replays: apply the diff on a throwaway branch off
the base, run the command, watch it go RED.

- Base: `10e45f72` (origin/main at phase start). All injections were committed
  on throwaway branches (`floor/canary-*`, since deleted) or in throwaway
  `/tmp` clones (destroyed); nothing foreign was ever committed to
  `floor/constraints`. Reverts were verified by empty diff against the base.
- Method honesty notes: (1) the D4 canary is a credential-SHAPED fake
  assembled at runtime ( halves `AKIA` + `ZYXWVUTSRQPONMLK`, never the
  contiguous literal in any repo file — the same discipline as the CI secret
  scan it mirrors), planted only in a `/tmp` clone that was destroyed after.
  (2) No D4 injection diff is archived, by design: the recipe below replaces
  it. (3) Exit codes were captured with `pipefail`; piped `tail` exits lied
  once during this run (D4 baseline) and were re-verified.
- The manifest.json in this directory binds the GREEN-side re-executions on
  the finished branch (evidence-run records). RED transcripts live in
  transcripts/ with the injection commits named (branches deleted after use).
  Provenance note: the recorder was first invoked with run-dir-relative
  artifact paths, which it resolved against the repo root; the files were
  moved into transcripts/ and the manifest's artifact pointers repointed to
  repo-root-relative form (campaign convention). Commands, exits, timestamps,
  and commit/wtree bindings are the recorder's untouched bytes; only the
  pointer spelling was normalized, and every pointer was verified to resolve.

## D1 suite-green — `python3 -m unittest discover -s tests`, exit 0

- Injection: one-assertion flip in tests/test_pins.py (expected `[]`, demanded
  `["FLOOR-CANARY-D1"]`). Census-stable: 1490 tests before and after.
- RED: `Ran 1490 tests, FAILED (failures=1)` — exactly the flipped test —
  exit 1. Transcripts: d1-red.txt, d1-injection.diff.
- GREEN after revert: `Ran 1490 tests, OK`, exit 0. Transcript: d1-green.txt.
- Footnote: a first variant (new failing test FILE) also went RED but with
  failures=3 — the census change tripped badge freshness too. It was discarded
  for the crisper single-cause proof above.

## D2 catalog-valid — `python3 scripts/validate.py`, exit 0

- Injection: playbooks/zz-canary/SKILL.md (three-layer violation).
- RED: exit 1 — `FAIL layer separation — SKILL.md found outside skills/`.
  Transcripts: d2-red.txt, d2-injection.diff.
- GREEN after revert: exit 0, `21/21 missions valid`. Transcript: d2-green.txt.
- Cross-fires: none among the fast gates (bundle, eval, ruff, proof_status,
  run_report, vf-bench all stayed GREEN — d2-crossfire.txt). D1 WOULD go RED:
  tests.test_architecture fails 3 tests on this injection (d2-crossfire-d1.txt),
  while tests.test_validate stays green (fixture-based, not repo-based).

## D3 lint-clean — `ruff check scripts runtime/scripts tests bench demo`, 0 findings

- Injection: scripts/floor_canary_d3.py returning an undefined name (F821).
- RED: exit 1 — `F821 Undefined name`, 1 error. d3-red.txt, d3-injection.diff.
- GREEN after revert: exit 0, `All checks passed!`. d3-green.txt.
- Cross-fires: none (validate, bundle, eval GREEN; test_repo_hygiene GREEN —
  d3-crossfire.txt, d3-crossfire-d1.txt). A pure single-gate fire.

## D4 secrets-clean — `gitleaks detect --redact --no-banner --source .`, 0 unwaived leaks

- Injection (throwaway `/tmp` clone only, destroyed after): the CI canary
  recipe — `printf 'CANARY = "%s%s"\n' 'AKIA' 'ZYXWVUTSRQPONMLK'` appended to
  tests/test_decisions.py (the `.gitleaksignore`-waived file itself), committed.
- RED: exit 1, `leaks found: 7` (6 pre-existing unmerged-campaign findings + 1
  canary). Verbose output attributes the new finding to the canary commit in
  tests/test_decisions.py — the ignore file waives only its 3 listed
  fingerprints, not the file. d4-red.txt, d4-red-verbose.txt.
- GREEN: exit 0 in a main-history-only clone (d4-green.txt), corroborated by
  CI validate success on main. No contiguous canary literal exists in any
  archived file (verified by scan before commit).
- History-scan semantics (learned the hard way): a revert commit does NOT
  restore GREEN for a history scanner — the canary commit stays in history.
  The GREEN side is therefore the never-touched tree, and the canary branch
  was destroyed, not reverted. Related artifact: a shared-checkout worktree
  scans unpushed campaign refs too (d4-worktree-allrefs.txt, exit 1 on 6
  harden-it campaign findings NOT on main) — that is ambient-state noise, not
  the gate signal. CI scans origin refs only and is green.

## D5 routing-eval — `eval.py run --suite routing --threshold 1.0`, score >= 1.0

- Injection: deflake-it description neutered (trigger vocabulary removed;
  `Use when` + length kept so the frontmatter stays schema-valid).
- RED: exit 1 — `Routing eval: 86/94 correct (91%)`, below threshold.
  d5-red.txt, d5-injection.diff.
- GREEN after revert: exit 0, 94/94. d5-green.txt.
- Cross-fires: validate ALSO fires (eval-schema coverage + badge freshness —
  d5-crossfire.txt); bundle stays GREEN. D1 WOULD go RED: tests.test_evals
  fails 6 tests (d5-crossfire-d1.txt). Layered defense, all observed.

## D6 proof-honesty — `proof_status.py --check` AND `run_report.py`, both exit 0

Two halves, each proven separately.

- D6a injection: review-it frontmatter flipped to `proof: self-run` with
  `proof_evidence: docs/runs/zz-canary-missing.md` (nonexistent).
- D6a RED: exit 1 — `FAIL: review-it (self-run) — unresolvable
  proof_evidence`. d6a-red.txt, d6a-injection.diff.
- D6a GREEN after revert: exit 0. d6a-green.txt.
- D6a cross-fires: validate AND run_report also fire (d6a-crossfire.txt);
  eval stays GREEN. D1 WOULD go RED via tests.test_architecture
  (d6a-crossfire-d1.txt).
- D6b injection: one hex char flipped in the run-close integrity inventory of
  the bound report docs/runs/2026-09-16-prove-it-self-run.md (manifest row).
- D6b RED: exit 1 — `FAIL prove-it (self-run)`, recorded-vs-actual mismatch
  on the graded manifest. d6b-red.txt, d6b-injection.diff.
- D6b GREEN after revert: exit 0. d6b-green.txt.
- D6b cross-fires: validate fires (it embeds the binding check); proof_status
  stays GREEN (the file still resolves — the halves are complementary, not
  redundant). d6b-crossfire.txt.
- D6b footnote (no false-positive): appending a benign line to the same bound
  report does NOT trip run_report — the gate re-hashes git objects at
  `inventory_at`, not the worktree. Tried first, stayed green, reverted.

## D7 bundle-self-contained — `python3 scripts/bundle.py --check`, exit 0

- Injection: outbound link `[canary spec](../../canary-missing-target.md)`
  appended to skills/review-it/SKILL.md.
- RED: exit 1 — `references/canary-missing-target.md was not vendored` +
  dead-link FAIL. d7-red.txt, d7-injection.diff.
- GREEN after revert: exit 0, 21 self-contained. d7-green.txt.
- Cross-fires: validate ALSO fires (reference resolution); eval stays GREEN.
  d7-crossfire.txt.

## D8 verifier-soundness — `python3 bench/vf-bench/gate.py`, false-done 0 + skipped 0

- Injection: one review leg neutered in runtime/scripts/verify.py (the
  no-pr.number check returns `[]` instead of failing).
- RED: exit 2 — `GATE FAIL: verify.py false-done is 1/20`. Per-trap re-score
  attributes the flip to exactly `unreviewed-mutation-1`; valid controls stay
  3/3 (the gate names the hole — it is not always-RED). d8-red.txt (with
  attribution appendix), d8-injection.diff.
- GREEN after revert: exit 0 — `false-done 0/20, valid 3/3, skipped 0`.
  d8-green.txt.
- Cross-fires: ruff + validate stay GREEN (d8-crossfire.txt). D1 WOULD go RED:
  tests.test_verify fails 2 tests (d8-crossfire-d1.txt).

## D9 coverage — line >= 80% on runtime/scripts + scripts (ratchet-only)

- No code injection: the tree at base IS the violation. Measured 75% (6058
  statements, 1541 missed) three times with coverage 7.16.1, default line
  coverage, full suite green each time (1490 OK).
- RED: the frozen gate `coverage report --fail-under=80` (scope
  scripts/* + runtime/scripts/*) exits 2 — `Coverage failure: total of 75 is
  less than fail-under=80`. d9-red.txt, d9-report.txt (per-file), d9-suite.log.
- Config validation: the committed .coveragerc reproduces the verdict with a
  bare `coverage report` (TOTAL 75%, exit 2, zero out-of-scope rows) — same
  data, recorded in d9-red.txt. A draft with `[run] source` alone leaked
  bench/tests/demo rows into the report (91% — a false GREEN shape); the
  `[report] include` closes that hole. Verified, not assumed.
- Discrimination probe (NOT the frozen gate): the same data passes at
  `--fail-under=75` (exit 0) — the tool is not always-RED. d9-probe.txt.
- GREEN: OWED to the WIRE unit (see below). Freezing below the bar was the
  human's explicit call against an unmeasured dimension; this phase records
  the gap instead of editing the number.

## Fires-proof matrix (all exits executed, pipefail-captured)

| Dim | RED exit | RED signal | GREEN exit | GREEN signal |
|---|---|---|---|---|
| D1 | 1 | 1490 tests, failures=1 (the flip) | 0 | 1490 OK |
| D2 | 1 | FAIL layer separation, names the file | 0 | 21/21 valid |
| D3 | 1 | F821, 1 error | 0 | All checks passed |
| D4 | 1 | leaks 7 (6 ambient + 1 canary, attributed) | 0 | main-history-only, 0 leaks |
| D5 | 1 | 86/94 (91%) < 100% | 0 | 94/94 |
| D6a | 1 | FAIL review-it, unresolvable evidence | 0 | 19 doctrine / 2 self-run |
| D6b | 1 | FAIL prove-it, inventory mismatch | 0 | 2 bound |
| D7 | 1 | dead link, not vendored | 0 | 21 self-contained |
| D8 | 2 | false-done 1/20, trap attributed | 0 | 0/20, 3/3 valid, 0 skipped |
| D9 | 2 | 75 < 80 fail-under | — | OWED: WIRE lifts to >= 80, then re-proves |

## What WIRE needs (per the delegation: CI wiring is a later phase)

1. Nothing in this branch touches .github/workflows (verified: `git status`
   shows no workflow edits). The D1–D8 CI steps already exist in validate.yml;
   WIRE's job there is the canary-PR RED proof per gate (one PR per gate
   carrying its injection, CI must go RED, closed unmerged), not new steps.
2. D9 needs a NEW CI step: hash-pinned coverage install (extend
   .github/ci-tools.lock — hashed, per the #301 discipline), then
   `coverage run -m unittest discover -s tests` + `coverage report` on the
   committed .coveragerc. Coverage 7.16.1 was used for measurement; WIRE pins
   deliberately (7.16.x line recommended, exact pin + hashes at wire time).
3. D9 needs real tests lifting 75% to >= 80% BEFORE its CI step can land
   green. Lowest-hanging files (see d9-report.txt): the long tail under
   runtime/scripts (e.g. decisions.py 18%, evidence-run.py 40%, egress.py
   52%, diff_scope.py 57%) versus the already-strong scripts/validate.py 78%,
   scripts/eval.py 80%. Lift-then-wire, in that order — landing the step red
   is not an option, and lowering the number is a one-way human call.
4. GUARD phase input: the guard must cover the `.coveragerc` fail_under
   (mirrors the frozen D9 number) alongside the Q4-confirmed surface.
5. Environment note for WIRE: local ruff is 0.16.7, CI pins 0.16.5 — align or
   record. Local gitleaks 8.30.1 matches the CI pin exactly.
