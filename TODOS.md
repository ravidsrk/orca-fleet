# TODOS

## Validator

### One reference grammar shared by validator and orphan test

**What:** Extract "what counts as an explicit protocol reference" into a single helper in `scripts/validate.py` that `tests/test_architecture.py`'s orphan test imports, instead of two separately maintained regex sets.

**Why:** The two checkers can silently drift: today a backticked name outside a Composes/rides clause satisfies the orphan test but is validated by nothing.

**Context:** Flagged (low confidence) by the 0.1.1 review's maintainability pass. The validator scopes backticked names to Composes/rides clauses and checks `.md` tokens everywhere; the orphan test accepts backticked names anywhere. Decide which asymmetries are deliberate, encode the rest once.

**Effort:** S
**Priority:** P2
**Depends on:** None

## Completed

### Fail one skill, not the whole run, on an unreadable SKILL.md

Shipped against issue #71. `read_text_safe` in `scripts/validate.py`; fixtures in `tests/test_validate.py`.
