# Runtime scripts and operator config — reference

The operator-facing CLIs under `runtime/scripts/` and the JSON registries under
`runtime/` that had no guide entry: what each is, its usage, flags, and exits.
Every section anchors to its source file (read the implementation, not this page,
when they disagree) and to the test that pins its behavior. Claim-checked by
`docs/runs/campaign-2026-09-16-document-it/extractor/claimcheck.py`.

## `decisions.py`

Writer, reader, and validator for the DECISIONS log (`docs/DECISIONS.md`). Source
`runtime/scripts/decisions.py:1-63`; behavior pinned by `tests/test_decisions.py`.

Usage: `python3 runtime/scripts/decisions.py [--file PATH] [--doors PATH] <subcommand> ...`

Subcommands: `append`, `active`, `tally`, `check`.

Flags: `--file` (log path, default `docs/DECISIONS.md`), `--doors` (door registry,
default `runtime/one-way-doors.json`). `append` takes `--id`, `--class`, `--answer`,
`--why`, `--task`, `--source`, `--ts`; `tally` takes `--lens`, `--json`.

Log line format: `ts · gate-or-ask-id · class · answer · why · task?` with classes
`mechanical`, `taste`, `one-way`. `append` refuses unknown classes, empty id/answer/why,
fields containing `·` or newlines, credential-shaped values, lines tripping the one-way
keyword net without class `one-way`, and `one-way` lines without `source=human:<name>`
(via `--source`). `active` lists non-superseded lines (newest per id wins; an answer of
exactly `superseded` retires the id). `tally --lens <name>` reports the consecutive
zero-finding streak for `lens-tally:<lens>` lines and whether the lens may auto-gate off
(10+ zeros, never for `security`, `privacy`, `data-migration`).

Exits: 0 ok · 1 validation failure · 2 could-not-run.
