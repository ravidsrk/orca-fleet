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

## `deny-hook.sh`

PreToolUse guard for read-write workers (Bash, Edit, Write). Reads the hook event JSON
on stdin, writes one decision object on stdout. Source `runtime/scripts/deny-hook.sh:1-80`;
behavior pinned by `tests/test_deny_hook.py`.

Usage: hook mode reads stdin (no arguments); `deny-hook.sh --settings <worktree>` prints
the settings.json registration block with the worktree boundary resolved.

Flags: `--help`, `--settings`.

HIGH tier denies (never asks) for Bash: recursive delete rooted at `/`, `~`, `$HOME`, or
`/*` (or carrying `--no-preserve-root`); force-push to the default branch (including the
`+main` refspec and outright deletion forms); `git push --force` without an effective
`--force-with-lease`; `orca orchestration reset`. An effective `--force-with-lease` exempts
a force-push but never a deletion. The Never list asks instead: live-prod mutation,
credential provisioning, destructive teardown, unpinned remote execution, publishing,
history-discarding local git. When `ORCA_UNIT_WORKTREE` is set, writes outside it deny —
Edit/Write `file_path`, NotebookEdit `notebook_path`, and absolute-path Bash redirects and
`tee` destinations — resolved through the full symlink chain.

Exits: always 0 — the decision is the output, not the status.
