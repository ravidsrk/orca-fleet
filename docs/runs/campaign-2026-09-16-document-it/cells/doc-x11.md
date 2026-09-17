# doc-x11 — cli:runtime/scripts/sandbox_doctor.py × explanation — FILLED

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: grep-both-ways failure origin, structural-JSON + stripped-text reading,
whole-token recipe match, caller-named-file removal. Confidence: high — rationale is
the module docstring.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: `> Why:` block; anchors only.
- Spec: frozen explanation cell for sandbox_doctor.py from
  `runtime/scripts/sandbox_doctor.py:1-25` + `:81-128`, not invented.
- Test-adequacy: claimcheck GREEN; rename names_recipe→titles_recipe RED
  (nc-doc-x11.txt).

## Anchors

- claimcheck --cell sandbox_doctor.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-x11.txt` (exit 1, file restored).
