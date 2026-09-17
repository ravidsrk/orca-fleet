# RV-D1 design-twice: the count-lint engine fork (drafted, not argued)

Seam: `scripts/validate.py` lines 891-919 — the count-lint regex engine
(`_ONES`, `_TEENS`, `_TENS`, `_SPELLED`, `_NUM`, `_SEP`, `_CATALOG_NOUN`,
`COUNT_LINT_RE`, `ALL_COUNT_RE`, `MISSION_CONTEXT_RE`) feeding
`check_doc_counts()` (lines 922-945). WIDTH today: 73 top-level symbols.

## Option A — move + narrow re-export (CHOSEN)

Move all 10 engine symbols to `scripts/_countlint.py`, loaded from
`validate.py` via `importlib.spec_from_file_location` (the `_eval_spec`
pattern already in the file, lines 53-56 — convention-consistent, works both
as `__main__` and under test importlib loading, where a plain
`from _countlint import` would fail for lack of package context).
`validate.py` keeps `COUNT_LINT_FILES` + `check_doc_counts()` (tests
`mock.patch.object(validate, "COUNT_LINT_FILES"/"ROOT")` — moving those names
would silently unmock the suite) and re-exports exactly one engine name,
`COUNT_LINT_RE` (the only engine name tests read: 7 uses).
`check_doc_counts()` reads the other two regexes as `_countlint.*`
attributes. `ALL_COUNT_RE` / `MISSION_CONTEXT_RE` leave `validate`'s
namespace — `git grep` proves zero external users, so this narrows the true
interface; reversible via git; disclosed in the PR, not an ADR (no consumer,
not one-way). WIDTH 73 → 64. Zero existing-test edits.

## Option B — move + update all test imports (REJECTED)

Move the engine and rewrite the 7 `validate.COUNT_LINT_RE` reads (plus the
`COUNT_LINT_FILES`/`check_doc_counts` mocks) to the new home, with no shim.
Narrower (`validate` loses all 10 names, WIDTH 73 → 63) but it edits the net
in the DEEPEN unit — the coupling `characterize.md` exists to forbid — and it
breaks the revert negative control (head tests importing the new home go
stillborn-ImportError, not assertion-RED, when production is restored to
base). The one extra WIDTH point is not worth an oracle edit plus a dead NC.

## Why A wins

A keeps every call site green with zero test churn, keeps the NC
assertion-shaped (the WIDTH pin reads file text, never imports), and still
drops two genuinely public-but-unused names. The re-export line is the honest
cost of an import-compatible move: 1 counted line for 10 removed.
