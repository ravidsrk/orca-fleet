# PW.1.3 — Design Software to Meet Security Requirements and Mitigate Security Risks

- Obligation (frozen NIST-SP-800-218@1.0.0): "Where appropriate, build in support for using standardized security features and services (e.g., enabling software to integrate with existing log management, identity management, access control, and vulnerability management systems) instead of creating proprietary implementations of security features and services. .Formerly PW.4.3"
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.gitleaks.toml:24`: "useDefault = true"
  - `SECURITY.md:7`: "1. Use GitHub's private vulnerability reporting on this repository"
- Re-derive: quotes exist at HEAD (rederive.py); standardized services are adopted, not re-implemented: the gitleaks default rule pack unmodified, GitHub's private vulnerability reporting, Ed25519 signatures (runtime/scripts/ed25519.py + dispatch-sign.py), and git/SHA integrity — no proprietary scanner, crypto, or reporting mechanism.
- Residuals: none statement-level.
