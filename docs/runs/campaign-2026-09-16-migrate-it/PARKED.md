# migrate-it self-test (campaign 2026-09-16) — PARKED: no migration target exists

RUN: migrate-it selftest · COORDINATOR · BASE c46d4b3f3371e41408aed19e54476fa194c20b42
(target = orca-fleet itself at origin/main tip) · T0 2026-09-16 · branch campaign/migrate-it-selftest

## Verdict: PARKED — the mission genuinely does not apply to this repo

`migrate-it`'s unit is "one migration PHASE of one table or shape" and its PLAN step
freezes the TABLE SET "from the surface the code actually reads — a table nobody reads
is not in the set". orca-fleet is a doctrine repo (missions/playbooks/runtime Markdown
plus stateless Python/shell tooling); its code reads **zero tables**. The frozen table
set is empty, so there is no phase ladder to run. Per the mission's own anti-patterns,
fabricating a run against a non-target would be narration graded as done.

## Compatibility checklist (from the skill's `compatibility` field, verbatim needs)

| Need | State in orca-fleet @ c46d4b3 | Evidence |
|---|---|---|
| The project's own migration runner | ABSENT — no `migrations/`, `db/migrate/`, `alembic/`, `prisma/migrations/` dir; none ever in git history | `git log --all --diff-filter=A -- migrations/* db/* alembic/*` → empty; `find -iname '*migration*'` → only `tests/test_migration_walkthrough.py`, `playbooks/data-migration.md` (doctrine, not a runner), one JSON receipt mentioning "contract-migration" |
| A database the fleet can migrate and dump | ABSENT — no `*.db`/`*.sqlite*` files; zero `sqlite3.connect`/`CREATE TABLE`/`ALTER TABLE` in `runtime/`, `scripts/`, `hooks/`, `bench/`, `demo/` | search returned 0 matches |
| Deploy path per phase | N/A — nothing stateful to deploy phases of | — |
| Read/write telemetry for the zero-reader window | N/A — no readers or writers of any old shape exist | — |

## Why no substitute qualifies

1. **`tests/eval_workspaces.json` sqlite snippets** (routing-eval fixtures naming
   `mission: migrate-it`) — synthetic workspace *text* used to test mission routing,
   not a real database: no readers, no writers, no deploys, no dump oracle. Migrating
   fixture strings would be a fabricated run.
2. **`docs/missions/migrate-it.md` SQLite walkthrough** — the mission's own executable
   in-memory demo, exercised by `tests/test_migration_walkthrough.py`. It is the
   doctrine's illustration, not a production shape with old/new code validity across
   deploys; "migrating" it proves nothing about the mission.
3. **Orca provenance DB** (named in ARCHITECTURE.md as recording fleet lifecycle) —
   owned by the external Orca runtime control plane, not by this repo; the fleet
   cannot migrate or dump it. Out of scope by the compatibility clause.
4. **Git-tracked JSON/ledger files** — plain files, not a stateful schema. There is no
   dual-write/backfill semantic, no old/new code validity window, and no reader/writer
   telemetry over them; forcing the phase ladder onto file edits would violate the
   mission-identity test (different oracle, different convergence proof).

## Pipeline position

SELF-ORIENT → PLAN reached; table set frozen at ∅; run parked before BOOTSTRAP
(no BASE integration to run — nothing to migrate). No phases dispatched, no PRs, no
deploys. Mission `proof:` stays `doctrine-only`; this park does not advance it.

## Reproduction

At `c46d4b3`: `find . -name '*.db' -o -name '*.sqlite*'` → empty;
`rg 'sqlite3\.connect|CREATE TABLE|ALTER TABLE' runtime scripts hooks bench demo` → no matches;
`git log --oneline --all --diff-filter=A -- 'migrations/*' 'db/*' 'alembic/*'` → empty.
