# Scope: journeys + budgets (mission inputs)

The mission inputs for this fixture: the user journeys missions execute
against, and the budgets they are judged by. Budgets live HERE, not in CI —
per the run's `perf-guard-lane` decision, a 30s guard at today's suite cost
would red main, so budgets are mission inputs, never CI gates.

Out of scope for the fixture itself: auth/users, real PostgreSQL,
mobile/emulator packaging (BROWSER tier only), production deploy, real pager
routing, and fixing F1–F4 (SPEC Boundaries + `FLAWS.md`).

## Journeys

- J1 file-and-track (reporter): open `/issues/new` → submit title/body/
  priority → issue appears in `/` list → `POST /issues/{id}/comments` →
  close via `/issues/{id}/edit` → detail view shows closed + comment.
  (prove-it / field-test-it input)
- J2 triage-at-scale (maintainer): seed 1k issues (`python -m app.seed
  --count 1000`) → `GET /issues` returns all 1000 with
  `X-Total-Comments: 50000`. (speed-it input; latency budgeted under B1,
  currently over — F1)
- J3 observe (oncall): scrape `/metrics` (request-latency histogram,
  `app_issues_total` gauge) → find the request's JSON log line in Loki →
  fire a test alert at Alertmanager → receipt visible at
  `/hooks/alerts/last`. (oncall-it input)
- J4 migrate (release): copy a booted DB → apply pending `0003` →
  `alembic current` reads `0003` → `downgrade -1` back to `0002`, data
  intact. (migrate-it input; the apply step is the mission, F3)
- J5 keyboard/screen-reader pass (a11y): tab through the new-issue form;
  every control announces its name. (access-it input; priority select
  currently fails — F2)

## Budgets (targets, not gates)

- B1: `GET /issues` p95 < 500ms at 1k issues x 50 comments
  (current ~900ms — F1; the speed-it target).
- B2: UI pages (`/`, `/issues/new`, `/issues/{id}/view`) p95 < 200ms
  uncached at 1k rows.
- B3: `uv run pytest` < 60s cold (current ~1s; the deflake-it ceiling).
- B4: compose smoke (build + health + PromQL + LogQL + teardown) < 15 min
  on CI runners.

A mission run measures against these budgets and parks what it cannot
measure; it does not add them as fixture CI gates.
