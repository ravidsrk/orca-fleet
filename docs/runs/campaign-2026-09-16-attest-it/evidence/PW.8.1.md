# PW.8.1 — Test Executable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements

- Obligation (frozen NIST-SP-800-218@1.0.0): "Determine whether executable code testing should be performed to find vulnerabilities not identified by previous reviews, analysis, or testing and, if so, which types of testing should be used."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `CONTRIBUTING.md:127`: "## Before you open the PR"
  - `CONTRIBUTING.md:140`: "capable of failing."
  - `.github/workflows/validate.yml:23`: "      - name: Run the contract test suite without Gitleaks"
  - `.github/workflows/validate.yml:143`: "      - name: VF-Bench soundness gate (verify.py false-done must be 0)"
- Re-derive: quotes exist at HEAD (rederive.py); the determination is documented: the contract suite is mandatory pre-PR and in CI (CONTRIBUTING: "Neither is optional"), every guard needs a negative-path fixture proving it can fail, plus the adversarial soundness gate (vf-bench) and secret-scan canary as vulnerability-oriented testing.
- Residuals: no fuzz or penetration testing determination (example-level; the attack surface is scripts + docs, tested by contract/adversarial suites instead).
