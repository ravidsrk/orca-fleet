# WIRE + canaries + GUARD (floor-it unpark, phase 2)

Branch `floor/wire`, PR #468, base `origin/main` at 3773815a (phase-1 merge #466),
later merged up to a281c2c6 (reshape #464/#467). Worker: floor-wire-worker.
Method: `floor-it` WIRE + PROVE-FIRES + GUARD on the frozen CONSTRAINTS.md table —
row notes binding, implemented exactly as frozen.

HEADs: code cf7e2e61, P1 rename fix 990fb445, main-merge bba81298,
YAML fix 469eb38b, fixture fix fd45c837, guard.yml P1 fix a99cf03c.

## 1. WIRE — every enforced dimension as a CI gate

D1–D8 needed no new steps: each frozen command was already the CI step in
`.github/workflows/validate.yml`, verified command-for-command against the
freeze. D9 is the one new step. D9's number was never touched (fail_under
stands at the frozen 80, ratchet-only); the tree was lifted to it instead.

| Dim | Frozen command | CI step | Status |
|---|---|---|---|
| D1 | `python3 -m unittest discover -s tests` | gates: suite | pre-existing, green (1684) |
| D2 | `python3 scripts/validate.py` | gates: validate | pre-existing, green |
| D3 | `ruff check scripts runtime/scripts tests bench demo` | gates: ruff | pre-existing, green (0.16.7 both sides) |
| D4 | `gitleaks detect --redact --no-banner --source .` (8.30.1 + self-test) | gates: secret scan | pre-existing, green |
| D5 | `python3 scripts/eval.py run --suite routing --threshold 1.0` | gates: eval | pre-existing, green (94/94) |
| D6a | `python3 runtime/scripts/proof_status.py --check` | gates: proof status | pre-existing, green |
| D6b | `python3 runtime/scripts/run_report.py` | gates: run report | pre-existing, green |
| D7 | `python3 scripts/bundle.py --check` | gates: bundle | pre-existing, green |
| D8 | `python3 bench/vf-bench/gate.py` | vfbench job | pre-existing, green |
| D9 | `coverage run -m unittest discover -s tests` + `coverage report` | gates: Coverage floor (NEW) | wired by this phase, green 81% |

D3 row-note skew resolved: local ruff and the lock both read 0.16.7, so the
note's "keeps the versions aligned" alternative holds with no recorded skew.
D9 row-note install honored: coverage==7.16.1 (the measurement line) joined
`.github/ci-tools.lock` by a spliced single-package `uv pip compile`
(all 121 hashes, mechanical — never hand-written) plus `PINNED`, proven by a
clean-venv `--require-hashes` install where all three console scripts run.

## 2. D9 lift — 74% to 81% with real tests, no exclusions

Baseline on the phase-1 tree: 6151 statements, 1593 missed, 74% (exit 2).
Final: 6267 statements, 1167 missed in CI (1168 locally — one line of
darwin/linux variance), 81% (exit 0). No `fail_under` edit, no new excludes,
no pragma, no vacuous tests. Four modules, all covered by in-process tests
that call the same entry points the subprocess suites drive:

- `decisions.py` 18% -> 100%: parse/format round-trips, every validate
  refusal, door loading failures, ordering/tiebreak math, all four commands
  through `main(argv)`, exit-2 paths, the module entry point.
- `floor_guard.py` 32% -> 100%: `main()` in-process over hermetic repos
  (clean/quiet/violation/waived/malformed/exit-2s), `scan()` per rule,
  diff parsing, waiver scope edge cases, base resolution incl. a real
  bare-origin origin/HEAD preference proof, the module entry point.
- `guard_text.py` 0% -> 100%: every detector family, evasion folds,
  envelope/banner behavior, fetch failures incl. timeout, `main()` paths.
- `verdict_check.py` 41% -> 99% (100% with the entry test): API paging,
  payload shapes, every CLI verdict, usage errors.

Denominator honesty, two finds: (a) the committed `.coveragerc` is what
scopes the report — deleting it (as one careless glob did mid-run, instantly
restored) un-scopes to a false 91%; (b) `guard_text.py` (84 statements) never
appears until a config-scoped collection counts it — the phase-1 75% silently
omitted it. Both are in the final number now.

Census 1684 (1665 wire tests + reshape's), badges regenerated twice (the
second for the main-merge; the one merge conflict was the generated file).

## 3. GUARD — the `guard-surface` rule + the floor-guard workflow

`floor_guard.py` gains the sixth rule for the Q4-frozen surface, exactly the
frozen list: whole files (any added/removed line trips) are `.gitleaksignore`,
`evals/routing.json`, vf-bench `VERSION`/`CANARY`/`traps/`; keyed files trip on
the key's assignment only — the ruff `select`, the `.coveragerc` fail_under,
`ROUTING_MIN_SCORE` in `tests/test_evals.py`, the three `EXPECTED_*` pins in
`bench/vf-bench/gate.py`. Assignment-only (not bare-mention) matching keeps
use-sites, comments, docs, and the guard's own source silent; matching is
path-gated throughout. Waivers are the frozen
`floor-waiver:<rule>:<path>` DECISIONS grants (existing machinery, new rule id).

Wired as `.github/workflows/guard.yml`: PR-only (a push has no base to diff),
`--base` from the PR's own base ref via a quoted env var (see P1-2 below),
same checkout depth convention as bind-check. Composes with verdict-check;
duplicates nothing. Guard is clean on this branch's own diff and green on
every non-guard canary (no false positives); red only where it should be.

Review P1-1 (Greptile 4031574743, answered in-thread): content-preserving
renames rendered as metadata with no content lines, so renaming `.coveragerc`
sideways evaded the guard. Fixed in 990fb445 — `collect_diff` passes
`--no-renames`, so a rename reads as the delete+add it is and the removed half
trips. Regression test covers a whole-file and a keyed rename; proven to fail
2/2 on the pre-fix code and pass fixed.

Review P1-2 (Greptile 4031782359, answered in-thread): the base ref was
interpolated inline and unquoted — a hostile branch name is script injection.
Fixed in a99cf03c via quoted env. Same pattern pre-exists in bind-check.yml:27
(not this PR's scope; flagged for a separate ticket in the reply).

## 4. PROVE-FIRES — eleven canary PRs, all RED, all closed unmerged

One canary PR per gate, each carrying exactly one deliberate violation,
branched off `floor/wire`, opened against it, CI run to RED, then closed
unmerged with the branch deleted (local and origin — verified no canary refs
remain). D4's fake credential was random hex in the waived file itself, never
recorded contiguously anywhere kept, branch destroyed right after its proof.

| Gate | PR | Head | RED run | Failing check |
|---|---|---|---|---|
| D1 | #469 | 0767f960 | 35164036054 | suite: exactly 1/1684 (the flip) |
| D2 | #470 | 515e237c | 35164039567 | validate: layer separation |
| D3 | #471 | e53f55eb | 35164043828 | Ruff: F821 (suite green) |
| D4 | #472 | 01f33a60 | 35163543630 | secret scan: leaks found 1, attributed |
| D5 | #473 | ee40941b | 35164046129 | suite: 3 test_evals fails (eval step shadowed; local eval on head exits 1 at 97%) |
| D6a | #474 | cf0570c7 | 35164049363 | validate binding cross-fire (proof_status shadowed; local exit 1) |
| D6b | #475 | 039a6a4a | 35164053372 | validate binding cross-fire (run_report shadowed; local exit 1) |
| D7 | #476 | 9f32daa9 | 35164058630 | validate reference cross-fire (bundle shadowed; local exit 1) |
| D8 | #477 | 8788b14c | 35164059899 | vfbench job: false-done 1/20 (+ 6 suite cross-fires) |
| D9 | #478 | 5d687755 | 35164063873 | Coverage floor: TOTAL 77% < 80, all else green |
| GUARD | #479 | 2838ec6e | guard 35164067907 | 2 guard-surface violations (validate cross-fire: 1 margin fail) |

Direct step/job proof for D1, D2, D3, D4, D8, D9, GUARD. D5/D6a/D6b/D7 are
structurally shadowed: the gates job is sequential fail-fast, and each of
those injections trips an earlier gate (suite for D5, validate for the rest)
before its own step executes. Their CI-RED is real, and each shadowed step's
own frozen command was re-run locally on the exact recorded head SHA with
exit != 0 (`transcripts/canary-*.txt` carry both halves). Those four steps
are long-standing CI steps running byte-identical commands — nothing about
the step path is new; only the injection is.

## 5. Incidents (all closed)

- Invalid workflow YAML killed dispatch, not an event drop. The D9 step name
  carried an unquoted `D9: ...` colon; GitHub silently scheduled zero
  `pull_request` runs for validate on every WIRE branch (the 0-job push runs
  were the tell). Fixed by quoting (469eb38b); dispatch confirmed on the next
  push. Lesson recorded: parse every touched workflow with a strict YAML
  loader before pushing.
- Fixture read ambient git config. `test_origin_head_wins_over_the_local_branch`
  built its seed clone on the ambient default branch (main locally, master on
  the runner) and failed only in CI. Reproduced locally by forcing master,
  fixed by pinning every fixture branch name (fd45c837), verified under both
  defaults. All canaries were rebased onto the fix and re-run.
- Gitleaks scans all refs, so the live D4 canary briefly poisoned every
  PR's secret-scan step (including #468's). Confirmed by attribution (the one
  leak was the canary commit on its own branch), sequenced around it (D4 ran
  first, alone; branch deleted immediately after its proof), and the final
  #468 run scans clean. The property matches the freeze row note's warning.

## 6. Evidence

`manifest.json`: 12 GREEN records bound to this branch (suite, coverage
run+report, validate, ruff, routing, proof-status, run-report, bundle,
vfbench, guard-clean, gitleaks). `transcripts/`: the 12 green artifacts plus
11 `canary-*-red.txt` receipts (PR + head + run URL + failing check +
excerpt). #468's own CI: run 35164493361 fully green (gates 8m22s incl. the
new coverage step at 81%, guard, vfbench). Suite 1684 green, validate.py
green, badges current, no new dependencies. floor-it stays doctrine-only —
this directory is run evidence for the coordinator, not a tier claim.
