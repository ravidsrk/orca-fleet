# PO.5.1 — Implement and Maintain Secure Environments for Software Development

- Obligation (frozen NIST-SP-800-218@1.0.0): "Separate and protect each environment involved in software development."
- Verdict: GAP
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Searched (all absent at HEAD):
  - NoMatch: `docs/ops.md` :: `(?i)multi-factor|MFA|zero trust|network segment|conditional access`
  - NoMatch: `runtime/sandbox-policy.md` :: `(?i)multi-factor|MFA|zero trust|network segment|conditional access`
  - NoMatch: `.github/workflows/validate.yml` :: `(?i)environment:|protection rule`
- Context (what exists, and why it does not satisfy): destructive work is required to run in ephemeral per-workspace sandboxes rather than on the host, and CI runs on hosted runners — but no authentication, segmentation, logging, monitoring, or audit posture for the development environments (maintainer machine, runners, sandboxes) is documented anywhere.
  - `runtime/sandbox-policy.md:64`: "## Danger belongs in an ephemeral sandbox, never on the host"
- Missing evidence: environment inventory with separation/protection controls (auth, segmentation, logging/monitoring) per environment.
- Owner: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Handoff: gaps/PO.5.1.md (verify-complete: environment record exists naming each dev environment and its separation + protection controls).
