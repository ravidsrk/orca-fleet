# Runtime policy — scheduled mission runs (Orca automations)

Orca `automations` run a prompt on a schedule (cron / `hourly` / `daily` / `weekdays` / `weekly` /
RRULE) against a fresh per-run worktree or an existing workspace. A scheduled mission is that: an
UNATTENDED coordinator invocation of a mission on a cadence — a nightly `clean-sweep`, a weekday
`review-it` sweep of open PRs.

## Create

```
orca automations create --name "<name>" --trigger daily --time 03:00 \
  --prompt "<the mission invocation, e.g. 'clean-sweep source=tracker on this repo'>" \
  --provider <coordinator agent> --repo id:<repoId> --json
```

`--repo` gives each run a fresh worktree (preferred for missions — clean BASE per run); `--workspace`
targets an existing one. `--disabled` while testing. The provider is the COORDINATOR; workers still
spawn per the roster (sandbox-policy.md).

## A scheduled run is a full run, unattended

- **Autonomy is headless** (gate-classification.md): auto-pick the recommended option on
  mechanical/taste gates; a ONE-WAY gate (freeze, BASE→default promotion, deploy, spend, secret
  rotation) is NEVER faked — the run PARKS it and winds down, surfacing what a human owes. So only
  missions whose value lands BEFORE a one-way gate schedule cleanly: `review-it` (report-only, no
  gates), `clean-sweep` with a bounded source (stops at the promotion PR). A scheduled `ship-it`
  from raw intent parks at the freeze gate almost immediately — schedule it only from a
  pre-frozen spec, and it still stops at PROMOTION_READY.
- **Each run is independent** — its own preflight, BASE, ledger, evidence, and run report. It never
  reuses a prior run's BASE.
- **Cross-run anti-inflation applies** (liveness-resume.md): a recurring run re-reads the prior
  run's completion report and re-verifies its green-but-unverified claims FIRST — a nightly sweep
  must not trust last night's checkmarks.
- **All safety rails hold** — merge ≠ deploy, one-way doors stay human, least-privilege workers. A
  scheduled run stops at BASE / a report; it never promotes to the default branch.

## Completion

The automation's run output is the mission's normal completion report plus the run's terminal
state and the human-owed queue (parked one-way gates, the promotion PR). A scheduled run that
parked at a gate is a correct outcome, not a failure — the next fire re-enumerates from current
state.
