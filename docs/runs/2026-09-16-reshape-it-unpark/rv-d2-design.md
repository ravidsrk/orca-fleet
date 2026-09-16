# RV-D2 design-twice: the outcome-reader fork (drafted, not argued)

Seam: `runtime/scripts/verify.py` lines 1097-1184 — the control-outcome
reader (`STILLBORN_MARKERS`, `ASSERTION_MARKERS`, `STRONG_ASSERTION_RE`,
`_ERRORS_RE`, `_FAILURES_RE`, `_counted`, `_failure_signature`), called from
exactly one site (`execute_negative_control`, line 1458) and read by tests
under one name (`verify._failure_signature`, 7 uses, no mocks). WIDTH today:
92 top-level symbols.

## Option A — move + narrow re-export (CHOSEN)

Move all 7 seam symbols to `runtime/scripts/_verify_sig.py`, loaded from
`verify.py` via an eager `importlib.spec_from_file_location` block (the
`validate.py::_eval_spec` shape, proven in RV-D1; `verify.py` already imports
`importlib.util` + `pathlib.Path`). `verify.py` re-exports exactly one name,
`_failure_signature` (lowercase: zero WIDTH cost); `execute_negative_control`
calls it through the submodule. The marker tables + `_counted` go private
with the move — `git grep` proves zero users outside `_failure_signature`,
so this narrows the true interface; reversible via git; disclosed in the PR,
not an ADR (no consumer, not one-way). WIDTH 92 → 85. Zero existing-test
edits.

## Option B — move + update all test imports (REJECTED)

Move the seam and rewrite the 7 `verify._failure_signature` reads to the new
home, with no shim. Same WIDTH (85 — the re-export is free) but it edits the
net in the DEEPEN unit — the coupling `characterize.md` exists to forbid —
and it breaks the revert negative control (head tests importing the new home
go stillborn-ImportError, not assertion-RED, when production is restored to
base). Zero WIDTH gain for an oracle edit plus a dead NC.

## Why A wins

A keeps every call site green with zero test churn and keeps the NC
assertion-shaped (the WIDTH pin reads file text for the count and imports
only `verify.py` itself, which exists in both shapes). B buys nothing here —
the re-export costs no WIDTH — and spends the oracle. Unanimous on the
numbers, not just the doctrine.
