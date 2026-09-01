# TODOS

## Completed

### One reference grammar shared by validator and orphan test

Shipped against issue #216. `explicit_protocol_refs` in `scripts/validate.py`; the
orphan test and the mission-guide compose check import it. Related-section
backticks are not composition.

### Fail one skill, not the whole run, on an unreadable SKILL.md

Shipped against issue #71. `read_text_safe` in `scripts/validate.py`; fixtures in `tests/test_validate.py`.
