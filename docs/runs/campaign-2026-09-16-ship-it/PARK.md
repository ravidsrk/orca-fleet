# ship-it self-test — PARKED at entry (no input)

Campaign: `campaign-2026-09-16-ship-it` · mission: `ship-it` · target: orca-fleet itself.
Base: `origin/main` at `c46d4b3f3371e41408aed19e54476fa194c20b42` (branch
`campaign/ship-it-selftest`, no push, no PR, no merge).

## Verdict

**PARKED — missing target.** `ship-it` enters by exactly one of three routes
(`skills/ship-it/SKILL.md`, Pipeline): a frozen spec to validate, raw intent to
grill + freeze, or a map-it handoff to adopt. At the base tip **none of the
three exists**:

| Entry route | Evidence of absence |
|---|---|
| Frozen spec handed in | No spec was supplied with the tasking; repo-wide search for a spec awaiting build finds only mission-guide mentions, no buildable spec doc (`entry-search.txt` §1). |
| Map-it handoff (frozen spec + frozen prepared DAG) | `docs/runs/` holds no MAPPED report and no prepared DAG; search finds none (`entry-search.txt` §2). Re-decomposing is forbidden on this route, and there is nothing to adopt. |
| Raw intent | The tasking names a repo ("orca-fleet itself"), not an intent. No intent, draft, or slice description was supplied. |

## Why no substitute qualifies (no fabricated run)

1. **Inventing an intent is not an entry.** The grill answers every DECISION to
   the human and never answers the human's side; FREEZE (human gate #1) needs an
   EXPLICIT human yes — silence and "looks good" are not a freeze
   (`playbooks/decide-and-freeze.md`). Freeze is one-way / HUMAN ONLY and never
   auto-resolved; in an unattended session the run PARKS
   (`runtime/gate-classification.md`). Self-authoring scope and self-freezing it
   would fake a human answer.
2. **Open tracker issues are clean-sweep's unit, not ship-it's.** `ship-it`
   excludes "closing an existing backlog (clean-sweep)". The 12 open issues at
   the tip (#235, #386, #407–#409, #427, #434, #440–#444) are backlog findings,
   needs-human gates, or other missions' designated targets (deflake-it, pin-it,
   chaining follow-ups). Shipping one as a "slice" would run the wrong mission.
3. **No worker was dispatched and no router mounted**, so the one-router rule is
   trivially satisfied; nothing was built, so no terminal release state
   (BUILT or above) is claimed.

## Preflight (for the record)

Orca 1.4.203 ready/connected, `gh` authed, `scripts/validate.py` green (21/21
missions valid) — see `preflight.txt`. Baseline suite re-run was not needed:
with no input there is no build whose regressions need adjudicating.

## Park class and what unparks it

Allowed park: `needs-human`. This run unparks when a human supplies either (a)
a raw intent to grill (then gate #1 can be answered in-session), or (b) a
frozen spec / map-it handoff to validate. It binds no proof tier: `ship-it`
stays `doctrine-only` per the field-proof plan, whose standing target remains
"the next mutating slice here" (`docs/runs/README.md`).
