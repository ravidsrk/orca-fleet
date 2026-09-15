# T9 — U387G: eval-glob holes (T6 regression + empty-glob semantics)

## Problem
Three Greptile threads on rollup PR #387, all verified live on BASE f66bd20:
- 4011878433 (prove-it) + 4011878440 (oncall-it): T6 (01d954e) replaced
  `**/*.py` with `tests/src/service/*.py` globs to scope venvs out — which
  opened false negatives for first-party code in `app/`, `lib/`, or any other
  package dir. A T6 regression; the right fix inverts T6 (broad positive +
  central exclusion), not broader whack-a-mole.
- 4011297664 (scripts/eval.py): a glob-based `not_matches` over an EMPTY match
  set vacuates to PASS (`any([])` is False → `not hit` is True). Whether an
  agent can pass a whole eval by deleting the globbed set depends on the
  eval's other (path-anchored) checks — surveyed + proven below, not assumed.

## Criteria
- C-1: `_glob_files` (scripts/eval.py) excludes dependency/tooling dirs by a
  DOCUMENTED denylist (finalize from a fixture survey; expected: venv,
  .venv, env, .env, virtualenv, site-packages, dist-packages, node_modules,
  .git, __pycache__); prove-it + oncall-it evals.json return to `**/*.py`
  coverage (one glob per check); survey EVERY mission's evals.json for
  T6-style narrow globs and broaden where fixtures warrant (list all surveyed
  missions + the broaden/keep verdict each in the manifest).
- C-2: delete-to-pass survey, committed as tests: for every eval with glob
  checks, a test deletes (or empties the matches of) the globbed set and
  asserts the eval STILL FAILS the workspace. Any eval that PASSES post-delete
  is RED: fix eval.py fail-closed (glob `matches`/`not_matches` over an empty
  set fails the check; the `exists` predicate keeps its semantics) until
  green. Evals already failing post-delete keep their test as a GUARD (U388
  C-2 precedent: sensitivity shown via mutant — neuter one anchoring path
  check and show the guard goes red).
- C-3: `python3 -m unittest discover -s tests` and `scripts/validate.py` green
  (validate.py checks evals validity — a broken evals.json fails the build).

## Negative control
`git checkout <base> -- scripts/eval.py skills/prove-it/evals/evals.json
skills/oncall-it/evals/evals.json` (revert production + evals, keep tests):
the C-1 tests fail (venv false-positive and/or app/ miss) and any C-2 red
evals fail; restore: green. Both directions quoted in u387g-negctrl.txt.

## Red-first
C-1 exploit tests first: a fixture workspace with (a) a venv dir containing
the banned pattern (must be IGNORED) and (b) an `app/` (+ `lib/`?) module
containing the banned pattern (must be CAUGHT) — RED on current narrow globs
(b-missed). C-2 delete tests next (red or guard per outcome above).

## Hot files (ONLY these + survey findings)
- `scripts/eval.py`
- `skills/prove-it/evals/evals.json`, `skills/oncall-it/evals/evals.json`
- other `skills/*/evals/evals.json` ONLY if the survey finds T6-style
  narrowing (each file justified in the manifest; default: untouched)
- `tests/test_evals.py`, `tests/eval_workspaces.json`
- `assets/badges/tests.json` (regen, own commit, only if the count moves)
- `docs/runs/2026-09-14-clean-sweep-tracker/u387g-manifest.json` (new)
- `docs/runs/2026-09-14-clean-sweep-tracker/u387g-negctrl.txt` (new)

## Out of scope
- Eval semantics beyond glob coverage (patterns, predicates, fixtures).
- New missions' evals; behavioral-runner grading.

## Worker protocol (run conventions)
- Ownership: ONLY the hot files above. Commit locally on your unit branch, one
  concern per commit (red tests / fix / badge / manifest). Do NOT push, merge,
  or touch BASE.
- Manifest: follow the u388-manifest.json schema. `contract.source` + `digest`
  are given in your TASK preamble. `head_sha` = your tip (coordinator re-binds
  at close). commands[] via WRAPPED runs on a clean tree.
- worker_done: three-sentence summary + explicit --outcome, tip SHA, quoted
  gate outputs + RED-first evidence, --files-modified, --report-path = manifest.
