# clean-sweep run — source=tracker — 2026-09-14 (takeover)

RUN: run_0607bdc681e6 · COORDINATOR: term_324d4430-b72d-40f7-8caa-0707d1a2adc0 (run-use adoption gen 2; driving shell: Muse CLI on maintainer Mac) · BASE: review/2026-09-14-holistic-fixes · FORK_POINT: eb1a2f104c0f94a7af386b85f6a0a38dccf97a1d · T0: 2026-09-14T15:34:09Z · SOURCE: tracker (4 open at T0: #235 #364 #385 #386; +2 PR-review findings to file as A1 A2) · WIP: builders=3 reviewers=1

Takeover provenance: kimi-code session_0b74c473-f848-457a-80d5-cf683b959158
(`~/.kimi-code/sessions/wd_orca-fleet_e01cdf52740c/session_0b74c473-f848-457a-80d5-cf683b959158`,
workDir this repo) died on provider quota (403 weekly limit) at 2026-09-14T15:30Z after opening
PR #387 (36 commits, #349–#384 + #385) and leaving 4 uncommitted review-feedback hunks + 2 fresh
review findings (A1: evidence-run lockfile litters the worktree; A2: run_report WIP check weaker
than the attention-budget protocol). Prior-run inflation check: re-read
docs/runs/2026-09-09-clean-sweep-tracker.md (DRY-WITH-PARKED); its parked #235 is re-confirmed
OPEN below; its 5 closes stay closed and are outside this run's denominator.

Substrate notes: orca 1.4.201 on PATH vs runtime/pins.json live PIN 1.4.200 — drift NOTE, not
refusal (spawn_worker.sh records it per spawn; re-witness is pin-it's loop). Managed accounts:
1 claude + 1 codex. CODEX DEAD until 2026-09-19 (usage limit; pane-verified 15:47Z) — cross-vendor
review via codex impossible this run. First spawn (codex, worker-start): exit 5 LAUNCHED_UNUSABLE —
1.4.201 launch.effective carries no args field at all ({agent,effort:null,model:null}), so no
PROFILE flag is provable on the supervised lane; worker-start unusable until pin-it re-witnesses.
Lane decision: ALL workers via WORKER_CMD custom-argv (explicit flags, coordinator-owned
semantics) — 09-09 precedent. Host permission mode: UNPROVEN (receipt omits args).

## Units (loop 1 — FREEZE pending STABILIZE + A1/A2 filing + twin enumeration)

| task_id | id | title | CLASS | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| STAB | — | land 4 PR-review hunks (deny-hook/run_report/verify/HUMAN_ACTIONS) + badge regen | conductor landing, worker-executed | t | n/a | n/a | n/a | t | n/a | lit | — | 1215e09 9651a52 8f7d5ac 917f9fd; pushed origin/BASE fast-forward (egress receipt); 1285 OK + full battery green; NC re-executed 11 failures; rides PR #387 |
| T1 | #388 | evidence-run lockfile dirties worktree | real-bug | t | f | f | f | f | f | lit | — | eddd3e0 e4ffbb7 75c0c91 8ec5c86; clean 1288 OK; NC re 2 NoLedgerLitter; I388 task_ed1282375c4b term_a74527b0 running |
| T2 | #389 | run_report WIP validation accepts incomplete reports | real-bug | t | t | t | f | f | f | lit | — | PR #391 @f642700 (base ✓ checks ✓); bot 2 P1 + 1 P2 held VALID (template waves, manifest abs-paths, dup cells); review next |
| T3 | #364 | fixture-backed evals + workspace-state oracle (S1) | real-feature-small | f | f | f | f | f | f | lit | — | Q1: fixtures+oracle (wave 2; brief TBD) |
| T4 | #385 | historical-docs polish, agent slice (status.json + parity test) | real-bug (docs) | t | t | t | f | f | f | lit | — | PR #390 @bcb4397; bot P2 held; axes R385a task_b865c036295d / R385b task_d1f583774723 / R385c task_65940316b418 live |
| T5 | #386 | sign manifest+inventory, retention backend (S2) | — | — | — | — | — | — | — | — | needs-human: key custody + backend undecided (Q2) | Q2: park |
| — | #235 | H-02 marketplace submissions (pre-parked needs-human) | needs-human | — | — | — | — | — | — | needs-human: external accounts | prior run + issue text |

PHASE: ORIENT → ENUMERATE → TRIAGE done → FREEZE → BUILD wave 1 running (U388 U389 U385) → wave 2: U364

FREEZE: query1 (coordinator, T0) 4 open + query2 (worker, 16:14Z) 6 open with
created-since-T0 exactly {#388,#389} and closed-since-T0 none — agreement modulo the run's
own 2 filings. Every frozen id maps to exactly one build unit: #388→U388, #389→U389,
#385-agent-slice→U385, #385-diagrams→Q3, #364→Q1, #386→Q2, #235→park needs-human. No id
without a unit; no unit without an id.

Run-close integrity inventory: retained inline in the Final report section at close (this
ledger is the living run record until then).

## T0 enumeration (query 1, coordinator, 2026-09-14T15:34:09Z)

```
open: 4
#386 enhancement,sev:S2 Optional hardening: sign the evidence manifest and run-close inventory
#385 documentation,sev:S2 Historical-docs polish: snapshot banners, ASSUMPTIONS hole, status.json drift
#364 sev:S1 Per-skill behavioral evals ship zero fixtures — they grade only narration
#235 sev:S2,needs-human [H-02] Submit remaining marketplace aggregators per docs/distribution.md
PR #387 OPEN base=main head=review/2026-09-14-holistic-fixes reviewDecision=(none) commits=36
```

BOOTSTRAP: preflight --base review/2026-09-14-holistic-fixes --fork-point eb1a2f104c0f --require-gitleaks → OK (repo=ravidsrk/orca-fleet). BASE ≠ default; fork-point == merge-base(BASE, origin/main).

## Loop log

(append per unit: dispatch → build → PR → review → merge → close → re-enumerate)

- 15:47 STABILIZE spawn 1: task_a6c1dfe46f13 → codex supervised (selector current) → exit 5
  LAUNCHED_UNUSABLE (launch.effective has no args on 1.4.201) + pane shows codex usage limit to
  2026-09-19. REFLECTION: what failed? unprovable profile flags + dead provider. Fix? stop per
  contract, respawn claude via WORKER_CMD custom-argv (explicit flags, no host dependence).
  Repeating? No — new lane, new agent. → worker-stop ctx_39334916997c.
- 15:48 STABILIZE spawn 2: WORKER_CMD claude custom-argv → exit 3 UNPROVEN (input_accepted,
  no turn_started); pane read shows a LIVE worker mid-turn (false negative) — no resend, no
  respawn beside it. HANDLE term_15569166.
- 15:50 A1/A2 filed as #388/#389 (egress receipts first, consent
  run-2026-09-14-clean-sweep:tracker-writes). Loop-1 denominator now 6: #235 #364 #385 #386
  #388 #389.
- 15:58 STABILIZE worker_done (succeeded): 4 commits 1215e09 9651a52 8f7d5ac 917f9fd, manifest
  tracked. Coordinator verified: all SHAs on HEAD, 430 criterion tests OK (re-run), validate +
  badges green, NC re-executed exit 1 / 11 failures (matches claim). Delivery acked, worker
  released (retained/no_owned_resource — custom lane owns no terminal; pane kept for forensics).
- Full suite at 917f9fd: 4 failures, ALL mine — the new ledger tripped
  test_run_archive_index_lists_every_report (no index row) +
  test_run_archive_integrity_standard_matches_practice (no inventory sentence), each ×2 via
  release-rehearsal clones. The 09-09 compound-learn warned exactly this; my pre-commit search
  for the tests used wrong terms and I trusted the empty result — search negatives are not
  evidence. Fixed this commit: index row + inventory sentence. Re-running.
- BASE green + pushed: 1285 OK + full local battery (validate/routing/proof/run_report/
  bundle/ruff/gitleaks); pushed 58c180c then e8db0f2 (fast-forward, egress receipts).
  STABILIZE closed (BUILD_DONE t, MERGED t; PR/review/bot n/a — rides PR #387).
- TRIAGE spawn: task_43ca0562f283 → custom lane needs a pre-created child worktree
  (worker-start-only "new-child" rejected with selector_not_found) → created
  /Users/ravindra/orca/workspaces/orca-fleet/triage-wave1 (child of coordinator, from
  origin/BASE), closed its fallback shell, spawned claude ro → exit 3 UNPROVEN again; pane
  shows LIVE worker in plan mode (query 2 running). PATTERN: the WORKER_CMD lane never
  observes turn_started on this host — exit 3 + pane-live = proceed, no resend.
- REVIEW-LEG DESIGN (read verify.py check_review before designing): one GitHub identity on
  this host, so no second-identity APPROVED exists for verify.py's lookup; verdict workers
  post COMMENTED verdict reviews (GO/NO-GO, blind-fix-first, 3 axes + aggregator), never
  APPROVE (that would fake independence). Mission close = merged + executed NC + fresh
  blind verdicts + revert audit (09-09 precedent); the verify.py review leg is RUN and its
  honest result RECORDED, never hidden. Manifest pr.reviewed_sha is filled by the conductor
  post-merge on BASE (record-keeping from the posted verdict, not a unit-head move).
- TRIAGE done-by-transcription (deviation, recorded): the ro worker finished all reads
  (query2 + 6 verdicts) but plan-mode blocks /tmp writes, so its repros were unexecutable
  and it parked at the plan-approval gate; ESC dismissed the dialog but the terminal then
  refused prompts (agent_prompt_blocked ×2 — no more retries). Harvested the full report
  from the worker's plan file, stopped + released the dispatch, closed the task manually
  (recovery write). Coordinator corroborated both code repros in /tmp clones (#388:
  litter + STALE-cascade + 16/16; #389: differential settings-row-binds vs control
  refused) with the repo untouched, and transcribed 3 agent-briefs + 3 human questions
  from the verified findings. Greptile correlation: #388/#389 are its 2 P1 comments on
  PR #387 verbatim — fixing them closes the bot loop there.
- WAVE 1 dispatched (3 builders, WIP ok): U388 task_f7cfdaa731df/ctx_4b956f9ab4ba,
  U389 task_0936788dace9/ctx_47bc79e5b377, U385 task_f5169734fd96/ctx_d28d22e7bbf3
  (digests d4ed45ce/c540cb30/eafaf7a1; units fork e04b0c2; specs landed 5af2e6f).
- U385 live ask msg_8a4540b37c04: spec's both-paths NC revert cannot go RED (restores
  base test module = green; verify.py refuses test paths per #280). Worker right, spec
  wrong → approved A+B (revert production path only + throwaway hand-mutation witness
  for the test-only C-2). Reply sent immediately; question was inside an acked batch —
  ack-before-reply is closed by this reply, no stall.
- U385 ask 2 msg_adc25bd5fa78: badge count moves 1285→1288 (outside hot files) → (a)
  regen on branch as a mechanical commit; integration collisions resolve by re-regen
  (integrator on unions, conductor after every merge). Replied + acked.
- U389 ask msg_cace8bc63c0e: same badge question → same answer (never cut tests to hold
  the count). U388 ask msg_ead6507afe29: same badge question → (A); plus branch name →
  bare u388-lockfile (create from tip; ravidsrk/* stays local-only). U388 otherwise
  green: 24/24, C-1/C-3 red-at-base, C-2 RED 10/10 vs no-lock mutant.
- Builds verified + settled: U385 (ea77ce9 87619de e72155c; 1288 OK; NC re C-1-only RED),
  U389 (e74dea0 0038a43 3ec17ee; 1289 OK; NC re 10F+1E), U388 (eddd3e0 e4ffbb7 75c0c91
  8ec5c86; 1288 OK; NC re 2 NoLedgerLitter). PRs: #390 @bcb4397 (1 bot P2 held),
  #391 @f642700 (3 bot held: 2 P1 + 1 P2). U385 axes: standards 1 Req + specs 1 Req +
  test-adequacy clean — the two Requireds + bot P2 are ONE issue (_guides link forms),
  found independently 3 ways.
- Verdict dispatch blocked once by my own dead-link trip: pasting the bot finding's
  bracket-link examples into taskspecs/verdict-385-r1.md failed
  test_no_navigable_doc_links (run files are navigable; EVIDENCE_TREES excludes only
  docs/reports + docs/completion/evidence). Fixed by rewording (no bracket-link forms in
  run files — sanitize all future verdict specs the same way).
- review-it consulted pre-verdict (mission cross-check): read-only verdict doctrine
  agrees with our shape (SHA-bound, no rerank, quoted lines). Its "posting is a human
  grant" rule governs review-it RUNS; in this clean-sweep run, verdict posts on feature
  unit PRs (COMMENTED/REQUEST_CHANGES, never APPROVE, same identity, dismissible) are
  routine pipeline evidence — classified taste, logged; the main-merge human gate stands.
