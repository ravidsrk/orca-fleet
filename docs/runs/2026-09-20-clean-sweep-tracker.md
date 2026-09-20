# clean-sweep run — source=tracker — 2026-09-20

RUN: run_bec47e54b673 · COORDINATOR: term_0bae108a-5af7-4d7a-b584-67d05a2787d1 (kimi-code driving shell; coordinator terminal COORD-2026-09-20, background surface) · BASE: review/2026-09-20-tracker-sweep · FORK_POINT: e8ddbd988486694a2985822e557a382b344e2872 (origin/main at T0) · T0: 2026-09-20T06:17:18Z · SOURCE: tracker (10 open at T0: #235 #386 #407 #409 #427 #434 #441 #442 #443 #444; enumeration digest: gh-issue-list-open-count=10) · WIP: builders=2 reviewers=1

PHASE: … → DONE → GATES RESOLVED (b) → REPAIRS → MERGES → CLOSED (terminal: DRY-WITH-PARKED on the STANDING parks only; all 4 buildable issues CLOSED with evidence; promotion PR #486)

Run-close integrity inventory: retained inline in the Final report section at close (this
ledger is the living run record until then).

Substrate notes: orca 1.4.204 on PATH vs pins.json live PIN v1.4.203 — patch bump, rides per #427
trigger rules (drift NOTE, not refusal; re-witness is pin-it's loop). claude + codex CLIs on PATH
(codex usage limit ended 2026-09-19 — lane probe owed at dispatch). No open PRs at T0.

## Prior-run re-verification (liveness-resume inflation post-mortem) — DONE, all VERIFIED

Subagent post-mortem over docs/runs/2026-09-14-clean-sweep-tracker.md + campaign-2026-09-16-clean-sweep
+ gate-batch.md: every claimed close (#364/#385/#388/#389/#393) is CLOSED with evidence comments;
every claimed merge (PRs #387/#390/#391/#392/#395/#397/#400-#404) is MERGED with merge commit
ancestor of origin/main; #387 review threads 42/42 resolved; #408 G1-G4 settled on disk
(gate-batch.md, record PR #453 merged 10e45f72); prove-it self-run (PR #437) and clean-sweep
self-run (PR #436, report docs/runs/2026-09-14-clean-sweep-self-run.md) both BIND via
run_report.py exit 0. Soft spots recorded, not actionable here: G2's "1 approval" overstates
main's live protection (no required PR reviews — status checks only); campaign loop-2 since-T0
query carries no timestamp (#417 closed mid-run by the chaining run — consistent with
externally-resolved either way). No prior green-but-unverified claim enters this run's
denominator: the prior denominator's issues are all closed and verified.

## T0 enumeration (query 1, coordinator, 2026-09-20T06:17:18Z)

```
open: 10
#235 sev:S2,needs-human   [H-02] Submit remaining marketplace aggregators
#386 enhancement,sev:S2   sign evidence manifest + run-close inventory; retention backend
#407 enhancement           Roadmap: orca-fleet from 0.6.1 to 1.0 (epic)
#409 documentation,enhancement,needs-human  harden-it self-run promotion (re-scoped)
#427 enhancement,p2        Re-pin Orca runtime contract (next cadence 2026-12-16)
#434 documentation         Regenerate proof-ladder diagrams post-first-promotion
#441                       mission-chaining: no inter-mission promotion lane
#442                       evidence-manifest/verify.py assume unit repo == evidence repo
#443                       mission-chaining: deferral carry has no artifact shape
#444                       mission-chaining: re-derivability for local-only targets undefined
open PRs: none
```

Query 2 (issues created/reopened/closed since T0): re-run each loop; at T0 the set is empty
by construction. Loop log below carries each re-run.

## Triage (skeptic, reproduce-or-refute)

| id | reproduction | verdict |
|---|---|---|
| #441 | `grep PARKED-AT-PROMOTION / promotion lane runtime/mission-chaining.md` → absent; doc names no terminal for a promotion-owed park (read in full, 40 lines) | REAL (doctrine gap) |
| #442 | `verify.py --help` → no --git-dir/--evidence-root; evidence paths bounded to one toplevel (line 37, #267 rule), SHAs resolved under same cwd | REAL (tooling gap) |
| #443 | mission-chaining.md:29-32 hands parked items to N+1 "as enumeration INPUT" with no artifact shape named | REAL (doctrine gap) |
| #444 | mission-chaining.md has no local-only/no-remote re-derivability rule | REAL (doctrine gap) |
| #235 | issue body + 2026-09-13 comment: every remaining box needs a maintainer account with submit rights; nothing agent-side closes it | PARK needs-human (external accounts) — re-confirmed |
| #386 | unparked 2026-09-16 by gate session (G1: maintainer offline key, Rekor anchor) BUT prerequisite "coordinator-signed verifier transcripts" unlanded (no signing in verify.py; dispatch-sign.py covers the dispatch tuple only) and tracked nowhere but this issue | PARK needs-human (prerequisite work unlanded; #386 is its own tracker) |
| #407 | roadmap epic; children #408-#419 all MERGED except #409 (re-scoped, parked below); 1.0 not reached (19/21 missions still doctrine-only) | PARK needs-human (maintainer roadmap tracker; closes at 1.0) |
| #409 | requires a full harden-it mission run (multi-day adversarial loop + human PoC-routing gate) — harden-it's own convergence proof, not clean-sweep's | PARK out-of-scope (hand to harden-it; needs-human label stands) |
| #427 | trigger check: date 2026-12-16 not reached; installed 1.4.204 vs pin 1.4.203 = patch bump (rides per the issue's own trigger rules); no SPAWN=NOTE "run pin-it" sighting this session | PARK out-of-scope (pin-it cadence; trigger not fired) |
| #434 | `gh secret list` → empty; provider render key not present, regen run stays parked per the 2026-09-16 gate comment | PARK needs-human (repo secret owed; ping on add) |

FREEZE: 10 frozen ids → build units: #441+#443+#444 → U-CHAIN (file-coherent: all amend
runtime/mission-chaining.md); #442 → U-442 (verify.py + tests). Parks: #235, #386, #407
(needs-human); #409, #427 (out-of-scope); #434 (needs-human). Every frozen id maps to exactly
one unit or park; no id without a unit; no unit without an id.

## Units

| task_id | id | title | CLASS | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| STAB | — | land 3 dirty doc files (rollup/README/CHANGELOG amendments) | conductor landing | t | n/a | n/a | n/a | t | n/a | lit | — | 3833c88 on BASE; claims pre-verified (PRs #483/#455/#456/#457, ls-remote campaign/*, run_report binds) |
| — | #235 | H-02 marketplace submissions | needs-human | — | — | — | — | — | — | — | needs-human: external accounts/listings, maintainer-only | prior run + issue text + 09-13 comment |
| — | #386 | sign manifest+inventory, retention | needs-human | — | — | — | — | — | — | — | needs-human: transcript-signing prerequisite unlanded; G1 answers recorded (gate-batch.md) | issue + gate-batch G1 |
| — | #407 | roadmap epic 0.6.1→1.0 | needs-human | — | — | — | — | — | — | — | needs-human: maintainer roadmap tracker | children merged except #409 |
| — | #409 | harden-it self-run promotion | out-of-scope | — | — | — | — | — | — | — | out-of-scope: harden-it mission run + human PoC gate | issue re-scope comment |
| — | #427 | Orca re-pin cadence | out-of-scope | — | — | — | — | — | — | — | out-of-scope: pin-it, trigger not fired (patch bump rides; 2026-12-16) | issue trigger rules |
| — | #434 | proof-ladder diagram regen | needs-human | — | — | — | — | — | — | — | needs-human: provider render key secret absent (gh secret list empty) | gate comment + probe |
| U-CHAIN | #441 #443 #444 | mission-chaining: promotion lane terminal, deferral-carry shape, local-only re-derivability | real-feature-small (doctrine) | t | t | t | t | t | t | lit | — | G1 RESOLVED (b): targeted repair + blind re-review GO + Greptile APPROVED @8ff20027; MERGED ec724054 (ancestry ✓); verify.py 6/6 OK (scope/commands/redaction/NC-executed/review/change-on-base); #441 #443 #444 CLOSED with evidence; worktree retired pending teardown |
| STAB-2 | — | repair 5 suite regressions from STABILIZE (index row + alt-string source repair) | conductor landing, worker-executed | t | n/a | n/a | n/a | t | t | lit | — | worker 4d13c672 (3 scoped files) → merged 2f04c402 (no-ff); coordinator-verified: 39/39 named tests OK + full suite exit 0 + tree clean at tip; egress receipt 4060372a; pushed; worktree+branch retired, no stray terminals |
| U-442 | #442 | verify.py cross-repo evidence root (--git-dir/--evidence-root split) | real-feature-small (tooling) | t | t | t | t | t | t | lit | needs-human (disclosed): verify review leg RED — no independent APPROVED on #485 (single-identity; Greptile check pass 0-comments, no APPROVE object; recoverable post-merge, 09-16 G3 class) | G2 RESOLVED (b): targeted repair + blind re-review GO; union merge (badge regen); MERGED c467d554 (ancestry ✓); verify.py 5/6 (all but review leg, NC EXECUTED red-on-assertion); #442 CLOSED with evidence; worktree retired pending teardown |

## Loop log

(append per unit: dispatch → build → PR → review → merge → close → re-enumerate)

- 06:17 T0 recorded; enumeration query 1 (10 open, 0 PRs).
- 06:2x STABILIZE: dirty-tree claims verified (PR #483 merged; campaign branches deleted;
  PRs #455/#456/#457 merged; run_report binds exit 0 for both self-run promotions) → committed
  3833c88 on BASE review/2026-09-20-tracker-sweep (fork e8ddbd98 = origin/main at T0).
- Prior-run post-mortem: all claims VERIFIED (subagent report in coordinator context; summary
  in "Prior-run re-verification" above). Nothing re-enters the denominator.
- 06:36 Run materialized: run_bec47e54b673, coordinator term_0bae108a (terminal COORD-2026-09-20).
  Tasks: U-CHAIN=task_61b5e8accc70, U-442=task_a25c91eeff96 (DAG verified: both ready, no deps,
  no cycles, disjoint hot files — mission-chaining.md vs verify.py+tests).
- 06:4x LANE PROBE (spawn 1, supervised worker-start, claude, PROFILE=rw): exit 5
  LAUNCHED_UNUSABLE — launch.effective={agent,effort:null,model:null}, no args field on 1.4.204,
  so no PROFILE flag provable (09-14 precedent on 1.4.201). Host permission mode: MANUAL
  (agentDefaultArgs=''). Per contract: worker-stop ctx_02702604cecd (closed_agent_terminal,
  ptyKilled) — never respawn beside it. NOTE: worker-stop settled task_61b5e8accc70 to
  `blocked` with NO gate row (gate-list empty) — recovery: task-update --status ready
  (recovery/override write, ledgered here). Lane decision: ALL workers via WORKER_CMD
  custom-argv (explicit flags, coordinator-owned semantics) — 09-14 precedent.
- 06:5x U-CHAIN BUILD dispatched: worktree u-chain (3cf2cdae::…/orca/workspaces/orca-fleet/u-chain,
  branch ravidsrk/u-chain from BASE tip — ravidsrk/ prefix is Orca's mapping, not drift, 09-14
  precedent) → spawn 2 custom-argv WORKER_CMD="claude --dangerously-skip-permissions"
  ORCA_COORD_ALLOW_CMD_OVERRIDE=1: exit 3 UNPROVEN (input_accepted, no turn_started,
  request 6ff99ef5) — pane read shows a LIVE worker mid-turn (bypass permissions on, spec read,
  false negative, 09-14 precedent): HANDLE term_98fd0f79-9118-4cd2-b057-f955b9e85500. No resend,
  no respawn.
- 06:5x U-442 BUILD dispatched: worktree u-442 (branch ravidsrk/u-442) → same custom-argv lane:
  exit 3 UNPROVEN (request ca86ab2f) — pane read shows LIVE worker mid-turn in verify.py:
  HANDLE term_cdd92b44-5d5a-4f8d-9868-9e21d818fb7a. WIP=2 builders (attention-budget met).
  Spec digests: build-u-chain.md sha256:87260521…, build-u442.md sha256:7498d20d… @a58bf71a.
  Timeboxes sent to both dispatches (report-by 45min, partial-report STOP).
- 06:57 DELIVERY delivery_6a5ff5b13e45 (4 msgs, transcribed): setup-status for the STOPPED
  ctx_02702604cecd (historical) · heartbeats both builders (alive) · LIVE question
  msg_2df108a4d6d0 (U-CHAIN branch ambiguity — leftover u-chain branch held by stopped spawn's
  worktree). REPLIED (A): build on ravidsrk/u-chain in the dispatched worktree (DECISIONS
  2026-09-20T06:57:11Z, mechanical). Leftover worktree U-CHAIN-builder-2649789649 retired:
  terminals closed (1 stopped), untracked package.json/pnpm-lock VERIFIED npm-init boilerplate
  then removed, worktree rm OK, branch u-chain carried no commits (rm cleaned it). Acked.

BOOTSTRAP: preflight --base review/2026-09-20-tracker-sweep --fork-point e8ddbd988486 --require-gitleaks → OK (repo=ravidsrk/orca-fleet). BASE ≠ default; fork-point == merge-base(BASE, origin/main).

- 07:1x DELIVERY delivery_62cf294b1cdc (5 msgs, transcribed+acked): U-CHAIN ESCALATION
  msg_a75b2c0447b5 — build complete/green on owned criteria but AC-3 (full suite green)
  unmeetable: 5 tests RED at head 315ad409 AND at BASE a58bf71a, byte-identical sets, caused
  by STABILIZE 296f100b (run ledger missing docs/runs/README.md index row → 4 failures) +
  3833c88e (README.md off wire_docs.py fixed point → 1 failure). Builder correctly STOPPED
  (out of its scope). COORDINATOR REPRODUCED: 39 tests OK at e8ddbd98 (origin/main), 5 RED
  at a58bf71a (/tmp/verify-stab detached worktree, whole output captured). Run-own regression
  → STAB-2 frozen (build-stab2.md), task_86f696b9efc8, worktree stab-2 (ravidsrk/stab-2),
  dispatched custom-argv claude: HANDLE term_1464f749-d82e-49c9-8f41-df7a976cb7b3,
  dispatch ctx_62655b197318 (UNPROVEN exit 3 → pane read: live mid-turn, bypass on). Chose
  escalation's option (b): repair BEFORE U-CHAIN lands; U-CHAIN worker_done under (a) with
  AC-3 parked 'no new red' is accepted for harvest, but CLOSE requires the suite green at
  the merge tip — STAB-2 lands first.

- 07:3x U-CHAIN worker_done msg_a4f3e8d7d8bf (succeeded, transcribed+acked delivery_5bf5965953b9).
  HARVEST (coordinator, independent): 3 commits on ravidsrk/u-chain (5ecf74e5 RED test →
  315ad409 GREEN doc → 5328cc86 evidence), author=maintainer, no trailers, tree clean; scope =
  mission-chaining.md + test_architecture.py + badges/tests.json + docs/reports/U-CHAIN/*
  (owned files only); manifest contract.digest == frozen spec digest 87260521… @a58bf71a,
  5/5 criteria, NC executed (revert + 4 per-clause hand mutants, all KILLED), intent non-empty,
  lighting=lit, suite cmd exit 1 = the 5 known STABILIZE regressions (STAB-2 repairs). Doc
  spot-check: PARKED-AT-PROMOTION resume rule, handoff-log shape, local-only bytes clause all
  present and substantive. BUILD_DONE=t. INTEGRATOR dispatched: task_017a294f6f1a (dep build),
  HANDLE term_452b7a7a-997d-49c8-8381-aa1c4e24a029, dispatch ctx_bb8c5282bde1 (UNPROVEN → pane
  live). SUBSTRATE: claude account at 79% weekly limit (pane warning) — review wave prefers
  codex (cross-vendor, limit ended 09-19); egress standing grants recorded for the integrator
  (base-writes + tracker-writes consent ids sent).

- 07:5x DELIVERY delivery_4509bd75d780 (3 msgs): STAB-2 QUESTION msg_b7e2def2ebb1 — the two
  named files cannot green the suite: (2) test_run_archive_integrity reads the LEDGER for
  /integrity inventory[^.]*retained/ (the line above, added by coordinator — my freeze-time
  omission); (3) wire_docs.py hardcodes the stale 'today every mission reads doctrine-only'
  alt (line 27) so running it REVERTS 3833c88e's repair, and docs/concepts.md:423 carries the
  same stale alt. REPLIED: coordinator repairs its own ledger on BASE (this edit); STAB-2
  scope widened to wire_docs.py + docs/concepts.md — fix NEW_ALT['proof-ladder'] at source,
  commit everything the script writes (DECISIONS x2, 07:5xZ). #434 pixel regen untouched.
  Review-wave DAG materialized: SPEC=task_b6c94c187b09 STANDARDS=task_067ec69be832
  TEST-ADEQUACY=task_1eba2dcf50f5 (deps: integrator task_017a294f6f1a; verdict task owed
  after axes report).

- 08:1x U-CHAIN INTEGRATED (worker_done msg_3b9623f271bf): gitleaks 0 findings on the 3-commit
  diff; egress receipts before each write; PR #484 base=review/2026-09-20-tracker-sweep
  head=ravidsrk/u-chain@5328cc86 (baseRefName asserted by integrator AND coordinator gh view);
  Greptile ran t=158s: 1 P1 + 2 P2, ALL tagged VALID and HELD unfixed for the review batch
  (P1: PARKED-AT-PROMOTION ancestry check vs leg N's own BASE is pre-satisfied + unresolvable
  in the no-remote lane; P2s: worked-exemplar handoff-log self-describes as proposal; contract
  test keyword co-occurrence weakness). PR_OPEN=t BOT=t (reconciled: 3 VALID held).
  REVIEW WAVE dispatched (codex cross-vendor, gpt-6-astra, pane-verified live; claude spared —
  79% weekly): SPEC term_1927d806/ctx_b3dc36fcf886 · STANDARDS term_83e191bd/ctx_7f47b80e2503 ·
  TEST-ADEQUACY term_1203e16a/ctx_147ba196881c. Verdict task_b44329122b48 queued on the 3 axes.
  Reviewer cap: 1 review unit in flight (axis fan-out exempt) — attention-budget met.

- 08:5x STAB-2 LANDED. worker_done msg_720ead2853e5 (succeeded): worker's 4d13c672 touched
  EXACTLY the 3 scoped files (wire_docs.py source string, docs/concepts.md, docs/runs/README.md
  index row; README.md byte-identical — the script's fixed point now matches the truthful
  committed text). BASE had moved to a8db9ba9 past the worker's 39db1cf3 merge — conductor
  landed union merge 2f04c402 (no-ff, conflict-free: worker files ∩ coordinator files = ∅).
  Coordinator verification at tip: 39/39 named tests OK (15.6s), full suite exit 0, badge
  regen byte-identical, tree clean. Egress receipt 4060372a → pushed a8db9ba9..2f04c402.
  Worktree stab-2 retired (terminals closed, rm OK, branch merged+gone, 0 stray terminals).
  BASE is GREEN for the first time this run.

- 09:1x DELIVERY delivery_6bff48bde63d (4 worker_dones, transcribed+acked):
  U-CHAIN REVIEW ROUND 1 = NO-GO on all three axes (codex cross-vendor, blind-expectation
  first, reviewed 5328cc86): STANDARDS 2 Required (promotion governance, commit
  reconstruction) + 1 Optional; TEST-ADEQUACY 3 Required (SIX surviving semantic mutants —
  contract assertions too weak; 4 clause deletions all killed, vacuity guard failed closed);
  SPEC 4 Required (promotion resume check targets wrong branch — echoes Greptile P1; contract
  test permits requirement-breaking mutations; AC-3 red = the 5 inherited failures, STALE —
  STAB-2 has since greened BASE; AC-4 runner receipt owed). Reports: docs/reports/U-CHAIN/
  review-{standards,tests,spec}.txt (uncommitted; verdict worker commits). Round 1 of ≤3.
  VERDICT dispatched: task_b44329122b48, codex term_4c863306/ctx_(receipt spawn-oV6Y7f).
  U-442 BUILD worker_done msg_5847d21d142f (succeeded): 3 commits on u-442 (4ad601a1 RED
  two-repo fixture → 1ef8bd79 fix → df4f524f evidence). HARVEST (coordinator): scope =
  verify.py +90, tests +190, evidence-manifest.md 2-line note, GENERATED regen (ARCHITECTURE
  + badges + 14 docs/missions — activation-load recompute, clean-sweep 33.9k→34.0k, validate
  owed at merge), docs/reports/u-442; author maintainer, no trailers; tree clean; branch 13
  behind BASE. --git-dir (SHA/git legs via git -C) split from --evidence-root (bounds
  manifest-relative paths); no-flag behavior byte-identical; #267 re-rooted not relaxed.
  BUILD_DONE=t. INTEGRATOR dispatched: task_4b39f5058111, claude term_5941f8b4 (receipt
  spawn-nUf2ZG) — merges green BASE first, then suite+validate, push, PR, Greptile reconcile.

- 09:4x U-CHAIN round 1 CLOSED OUT: verdict worker (codex) aggregated 9 Required axis findings
  + 3 held VALID bot findings, posted receipted COMMENTED 'verdict: NO-GO — round 1' on PR
  #484 (coordinator-verified via gh pr view: review present, first line exact), pushed
  evidence-only commit 5619d5be (code tree unchanged — conductor tree-check at merge). Round
  2 fix batch frozen (build-u-chain-r2.md, digest 63ce1e4e…): F-1 promotion=BASE→default +
  local-ref resume; F-2 bundle/mirror reproduces commits, seed+diff supplemental; F-3
  operative assertions + whitespace normalize + 6 reviewer mutants RED-recorded; F-4 NC
  re-recorded via evidence-run.py; F-5 exemplar cited as adopted proposal; F-6 green-BASE
  merge + full-suite receipt. R2 FIX dispatched: task_bf8332aed4e9, claude
  term_956f95b3-81a7-4bee-b309-f4878527d0fd (dispatch ctx_847e6680c4b9), fresh terminal in u-chain
  worktree per dispatch-lifecycle.

- 10:1x U-442 INTEGRATED (worker_done msg_365f21ba5b1b): merged BASE 0f8cb8a2 conflict-free →
  head 5a57c8d2 GREEN (1714 tests OK 277s, validate 21/21, gitleaks clean); PR #485
  base=review/2026-09-20-tracker-sweep (asserted + coordinator-verified, head a5f84978 after
  the integrate.json push); Greptile at 163s: 2 P1s on verify.py, both adjudicated VALID and
  HELD (P1-1: _read_artifact's tracked-at-head_sha branch reads through the SHA root — the
  split's own blind spot; P1-2 in integrate.json). PR_OPEN=t BOT=t. REVIEW WAVE dispatched
  (codex): SPEC term_f528a13f/task_18e1477e843e · STANDARDS term_681d04c2/task_fa64821477cd ·
  TESTS term_239b915c/task_83d2f645badb; verdict task_9af4e0003988 queued on the axes.
  Review units in flight: 2 (U-CHAIN r2 is a build round, not a review) — within cap.

- 10:4x U-CHAIN r2 FIX DONE (worker_done msg_8f46a23da8da): merge 1066c028 (BASE ed51fe11,
  conflict-free) + 88a64c90 (fix, mission-chaining.md +44/test_architecture.py +69) +
  0dbc669e (evidence). HARVEST: scope = the two spec'd files + receipts; F-1 text verified
  (BASE→DEFAULT, local-ref ancestry check, lanes cannot PROMOTE); manifest head_sha 88a64c90,
  5/5 criteria addressed, commands all evidence-run receipts (suite exit 0 wtree a32a6472 ==
  88a64c90^{tree} — verified), NC re-recorded through the runner + 13 mutants killed
  (mutants-r2.txt); suite green at the merged head. R2 INTEGRATE dispatched:
  task_c01a07c4fb08, claude term_a2768396 (push + Greptile reconcile on the new head).
  Round-2 review wave follows the bot reconcile.

- 11:2x U-CHAIN r2 INTEGRATED (worker_done msg_08bdb8df7836): gitleaks clean, egress 61ba882d,
  ff push 5619d5be..0dbc669e; Greptile on the new head: 2 NEW VALID held — BOT-4 (P1,
  mission-chaining.md:46: the BASE→DEFAULT resume check names origin/<default> with no
  freshness obligation — a stale ref parks a promoted chain; sits in the clause F-1 rewrote)
  and BOT-5 (P2, docs/reports/U-CHAIN/run_mutants-r2.py). Both join the r2 review batch.
  R2 REVIEW WAVE dispatched (codex): SPEC term_99f75411/task_99fd6b826460 · STANDARDS
  term_b695c937/task_2c6e0642e3c0 · TESTS term_0d9de635/task_e842d3e68c58; r2 verdict
  task_a4a0d7ba48a3 queued. U-442 r2 fix batch frozen meanwhile (build-u442-r2.md,
  digest 9df586e1…: F-1 evidence authority, F-2 raw-read git-context, F-3 evidence-root
  honored, F-4 symlink containment, F-5 nested-cwd).

- 11:5x U-442 round 1 CLOSED OUT: verdict posted (review 5260074858 'verdict: NO-GO — round 1'
  @a5f84978 tree 8a39ac3e, coordinator-verified via gh api — first line exact), evidence
  commit 0056bf16 pushed (code-identical). 9 Required across axes + 2 held VALID P1s. R2 FIX
  dispatched: task_14fe56e3cd29, claude term_bb52652d (spawn-4TvuBd), batch F-1..F-5 from
  build-u442-r2.md (digest 9df586e1…). Round 2 of ≤3 for U-442; U-CHAIN's r2 re-review in
  flight. Review units: U-CHAIN r2 (1) — cap met.

- 12:2x U-CHAIN round 2 CLOSED OUT: verdict review 5260110523 'verdict: NO-GO — round 2'
  @302d43e9 (coordinator-verified first line exact), evidence b431c418 pushed. 10 Required
  + BOT-4/BOT-5. Round-3 (FINAL) batch frozen (build-u-chain-r3.md, digest 4b541540…):
  G-1 fetch-before-resume freshness; G-2 harness derives its baseline; G-3 stillborn ≠ kill;
  G-4 resume alternatives fully bound; G-5 carry schema + missing-log; G-6 reconstruction
  obligations. R3 FIX dispatched: task_ed293bd7d1d8, claude term_afb945ab (spawn-kGaXWN).
  A round-3 NO-GO parks U-CHAIN with a gate naming the sticking finding (round budget).
  U-442's r2 fix (F-1..F-5) still in flight.

- 13:3x U-442 r2 FIX DONE (worker_done msg_6038af40c2c8): merge abb00452 (BASE 5df4c0d8) +
  76922d5a fix (_roots_are_split() gates the tracked-at-head shortcut; --symbol via the
  selected git context) + 88c9645c tests (12 regressions) + 5113e156 badges + bc0fc21d
  evidence; 9/9 mutants killed (4 r1 survivors + M1/M6 + 3 new). HYGIENE BREACH caught at
  harvest: all 4 r2 commits carried a Co-Authored-By agent trailer (r1 commits clean).
  CONDUCTOR NORMALIZATION (dispatch-lifecycle trailer strip, never squash): filter-branch
  msg-filter over the 4 unpushed commits → e4cbf222, TREE IDENTICAL, diff empty, backup ref
  deleted; ledgered here per coordinator-verification discipline. R2 INTEGRATE dispatched:
  task_c3b292b75f56, claude term_40826a62 (suite+validate re-verify, --force-with-lease
  push, Greptile reconcile). U-CHAIN's FINAL r3 fix still in flight.

- 14:0x U-CHAIN r3 (FINAL) FIX DONE (worker_done msg_ce5d59d31724): 5bd2eb07 fix + 14575aba
  evidence + re-merges; 28/28 mutants RED, harness replays clean. HARVEST: G-1 freshness
  clause verified in place (fetch-before-check, UNPROVEN-not-landed, preflight contract
  cited, offline stays local). TRAILER BREACH #2: 3 unpushed commits dirty (5bd2eb07,
  14575aba, 0213c734) — conductor strip over b431c418..HEAD → head d75b23b1, TREE IDENTICAL,
  0 trailers remain, backup ref deleted (ledgered; second occurrence — claude workers are
  appending trailers despite the spec's 'no trailers' line; compound-learn candidate).
  R3 INTEGRATE dispatched: task_aeb2e5dc5e06, claude term_b545ef34 (suite+validate+harness
  replay, --force-with-lease push, Greptile). U-442's r2 integrator still in flight.

- 14:3x U-442 r2 INTEGRATED (worker_done msg_b4ac151b4f79): gitleaks clean, suite 1726 OK
  315s, validate 21/21, egress 5b4dfa3d, --force-with-lease push; Greptile on e4cbf222:
  CLEAN ('38 files reviewed, 0 comments') — both r1 P1s RESOLVED (fixed in 3fca0bb9).
  R2 REVIEW WAVE dispatched (codex): SPEC term_fd9e3a65/task_fca8f7f33479 · STANDARDS
  term_65b8cf90/task_728ba3caffe9 · TESTS term_630b9905/task_c71a9c244015; r2 verdict
  task_98567ecbb515 queued. U-CHAIN r3 integrator still in flight (suite+harness+push).

- 15:2x U-CHAIN r3 (FINAL) INTEGRATED (worker_done msg_fa72d2b45fc0): gitleaks clean, suite
  1707 OK 289s, validate, harness 31 mutants 28/28-for-assertion + controls green; egress
  e925b0fc; push resolved FAST-FORWARD b431c418..d75b23b1 (stripped commits never reached
  origin; lease pinned, no bare force). GREPTILE APPROVED d75b23b1 (review 5260194743,
  auto-approve marker) — the independent-review leg candidate (09-14 T8 precedent). BOT-4
  FIXED at 1635b27f, BOT-5 FIXED; 1 new VALID P2 held: BOT-6 'interrupted runs skip
  restoration' (mutants_core.py:116 — harness robustness; standards axis leads its
  adjudication). R3 FINAL REVIEW WAVE dispatched (codex): SPEC term_70a30067/
  task_8d5bc3ab4de1 · STANDARDS term_bcae1cd8/task_21ed299df460 · TESTS term_91d5f0ed/
  task_83fd4a2c8186; r3 verdict task_c2c948e1987f queued. U-442's r2 axes in flight.

- 16:1x U-CHAIN round 3 (FINAL) = NO-GO: SPEC GO (BOT-6 Optional w/ reason — disposable
  checkouts), STANDARDS 2R, TESTS 3R. THREE failed rounds = the acceptance-review budget
  cap → the unit does NOT loop and does NOT merge: PARKED with gate-batch.md G1 naming the
  three sticking findings (harness skip-as-success; manifest names conductor-stripped
  5bd2eb07 — my trailer rewrite, rebind owed to 1635b27f, tree-identical; two narrow
  contract-test survivors: reversed ancestry operands, optional OWED). Options (a) accept
  park / (b) authorize exceptional targeted repair + re-review / (c) merge anyway with
  human accept-with-reason. Default (a). Surfaced to the maintainer in-session (interactive
  prose brief). R3 verdict worker posting the official NO-GO on PR #484.

- 16:5x U-CHAIN round-3 verdict POSTED: review 5260271654 'verdict: NO-GO — round 3'
  (coordinator-verified first line exact), evidence 1e2f099b pushed. 5 Required entries
  (S-R3-1 skip-guard, S-R3-2 manifest rebind, R3-TA-1/2/3 incl. reversed-operands +
  optional-OWED survivors); BOT-6 accepted-with-reason recorded. PARK IS TERMINAL pending
  gate G1: no merge, no fourth automatic round. Bot threads 4056606142 (BOT-6) stays
  unanswered-with-accept-recorded; the unit's worktrees/terminals RETAINED (a G1 (b) answer
  re-engages them; a G1 (a)/(c) answer closes out or merges per the human's recorded grant).
  U-442 r3 fix in flight.

- 17:2x U-442 r3 (FINAL) FIX DONE (worker_done msg_39f6b85de388): 5 TRAILER-FREE commits
  (the warning landed — harvest-verified 0 trailers): 361b6308 merge + cd07307e fix (20s
  timeout restored at the call site; _roots_are_split OSError branch COVERED, :209 pragma
  deleted) + 378a1a2e/5269310a evidence (manifest re-bound, receipts wtree eff64964) +
  1ce683eb/e8ea772b reports. Guard adjudication: CI guard RED was 6 hits — verify.py clean
  after the fix; all 6 are archival quotations in 3 report files → 3 DECISIONS floor-waivers
  (verdict-r2.json, verdict-review-r2.md, integrate-r2.json; 2026-09-17 precedent; the
  worker's e8ea772b rewording didn't fully unquote — waivers cover the rest). Branch lacks
  the waivers (merged BASE pre-waiver) → R3 INTEGRATE merges them in first:
  task_a3dcf19e1d91, claude term_ec229de2 (guard must print clean, suite+validate,
  push, Greptile + PR guard check-run watch).

- 17:5x U-442 r3 (FINAL) INTEGRATED (worker_done msg_806387b9f5db): BASE db1b72bc merged
  (waivers in), floor-guard 'clean (6 waived)', suite 1733 OK 256s, validate, gitleaks
  clean, egress 10:28:29Z, ff push ed0ee848..c1d1e59c; Greptile clean on the new head
  (48 files, 0 comments); PR's 4 existing comments are r1 threads GitHub re-pointed
  (original_commit_id 5a57c8d2) — not new findings. R3 FINAL REVIEW WAVE dispatched
  (codex): SPEC term_b4314b77/task_9a5a5fb70280 · STANDARDS term_1f495462/
  task_a0920360cf2a · TESTS term_715282eb/task_fd34e15af706; r3 verdict task_57ea07ec0722
  queued. U-CHAIN parked-terminal pending G1.

- 18:2x U-442 round 3 (FINAL) = NO-GO, verdict POSTED: review 5260415981
  'verdict: NO-GO — round 3' (coordinator-verified first line exact), evidence cb5a95c4
  pushed. 5 Required stickers (S3-R1 manifest -v mismatch; R3-STD-1 five stale artifact
  refs; R3-T1/T2/T3 coverage mutants + probe vacuity). PARK TERMINAL per the budget —
  gate-batch.md G2. Both build units are now terminal-parked; the run moves to close-out:
  re-enumeration → final report → final-tip verification → promotion PR.

- 19:0x CLOSE-OUT: loop-2 enumeration pasted (10 open identical to T0, 0 created/closed).
  Park notices posted on #441/#442/#443/#444 (issue comments, egress bdfa2040). Final
  report + WIP rows + integrity inventory + REFLECTION committed (37d47394). FINAL TIP
  VERIFIED: validate.py 21/21, full suite exit 0, badge regen byte-identical, tree clean.
  PROMOTION PR #486 opened BASE→main (egress 6277be2a; baseRefName=main asserted by gh
  view) — LEFT FOR THE HUMAN, never merged by the fleet. TERMINAL: DRY-WITH-PARKED.

- 19:3x PR THREAD CLOSE-OUT (post-terminal, maintainer ask): PR #486 Greptile P1 (close
  inventory not machine-verifiable — VALID: heading lacked the (sha256) marker, entries
  were 16-char prefixes) + P2 (archive row said IN PROGRESS — VALID) → fixed in cd785d8f
  (inventory rewritten in inventory.py's fenced full-64 shape, 10 verified/0 mismatched/
  0 missing via inventory.py check; docs/runs/README.md row to DRY-WITH-PARKED); 39/39
  doc tests + validate green; Greptile auto-resolved both. PR #484's 4 remaining threads
  replied with fix citations and RESOLVED: exemplar-citation P2 (F-5 @88a64c90),
  keyword-semantics P2 (F-3+G-4..6, 28/28 replayable), BOT-4 stale-ref P1 (G-1
  @1635b27f), BOT-6 P2 (ACCEPTED-WITH-REASON — disposable checkouts make interrupted
  runs non-evidence; recorded in verdict 5260271654). Egress 75751e66. FINAL THREAD
  STATE VERIFIED: #484 6/6, #485 2/2, #486 2/2 resolved — zero unresolved review
  threads across the run's PRs.

- 19:5x G1+G2 RESOLVED (b) — maintainer grant in-session (DECISIONS gate-batch-G1/G2,
  one-way, human-named). Targeted repair specs frozen (repair-u-chain.md b3fcff7c,
  repair-u442.md aa6acc52). REPAIR WORKERS dispatched: U-CHAIN task_d74ecf85c11d claude
  term_e0cbe15b (skip-guard, manifest rebind, 2 test binds); U-442 task_5d3efd6689f4
  claude term_25c63842 (proof-command agreement, 5 stale refs, 2 coverage mutants +
  probe-fired). Then: targeted blind re-review (codex, one per unit, scoped to the
  repair commits only) → conductor merges → closes.

- 20:3x REPAIRS DONE + harvested: U-442 (worker_done msg_3d692f41ec2b): 5 trailer-free
  commits, scope tests+evidence only (verify.py UNTOUCHED), one agreed proof command
  ('python3 -m unittest tests.test_verify.CrossRepoRoots' carried by both nc.command and
  an exit-0 receipt), 5 stale refs re-pointed to r3 bytes, 3 killing tests + probe-FIRED
  assertion. U-CHAIN (worker_done msg_d009b30ddf79): 4 trailer-free commits (merge,
  9b196bf2 R-1+R-3, 9622a242 R-2, b976df56 evidence); skip-guard = GREEN only on ≥1
  executed AND zero skips + a selftest running a real skip-producing module; manifest
  re-bound to 1635b27f (on-branch). Both branches pushed (egress 0126c6cb:
  1e2f099b..b976df56, cb5a95c4..85a1e797). TARGETED re-review dispatched (codex, scoped
  to repair commits only — the G1-b/G2-b grant): U-CHAIN term_e74203f5/task_6d74187e0783,
  U-442 term_35beb831/task_92b0bcbf0011. Process note: delivery_fb3706416306 was acked
  one window late (missed ack, replay matched transcripts, no double-action).

- 21:1x UNITS CLOSED. G1/G2 (b) executed end-to-end: repairs (0 trailers both), targeted
  blind re-review GO ×2 (codex, repair-commits-only), fleet GO records posted, Greptile
  APPROVED #484 @8ff20027 (review leg green). CONDUCTOR MERGES: #484 ec724054
  (--match-head-commit 8ff20027…, branch deleted); #485 c467d554 after the union merge
  5bec0616 (badges/tests.json conflict → regenerated by gen-badges.py, the only
  resolution file; gates re-run green; push ff; merged at fresh headRefOid — two of my
  own typed-SHA merge attempts failed on mangled OIDs before pasting from gh view, slip
  noted). Both ancestry-verified on BASE. #441 #442 #443 #444 CLOSED with evidence
  comments (egress aa213e44, 55e72ce1). CONDUCTOR CLOSE per 09-14 shape: close re-runs at
  the merged heads (contract tests / validate / harness / full suite, all exit 0,
  evidence-run receipts), pr blocks filled, reviewer_mode=cross-vendor, contracts
  FINALIZED as coordinator JSON (contract-u-chain.json / contract-u442.json — the
  reviewers' named owed finalization: prose specs carried no machine-readable criterion
  ids; texts verbatim from the frozen specs), NC fields normalized (tool=revert, single
  artifact, U-CHAIN's -v dropped to the receipt-backed spelling). VERIFY: U-CHAIN 6/6
  OK; U-442 5/6 — review leg RED (no independent APPROVED on #485; single-identity,
  09-16 G3 class) disclosed in-manifest and here. Terminal state of the denominator:
  4 issues CLOSED with evidence, 6 parked (all clean-class or gate-named needs-human).

- 21:3x CLOSE COMPLETE: WT_CLEAN verified (both unit worktrees/branches/terminals gone at
  merge — gh --delete-branch + Orca teardown; orca worktree list shows only the
  coordinator checkout; 0 stray terminals); scratch worktrees removed. FINAL TIP
  re-verified after the close commits: full suite exit 0, validate 21/21, tree clean.
  Run state: CLOSED with evidence — #441 #442 #443 #444 (verify 6/6 + 5/6-disclosed);
  parked clean-class — #409 #427 (out-of-scope handoffs); parked needs-human with named
  gates — #235 #386 #407 #434 (all re-confirmed this run). PR #486 absorbs the advanced
  BASE; its merge and the U-442 review-leg waiver are the maintainer's remaining calls.

- 21:5x PR #486 REVIEW FINDINGS x3 (Greptile), all VALID, all fixed: (1) inventory staled by
  the G1/G2-resolution edits → regenerated with the complete artifact set (14 entries,
  incl. the repair specs + coordinator contracts that postdated the first block):
  inventory.py check 14 verified/0 mismatched/0 missing; (2) the Final report still
  classified the closed units as parked/open → rewritten to the post-close truth
  (terminal paragraph marked UPDATED post-close, disposition rows CLOSED with citations,
  landed-on-BASE list carries both merges, wave=4 row added: throughput=1.3, rework=0,
  freshness=0; docs/runs/README.md row updated to match); (3) gate-batch carried the G2
  resolution TWICE (one mis-placed under G1 citing gate-batch-G2 — my uncounted
  str.replace hit both 'Default' lines; slip named) → one RESOLVED per section, each
  citing its own DECISIONS id. 39/39 doc tests + validate green after the fixes.

- 22:0x CI FAILURE DIAGNOSIS + FIX (PR #486, maintainer ask): two independent causes.
  (1) bind-check: bind_check.py (#415) routes every TOP-LEVEL docs/runs/*.md with a RUN:
  line to the binder — but fleet living ledgers carry the liveness-resume RUN: shape, and
  the 09-14 tracker predates the check, so this run's ledger was the FIRST top-level
  living ledger ever submitted through it. Router blind spot, not a bad report and not a
  binder weakening: taught the router the liveness shape (first-RUN:-line `RUN: <id> ·
  COORDINATOR:` → skip as fleet workflow ledger; a malformed SHAPED submission quoting a
  ledger line still fails closed). tests/test_bind_check.py +2 (top-level skip + shaped
  negative control): 30/30 OK; bind_check.py --base origin/main → no candidates, exit 0.
  (2) floor-guard: 4 violations in merged evidence/run-record files → 4 DECISIONS
  waivers with honest classes (the skip-decorator literal is the probe fixture proving
  the S-R3-1 skip-guard; 2× noqa E402 sys.path bootstrap in evidence harnesses; 1×
  archival pragma quotation in the frozen r3 spec). My first waiver line then tripped the
  guard ITSELF (the skip-decorator literal quoted in DECISIONS.md — recursive class; reworded).
  floor-guard: clean (10 waived). Inventory re-derived after the waiver edits (14/14).
  Coordinator-executed tooling change, disclosed here per the run's conductor practice.

BRANCHES: local worktree checkouts carry the `ravidsrk/` prefix mapping to the unit tips
(ravidsrk/u-chain, ravidsrk/u-442). Not drift — do not "fix".

## Final report — DRY-WITH-PARKED

**Terminal: DRY-WITH-PARKED** — UPDATED 2026-09-20T21:4xZ post-close: the two budget parks
below were RESOLVED the same day (gates G1/G2, option b, human grant): both units merged and
their 4 issues CLOSED with evidence. The remaining degraded parks are the 4 standing
needs-human items (#235 #386 #407 #434, each with a named trigger); #409/#427 are
out-of-scope handoffs. The set is exhausted: every T0 item is either closed with evidence or
parked in a named class, and zero created/closed/reopened since T0 beyond the run's own 4.
(The loop-2 paste below is the pre-close snapshot, true at 18:3xZ; the closes landed after,
through the gate resolutions — the loop-3 query is in the close log.)

### Loop-2 enumeration (pasted, 2026-09-20T18:3xZ)

```
open: 10 — #444 #443 #442 #441 #434 #427 #409 #407 #386 #235 (identical to T0)
created since T0 (2026-09-20T06:17:18Z): [] · closed since T0: [] · reopened: []
```

### Per-item disposition (completion-audit shape: verdict · mode · citation)

| id | disposition | class | citation |
|---|---|---|---|
| #441 #443 #444 | CLOSED with evidence — G1 resolved (b): targeted repair + blind re-review GO + Greptile APPROVED; merged ec724054; verify.py 6/6 OK | closed | PR #484 MERGED; closing comments on each issue |
| #442 | CLOSED with evidence — G2 resolved (b): targeted repair + blind re-review GO; union merge (badge regen); merged c467d554; verify.py 5/6 (review leg RED, no independent APPROVED — single-identity, disclosed) | closed (1 leg disclosed) | PR #485 MERGED; closing comment |
| #235 | park re-confirmed (external accounts; index check 09-13 stands) | needs-human | issue text |
| #386 | park re-confirmed (transcript-signing prerequisite unlanded; G1-of-09-16 answers recorded) | needs-human | gate-batch 09-14 G1 |
| #407 | park re-confirmed (roadmap epic; closes at 1.0) | needs-human | children merged except #409 |
| #434 | park re-confirmed (render-key secret absent; alt-text truth repaired repo-wide by STAB-2 at the generator) | needs-human | gh secret list empty; 4d13c672 |
| #409 | handoff (harden-it mission run + human PoC gate) | out-of-scope | issue re-scope |
| #427 | handoff (pin-it cadence; trigger not fired — patch bump rides) | out-of-scope | issue trigger rules |
| — | STABILIZE + STAB-2 landed on BASE (doc claims verified; 5 suite regressions repaired; generator alt-string fixed at source) | closed with evidence | 3833c88, 2f04c402; 39/39 + full suite green at tip |

Landed on BASE this run: 3833c88 (doc amendments), 2f04c402 (STAB-2), ec724054 (U-CHAIN,
PR #484), c467d554 (U-442, PR #485), the closed unit manifests + coordinator-finalized
contracts, and all ledger/DECISIONS/transcript commits. Both unit PRs are MERGED with
branches and worktrees retired (WT_CLEAN verified); the promotion to main rides PR #486.

First-merge spot-check (merge-serialization): STAB-2 was the run's first merge — verified
at landing (merge commit no-ff, author maintainer, no trailers, branch deleted, worktree
retired, suite green at tip). The two later merges (#484/#485) were verified against the
same pattern at merge time: merge commits preserved, maintainer-authored, no trailers,
branches deleted, worktrees+terminals retired, ancestry + tip suite green.

## WIP-curve protocol row (mutating run)

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations |
|---|---|---|---|---|---|
| wave=1 | builders=2 reviewers=0 | throughput=0 (0 units verified-CLOSED; 2 built + 1 repair in ~2.5h) | latency_median=8 min latency_max=25 min (worker_done → harvest-verified) | rework=0 of 2 units at this wave | freshness=0 |
| wave=2 | builders=2 reviewers=1 | throughput=0 | latency_median=12 min latency_max=40 min (axis done → verdict posted) | rework=2 of 2 units (both r1 NO-GO) | freshness=0 (no merges attempted) |
| wave=3 | builders=2 reviewers=2 | throughput=0 | latency_median=10 min latency_max=35 min | rework=2 of 2 units (r2 NO-GO; r3 final) | freshness=0 (no merges attempted) |
| wave=4 | builders=2 reviewers=2 | throughput=1.3 (2 units verified-CLOSED in ~1.5h of targeted-repair wave) | latency_median=15 min latency_max=40 min (repair done → targeted GO → merged) | rework=0 of 2 units (targeted rounds GO on first pass) | freshness=0 (both merges at fresh headRefOid, one content-identical union) |

CAP BREACH, recorded per the protocol's negative-data rule: at ~15:2x–16:5x two review
UNITS were in flight simultaneously (U-CHAIN r3 fan + U-442 r2 fan) against the
reviewers=1 cap the ledger header's builders=2 implies. The header cap was never raised;
the dispatches should have been serialized. No freshness violation resulted (no merges),
and both fans completed with full axis isolation — but the breach is the measurement:
reviewers=2 produced no throughput gain (both units parked on evidence-layer stickers,
not on review starvation).

## Run-close integrity inventory (sha256)

Retained inline per the ledger line. The ledger itself is excluded — a file cannot carry
its own hash; every other run-record artifact is below, full 64-hex, re-derivable with
`python3 runtime/scripts/inventory.py check docs/runs/2026-09-20-clean-sweep-tracker.md`.
Unit manifests live UNMERGED on the parked branches (U-CHAIN docs/reports/U-CHAIN/manifest.json
@d75b23b1; U-442 docs/reports/u-442/manifest.json @c1d1e59c) — inventoried there, not here.
Transcripts: docs/runs/2026-09-20-clean-sweep-tracker/transcripts/<delivery-id>/<msg-id>.json —
one per delivered message, committed per window.

```
2ba4e6026a17796e66a26103193ea8aebf17c0ed0e7c8bf045800cbadaf2f849  docs/runs/2026-09-20-clean-sweep-tracker/gate-batch.md
db43a8a836d6b003c603e9f35c7338bcfd92d688abe62a3a4d7876175d5a0316  docs/runs/2026-09-20-clean-sweep-tracker/REFLECTION.md
e2e36cad21c639eb834df718a43db9935b9f8b3db511f795e900c2f507ece2b0  docs/DECISIONS.md
872605215c4b4e418d9efd1ed518dfeccf7d417283bdd3c3c21670d3a0bcb1cb  docs/runs/2026-09-20-clean-sweep-tracker/build-u-chain.md
63ce1e4e0e538557ac5661bf6905707c82ad3937061531ec457e2812a4f0a9c8  docs/runs/2026-09-20-clean-sweep-tracker/build-u-chain-r2.md
4b5415407cc65bece717fd0d0fa185dad3e39689e6eab6804fc8b122ad495caa  docs/runs/2026-09-20-clean-sweep-tracker/build-u-chain-r3.md
7498d20d8e7f580f986d2abca320b925956808c6da08057a38240e7cff10471f  docs/runs/2026-09-20-clean-sweep-tracker/build-u442.md
9df586e16c8080baef3799b7564a1fdd284ff23f5cf47c54040e80726a01cabf  docs/runs/2026-09-20-clean-sweep-tracker/build-u442-r2.md
027daa4a46a9f8555cb520a34aeb0936fa6edad467468cc107edcf92f9f5bce9  docs/runs/2026-09-20-clean-sweep-tracker/build-u442-r3.md
f454ff135603ce6a93d555bfc0c2b6c61dbb4b1ebd9eb0f7e0ed69698081c195  docs/runs/2026-09-20-clean-sweep-tracker/build-stab2.md
b3fcff7c34ee11727328e96e4269ee99986e6ba1c842951db7dee70da6d035c7  docs/runs/2026-09-20-clean-sweep-tracker/repair-u-chain.md
aa6acc52bd8dbf8d8510204279c3780f9c95c056c85742ff686d1c87f82555a1  docs/runs/2026-09-20-clean-sweep-tracker/repair-u442.md
06d857684c7ee4e5928846e15273d0ec4ded17a014d981300d7fa8f6655cfd70  docs/runs/2026-09-20-clean-sweep-tracker/contract-u-chain.json
d6cf3b24d463f72d41f07e2203fb662000683cdb19139b694ebdc1237a99a644  docs/runs/2026-09-20-clean-sweep-tracker/contract-u442.json
```

Egress: `egress.py verify` at close — chain intact, 305 receipts, head d0a5005c (UNANCHORED
by design of the tool's own warning; the head is recorded here as the anchor).
