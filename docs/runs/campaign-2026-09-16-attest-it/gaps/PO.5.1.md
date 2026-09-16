# Gap handoff — PO.5.1 (secure development environments)

- Obligation: NIST-SP-800-218@1.0.0 PO.5.1 — "Separate and protect each environment involved in software development."
- Missing evidence: an environment inventory with separation/protection controls per environment (auth, segmentation, logging/monitoring). Searched at 6390743: no MFA/zero-trust/segmentation/monitoring posture in docs/ops.md, runtime/sandbox-policy.md, or CI config.
- Recipient: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Ask (Task item): write and commit an environment record (suggested path: docs/environments.md) listing each environment involved in development (maintainer workstation, GitHub Actions runners, ephemeral danger sandboxes, any others) with, per environment: authentication controls, network/host separation from other environments, and what logging/monitoring/audit exists. Where a control is "none, accepted risk", write that explicitly with a date rather than leaving it blank.
- Verify-complete: the environment record exists, names each dev environment with its separation + protection controls (or explicit accepted-risk entries), and the PO.5.1 re-derivation check for its quotes passes.
- Run ref: evidence/PO.5.1.md. Park class: needs-human.
