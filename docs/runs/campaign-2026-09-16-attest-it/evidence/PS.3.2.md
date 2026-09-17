# PS.3.2 — Archive and Protect Each Software Release

- Obligation (frozen NIST-SP-800-218@1.0.0): "Collect, safeguard, maintain, and share provenance data for all components of each software release (e.g., in a software bill of materials .SBOM)."
- Verdict: GAP
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Searched (all absent at HEAD):
  - Absent: `**/*sbom*`
  - Absent: `**/*cyclonedx*`
  - Absent: `**/*spdx*`
  - Absent: `**/*swid*`
- Decisive negative evidence: the component-provenance records (runtime/pins.json, .github/ci-tools.lock) postdate all 9 published release cuts — `git show v0.6.1:runtime/pins.json` fails — so no release cut carries its components' provenance, and no per-release SBOM exists. Current-state pins are maintained (pins.json witnessed 2026-09-16) but that is a promise for the next cut, not an artifact for any past one.
  - `docs/releases.json:8`: "      "commit": "fc0d08c4276ae25e5e3ac48caa11976ec331e304","
- Missing evidence: per-release component provenance (SBOM or equivalent) archived with each release.
- Owner: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Handoff: gaps/PS.3.2.md (verify-complete: the next release cut retains pins.json + ci-tools.lock, or a per-release SBOM is published and referenced from releases.json).
