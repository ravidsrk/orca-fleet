# RV.3.1 — Analyze Vulnerabilities to Identify Their Root Causes

- Obligation (frozen NIST-SP-800-218@1.0.0): "Analyze identified vulnerabilities to determine their root causes."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `skills/root-cause/SKILL.md:19`: "  unit: one falsifiable hypothesis about one bug"
  - `CHANGELOG.md:20`: "What the #308 round changed about the verifier is worth naming, because each was a way a unit"
- Re-derive: quotes exist at HEAD (rederive.py); the root-cause mission (red-capable repro → ranked hypotheses → falsification → demonstrated cause) is the standing process, and review rounds record root causes (e.g., the #308 round's "graded against a proof it chose" class analysis) in the changelog and tracker.
- Residuals: none statement-level.
