# PO.5.2 — Implement and Maintain Secure Environments for Software Development

- Obligation (frozen NIST-SP-800-218@1.0.0): "Secure and harden development endpoints (i.e., endpoints for software designers, developers, testers, builders, etc.) to perform development-related tasks using a risk-based approach."
- Verdict: GAP
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Searched (all absent at HEAD):
  - NoMatch: `docs/ops.md` :: `(?i)harden|FIPS|endpoint|device.{0,20}policy|disk encryption`
  - NoMatch: `CONTRIBUTING.md` :: `(?i)harden|FIPS|endpoint`
  - Absent: `**/*hardening*`
  - Absent: `**/*mdm*`
- Context (what exists, and why it does not satisfy): development happens on the maintainer's machine and hosted CI runners, but no endpoint-hardening baseline, least-functionality build, monitoring, or MFA posture is documented for any development endpoint.
  - `docs/ops.md:3`: "Bus factor 1: Ravindra Kumar ([`ravidsrk`](https://github.com/ravidsrk),"
- Missing evidence: a development-endpoint hardening baseline (approved config, least functionality, monitoring) applied to each endpoint.
- Owner: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Handoff: gaps/PO.5.2.md (verify-complete: endpoint baseline exists and each dev endpoint is recorded against it).
