# PW.7.1 — Review and/or Analyze Human-Readable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements

- Obligation (frozen NIST-SP-800-218@1.0.0): "Determine whether code review (a person looks directly at the code to find issues) and/or code analysis (tools are used to find issues in code, either in a fully automated way or in conjunction with a person) should be used, as defined by the organization."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `CONTRIBUTING.md:127`: "## Before you open the PR"
  - `playbooks/acceptance-review.md:3`: "Recipe: Matt `code-review` two-axis (isolated) + gstack review-army dispatch mechanics. Always-on for"
  - `.github/workflows/validate.yml:72`: "      - name: Secret scan (gitleaks, pinned)"
  - `.github/workflows/validate.yml:118`: "      - name: Ruff (syntax / undefined names)"
- Re-derive: quotes exist at HEAD (rederive.py); the determination is documented: human review (build-blind, always-on for non-trivial diffs) plus automated analysis (secret scan, ruff, validator) on every PR.
- Residuals: none statement-level.
