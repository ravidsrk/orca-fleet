# PW.9.2 — Configure Software to Have Secure Settings by Default

- Obligation (frozen NIST-SP-800-218@1.0.0): "Implement the default settings (or groups of default settings, if applicable), and document each setting for software administrators."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `runtime/scripts/spawn_worker.sh:180`: "PROFILE="${PROFILE:-rw}""
  - `ruff.toml:4`: "target-version = "py313""
  - `.gitleaks.toml:24`: "useDefault = true"
  - `runtime/sandbox-policy.md:64`: "## Danger belongs in an ephemeral sandbox, never on the host"
- Re-derive: quotes exist at HEAD (rederive.py); defaults are implemented in code (spawn_worker.sh profile handling with refusal branches), stored as config-as-code under change control (git + PR gates), and documented per-setting with purpose, options, and security relevance in runtime/sandbox-policy.md and docs/ops.md.
- Residuals: same scope note as PW.9.1 (operator docs, not a service admin guide).
