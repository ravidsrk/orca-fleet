# U-442 — ROUND 3 (FINAL) fix batch

Head: `cd07307e93a6c0bd7a30299aa89411a18417ac72` (implementation) · evidence commits follow it.
Base: `a58bf71a283928a8278e560163452ee70c7ad609` · BASE merged at `81c8772a` (docs/runs only, clean).
Suite: 1733 tests, exit 0 · `scripts/validate.py` exit 0 · 15 mutants, 0 survivors · lighting=lit.

Answers every round-2 Required: SPEC S2-R1/R2/R3 and TESTS R2-T1/T2/T3, plus the CI guard hold.

## H-1 + H-5 — the F-4 escape fixtures are PINNED and otherwise valid

`test_an_evidence_path_escaping_through_a_symlink_is_refused` and
`test_a_nested_evidence_root_bounds_against_itself_not_the_clone` now pin BOTH the ordinary
artifact and the escaping path they actually name, over otherwise-valid evidence. The nested
fixture owns its selected-root contract and its ordinary command artifact, so the manifest is
refused for the escape and nothing else — asserted, not assumed (`assertNotIn("unpinned
evidence")`, `assertNotIn("contract unreadable")`).

That is what kills **N5** (`if err and "escapes" in err and path in artifact_inventory(m)` →
resolve anyway): a declared inventory pin cannot authorize an escape. A pin says WHICH bytes,
never WHERE they may live. Unpinned, both fixtures were refused for the missing pin and the
containment bound was never the thing on trial.

## H-4 — one-flag collisions and same-repo nested evidence (R2-T1)

Three regressions pin the root classifier:

- `test_only_git_flag_collision_still_requires_pin` — invoked from A with only `--git-dir B`.
- `test_only_evidence_flag_collision_still_requires_pin` — invoked from B with only
  `--evidence-root A`.
- `test_same_repo_nested_evidence_cannot_borrow_root_blob` — SHAs and a nested evidence root in
  ONE clone; repository identity is not ROOT identity.

Each plants a valid-looking colliding blob at the evidence artifact's own relative path in the
SHA repo and drops `artifacts[]`. All three must be REFUSED. **N1** (`and` → `or`) and **N2**
(resolve the evidence root back to its enclosing repository) both die.

## H-6 — the symbol check pins `origin/<base>`, not HEAD (R2-T3)

`test_symbol_only_on_head_cannot_substitute_for_base` (symbol on a later local HEAD only → must
NOT satisfy) and `test_symbol_only_on_base_is_found_even_when_head_deleted_it` (symbol on
`origin/main`, deleted by a later local commit → MUST still be found). **N4** (grep ref → `HEAD`)
fails the first as a false acceptance and the second as a false rejection.

## H-3 — the legacy 20s symbol-grep budget, restored (S2-R3)

`check_symbol_on_base` moved onto `_git` for the SHA root and inherited its 10s default; the
`_run` call it replaced allowed 20s. A grep taking 11s turned a symbol that IS on base into a
fatal miss — with both new flags ABSENT, which is the invocation the unit promised to leave
byte-identical. The clock is now passed explicitly at the call site.

Not a named constant: verify.py's interface WIDTH is a ratchet with two slots left before the
pre-deepening baseline of 92, and a timeout is not an interface. The 11-second boundary is not
assertable in a suite that must stay fast, so what is pinned instead is the VALUE reaching
subprocess: `test_the_symbol_grep_keeps_the_legacy_twenty_second_budget` reads it off a recording
`_run` and compares it to `_run`'s own default, asserting it differs from `_git`'s. **N6**
(drop `timeout=20`) dies.

## H-7 — the pragma is gone; the two quotations are not the worker's to waive

`runtime/scripts/verify.py:209` carried a coverage-exemption pragma on the `OSError` leg of
`_roots_are_split`. The branch is COVERED, not waived:
`test_an_unresolvable_root_fails_closed_to_split` makes `Path.resolve` raise `ELOOP` and asserts
the classifier answers True. **N7** (fail open) dies. The guard no longer names verify.py.

**The guard is not green.** Seven archival-quotation violations remain, all in report/run prose
that QUOTES the pragma string (this report deliberately does not, so it does not lengthen the list) — and two of them are paths the frozen batch did not name:

| path | in the frozen H-7 list |
|---|---|
| `docs/reports/u-442/verdict-r2.json` (×4) | yes |
| `docs/reports/u-442/verdict-review-r2.md` | yes |
| `docs/reports/u-442/integrate-r2.json:131` | **no** |
| `docs/runs/.../build-u442-r3.md:40` | **no** — the round-3 spec itself, arrived on BASE |

H-7 assigns those DECISIONS floor-waivers (archival-quotation class, 2026-09-17 precedent) to the
coordinator; none is recorded yet, and a worker faking a governance decision is the one thing this
fleet never does. The code half is done and verified; the waiver half is open, and its list is two
entries longer than the frozen batch expected.

## H-2 — the manifest, re-bound (S2-R2)

`docs/reports/u-442/manifest.json` was still the round-1 artifact: `head_sha 1ef8bd79`, an exit-1
full-suite receipt, `AC-3 addressed:false`. Re-emitted at `cd07307e`:

| receipt | exit | wtree |
|---|---|---|
| `tests` (`test_verify`, 274) | 0 | `eff64964…` |
| `unit-scope-tests` (`CrossRepoRoots`, 27) | 0 | `eff64964…` |
| `validate` | 0 | `eff64964…` |
| `full-suite` (1733) | 0 | `eff64964…` |

Every `wtree` is exactly `git rev-parse cd07307e^{tree}`. Each receipt ran in its OWN fresh
worktree at head_sha with the manifest written outside it, so the fingerprint describes the
content the command was given and not that content plus the wrapper's own writes — the failure
mode that makes a second receipt in one tree stale. `verify.py` reads the ledger FRESH
(`selfcheck-r3.txt`). All four criteria addressed; intent refreshed; `artifacts[]` pins the
round-2 and round-3 report files.

The negative control is re-derived at this head, not inherited: GREEN 27/27 at `cd07307e`
(`nc-green.txt`), then `git checkout a58bf71a -- runtime/scripts/verify.py` → exit 1, 24 assertion
failures and 1 error (`nc-red.txt`). The single error is honest for a BASE revert rather than a
behavioural mutant: at base there is no `_ROOTS` at all, so the fail-closed-classifier test cannot
reach an assertion. The behavioural controls that keep the flags present are the 15 mutants, all
assertion kills.

## Mutants — 15 run, 15 KILLED, 0 survivors

`round2-replay-r3.json` (round 2's nine, re-run against the moved test surface) and
`round3-mutants.json` (N1, N2, N4, N5, N6, N7). All exit 1 with assertion failures only — no
stillborn setup or import errors.

M8's anchor was re-expressed: the H-3 fix added `timeout=20` to the line that mutant replaces, so
the round-2 `before` string no longer occurs at this head. The mutation itself is unchanged (the
symbol grep runs in the process cwd) and it still dies, now on three tests rather than two.

## Scope

`runtime/scripts/verify.py` (one call-site timeout, one pragma deleted), `tests/test_verify.py`
(two fixtures upgraded, seven regressions added, `inspect` imported),
`assets/badges/tests.json` (1726 → 1733, validator-mandatory), `docs/reports/u-442/*`. No new
flags, no behaviour change beyond H-3's restoration, no PR action.
