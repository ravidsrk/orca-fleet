# RV.1.1 — Identify and Confirm Vulnerabilities on an Ongoing Basis

- Obligation (frozen NIST-SP-800-218@1.0.0): "Gather information from software acquirers, users, and public sources on potential vulnerabilities in the software and third-party components that the software uses, and investigate all credible reports."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `SECURITY.md:7`: "1. Use GitHub's private vulnerability reporting on this repository"
  - `SECURITY.md:12`: "You should receive an acknowledgement within 72 hours. We will confirm"
  - `docs/research/2026-09-10-upstream-audit/orca.md:3`: "# Orca substrate adoption audit — orca-fleet vs stablyai/orca"
  - `docs/completion/ISSUES.md:1`: "# ISSUES — S5-C filing ledger (run 3, 2026-09-09)"
- Re-derive: quotes exist at HEAD (rederive.py); intake channels exist for acquirers/users (private reporting + email with 72h ack SLA), third-party components are evaluated in dated upstream audits, and credible reports are investigated through the issue tracker (review backlogs #255–#338 filed and closed per CHANGELOG).
- Residuals: no automated vulnerability-database feed or composition monitor (see PW.4.4 gap); gathering is channel-based plus periodic audits.
