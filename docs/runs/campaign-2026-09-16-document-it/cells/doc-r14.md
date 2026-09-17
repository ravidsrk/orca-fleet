# doc-r14 — cli:runtime/scripts/wtree.sh × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: temp-index content fingerprint, untracked-included/ignored-out semantics,
commit-invariance, stat-cache seed with racy-index guard, exits 0/1 fail-closed.
Confidence: high — full file read (63 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; test anchor honestly "exercised by" (no dedicated test
  file exists — verified, not assumed).
- Spec: frozen reference cell for wtree.sh from `runtime/scripts/wtree.sh:1-30`. No
  creep.
- Test-adequacy: claimcheck GREEN; flagless CLI so the control moves the anchored
  `tests/test_evidence_run.py` aside → RED (nc-doc-r14.txt), then restores.

## Anchors

- claimcheck --cell wtree.sh → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r14.txt` (exit 1, file restored).
