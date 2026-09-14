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
| STAB | — | land 4 PR-review hunks (deny-hook/run_report/verify/HUMAN_ACTIONS) + badge regen | conductor landing, worker-executed | f | n/a | n/a | n/a | f | f | lit | — | — |
| T1 | #388 | evidence-run lockfile dirties worktree (filed 15:50Z) | needs-triage | f | f | f | f | f | f | lit | — | — |
| T2 | #389 | run_report WIP validation accepts incomplete reports (filed 15:50Z) | needs-triage | f | f | f | f | f | f | lit | — | — |
| T3 | #364 | per-skill behavioral evals ship zero fixtures (S1) | needs-triage | f | f | f | f | f | f | lit | — | — |
| T4 | #385 | historical-docs polish (S2; commit 2d37bc2 partial) | needs-triage | f | f | f | f | f | f | lit | — | — |
| T5 | #386 | optional hardening: sign manifest+inventory, retention backend (S2) | needs-triage | f | f | f | f | f | f | lit | — | — |
| — | #235 | H-02 marketplace submissions (pre-parked needs-human) | needs-human | — | — | — | — | — | — | — | needs-human: external accounts | prior run + issue text |

PHASE: ORIENT → ENUMERATE done · STABILIZE next · FREEZE after (green BASE + A1/A2 filed + twin enumeration agrees)

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
