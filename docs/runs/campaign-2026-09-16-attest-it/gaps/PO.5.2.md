# Gap handoff — PO.5.2 (development endpoint hardening)

- Obligation: NIST-SP-800-218@1.0.0 PO.5.2 — "Secure and harden development endpoints (i.e., endpoints for software designers, developers, testers, builders, etc.) to perform development-related tasks using a risk-based approach."
- Missing evidence: a development-endpoint hardening baseline applied to each endpoint. Searched at 6390743: no hardening/MDM/endpoint record anywhere.
- Recipient: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Ask (Task item): write and commit an endpoint baseline (suggested path: docs/endpoints.md): the approved hardening configuration (encryption, least-functionality software set, MFA, monitoring), and one row per development endpoint recording its compliance state and check date. Do not paste secrets, serials, or other sensitive identifiers — record posture ("FileVault on, checked YYYY-MM-DD"), not credentials.
- Verify-complete: the baseline exists, each dev endpoint is recorded against it with a check date, and the PO.5.2 re-derivation check for its quotes passes.
- Run ref: evidence/PO.5.2.md. Park class: needs-human.
