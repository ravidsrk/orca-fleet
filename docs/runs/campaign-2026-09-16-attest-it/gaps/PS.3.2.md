# Gap handoff — PS.3.2 (per-release component provenance)

- Obligation: NIST-SP-800-218@1.0.0 PS.3.2 — "Collect, safeguard, maintain, and share provenance data for all components of each software release (e.g., in a software bill of materials .SBOM)."
- Missing evidence: per-release component provenance archived with each release. Found instead: release-level provenance exists (releases.json rows + annotated tags), and current-state component pins exist (runtime/pins.json, .github/ci-tools.lock) — but both postdate all 9 release cuts, and no SBOM in any standard format exists.
- Recipient: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Ask (Task item): pick one: (a) extend the release-cut procedure (docs/ops.md) so each future cut records the component set (pins.json + ci-tools.lock SHAs, or a generated SBOM in CycloneDX/SPDX) and references it from releases.json; or (b) publish a one-time SBOM for the current tree plus the going-forward rule. Either way the next release row must point at component provenance a fresh clone can re-read.
- Verify-complete: the next published release row references component provenance readable from a fresh clone at the cut commit (or a published SBOM artifact); the PS.3.2 re-derivation check passes against it.
- Run ref: evidence/PS.3.2.md. Park class: needs-human (taste: SBOM format choice).
