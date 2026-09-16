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

> Why: the log was a parser without a writer — hand-typed lines let two coordinators
> disagree about the same record. `append` refuses reclassification by wording (the net
> is built from the registry at `runtime/scripts/decisions.py:load_doors`) and demands a
> human source for one-way lines (`runtime/scripts/decisions.py:HUMAN_SOURCE`). Tallies
> live in committed state so a crashed run's gate verdict survives, and the `security`,
> `privacy`, `data-migration` lenses never gate off
> (`runtime/scripts/decisions.py:NEVER_GATE`): their value is the miss they would catch —
> a policy naming three and a gate enforcing two is how privacy silently switched itself
> off (PR #277 review).

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

> Why: doctrine sits above the model and this sits below it — a read-write worker runs
> with prompts turned down, so the hook is the only thing between an improvised command
> and the disk. Polarity is fail-closed (unparseable input denies) and the decision
> nesting is load-bearing (`runtime/scripts/deny-hook.sh:permissionDecision` — a
> top-level decision is ignored, which is how a deny silently becomes an allow). HIGH
> denies what has no legitimate form while the Never list asks what does; the worktree
> boundary (`runtime/scripts/deny-hook.sh:ORCA_UNIT_WORKTREE`) resolves the full symlink
> chain because a worker that can run a shell can spell any write as a redirect.

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

> Why: the failure mode that makes a scope gate worthless is silence — a shallow checkout
> resolves no base, the diff is empty, and a legitimate-looking zero is recorded. So the
> script distinguishes nothing-changed from could-not-look
> (`runtime/scripts/diff_scope.py:ScopeError`), and the changed set is a union including
> untracked files (`runtime/scripts/diff_scope.py:changed_files`) because a brand-new
> migration is exactly what a reviewer must see. Partial-match stays information, not
> failure, unless a lens opts into `--strict` — turning it into a failure by default would
> break every caller whose repo has a file the table has no rule for.

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

> Why: the gate runs as a completion hook in arbitrary sandboxes where `pip install` may
> not be possible, so the whole gate is stdlib-only — this module's only import is
> `runtime/scripts/ed25519.py:hashlib`. It is the public-domain "slow but correct"
> reference because it signs tiny dispatch records, never bulk data; the one place it
> goes beyond the bare reference is `runtime/scripts/ed25519.py:checkvalid`, which
> rejects malleable and small-order forgeries a bare verifier accepts. A deployment that
> wants constant-time swaps backends behind the same three functions.

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

> Why: the integrity inventory hashes what a run produced, but nothing recorded what it
> sent — this ledger is the second half. Receipts are content-free (hash + count + kind)
> because the ledger is forensic observability, not an exfiltration control: it records
> attempted egress so an accident is auditable, while anything with a shell can still
> send without one. The chain (`runtime/scripts/egress.py:record_id` over fixed
> `runtime/scripts/egress.py:FIELDS`) proves continuity with a genesis, never with THE
> genesis — a rewritten history links correctly — so `verify` prints the head
> (`runtime/scripts/egress.py:head_digest`) for anchoring off the writer, and unanchored
> output says so rather than reading as a clean bill.

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

> Why: each bar-lowering move is invisible to a green build and obvious in a diff — so
> the guard reads the diff, and only loosening is loud. Waivers come from the DECISIONS
> log (`runtime/scripts/floor_guard.py:_WAIVER_ID_PREFIX`, retired through the sibling
> `runtime/scripts/floor_guard.py:_load_decisions`) rather than an ignore file, because
> scope in the id gives the waiver an identity the ledger can retire — and no prose is
> parsed, since a sentence mentioning a rule and a path is not a waiver. Reporting names
> the pattern, never the matched text, which may be the credential someone tried to
> suppress; and the guard runs OFF the worker, because a guard the builder can see is a
> guard the builder edits.

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

## `guard_text.py`

Trust envelope: the only sanctioned path for untrusted text into a task spec. Reads text
from stdin, or from a fetch command given as argv, and emits it inside a bannered envelope
with directive-looking lines labeled. Source `runtime/scripts/guard_text.py:1-57`;
behavior pinned by `tests/test_guard_text.py`.

Usage: `... | guard_text.py --source issue|pr|ci|web [--label TEXT] [--timeout SECS]`
or `guard_text.py --source <s> --fetch <argv...>` (everything after `--fetch` is the
fetch command; no shell).

Flags: `--source` (required; one of `issue`, `pr`, `ci`, `web`), `--label` (provenance
label, sanitized and capped), `--timeout` (fetch timeout seconds, default 60), `--fetch`
(command argv; omit to read stdin).

Labels (`[INJECTION-PATTERN:...]`): instruction-override, authority-claim,
suppression-request, command-execution, role-play-marker — matched over an NFKC-folded
copy with Unicode format characters stripped; the emitted text is always the original
bytes. Forged banners inside the content are defused with a spliced zero-width space.
Output is a rendering for a reader — never round-trip it into a live PR or issue.

Exits: 0 envelope written · 2 usage error · 3 fetch failed or timed out (no envelope on stdout).

## `hitl-loop.template.sh`

Template for a bounded human-in-the-loop reproduction loop — bugs that only reproduce
through a human: a login, a device, a click. Copy it beside the diagnosis notes, edit
only between the EDIT markers, run it from the diagnosis loop. Source
`runtime/scripts/hitl-loop.template.sh:1-26`; behavior pinned by `tests/test_hitl_loop.py`.

Usage: `hitl-loop.template.sh [--rounds N] [--dry-run] [--help]`

Flags: `--rounds` (default 3; must be a number), `--dry-run` (no reads, placeholder
answers, so the steps parse before a human sits through them), `--help`.

Helpers: `step "<instruction>"` (show, wait for Enter), `capture VAR "<question>"` (ask,
read the answer). Capture OBSERVATIONS, never actions. The verdict is the `REPRODUCED=`
line (`REPRODUCED=yes` stops at once; otherwise `REPRODUCED=no` plus `ROUNDS_USED=` after
N rounds) — never the exit code. A checkpoint step ends each unreproduced round.

Exits: 0 done · 2 usage.

## `pm.py`

Tolerant parser for saved `orca orchestration inbox/check` JSON output. Decodes
successive JSON objects, skips keepalive-only envelopes structurally, prints each
message with untrusted fields rendered inert. Source `runtime/scripts/pm.py:1-21`;
behavior pinned by `tests/test_pm.py`.

Usage: save stdout only, then `python3 pm.py inbox.json` (keepalives arrive on stderr —
a merged stream breaks naive parsing).

Flags: none — the single argument is the input file. There is no help flag: passing
--help tries to read a file literally named --help.

Output prints `MESSAGES: <n>`, then per message `ID`, `FROM`, `TYPE`, `SUBJ`, `BODY`,
`PAYLOAD`. Missing fields print as `?`. Every printed field passes through escaping for
C0/C1 controls, DEL, and invisible Unicode (Cf, Zl, Zp), so hostile text can neither
drive the terminal nor reorder what it shows. Malformed segments are skipped line-wise
(counted on stderr); envelopes carrying a `messages` key outside the expected shape warn
as unrecognized rather than silently undercounting.

Exits: 0 ok · 1 usage (no input file) · 2 unreadable input.

## `sandbox_doctor.py`

Reads the transcript of `orca vm recipe doctor` for a recipe and says whether it is
CLEAR for the danger lane. Clear means no fail AND no warn. Source
`runtime/scripts/sandbox_doctor.py:1-25`; behavior pinned by
`tests/test_sandbox_doctor.py`.

Usage: `sandbox_doctor.py <transcript> <recipe-id>`

Flags: none — two positional arguments.

Verdict rule: the transcript must name THIS recipe (the whole id, not a substring of a
longer one) and report no fail and no warn. JSON transcripts read structurally (empty
finding collections are good news; `ok:false` is a finding); plain-text transcripts first
strip "none of these" shapes (`"failures": []`, `failures: 0`, `0 warnings`, `no
failures`) before matching fail/warn/error words. Called by
`runtime/scripts/spawn_worker.sh`, which runs the doctor itself and passes its own output
here — a transcript the caller names is not evidence.

Exits: 0 clear · 1 not clear (reason on stderr) · 2 usage.

## `spawn_worker.sh`

Fail-closed Orca worker dispatch for fleet coordinators: supervised lane
(`worker-start`: worktree + agent terminal + readiness + dispatch) and custom-argv lane
(`terminal create` + `dispatch --inject`). Source `runtime/scripts/spawn_worker.sh:1-80`;
behavior pinned by `tests/test_spawn_worker.py`.

Usage: `SP=<dir> [PROFILE=rw] spawn_worker.sh [--mark-ready] <task_id> <worktree_selector> <title> [agent] [effort]`

Flags: `--mark-ready` (only applies when every declared dep is already completed; the
script never forces ready).

Agents: `claude`, `codex`, `cursor`, `gemini`, `grok`, `droid`, `opencode`, `omp`, `pi`
(default `claude`; effort default `xhigh`); unknown agents refuse. Profiles: `ro`, `rw`
(default), `danger` — least privilege; `danger` needs the ephemeral sandbox plus
`ORCA_SANDBOX_RECIPE`, and the script runs the doctor transcript itself into
`ORCA_SANDBOX_DOCTOR` for `runtime/scripts/sandbox_doctor.py`. Env: `SP` (receipt dir,
default cwd), `PROFILE`, `ORCA_COORD_ALLOW_AUTONOMOUS_WRITE` (must be 1 for rw),
`ORCA_COORD_ALLOW_DANGER` (must be 1 for danger), `ORCA_SANDBOX_RECIPE`,
`ORCA_SANDBOX_DOCTOR`, `WORKER_CMD` (generic override; needs
`ORCA_COORD_ALLOW_CMD_OVERRIDE=1`), `SETTLE_SECS` (default 20, custom-argv lane).

Exits: 0 dispatched · 1 spawn/dispatch step failed · 2 usage or policy refusal (every
typed refusal code) · 3 custom-argv turn UNPROVEN (inspect, never respawn, never
re-Enter) · 4 supervised outcome_unknown (inspect via the receipt's nextCommands, never
respawn) · 5 LAUNCHED_UNUSABLE (worker live but the profile flag unproven — stop it, fix
the host).

## `watchdog.py`

Liveness watchdog: mechanized first response from the worker-supervision policy.
Classifies workers OK/SLOW/HUNG/WEDGED from a heartbeats snapshot, auto-nudges HUNG
once, recommends stop-redispatch on still-HUNG or WEDGED. Source
`runtime/scripts/watchdog.py:1-53`; behavior pinned by `tests/test_watchdog.py`.

Usage: `watchdog.py --heartbeats SNAPSHOT [--config FILE] [--state FILE] [--log FILE] [--now ISO] [--dry-run]`

Flags: `--heartbeats` (required JSON snapshot: run id plus per-worker dispatch,
movement, stop, terminal, wedge markers, nudge history), `--config`
(threshold/rate-limit JSON, default `runtime/watchdog.json`), `--state` (nudge-history
JSON, default .orca/watchdog-state.json), `--log` (JSONL action log, default
.orca/watchdog.jsonl), `--now` (override the tick timestamp), `--dry-run` (classify
only: print WOULD-nudge/WOULD-recommend, change nothing — the mode for CI and cautious
coordinators).

Classes: `OK` (movement within slow_after_s), `SLOW` (idle past slow_after_s but short of
hung_after_s and STOP — no action), `HUNG` (idle past hung_after_s, or past STOP with no
report — one auto-nudge, then a stop-redispatch recommendation), `WEDGED` (explicit wedge
markers, or transcript frozen past wedge_frozen_s beyond STOP with an unanswered nudge —
immediate recommendation, never nudged). Live mode execs `nudge_command` with argv
placeholders and refuses to run without one configured. Rate limits cap nudges per
dispatch, spacing per worker, and nudges per worker per hour; history persists in the
state file across invocations.

Exits: 0 tick done, nothing needs the coordinator · 1 at least one (WOULD-)recommendation
· 2 could-not-run.

## `wtree.sh`

Prints a working-tree CONTENT fingerprint (a git tree hash). Builds a temp index, stages
the full tree into it, prints `git write-tree` of that index — the real index is never
touched. Source `runtime/scripts/wtree.sh:1-30`; exercised by `tests/test_evidence_run.py`.

Usage: `wtree.sh [repo-dir]` (default: current directory).

Flags: none — one optional positional argument.

Untracked non-ignored files are included; .gitignore'd scratch stays out. Committing
identical content does not change the fingerprint, so a record made on a dirty tree stays
valid once committed; content-preserving rebase/amend/squash does not change it either.
The temp index seeds from a copy of the real one (stat cache preserved, mtime restored
against racy-index reads), falling back to `read-tree HEAD` when the restore fails.
Staged blobs enter the object store as unreachable objects until gc, like `git stash -u`.

Exits: 0 prints the hash · 1 outside a git repo, or no commits and no usable index
(callers fail closed on nonzero — never treat it as an empty fingerprint).

## `one-way-doors.json`

The fleet's one-way door registry: the single enumerated list of human-only decisions —
hard or impossible to reverse, or out of the fleet's authority. Source
`runtime/one-way-doors.json`; enforced by `runtime/scripts/decisions.py`, pointed at by
`runtime/gate-classification.md` and `runtime/sandbox-policy.md`; shape pinned by
`tests/test_one_way_doors.py`.

Top-level keys: `version` (currently 1), `note` (the registry contract), `doors` (the
list). Each door carries `id`, `title`, `why`, and `keywords` — multi-word destructive
phrasings, matched case-insensitively as substrings after whitespace folding, so a single
common word never fires on ordinary prose.

Keys:

| `merge-to-default` | Merge to the default branch (or promote BASE to it) |
| `deploy` | Deploy to a shared or production environment |
| `rollback` | Roll back a deployed release |
| `deletion` | Delete data, branches, worktrees, or infrastructure |
| `spend` | Commit money the fleet does not hold |
| `scope-change` | Change the frozen scope of a run |
| `secret-rotation` | Rotate or revoke a secret |
| `live-credentials` | Use, provision, or move live credentials |
| `freeze` | Freeze or unfreeze the run's contract |

## `watchdog.json`

Liveness-watchdog thresholds and rate limits for `runtime/scripts/watchdog.py`. Every
detection threshold lives here so coordinators tune without code edits; the script
refuses unknown keys, so a typo fails loud instead of silently holding a default. Source
`runtime/watchdog.json`.

Keys:

| `_about` | Provenance: generalized from the 2026-09-14 clean-sweep tracker run |
| `slow_after_s` | 600 — idle past this is SLOW |
| `hung_after_s` | 1800 — idle past this is HUNG |
| `wedge_frozen_s` | 1200 — transcript frozen past this beyond STOP (plus an unanswered nudge) is WEDGED |
| `max_nudges_per_dispatch` | 1 |
| `nudge_window_s` | 3600 — minimum spacing between nudges to one worker |
| `max_nudges_per_hour_per_worker` | 1 |
| `nudge_text` | The auto-nudge message |
| `nudge_command` | null — no transport configured; live mode refuses to run without one |
