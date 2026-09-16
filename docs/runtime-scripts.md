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

## `diff_scope.py`

Fail-loud scope classification: which review lenses a change earns. Emits shell-safe
`SCOPE_<FLAG>=true|false` assignments (sourcable) or a JSON object. Source
`runtime/scripts/diff_scope.py:1-75`; behavior pinned by `tests/test_diff_scope.py`.

Usage: `diff_scope.py [--base REF] [--repo DIR] [--strict] [--json]` (also sourcable as
`source <(diff_scope.py)`).

Flags: `--base` (default origin/HEAD, then origin/main, main, master), `--repo` (default
`.`), `--strict` (any unmatched path exits nonzero), `--json` (emit an object instead of
shell assignments).

Changed set = committed diff vs merge base + working tree + untracked files. Twelve
independent flags: `FRONTEND`, `BACKEND`, `PROMPTS`, `TESTS`, `DOCS`, `CONFIG`,
`MIGRATIONS`, `API`, `AUTH`, `SECURITY`, `A11Y`, `PERF` — path signals plus working-tree
content signals (capped at 256 KiB per file; deleted files contribute path signals only).
Only `BACKEND` is exclusive of frontend view files.

Exits: 0 classified · 2 SCOPE_ERROR=no_base|diff_failed|unmatched.

## `ed25519.py`

Vendored pure-Python Ed25519 (RFC 8032), dependency-free. Import-only library — no CLI.
Source `runtime/scripts/ed25519.py:1-21`; verified against the RFC 8032 test vectors in
`tests/test_ed25519.py`.

API: `publickey`, `signature`, `checkvalid`.

`publickey(seed)` derives the 32-byte public key for a 32-byte secret seed;
`signature(msg, seed, pub)` returns the 64-byte signature; `checkvalid(sig, msg, pub)`
returns True iff valid. Hardening beyond the bare reference: rejects non-canonical
`S >= L`, non-canonical point encodings, and small-order/identity public keys (cofactor
check). Not constant-time: signs and verifies tiny dispatch-provenance records only, never
bulk data or network secrets. Used by `runtime/scripts/dispatch-sign.py` (sign, off the
graded worker) and `runtime/scripts/verify.py` (verify at the gate).

Exits: n/a (library).

## `egress.py`

Content-free, hash-chained receipts for everything the fleet sends off-repo. One JSON
object per line in `.orca/egress.jsonl` (mode 0600), appended BEFORE the send. Source
`runtime/scripts/egress.py:1-73`; behavior pinned by `tests/test_egress.py`.

Status: doctrine names it (`egress.py write ... && <send>`), but no automated sink calls
it yet — receipts are written only by a coordinator following the policy by hand.

Usage: `egress.py [--ledger PATH] <write|verify|grants> ...`

Subcommands: `write`, `verify`, `grants`.

Flags: `--ledger` (default `$ORCA_EGRESS_LEDGER` or `.orca/egress.jsonl`). `write` takes
`--sink`, `--host`, `--payload-class`, `--consent`, `--bytes`, `--payload-file`,
`--payload-sha256`, `--ts`; `verify` takes `--expect-head`; `grants` takes `--json`.

Record fields: `id`, `ts`, `sink`, `host`, `payload_class`, `bytes`, `payload_sha256`,
`consent`, `prev` — never the payload text (sha256 + byte count + kind only). `prev`
chains to the previous raw line; `id` names the line and its chain position. `verify`
recomputes the chain and prints the head digest; pass `--expect-head` with a head anchored
off the writer to catch a wholesale rewrite.

Exits: 0 ok · 2 usage · 3 fail-closed (receipt unwritable, or chain broken).

## `floor_guard.py`

Diff-scoped floor guard: catches the five moves that lower the bar without touching a
stated requirement (silenced checker, test made easier, unfinished work, removed
assertion, lowered threshold or new exception). Reads the merge base against `--base`
plus the working tree plus untracked files. Source `runtime/scripts/floor_guard.py:1-68`;
behavior pinned by `tests/test_floor_guard.py`.

Usage: `floor_guard.py [--base REF] [--constraints FILE] [--waivers FILE] [--repo DIR] [--quiet]`

Flags: `--base` (default origin/HEAD, then origin/main, main, master), `--constraints`
(numbers file, default CONSTRAINTS.md), `--waivers` (DECISIONS log, default
`docs/DECISIONS.md`), `--repo` (default `.`), `--quiet` (findings only, no clean banner).

Rules (stable ids): `silenced-checker`, `test-made-easier`, `unfinished-work`,
`assertion-removed` (removed lines only, in test paths that still exist),
`threshold-lowered` (a number in the constraints file that went down), `new-exception`.
Reporting is redaction-first: rule id, file:line, pattern name — never the matched text.
Waivers come from the DECISIONS log as `floor-waiver:<rule>:<path-or-glob>` records —
never from an ignore file, never prose. Run it OFF the worker.

Exits: 0 clean · 1 un-waived findings · 2 could-not-run (never read as clean).

## `gate-batch.py`

Run-close human gates as typed records, not prose. Store is
docs/runs/&lt;run&gt;/gate-batch.json (schema `gate-batch/1`); the sibling `.md` is a
rendered view re-rendered on every mutation. Source `runtime/scripts/gate-batch.py:1-20`;
behavior pinned by `tests/test_gate_batch.py`.

Usage: `gate-batch.py [--run DIR | --file PATH] <subcommand> ...`

Subcommands: `init`, `add`, `answer`, `waive`, `overtake`, `list`, `stale`, `show`, `render`.

Flags: `--run` (run directory under docs/runs) or `--file` (explicit batch path, for
tests and scratch). `init` takes `--title`, `--run-id`, `--intro`, `--intro-file`,
`--resolved`, `--resolved-file`, `--force-init-over-md`; `add` takes `--id`, `--title`,
`--question`, `--question-file`, `--asked`, `--related`, `--blocking`; `answer` takes a
gate id plus `--answer`, `--date`; `waive` takes a gate id plus `--reason`, `--date`;
`overtake` takes a gate id plus `--note`, `--date`; `list` takes `--status`,
`--blocking`; `stale` takes `--days` (default 7), `--today`; `show` takes a gate id;
`render` takes `--out`, `--check`.

Gates move `owed` to exactly one of `answered`, `waived`, `overtaken` — re-transitioning
is an error. Gate ids look like `G1`. `stale` reports gates owed past N days and never
notifies; `render --check` verifies the view matches the store. `related`/`blocking` are
store-only and never render.

Exits: 0 ok (stale/list report exit 0 either way) · 2 usage or store error.
