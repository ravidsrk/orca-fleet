# Frozen flaws F1–F4 (fixture imperfection set)

These four flaws are DELIBERATE, FROZEN true signal for finding-missions.
Each states its oracle, and each carries the same rule (SPEC AC4.5):

> **Fix a flaw ONLY inside a mission run — never as drive-by fixture work.**
> A fixture PR that "fixes" F1–F4 destroys a mission's target.

## F1 — issue-list N+1, >500ms at 1k rows (speed-it signal)

`GET /issues` (`app/routers/issues.py::list_issues`) fans out per row: one ids
query, then per issue one issue fetch plus one comments fetch — >= 2N+1
SELECTs for N rows, pinned by
`tests/test_telemetry_seed.py::test_list_issues_is_n_plus_one`. JSON shape is
the straightforward read; the fan-out hides behind the `X-Total-Comments`
header.

Oracle (timing harness; verbatim from the `app/seed.py` docstring):

1. `cd demo/target-app`
2. `rm -f /tmp/f1.db && DATABASE_URL=sqlite:////tmp/f1.db uv run python -m app.seed --count 1000`
3. `DATABASE_URL=sqlite:////tmp/f1.db uv run uvicorn app.main:app --port 8123 & sleep 3`
4. `time curl -s http://127.0.0.1:8123/issues -o /tmp/f1-issues.json`
5. `kill %1`

Measured: 878–902ms across 3 runs at S3 head (1000 issues, 135071 bytes);
re-verified at S4 head: 0.99s, 1.02s, 1.05s across 3 runs (1000 issues,
135071 bytes, X-Total-Comments 50000; server-side durations 1002–1044ms). If the machine outruns the flaw, raise
`--count`: time grows linearly with rows — that linearity IS the N+1 signal.

F1/F3 coupling: F1's wall time rides on the missing F3 index — every per-row
comments fetch is a full SCAN until 0003 lands. Applying 0003 will shrink the
wall time but NOT the statement count (still 2N+1): the SELECT-count shape
test is the stable N+1 signal, wall clock is the measured witness.

## F2 — priority `<select>` has no associated `<label>` (access-it signal)

`app/templates/_form.html` (shared new/edit form): the priority `<select>`
sits beside a bare `<span>Priority</span>` — no `<label for="priority">`.
(The status `<select>` right above it HAS a label; the contrast is the tell.)

Oracle: axe-core rule `label` fires on `/issues/new` and
`/issues/{id}/edit`. Per the SPEC seams there is no browser driver in fixture
CI — axe/Playwright arrive with access-it runs, which execute against this
frozen DOM.

## F3 — migration 0003 generated but UNAPPLIED (migrate-it signal)

`alembic/versions/0003_add_comments_issue_id_index.py` exists on disk and
adds `ix_comments_issue_id` on `comments(issue_id)` — the index F1's wall
time is waiting for. It is NOT applied at freeze. The exact mechanism:

- Single-head linear chain on disk: `0001 -> 0002 -> 0003`
  (`down_revision = "0002"`); `uv run alembic heads` shows `0003 (head)`.
- Fixture boot pins the upgrade target: `app/seed.py::ensure_migrated` runs
  `alembic upgrade "0002"` (not `"head"`). Both boot paths share it —
  `python -m app.seed` (incl. the F1 oracle seed) and `docker compose up`
  (whose command runs `python -m app.seed --count 0`).
- So `uv run alembic current` on a booted DB reads `0002` while heads show
  `0003`: pending, provably. CI's migrate job asserts exactly this, plus a
  downgrade/re-upgrade round-trip and a scratch-DB validity check of the
  0003 file itself.

Applying 0003 (and proving the F1 wall-time delta) is a migrate-it mission
run, not fixture work.

## F4 — README claims PostgreSQL support (clean-sweep signal)

The README's Database section says PostgreSQL works: "point `DATABASE_URL`
at your Postgres DSN and the app connects as-is". It does not — only SQLite
is wired:

- `pyproject.toml` has no Postgres driver (no `psycopg`/`psycopg2`), so a
  `postgresql://` URL dies at `create_engine` with `ModuleNotFoundError`.
- `app/models.py` passes `connect_args={"check_same_thread": False}`
  unconditionally — a SQLite-only argument.
- `alembic.ini` and `compose.yaml` hardcode `sqlite:` URLs.

Oracle: clean-sweep doc-claim check — README sentence vs. wiring above. The
claim is planted deliberately; correcting it (or wiring real Postgres) is
mission work.
