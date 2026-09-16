# RV.1.2 — Identify and Confirm Vulnerabilities on an Ongoing Basis

- Obligation (frozen NIST-SP-800-218@1.0.0): "Review, analyze, and/or test the software’s code to identify or confirm the presence of previously undetected vulnerabilities."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.github/workflows/validate.yml:4`: "  pull_request:"
  - `.github/workflows/validate.yml:143`: "      - name: VF-Bench soundness gate (verify.py false-done must be 0)"
  - `docs/reviews/2026-09-10-review.md:29`: "mutation unit. Six of ten manifest-gaming attacks landed. The claim that holds is narrower:"
- Re-derive: quotes exist at HEAD (rederive.py); the toolchain performs automated analysis + testing on every PR (continuous basis), the adversarial soundness gate probes for false-done verdicts, and independent attack reviews (2026-09-10, 2026-09-11, 2026-09-14) confirmed previously undetected vulnerabilities that were then fixed.
- Residuals: none statement-level.
