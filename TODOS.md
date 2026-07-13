# TODOS

## Validator

### Fail one skill, not the whole run, on an unreadable SKILL.md

**What:** Wrap the `read_text` in `validate_skill` so a non-UTF-8 or permission-broken SKILL.md returns a one-item error list instead of crashing the run with a raw traceback.

**Why:** One corrupt file currently aborts validation of the entire catalog, hiding the per-skill report for everything else.

**Context:** Pre-existing (predates the 0.1.1 hardening); surfaced by the 0.1.1 adversarial review but out of that diff's scope. The read is at the top of `validate_skill` in `scripts/validate.py`; `check_protocol_doc_refs` reads playbooks/runtime the same way and needs the same guard. Add a fixture test alongside the ones in `tests/test_validate.py`.

**Effort:** S
**Priority:** P2
**Depends on:** None

### One reference grammar shared by validator and orphan test

**What:** Extract "what counts as an explicit protocol reference" into a single helper in `scripts/validate.py` that `tests/test_architecture.py`'s orphan test imports, instead of two separately maintained regex sets.

**Why:** The two checkers can silently drift: today a backticked name outside a Composes/rides clause satisfies the orphan test but is validated by nothing.

**Context:** Flagged (low confidence) by the 0.1.1 review's maintainability pass. The validator scopes backticked names to Composes/rides clauses and checks `.md` tokens everywhere; the orphan test accepts backticked names anywhere. Decide which asymmetries are deliberate, encode the rest once.

**Effort:** S
**Priority:** P2
**Depends on:** None

## Completed
