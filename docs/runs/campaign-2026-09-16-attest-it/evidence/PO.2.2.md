# PO.2.2 — Implement Roles and Responsibilities

- Obligation (frozen NIST-SP-800-218@1.0.0): "Provide role-based training for all personnel with responsibilities that contribute to secure development. Periodically review personnel proficiency and role-based training, and update the training as needed."
- Verdict: GAP
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Searched (all absent at HEAD):
  - Absent: `**/*training*`
  - Absent: `**/*onboarding*`
  - Absent: `**/*curriculum*`
  - NoMatch: `CONTRIBUTING.md` :: `(?i)training plan|training curriculum|role-based training`
  - NoMatch: `AGENTS.md` :: `(?i)training plan|training curriculum|role-based training`
- Context (what exists, and why it does not satisfy): contributor guidance exists (CONTRIBUTING.md, AGENTS.md) but no role-based training plan, curriculum, proficiency review, or outcome measurement exists for any role.
- Missing evidence: a training plan per role (outcomes, curriculum, proficiency review).
- Owner: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Handoff: gaps/PO.2.2.md (verify-complete: training plan exists at a stable path naming roles, curricula, and last review date).
