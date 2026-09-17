# Frozen contract — review-it self-test 2026-09-16 (unit R1)

Source: `ravidsrk/orca-fleet` issue #417, "Acceptance Criteria" section,
frozen here verbatim as the spec denominator for this review. First hit in
the acceptance-review spec-source search order (no frozen unit spec; the
originating issue carries explicit criteria; PR #445 body corroborates).

## Criteria

- AC-1: Chain declaration (sequence + terminal states) posted in-issue BEFORE the run.
- AC-2: `docs/reports/chaining-<date>/` published with per-leg manifests + handoffs.
- AC-3: Terminal-state table complete; any degraded stop published, not hidden.
- AC-4: ≥0 follow-up issues filed for protocol gaps (zero is allowed only if the
  run genuinely hit none — say so explicitly).
- AC-5: A second person can re-derive each leg's outcome from the cited SHAs.

## Corroborating refs (NOTE-only, not the denominator)

- PR #445 body: report contents, resume path for the reviewer, follow-ups
  #441–#444, "validate.py green (21 missions); unittest 1490 OK".
- `runtime/mission-chaining.md`: report-shape expectations quoted by the run.
