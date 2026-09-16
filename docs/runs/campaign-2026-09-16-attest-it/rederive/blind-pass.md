# Second-pass verdict review (fairness re-derivation)

Method: after the mechanical re-derivation passed 664/664, a second judgment pass
re-asked, per close call, "does the cited artifact satisfy the STATEMENT?" —
starting from the frozen statement text, then re-opening the artifact. Blindness
caveat (recorded, not hidden): same session as gathering (`instructed-isolation`);
the mechanical script is the independent oracle for existence, this pass is the
independent oracle for fairness. A sample of citations was additionally re-read
through a different tool path (`git show TARGET:path | sed`) — 6/6 byte-identical.

## Expectations vs gathered verdicts (close calls only)

- PO.1.3 (commercial-component requirements): expectation from statement alone was
  GAP-or-vacuous. Artifact check: component inventory (pins.json 4 OSS repos +
  OSS lockfile + stdlib-only rule + "no other cloud accounts") genuinely exhausts
  the component set with zero commercial items. VERIFIED-via-empty-precondition
  upheld — with the re-opener condition recorded in the evidence file.
- PS.1.1 (least-privilege storage): expectation was GAP (write access is a GitHub
  setting, external state). Artifact check: for intentionally-public code the
  task's own example shifts the duty to integrity + availability + accountability,
  all evidenced in-tree (hashes, per-account log, owner review, no-rewrite rule).
  VERIFIED upheld, residuals explicit (unsigned third, external write enforcement).
- PS.2.1 (integrity info to acquirers): expectation VERIFIED. Artifact check:
  releases.json cut SHAs + annotated tags + CHANGELOG, all 9 bindings re-derived.
  Upheld; unsigned tags noted as residual, not hidden.
- PS.3.2 (per-release component provenance): expectation was VERIFIED (pins exist).
  Artifact check REVERSED it: pins/lock postdate all 9 cuts (`git show
  v0.6.1:runtime/pins.json` fails), no SBOM. GAP upheld — the pass's highest-value
  reversal; a promise for the next cut is not an artifact for any past one.
- PW.4.4 (lifecycle component verification): expectation GAP. Artifact check:
  point-in-time audits + pin re-witnessing exist, but no recurring vuln
  verification. GAP upheld.
- PW.6.1 vs PW.6.2 (interpreter tools): expectation was GAP/GAP. Artifact check
  split them: PW.6.1's statement (USE current, integrity-checked tools) is met
  (py3.13 pin, hashed toolchain, checksum-verified downloads); PW.6.2's
  (DETERMINE + implement approved security-feature configs) is not — the only
  approved config explicitly declines the broader ruleset. Split upheld.
- PW.9.1/PW.9.2 (secure defaults): expectation was GAP (no deployable service).
  Artifact check: the software's security-relevant settings ARE the fleet
  operational defaults, and a fail-closed baseline is defined, implemented, and
  documented. VERIFIED upheld with the scope note explicit.
- RV.1.1 (vuln intake): expectation VERIFIED. Artifact check: intake channels +
  audits + investigation trail exist; automated feed missing (residual pointing
  at the PW.4.4 gap, no double-count). Upheld.
- RV.3.3 (class eradication): expectation was the weakest VERIFIED. Artifact
  check: executed evidence exists (10-attack review → lane-wide executed-control
  requirement → §10 re-measurement + vf-bench corpus + CHANGELOG class analysis).
  Upheld — execution, not just process.
- All 8 GAPs: each names missing evidence no in-tree artifact supplies; no
  substitute was found on the second look either. Owners + verify-complete
  observations present in all 8 handoffs.

## Divergences

- 1 reversal during gathering (PS.3.2 pass→GAP, above). 0 reversals in this pass.
- 7 citation errors caught by the mechanical oracle across both passes
  (releases.json numbering, 3 off-by-one lines, 8 U+2019 apostrophes, 1 script
  regex bug, 1 unstable log pin) — all corrected, none waived.
