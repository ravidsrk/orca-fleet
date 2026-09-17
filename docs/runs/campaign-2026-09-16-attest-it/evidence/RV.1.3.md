# RV.1.3 — Identify and Confirm Vulnerabilities on an Ongoing Basis

- Obligation (frozen NIST-SP-800-218@1.0.0): "Have a policy that addresses vulnerability disclosure and remediation, and implement the roles, responsibilities, and processes needed to support that policy."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `SECURITY.md:5`: "Please **do not** open a public GitHub issue for a security report."
  - `SECURITY.md:12`: "You should receive an acknowledgement within 72 hours. We will confirm"
  - `docs/ops.md:170`: "## Incident (2 a.m.)"
  - `docs/ops.md:203`: "   Rehearsed on a scratch clone: 2026-09-01"
- Re-derive: quotes exist at HEAD (rederive.py); the disclosure policy (SECURITY.md: channels, scope, ack SLA) plus the incident/rollback processes (ops.md) with rehearsal transcripts implement the roles (named maintainer), responsibilities, and processes.
- Residuals: no formal PSIRT — proportionate to a bus-factor-1 project, with the maintainer as the response role.
