# PW.8.2 — Test Executable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements

- Obligation (frozen NIST-SP-800-218@1.0.0): "Scope the testing, design the tests, perform the testing, and document the results, including recording and triaging all discovered issues and recommended remediations in the development team’s workflow or issue tracking system."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim — HEAD files, plus this run's executed receipt):
  - `RUN:receipts/suite-2026-09-16.log:26`: "Ran 1490 tests in 254.407s"
  - `RUN:receipts/suite-2026-09-16.log:28`: "OK"
  - `.github/workflows/validate.yml:23`: "      - name: Run the contract test suite without Gitleaks"
  - `CONTRIBUTING.md:140`: "capable of failing."
  - `docs/completion/ISSUES.md:1`: "# ISSUES — S5-C filing ledger (run 3, 2026-09-09)"
- Re-derive: HEAD quotes via rederive.py; RUN: lines checked against the run's own receipt bytes (sha256-pinned in the manifest); testing is performed in CI on every PR and was executed in this run (1490 tests, exit 0); discovered issues are recorded/triaged in the tracker + completion register.
- Residuals: none statement-level.
