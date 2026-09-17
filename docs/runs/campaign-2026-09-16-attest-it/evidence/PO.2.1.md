# PO.2.1 — Implement Roles and Responsibilities

- Obligation (frozen NIST-SP-800-218@1.0.0): "Create new roles and alter responsibilities for existing roles as needed to encompass all parts of the SDLC. Periodically review and maintain the defined roles and responsibilities, updating them as needed."
- Verdict: GAP
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Searched (all absent at HEAD):
  - Absent: `**/CODEOWNERS`
  - Absent: `**/*roles*responsibilit*`
  - NoMatch: `CONTRIBUTING.md` :: `(?i)role-based|roles and responsibilities|security champion`
  - NoMatch: `AGENTS.md` :: `(?i)roles and responsibilities|security champion`
- Context (what exists, and why it does not satisfy): `docs/ops.md:3` names the single maintainer ("Bus factor 1: Ravindra Kumar ...") — an inventory of one, not SDLC roles covering development, testing, assurance, and release with periodic review.
  - `docs/ops.md:3`: "Bus factor 1: Ravindra Kumar ([`ravidsrk`](https://github.com/ravidsrk),"
- Missing evidence: a written SDLC roles/responsibilities record (roles, who holds them, review cadence).
- Owner: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Handoff: gaps/PO.2.1.md (verify-complete: file exists at a stable path and names SDLC roles + holders + review date).
