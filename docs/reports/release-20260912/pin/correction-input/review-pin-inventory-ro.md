reviewed_sha: 9eb2e6f6171845100b969e2d59e65b0d34ddf86f
axis: inventory
verdict: NEEDS_CHANGES
scope: Inventory fidelity only; no candidate-acceptance or PINNED verdict.

Fleet policy enforced by this repository is excluded. Runtime command shapes, receipt fields, errors, lifecycle and scoping
behavior remain mechanics, including when embedded in policy prose or helper code. Repository parsing, ledger rules and
recovery choices do not themselves establish runtime behavior.

The snapshot passes integrity checks, but the inventory omits mechanics, drops qualifiers during atomization, includes an
unsupported legacy explanation, and assigns some evidence to predicates broader than its stated witness. One omitted source
assertion directly contradicts a retained Droid launch assertion. The report also misstates the mechanics-parent count.

Coverage inspected: 53/53 source files (12 runtime policies, 20 scripts, 21 mission files; 11,317 lines loaded and scanned),
309/309 parent excerpts, 134/134 exclusions, and 175 mechanics-parent mappings to all 429 children. All 563 additive source
records contain their quoted text within the stated Git-source spans. The eight recorded location corrections are correctly
applied, including corrected ending lines. All 320 unfinished child IDs appear in CONTINUATION.md.

The 105 WITNESSED and four PATCHED labels remain worker claims. I inspected their 22 shared evidence-mapping groups and the
inventory’s 62 distinct receipt references; raw receipts are absent from the fixed snapshot and were not independently
inspected. The 303 TODO plus 17 PARTIAL-TODO children remain unfinished work. This review establishes no runtime conformance,
test results, merged changes, issue closure or release readiness.

Integrity

All five files match inventory.json’s hashes and byte counts, checked before reliance and again after review. The frozen
inventory remains SHA256 bc87dd46ee92e1c984c6059b29846d274f4758f8c4c25ddf16c5380f5dd459c6. All 53 coverage hashes and line
counts match git show at reviewed_sha.

Parent and child IDs are unique. The 134 exclusions and 175 mapped parents are disjoint and cover all 309 original IDs.

Verified inventory defects and additive corrections

Proposed IDs below are additions. Preserve the original IDs, excerpts, classifications and snapshot bytes; append corrections
and mapping links in a new companion.

1. P1 — An omitted source contradiction makes the launch inventory incomplete.

   Source: runtime/scripts/spawn_worker.sh:167: “opencode/droid/omp/pi have no Orca autonomous launch flag at all.” This span
   has no frozen parent. In contrast, line 82 says Orca appends --auto high for Droid; runtime/sandbox-policy.md:35 also lists
   that flag.

   Affected: spawn_worker.sh coverage; C217.01/C255.06 represent the positive Droid assertion while the negative assertion is
   absent.

   Correction: append C310, bound to line 167, with C310.01–04 for the separate opencode, Droid, omp and pi absence
   assertions. Link C310.02 as contradicting C217.01/C255.06. Link matching omp/pi predicates to C219.01–02. Preserve both
   Droid polarities for later probing; this audit does not decide which is true.

2. P1 — Coverage ranges omit operational commands and daemon behavior.

   These source spans have no frozen parent containing the relevant command or assertion:

    Source and quote                         Affected mapping                          Additive correction
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    runtime/liveness-resume.md:50:           Coverage; C086/C087/C123                  Add C311.01 for selector acceptance
    worker-list --run <id> --terminal-                                                 and C311.02 for filtering the selected
    state reclaimable                                                                  Run to reclaimable terminals. Keep the
                                                                                       end-of-run decision rule excluded.
   ───────────────────────────────────────  ────────────────────────────────────────  ────────────────────────────────────────
    runtime/scripts/deny-hook.sh:82–83:      Coverage; C201/C270/C283 cover            Add C312.01 for environment
    “an env var exported here does not       arguments                                 propagation, bound to lines 80–83.
    cross the Orca daemon into the
    worker's process”
   ───────────────────────────────────────  ────────────────────────────────────────  ────────────────────────────────────────
    runtime/scripts/spawn_worker.sh:681:     C012/C296 cover lifecycle or returned     Add C313.01 for this command shape,
    terminal create --worktree "$sel"        handle                                    including the wrapper’s --json at line
    --title "$title" --command "$cmd"                                                  124.
   ───────────────────────────────────────  ────────────────────────────────────────  ────────────────────────────────────────
    runtime/scripts/spawn_worker.sh:703:     C252.04/C253.01/C297.01 cover results     Add C314.01 for this argv and named
    terminal wait --terminal "$h" --for                                                condition; link result predicates
    tui-idle --timeout-ms 90000 --json                                                 separately.
   ───────────────────────────────────────  ────────────────────────────────────────  ────────────────────────────────────────
    runtime/scripts/spawn_worker.sh:729:     C015/C250/C298 cover submission/          Add C315.01 for task/recipient binding
    orchestration dispatch --task "$task"    receipt fields                            through this command shape, including
    --to "$h" --inject                                                                 wrapper --json.
   ───────────────────────────────────────  ────────────────────────────────────────  ────────────────────────────────────────
    runtime/scripts/spawn_worker.sh:423:     C101 covers retry-of; C267 covers         Add C316.01 for the explicit ready-
    orchestration task-update --id           task-list                                 status update command; keep helper
    "$task" --status ready                                                             authorization checks excluded.

3. P2 — Four whole-record exclusions hide mechanics inside fleet instructions.

    Source and quote                                       Excluded ID    Additive correction
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    runtime/dispatch-lifecycle.md:50: check --terminal     C021           Add C021.01 for the terminal selector; keep
    <its own handle>                                                      checkpoint timing excluded. C022.01’s fenced-error
                                                                          predicate is different.
   ─────────────────────────────────────────────────────  ─────────────  ─────────────────────────────────────────────────────
    runtime/dispatch-lifecycle.md:130: “concrete           C045           Add C045.01 for the dispatch-address recipient
    terminal or dispatch:<id>”                                            form; keep the fleet addressing requirement
                                                                          excluded.
   ─────────────────────────────────────────────────────  ─────────────  ─────────────────────────────────────────────────────
    runtime/dispatch-lifecycle.md:140: “comments are       C050           Add C050.01, preserving the reliability assertion
    best-effort and lossy”                                                with its observable loss/durability boundary still
                                                                          requiring specification. C048/C049 do not cover
                                                                          lossiness.
   ─────────────────────────────────────────────────────  ─────────────  ─────────────────────────────────────────────────────
    runtime/liveness-resume.md:62: orca terminal read      C104           Add C104.01–02 for the two command forms. Keep
    --terminal <h> --screen or worker-read --dispatch                     helper exit 3 and recovery decisions excluded.
    <id>

4. P1 — Atomization drops distinct mechanics from retained parents.

    Source and quote                                    Existing IDs        Additive correction
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    runtime/dispatch-lifecycle.md:16: “It exits 0       C005.01             Add C005.02 for the version-bound exit-status
    only when the worker is ready”                                          implication. Accepted-write readiness is
                                                                            separate.
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/liveness-resume.md:64–65: “3 consecutive    C105.01, C176.04    Add C105.02, explicitly naming task status
    failures marks the task failed”                                         failed; bind through line 65, where the frozen
                                                                            excerpt cuts off.
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/liveness-resume.md:98:                      C117.01–02          Add C117.03 for the exclusive trigger. Positive
    “promoteReadyTasks fires only when a dep                                promotion and all-dependencies completion do not
    COMPLETES”                                                              cover “only when.”
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/mission-scheduling.md:23–24: “a bounded     C145.01–04          Add C145.05 for bounded precheck execution, with
    command”; “spawns nothing”                                              the bound unspecified by source. Add C145.06–07
                                                                            for terminal/worktree creation on skipped runs;
                                                                            C145.04 names only an agent.
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/mission-scheduling.md:34,38: “existing-     C147.03–05          Add C147.06–07 for the session switches’
    workspace automations only”; orca environment                           workspace restriction and C147.08 for the
    list                                                                    environment-ID list command. Do not invent a
                                                                            particular unsupported-target refusal.
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/orca-dag-semantics.md:75:                   C176.01–05          Add C176.06 for reconstructible task creation.
    “Reconstructible facts: creation”
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/orca-dag-semantics.md:128: “a typed flag    C198.01             Add C198.02 for misspelled/unknown typed-flag
    cannot be misspelled silently”                                          detection. The existing child covers only
                                                                            PowerShell quoting.
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/scripts/spawn_worker.sh:78–80: Cursor is    C255.09             Add C255.11–13 for Cursor model support, Cursor
    “one of the three agents” targeted by                                   effort support and the asserted three-agent
    --model/--effort                                                        cardinality. “Supported providers” loses these
                                                                            details.
   ──────────────────────────────────────────────────  ──────────────────  ───────────────────────────────────────────────────
    runtime/scripts/spawn_worker.sh:544–545:            C276.01             Add C276.02–03 for the field on each command. The
    “agentTerminalHandle is a worker-list/worker-                           terminal-effects predicate is different.
    show field”

5. P2 — Independently falsifiable behaviors remain bundled.

   Preserve each broad child as a conjunction and append decomposition links:

    Source                                               Compound child    Correction
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    runtime/dispatch-lifecycle.md:23: “a fresh agent     C010.02           Add C010.05–06 for fresh terminal creation and
    terminal, no setup rerun”                                              absence of setup rerun.
   ───────────────────────────────────────────────────  ────────────────  ────────────────────────────────────────────────────
    runtime/dispatch-lifecycle.md:73:                    C033.05           Add C033.06–07 for exit status and returned
    “release_unknown exits 1” and receipt recovery                         recovery action.
    action
   ───────────────────────────────────────────────────  ────────────────  ────────────────────────────────────────────────────
    runtime/dispatch-lifecycle.md:122–123: 160-          C039.09           Add C039.10–11 for the cap and marker.
    character cap and spec_truncated marker
   ───────────────────────────────────────────────────  ────────────────  ────────────────────────────────────────────────────
    runtime/gate-classification.md:16–18: ask CSV,       C068.03           Add C068.04–05 for each reversed-format case.
    gate-create JSON; mixing is refused
   ───────────────────────────────────────────────────  ────────────────  ────────────────────────────────────────────────────
    runtime/scripts/spawn_worker.sh:83–84: “opencode     C255.07           Link its conjuncts to existing C218.01/C218.02.
    AND kilo are actively STRIPPED”                                        One provider’s witness cannot establish both.

6. P2 — C183.02 inserts an unsupported legacy-import explanation.

   Source: runtime/orca-dag-semantics.md:94–95 says a pending child whose dependency “failed or never existed” never auto-
   promotes. C183.02 instead asserts that a missing dependency cannot newly be created, but a “legacy imported” child cannot
   promote. The source does not attribute the case to legacy import. Creation validation is separately asserted at runtime/
   liveness-resume.md:94–95, already C115.01.

   Correction: add C183.03, preserving the unqualified missing-dependency/nonpromotion predicate. Link C115.01 to record the
   apparent tension. Annotate C183.02’s legacy import as a fixture hypothesis requiring evidence, not source doctrine.

7. P1/P2 — Shared evidence is credited beyond its named witness.

   P1, wake behavior: runtime/orca-dag-semantics.md:57–59 calls --types the “WAKE CONDITION, not a filter.” C096.02/C169.01
   are WITNESSED against mailbox-delivery/replay/ack/final-ack receipts. Their shared scope explicitly says the matching
   handoff was already queued and delayed wake was unproven. That names evidence for mixed-type delivery, not evidence
   distinguishing wake behavior from an immediate read.

   Correction: add C096.03–04/C169.02–03, separating mixed delivery from wake behavior. Preserve batch evidence for delivery;
   leave wake behavior unresolved pending a sequence showing the waiter remains blocked with only nonmatching mail and wakes
   after matching mail arrives. C058.01/C137.01 may share the narrower batch evidence; they are not independent experiments.

   P2, deprecation: runtime/dispatch-lifecycle.md:124 and runtime/scripts/pm.py:8–10 call _heartbeat a deprecated alias.
   C040.03/C232.01/C235.01 share mailbox-empty-wait.json, whose named observation is a tick containing both markers. Co-
   presence does not establish alias/deprecation status.

   Correction: add marker-presence and alias-status predicates under each parent: C040.05–06, C232.02–03, C235.02–03. Reuse
   the tick only for marker presence. Record deprecation as source/guide provenance unless a receipt establishes the
   relationship. Keep C040.04’s recurring-cadence work unfinished.

8. P2 — CLAIM-AUDIT.md reports the wrong mechanics-parent count.

   Snapshot source: /tmp/orca-release-audit-20260912/pin-inventory-snapshot/CLAIM-AUDIT.md:3 says “134 exclusions” and “309
   mechanics-bearing parent records.” The actual mechanics-parent set contains 175 IDs; 309 is the frozen source-record
   denominator.

   Affected: summary of C001–C309. Append a corrigendum: 309 frozen records = 134 proposed exclusions + 175 mechanics parents
   → 429 draft children. Count subsequent additions separately. Preserve line 5’s qualification that these are not counts of
   independent experiments.

Unresolved receipt mappings and coverage limits

These are exact evidence needs, not findings that live behavior is false:

- C003.03, runtime/dispatch-lifecycle.md:6–7: map every listed reference name to its individual invocation receipt. The seven
  referenced paths include full-guide captures and three named reference captures; the fixed packet cannot establish
  individual retrieval of every reference.

- C066.01, runtime/gate-classification.md:11–12: helper-gates-during-ask.json must establish absence of any newly created gate
  row. Its summary says only “no pending DAG gate”; whether the receipt covers all gate states is unresolved.

- C052.01, runtime/dispatch-lifecycle.md:147–148: bind followup-bulk-close.json to both inert process identities and
  authoritative exit observations. Zero listed terminals alone is insufficient. The raw receipts were not inspected.

- C048.01 covers metadata storage. The workspace-card presentation assertion at runtime/dispatch-lifecycle.md:138 needs
  additive C048.02 for visible rendering; metadata readback is a different observation.

- Device surfaces at skills/field-test-it/SKILL.md:60–72 were inspected but fall outside the requested mission-dispatch-
  preamble cut. Device behavior was not audited.

- All 53 files received hash, line-count and mechanics-candidate inspection; all parent excerpts and child assertions were
  checked. This is not line-by-line implementation verification of every policy helper. No tests, runtime probes, source
  edits, credential access or permission changes were performed.

Verified inventory defects are ready for additive correction. Evidence-dependent mappings remain unresolved. None of the 320
existing unfinished children earns a workload-based park.

Delivery failure

Saving the report was refused:

PermissionError: [Errno 1] Operation not permitted: '/tmp/orca-release-audit-20260912/review-pin-inventory-ro.md'

worker_done was attempted exactly once with the injected task/dispatch contract and --outcome succeeded for completion of this
audit. It exited 1:

Could not connect to the running Orca app. Restart Orca and try again.
Orca is not running. Run 'orca open' first.

Completion was not recorded through IPC. No retry or permission change was attempted; explicit coordinator recovery is
required.
