# PS.1.1 — Protect All Forms of Code from Unauthorized Access and Tampering

- Obligation (frozen NIST-SP-800-218@1.0.0): "Store all forms of code – including source code, executable code, and configuration-as-code – based on the principle of least privilege so that only authorized personnel, tools, services, etc. have access."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Basis: the code is intentionally public open-source, so per the task's own example the duty is integrity + availability + accountability: git object hashes, per-account change attribution, owner review of changes, and no history rewrites.
- Evidence (verbatim at HEAD):
  - `docs/ops.md:196`: "   through the normal gates — never a force-push or a history rewrite"
  - `SECURITY.md:5`: "Please **do not** open a public GitHub issue for a security report."
  - `runtime/evidence-manifest.md:144`: "later audit reject an artifact whose hash no longer matches."
- Re-derive: quotes exist at HEAD (rederive.py); accountability: `git log --format='%h %an %ae %s' -5` shows per-account attribution; merge history (`git log --merges`) shows PR-gated integration; 670/1211 commits carry good signatures (`git log --format=%G?`).
- Residuals: ~1/3 of commits are unsigned or uncheckable (no signing requirement enforced); write-access enforcement itself is a GitHub repo setting (external state, not re-derivable from the tree).
