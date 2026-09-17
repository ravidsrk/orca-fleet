# oncall-it self-test — FREEZE assessment (human gate → PARK)

FREEZE is a human gate: the PATH SET (endpoints, jobs, external dependencies)
plus 2–4 on-call questions per path. The questions ARE the denominator; a path
whose questions the human will not name does not enter the set.

## Outcome: EMPTY path set — nothing to freeze

The target (orca-fleet @ `c46d4b3`) has no production path of the mission's
kind. `instrument.md` defines the unit as "ONE production path — an endpoint,
a job, or an external dependency". The repo contains:

- Markdown doctrine (`skills/`, `playbooks/`, `runtime/*.md`, `docs/`),
- one-shot local CLI tools (`scripts/validate.py`, `runtime/scripts/*.py`,
  `hooks/`),
- contract tests (`tests/`), CI gates (`.github/workflows/`).

None of these receives production traffic, runs on a schedule against users,
or is depended on by an external caller. No 2 a.m. question exists for any of
them that telemetry could answer.

## Substitutes considered and rejected (no substitute qualifies)

1. **CI workflows (`validate`, `negative-control-demo`) as "jobs".**
   Rejected: no queryable metrics backend (no RED/USE series, no histograms,
   no correlation IDs — only GitHub run conclusions); no staging (inducing a
   failure means redding `main`, prohibited — see T-11 transcript); the alert
   destination (issue notifications) is not observable by the fleet (T-11:
   delivery "NOT observed"); the oracle — a source-blind worker naming the
   failing component of an *induced staging failure* from telemetry alone —
   cannot run. A "job" without telemetry, staging, or an observable alert
   channel is not an oncall-it path; instrumenting it would be logging into a
   void with no convergence proof possible.
2. **`alert-on-failure.yml` as a pre-built "alert".** Rejected: it is a CI
   notification (cause-adjacent: "CI failed"), not a symptom alert with two
   severities, an SLO/history-justified threshold, and a runbook link; its
   drill proves issue-filing, not telemetry-answerable on-call questions.
   Counting it would grade done on narration, against the evidence protocol.
3. **`runtime/scripts/watchdog.py` / `pm.py` as "jobs".** Rejected: one-shot
   local coordinator tools with no production traffic, no backend, no staging,
   no alert channel. Same void as (1).
4. **Inventing a demo service to instrument.** Rejected: fabricating a target
   the repo does not ship would be a fabricated run. The campaign instruction
   forbids it explicitly.

## Gate handling

Per `gate-classification.md`, a freeze is one-way / HUMAN ONLY and a fleet
never fakes a human answer; in a headless session the genuinely unanswerable
blocks. Here there is nothing for the human to freeze — the denominator is
empty by the target's own declaration (`docs/ops.md`: no hosted service, no
staging, no deploy target). Filing a questionnaire asking the human to "name
paths" would manufacture work, not unblock any: no answer can conjure a
staging environment or telemetry backend into existence. The honest terminal
is therefore a task-level PARK (mission does not apply), not
OPERABLE-WITH-PARKED (which presupposes ≥1 frozen path with a named blocker).

## Unpark condition (VERIFY-COMPLETE for a future run)

A fresh worker can re-derive applicability with: `test -n "$(find .
-path ./.git -prune -o -type d \( -iname '*staging*' -o -iname
'terraform' -o -iname 'infra*' \) -print)"` AND a telemetry-backend config
present in the tree AND a staging failure inducible without redding `main`.
Today: all three absent.
