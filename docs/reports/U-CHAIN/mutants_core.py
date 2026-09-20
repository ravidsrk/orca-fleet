"""Shared core for the U-CHAIN mutation harnesses.

Two round-2 Required findings live here, not in the mutant lists:

BOT-5 / S-R2-2 — the baseline must be SELF-DERIVING. `run_mutants-r2.py` read an
untracked `base-policy.md`, so a clean-checkout replay raised FileNotFoundError before
a single mutant ran. The baseline is now read from a pinned Git object and its bytes are
checked against a recorded SHA256, so the harness runs from an exact checkout and cannot
silently run against the wrong baseline.

R2-HARNESS / S-R2-3 — a nonzero exit is NOT a kill. An ImportError, a collection error,
or a run in which no test executed all exit nonzero while proving nothing: no contract
assertion ever ran. A kill requires an ASSERTION failure from the covering test. Anything
else is STILLBORN and fails the harness. Both positive controls must be green for the
same reason: a battery whose controls are red measured nothing.
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

POLICY = Path("runtime/mission-chaining.md")

# The unit's BASE: the policy bytes before the U-CHAIN fix batch. Identical at a58bf71a
# (the SHA the round-2 transcript pinned) and at ed51fe11 (this branch's merge base).
UNIT_BASE_SHA = "ed51fe11de5f7329ecf02ffb933bf50648ae5654"
BASE_SHA256 = "1bacd1fe7be765311b08abba787f45844b39658a8908096fbc853a09a4a26e72"

CMD = [sys.executable, "-B", "-m", "unittest",
       "tests.test_architecture.TestArchitecture.test_chain_link_boundary_is_specified", "-v"]


def baseline():
    """The pre-fix policy bytes, derived from the pinned commit and hash-checked."""
    p = subprocess.run(["git", "show", f"{UNIT_BASE_SHA}:{POLICY.as_posix()}"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"FATAL: cannot derive baseline from {UNIT_BASE_SHA}: {p.stderr.strip()}")
    got = hashlib.sha256(p.stdout.encode()).hexdigest()
    if got != BASE_SHA256:
        sys.exit(f"FATAL: baseline hash mismatch: expected {BASE_SHA256}, got {got}")
    return p.stdout


def bullet(text, start):
    """The whole top-level bullet whose first line starts with `start`."""
    m = re.search(r"(?ms)^- " + re.escape(start) + r".*?(?=^- \*\*)", text)
    assert m, start
    return m.group(0)


def repl_bullet(text, start, new):
    return text.replace(bullet(text, start), new)


def drop_bullet(text, start):
    return text.replace(bullet(text, start), "")


def sub(text, old, new):
    assert old in text, old[:60]
    assert text.count(old) == 1, f"ambiguous selector: {old[:60]}"
    return text.replace(old, new, 1)


def classify(proc):
    """GREEN / RED / STILLBORN.

    RED means the covering test ran and an assertion failed — the only outcome that
    proves the contract test binds the mutated obligation. A nonzero exit with no
    assertion failure (ImportError, loader error, no tests collected) is STILLBORN.
    """
    out = proc.stdout + proc.stderr
    if re.search(r"^Ran 0 tests", out, re.M):
        return "STILLBORN"
    if proc.returncode == 0:
        return "GREEN" if re.search(r"^OK", out, re.M) else "STILLBORN"
    if "AssertionError" in out and re.search(r"FAILED \(failures=\d+", out):
        return "RED"
    return "STILLBORN"


def _run_test():
    return subprocess.run(CMD, capture_output=True, text=True)


def _control(label, orig):
    POLICY.write_text(orig)
    p = _run_test()
    verdict = classify(p)
    print(f"{label}: exit={p.returncode}; {verdict} — unmutated head")
    if verdict != "GREEN":
        first = next((l for l in (p.stdout + p.stderr).splitlines()
                      if "Error" in l or "FAILED" in l), "")
        if first:
            print(f"    {first.strip()}")
    return verdict == "GREEN"


def main(mutants):
    """`mutants` maps label -> (expected verdict, why, fn). Expected is "RED" or "GREEN"."""
    orig = POLICY.read_text()
    failures = []

    print("== POSITIVE CONTROL ==")
    if not _control("fixed-head", orig):
        failures.append("fixed-head control is not GREEN")

    print("\n== MUTANTS ==")
    survivors, stillborn, wrong = [], [], []
    for label, (expected, why, fn) in mutants.items():
        POLICY.write_text(fn(orig))
        p = _run_test()
        POLICY.write_text(orig)
        out = (p.stdout + p.stderr).strip()
        verdict = classify(p)
        shown = {"RED": "KILLED (RED)", "GREEN": "GREEN", "STILLBORN": "STILLBORN"}[verdict]
        print(f"{label}: exit={p.returncode}; {shown} [expected {expected}] — {why}")
        first = next((l for l in out.splitlines() if "AssertionError" in l), "")
        if first:
            print(f"    {first.strip()}")
        if verdict == "STILLBORN":
            stillborn.append(label)
        elif verdict != expected:
            (survivors if expected == "RED" else wrong).append(label)

    print(f"\n{len(mutants)} mutants run; "
          f"{sum(1 for k, v in mutants.items() if v[0] == 'RED')} expected RED, "
          f"{sum(1 for k, v in mutants.items() if v[0] == 'GREEN')} expected GREEN")
    print(f"SURVIVORS (expected RED, stayed green): {survivors or 'none'}")
    print(f"FALSE REDS (expected GREEN, went red): {wrong or 'none'}")
    print(f"STILLBORN (nonzero without an assertion failure): {stillborn or 'none'}")

    if not _control("head-restored", orig):
        failures.append("head-restored control is not GREEN")

    for name, bad in (("survivors", survivors), ("false reds", wrong),
                      ("stillborn runs", stillborn)):
        if bad:
            failures.append(f"{len(bad)} {name}: {bad}")
    if failures:
        print("\nHARNESS FAILED: " + "; ".join(failures))
        sys.exit(1)
    print("\nHARNESS OK: every mutant died for the right reason; both controls GREEN.")
    sys.exit(0)
