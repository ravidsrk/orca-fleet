# Inventory correction for the bounded runtime pin

**Inventory correction prepared; PARTIAL-WITNESS remains. AC-1 is unfulfilled, #266 remains open, and no PINNED, merge or release verdict is made.** This unit changes report/inventory/evidence companions only. The doctrine repairs, helper scripts, runtime pin, frozen outer contract and mission proof tiers retain their entry bytes.

The source oracle for this correction is Git `9eb2e6f6171845100b969e2d59e65b0d34ddf86f`; the corrected packet starts at specialist head `e2e7adab8a7ddf53844d2564734202e89bb78e98`. The intended parent integration branch is `codex/release-audit-20260912` at the supplied `9eb2e6f6171845100b969e2d59e65b0d34ddf86f`. No parent-state mutation or runtime fixture was performed.

## Current authority and preserved history

Use [claim-current.json](claim-current.json) for effective child predicates and [claim-inventory.json](claim-inventory.json) for parent mappings. They apply [claim-corrections.json](claim-corrections.json) to the byte-preserved first [atomization](claim-atomization.json). Historical classifications in that first atomization, the old manifests, and [history](history/e2e7adab/CLAIM-AUDIT.md) are not current verdicts. Every changed child carries an explicit correction and before-record; unsupported labels are retracted from the current views.

The original frozen SHA256 remains `bc87dd46ee92e1c984c6059b29846d274f4758f8c4c25ddf16c5380f5dd459c6`. All five snapshot files and their inventory are preserved under `history/snapshot/`; the two Markdown snapshots each have one extra final newline compared with e2e7adab, so both byte forms are retained. The two entry untracked sidecars are copied unchanged under `history/e2e7adab/`; all earlier committed manifests remain unchanged. Current sidecars are written after the correction commit to avoid a self-referential SHA.

## Accounting corrigendum

The old CLAIM-AUDIT narrative incorrectly called all 309 records mechanics parents. The original graph is **309 frozen records = 134 proposed exclusions + 175 mechanics parents → 429 draft children**. The correction preserves that denominator, moves four mixed records out of whole-record exclusion, and appends seven parents and 52 children.

| Measure | Original | Corrected |
|---|---:|---:|
| Source files | 53 | 53 |
| Original source records | 309 | 309 |
| Appended parents | 0 | 7 (C310–C316) |
| Total parent records | 309 | 316 |
| Wholly excluded parents | 134 | 130 |
| Mechanics-bearing parents | 175 | 186 (179 original + 7 appended) |
| Child records, including retained conjunctions | 429 | 481 |
| Narrowly witnessed | 105 | 104 |
| Historical refuted/patched children | 4 | 4 |
| TODO | 303 | 350 |
| PARTIAL-TODO | 17 | 23 |
| Unfinished | 320 | 373 |

These are record counts, not counts of independent experiments. Six original witness labels are retracted to PARTIAL-TODO and five new narrow children share two existing experiments, giving 105 − 6 + 5 = 104 witnessed records. The unsupported C183.02 interpretation remains an explicit TODO hypothesis, not source doctrine. No workload parks were created.

## Reproduced source defects and additions

All eight audit groups were reproduced before current-view publication using original Git objects and frozen/snapshot records. [correction-source-refutations.json](correction-source-refutations.json) stores exact old records, source spans/quotes and the evidence against each inventory assertion. This is a source-inventory refutation, never a refutation of runtime behavior. The independent audit is retained as input; this builder's reproduction is self-verified and does not replace fresh acceptance review.

- **G1: Omitted Droid absence contradicts retained positive launch assertion.** Appended children: C310.01, C310.02, C310.03, C310.04.
- **G2: Omitted operational commands and daemon environment assertion.** Appended children: C311.01, C311.02, C312.01, C313.01, C314.01, C315.01, C316.01.
- **G3: Whole-record exclusions drop mechanics embedded in policy.** Appended children: C021.01, C045.01, C050.01, C104.01, C104.02.
- **G4: Retained-parent atomization drops independent qualifiers.** Appended children: C005.02, C105.02, C117.03, C145.05, C145.06, C145.07, C147.06, C147.07, C147.08, C176.06, C198.02, C255.11, C255.12, C255.13, C276.02, C276.03.
- **G5: Compound children require explicit conjunct links.** Appended children: C010.05, C010.06, C033.06, C033.07, C039.10, C039.11, C068.04, C068.05.
- **G6: Legacy-import explanation is unsupported by source.** Appended children: C183.03.
- **G7: Delivery and marker evidence is overcredited as wake and alias behavior.** Appended children: C096.03, C096.04, C169.02, C169.03, C040.05, C040.06, C232.02, C232.03, C235.02, C235.03.
- **G8: 309 mechanics-parent narrative is contradicted by the 175-ID mapping.** Appended children: none; explicit count corrigendum.

G1 retains both Droid polarities: C310.02 contradicts C217.01/C255.06. The helper script is unchanged; an authorized launch observation must decide which assertion describes the binary. G3 retains the policy fragments of C021/C045/C050/C104 while mapping their mechanics. G4 preserves readiness exit implications, failed-task status, exclusive promotion, bounded precheck and zero-spawn components, session restrictions, typed-flag detection, Cursor support/cardinality and command-specific result fields. G5 retains the broad children as conjunctions and links the two provider-stripping components of C255.07 to existing C218.01/C218.02. G6 replaces the source interpretation with unqualified C183.03 and records its tension with C115.01; legacy import is only a possible fixture hypothesis.

Additional visible-rendering predicate: **C048.02**, distinct from metadata storage C048.01.

Exactly 22 original child records receive explicit metadata/assertion/disposition corrections: C003.03, C010.02, C033.05, C039.09, C040.03, C048.01, C052.01, C058.01, C066.01, C068.03, C096.02, C115.01, C137.01, C169.01, C183.02, C217.01, C219.01, C219.02, C232.01, C235.01, C255.06, C255.07.

## Receipt reconciliation

[correction-evidence-reconciliation.json](correction-evidence-reconciliation.json) binds the existing receipt bytes at e2e7adab and the coordinator-owned teardown packet. The original manifest's 289 artifact hashes were checked against that Git commit. No runtime/Run/terminal was created, no probe was executed, and no guide/source declaration was promoted to live behavior.

- **C003.03:** all seven orchestration and three orca-cli reference names now map to individual `--reference` invocations with exit zero. The old seven-path mapping omitted seven existing individual receipts; full-guide capture is not substituted for retrieval. This resolves the audit's evidence-mapping uncertainty only for guide retrieval.
- **C066.01:** the ask-time `gate-list --task` response contains exactly the preexisting resolved gate, matching create/resolve identity and timestamp. No `--status` selector was used. This corrects the audit's pending-only summary, but complete all-state/Run coverage and transient gate creation remain unobserved; current status is PARTIAL-TODO.
- **C052.01:** both inert handle/PTY/incarnation identities map from the existing before-list/create receipts to the same worktree, `closed=2/stopped=2`, and coordinator terminal reads showing each `status=exited`. Credit is limited to these two processes. Empty terminal lists alone are not the exit oracle; restart durability remains TODO under C052.03.
- **C096.02/C169.01:** broad wake predicates are PARTIAL-TODO. C096.03/C169.02 retain the 50-message mixed batch, identical replay, one-message remainder and final empty acknowledgment evidence. C058.01/C137.01 are explicitly narrowed to that same delivery experiment. C096.04/C169.03 require a blocked nonmatching-only waiter followed by later matching mail.
- **C040.03/C232.01/C235.01:** broad marker/alias assertions are PARTIAL-TODO. C040.05/C232.02/C235.02 reuse the single tick containing both markers; C040.06/C232.03/C235.03 keep alias/deprecation provenance separate and unobserved. One tick does not finish recurring cadence C040.04.
- **C048.01/C048.02:** metadata storage does not observe a workspace card. Visible rendering remains TODO until the coordinator supplies an authorized screenshot/accessibility witness tied to the exact comment and workspace.

## Continuation and acceptance boundary

[CONTINUATION.md](CONTINUATION.md) lists every one of the 373 unfinished child IDs by family and the concrete fixture requests. [outstanding-claims.json](outstanding-claims.json) retains each exact predicate, source, probe and precondition. Local scratch, worker and UI fixtures are obtainable in separately authorized units; absent provider/OS/isolated-runtime conditions are recorded separately. Workload is never a parking reason.

The five former owned terminals are exited and both scratch paths are absent according to the coordinator evidence. No cleanup remains for this unit. New probes must use newly authorized resources, not those retired fixtures. Independent source/completeness acceptance, exact-head clean-environment checks, replay of the three prior doctrine refutations and the mission's required live-probe sample still belong to the coordinator. The outer contract remains unchanged and AC-1 remains false.

## Base re-witness at 4c52b47

The correction branch now sits on integration base `4c52b479a10d861a0f96fe00ef732e214232c5f5` (`origin/codex/release-audit-20260912`). Its merges changed 13 of the 53 coverage files after baseline e2e7adab: `runtime/evidence-manifest.md`, `runtime/merge-serialization.md`, `runtime/mission-scheduling.md`, seven `runtime/scripts/` files (`deny-hook.sh`, `diff_scope.py`, `evidence-run.py`, `floor_guard.py`, `preflight.py`, `run_report.py`, `verify.py`) and the absorb-it, migrate-it and modernize-it `SKILL.md` files. No pin commit changes them. `base_rewitness` in [claim-corrections.json](claim-corrections.json) records each file's baseline and moved-base SHA256 and relocates all 60 spans on those files (inventory quotes plus independent-audit bindings) and every included range to an identical baseline block at 4c52b47: 46 keep their lines, 14 moved (12 in mission-scheduling.md, 2 in deny-hook.sh), none is absent or ambiguous, and 9 files carry no included range or span.

The frozen inventory, source oracle 9eb2e6f, denominator, graph and dispositions are unchanged. This is a source-drift record, not a runtime witness, and it credits no claim. The checker accepts a changed coverage file only when it is listed, the re-witness starts at the baseline, the moved base is an ancestor of HEAD, both hashes match, the working bytes equal the moved base, the recorded span set equals the inventory's, and each relocated quote and range is present. [rewitness-checks/negative-controls.json](rewitness-checks/negative-controls.json) shows that reverting either the inventory delta or the checker delta restores the 13 drift errors, and that ten single mutations of the record or the doctrine bytes each go RED. [probe-sources/pin-rewitness-gen.py.txt](probe-sources/pin-rewitness-gen.py.txt) regenerates the record and [probe-sources/pin-rewitness-controls.py.txt](probe-sources/pin-rewitness-controls.py.txt) replays the controls.

## Verification method

Run `python docs/reports/release-20260912/pin/check-correction.py` to re-derive source hashes, exact quotes, original-plus-additive graph equality, parent coverage, links, current dispositions and unfinished-ID coverage. Its `--baseline` option applies the same source-bound obligations to the original graph and exits nonzero for the omitted/uncorrected records. This negative control verifies inventory fidelity, not runtime semantics; it is not a prose-mirroring unit test. Command receipts retain actual exit codes and content fingerprints. The final command outcomes and correction SHA are in the post-commit manifest and handoff report; precommit test fingerprints are not relabeled as clean-head proofs.
