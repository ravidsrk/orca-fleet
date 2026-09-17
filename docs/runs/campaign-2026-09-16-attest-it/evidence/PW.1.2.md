# PW.1.2 — Design Software to Meet Security Requirements and Mitigate Security Risks

- Obligation (frozen NIST-SP-800-218@1.0.0): "Track and maintain the software’s security requirements, risks, and design decisions."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `docs/DECISIONS.md:1`: "# DECISIONS — durable auto-resolves (`ts · gate-or-ask-id · class · answer · why · task_id?`)"
  - `docs/completion/ISSUES.md:1`: "# ISSUES — S5-C filing ledger (run 3, 2026-09-09)"
  - `docs/ops.md:170`: "## Incident (2 a.m.)"
- Re-derive: quotes exist at HEAD (rederive.py); design decisions accumulate in docs/DECISIONS.md (durable, timestamped, RESUME-read), risks/issues in the tracker + completion register, incident responses in docs/ops.md — all versioned in git for the software life cycle.
- Residuals: approved-exception records with periodic re-evaluation dates are implicit (DECISIONS lines carry timestamps) rather than a dedicated exception register.
