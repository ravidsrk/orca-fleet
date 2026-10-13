#!/usr/bin/env python3
"""Control-outcome reader — the verdict behind verify.py's executed negative
control (moved here verbatim by reshape-it RV-D2; `verify.py` keeps one
re-export, `_failure_signature`). Private module: import through
`runtime/scripts/verify.py`, never directly.
"""
import re


# A control run that dies before the oracle ever executes is a STILLBORN MUTANT, not a kill: the
# non-zero exit is the module failing to load, so it would be non-zero for any command at all.
# Vera-Pérez et al. 2018 and Niedermayr et al. 2016 are explicit that only a mutant the test suite
# actually EXERCISES says anything about that suite (docs/reviews/2026-09-11 §4 A14; #280).
STILLBORN_MARKERS = (
    "importerror", "modulenotfounderror", "syntaxerror", "indentationerror",
    "cannot import name", "error collecting", "collection error", "unable to import",
    "no module named", "failed to load", "conftest.py", "attributeerror: module",
)
# What a real oracle failing looks like, across the runners the catalog's missions actually drive.
ASSERTION_MARKERS = (
    "assertionerror", "assert", "failed", "fail:", "failures=", "expected", "not ok",
    "panicked at", "✗", "test failed", "e   ", "✕",
)
# Evidence an assertion was actually EVALUATED and FAILED, as opposed to a runner summarising that
# something went wrong, or a traceback merely QUOTING a line of source. Only these override a
# stillborn marker, and each is anchored to the start of a line for that reason: a collection
# traceback echoes the source it was reading ("    assert helper() == 1") while the assertion
# never ran, so an unanchored "assert " let a stillborn mutant through (PR #308 review, round 3).
# `AssertionError` at the head of a line is an exception that was RAISED; a failed import cannot
# produce one. pytest prefixes the failing assertion with `E`, and never the source it quotes.
STRONG_ASSERTION_RE = re.compile(
    r"^[ \t]*(?:e[ \t]+)?assertionerror\b"      # AssertionError raised (pytest prefixes E)
    r"|^[ \t]*e[ \t]+assert\b"                   # pytest's failing assertion line
    r"|^[ \t]*thread .*panicked at"               # Rust
    r"|✗|✕",
    re.M,
)
# unittest and pytest both distinguish an ERROR (an exception escaped) from a FAILURE (an assertion
# was evaluated and was false). Only the second exercises the oracle. `FAILED (errors=1)` is an
# import blowing up, and it says "FAILED" — which is why the assertion markers alone cannot be
# trusted to mean an assertion ran (PR #308 review).
_ERRORS_RE = re.compile(r"\berrors?\s*[=:]\s*(\d+)|\b(\d+)\s+errors?\b")
_FAILURES_RE = re.compile(r"\bfailures?\s*[=:]\s*(\d+)|\b(\d+)\s+failed\b")


def _counted(pattern, text):
    """Sum of every count `pattern` reports in a runner's summary line. None when it reports none."""
    total, seen = 0, False
    for match in pattern.finditer(text):
        for group in match.groups():
            if group is not None:
                total += int(group)
                seen = True
    return total if seen else None


def _failure_signature(out, err):
    """Read the control run's output. Returns (ok, reason).

    A non-zero exit is not a kill on its own — `grep` exits 1 on no-match, an unimportable module
    exits 1 before a single assertion runs, and both look identical to a gate that only reads the
    return code. The RED must LOOK like an oracle failing.

    Three layers, in this order, because two review rounds on #308 showed either one alone is
    wrong. The RUNNER'S OWN SUMMARY is the best evidence there is: unittest and pytest already
    separate errors from failures, so `FAILED (errors=1)` is a stillborn mutant no matter what
    words surround it. Only when no summary exists — a plain script, say — does the substring scan
    matter, and even then explicit assertion evidence outranks it: a test asserting that a
    `ModuleNotFoundError` is raised prints that name while its oracle runs perfectly well. That
    evidence is line-anchored, because a collection traceback QUOTES the source it was reading —
    an `assert` in echoed source is not an assertion that ran."""
    text = f"{out}\n{err}".lower()
    if not text.strip():
        return False, ("the control run produced NO output at all. A silent non-zero exit is not a "
                       "failing test — it is what `grep` does when it finds nothing; fail-closed "
                       "(#280)")
    errors = _counted(_ERRORS_RE, text)
    failures = _counted(_FAILURES_RE, text)
    if errors and not failures:
        return False, (f"the runner reports {errors} error(s) and no assertion failure — an error is "
                       "an exception escaping, not an oracle evaluating to false, so it does not "
                       "show the criterion-bound assertion ran at all; fail-closed (#280)")
    if not failures:
        # No runner summary to trust, so read the text. A stillborn mutant refuses unless the
        # output carries evidence an assertion was really evaluated.
        stillborn = [mark for mark in STILLBORN_MARKERS if mark in text]
        if stillborn and not STRONG_ASSERTION_RE.search(text):
            return False, (f"the control run did not get as far as an oracle ({stillborn[0]!r} in "
                           "its output, and nothing showing an assertion was evaluated) — that is "
                           "a STILLBORN MUTANT, not a kill. The non-zero exit is the module failing "
                           "to load, which would happen for any command; the control must leave the "
                           "code runnable and fail an ASSERTION (#280)")
    if not any(mark in text for mark in ASSERTION_MARKERS):
        return False, ("the control run exited non-zero but its output names no assertion failure, "
                       "so nothing shows the criterion-bound oracle actually ran and failed; "
                       "fail-closed (#280)")
    return True, None
