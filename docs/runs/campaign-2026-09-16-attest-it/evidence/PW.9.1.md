# PW.9.1 — Configure Software to Have Secure Settings by Default

- Obligation (frozen NIST-SP-800-218@1.0.0): "Define a secure baseline by determining how to configure each setting that has an effect on security or a security-related setting so that the default settings are secure and do not weaken the security functions provided by the platform, network infrastructure, or services."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Scope note: this software ships no networked service; the security-relevant settings are the fleet's operational defaults (worker profiles, capability opt-ins, secret handling), and the baseline is fail-closed by default.
- Evidence (verbatim at HEAD):
  - `runtime/sandbox-policy.md:64`: "## Danger belongs in an ephemeral sandbox, never on the host"
  - `runtime/scripts/spawn_worker.sh:98`: "#   ORCA_COORD_ALLOW_AUTONOMOUS_WRITE  must be 1 for PROFILE=rw (accept autonomous bypass workers)"
  - `runtime/scripts/spawn_worker.sh:99`: "#   ORCA_COORD_ALLOW_DANGER   must be 1 for PROFILE=danger (implies the above + ephemeral sandbox)"
  - `.gitignore:1`: ".env"
  - `.gitignore:2`: ".secrets/*"
- Re-derive: quotes exist at HEAD (rederive.py); fail-closed defaults are documented (ro non-mutating; rw/danger refused without explicit opt-ins; secrets never in git) and the CI-tested negative controls (canary, drill issues) exercise them.
- Residuals: no deployable-service admin console exists, so "settings for software administrators" maps to operator docs (sandbox-policy, ops.md) rather than an admin guide.
