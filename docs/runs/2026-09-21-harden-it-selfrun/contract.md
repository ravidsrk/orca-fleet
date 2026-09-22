# h409 run-close contract — FROZEN 2026-09-22

Unit: the harden-it 2026-09-21 run-close evidence bundle for issue #409 (report-only — the code
changes were each graded on their own merge trains; this unit grades the run's terminal evidence).

- RC-1: the final re-audit at the merged tip reports CLEAN — zero unrefuted P0/P1 across the six
  threat-model axes (docs/reports/h409/reaudit-r2.md).
- RC-2: the final re-attack re-derives every prior attack as REFUSED with no new sound-lane
  false GREEN (docs/reports/h409/reattack-r3.md).
- RC-3: every confirmed finding (F-1..F-6, R1, C-1, C-2, the /bin-symlink-node hole) carries an
  independent review verdict and a real-CLI runtime-prove record on its merge train
  (docs/reports/h409/review-*.txt, docs/reports/h409/runtime-prove*.txt).
- RC-4: the gitleaks negative-control unit is recorded — repo scan GREEN, planted secret RED,
  cleaned scan GREEN (docs/runs/2026-09-21-harden-409.md loop log).
