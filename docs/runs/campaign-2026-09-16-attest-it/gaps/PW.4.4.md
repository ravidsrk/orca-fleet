# Gap handoff — PW.4.4 (lifecycle verification of third-party components)

- Obligation: NIST-SP-800-218@1.0.0 PW.4.4 — "Verify that acquired commercial, open-source, and all other third-party software components comply with the requirements, as defined by the organization, throughout their life cycles."
- Missing evidence: a recurring component-verification mechanism. Found instead: point-in-time upstream audits (2026-09-09/10) and pin re-witnessing (orca, 2026-09-16) — but no vulnerability-database monitoring, no automated known-vulnerability detection in the toolchain, no end-of-life tracking.
- Recipient: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Ask (Task item): stand up one recurring check and record its runs: e.g., enable Dependabot/Renovate alerts on the repo, or add a scheduled CI job running `pip-audit`/OSV-scan over .github/ci-tools.lock, or calendar a quarterly manual CVE review of pins.json upstreams with a dated log. Any of these closes the gap if its runs are recorded.
- Verify-complete: the mechanism exists (config in tree or calendar record) with ≥1 recorded run dated after this run; the PW.4.4 re-derivation check for its quotes passes.
- Run ref: evidence/PW.4.4.md. Park class: needs-human (taste: mechanism choice).
