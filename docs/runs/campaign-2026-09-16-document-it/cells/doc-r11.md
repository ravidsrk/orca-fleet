# doc-r11 — cli:runtime/scripts/sandbox_doctor.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: transcript verdict reader, two positional args, whole-id recipe match,
structural JSON vs stripped-text reading, no-fail-and-no-warn rule, exits 0/1/2.
Confidence: high — full file read (151 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: template kept; fetch invocation unbackticked where it carries a flag the
  source never names.
- Spec: frozen reference cell for sandbox_doctor.py from
  `runtime/scripts/sandbox_doctor.py:1-25` + verdict `:107-128` + main `:131-147`.
  No creep.
- Test-adequacy: claimcheck GREEN; flagless CLI so the control moves the anchored
  `tests/test_sandbox_doctor.py` aside → RED (nc-doc-r11.txt), then restores.

## Anchors

- claimcheck --cell sandbox_doctor.py → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r11.txt` (exit 1, file restored).
