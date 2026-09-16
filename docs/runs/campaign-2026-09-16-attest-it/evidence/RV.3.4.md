# RV.3.4 — Analyze Vulnerabilities to Identify Their Root Causes

- Obligation (frozen NIST-SP-800-218@1.0.0): "Review the SDLC process, and update it if appropriate to prevent (or reduce the likelihood of) the root cause recurring in updates to the software or in new software that is created."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `CONTRIBUTING.md:101`: "Runtime files encode operational lessons that were paid for in broken runs — wrong-base"
  - `CHANGELOG.md:20`: "What the #308 round changed about the verifier is worth naming, because each was a way a unit"
- Re-derive: quotes exist at HEAD (rederive.py); SDLC updates from root causes are the demonstrated norm: review rounds changed verifier gates, evidence rules, and run contracts (e.g., executed negative controls, signed dispatch inputs, CHANGES_REQUESTED persistence), each landed with tests and changelog entries.
- Residuals: none statement-level.
