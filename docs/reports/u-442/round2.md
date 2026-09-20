# U-442 round 2 — fix batch F-1..F-5

RUN: u-442 round 2 · head_sha `5113e1562abe09afa0b481a56dc01f2c3253cc8f` · tree `35c449f71cc69b0aae5ad362dbe32d50391ec471` · lighting=lit

Answers every Required from round 1 (SPEC R1/R2, TESTS T1–T5) and both held Greptile P1s.
Spec: `docs/runs/2026-09-20-clean-sweep-tracker/build-u442-r2.md`, frozen at dispatch.
Base `origin/review/2026-09-20-tracker-sweep` had moved to `5df4c0d8`; merged into u-442
with no conflict before any edit.

## The five items

| Item | Finding answered | Where |
|---|---|---|
| F-1 evidence authority | SPEC R1 · Greptile P1-1 · STANDARDS cross-repo substitution · TESTS T1 | `verify.py` `_roots_are_split()`, `_read_artifact` |
| F-2 every raw git read honors `--git-dir` | SPEC R2 · Greptile P1-2 · TESTS T5 | `verify.py` `check_symbol_on_base` (+ T5 regression on the already-rooted `path@ref` read) |
| F-3 `--evidence-root` honored, not just parsed | TESTS T2 | 2 regressions (distinct cwd, named subdirectory) |
| F-4 containment survives symlink spelling | TESTS T3 | 2 regressions (symlink escape, nested-root upward escape) |
| F-5 no-flag compatibility from a nested cwd | TESTS T4 | 1 regression |

**F-1.** The tracked-at-`head_sha` shortcut is a single-repo identity — *the file I resolved
IS the blob git tracks at that commit*. `_roots_are_split()` names when that identity holds.
Under a split the shortcut is unavailable and an artifact passes only on its declared
`artifacts[]` sha256 against bytes read from the **evidence** root; a same-path blob in the
SHA repo is never consulted. Two clones of one project count as split (same paths, different
roots). An unresolvable toplevel fails closed as split.

**F-2.** `check_symbol_on_base` ran `git grep` in the process cwd while the adjacent ancestry
check used `--git-dir` — a false refusal *and* a false acceptance, both covered. The raw-byte
`path@ref` read already routed through `_git_bytes`; T5's point was that nothing tested it, so
the regression (not a code change) is what closes it.

## Mutation matrix — the reviewers' own mutants, re-run

`python3 -m unittest discover -s tests -p test_verify.py`, one fresh process per mutant,
production file restored after each. Runner: `docs/reports/u-442/round2-mutants.json`.

| Mutant | Verdict | exit | result | killed by |
|---|---|---|---|---|
| `M1_evidence_from_sha_root` | KILLED | 1 | FAILED (failures=12) | `test_a_colliding_sha_repo_blob_cannot_satisfy_a_mismatched_pin`, `test_a_colliding_sha_repo_blob_cannot_substitute_for_pinned_evidence` … |
| `M2_ignore_evidence_root` | KILLED | 1 | FAILED (failures=2) | `test_a_nested_evidence_root_bounds_against_itself_not_the_clone`, `test_the_named_evidence_root_is_honored_from_a_distinct_cwd` |
| `M3_remove_canonical_containment` | KILLED | 1 | FAILED (failures=2) | `test_a_nested_evidence_root_bounds_against_itself_not_the_clone`, `test_an_evidence_path_escaping_through_a_symlink_is_refused` |
| `M4_no_flag_cwd_root` | KILLED | 1 | FAILED (failures=1) | `test_a_valid_no_flag_run_from_a_nested_directory_still_binds_to_the_toplevel` |
| `M5_git_bytes_ignore_sha_root` | KILLED | 1 | FAILED (failures=1) | `test_a_path_at_ref_contract_read_uses_the_sha_repo` |
| `M6_git_ignore_sha_root` | KILLED | 1 | FAILED (failures=8) | `test_a_colliding_sha_repo_blob_cannot_substitute_for_pinned_evidence`, `test_a_path_at_ref_contract_read_uses_the_sha_repo` … |
| `M7_drop_the_split_gate_on_the_tracked_blob_shortcut` | KILLED | 1 | FAILED (failures=4) | `test_a_colliding_sha_repo_blob_cannot_satisfy_a_mismatched_pin`, `test_a_colliding_sha_repo_blob_cannot_stand_in_for_a_missing_pin` … |
| `M8_symbol_grep_in_process_cwd` | KILLED | 1 | FAILED (failures=2) | `test_a_symbol_only_in_the_evidence_repo_is_not_accepted_as_on_base`, `test_the_symbol_leg_runs_in_the_sha_repo_not_the_process_cwd` |
| `M9_split_always_false` | KILLED | 1 | FAILED (failures=4) | `test_a_colliding_sha_repo_blob_cannot_satisfy_a_mismatched_pin`, `test_a_colliding_sha_repo_blob_cannot_stand_in_for_a_missing_pin` … |

M2–M5 are the four the tests review recorded as SURVIVOR; all four are now KILLED.
M7–M9 mutate this round's own fixes. **Zero survivors.**

## Gates at `5113e1562abe09afa0b481a56dc01f2c3253cc8f`

| Gate | Command | Result |
|---|---|---|
| Full suite | `python3 -m unittest discover -s tests` | exit 0 — Ran 1726 tests, OK |
| Validator | `python3 scripts/validate.py` | exit 0 — All 21 missions valid; three-layer separation holds; evals valid |
| Interface width | `tests/test_reshape_width_verify.py` | 90, pin raised 88 -> 90; baseline 92 untouched |

suite.txt sha256=de6ce375d051f6b38fd18bef8ad39952003cc5df92a713591676c83081c5f4a6

## Scope and what I did not do

Within the frozen scope: `runtime/scripts/verify.py`, `tests/test_verify.py`,
`tests/test_reshape_width_verify.py` (the interface width did move), a net-neutral
`runtime/evidence-manifest.md` note, and this evidence. Generated churn is two files
(`assets/badges/tests.json`, `docs/missions/floor-it.md`) — `validate.py` fails the build
on stale output, so the regen is demanded, not elective.

**The activation-load ratchet constrained the documentation.** Expanding the
evidence-manifest.md note pushed `clean-sweep` to ~34,059 tokens against a 34,000 cap; a
compressed version still measured ~34,024, then ~34,003. That cap is a ratchet and raising
it is a weakened gate, which the spec's stop condition forbids. The note was therefore
rewritten to carry the split-authority rule inside the existing sentence's byte budget
(+13 chars, load back under the cap). Worth a coordinator decision: the doc has roughly
five tokens of headroom, so the next behavioral note in any clean-sweep-mandatory runtime
doc has nowhere to go.

No PR action taken — the integrator owns that.
