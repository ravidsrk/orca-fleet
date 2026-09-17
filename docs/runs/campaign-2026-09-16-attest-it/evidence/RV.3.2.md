# RV.3.2 — Analyze Vulnerabilities to Identify Their Root Causes

- Obligation (frozen NIST-SP-800-218@1.0.0): "Analyze the root causes over time to identify patterns, such as a particular secure coding practice not being followed consistently."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `CONTRIBUTING.md:101`: "Runtime files encode operational lessons that were paid for in broken runs — wrong-base"
  - `CHANGELOG.md:20`: "What the #308 round changed about the verifier is worth naming, because each was a way a unit"
  - `runtime/evidence-manifest.md:140`: "Verification failing on any required check → NOT done; re-dispatch, or SUSPECT if provenance says done but git disagrees."
- Re-derive: quotes exist at HEAD (rederive.py); the pattern is institutional: paid-for lessons become runtime policy and toolchain guards (validator checks, contract tests, vf-bench traps keyed to issue numbers), so each root-cause class gains automatic detection of future instances.
- Residuals: lessons live in policy/test code and the changelog rather than a separate wiki page (same content, different shelf).
