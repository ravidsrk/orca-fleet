# RV.3.3 — Analyze Vulnerabilities to Identify Their Root Causes

- Obligation (frozen NIST-SP-800-218@1.0.0): "Review the software for similar vulnerabilities to eradicate a class of vulnerabilities, and proactively fix them rather than waiting for external reports."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `skills/harden-it/SKILL.md:4`: "  Establish a threat model and close it: audit → prove exploits → fix → RE-ATTACK the fix and"
  - `CHANGELOG.md:20`: "What the #308 round changed about the verifier is worth naming, because each was a way a unit"
  - `docs/reviews/2026-09-10-review.md:14`: "dated re-measurement** at `9afefc6` — the same attacks and the same routing matrix, re-run against"
  - `.github/workflows/validate.yml:143`: "      - name: VF-Bench soundness gate (verify.py false-done must be 0)"
- Re-derive: quotes exist at HEAD (rederive.py); class eradication is executed, not just documented: the 2026-09-10 attack class (worker-chosen proof oracles) was fixed across all lanes and re-measured (§10), and the vf-bench trap corpus plus the ≥10% sampling-audit floor keep sweeping for recurrences.
- Residuals: none statement-level.
