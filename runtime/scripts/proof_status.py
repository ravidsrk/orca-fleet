#!/usr/bin/env python3
"""Proof-posture reporter and CI lens over the mission catalog.

Distinct from ``scripts/validate.py`` (the build gate): this tool summarizes each
mission's proof tier and surfaces whether its ``proof_evidence`` report actually
resolves to a file in the repo — for humans (default report), machines (``--json``),
and CI (``--check``).

Reads every ``skills/*/SKILL.md`` frontmatter. Never writes files, never touches the
network. Frontmatter parsing mirrors ``scripts/validate.py``'s minimal key/scalar
approach — only ``name``, ``proof``, and ``proof_evidence`` are consumed here.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# runtime/scripts/proof_status.py -> repo root is three parents up.
ROOT = Path(__file__).resolve().parent.parent.parent

PROOF_TIERS = ("doctrine-only", "self-run", "external-run")
# Tiers that must carry a resolvable evidence report; doctrine-only is exempt.
TIERS_REQUIRING_EVIDENCE = {"self-run", "external-run"}


def parse_frontmatter(text):
    """Minimal YAML-frontmatter reader (ported from scripts/validate.py).

    Returns (data, error). Only flat scalar keys are needed here.
    """
    if not text.startswith("---"):
        return None, "missing opening ---"
    end = text.find("\n---", 4)
    if end == -1:
        return None, "missing closing ---"
    block = text[3:end].strip()
    data = {}
    current_key = None
    multiline_indicator = None
    multiline_value = []
    for line in block.split("\n"):
        if multiline_indicator and (line.startswith("  ") or line.strip() == ""):
            multiline_value.append(line[2:] if line.startswith("  ") else line)
            continue
        if multiline_indicator:
            data[current_key] = " ".join(l.strip() for l in multiline_value if l.strip())
            multiline_indicator = None
            multiline_value = []
        m = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val in (">", "|", ">-", "|-"):
                current_key = key
                multiline_indicator = val
                multiline_value = []
            elif val.startswith('"') and val.endswith('"'):
                data[key] = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                data[key] = val[1:-1]
            elif val == "":
                current_key = key
                data[key] = "<object>"
            else:
                data[key] = val
    if multiline_indicator:
        data[current_key] = " ".join(l.strip() for l in multiline_value if l.strip())
    return data, None


def collect(skills_dir, root):
    """Return one record per ``skills/*/SKILL.md``, one per mission, sorted by dir name.

    Each record: name, proof, proof_evidence (str or None), evidence_resolves (bool),
    plus dir (the mission directory name) and any parse error.
    """
    records = []
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        md = skill_dir / "SKILL.md"
        if not md.is_file():
            continue
        rec = {
            "dir": skill_dir.name,
            "name": None,
            "proof": None,
            "proof_evidence": None,
            "evidence_resolves": False,
            "error": None,
        }
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as err:
            rec["error"] = f"unreadable: {err}"
            records.append(rec)
            continue
        data, err = parse_frontmatter(text)
        if err:
            rec["error"] = err
            records.append(rec)
            continue
        rec["name"] = data.get("name")
        rec["proof"] = data.get("proof")
        evidence = data.get("proof_evidence")
        if evidence and evidence != "<object>":
            rec["proof_evidence"] = evidence
            rec["evidence_resolves"] = (root / evidence).is_file()
        records.append(rec)
    return records


def rollup(records):
    """Count of missions per proof tier plus total (AC-2)."""
    counts = {tier: 0 for tier in PROOF_TIERS}
    for rec in records:
        if rec["proof"] in counts:
            counts[rec["proof"]] += 1
    counts["total"] = len(records)
    return counts


def check_failures(records):
    """Missions whose tier requires evidence but whose evidence is missing/unresolvable (AC-3)."""
    failures = []
    for rec in records:
        if rec["proof"] in TIERS_REQUIRING_EVIDENCE:
            if not rec["proof_evidence"] or not rec["evidence_resolves"]:
                failures.append(rec)
    return failures


def format_report(records):
    lines = []
    name_w = max((len(r["name"] or r["dir"]) for r in records), default=4)
    tier_w = max(len(t) for t in PROOF_TIERS)
    for rec in records:
        name = rec["name"] or rec["dir"]
        tier = rec["proof"] or "?"
        evidence = rec["proof_evidence"] or "—"
        if rec["proof_evidence"]:
            mark = "ok" if rec["evidence_resolves"] else "MISSING"
        else:
            mark = "—"
        lines.append(f"{name:<{name_w}}  {tier:<{tier_w}}  [{mark:<7}] {evidence}")
    counts = rollup(records)
    lines.append("")
    lines.append("coverage rollup:")
    for tier in PROOF_TIERS:
        lines.append(f"  {tier:<{tier_w}}  {counts[tier]}")
    lines.append(f"  {'total':<{tier_w}}  {counts['total']}")
    return "\n".join(lines)


def json_records(records):
    """Per-mission machine-readable array (AC-3, --json)."""
    return [
        {
            "name": rec["name"],
            "proof": rec["proof"],
            "proof_evidence": rec["proof_evidence"],
            "evidence_resolves": rec["evidence_resolves"],
        }
        for rec in records
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Proof-posture reporter and CI lens over the mission catalog."
    )
    ap.add_argument("--json", action="store_true", help="emit per-mission records as a JSON array")
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero iff a mission above doctrine-only lacks resolvable proof_evidence",
    )
    ap.add_argument("--root", default=None, help="repo root (default: inferred from this script)")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else ROOT
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        print(f"no skills/ directory under {root}", file=sys.stderr)
        return 1

    records = collect(skills_dir, root)

    if args.json:
        print(json.dumps(json_records(records), indent=2))
    else:
        print(format_report(records))

    if args.check:
        failures = check_failures(records)
        if failures:
            for rec in failures:
                name = rec["name"] or rec["dir"]
                why = "no proof_evidence" if not rec["proof_evidence"] else "unresolvable proof_evidence"
                print(
                    f"FAIL: {name} ({rec['proof']}) — {why}: {rec['proof_evidence'] or '—'}",
                    file=sys.stderr,
                )
            print(
                f"proof-status: {len(failures)} mission(s) above doctrine-only missing evidence",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
