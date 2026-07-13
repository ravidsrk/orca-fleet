#!/usr/bin/env python3
"""
Validate orca-fleet against its own architecture (see ARCHITECTURE.md).

Two things are checked:

1. Every mission (skills/<name>/SKILL.md) is a valid agentskills.io skill:
   - name: 1-64 chars, lowercase letters/digits/hyphens, matches its folder
   - description: 1-1024 chars
   - compatibility: optional, 1-500 chars

2. The three-layer separation holds:
   - Only skills/ contains SKILL.md. A SKILL.md under playbooks/ or runtime/ would
     republish an internal protocol as a discoverable skill — the exact routing
     collision this repo exists to remove.
   - Every name in a mission's "Composes …; rides …" clause resolves to a real
     playbook or runtime policy, and every mission has at least one such
     machine-checkable name (a clause with no backticked names silently no-ops).
   - Every lowercase `<name>.md` mention anywhere in a mission resolves too —
     pipeline text references protocols outside the clause, and a rename must not
     dangle there. Uppercase docs (ARCHITECTURE.md, SKILL.md) are exempt.

Exit code: 0 if all valid, 1 if any failure.

Spec: https://agentskills.io/specification
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
PLAYBOOKS_DIR = ROOT / "playbooks"
RUNTIME_DIR = ROOT / "runtime"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# A mission declares what it composes in a "Composes ... rides ..." clause. Capture
# each such clause (up to the first sentence break) and check every backtick name in
# it resolves to a real playbook or runtime policy — this catches typos and renames.
COMPOSE_CLAUSE_RE = re.compile(r"(?:Composes|COMPOSES|rides)\s+(.+?)(?:\.\s|\.$|\n\n)", re.DOTALL)
BACKTICK_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
# Any lowercase `<name>.md` mention (pipeline text, parentheticals) must also resolve;
# basenames that fail NAME_RE (ARCHITECTURE.md, SKILL.md) are exempt.
MD_TOKEN_RE = re.compile(r"[\w./-]+\.md\b")


def known_protocol_names():
    names = set()
    for d in (PLAYBOOKS_DIR, RUNTIME_DIR):
        if d.exists():
            names |= {p.stem for p in d.glob("*.md")}
    return names


def parse_frontmatter(text):
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


def validate_skill(skill_dir, protocols):
    errors = []
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["missing SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    data, err = parse_frontmatter(text)
    if err:
        return [f"frontmatter parse error: {err}"]

    if "name" not in data:
        errors.append("missing 'name' field")
    else:
        n = data["name"]
        if not (1 <= len(n) <= 64):
            errors.append(f"name length {len(n)} out of 1-64")
        if not NAME_RE.match(n):
            errors.append(f"name '{n}' invalid (lowercase letters/digits/hyphens only)")
        if n != name:
            errors.append(f"name '{n}' does not match folder '{name}'")

    if "description" not in data:
        errors.append("missing 'description' field")
    elif not (1 <= len(data["description"]) <= 1024):
        errors.append(f"description length {len(data['description'])} out of 1-1024")

    if "compatibility" in data:
        c = data["compatibility"]
        if c != "<object>" and not (1 <= len(c) <= 500):
            errors.append(f"compatibility length {len(c)} out of 1-500")

    # architecture: every playbook/runtime a mission says it Composes/rides must exist,
    # and there must be at least one such name — a clause the regex can't see into
    # (bare directory pointers, prose) would otherwise pass with zero checks.
    clause_refs = [
        ref
        for clause in COMPOSE_CLAUSE_RE.findall(text)
        for ref in BACKTICK_RE.findall(clause)
    ]
    for ref in clause_refs:
        if ref not in protocols:
            errors.append(
                f"dangling composition: `{ref}` names no playbook or runtime policy"
            )
    if not clause_refs:
        errors.append(
            "no machine-checkable composition: the Composes/rides clause must name "
            "at least one playbook or runtime policy in backticks"
        )

    # every lowercase `<name>.md` mention must resolve (catches renames outside the clause)
    for tok in MD_TOKEN_RE.findall(text):
        stem = tok.rsplit("/", 1)[-1][: -len(".md")]
        if NAME_RE.match(stem) and stem not in protocols:
            errors.append(f"dangling reference: {tok} names no playbook or runtime policy")

    return errors


def check_layer_separation():
    """Only skills/ may contain SKILL.md — playbooks and runtime are not discoverable."""
    leaks = []
    for layer in (PLAYBOOKS_DIR, RUNTIME_DIR):
        if layer.exists():
            leaks += [str(p.relative_to(ROOT)) for p in layer.rglob("SKILL.md")]
    return leaks


def main():
    if not SKILLS_DIR.exists():
        print(f"skills/ not found at {SKILLS_DIR}", file=sys.stderr)
        return 2

    protocols = known_protocol_names()
    all_passed = True
    total = 0
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith((".", "_")):
            continue
        total += 1
        errors = validate_skill(skill_dir, protocols)
        if errors:
            all_passed = False
            print(f"FAIL {skill_dir.name}")
            for e in errors:
                print(f"   - {e}")
        else:
            print(f"ok   {skill_dir.name}")

    leaks = check_layer_separation()
    if leaks:
        all_passed = False
        print("\nFAIL layer separation — SKILL.md found outside skills/:")
        for leak in leaks:
            print(f"   - {leak} (playbooks/runtime are callable, not discoverable)")

    print()
    if all_passed:
        print(f"All {total} missions valid; three-layer separation holds.")
        return 0
    print("Validation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
