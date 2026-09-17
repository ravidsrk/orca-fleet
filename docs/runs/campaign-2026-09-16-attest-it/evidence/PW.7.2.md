# PW.7.2 — Review and/or Analyze Human-Readable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements

- Obligation (frozen NIST-SP-800-218@1.0.0): "Perform the code review and/or code analysis based on the organization’s secure coding standards, and record and triage all discovered issues and recommended remediations in the development team’s workflow or issue tracking system."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.github/workflows/validate.yml:104`: "          "$gl" detect --redact --no-banner --source ."
  - `.github/workflows/validate.yml:117`: "          echo "negative control: a planted credential in the waived file is still caught""
  - `playbooks/acceptance-review.md:61`: "Pinned fixed point (non-empty `git diff <fp>...HEAD`), ALL THREE axes reported with no cross-rerank,"
  - `playbooks/triage-findings.md:12`: "- **Gated (default):** report only candidates at high confidence — a concrete exploit path or a"
  - `docs/completion/ISSUES.md:1`: "# ISSUES — S5-C filing ledger (run 3, 2026-09-09)"
- Re-derive: quotes exist at HEAD (rederive.py); analysis runs on every PR with a canary negative control; human review follows the three-axis process with recorded reviewed_sha; discovered issues are recorded and triaged in the GitHub tracker plus the completion register (96 issues fetched/deduped per ISSUES.md).
- Residuals: none statement-level.
