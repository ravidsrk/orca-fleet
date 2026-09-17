# PW.6.2 — Configure the Compilation, Interpreter, and Build Processes to Improve Executable Security

- Obligation (frozen NIST-SP-800-218@1.0.0): "Determine which compiler, interpreter, and build tool features should be used and how each should be configured, then implement and use the approved configurations."
- Verdict: GAP
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD — the determination that exists, and what it declines):
  - `ruff.toml:7`: "select = ["E9", "F63", "F7", "F82"]"
  - `ruff.toml:3`: "# not a catalog-gate hole (issue #214)."
- Searched (absent at HEAD):
  - NoMatch: `ruff.toml` :: `(?i)S\[|bandit|flake8-bandit|semgrep|darglint`
  - NoMatch: `.github/workflows/validate.yml` :: `(?i)bandit|semgrep|warnings.as.errors|-W error`
- Why this is a gap, not a pass: the only approved static configuration selects syntax/undefined-name rules; no security-feature configuration for the interpreter or build (warning classes for insecure code, warnings-as-errors, approved security ruleset) is determined, implemented, or continuously verified anywhere.
- Missing evidence: an approved interpreter/build security-feature configuration, implemented as config-as-code and enforced in CI.
- Owner: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Handoff: gaps/PW.6.2.md (verify-complete: approved security configuration exists as config-as-code and a CI step enforces it).
