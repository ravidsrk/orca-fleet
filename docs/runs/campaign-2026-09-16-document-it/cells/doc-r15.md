# doc-r15 — config:runtime/one-way-doors.json × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: 9 doors tabled with titles, door record shape (id/title/why/keywords),
multi-word substring matching rule, decisions.py enforcement link.
Confidence: high — full registry read (157 lines).

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: Keys-table form for a config entity; titles match the registry verbatim.
- Spec: frozen reference cell for one-way-doors.json from the registry itself +
  enforcement in `runtime/scripts/decisions.py:109-135`. No creep.
- Test-adequacy: claimcheck GREEN; rename scope-change→scope-drift RED (nc-doc-r15.txt).

## Anchors

- claimcheck --cell one-way-doors.json → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r15.txt` (exit 1, file restored).
