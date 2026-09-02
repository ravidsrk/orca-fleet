# Run report — <mission> <self-run | external-run>, <YYYY-MM-DD>

Copy this file to `docs/runs/<YYYY-MM-DD>-<mission>-<self-run|external-run>.md`, fill every
section, add the row to the index table in [README.md](README.md), then set the mission's
frontmatter `proof:` and `proof_evidence:` to the new path. Nothing else advances a tier:
`scripts/validate.py` refuses `proof:` above `doctrine-only` unless the report exists here, names
the mission in its filename and body, and `tests/test_docs_navigation.py` requires the index row
plus the integrity inventory below (inline, or a named retention location).

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
nothing loses the review waiver and goes RED); when the record omits it, omit the flag. The manifest
defaults an omitted lighting to `lit`, but omitting the CLI flag does not populate the dispatch
lighting, and with `--dispatch-record` a value the record did not sign is a fail-closed RED. `--base`
is the integration base for ancestry. Omitting the contract flags is a fail-closed scope RED to record,
not a flag to drop.

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
