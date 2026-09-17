# Gap handoff — PW.6.2 (approved interpreter/build security-feature configuration)

- Obligation (frozen NIST-SP-800-218@1.0.0): "Determine which compiler, interpreter, and build tool features should be used and how each should be configured, then implement and use the approved configurations."
- Missing evidence: an approved interpreter/build security-feature configuration. Found instead: ruff.toml selects syntax/undefined-name rules only (E9/F63/F7/F82) with the broader ruleset explicitly deferred (issue #214); no security ruleset, warnings-as-errors policy, or interpreter hardening config exists.
- Recipient: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Ask (Task item): determine and land the approved configuration as config-as-code: e.g., extend ruff.toml with an agreed security ruleset (or adopt bandit/semgrep with a pinned config), decide the warnings-as-errors policy, and enforce it in a CI step. If the decision is "not now", record that as a dated DECISIONS-line exception with a re-evaluation trigger — the gap then converts to a tracked exception rather than an undocumented absence.
- Verify-complete: the approved security configuration exists as config-as-code, a CI step enforces it (or a dated exception with re-evaluation trigger is recorded); the PW.6.2 re-derivation check for its quotes passes.
- Run ref: evidence/PW.6.2.md. Park class: needs-human (taste: ruleset choice).
