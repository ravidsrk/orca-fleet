# U-442 — verify.py: split the SHA root from the evidence root

UNIT: U-442 · ISSUE: #442 · RUN: run_bec47e54b673 · BASE: `review/2026-09-20-tracker-sweep`
BASE_SHA: `a58bf71a283928a8278e560163452ee70c7ad609` · HEAD_SHA: `1ef8bd797477314f25ece410fe8a6e70c2560bad`
LIGHTING: lit · CLASS: mutation (real-feature-small, tooling) · MANIFEST: [manifest.json](manifest.json)

## What was wrong

`verify.py` assumed the unit repo **is** the evidence repo. `_git()` ran every git operation in
the process cwd, and `_resolve()` bounded every evidence path against that same toplevel. A
chained-run manifest breaks the assumption in both directions at once — the chaining report lives
in the fleet repo, the leg SHAs in the target repo — so running the verifier in the evidence repo
made the SHAs "not a real commit" and running it in the target repo made the evidence unreadable.
There was no third place to stand, which is why the finding says the verifier "can never run".

## What changed

`_ROOTS = {"git": None, "evidence": None}`, written once from argv in `main()`.

- `--git-dir` — the clone the git/SHA legs run against (`git -C`): commit existence, ancestry,
  trees, `path@ref` reads, negative-control worktrees, `infer_repo`.
- `--evidence-root` — the root manifest-relative evidence paths resolve and are bounded under.

With neither flag the two are `None` and every resolution is the single-repo one: no `-C` is
added, and `_resolve` derives the same toplevel from the same `git rev-parse` with the same
`is None` fallback. `--evidence-root` is deliberately **not** implied by `--git-dir` — redirecting
the SHA legs must never silently move the #267 bound.

### #267 is re-rooted, not relaxed

- An absolute evidence path, and one escaping the root, stay REFUSED — now against whichever root
  was named.
- The named root must itself be inside a git work tree. Evidence an auditor cannot re-derive from
  a clone is exactly what #267 refuses; `--evidence-root /tmp` is not a root, it is a hiding place.
- A bad root is a USAGE error (exit 1), never a verdict on the unit (exit 2). A misconfigured
  verifier has not judged anything.
- Cross-repo evidence can never be "tracked at head_sha" — the other repo does not hold it — so it
  passes on its `artifacts[]` sha256 pin alone, and dropping the pin fails. The split buys no way
  around the pin; `test_an_unpinned_cross_repo_artifact_is_refused` is the guard.

### Interface width

Three new top-level names (`_ROOTS`, `_git_bytes`, `_root_arg`). The reshape-it RV-D2 width pin
moves **85 → 88**, with the budget and the reason recorded in `tests/test_reshape_width_verify.py`'s
docstring. The ratchet the pin actually defends — width < the pre-deepening baseline of 92 — is
untouched, as is the identity check that the signature engine stayed behind `_verify_sig`.
`set_roots`, `_git_prefix` and `_evidence_root` were drafted and then folded into `_ROOTS` and its
two call sites precisely to keep that budget small.

## Evidence

| Label | Command | Exit | Artifact |
|---|---|---|---|
| tests | `python3 -m unittest tests.test_verify` | 0 (255 tests) | [tests.txt](tests.txt) |
| unit-scope-tests | `python3 -m unittest tests.test_verify tests.test_reshape_width_verify tests.test_validate` | 0 | [unit-scope.txt](unit-scope.txt) |
| validate | `python3 scripts/validate.py` | 0 | [validate.txt](validate.txt) |
| full-suite | `python3 -m unittest discover -s tests` | **1** | [full-suite.txt](full-suite.txt) |

Every record was made by `runtime/scripts/evidence-run.py` with the artifacts staged OUTSIDE the
repo, so the working-tree fingerprint stayed `head_sha`'s tree
(`wtree 9d5293f1 == git rev-parse 1ef8bd79^{tree}`); the files here are byte-identical copies,
pinned by sha256 in `artifacts[]`.

### Negative control — EXECUTED

`git checkout a58bf71a -- runtime/scripts/verify.py` in a throwaway worktree at `head_sha`, test
kept, bound command re-run:

- **control**: exit 1 — **8 assertion failures** in `CrossRepoRoots` ([nc-red.txt](nc-red.txt))
- **clean head_sha**: exit 0 — 255 tests ([nc-green.txt](nc-green.txt))

The single case that survives the control is
`test_without_the_split_the_same_manifest_cannot_verify`, which asserts the PRE-split behaviour
and is supposed to hold on both sides. The other helpers are written so the control **kills**
rather than explodes: the teardown reads `_ROOTS` through `getattr`, and `_run_main` catches the
`SystemExit` argparse raises for an option it does not know. Without that, reverting the split
gives eight errors in `setUp` — a stillborn mutant, which proves the module changed and not that
the behaviour did.

## Self-check with the verifier itself ([selfcheck.txt](selfcheck.txt))

Running `verify.py` on this unit's own manifest is a self-check, not the independent
verification — the coordinator owns that. It is recorded because of what it leaves standing and
what it does not:

- PASS: SHA existence, the redaction scan, the intent packet, lighting, reviewer_mode, the
  negative control, and `commands ledger FRESH — 3 exit-0 record(s) bound to head_sha's tree
  9d5293f13e46`.
- FAIL `mutation unit: no pr.number` — expected; the integrator opens the PR, per the build spec.
- FAIL `scope: no criterion ids in the authoritative contract` — **for the coordinator.** The
  frozen spec `docs/runs/2026-09-20-clean-sweep-tracker/build-u442.md` writes its acceptance
  criteria as unlabeled `- [ ]` checkboxes, so `check_scope` can extract no id set and fails
  closed, exactly as it should. As frozen, that document cannot serve as the authoritative
  `--contract-source` for this unit. The manifest declares `AC-1..AC-4` and this report maps each
  to a criterion, but those ids are the worker's reading of the spec, and a manifest cannot
  certify its own denominator. Re-freezing the spec with labeled ids (or naming a contract that
  has them) is what makes the independent verification runnable.

## Acceptance criteria

| id | criterion | state |
|---|---|---|
| AC-1 | two-repo fixture test fails at base, passes at head | MET — 8 cases, RED at base (nc-red.txt), GREEN at head |
| AC-2 | no-flag invocation unchanged; #267 escape-refusal still passes against the evidence root | MET — 255-test module green; the escape/absolute/unpinned/root-outside-a-clone cases are in the fixture class |
| AC-3 | full suite green at head; `validate.py` exit 0 | **PARTIAL** — `validate.py` exit 0; the suite exits 1 on 5 failures that all reproduce at `base_sha` (see below) |
| AC-4 | negative control executed, fixture test RED | MET — executed, recorded, 8 assertion failures |

### AC-3: the 5 pre-existing failures (not this unit's, not fixed here)

Reproduced at `base_sha` in a detached worktree before any of this unit's work:

- `test_docs_navigation.TestDocsNavigation.test_run_archive_index_lists_every_report` — the run
  archive index does not link `docs/runs/2026-09-20-clean-sweep-tracker.md`, which base commits
  `296f100b`/`a58bf71a` added.
- `test_docs_navigation.TestDocsNavigation.test_run_archive_integrity_standard_matches_practice`
- `test_docs_navigation.ReleaseCutWalkthrough.test_next_release_preparation_cut_tag_and_provenance`
- `test_docs_navigation.ReleaseRehearsalIsolation.test_inherited_git_selection_cannot_mutate_another_repository`
- `test_wire_docs.WiringScriptAnchors.test_the_committed_docs_are_the_scripts_fixed_point` —
  `README.md` is not the wiring script's fixed point.

Head runs 1714 tests to base's 1706 and fails the same 5. They are outside this unit's frozen
scope (`verify.py` + its tests + one clause of `evidence-manifest.md`), so they are reported here
rather than fixed — **the base branch is red on its own and this unit does not make it green.**

## Files

`runtime/scripts/verify.py`, `tests/test_verify.py`, `tests/test_reshape_width_verify.py`,
`runtime/evidence-manifest.md`, plus `scripts/gen-badges.py` output (`ARCHITECTURE.md`,
`assets/badges/tests.json`, 14 × `docs/missions/*.md`): the doc clause costs every mission that
rides `evidence-manifest.md` a few hundred activation tokens, and the generated table has to say so.

This report and its manifest are committed AFTER `head_sha` — pinning them at it is impossible,
since the manifest records the run whose fingerprint is that tree.
