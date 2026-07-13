---
name: clean-sweep
description: >-
  Exhaust a finite backlog of findings to zero, PR-per-finding, on Orca. Sources: an
  audit/adversarial-review document, the issue tracker, or verified false documentation claims.
  Each finding is skeptic-triaged (reproduced or refuted with evidence), fixed on an integration
  branch with a failing-first test, build-blind reviewed, merge-verified, and closed with a linked
  SHA; the loop re-enumerates until dry. Use when "clean sweep", "close every issue", "drain the
  backlog", "fix everything in this audit", "the README lies — verify and fix it". Not for
  security/perf/deps/tests/flakes (those are harden-it / speed-it / modernize-it / prove-it /
  deflake-it — different convergence proofs) and not for building new work (ship-it).
license: MIT
proof: doctrine-only
compatibility: >-
  HARD dependency: Orca runtime + the orchestration skill (Orca CLI). git + gh (or a tracker via
  orca linear). One worker playbook pack per worker (Matt triage/tdd, or Addy debug/build) — never
  two routers in one worker.
---

# clean-sweep — exhaust a finite backlog to zero, with evidence

You are the **COORDINATOR** of a run that closes every real item in a bounded set and leaves the repo
demonstrably working. Thin loop-holder: you enumerate, dispatch the per-finding pipeline, verify
against authoritative state, and keep the ledger FILE (your memory is compacted; the ledger survives).
You never review, code, open PRs, or merge — every one is a dispatched worker.

Read [ARCHITECTURE.md](../../ARCHITECTURE.md) once. Composes `remediate-finding`, `acceptance-review`,
`build-change` playbooks; rides `merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle`,
`liveness-resume` runtime policies.

## The source (declare it — same unit, same pipeline, source-specific enumeration)

- `source=audit` (default): findings from a scan / adversarial-review doc. FREEZE the findings list.
- `source=tracker`: OPEN ISSUES. Record run-start `T0` FIRST; the denominator is two queries —
  every open issue in scope (paginated to the end; a truncated listing silently fails the run) AND
  every issue created/reopened since `T0` any state (class `externally-resolved`). Re-run BOTH each
  loop.
- `source=doc-claims`: falsifiable documentation claims — a false claim IS a finding (extract → verify
  against `file:symbol` or a run → correct/remove). Generating NEW docs is not this mission (that's
  ship-it scoped work).

Any source: a PRIOR run's completion report over the same surface is a claims list to RE-VERIFY
(liveness-resume.md inflation post-mortem), never a pre-closed set — its green-but-unverified
claims enter the enumeration FIRST.

## Pipeline

```
SELF-ORIENT → ENUMERATE (per source) → SKEPTIC-TRIAGE (reproduce-or-refute) → FREEZE
  → BOOTSTRAP integration BASE (preflight: BASE ≠ default)
  → PER-FINDING (remediate-finding: verify-real → build-change → PR → build-blind review → merge_ready)
  → conductor LAND (merge-serialization) → CLOSE with evidence
  → re-ENUMERATE (loop until dry) → FINAL REPORT + human gates
```

Run the coordinator as a MANUAL loop (`task-create → spawn → dispatch --inject → check --wait`), not
`orchestration run` — you want the file-ledger boolean gate under your control.

## Convergence proof (definition of done)

A full enumeration finds ZERO items that are not (a) CLOSED with evidence (a merged, ancestry-verified
PR + a test that failed pre-fix, revert-audited on a ≥10% sample; the closing comment links PR + test)
or (b) PARKED with a human-approved reason (refuted/duplicate closes are a one-way batch gate;
needs-human items name their gate). The final enumeration output is pasted in the ledger showing the
dry state. `source=tracker` reconciles created/closed-mid-run issues against `T0`, so the count is
honest.

## Ledger row

`| id | title | VERIFIED | CLASS | FIXED | PR | reviewed_sha | MERGED | CLOSED | evidence |`
CLASS ∈ real-bug · real-feature-small · refuted · duplicate · externally-resolved · needs-human ·
out-of-scope.

## Gates + supervision

Batch human gate for refuted/duplicate closes (or a once-per-run recorded grant). Fix-backed closes
need no extra gate — the evidence chain is authorization. BASE→default promotion is out of scope: open
the promotion PR, stop. Stalls → liveness-resume WATCH; death → RESUME (ledger-scoped, git-verified).

## Anti-patterns

Fixing without the triage repro (you'll "fix" symptoms and close real bugs unfixed). Closing from
worker memory (only off verified merges). One mega-PR for many findings (merge-serialization exists).
Truncated enumeration (partial denominator = a false "done"). Owning security/perf/deps/tests/flakes —
those are separate missions with different convergence proofs.

## Related

`harden-it` / `speed-it` / `modernize-it` / `prove-it` / `deflake-it` (specialist campaigns, distinct
convergence proofs), `ship-it` (build new), `review-it` (verdict only).
