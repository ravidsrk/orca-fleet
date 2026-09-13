# Scope and atomic claim audit

The frozen denominator is still **309 source records**. This additive audit identifies **134 exclusions** and **309 mechanics-bearing parent records**, expanded into **429 child predicates**. It does not replace 309 with a smaller denominator or treat exclusions as passed tests.

Child dispositions: **105 narrowly witnessed**, **4 refuted/patched children across C016/C090/C109**, **320 unfinished** (303 TODO + 17 partial TODO). Duplicate source predicates intentionally share receipts only for the same observed behavior; the counts are not counts of independent experiments. Independent source-completeness and clause review remain owed.

Exact source text and line spans for every retained/excluded record are in [claim-atomization.json](claim-atomization.json). The original spans bind to the frozen base; all report content binds to the final companion manifest.

## Scope exclusions

- **C002** `runtime/dispatch-lifecycle.md:5` — Anti-drift declaration is the repo authoring rule, not evidence that every line matches the binary.
- **C007** `runtime/dispatch-lifecycle.md:18` — Historical source/tag witness label and probe debt, not a new installed behavior.
- **C014** `runtime/dispatch-lifecycle.md:33` — Choice to use low-level lane for custom topology/ro and ledger it is fleet policy.
- **C017** `runtime/dispatch-lifecycle.md:37` — Deletion of the repository re-Enter loop and warning about stray input is local repair history.
- **C021** `runtime/dispatch-lifecycle.md:50` — When workers check their inbox is a fleet checkpoint requirement.
- **C027** `runtime/dispatch-lifecycle.md:62` — Three-to-four-deep chain budget is fleet policy.
- **C029** `runtime/dispatch-lifecycle.md:66` — Coordinator dispatching review axes is the repository no-subworker rule.
- **C036** `runtime/dispatch-lifecycle.md:114` — Recording Run id in file ledger is repository bookkeeping.
- **C038** `runtime/dispatch-lifecycle.md:119` — Processing all messages before ack is the coordinator protocol; FIFO/ack mechanics are retained in C037/C039.
- **C042** `runtime/dispatch-lifecycle.md:127` — Requiring retry IDs on every non-idempotent call is a fleet usage rule; availability is retained in C041.
- **C045** `runtime/dispatch-lifecycle.md:130` — Concrete lifecycle addressing is explicitly declared fleet policy; runtime group behavior remains in C043/C044.
- **C050** `runtime/dispatch-lifecycle.md:139` — Comments cannot replace ledger is an evidence-retention rule, not an API guarantee.
- **C051** `runtime/dispatch-lifecycle.md:147` — Ledger row shape is repository bookkeeping.
- **C054** `runtime/dispatch-lifecycle.md:154` — This is a historical probe-debt preface at v1.4.199; each actual probe remains C055-C060.
- **C057** `runtime/dispatch-lifecycle.md:158` — Numbered-list token 3. carries no assertion.
- **C062** `runtime/evidence-manifest.md:13` — JSON shape introduction belongs to repository evidence schema.
- **C070** `runtime/gate-classification.md:23` — Coordinator manually placing gate resolution in task text is a repair procedure; omission predicate stays C069.
- **C071** `runtime/gate-classification.md:25` — Source-witness/probe-owed classification of the prior predicate is historical evidence status.
- **C072** `runtime/gate-classification.md:27` — Prediction that an uninformed agent invents an answer is behavioral advice, not Orca mechanics.
- **C074** `runtime/gate-classification.md:32` — Treating an unanswered active ask as urgent work is fleet inbox policy.
- **C075** `runtime/gate-classification.md:33` — Do not wait for blocked is coordinator advice; actual task-state predicate remains C073/C187.
- **C077** `runtime/gate-classification.md:35` — Historical unanswered asks are not fleet stalls by repository convergence definition.
- **C080** `runtime/gate-classification.md:97` — To reach a human is an incomplete section introducer.
- **C088** `runtime/liveness-resume.md:22` — Account of earlier fleet mistakes is narrative history.
- **C089** `runtime/liveness-resume.md:25` — Always pass Run scope is usage policy; actual filtering remains C090/C123.
- **C091** `runtime/liveness-resume.md:30` — Meaning assigned to outcome_unknown is an interpretation; positive/negative receipt behavior stays C006.
- **C092** `runtime/liveness-resume.md:30` — spawn_worker exit 4 and its inspection output are this repository helper contract.
- **C094** `runtime/liveness-resume.md:34` — Absence authorizes no cleanup is a permission rule.
- **C095** `runtime/liveness-resume.md:35` — Wait or inspect is a coordinator decision rule.
- **C098** `runtime/liveness-resume.md:46` — Three empty waits and acting on attention is the fleet liveness algorithm; row fields stay C087.
- **C099** `runtime/liveness-resume.md:48` — Preference for runtime-provided argv over heuristic is a methodological judgment.
- **C100** `runtime/liveness-resume.md:49` — Inspection command does not authorize cleanup is a fleet authority rule.
- **C102** `runtime/liveness-resume.md:58` — spawn_worker exit 5 and mandatory stop are local profile enforcement.
- **C103** `runtime/liveness-resume.md:59` — Local helper exits 4/1 and retry advice are repo-owned control flow.
- **C104** `runtime/liveness-resume.md:61` — Local helper exit 3 and pane-first dual-writer precautions are fleet recovery policy.
- **C106** `runtime/liveness-resume.md:68` — Rewriting task or parking is a fragment of the fleet retry policy.
- **C107** `runtime/liveness-resume.md:68` — Three-attempt accounting belongs to fleet doctor policy, distinct from runtime circuit C105.
- **C108** `runtime/liveness-resume.md:69` — Reconfirming danger environment grant is repo permission policy.
- **C114** `runtime/liveness-resume.md:79` — Claim that WATCH/RESUME suffice is a fleet strategy judgment, not an API behavior.
- **C116** `runtime/liveness-resume.md:95` — Narrative consequence of missing-dep validation; exact validation remains C115.
- **C119** `runtime/liveness-resume.md:100` — Classifying stranded child as not a retry is fleet taxonomy; pending behavior stays C118.
- **C120** `runtime/liveness-resume.md:101` — Watchdog threshold and surfacing rule are fleet supervision algorithm.
- **C124** `runtime/liveness-resume.md:109` — Using unfiltered list only for discovery is fleet usage policy; list behavior stays C155.
- **C125** `runtime/liveness-resume.md:137` — Numbered-list token 2. carries no assertion.
- **C129** `runtime/liveness-resume.md:148` — Numbered-list token 3. carries no assertion.
- **C130** `runtime/liveness-resume.md:148` — Cross-verifying completed claims against git is evidence protocol.
- **C133** `runtime/merge-serialization.md:19` — Preference for explicit conductor handle is declared fleet convention.
- **C135** `runtime/merge-serialization.md:23` — Never group-address merge_ready is fleet discipline; runtime fanout stays C134.
- **C136** `runtime/merge-serialization.md:28` — Numbered-list token 1. carries no assertion.
- **C138** `runtime/merge-serialization.md:30` — Processing entire delivery before ack is fleet mailbox algorithm; mechanism stays C172.
- **C139** `runtime/merge-serialization.md:31` — Acking after is an incomplete connective.
- **C141** `runtime/mission-scheduling.md:4` — Definition/examples of scheduled mission outcome are repository taxonomy.
- **C144** `runtime/mission-scheduling.md:18` — Role assignment of coordinator vs roster workers is fleet architecture.
- **C146** `runtime/mission-scheduling.md:25` — Cost motivation for precheck is incomplete narrative, not API claim.
- **C150** `runtime/orca-dag-semantics.md:4` — Source pedigree and instruction to treat contract seriously is evidence framing.
- **C156** `runtime/orca-dag-semantics.md:18` — Foreign runs are not our wins/stalls is fleet convergence accounting.
- **C159** `runtime/orca-dag-semantics.md:31` — Do not build fleets on hierarchy is policy; parent_id mechanics remain C158.
- **C161** `runtime/orca-dag-semantics.md:41` — Table header Type/Reality carries no assertion.
- **C162** `runtime/orca-dag-semantics.md:42` — Markdown table divider carries no assertion.
- **C164** `runtime/orca-dag-semantics.md:43` — Reconstruction advice using task spec is a coordinator procedure; dispatch receipt claim stays C163.
- **C167** `runtime/orca-dag-semantics.md:47` — Expectation during serialized merges is workflow narrative.
- **C170** `runtime/orca-dag-semantics.md:59` — Warning about acknowledging unprocessed mail is algorithmic consequence; delivery mechanics stay C169/C172.
- **C171** `runtime/orca-dag-semantics.md:61` — Process then ack is coordinator policy.
- **C173** `runtime/orca-dag-semantics.md:68` — Process batch then ack is coordinator policy.
- **C179** `runtime/orca-dag-semantics.md:87` — Convergence definition combines task terminality and inbox/gates; this is fleet policy, not a runtime converged flag.
- **C180** `runtime/orca-dag-semantics.md:90` — Not converged heading carries no standalone assertion.
- **C181** `runtime/orca-dag-semantics.md:92` — Nonterminal statuses as blockers is fleet convergence definition.
- **C182** `runtime/orca-dag-semantics.md:93` — Unanswered active ask as blocker is fleet convergence definition.
- **C184** `runtime/orca-dag-semantics.md:103` — Numbered-list token 1. carries no assertion.
- **C188** `runtime/orca-dag-semantics.md:107` — Numbered-list token 2. carries no assertion.
- **C191** `runtime/orca-dag-semantics.md:113` — Ignoring ask burns timeout is explanatory advice; runtime timeout remains C186.
- **C192** `runtime/orca-dag-semantics.md:113` — Rescan unanswered asks on resume is coordinator recovery algorithm.
- **C193** `runtime/orca-dag-semantics.md:114` — Historical unanswered ask does not stall is fleet convergence policy.
- **C194** `runtime/orca-dag-semantics.md:114` — Do not spin waiting for historical ask is fleet supervision policy.
- **C197** `runtime/orca-dag-semantics.md:123` — SHA-bound manifest as definition of done and typed flags requirement are repository evidence protocol; payload flag mechanics remain C061/C020.
- **C204** `runtime/sandbox-policy.md:18` — Record actual launch effects and host permission in ledger is evidence policy; launch mapping stays C201-C203.
- **C205** `runtime/sandbox-policy.md:19` — Historical source-witness/live-debt label, not new mechanics.
- **C206** `runtime/sandbox-policy.md:22` — spawn_worker PROFILE mapping is repository helper behavior; external agent mapping stays C207/C212-C219.
- **C208** `runtime/sandbox-policy.md:24` — Native ro choices and unverified dashes state repository roster evidence boundary.
- **C209** `runtime/sandbox-policy.md:25` — History of misleading ro note is narrative.
- **C210** `runtime/sandbox-policy.md:28` — Permission table heading carries no assertion.
- **C211** `runtime/sandbox-policy.md:29` — Markdown table divider carries no assertion.
- **C221** `runtime/sandbox-policy.md:39` — Permission boundary for report-only missions is repository policy.
- **C224** `runtime/sandbox-policy.md:79` — Caller-named transcript is not evidence is repository evidence rule.
- **C226** `runtime/sandbox-policy.md:82` — Snapshot before serve is operational safety advice; pairing behavior remains C225.
- **C229** `runtime/scripts/deny-hook.sh:722` — Worker never resets is repo deny-hook rule; reset effects stay C227/C228.
- **C231** `runtime/scripts/pm.py:4` — pm.py parsing/skip algorithm is local implementation; stderr/markers remain C230/C232/C235.
- **C236** `runtime/scripts/pm.py:106` — Future alias removal is explicitly hypothetical and has no current installed predicate.
- **C237** `runtime/scripts/pm.py:114` — pm.py display loop is repository implementation.
- **C238** `runtime/scripts/sandbox_doctor.py:2` — Docstring defines repository transcript checker purpose; doctor invocation remains C222/C223/C262.
- **C239** `runtime/scripts/sandbox_doctor.py:4` — No warn/no fail CLEAR threshold is repo doctor acceptance policy and a risk judgment.
- **C240** `runtime/scripts/sandbox_doctor.py:32` — Comment introducing local status constants carries no installed assertion.
- **C241** `runtime/scripts/sandbox_doctor.py:33` — BAD_STATUS vocabulary is local parser code.
- **C242** `runtime/scripts/sandbox_doctor.py:35` — FINDING_KEYS vocabulary is local parser code.
- **C243** `runtime/scripts/sandbox_doctor.py:37` — STATUS_KEYS vocabulary is local parser code.
- **C244** `runtime/scripts/spawn_worker.sh:4` — Helper v5 header is local release history.
- **C248** `runtime/scripts/spawn_worker.sh:17` — Helper exits and launch unusable branch are local implementation; runtime nextCommands remains C278.
- **C249** `runtime/scripts/spawn_worker.sh:22` — Stop-before-respawn and chosen custom lane are repository recovery implementation.
- **C257** `runtime/scripts/spawn_worker.sh:93` — Cross-reference and comment delimiter only.
- **C258** `runtime/scripts/spawn_worker.sh:137` — Heredoc/function closing tokens only.
- **C260** `runtime/scripts/spawn_worker.sh:273` — Comment maps documentation options; documentation map is not an installed runtime assertion. Doctor availability remains C262.
- **C261** `runtime/scripts/spawn_worker.sh:275` — Choosing JSON-to-plain fallback is repository helper algorithm.
- **C263** `runtime/scripts/spawn_worker.sh:313` — PROFILE rw being default is repository policy.
- **C264** `runtime/scripts/spawn_worker.sh:313` — Isolation/review/PR policy and agent mapping implementation are repo code; external map predicates stay C255.
- **C265** `runtime/scripts/spawn_worker.sh:338` — Environment override opt-in and precedence are repository helper policy.
- **C266** `runtime/scripts/spawn_worker.sh:370` — emit function print/exit tail is repository glue.
- **C268** `runtime/scripts/spawn_worker.sh:433` — Shell case terminator only.
- **C269** `runtime/scripts/spawn_worker.sh:435` — Local lane-selection rules are repository helper code.
- **C273** `runtime/scripts/spawn_worker.sh:473` — Local receipt parser stdout/stderr formatting is repository helper code.
- **C275** `runtime/scripts/spawn_worker.sh:525` — Optional data/error parser and exit classifications are repository code; runtime typed-code predicates stay C274.
- **C277** `runtime/scripts/spawn_worker.sh:553` — Local state branch interpreting outcome_unknown; runtime transition remains C006.
- **C279** `runtime/scripts/spawn_worker.sh:566` — Missing-state classification is repository parser policy.
- **C280** `runtime/scripts/spawn_worker.sh:567` — Narrative of earlier helper parser regression is local history.
- **C281** `runtime/scripts/spawn_worker.sh:569` — Unexpected receipt recovery branch is repository fail-closed behavior.
- **C284** `runtime/scripts/spawn_worker.sh:636` — Shell fi delimiter only.
- **C285** `runtime/scripts/spawn_worker.sh:638` — Helper case/echo/exit logic is repository code.
- **C286** `runtime/scripts/spawn_worker.sh:651` — Unreadable receipt not success is repository acceptance policy.
- **C287** `runtime/scripts/spawn_worker.sh:651` — Inspect-never-respawn instruction is fleet dual-writer policy.
- **C288** `runtime/scripts/spawn_worker.sh:651` — Receipt-path echo and local unknown diagnostic are repository output text.
- **C289** `runtime/scripts/spawn_worker.sh:653` — Inspection/stop/abandon recovery instruction is fleet policy, not permission to invoke cleanup.
- **C290** `runtime/scripts/spawn_worker.sh:653` — Echo/case termination fragment only.
- **C292** `runtime/scripts/spawn_worker.sh:665` — Local diagnostic predicts inability to satisfy PROFILE; actual host mapping remains C283/C291.
- **C293** `runtime/scripts/spawn_worker.sh:665` — Stop-never-respawn is fleet safety policy.
- **C294** `runtime/scripts/spawn_worker.sh:665` — Host fix / override grant advice is local configuration policy.
- **C295** `runtime/scripts/spawn_worker.sh:665` — Helper exit codes and branch selection are repository code; low-level mechanics remain C250.
- **C299** `runtime/scripts/spawn_worker.sh:761` — Case branch comments about observed stage are local parser control flow.
- **C301** `skills/oss-contribute/SKILL.md:76` — Manual orchestration loop and file-ledger gate preference is mission policy; retired aliases remain C154.
- **C302** `skills/oss-contribute/SKILL.md:77` — No conductor/merges is this mission's scope restriction.
- **C303** `skills/pin-it/SKILL.md:14` — Compatibility prerequisites say what environment the mission requires, not that the current environment passes.
- **C304** `skills/pin-it/SKILL.md:16` — One worker router requirement is repository architecture.
- **C305** `skills/pin-it/SKILL.md:33` — Incomplete fragment about corrupt command shapes, no independent mechanics predicate.
- **C306** `skills/pin-it/SKILL.md:33` — Binary/guide evidence hierarchy is mission methodology.
- **C307** `skills/pin-it/SKILL.md:40` — Scratch isolation, teardown and no-default-branch rules are mission authorization boundaries; teardown API predicates stay C052/C053.
- **C309** `skills/ship-it/SKILL.md:60` — Ship-it preflight requirements are conditions to verify per run, not unconditional runtime assertions.

## Mechanics parents and children

### C001 — runtime/attention-budget.md:26

- **C001.01 / WITNESSED**: worker-list rows expose projection.liveness. [helper-workers-bound](receipts/helper-workers-bound.json)
- **C001.02 / WITNESSED**: worker-list rows expose projection.attention.requiresAction. [helper-workers-bound](receipts/helper-workers-bound.json)

### C003 — runtime/dispatch-lifecycle.md:5

- **C003.01 / WITNESSED**: skills get orchestration and orca-cli return installed topic guides. [orchestration-full](receipts/orchestration-full.json), [orca-cli-full](receipts/orca-cli-full.json), [orchestration-references](receipts/orchestration-references.json), [orca-cli-references](receipts/orca-cli-references.json), [orchestration-worker-contract](receipts/orchestration-worker-contract.json), [orchestration-recovery-and-cleanup](receipts/orchestration-recovery-and-cleanup.json), [orchestration-legacy-contract-migration](receipts/orchestration-legacy-contract-migration.json)
- **C003.02 / WITNESSED**: skills get TOPIC --references lists references. [orchestration-full](receipts/orchestration-full.json), [orca-cli-full](receipts/orca-cli-full.json), [orchestration-references](receipts/orchestration-references.json), [orca-cli-references](receipts/orca-cli-references.json), [orchestration-worker-contract](receipts/orchestration-worker-contract.json), [orchestration-recovery-and-cleanup](receipts/orchestration-recovery-and-cleanup.json), [orchestration-legacy-contract-migration](receipts/orchestration-legacy-contract-migration.json)
- **C003.03 / WITNESSED**: skills get TOPIC --reference NAME retrieves each listed reference. [orchestration-full](receipts/orchestration-full.json), [orca-cli-full](receipts/orca-cli-full.json), [orchestration-references](receipts/orchestration-references.json), [orca-cli-references](receipts/orca-cli-references.json), [orchestration-worker-contract](receipts/orchestration-worker-contract.json), [orchestration-recovery-and-cleanup](receipts/orchestration-recovery-and-cleanup.json), [orchestration-legacy-contract-migration](receipts/orchestration-legacy-contract-migration.json)
- **C003.04 / TODO**: older CLI --full fallback remains version-specific, not established by 1.4.200. No live receipt establishes this predicate.

### C004 — runtime/dispatch-lifecycle.md:15

- **C004.01 / TODO**: worker-start supports a fresh worktree/terminal with task, name, agent and setup run. No live receipt establishes this predicate.
- **C004.02 / TODO**: fresh worker-start orders placement then terminal then readiness then dispatch. No live receipt establishes this predicate.

### C005 — runtime/dispatch-lifecycle.md:16

- **C005.01 / TODO**: v1.4.199 worker-start ready requires accepted preamble write without observed turn start. No live receipt establishes this predicate.

### C006 — runtime/dispatch-lifecycle.md:17

- **C006.01 / WITNESSED**: v1.4.200 ready worker-start receipt includes an observed turn start. [helper-start](receipts/helper-start.json)
- **C006.02 / TODO**: without observed turn start v1.4.200 worker-start returns outcome_unknown. No live receipt establishes this predicate.

### C008 — runtime/dispatch-lifecycle.md:20

- **C008.01 / WITNESSED**: successful worker-start receipt carries runId, taskId and dispatchId. [helper-start](receipts/helper-start.json)
- **C008.02 / WITNESSED**: successful worker-start receipt carries state and stage. [helper-start](receipts/helper-start.json)
- **C008.03 / WITNESSED**: successful worker-start receipt carries setup and launch.requested/effective. [helper-start](receipts/helper-start.json)
- **C008.04 / WITNESSED**: successful worker-start receipt carries mode, effects and residualResources. [helper-start](receipts/helper-start.json)
- **C008.05 / TODO**: failed worker-start receipt carries failedStage, lastError, recovery and nextCommands. No live receipt establishes this predicate.

### C009 — runtime/dispatch-lifecycle.md:21

- **C009.01 / WITNESSED**: worker-start identifies its agent terminal by effects entry kind terminal and role agent. [helper-start](receipts/helper-start.json)

### C010 — runtime/dispatch-lifecycle.md:22

- **C010.01 / TODO**: launch.effective describes actually applied launch options. No live receipt establishes this predicate.
- **C010.02 / TODO**: worker-start existing worktree creates a fresh terminal without rerunning setup. No live receipt establishes this predicate.
- **C010.03 / WITNESSED**: worker-start --terminal reuses the exact idle terminal. [helper-start](receipts/helper-start.json)
- **C010.04 / PARTIAL-TODO**: worker-start --terminal cleanup ownership follows the reported effects ownership. [helper-workers-bound](receipts/helper-workers-bound.json), [settle-release](receipts/settle-release.json)

### C011 — runtime/dispatch-lifecycle.md:26

- **C011.01 / TODO**: task_not_found is a typed error.code. No live receipt establishes this predicate.
- **C011.02 / TODO**: task_not_startable reports unmetDependencies and retryOf when applicable. No live receipt establishes this predicate.
- **C011.03 / TODO**: inject_rejected is a typed error.code. No live receipt establishes this predicate.
- **C011.04 / TODO**: nested_worker_depth_exceeded is a typed error.code. No live receipt establishes this predicate.
- **C011.05 / PARTIAL-TODO**: consumer_fenced is a typed error.code. [fixture-create-foreign](receipts/fixture-create-foreign.json)
- **C011.06 / TODO**: dispatch_inactive is a typed error.code. No live receipt establishes this predicate.
- **C011.07 / TODO**: runtime_error is a catch-all typed error.code. No live receipt establishes this predicate.
- **C011.08 / TODO**: error.data.nextSteps supplies recovery where present. No live receipt establishes this predicate.

### C012 — runtime/dispatch-lifecycle.md:31

- **C012.01 / TODO**: terminal create plus dispatch --inject creates no supervised worker-lifecycle row. No live receipt establishes this predicate.
- **C012.02 / TODO**: worker-stop does not stop a low-level unsupervised process. No live receipt establishes this predicate.
- **C012.03 / TODO**: worker-release does not close a low-level unsupervised process. No live receipt establishes this predicate.

### C013 — runtime/dispatch-lifecycle.md:32

- **C013.01 / TODO**: worker-list shows a low-level injected dispatch as unsupervised. No live receipt establishes this predicate.
- **C013.02 / TODO**: unsupervised terminal state is retained. No live receipt establishes this predicate.

### C015 — runtime/dispatch-lifecycle.md:33

- **C015.01 / TODO**: dispatch --inject submits the preamble without another Enter. No live receipt establishes this predicate.
- **C015.02 / TODO**: dispatch --inject JSON returns prompt.requestId. No live receipt establishes this predicate.
- **C015.03 / TODO**: dispatch --inject JSON returns prompt.stages input_accepted or turn_started. No live receipt establishes this predicate.

### C016 — runtime/dispatch-lifecycle.md:35

- **C016.01 / PATCHED**: retry shorthand without original text and Enter is accepted as written in original prose. [retry-original-id-shorthand](receipts/retry-original-id-shorthand.json), [retry-original-id-text-only](receipts/retry-original-id-text-only.json), [retry-original-exact](receipts/retry-original-exact.json)
- **C016.02 / WITNESSED**: terminal send replay with original identity and payload does not resend. [effect-original-send](receipts/effect-original-send.json), [effect-before-replay](receipts/effect-before-replay.json), [effect-original-replay](receipts/effect-original-replay.json), [effect-after-replay](receipts/effect-after-replay.json), [retry-original-exact](receipts/retry-original-exact.json)
- **C016.03 / TODO**: wait-submit timeout returns an input-accepted receipt. No live receipt establishes this predicate.

### C018 — runtime/dispatch-lifecycle.md:44

- **C018.01 / TODO**: worker_done requires an explicit succeeded or failed outcome. No live receipt establishes this predicate.
- **C018.02 / WITNESSED**: worker_done with omitted recipient routes to the active Dispatch owning Run. [helper-check-1](receipts/helper-check-1.json), [helper-tasks-after-done](receipts/helper-tasks-after-done.json), [helper-dispatch-after-done](receipts/helper-dispatch-after-done.json)

### C019 — runtime/dispatch-lifecycle.md:46

- **C019.01 / TODO**: worker dispatch preamble provides its from handle. No live receipt establishes this predicate.
- **C019.02 / TODO**: worker dispatch preamble provides dispatch capability. No live receipt establishes this predicate.
- **C019.03 / TODO**: worker send authenticates from handle and dispatch capability. No live receipt establishes this predicate.

### C020 — runtime/dispatch-lifecycle.md:48

- **C020.01 / TODO**: send accepts typed report-path. No live receipt establishes this predicate.
- **C020.02 / TODO**: send accepts typed files-modified. No live receipt establishes this predicate.
- **C020.03 / TODO**: PowerShell raw payload quoting can strip JSON quotes. No live receipt establishes this predicate.

### C022 — runtime/dispatch-lifecycle.md:50

- **C022.01 / TODO**: a check by a fenced consumer returns consumer_fenced. No live receipt establishes this predicate.

### C023 — runtime/dispatch-lifecycle.md:55

- **C023.01 / WITNESSED**: explicit parent-worktree records the requested parent. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)
- **C023.02 / TODO**: worker-start --worktree new-child creates a child worktree. No live receipt establishes this predicate.

### C024 — runtime/dispatch-lifecycle.md:56

- **C024.01 / TODO**: worktree create without parent flags infers parent when caller context is available. No live receipt establishes this predicate.
- **C024.02 / TODO**: worktree create --no-parent records no parent. No live receipt establishes this predicate.

### C025 — runtime/dispatch-lifecycle.md:59

- **C025.01 / TODO**: worker-start exact existing worktree selector creates fresh terminal in that worktree. No live receipt establishes this predicate.
- **C025.02 / TODO**: worker-start rejects a bare repository id as a worktree selector. No live receipt establishes this predicate.
- **C025.03 / TODO**: active worktree selector can resolve to coordinator root. No live receipt establishes this predicate.

### C026 — runtime/dispatch-lifecycle.md:61

- **C026.01 / TODO**: fresh terminal session does not inherit builder conversation. No live receipt establishes this predicate.

### C028 — runtime/dispatch-lifecycle.md:65

- **C028.01 / TODO**: nested dispatch depth is counted from the issuing terminal. No live receipt establishes this predicate.
- **C028.02 / TODO**: default nested depth limit is one. No live receipt establishes this predicate.
- **C028.03 / TODO**: host setting can raise the nested depth limit. No live receipt establishes this predicate.

### C030 — runtime/dispatch-lifecycle.md:69

- **C030.01 / WITNESSED**: worktree create returns composite repoId::absolutePath id. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)
- **C030.02 / WITNESSED**: path:absolutePath selector addresses that worktree. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)
- **C030.03 / TODO**: full composite id selector addresses that worktree. No live receipt establishes this predicate.
- **C030.04 / TODO**: bare repo id is not a complete worktree selector. No live receipt establishes this predicate.

### C031 — runtime/dispatch-lifecycle.md:70

- **C031.01 / TODO**: on Linux outside managed terminals bare orca can name the GNOME screen reader. No live receipt establishes this predicate.
- **C031.02 / TODO**: orca-ide is the Linux IDE entrypoint in that installation. No live receipt establishes this predicate.

### C032 — runtime/dispatch-lifecycle.md:71

- **C032.01 / TODO**: worker-release preserves inspectable output. No live receipt establishes this predicate.
- **C032.02 / TODO**: worker-release closes the exact terminal owned by the Dispatch. No live receipt establishes this predicate.
- **C032.03 / TODO**: worker-retain retains the worker terminal. No live receipt establishes this predicate.

### C033 — runtime/dispatch-lifecycle.md:72

- **C033.01 / WITNESSED**: worker-release retained exits zero. [settle-release](receipts/settle-release.json), [settle-release-replay](receipts/settle-release-replay.json)
- **C033.02 / TODO**: worker-release release_pending exits zero. No live receipt establishes this predicate.
- **C033.03 / TODO**: worker-release already_released exits zero. No live receipt establishes this predicate.
- **C033.04 / WITNESSED**: repeating worker-release is idempotent. [settle-release](receipts/settle-release.json), [settle-release-replay](receipts/settle-release-replay.json)
- **C033.05 / TODO**: worker-release release_unknown exits one and supplies recovery. No live receipt establishes this predicate.

### C034 — runtime/dispatch-lifecycle.md:74

- **C034.01 / TODO**: settlement fences a former worker writer after terminal handle replacement. No live receipt establishes this predicate.

### C035 — runtime/dispatch-lifecycle.md:112

- **C035.01 / TODO**: run-create returns a Run id. No live receipt establishes this predicate.
- **C035.02 / WITNESSED**: task-list --run filters tasks to that Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C035.03 / WITNESSED**: worker-list --run filters workers to that Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C035.04 / WITNESSED**: bound coordinator check reads that Run mailbox. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C035.05 / TODO**: retired orchestration run alias returns recovery without scheduling. No live receipt establishes this predicate.
- **C035.06 / TODO**: retired coordinator-start alias returns recovery without scheduling. No live receipt establishes this predicate.

### C037 — runtime/dispatch-lifecycle.md:118

- **C037.01 / WITNESSED**: check returns oldest FIFO delivery. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)
- **C037.02 / WITNESSED**: a check delivery contains at most 50 messages. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)
- **C037.03 / WITNESSED**: unacknowledged delivery is replayed identically. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)
- **C037.04 / WITNESSED**: ack advances to the next delivery. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)

### C039 — runtime/dispatch-lifecycle.md:121

- **C039.01 / TODO**: task-list does not mark messages read. No live receipt establishes this predicate.
- **C039.02 / TODO**: inbox does not mark messages read. No live receipt establishes this predicate.
- **C039.03 / TODO**: dispatch-show does not mark messages read. No live receipt establishes this predicate.
- **C039.04 / TODO**: default check marks received messages read. No live receipt establishes this predicate.
- **C039.05 / TODO**: check --unread consumes received messages. No live receipt establishes this predicate.
- **C039.06 / TODO**: check --peek leaves received messages unread. No live receipt establishes this predicate.
- **C039.07 / TODO**: check --all reads history without consuming. No live receipt establishes this predicate.
- **C039.08 / TODO**: task-list --brief collapses whitespace. No live receipt establishes this predicate.
- **C039.09 / TODO**: task-list --brief truncates spec at 160 chars and sets spec_truncated. No live receipt establishes this predicate.

### C040 — runtime/dispatch-lifecycle.md:124

- **C040.01 / WITNESSED**: check wait emits keepalive on stderr. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)
- **C040.02 / WITNESSED**: check wait keeps stdout parseable without keepalive lines. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)
- **C040.03 / WITNESSED**: keepalive carries both _keepalive and deprecated _heartbeat. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)
- **C040.04 / PARTIAL-TODO**: check wait emits keepalive every 15 seconds. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)

### C041 — runtime/dispatch-lifecycle.md:126

- **C041.01 / TODO**: every orchestration mutation accepts retry-request. No live receipt establishes this predicate.
- **C041.02 / TODO**: same mutation retry request deduplicates dispatch. No live receipt establishes this predicate.
- **C041.03 / TODO**: request-show distinguishes completed, pending and absent requests. No live receipt establishes this predicate.

### C043 — runtime/dispatch-lifecycle.md:128

- **C043.01 / TODO**: group recipients are broadcast-only. No live receipt establishes this predicate.

### C044 — runtime/dispatch-lifecycle.md:128

- **C044.01 / TODO**: worker_done to group is rejected. No live receipt establishes this predicate.
- **C044.02 / TODO**: heartbeat to group is rejected. No live receipt establishes this predicate.
- **C044.03 / TODO**: merge_ready to group fans out. No live receipt establishes this predicate.

### C046 — runtime/dispatch-lifecycle.md:130

- **C046.01 / WITNESSED**: accepted owning worker_done completes its task without manual status update. [helper-check-1](receipts/helper-check-1.json), [helper-tasks-after-done](receipts/helper-tasks-after-done.json), [helper-dispatch-after-done](receipts/helper-dispatch-after-done.json)

### C047 — runtime/dispatch-lifecycle.md:132

- **C047.01 / TODO**: inject creates no dispatch message row. No live receipt establishes this predicate.
- **C047.02 / TODO**: inject creates no handoff message row. No live receipt establishes this predicate.
- **C047.03 / TODO**: send accepts type dispatch. No live receipt establishes this predicate.
- **C047.04 / TODO**: send accepts type handoff. No live receipt establishes this predicate.
- **C047.05 / TODO**: runtime does not generate merge_ready. No live receipt establishes this predicate.

### C048 — runtime/dispatch-lifecycle.md:138

- **C048.01 / WITNESSED**: worktree comment is stored and shown in workspace metadata. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)

### C049 — runtime/dispatch-lifecycle.md:138

- **C049.01 / WITNESSED**: worktree set updates comment. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)
- **C049.02 / WITNESSED**: worktree set updates workspace-status. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)

### C052 — runtime/dispatch-lifecycle.md:147

- **C052.01 / WITNESSED**: terminal close --worktree --all stops all owned workspace processes. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)
- **C052.02 / WITNESSED**: bulk close retires terminal surfaces. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)
- **C052.03 / TODO**: bulk close durably removes tabs layouts and resume records. No live receipt establishes this predicate.
- **C052.04 / WITNESSED**: worktree rm removes a clean owned scratch worktree. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)

### C053 — runtime/dispatch-lifecycle.md:149

- **C053.01 / TODO**: unconfirmed bulk PTY close reports unverifiable. No live receipt establishes this predicate.

### C055 — runtime/dispatch-lifecycle.md:156

- **C055.01 / TODO**: fresh worker-start per installed roster agent reports actual launch options and turn-start state. No live receipt establishes this predicate.

### C056 — runtime/dispatch-lifecycle.md:157

- **C056.01 / TODO**: low-level dispatch prompt stages and exact request replay are observable. No live receipt establishes this predicate.

### C058 — runtime/dispatch-lifecycle.md:158

- **C058.01 / WITNESSED**: check types wake delivers other message types in FIFO. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)
- **C058.02 / TODO**: scratch merge_ready group broadcast fanout is observable. No live receipt establishes this predicate.

### C059 — runtime/dispatch-lifecycle.md:159

- **C059.01 / WITNESSED**: task-create with bogus dependency is refused. [fixture2-missing-dep](receipts/fixture2-missing-dep.json), [fixture2-foreign-dep](receipts/fixture2-foreign-dep.json)

### C060 — runtime/dispatch-lifecycle.md:160

- **C060.01 / WITNESSED**: resolved gate marker presence in regenerated dispatch-show preamble is observable. [fixture2-gate-preamble-preview](receipts/fixture2-gate-preamble-preview.json), [helper-preamble](receipts/helper-preamble.json)

### C061 — runtime/evidence-manifest.md:12

- **C061.01 / TODO**: typed report-path is preserved in the worker_done payload. No live receipt establishes this predicate.

### C063 — runtime/gate-classification.md:8

- **C063.01 / WITNESSED**: worker ask creates a question message in owning Run. [helper-check-0](receipts/helper-check-0.json), [helper-tasks-during-ask](receipts/helper-tasks-during-ask.json), [helper-gates-during-ask](receipts/helper-gates-during-ask.json), [helper-reply](receipts/helper-reply.json), [helper-check-1](receipts/helper-check-1.json)

### C064 — runtime/gate-classification.md:8

- **C064.01 / TODO**: ask timeout leaves the question pending. No live receipt establishes this predicate.
- **C064.02 / TODO**: default ask timeout is 600000ms. No live receipt establishes this predicate.
- **C064.03 / TODO**: ask timeout cap is 1800000ms. No live receipt establishes this predicate.
- **C064.04 / TODO**: ask --resume continues the same question id. No live receipt establishes this predicate.
- **C064.05 / TODO**: a new ask creates a distinct question. No live receipt establishes this predicate.

### C065 — runtime/gate-classification.md:10

- **C065.01 / WITNESSED**: reply --id with body answers the specified question. [helper-check-0](receipts/helper-check-0.json), [helper-tasks-during-ask](receipts/helper-tasks-during-ask.json), [helper-gates-during-ask](receipts/helper-gates-during-ask.json), [helper-reply](receipts/helper-reply.json), [helper-check-1](receipts/helper-check-1.json)

### C066 — runtime/gate-classification.md:11

- **C066.01 / WITNESSED**: worker ask creates no DAG decision gate row. [helper-check-0](receipts/helper-check-0.json), [helper-tasks-during-ask](receipts/helper-tasks-during-ask.json), [helper-gates-during-ask](receipts/helper-gates-during-ask.json), [helper-reply](receipts/helper-reply.json), [helper-check-1](receipts/helper-check-1.json)

### C067 — runtime/gate-classification.md:13

- **C067.01 / TODO**: gate-create requires task. No live receipt establishes this predicate.
- **C067.02 / TODO**: gate-create requires question. No live receipt establishes this predicate.
- **C067.03 / WITNESSED**: gate-create blocks ready task. [fixture2-gate-create](receipts/fixture2-gate-create.json), [fixture2-gate-blocked](receipts/fixture2-gate-blocked.json), [fixture2-gate-resolve](receipts/fixture2-gate-resolve.json), [fixture2-gate-after](receipts/fixture2-gate-after.json)
- **C067.04 / WITNESSED**: gate-resolve clears the task hold. [fixture2-gate-create](receipts/fixture2-gate-create.json), [fixture2-gate-blocked](receipts/fixture2-gate-blocked.json), [fixture2-gate-resolve](receipts/fixture2-gate-resolve.json), [fixture2-gate-after](receipts/fixture2-gate-after.json)

### C068 — runtime/gate-classification.md:16

- **C068.01 / TODO**: ask options accepts CSV. No live receipt establishes this predicate.
- **C068.02 / WITNESSED**: gate-create options accepts JSON array. [fixture2-gate-create](receipts/fixture2-gate-create.json), [fixture2-gate-blocked](receipts/fixture2-gate-blocked.json), [fixture2-gate-resolve](receipts/fixture2-gate-resolve.json), [fixture2-gate-after](receipts/fixture2-gate-after.json)
- **C068.03 / TODO**: mixing option formats is refused. No live receipt establishes this predicate.

### C069 — runtime/gate-classification.md:20

- **C069.01 / WITNESSED**: gate-resolve does not add resolution to regenerated live preamble. [fixture2-gate-preamble-preview](receipts/fixture2-gate-preamble-preview.json), [helper-preamble](receipts/helper-preamble.json)
- **C069.02 / TODO**: worker-start original injected preamble omits resolved gate context. No live receipt establishes this predicate.
- **C069.03 / TODO**: low-level dispatch original injected preamble omits resolved gate context. No live receipt establishes this predicate.
- **C069.04 / TODO**: retired scheduler preamble injection differs from live path. No live receipt establishes this predicate.

### C073 — runtime/gate-classification.md:31

- **C073.01 / PARTIAL-TODO**: worker ask blocks until reply or timeout. [helper-check-0](receipts/helper-check-0.json), [helper-reply](receipts/helper-reply.json)
- **C073.02 / WITNESSED**: task stays dispatched during ask. [helper-check-0](receipts/helper-check-0.json), [helper-tasks-during-ask](receipts/helper-tasks-during-ask.json), [helper-gates-during-ask](receipts/helper-gates-during-ask.json), [helper-reply](receipts/helper-reply.json), [helper-check-1](receipts/helper-check-1.json)

### C076 — runtime/gate-classification.md:34

- **C076.01 / TODO**: check marks messages read on receive. No live receipt establishes this predicate.

### C078 — runtime/gate-classification.md:37

- **C078.01 / WITNESSED**: unresolved DAG gate keeps task blocked. [fixture2-gate-create](receipts/fixture2-gate-create.json), [fixture2-gate-blocked](receipts/fixture2-gate-blocked.json), [fixture2-gate-resolve](receipts/fixture2-gate-resolve.json), [fixture2-gate-after](receipts/fixture2-gate-after.json)

### C079 — runtime/gate-classification.md:97

- **C079.01 / TODO**: ask addresses coordinator identity rather than a human terminal role. No live receipt establishes this predicate.

### C081 — runtime/liveness-resume.md:3

- **C081.01 / TODO**: runtime warns on stalls without autonomously resolving them. No live receipt establishes this predicate.

### C082 — runtime/liveness-resume.md:4

- **C082.01 / TODO**: task and dispatch provenance persist in SQLite. No live receipt establishes this predicate.
- **C082.02 / TODO**: dispatch last_heartbeat_at persists across runtime restart. No live receipt establishes this predicate.
- **C082.03 / TODO**: dispatch failure_count persists across runtime restart. No live receipt establishes this predicate.
- **C082.04 / TODO**: worker_done payload persists across runtime restart. No live receipt establishes this predicate.

### C083 — runtime/liveness-resume.md:9

- **C083.01 / TODO**: runtime verifies taskId and dispatchId against the sending pane. No live receipt establishes this predicate.

### C084 — runtime/liveness-resume.md:10

- **C084.01 / TODO**: pane handle may change after restart. No live receipt establishes this predicate.
- **C084.02 / TODO**: lifecycle messages from a non-owning pane are ignored. No live receipt establishes this predicate.

### C085 — runtime/liveness-resume.md:12

- **C085.01 / TODO**: stale handle yields terminal_handle_stale. No live receipt establishes this predicate.
- **C085.02 / TODO**: terminal list resolves replacement handle after restart. No live receipt establishes this predicate.

### C086 — runtime/liveness-resume.md:18

- **C086.01 / WITNESSED**: worker-list enumerates runtime worker state. [helper-workers-bound](receipts/helper-workers-bound.json)

### C087 — runtime/liveness-resume.md:18

- **C087.01 / WITNESSED**: worker-list row has projection.liveness. [helper-workers-bound](receipts/helper-workers-bound.json)
- **C087.02 / WITNESSED**: worker-list row has projection.attention.categories. [helper-workers-bound](receipts/helper-workers-bound.json)
- **C087.03 / WITNESSED**: worker-list row has projection.attention.requiresAction. [helper-workers-bound](receipts/helper-workers-bound.json)
- **C087.04 / WITNESSED**: worker-list row has projection.nextAction.argv. [helper-workers-bound](receipts/helper-workers-bound.json)
- **C087.05 / TODO**: worker-show observation.status describes PTY liveness. No live receipt establishes this predicate.
- **C087.06 / TODO**: a trust-blocked agent can retain a live PTY observation. No live receipt establishes this predicate.

### C090 — runtime/liveness-resume.md:25

- **C090.01 / PATCHED**: unscoped worker-list always reports every runtime Dispatch as original prose asserts. [helper-workers-bound](receipts/helper-workers-bound.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json)

### C093 — runtime/liveness-resume.md:33

- **C093.01 / WITNESSED**: missing_status yields unverifiable. [helper-workers-bound](receipts/helper-workers-bound.json)
- **C093.02 / TODO**: stale_status yields unverifiable. No live receipt establishes this predicate.
- **C093.03 / TODO**: restored_unconfirmed yields unverifiable. No live receipt establishes this predicate.
- **C093.04 / TODO**: host_unavailable yields unverifiable. No live receipt establishes this predicate.
- **C093.05 / TODO**: disconnected remote worker yields unverifiable. No live receipt establishes this predicate.

### C096 — runtime/liveness-resume.md:42

- **C096.01 / WITNESSED**: empty check wait timeout returns count zero without command error. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)
- **C096.02 / WITNESSED**: types selects wake condition while delivery includes all FIFO types. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)

### C097 — runtime/liveness-resume.md:44

- **C097.01 / WITNESSED**: keepalive appears only on stderr. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)

### C101 — runtime/liveness-resume.md:52

- **C101.01 / TODO**: worker-start retry-of targets a prior failed dispatch. No live receipt establishes this predicate.
- **C101.02 / TODO**: typed refusal exposes task_not_found. No live receipt establishes this predicate.
- **C101.03 / TODO**: typed refusal exposes task_not_startable with unmetDependencies. No live receipt establishes this predicate.
- **C101.04 / TODO**: typed refusal exposes inject_rejected. No live receipt establishes this predicate.
- **C101.05 / TODO**: typed refusal exposes nested_worker_depth_exceeded. No live receipt establishes this predicate.
- **C101.06 / PARTIAL-TODO**: typed refusal exposes consumer_fenced. [fixture-create-foreign](receipts/fixture-create-foreign.json)
- **C101.07 / TODO**: typed refusal exposes dispatch_inactive. No live receipt establishes this predicate.
- **C101.08 / TODO**: typed refusal carries nextSteps where supplied. No live receipt establishes this predicate.

### C105 — runtime/liveness-resume.md:64

- **C105.01 / TODO**: three consecutive dispatch failures trip task circuit break. No live receipt establishes this predicate.

### C109 — runtime/liveness-resume.md:70

- **C109.01 / PATCHED**: regenerated dispatch preamble is the exact original request payload as prose asserts. [helper-regenerated-retry](receipts/helper-regenerated-retry.json)
- **C109.02 / PATCHED**: retry shorthand without original text and Enter succeeds as prose asserts. [retry-original-id-shorthand](receipts/retry-original-id-shorthand.json), [retry-original-id-text-only](receipts/retry-original-id-text-only.json), [retry-original-exact](receipts/retry-original-exact.json)

### C110 — runtime/liveness-resume.md:72

- **C110.01 / TODO**: terminal send timeout returns input accepted. No live receipt establishes this predicate.
- **C110.02 / WITNESSED**: terminal send retry never resends. [effect-original-send](receipts/effect-original-send.json), [effect-before-replay](receipts/effect-before-replay.json), [effect-original-replay](receipts/effect-original-replay.json), [effect-after-replay](receipts/effect-after-replay.json), [retry-original-exact](receipts/retry-original-exact.json)

### C111 — runtime/liveness-resume.md:73

- **C111.01 / WITNESSED**: input accepted alone does not demonstrate a started agent turn. [effect-original-send](receipts/effect-original-send.json), [effect-before-replay](receipts/effect-before-replay.json), [effect-original-replay](receipts/effect-original-replay.json), [effect-after-replay](receipts/effect-after-replay.json), [retry-original-exact](receipts/retry-original-exact.json)

### C112 — runtime/liveness-resume.md:76

- **C112.01 / TODO**: worker-show human prompt uses observation.agentWait. No live receipt establishes this predicate.
- **C112.02 / TODO**: absent agentWait differs from explicit null. No live receipt establishes this predicate.

### C113 — runtime/liveness-resume.md:78

- **C113.01 / TODO**: orchestration reset discards task and dispatch state. No live receipt establishes this predicate.

### C115 — runtime/liveness-resume.md:94

- **C115.01 / WITNESSED**: missing dependency is rejected with dependency must belong to Run error. [fixture2-missing-dep](receipts/fixture2-missing-dep.json), [fixture2-foreign-dep](receipts/fixture2-foreign-dep.json)
- **C115.02 / WITNESSED**: foreign-Run dependency is rejected with dependency must belong to Run error. [fixture2-missing-dep](receipts/fixture2-missing-dep.json), [fixture2-foreign-dep](receipts/fixture2-foreign-dep.json)

### C117 — runtime/liveness-resume.md:98

- **C117.01 / WITNESSED**: completing dependency promotes its pending child. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C117.02 / TODO**: promotion requires all dependencies completed. No live receipt establishes this predicate.

### C118 — runtime/liveness-resume.md:99

- **C118.01 / WITNESSED**: failed dependency leaves child pending at observation. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C118.02 / TODO**: pending failed-dependency child never self-promotes. No live receipt establishes this predicate.
- **C118.03 / TODO**: runtime convergence detection flags blocked but not pending. No live receipt establishes this predicate.

### C121 — runtime/liveness-resume.md:102

- **C121.01 / WITNESSED**: deps stores dependency edges. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C121.02 / WITNESSED**: parent_id exists independently of deps. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)

### C122 — runtime/liveness-resume.md:107

- **C122.01 / WITNESSED**: single runtime stores tasks from multiple Runs. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)

### C123 — runtime/liveness-resume.md:107

- **C123.01 / WITNESSED**: task-list run filtering honors exact Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C123.02 / WITNESSED**: worker-list run filtering honors exact Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C123.03 / WITNESSED**: bound check honors exact Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)

### C126 — runtime/liveness-resume.md:137

- **C126.01 / TODO**: run-use binds an existing Run to caller. No live receipt establishes this predicate.
- **C126.02 / TODO**: takeover-legacy preserves live worker Dispatches. No live receipt establishes this predicate.
- **C126.03 / TODO**: takeover-legacy preserves worker processes. No live receipt establishes this predicate.
- **C126.04 / TODO**: takeover-legacy preserves worker filesystems. No live receipt establishes this predicate.
- **C126.05 / TODO**: takeover-legacy routes subsequent questions to new coordinator. No live receipt establishes this predicate.

### C127 — runtime/liveness-resume.md:141

- **C127.01 / TODO**: re-attaching Dispatch surfaces consumer_fenced. No live receipt establishes this predicate.
- **C127.02 / TODO**: old coordinator mutations are fenced after adoption. No live receipt establishes this predicate.

### C128 — runtime/liveness-resume.md:142

- **C128.01 / TODO**: run-use cannot nominate adopter using from flag. No live receipt establishes this predicate.
- **C128.02 / TODO**: run_legacy_local is empty tombstone. No live receipt establishes this predicate.
- **C128.03 / TODO**: recovered Run has documented objective name. No live receipt establishes this predicate.

### C131 — runtime/merge-serialization.md:9

- **C131.01 / TODO**: merge_ready send requires subject. No live receipt establishes this predicate.
- **C131.02 / TODO**: merge_ready accepts JSON payload. No live receipt establishes this predicate.
- **C131.03 / TODO**: merge_ready delivers without built-in merge action. No live receipt establishes this predicate.

### C132 — runtime/merge-serialization.md:17

- **C132.01 / WITNESSED**: omitted recipient from active Dispatch routes to owning Run. [helper-check-1](receipts/helper-check-1.json), [helper-tasks-after-done](receipts/helper-tasks-after-done.json), [helper-dispatch-after-done](receipts/helper-dispatch-after-done.json)

### C134 — runtime/merge-serialization.md:21

- **C134.01 / TODO**: group merge_ready is permitted. No live receipt establishes this predicate.
- **C134.02 / TODO**: group worker_done is rejected. No live receipt establishes this predicate.
- **C134.03 / TODO**: group heartbeat is rejected. No live receipt establishes this predicate.

### C137 — runtime/merge-serialization.md:28

- **C137.01 / WITNESSED**: types wake returns whole FIFO delivery. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)

### C140 — runtime/mission-scheduling.md:3

- **C140.01 / TODO**: automation accepts cron schedule. No live receipt establishes this predicate.
- **C140.02 / TODO**: automation accepts hourly schedule. No live receipt establishes this predicate.
- **C140.03 / TODO**: automation accepts daily schedule. No live receipt establishes this predicate.
- **C140.04 / TODO**: automation accepts weekdays schedule. No live receipt establishes this predicate.
- **C140.05 / TODO**: automation accepts weekly schedule. No live receipt establishes this predicate.
- **C140.06 / TODO**: automation accepts RRULE schedule. No live receipt establishes this predicate.
- **C140.07 / TODO**: automation can target fresh per-run worktree. No live receipt establishes this predicate.
- **C140.08 / TODO**: automation can target existing workspace. No live receipt establishes this predicate.

### C142 — runtime/mission-scheduling.md:11

- **C142.01 / TODO**: automation create accepts name trigger time timezone precheck prompt provider and repo flags. No live receipt establishes this predicate.

### C143 — runtime/mission-scheduling.md:17

- **C143.01 / TODO**: repo automation creates fresh worktree per run. No live receipt establishes this predicate.
- **C143.02 / TODO**: workspace automation targets existing workspace. No live receipt establishes this predicate.
- **C143.03 / TODO**: disabled automation does not fire schedule. No live receipt establishes this predicate.

### C145 — runtime/mission-scheduling.md:23

- **C145.01 / TODO**: automation runs precheck before agent launch. No live receipt establishes this predicate.
- **C145.02 / TODO**: precheck exit zero permits run. No live receipt establishes this predicate.
- **C145.03 / TODO**: nonzero precheck records skipped run. No live receipt establishes this predicate.
- **C145.04 / TODO**: nonzero precheck spawns no agent. No live receipt establishes this predicate.

### C147 — runtime/mission-scheduling.md:32

- **C147.01 / TODO**: create and edit accept timezone. No live receipt establishes this predicate.
- **C147.02 / TODO**: missed-run-grace-minutes drops overly late fires. No live receipt establishes this predicate.
- **C147.03 / TODO**: reuse-session reuses existing-workspace session. No live receipt establishes this predicate.
- **C147.04 / TODO**: fresh-session starts new existing-workspace session. No live receipt establishes this predicate.
- **C147.05 / TODO**: host runtime:environment-id places on paired server. No live receipt establishes this predicate.

### C148 — runtime/mission-scheduling.md:40

- **C148.01 / TODO**: automations run fires a saved automation now. No live receipt establishes this predicate.
- **C148.02 / TODO**: automations runs returns history including skipped runs. No live receipt establishes this predicate.

### C149 — runtime/orca-dag-semantics.md:3

- **C149.01 / TODO**: CLI run/task/worker/check/send supports manual orchestration. No live receipt establishes this predicate.

### C151 — runtime/orca-dag-semantics.md:6

- **C151.01 / TODO**: installed runtime orchestration schema line is v40. No live receipt establishes this predicate.

### C152 — runtime/orca-dag-semantics.md:10

- **C152.01 / TODO**: run-create creates a namespace. No live receipt establishes this predicate.
- **C152.02 / WITNESSED**: run-use binds namespace. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C152.03 / WITNESSED**: run-current returns current binding. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C152.04 / TODO**: run-list lists namespaces. No live receipt establishes this predicate.
- **C152.05 / TODO**: run-show returns namespace provenance. No live receipt establishes this predicate.

### C153 — runtime/orca-dag-semantics.md:11

- **C153.01 / PARTIAL-TODO**: every created task belongs to one Run. [fixture2-create-good-child](receipts/fixture2-create-good-child.json)
- **C153.02 / WITNESSED**: task-list --run honors Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C153.03 / WITNESSED**: worker-list --run honors Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)
- **C153.04 / WITNESSED**: coordinator check honors bound Run. [fixture2-bind-a](receipts/fixture2-bind-a.json), [fixture2-bind-b](receipts/fixture2-bind-b.json), [fixture2-run-current](receipts/fixture2-run-current.json), [fixture2-deps-after](receipts/fixture2-deps-after.json), [fixture2-run-b-before](receipts/fixture2-run-b-before.json), [teardown-tasks-before-b](receipts/teardown-tasks-before-b.json), [helper-workers-explicit-a](receipts/helper-workers-explicit-a.json), [helper-workers-explicit-b](receipts/helper-workers-explicit-b.json), [mailbox-delivery](receipts/mailbox-delivery.json)

### C154 — runtime/orca-dag-semantics.md:12

- **C154.01 / TODO**: retired orchestration run performs no scheduling effects. No live receipt establishes this predicate.
- **C154.02 / TODO**: retired coordinator-start performs no scheduling effects. No live receipt establishes this predicate.
- **C154.03 / TODO**: retired coordinator-stop performs no scheduling effects. No live receipt establishes this predicate.
- **C154.04 / TODO**: retired aliases return current-skill recovery. No live receipt establishes this predicate.

### C155 — runtime/orca-dag-semantics.md:17

- **C155.01 / TODO**: unscoped task-list exposes tasks across historical Runs. No live receipt establishes this predicate.
- **C155.02 / TODO**: runtime does not automatically prune old tasks. No live receipt establishes this predicate.

### C157 — runtime/orca-dag-semantics.md:21

- **C157.01 / TODO**: new Run does not reset issuing worker nested depth. No live receipt establishes this predicate.
- **C157.02 / TODO**: worker-start at default worker depth returns nested_worker_depth_exceeded. No live receipt establishes this predicate.

### C158 — runtime/orca-dag-semantics.md:27

- **C158.01 / WITNESSED**: tasks.deps is dependency promotion graph. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C158.02 / WITNESSED**: task-create --parent writes parent_id. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C158.03 / TODO**: worker-start --parent writes parent_id. No live receipt establishes this predicate.
- **C158.04 / TODO**: parent id is validated to same Run. No live receipt establishes this predicate.
- **C158.05 / TODO**: worker terminal listing reads parent_id. No live receipt establishes this predicate.
- **C158.06 / TODO**: attention queries read parent_id. No live receipt establishes this predicate.

### C160 — runtime/orca-dag-semantics.md:39

- **C160.01 / TODO**: CLI runtime does not generate dispatch and handoff message types. No live receipt establishes this predicate.

### C163 — runtime/orca-dag-semantics.md:43

- **C163.01 / TODO**: dispatch inject writes prompt to PTY. No live receipt establishes this predicate.
- **C163.02 / TODO**: dispatch inject adds no dispatch message row. No live receipt establishes this predicate.

### C165 — runtime/orca-dag-semantics.md:44

- **C165.01 / TODO**: runtime does not generate handoff messages. No live receipt establishes this predicate.

### C166 — runtime/orca-dag-semantics.md:46

- **C166.01 / TODO**: runtime delivers fleet-written merge_ready. No live receipt establishes this predicate.
- **C166.02 / TODO**: merge_ready causes no built-in merge behavior. No live receipt establishes this predicate.

### C168 — runtime/orca-dag-semantics.md:49

- **C168.01 / TODO**: send accepts worker_done type. No live receipt establishes this predicate.
- **C168.02 / TODO**: send accepts merge_ready type. No live receipt establishes this predicate.
- **C168.03 / TODO**: send accepts heartbeat type. No live receipt establishes this predicate.
- **C168.04 / TODO**: send accepts question type. No live receipt establishes this predicate.
- **C168.05 / TODO**: send accepts escalation type. No live receipt establishes this predicate.
- **C168.06 / TODO**: send accepts status type. No live receipt establishes this predicate.
- **C168.07 / TODO**: send accepts decision_gate type. No live receipt establishes this predicate.
- **C168.08 / TODO**: send accepts dispatch type. No live receipt establishes this predicate.
- **C168.09 / TODO**: send accepts handoff type. No live receipt establishes this predicate.
- **C168.10 / TODO**: legacy direct-ask writes decision_gate. No live receipt establishes this predicate.
- **C168.11 / TODO**: migration converts old decision_gate to status. No live receipt establishes this predicate.
- **C168.12 / TODO**: runtime does not generate dispatch. No live receipt establishes this predicate.
- **C168.13 / TODO**: runtime does not generate handoff. No live receipt establishes this predicate.

### C169 — runtime/orca-dag-semantics.md:57

- **C169.01 / WITNESSED**: types controls wake rather than filtering delivery. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)

### C172 — runtime/orca-dag-semantics.md:66

- **C172.01 / WITNESSED**: check delivery is FIFO. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)
- **C172.02 / WITNESSED**: check batch maximum is 50. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)
- **C172.03 / WITNESSED**: delivery replay is identical until ack. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)
- **C172.04 / TODO**: delivery survives coordinator crash after receive. No live receipt establishes this predicate.

### C174 — runtime/orca-dag-semantics.md:69

- **C174.01 / TODO**: every mutation accepts retry-request. No live receipt establishes this predicate.
- **C174.02 / TODO**: request-show inspects request. No live receipt establishes this predicate.
- **C174.03 / TODO**: same request id deduplicates dispatch. No live receipt establishes this predicate.

### C175 — runtime/orca-dag-semantics.md:74

- **C175.01 / PARTIAL-TODO**: task status is overwritten in place. [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C175.02 / PARTIAL-TODO**: pending to ready promotion creates no timestamp. [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C175.03 / TODO**: pending to ready promotion creates no message. No live receipt establishes this predicate.

### C176 — runtime/orca-dag-semantics.md:75

- **C176.01 / TODO**: dispatch attempts can be reconstructed from records. No live receipt establishes this predicate.
- **C176.02 / TODO**: latest dispatch is active. No live receipt establishes this predicate.
- **C176.03 / TODO**: failure_count carries maximum forward. No live receipt establishes this predicate.
- **C176.04 / TODO**: failure circuit trips at three. No live receipt establishes this predicate.
- **C176.05 / TODO**: worker_done records completion. No live receipt establishes this predicate.

### C177 — runtime/orca-dag-semantics.md:81

- **C177.01 / WITNESSED**: owning pane worker_done auto-completes task. [helper-check-1](receipts/helper-check-1.json), [helper-tasks-after-done](receipts/helper-tasks-after-done.json), [helper-dispatch-after-done](receipts/helper-dispatch-after-done.json)

### C178 — runtime/orca-dag-semantics.md:82

- **C178.01 / TODO**: restart re-attachment surfaces consumer_fenced. No live receipt establishes this predicate.
- **C178.02 / TODO**: old binding cannot mutate after new binding adoption. No live receipt establishes this predicate.

### C183 — runtime/orca-dag-semantics.md:94

- **C183.01 / WITNESSED**: failed-dependency child remains pending. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C183.02 / TODO**: missing dependency cannot newly be created but legacy imported missing-dependency child cannot promote. No live receipt establishes this predicate.

### C185 — runtime/orca-dag-semantics.md:103

- **C185.01 / WITNESSED**: worker ask writes question to owning Run. [helper-check-0](receipts/helper-check-0.json), [helper-tasks-during-ask](receipts/helper-tasks-during-ask.json), [helper-gates-during-ask](receipts/helper-gates-during-ask.json), [helper-reply](receipts/helper-reply.json), [helper-check-1](receipts/helper-check-1.json)
- **C185.02 / TODO**: coordinator ask writes question to owning Run. No live receipt establishes this predicate.

### C186 — runtime/orca-dag-semantics.md:103

- **C186.01 / PARTIAL-TODO**: ask blocks until reply or timeout. [helper-check-0](receipts/helper-check-0.json), [helper-reply](receipts/helper-reply.json)
- **C186.02 / TODO**: timeout leaves question pending. No live receipt establishes this predicate.
- **C186.03 / TODO**: resume preserves question id. No live receipt establishes this predicate.

### C187 — runtime/orca-dag-semantics.md:105

- **C187.01 / WITNESSED**: ask does not change dispatched task to blocked. [helper-check-0](receipts/helper-check-0.json), [helper-tasks-during-ask](receipts/helper-tasks-during-ask.json), [helper-gates-during-ask](receipts/helper-gates-during-ask.json), [helper-reply](receipts/helper-reply.json), [helper-check-1](receipts/helper-check-1.json)

### C189 — runtime/orca-dag-semantics.md:107

- **C189.01 / WITNESSED**: gate-create blocks task. [fixture2-gate-create](receipts/fixture2-gate-create.json), [fixture2-gate-blocked](receipts/fixture2-gate-blocked.json), [fixture2-gate-resolve](receipts/fixture2-gate-resolve.json), [fixture2-gate-after](receipts/fixture2-gate-after.json)
- **C189.02 / WITNESSED**: gate-resolve unblocks task. [fixture2-gate-create](receipts/fixture2-gate-create.json), [fixture2-gate-blocked](receipts/fixture2-gate-blocked.json), [fixture2-gate-resolve](receipts/fixture2-gate-resolve.json), [fixture2-gate-after](receipts/fixture2-gate-after.json)

### C190 — runtime/orca-dag-semantics.md:113

- **C190.01 / WITNESSED**: worker ask keeps task dispatched. [helper-check-0](receipts/helper-check-0.json), [helper-tasks-during-ask](receipts/helper-tasks-during-ask.json), [helper-gates-during-ask](receipts/helper-gates-during-ask.json), [helper-reply](receipts/helper-reply.json), [helper-check-1](receipts/helper-check-1.json)
- **C190.02 / TODO**: check reads ask message without answering it. No live receipt establishes this predicate.

### C195 — runtime/orca-dag-semantics.md:115

- **C195.01 / WITNESSED**: DAG task is blocked until gate resolution. [fixture2-gate-create](receipts/fixture2-gate-create.json), [fixture2-gate-blocked](receipts/fixture2-gate-blocked.json), [fixture2-gate-resolve](receipts/fixture2-gate-resolve.json), [fixture2-gate-after](receipts/fixture2-gate-after.json)

### C196 — runtime/orca-dag-semantics.md:123

- **C196.01 / TODO**: worker_done.payload is stored as free-form TEXT. No live receipt establishes this predicate.
- **C196.02 / TODO**: tasks.result is stored as free-form TEXT. No live receipt establishes this predicate.

### C198 — runtime/orca-dag-semantics.md:126

- **C198.01 / TODO**: PowerShell raw payload quoting can strip JSON quotes. No live receipt establishes this predicate.

### C199 — runtime/sandbox-policy.md:4

- **C199.01 / TODO**: Orca autonomous argument map is upstream tui-agent-permissions.ts. No live receipt establishes this predicate.

### C200 — runtime/sandbox-policy.md:6

- **C200.01 / TODO**: claude acceptEdits can prompt on shell or network. No live receipt establishes this predicate.
- **C200.02 / TODO**: codex workspace-write can prompt on shell or network. No live receipt establishes this predicate.
- **C200.03 / TODO**: gemini auto_edit can prompt on shell or network. No live receipt establishes this predicate.

### C201 — runtime/sandbox-policy.md:11

- **C201.01 / TODO**: worker-start appends host agentDefaultArgs setting. No live receipt establishes this predicate.

### C202 — runtime/sandbox-policy.md:12

- **C202.01 / TODO**: migrated default argument map equals YOLO map. No live receipt establishes this predicate.
- **C202.02 / TODO**: manual host mode uses empty default args. No live receipt establishes this predicate.

### C203 — runtime/sandbox-policy.md:14

- **C203.01 / TODO**: default supervised launch of ro request may receive bypass default args. No live receipt establishes this predicate.
- **C203.02 / TODO**: manual host launch can require human permission prompts. No live receipt establishes this predicate.

### C207 — runtime/sandbox-policy.md:22

- **C207.01 / TODO**: Orca argument map contains autonomous flags and no native read-only tier. No live receipt establishes this predicate.

### C212 — runtime/sandbox-policy.md:30

- **C212.01 / TODO**: claude native plan flag is accepted. No live receipt establishes this predicate.
- **C212.02 / TODO**: claude autonomous skip-permissions flag is accepted. No live receipt establishes this predicate.

### C213 — runtime/sandbox-policy.md:31

- **C213.01 / TODO**: codex native sandbox read-only flag is accepted. No live receipt establishes this predicate.
- **C213.02 / TODO**: codex bypass-approvals-and-sandbox flag is accepted. No live receipt establishes this predicate.

### C214 — runtime/sandbox-policy.md:32

- **C214.01 / TODO**: gemini native plan flag is accepted. No live receipt establishes this predicate.
- **C214.02 / TODO**: gemini yolo flag is accepted. No live receipt establishes this predicate.

### C215 — runtime/sandbox-policy.md:33

- **C215.01 / TODO**: cursor autonomous flag is yolo. No live receipt establishes this predicate.

### C216 — runtime/sandbox-policy.md:34

- **C216.01 / TODO**: grok autonomous flag is permission-mode bypassPermissions. No live receipt establishes this predicate.

### C217 — runtime/sandbox-policy.md:35

- **C217.01 / TODO**: droid autonomous flag is auto high. No live receipt establishes this predicate.

### C218 — runtime/sandbox-policy.md:36

- **C218.01 / TODO**: Orca strips dangerously-skip-permissions from opencode. No live receipt establishes this predicate.
- **C218.02 / TODO**: Orca strips dangerously-skip-permissions from kilo. No live receipt establishes this predicate.

### C219 — runtime/sandbox-policy.md:37

- **C219.01 / TODO**: omp absent from Orca autonomous argument map. No live receipt establishes this predicate.
- **C219.02 / TODO**: pi absent from Orca autonomous argument map. No live receipt establishes this predicate.

### C220 — runtime/sandbox-policy.md:39

- **C220.01 / TODO**: native read-only mode cannot mutate. No live receipt establishes this predicate.
- **C220.02 / TODO**: native read-only mode is non-blocking. No live receipt establishes this predicate.

### C222 — runtime/sandbox-policy.md:67

- **C222.01 / TODO**: recipe create lifecycle is supported. No live receipt establishes this predicate.
- **C222.02 / TODO**: recipe suspend lifecycle is supported. No live receipt establishes this predicate.
- **C222.03 / TODO**: recipe resume lifecycle is supported. No live receipt establishes this predicate.
- **C222.04 / TODO**: recipe destroy lifecycle is supported. No live receipt establishes this predicate.
- **C222.05 / TODO**: serve recipe-json pairs environment. No live receipt establishes this predicate.
- **C222.06 / TODO**: doctor provision validates recipe. No live receipt establishes this predicate.
- **C222.07 / TODO**: doctor connect is synonym for provision. No live receipt establishes this predicate.

### C223 — runtime/sandbox-policy.md:73

- **C223.01 / TODO**: recipe doctor can report warnings with ok true. No live receipt establishes this predicate.
- **C223.02 / TODO**: doctor provision produces verdict consumed by sandbox_doctor. No live receipt establishes this predicate.

### C225 — runtime/sandbox-policy.md:80

- **C225.01 / TODO**: snapshot after serve duplicates pairing identity. No live receipt establishes this predicate.
- **C225.02 / TODO**: duplicated identity causes wrong-host placement ambiguity. No live receipt establishes this predicate.

### C227 — runtime/scripts/deny-hook.sh:37

- **C227.01 / TODO**: orchestration reset discards fleet Dispatch state. No live receipt establishes this predicate.

### C228 — runtime/scripts/deny-hook.sh:721

- **C228.01 / TODO**: orchestration reset discards fleet Dispatch state. No live receipt establishes this predicate.

### C230 — runtime/scripts/pm.py:2

- **C230.01 / PARTIAL-TODO**: check keepalive appears on stderr every 15 seconds. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)

### C232 — runtime/scripts/pm.py:8

- **C232.01 / WITNESSED**: keepalive carries both markers with heartbeat as deprecated alias. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)

### C233 — runtime/scripts/pm.py:21

- **C233.01 / TODO**: inbox JSON can be consumed by local parser. No live receipt establishes this predicate.

### C234 — runtime/scripts/pm.py:91

- **C234.01 / WITNESSED**: check JSON returns result.messages list. [mailbox-delivery](receipts/mailbox-delivery.json), [mailbox-replay](receipts/mailbox-replay.json), [mailbox-ack](receipts/mailbox-ack.json), [mailbox-final-ack](receipts/mailbox-final-ack.json)

### C235 — runtime/scripts/pm.py:98

- **C235.01 / WITNESSED**: check keepalive carries current _keepalive and alias _heartbeat. [mailbox-empty-wait](receipts/mailbox-empty-wait.json)

### C245 — runtime/scripts/spawn_worker.sh:4

- **C245.01 / TODO**: v1.4.199 worker-start composes placement and dispatch. No live receipt establishes this predicate.
- **C245.02 / TODO**: v1.4.199 ready requires accepted write only. No live receipt establishes this predicate.

### C246 — runtime/scripts/spawn_worker.sh:9

- **C246.01 / PARTIAL-TODO**: v1.4.200 readiness requires observed turn_started. [helper-start](receipts/helper-start.json)
- **C246.02 / TODO**: unproven turn start returns outcome_unknown. No live receipt establishes this predicate.

### C247 — runtime/scripts/spawn_worker.sh:11

- **C247.01 / PARTIAL-TODO**: refusals report typed error.code. [fixture-create-foreign](receipts/fixture-create-foreign.json), [fixture2-missing-dep](receipts/fixture2-missing-dep.json)
- **C247.02 / TODO**: nextSteps contains runtime recovery where available. No live receipt establishes this predicate.

### C250 — runtime/scripts/spawn_worker.sh:24

- **C250.01 / TODO**: dispatch inject submits preamble. No live receipt establishes this predicate.
- **C250.02 / TODO**: dispatch inject returns prompt.requestId. No live receipt establishes this predicate.
- **C250.03 / TODO**: dispatch inject returns prompt.stages. No live receipt establishes this predicate.

### C251 — runtime/scripts/spawn_worker.sh:29

- **C251.01 / WITNESSED**: retry shorthand is a replay operation once original text and Enter preconditions are supplied. [effect-original-send](receipts/effect-original-send.json), [effect-before-replay](receipts/effect-before-replay.json), [effect-original-replay](receipts/effect-original-replay.json), [effect-after-replay](receipts/effect-after-replay.json), [retry-original-exact](receipts/retry-original-exact.json)
- **C251.02 / TODO**: retry wait timeout returns input acceptance without resend. No live receipt establishes this predicate.

### C252 — runtime/scripts/spawn_worker.sh:33

- **C252.01 / WITNESSED**: terminal retry requires text plus Enter. [retry-original-id-shorthand](receipts/retry-original-id-shorthand.json), [retry-original-id-text-only](receipts/retry-original-id-text-only.json), [helper-regenerated-retry](receipts/helper-regenerated-retry.json)
- **C252.02 / WITNESSED**: dispatch-show can regenerate preamble. [helper-preamble](receipts/helper-preamble.json)
- **C252.03 / TODO**: regenerated preamble byte-matches original low-level dispatch prompt. No live receipt establishes this predicate.
- **C252.04 / PARTIAL-TODO**: terminal wait returns wait.satisfied false for an unmet condition. [scratch-wait-unsatisfied](receipts/scratch-wait-unsatisfied.json), [scratch-wait-exit-2s](receipts/scratch-wait-exit-2s.json)

### C253 — runtime/scripts/spawn_worker.sh:40

- **C253.01 / PARTIAL-TODO**: terminal wait unsatisfied result exits one. [scratch-wait-unsatisfied](receipts/scratch-wait-unsatisfied.json), [scratch-wait-exit-2s](receipts/scratch-wait-exit-2s.json)
- **C253.02 / TODO**: worker-start launch args inherit agentDefaultArgs. No live receipt establishes this predicate.
- **C253.03 / TODO**: migrated default args are YOLO map. No live receipt establishes this predicate.

### C254 — runtime/scripts/spawn_worker.sh:46

- **C254.01 / TODO**: manual host has empty agentDefaultArgs. No live receipt establishes this predicate.

### C255 — runtime/scripts/spawn_worker.sh:69

- **C255.01 / TODO**: claude plan and skip-permissions map are supported. No live receipt establishes this predicate.
- **C255.02 / TODO**: codex read-only and bypass map are supported. No live receipt establishes this predicate.
- **C255.03 / TODO**: gemini plan and yolo map are supported. No live receipt establishes this predicate.
- **C255.04 / TODO**: cursor yolo map is supported. No live receipt establishes this predicate.
- **C255.05 / TODO**: grok bypassPermissions map is supported. No live receipt establishes this predicate.
- **C255.06 / TODO**: droid auto high map is supported. No live receipt establishes this predicate.
- **C255.07 / TODO**: opencode and kilo strip skip-permissions. No live receipt establishes this predicate.
- **C255.08 / TODO**: omp and pi lack default autonomous argument mapping. No live receipt establishes this predicate.
- **C255.09 / TODO**: worker-start model and effort target supported providers. No live receipt establishes this predicate.
- **C255.10 / TODO**: worker-start effort requires model. No live receipt establishes this predicate.

### C256 — runtime/scripts/spawn_worker.sh:91

- **C256.01 / WITNESSED**: worktree id is composite repoId::absolutePath. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)
- **C256.02 / WITNESSED**: path:absolutePath selector resolves worktree. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)

### C259 — runtime/scripts/spawn_worker.sh:217

- **C259.01 / WITNESSED**: orca --version emits a version-shaped token. [version](receipts/version.json)

### C262 — runtime/scripts/spawn_worker.sh:276

- **C262.01 / TODO**: doctor provision is available in plain form. No live receipt establishes this predicate.
- **C262.02 / TODO**: doctor JSON flag is version-dependent. No live receipt establishes this predicate.

### C267 — runtime/scripts/spawn_worker.sh:375

- **C267.01 / WITNESSED**: task-list returns task deps and status. [fixture2-create-good-child](receipts/fixture2-create-good-child.json), [fixture2-deps-before](receipts/fixture2-deps-before.json), [fixture2-complete-good](receipts/fixture2-complete-good.json), [fixture2-fail-bad](receipts/fixture2-fail-bad.json), [fixture2-deps-after](receipts/fixture2-deps-after.json)
- **C267.02 / PARTIAL-TODO**: deps represents dependency identifiers as array or JSON-encoded array. [fixture2-deps-after](receipts/fixture2-deps-after.json)

### C270 — runtime/scripts/spawn_worker.sh:438

- **C270.01 / TODO**: supervised worker-start inherits host default arguments. No live receipt establishes this predicate.

### C271 — runtime/scripts/spawn_worker.sh:446

- **C271.01 / TODO**: worker-start fresh path composes placement and readiness and dispatch. No live receipt establishes this predicate.
- **C271.02 / TODO**: worker-start rejects name on current or existing worktree. No live receipt establishes this predicate.
- **C271.03 / TODO**: worker-start failure and unknown states both can exit nonzero. No live receipt establishes this predicate.

### C272 — runtime/scripts/spawn_worker.sh:457

- **C272.01 / TODO**: worker-start accepts task worktree and agent arguments. No live receipt establishes this predicate.

### C274 — runtime/scripts/spawn_worker.sh:479

- **C274.01 / TODO**: task_not_found is a typed policy refusal. No live receipt establishes this predicate.
- **C274.02 / TODO**: task_not_startable is typed policy refusal. No live receipt establishes this predicate.
- **C274.03 / TODO**: inject_rejected is typed policy refusal. No live receipt establishes this predicate.
- **C274.04 / TODO**: nested_worker_depth_exceeded is typed policy refusal. No live receipt establishes this predicate.
- **C274.05 / TODO**: dispatch_inactive is typed policy refusal. No live receipt establishes this predicate.
- **C274.06 / PARTIAL-TODO**: consumer_fenced is typed policy refusal. [fixture-create-foreign](receipts/fixture-create-foreign.json)

### C276 — runtime/scripts/spawn_worker.sh:542

- **C276.01 / WITNESSED**: worker-start terminal effects identify the agent handle. [helper-start](receipts/helper-start.json)

### C278 — runtime/scripts/spawn_worker.sh:554

- **C278.01 / TODO**: outcome_unknown receipt supplies exact inspection nextCommands. No live receipt establishes this predicate.

### C282 — runtime/scripts/spawn_worker.sh:579

- **C282.01 / TODO**: launch.effective represents host-applied launch options. No live receipt establishes this predicate.

### C283 — runtime/scripts/spawn_worker.sh:582

- **C283.01 / TODO**: supervised launch args come from host agentDefaultArgs. No live receipt establishes this predicate.

### C291 — runtime/scripts/spawn_worker.sh:656

- **C291.01 / TODO**: launch.effective reveals whether autonomous flag was applied. No live receipt establishes this predicate.

### C296 — runtime/scripts/spawn_worker.sh:686

- **C296.01 / WITNESSED**: terminal create JSON returns a terminal handle. [followup-scratch-create](receipts/followup-scratch-create.json), [followup-inert-create](receipts/followup-inert-create.json), [followup-comment](receipts/followup-comment.json), [followup-bulk-close](receipts/followup-bulk-close.json), [followup-terminals-after](receipts/followup-terminals-after.json), [followup-remove](receipts/followup-remove.json), [followup-path-absent](receipts/followup-path-absent.json)

### C297 — runtime/scripts/spawn_worker.sh:705

- **C297.01 / PARTIAL-TODO**: terminal wait returns result.wait.satisfied boolean. [scratch-wait-unsatisfied](receipts/scratch-wait-unsatisfied.json), [scratch-wait-exit-2s](receipts/scratch-wait-exit-2s.json)

### C298 — runtime/scripts/spawn_worker.sh:741

- **C298.01 / TODO**: dispatch --inject returns result.prompt. No live receipt establishes this predicate.
- **C298.02 / WITNESSED**: terminal send returns result.send.prompt. [retry-original-exact](receipts/retry-original-exact.json)

### C300 — runtime/scripts/spawn_worker.sh:764

- **C300.01 / WITNESSED**: retry-request and wait-submit require text plus Enter. [retry-original-id-shorthand](receipts/retry-original-id-shorthand.json), [retry-original-id-text-only](receipts/retry-original-id-text-only.json), [helper-regenerated-retry](receipts/helper-regenerated-retry.json)
- **C300.02 / WITNESSED**: retry request is bound to prompt payload. [retry-original-id-shorthand](receipts/retry-original-id-shorthand.json), [retry-original-id-text-only](receipts/retry-original-id-text-only.json), [helper-regenerated-retry](receipts/helper-regenerated-retry.json)
- **C300.03 / TODO**: dispatch-show regenerates the exact original low-level prompt payload. No live receipt establishes this predicate.

### C308 — skills/pin-it/SKILL.md:72

- **C308.01 / TODO**: orchestration calls without live sender terminal fail no_active_sender_terminal. No live receipt establishes this predicate.
