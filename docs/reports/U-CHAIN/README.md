# U-CHAIN — evidence (issues #441, #443, #444)

Unit of the 2026-09-20 clean-sweep tracker run (`docs/runs/2026-09-20-clean-sweep-tracker.md`),
frozen specs `docs/runs/2026-09-20-clean-sweep-tracker/build-u-chain.md` (round 1) and
`build-u-chain-r2.md` (round 2 fix batch).

**Round 2 is the live record.** Round 1 was reviewed NO-GO on all three axes
([spec](review-spec.txt), [standards](review-standards.txt), [tests](review-tests.txt)); the six
fix items F-1 … F-6 and their receipts are in [manifest.json](manifest.json). The round-1 figures
below are kept for comparison.

| | round 1 | round 2 |
|---|---|---|
| base_sha | `a58bf71a283928a8278e560163452ee70c7ad609` | `ed51fe11de5f7329ecf02ffb933bf50648ae5654` (BASE `review/2026-09-20-tracker-sweep`, merged in as `1066c028`) |
| head_sha | `315ad409097b378b3d342d5144322d0f92d0d119` | `88a64c902ea1cd2ab0e3040781f918bb8daaefc6` |
| policy | 77 lines | 89 lines (cap 160) |
| full suite | 1707 tests, 5 RED (also RED at base) | **1707 tests, OK, exit 0** |
| mutants | 4 killed, **6 survivors** | **13 killed, 0 survivors** ([mutants-r2.txt](mutants-r2.txt)) |

| | |
|---|---|
| branch | `ravidsrk/u-chain` (coordinator-directed: `u-chain` was held by a residual worktree) |
| class | mutation unit, doctrine (prose + one contract test) |
| manifest | [manifest.json](manifest.json) |

## What changed

`runtime/mission-chaining.md` 40 → 77 lines (runtime cap 160), three clauses inside the existing
chain contract — one per finding, no restructuring:

- **#441** — chains are human-paced at every link boundary, and the wait is named
  `PARKED-AT-PROMOTION`: a CHAIN state in the ledger header, not a mission terminal, resumed only
  by a landed promotion SHA or a written BASE-carry grant.
- **#443** — the deferral carry gets one shape, the **handoff log** (one file per chain, carry
  table + gate record), with an absent log read as an unfinished chain rather than an empty one.
  The shape is the #417 chaining run's own proposal, linked as the worked exemplar.
- **#444** — a leg whose target has no remote cannot be re-derived from cited SHAs, so the chain
  must publish the bytes: a pushed mirror, or embedded reconstruction artifacts hashed into the
  run-close integrity inventory.

One contract test, `tests/test_architecture.py::TestArchitecture::test_chain_link_boundary_is_specified`,
asserts each property **inside one bullet** rather than anywhere in the file — the gap was a missing
rule, not a missing word, and a file-wide `assertIn` would stay green against sprinkled vocabulary.

## Acceptance criteria

| | criterion | result |
|---|---|---|
| AC-1 | contract test RED at base, GREEN at head | MET — [negctrl.txt](negctrl.txt), [contract-test.txt](contract-test.txt) |
| AC-2 | `validate.py` exit 0 at head | MET — [validate.txt](validate.txt) |
| AC-3 | full suite green at head | **NOT MET** — see below |
| AC-4 | negative control executed | MET — [negctrl.txt](negctrl.txt) + [negctrl-per-criterion.txt](negctrl-per-criterion.txt) |
| AC-5 | `mission-chaining.md` ≤ 160 lines | MET — 77 |

## AC-3: the suite is red, and it was red before this unit

`python3 -m unittest discover -s tests` at head: **1707 tests, 5 failures**
([suite.txt](suite.txt)). The identical 5 fail at `base_sha` in a throwaway worktree
([prered-base.txt](prered-base.txt)) — the failing sets are byte-identical:

```
test_docs_navigation.ReleaseCutWalkthrough.test_next_release_preparation_cut_tag_and_provenance
test_docs_navigation.ReleaseRehearsalIsolation.test_inherited_git_selection_cannot_mutate_another_repository
test_docs_navigation.TestDocsNavigation.test_run_archive_index_lists_every_report
test_docs_navigation.TestDocsNavigation.test_run_archive_integrity_standard_matches_practice
test_wire_docs.WiringScriptAnchors.test_the_committed_docs_are_the_scripts_fixed_point
```

Both causes are the run's own STABILIZE commits, not this unit:

- `296f100b` added `docs/runs/2026-09-20-clean-sweep-tracker.md` without a row in the run-archive
  index — `AssertionError: '(2026-09-20-clean-sweep-tracker.md)' not found in ...`.
- `3833c88e` left `README.md` off the wiring script's fixed point —
  `'would wire README.md: img 15->15, picture blocks 10'`.

Fixing either means editing `docs/runs/README.md` / `README.md`, outside this unit's scope and
forbidden by its stop rule. **Parked for the coordinator**: AC-3 is satisfied only in the
"no new red" sense. Nothing here was skipped for convenience.

## Negative control

Executed, in a throwaway worktree at `head_sha`, tool `revert` — plus a stronger per-criterion
pass, tool `hand`:

1. **Whole amendment** — `git checkout <base_sha> -- runtime/mission-chaining.md` (37 lines
   removed, the test kept) → the contract test exits **1** with an `AssertionError` (not an
   ImportError, not silence). Same command on clean `head_sha` → **0**. [negctrl.txt](negctrl.txt)
2. **One mutant per clause** — each added bullet dropped on its own at `head_sha`:
   the #441 human-pacing bullet, the #441 `PARKED-AT-PROMOTION` bullet, the #443 handoff-log
   bullet, the #444 local-only bullet. **4/4 KILLED**, each RED naming its own clause; clean head
   GREEN. [negctrl-per-criterion.txt](negctrl-per-criterion.txt)

The control restores the *doc* — the thing under change — never the test, so it proves the
doctrine and not the oracle.

## Artifact staging (disclosure)

The `commands[]` records were produced by `runtime/scripts/evidence-run.py` with their artifacts
written **outside the worktree**, then copied here unchanged. `wtree.sh` fingerprints untracked
files too, so writing evidence into the repo mid-run would have moved every later record off
`head_sha`'s tree. All three records therefore carry
`wtree = 7cbc79d7f8fbaab8470557d4bc2becb8276952b8 = git rev-parse <head_sha>^{tree}`. The only
post-hoc edit is each record's `artifact` path, rewritten from its staging path to the repo-relative
path above; the bytes are unchanged and every one is sha256-pinned in `manifest.json` `artifacts[]`.
These evidence files land in the commit *after* `head_sha`, so they bind by hash, not by tracking.

## Not claimed

`pr`, `review` and `reviewer_mode` are absent from the manifest, deliberately: the spec assigns PR
opening to the integrator, so no review happened and none is asserted. `#442`'s cross-repo
evidence-root gap is unit U-442 and nothing here touches `verify.py` or any other runtime policy.

## Round 2 — the fix batch

| item | source findings | fix |
|---|---|---|
| F-1 | SPEC-1, S1, Greptile P1 | promotion is **BASE→DEFAULT** (gate-classification.md, merge-serialization.md), not unit→BASE; the resume check is the leg's integration BASE tip being an ancestor of the DEFAULT branch, naming a valid LOCAL ref for a no-remote target; restricted lanes cannot PROMOTE but can still integrate |
| F-2 | S2 | the required reconstruction artifact must be **commit-preserving** (a self-contained `git bundle` or equivalent that reproduces every cited commit); seed sources + full diff are SUPPLEMENTAL only — the line `leg1/RESTORE.md` already drew |
| F-3 | SPEC-2, TA-441/443/444, Greptile test P2, S3 | the contract test now binds each rule's **obligation** words, not its subject vocabulary, and normalises bullet whitespace first; all six round-1 survivors and both SPEC-2 mutants now die |
| F-4 | SPEC-4 | negative control re-recorded **through `evidence-run.py`** — `tests-negative-control` (exit 1, reverted-content fingerprint) paired with `tests-positive-control` (exit 0, head-tree fingerprint) |
| F-5 | Greptile P2 | the historical exemplar is untouched; the **citing** text now says its proposed shape is adopted here |
| F-6 | SPEC-3 | green BASE merged (no conflict); the FULL suite is green at the new head, recorded through `evidence-run.py` |

Mutation battery: [mutants-r2.txt](mutants-r2.txt), harness [run_mutants-r2.py](run_mutants-r2.py)
(13 cases — base revert, four single-bullet deletions, the six round-1 survivors, two SPEC-2
requirement-reversing mutants; each starts from the unmutated head policy and restores it).
