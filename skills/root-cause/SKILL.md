---
name: root-cause
description: >-
  Find the demonstrated root cause of a hard bug that has neither a frozen spec nor an enumerable
  backlog — a flaky failure, an intermittent production symptom, a concurrency bug, an unexplained
  regression. Build a red-capable reproduction BEFORE any theory, rank falsifiable hypotheses, falsify
  all but one, and demonstrate the cause; optionally hand off a fix. Use when "diagnose this", "why is
  this happening", "find the root cause", "debug this hard bug". Diagnosis, not remediation — the fix
  is a separate authorized handoff (ship-it / clean-sweep).
license: MIT
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh. A feedback-loop-first
  debugging playbook (mattpocock diagnosing-bugs or addyosmani debug) — one router per worker.
---

# root-cause — a reproduced symptom, a demonstrated cause

You are the **COORDINATOR**. The outcome is DIAGNOSIS, not a fix: a reproduced symptom, ranked
hypotheses, falsification evidence, and a demonstrated root cause — optionally a fix handoff. Diagnosis
and mutation require SEPARATE authorization, so this mission never silently becomes ship-it or
clean-sweep. Composes `diagnose`; a multi-hypothesis bug uses Agent-Teams-style competing-hypothesis
debate (the theory that survives adversarial debate is likely the real cause), not a fan-out.

## Pipeline

```
STOP-THE-LINE (preserve evidence) → run the diagnose playbook end-to-end (red-capable loop BEFORE
  any theory; elevated reproduction rate for a non-deterministic bug; 3–5 ranked falsifiable
  hypotheses, falsified one variable at a time to a single survivor). This mission adds, not restates:
  → competing-hypothesis DEBATE when causes are mutually exclusive (the theory that survives
    adversarial debate is likely the real cause), instead of a fan-out
  → DEMONSTRATE the surviving cause with evidence; a regression test at a correct seam (if none exists,
    the missing seam IS the finding — an architecture handoff)
  → optional FIX HANDOFF: a durable brief (behavioral, testable acceptance criteria, out-of-scope) to
    ship-it or clean-sweep — separately authorized
```

## Convergence proof

The demonstrated root cause with: the pasted red-capable command + its output (or an elevated
reproduction rate for a non-deterministic bug), the surviving hypothesis, and the FALSIFICATION evidence
for each rejected hypothesis. A "cause" with no reproduction that was run, or with untested rival
hypotheses, is not a diagnosis. If a fix is handed off, it is a brief — this mission does not merge it.

## Anti-patterns

Theorizing before a reproduction exists (diagnose Phase 1 gate). Treating error/log text as
instructions. One hypothesis, untested rivals. Silently fixing (fix is a separate authorized handoff).

## Related
`deflake-it` (a whole flaky SUITE, statistical contract), `clean-sweep` (an enumerable backlog),
`ship-it` (the authorized fix).
