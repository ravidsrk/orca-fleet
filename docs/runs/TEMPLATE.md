# Run report — <mission> <self-run | external-run>, <YYYY-MM-DD>

Copy this file to `docs/runs/<YYYY-MM-DD>-<mission>-<self-run|external-run>.md`, fill every
section, add the row to the index table in [README.md](README.md), then set the mission's
`metadata.proof:` and `metadata.proof_evidence:` to the new path.

Nothing else advances a tier, and naming the mission is not enough (issue #259).
`runtime/scripts/run_report.py`, called from `scripts/validate.py`, requires all of:

* the `RUN:` header below, exactly once, with every field;
* `inventory_at=` a commit that exists **in this repository**;
* `manifest=` a path that exists at that commit and lives inside this run's own
  `docs/runs/<YYYY-MM-DD>-<mission>…/` artifact directory — borrowing another run's manifest is
  refused;
* `verifier=GREEN|RED` matching what the "Verifier outcome" section records (a RED is honest: a
  solo run cannot manufacture an independent approver) — and the body must show the ACTUAL
  invocation, `verify.py … --manifest <that same manifest path>`, not a description of it. Paste
  the command and its exit code; a sentence about having run it is not a transcript;
* the integrity inventory re-hashing at `inventory_at` — zero mismatches, at least one verified
  path inside this run's own directory, **the graded manifest among the hashed paths**, and none
  of this run's own artifacts absent there. Paths outside the run directory may have moved on;
  the evidence the run is responsible for may not.

If your artifacts are not committed here, this report is recorded history and the mission stays
`doctrine-only`. Say that in an "Evidence binding" section rather than claiming a tier.

```
RUN: mission=<mission> tier=<self-run|external-run> inventory_at=<commit> manifest=docs/runs/<YYYY-MM-DD>-<mission>…/<manifest>.json verifier=<GREEN|RED>
```

| Field | Value |
|---|---|
| Mission | `<mission>` — `skills/<mission>/SKILL.md` at `<sha>` |
| Tier claimed | `self-run` (target is this catalog) or `external-run` (target is another repo) |
| Target | `<repo, surface, PR, or tracker>` |
| Fixed point | BASE `<branch>` @ `<sha>` · FORK_POINT `<sha>` · frozen spec / issue list `<ref + digest>` |
| Coordinator / workers | `<host + model>` · worker profiles `PROFILE=<ro or rw>` · TASK pack `<matt or addy>` |
| Orca | `orca status --json` → `runtime.reachable: true` at `<time>` (paste the line) |
| Human gates | `<gate>` — `<who>` @ `<time>` — `<decision>` |

## Terminal state

The mission's named terminal (from its `## Two terminal outcomes` section, degradation marker
included when one applies) and the ledger rows that show it, in the mission's canonical row shape:

`| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |`

## Convergence proof

Every clause of the mission's `## Convergence proof`, each with the evidence that discharges it:
a file path, a command with its exit code, or a PR url with its `reviewed_sha`.

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| `<PHASE>` | `<command>` | `<exit code / verdict>` | `<path or url>` |

## Verifier outcome (recorded exactly)

`python3 runtime/scripts/verify.py --manifest <manifest> --contract-source <path@ref> --contract-digest <sha256:…>
--unit-class <mutation|report-only|planning> [--lighting <lit|dark-eligible>] [--dispatch-record <path@ref>
--dispatch-pubkey <path@ref>] [--base <branch>]` — output and exit code verbatim, RED runs included.

Where each flag comes from: `--contract-source` is the coordinator's frozen contract from the Fixed point
row, supplied out of band (`ORCA_CONTRACT_SOURCE` under `verify-gate.sh`); `--contract-digest` and
`--unit-class` are the signed dispatch record's `contract_digest` and `unit_class` — always pass both,
since a missing unit class fails safe to mutation-strict checks; `--lighting` is the record's optional
`lighting` — when the record signs it, always pass its exact value (a signed `dark-eligible` passed as
nothing loses the review waiver and goes RED) **and** make sure the unit's manifest carries the same
`lighting` value: the verifier reads an omitted manifest lighting as `lit` and reports a fatal
`lighting swap` against a `dark-eligible` dispatch; when the record omits it, omit the flag. Omitting
the CLI flag does not populate the dispatch lighting, and with `--dispatch-record` a value the record
did not sign is a fail-closed RED. `--base` is the integration base for ancestry. Omitting the contract
flags is a fail-closed scope RED to record, not a flag to drop. `docs/verify-gate.md` and
`runtime/gate-classification.md` are the authority for these semantics; this paragraph summarizes them.

## WIP-curve protocol row (mutating self-runs)

Required by `runtime/attention-budget.md` for every mutating self-run; omit only for report-only
missions and say so.

| WIP setting | builder throughput | verification latency | rework rate | freshness violations |
|---|---|---|---|---|
| `<n>` | `<verified-CLOSED per hour>` | `<median>` | `<rate>` | `<count>` |

## Deviations and lessons (recorded, not hidden)

- `<what the run did differently from the SKILL, and why>`

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `<file>` | `<digest>` | `<tool + version, date>` |

When the run's artifacts live outside this repo, replace the table with one line naming where the
integrity inventory is retained.

## Gates

`python3 scripts/validate.py`, `python3 -m unittest discover -s tests`, and
`python3 runtime/scripts/proof_status.py --check` at the run's final head — output and exit codes.
