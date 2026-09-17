# Lens-tally record — run-local equivalent of `docs/DECISIONS.md` lines

Per `risk-review`, every lens dispatch appends one DECISIONS line
(`lens-tally:<lens>`, class `mechanical`, finding count as answer).
`docs/DECISIONS.md` carries zero `lens-tally:` lines at the fixed point, so
no lens had an auto-gate streak entering this run.

DEVIATION (recorded, not hidden): the tally lines below were NOT appended to
`docs/DECISIONS.md`, because review-it is report-only and modifying repo
state outside the run's own evidence directory would break the permission
boundary the verdict certifies. They are recorded here with identical shape
so a future coordinator can adopt them.

- id=`lens-tally:security` class=`mechanical` answer=`0 findings (CLEAN, bounded run)` run=`campaign-2026-09-16-review-it`
- id=`lens-tally:privacy` class=`mechanical` answer=`0 findings (CLEAN)` run=`campaign-2026-09-16-review-it`
- id=`lens-tally:data-migration` class=`mechanical` answer=`0 findings (N/A, no surface)` run=`campaign-2026-09-16-review-it`
- id=`lens-tally:perf` class=`mechanical` answer=`0 findings (CLEAN, bounded run on keyword flag)` run=`campaign-2026-09-16-review-it`
- id=`lens-gate:api-contract` class=`mechanical` answer=`gate-off: no public route/interface change (script API=false)` run=`campaign-2026-09-16-review-it`
- id=`lens-gate:a11y` class=`mechanical` answer=`gate-off: prose only, no component/markup (script A11Y=false)` run=`campaign-2026-09-16-review-it`
- id=`lens-tally:simplification` class=`mechanical` answer=`0 advisory findings` run=`campaign-2026-09-16-review-it`
