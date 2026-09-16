# Axis — Spec fidelity (router: matt)

Spec source: issue #417 Acceptance Criteria AC-1..AC-5 (`criteria.md`). Each
criterion is quoted, then bound to the diff with a quoted line. All paths at
reviewed_sha `c46d4b3f` under `docs/reports/chaining-2026-09-16/` unless noted.

## Criterion binding

**AC-1** — "Chain declaration (sequence + terminal states) posted in-issue
BEFORE the run." SATISFIED. The declaration comment predates the run
(`gh api …/issues/417/comments`: declaration `2026-09-16T05:54:51Z`, unblock
`2026-09-16T09:07:37Z`, run T0 `2026-09-16T09:56Z` per `leg1/ledger.md:3`).
The report quotes and cites it:

> `CHAIN-REPORT.md:25`: `Declared in-issue BEFORE the run (#417 comment 2026-09-16T05:54:51Z), quoted from`

Transcript: `transcripts/declaration.txt`.

**AC-2** — "`docs/reports/chaining-<date>/` published with per-leg manifests +
handoffs." SATISFIED. Directory exists with 3 unit manifests
(`manifest-f3/f5/f6.json`), rollup (`manifest-leg1.json`), and handoff
(`handoff-log.md`). Quoted:

> `CHAIN-REPORT.md:64-65`: `Per-unit manifests: \`leg1/manifest-f3.json\`, \`manifest-f5.json\`,`

**AC-3** — "Terminal-state table complete; any degraded stop published, not
hidden." SATISFIED. Table at `CHAIN-REPORT.md:18-21` names both links with
terminals (NOT-DRY / NOT-STARTED), verification, and carry; §"Why the chain
stopped" publishes both holds. "No degraded terminal was hit"
(`CHAIN-REPORT.md:11`) is consistent: NOT-DRY is review-owed, not one of the
protocol's degraded classes (`-WITH-*`, `NO-GO`, `INCONCLUSIVE`).

**AC-4** — "≥0 follow-up issues filed for protocol gaps." SATISFIED (4 filed,
all OPEN, titles match G1–G4):

> `gaps.md:21`: `Issue: #441`

Verified: #441 promotion lane, #442 verify.py cross-repo, #443 carry shape,
#444 local-target re-derivability. Transcript: `transcripts/followups.txt`.
O1 honestly recorded as NOT filed with the reason stated (`gaps.md:57`).

**AC-4b (explicit zero-gap clause)** — N/A; gaps were found and filed.

**AC-5** — "A second person can re-derive each leg's outcome from the cited
SHAs." MECHANICALLY SATISFIED (see test-adequacy axis for the full
re-derivation record): bundle verifies, all 9 cited SHAs resolve, all 4 wtree
bindings match, `seed-*` bytes are byte-identical to the seed commit, and
`git diff <seed>..<tip> | sha256sum` equals the `full-diff.txt` hash. The
cited "77 lines" is exact (`full-diff.txt` has 77 lines).

No missing/partial criteria, no scope creep (every file serves the report or
AC-5 re-derivability), nothing implemented-but-wrong.

## Findings

### SP-FYI1 (FYI) — AC-5's human-verdict half remains maintainer-owed

> `CHAIN-REPORT.md:80-82`: `Resume: the PR reviewer (human second person) reads \`leg1/full-diff.txt\` (77 lines) and re-derives`

This agent run supplies the mechanical re-derivation; lifting G-REVIEW
(NOT-DRY → DRY) requires the human GO the report names. Not a diff defect —
the report states the resume path correctly.

### SP-FYI2 (FYI) — PR-body merge precondition, checked and clear

The PR body asked "Do NOT merge without maintainer review". The merge record
shows ravidsrk COMMENTED + greptile APPROVED (transcript `pin.txt`). The
precondition says *review*, not *approval* — a maintainer review is on record,
so no violation is found. Process observation only; post-merge, no action.

## Axis verdict

No Critical, no Required. Worst: FYI. (Self-verified — no independent verifier.)
