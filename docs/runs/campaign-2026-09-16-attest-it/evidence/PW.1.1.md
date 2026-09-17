# PW.1.1 — Design Software to Meet Security Requirements and Mitigate Security Risks

- Obligation (frozen NIST-SP-800-218@1.0.0): "Use forms of risk modeling – such as threat modeling, attack modeling, or attack surface mapping – to help assess the security risk for the software."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `docs/reviews/2026-09-10-review.md:9`: "Reviewed SHA: `af8ea8975cdc5e9d0911a1d251cb02afd4f7a5dd` (main, 2026-09-10, merge of #254)."
  - `docs/reviews/2026-09-10-review.md:29`: "mutation unit. Six of ten manifest-gaming attacks landed. The claim that holds is narrower:"
  - `docs/reviews/2026-09-10-review.md:34`: "1. **The negative control is never executed by any mechanism.** `verify.py:370-397` pattern-matches"
  - `skills/harden-it/SKILL.md:4`: "  Establish a threat model and close it: audit → prove exploits → fix → RE-ATTACK the fix and"
- Re-derive: quotes exist at HEAD (rederive.py); the archived review is attack modeling applied to this software at a pinned SHA (10 manifest-gaming attacks A1–A10 with bypass logs, §10 dated re-measurement at 9afefc6); harden-it institutionalizes threat-model → exploit → re-attack as the standing loop.
- Residuals: risk modeling is review-driven, not a standing STRIDE artifact per component.
