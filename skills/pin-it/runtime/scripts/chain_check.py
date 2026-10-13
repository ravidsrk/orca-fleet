#!/usr/bin/env python3
"""Executable form of mission-chaining.md's degraded-terminal rule.

The chaining policy says a degraded terminal STOPS the chain and every other
named terminal may proceed only when the chain declared it allowed — but the
classification lived only as prose, so a terminal the prose forgot (migrate-it's
ABANDONED, added here after the full review) silently read as clean. This is
the checker a chaining coordinator runs at each link boundary, and `audit`
keeps the catalog honest: every bold terminal a mission declares must carry
the "(degraded)" label exactly when this classification calls it degraded, so
a new terminal cannot drift past the rule unlabelled.

Subcommands
    classify <terminal>            print clean | degraded | handoff
    gate --allowed A,B <terminal>  exit 0 + PROCEED, or exit 1 + STOP <why>
    audit [--root DIR]             check every skills/*/SKILL.md terminal label

Exit codes: 0 ok / proceed · 1 stop or audit failure · 2 usage / could not run.
"""
import argparse
import re
import sys
from pathlib import Path

DEGRADED_SUFFIXES = (
    "-WITH-PARKED", "-WITH-OPEN-ITEMS", "-WITH-GAPS", "-WITH-MANUAL-PARKED",
    "-WITH-BLOCKED", "-WITH-QUARANTINE", "-WITH-PINNED",
)
DEGRADED_STANDALONE = frozenset({"NO-GO", "INCONCLUSIVE", "ABANDONED"})
HANDOFF = frozenset({"awaiting-maintainer-merge"})
HANDOFF_SUFFIX = "-WITH-HANDOFF"

_TERMINAL_RE = re.compile(r"^- \*\*([A-Z][A-Z0-9-]*)\*\*(\s*\(degraded\b)?", re.M)


def classify(terminal):
    """clean | degraded | handoff for one named mission terminal."""
    name = (terminal or "").strip()
    if name in DEGRADED_STANDALONE or name.endswith(DEGRADED_SUFFIXES):
        return "degraded"
    if name in HANDOFF or name.endswith(HANDOFF_SUFFIX):
        return "handoff"
    return "clean"


def gate(terminal, allowed):
    """(proceed, why). Degraded always stops; anything else proceeds only
    when the chain declared it allowed up front."""
    cls = classify(terminal)
    if cls == "degraded":
        return False, f"{terminal} is degraded — the chain stops and parks"
    if terminal not in allowed:
        return False, f"{terminal} ({cls}) is not in the chain's allowed set {sorted(allowed)}"
    return True, f"{terminal} ({cls}) is declared allowed"


def audit(root=None):
    """Problems where a mission's "(degraded)" label disagrees with classify()."""
    root = Path(root) if root else Path(__file__).resolve().parent.parent.parent
    problems = []
    for skill_md in sorted((root / "skills").glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        for name, label in _TERMINAL_RE.findall(text):
            cls = classify(name)
            if label and cls != "degraded":
                problems.append(f"{skill_md.parent.name}: {name} is labelled (degraded) "
                                f"but classifies {cls}")
            if cls == "degraded" and not label:
                problems.append(f"{skill_md.parent.name}: {name} classifies degraded but "
                                "carries no (degraded) label")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("classify")
    c.add_argument("terminal")
    g = sub.add_parser("gate")
    g.add_argument("--allowed", required=True, help="comma-separated terminals the chain declared")
    g.add_argument("terminal")
    a = sub.add_parser("audit")
    a.add_argument("--root", default=None)
    args = parser.parse_args(argv)
    if args.command == "classify":
        print(classify(args.terminal))
        return 0
    if args.command == "gate":
        allowed = {t.strip() for t in args.allowed.split(",") if t.strip()}
        proceed, why = gate(args.terminal, allowed)
        print(f"{'PROCEED' if proceed else 'STOP'}: {why}")
        return 0 if proceed else 1
    problems = audit(args.root)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print("chain-check: every declared terminal label agrees with the classification")
    return 0


if __name__ == "__main__":
    sys.exit(main())
