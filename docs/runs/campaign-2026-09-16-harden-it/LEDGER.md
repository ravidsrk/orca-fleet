RUN: - · COORDINATOR: solo/46f45b71 · BASE: - · FORK_POINT: - · T0: 2026-09-16T12:24:03Z · SOURCE: THREAT-MODEL.md@42ddea9b29d201cef538d6bc6f6a6c5968a95416ae32ea647f03f4d47ae94dfc · WIP: builders=1 reviewers=1

# Ledger — harden-it self-run, campaign-2026-09-16

PHASE: ORIENT → AUDIT (see phase log at bottom; forward-only)

Solo-run degradations (recorded once, apply to every unit — never silent):
- D1 RUN:- — no Orca orchestration namespace: `run-create` refused with
  `no_active_sender_terminal` (no live Orca terminal in this session). Receipt:
  `receipts/run-create-refused.txt`. WATCH/RESUME/recovery paths that need a Run id
  are inapplicable; ledger file + git are the durable state.
- D2 BASE:- — no integration BASE bootstrapped: harden-it bootstraps BASE to integrate
  per-unit fix PRs; this run opens no PRs (task orders: no push/PRs/merge) and Phase-0
  preflight ran `--mode readonly` (exit 0). If a VERIFIED P0/P1 needs a fix, BASE is
  bootstrapped then and the header rewritten. Audit fixed point = origin/main tip
  `c46d4b3f3371e41408aed19e54476fa194c20b42` (== the SHA a BASE would fork from).
- D3 No independent verifiers/workers dispatchable (solo session, D1). Every finding is
  "self-verified — no independent verifier" per triage-findings §5, and any mutation
  unit stops at the executed-control lane (acceptance-review SOLO RUN). Re-attack, where
  owed, is same-context and labelled as such.
- D4 No ephemeral sandbox available: any networked/destructive/supply-chain PoC is
  evidence-backed PARKED per PoC ROUTING, never executed on the host.

Worker TASK pack: addy (one router; gstack never co-mounted). Triage mode: Gated.

## Findings (harden-it canonical row)

`| task_id | finding | class | VERIFIED | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | REATTACKED | WT_CLEAN | lighting | park | evidence |`

| task_id | finding | class | VERIFIED | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | REATTACKED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | base_ref run: interpolation (bind-check.yml:27) | ci-injection | BELOW-BAR f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave B |
| C2 | gitleaks --no-git 3 hits | secret-scan | REFUTED f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | refuted | receipts/gitleaks-audit.txt |
| C3 | .env.example NC fallback comment | doc-drift | BELOW-BAR f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave E |
| C4 | alert-on-failure step-output interpolation | ci-injection | CLEAN f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave B |
| C5 | unpinned install (install.sh) | supply-chain | BELOW-BAR f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave B |

## Phase log

- 2026-09-16T12:24:03Z ORIENT: threat model committed (digest 42ddea9b…), preflight
  readonly exit 0, gitleaks git-mode clean (receipts/gitleaks-audit.txt is the --redact
  --no-git capture incl. the 3 known waived fixtures; configured git scan: no leaks found).
