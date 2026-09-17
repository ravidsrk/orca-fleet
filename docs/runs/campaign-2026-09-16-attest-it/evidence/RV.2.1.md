# RV.2.1 — Assess, Prioritize, and Remediate Vulnerabilities

- Obligation (frozen NIST-SP-800-218@1.0.0): "Analyze each vulnerability to gather sufficient information about risk to plan its remediation or other risk response."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `playbooks/triage-findings.md:1`: "# Playbook — triage-findings  (candidate findings → VERIFIED, with the noise removed)"
  - `playbooks/triage-findings.md:12`: "- **Gated (default):** report only candidates at high confidence — a concrete exploit path or a"
  - `docs/completion/ISSUES.md:1`: "# ISSUES — S5-C filing ledger (run 3, 2026-09-09)"
- Re-derive: quotes exist at HEAD (rederive.py); each vulnerability is analyzed for exploitability/impact through the triage confidence gate, recorded in the issue tracker with severity labels (sev:S2/S3), and the record carries the remediation plan.
- Residuals: risk scoring is qualitative (severity labels + exploit-path analysis), not a numeric formula.
