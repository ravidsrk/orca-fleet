# PW.4.4 — Reuse Existing, Well-Secured Software When Feasible Instead of Duplicating Functionality

- Obligation (frozen NIST-SP-800-218@1.0.0): "Verify that acquired commercial, open-source, and all other third-party software components comply with the requirements, as defined by the organization, throughout their life cycles."
- Verdict: GAP
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Searched (all absent at HEAD):
  - NoMatch: `.github/workflows/validate.yml` :: `(?i)dependabot|renovate|pip-audit|snyk|\bosv\b|advisory|CVE`
  - Absent: `.github/dependabot.yml`
  - Absent: `.github/renovate*`
  - NoMatch: `runtime/pins.json` :: `(?i)vulnerab|CVE|advisory|end.of.life|eol`
- Context (what exists, and why it does not satisfy): pins are re-witnessed on audit cadence (orca pin witnessed 2026-09-16) and upstream audits evaluate components point-in-time — but no recurring mechanism verifies lifecycle compliance: no vulnerability-database monitoring, no automated known-vulnerability detection in the toolchain, no end-of-life tracking.
  - `runtime/pins.json:7`: "    "witnessed": "2026-09-16","
- Missing evidence: a recurring component-verification mechanism (vulnerability monitoring and/or automated detection) with a record of its runs.
- Owner: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Handoff: gaps/PW.4.4.md (verify-complete: a component-vulnerability check exists — automated or calendared — with its latest run recorded).
