#!/usr/bin/env python3
"""
Validate orca-fleet against its own architecture (see ARCHITECTURE.md).

Two things are checked:

1. Every mission (skills/<name>/SKILL.md) is a valid agentskills.io skill:
   - name: 1-64 chars, lowercase letters/digits/hyphens, matches its folder
   - description: 1-1024 chars
   - compatibility: optional, 1-500 chars
   - proof: required — doctrine-only | self-run | external-run. Advancing past
     doctrine-only requires proof_evidence: a run-report path that exists. Ten
     unproven missions presented as proven is how the predecessor repo died;
     the honesty is machine-checked here.
   - instruction budget: missions ≤ 130 lines, playbooks ≤ 90, runtime policies
     ≤ 160. Doctrine creep gets caught by CI, not by a postmortem. Raise a cap
     only by deliberate edit with a reason in the commit.

2. The three-layer separation holds:
   - Only skills/ contains SKILL.md. A SKILL.md under playbooks/ or runtime/ would
     republish an internal protocol as a discoverable skill — the exact routing
     collision this repo exists to remove.
   - Every name in a mission's "Composes …; rides …" clause resolves to a real
     playbook or runtime policy, and every mission has at least one such
     machine-checkable name (a clause with no backticked names silently no-ops).
     The clause is scanned to the end of its paragraph — an abbreviation ("e.g. ")
     or a capitalized "Rides" cannot truncate or escape the scan.
   - Every `<name>.md` mention in a mission AND in every playbook/runtime policy
     resolves — a rename must not dangle anywhere. Uppercase docs (ARCHITECTURE.md,
     SKILL.md) are exempt; URLs are ignored; case/underscore typos of real protocol
     names and path-prefixed references are flagged.

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
PROOF_VALUES = {"doctrine-only", "self-run", "external-run"}
# Mutating missions land code; they must ride the SHA-bound evidence protocol so
# completion is never graded on worker narration. Report-only / planning /
# diagnosis missions bind evidence differently and are not in this set.
MUTATING_MISSIONS = {
    "ship-it",
    "clean-sweep",
    "harden-it",
    "speed-it",
    "modernize-it",
    "prove-it",
    "deflake-it",
}
# Instruction budget (lines, whole file). The predecessor's mandatory instruction
# surface hit ~42K tokens with no counterpressure; these caps are the counterpressure.
MISSION_MAX_LINES = 130
PLAYBOOK_MAX_LINES = 90
RUNTIME_MAX_LINES = 160
# A mission declares what it composes in a "Composes ... rides ..." clause. Capture
# each such clause through the END of its paragraph — terminating at the first
# sentence break lets an abbreviation ("e.g. ") truncate the clause and smuggle
# dangling names past the check — and verify every backtick name in it resolves.
# RIDES (all-caps) is accepted alongside Rides/rides, matching COMPOSES handling.
COMPOSE_CLAUSE_RE = re.compile(
    r"\b(?:Composes|COMPOSES|Rides|RIDES|rides)\b\s+(.+?)(?:\n\n|\Z)", re.DOTALL
)
# Mutator evidence-manifest must appear in a composition rides clause, not mid-prose
# ("the worker rides `evidence-manifest` out of turn") and not a mere Composes mention
# ("does not ride `evidence-manifest`"). Accept only rides after `;`, after a newline,
# or at the start of the document — the forms missions actually write.
RIDES_CLAUSE_RE = re.compile(
    r"(?:(?<=;)|(?<=\n)|(?<=\A))\s*(?:Rides|RIDES|rides)\b\s+(.+?)(?:\n\n|\Z)",
    re.DOTALL,
)
BACKTICK_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
# Any lowercase `<name>.md` mention (pipeline text, parentheticals) must also resolve;
# basenames that fail NAME_RE (ARCHITECTURE.md, SKILL.md) are exempt.
MD_TOKEN_RE = re.compile(r"[\w./-]+\.md\b")


def md_ref_errors(text, protocols):
    """Errors for every `<name>.md` token that should be a protocol reference.

    URL tokens (https://…/x.md) are external links, not protocol refs. Uppercase
    docs (ARCHITECTURE.md, SKILL.md) are exempt via NAME_RE — but a case or
    underscore typo of a REAL protocol name must not ride that exemption, and a
    path-prefixed form must not pass on basename alone (the path can lie about
    where the file lives) — protocols are referenced by bare name.
    """
    errs = []
    for m in MD_TOKEN_RE.finditer(text):
        tok = m.group(0)
        if tok.startswith("//") or text[max(0, m.start() - 1):m.start()] == ":":
            continue  # URL — an external link, not a protocol reference
        stem = tok.rsplit("/", 1)[-1][: -len(".md")]
        canon = stem.lower().replace("_", "-")
        if NAME_RE.match(stem):
            if "/" in tok:
                # A path-prefixed PROTOCOL name is the wrong-directory lie
                # (playbooks/sandbox-policy.md). A path to anything else (a run
                # report, a doc) is legitimate — but it must exist.
                if stem in protocols or canon in protocols:
                    errs.append(
                        f"path-prefixed reference: {tok} — reference protocols by "
                        f"bare name (`{stem}` or {stem}.md)"
                    )
                elif not (ROOT / tok).exists():
                    errs.append(f"dangling path: {tok} does not exist")
            elif stem not in protocols:
                errs.append(f"dangling reference: {tok} names no playbook or runtime policy")
        elif canon in protocols:
            errs.append(
                f"case/underscore typo: {tok} — the protocol file is {canon}.md"
            )
    return errs


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
        if c == "<object>":
            errors.append("compatibility must be a string (1-500 chars), got a mapping")
        elif not (1 <= len(c) <= 500):
            errors.append(f"compatibility length {len(c)} out of 1-500")

    # proof status: honest by construction — no mission presents itself as proven
    # without a run report on disk
    proof = data.get("proof")
    if proof is None:
        errors.append("missing 'proof' field (doctrine-only | self-run | external-run)")
    elif proof not in PROOF_VALUES:
        errors.append(f"proof '{proof}' invalid (want one of {sorted(PROOF_VALUES)})")
    elif proof != "doctrine-only":
        evidence = data.get("proof_evidence", "")
        if not evidence or not (ROOT / evidence).exists():
            errors.append(
                f"proof '{proof}' requires proof_evidence: a run-report path that exists"
            )

    lines = len(text.splitlines())
    if lines > MISSION_MAX_LINES:
        errors.append(
            f"instruction budget: {lines} lines > {MISSION_MAX_LINES} (mission cap)"
        )

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
    ride_refs = [
        ref
        for clause in RIDES_CLAUSE_RE.findall(text)
        for ref in BACKTICK_RE.findall(clause)
    ]
    if name in MUTATING_MISSIONS and "evidence-manifest" not in ride_refs:
        errors.append(
            "mutating mission must ride `evidence-manifest` in a rides clause "
            "(SHA-bound definition of done; a Composes mention alone does not count)"
        )

    # every lowercase `<name>.md` mention must resolve (catches renames outside the clause)
    errors.extend(md_ref_errors(text, protocols))

    return errors


def check_protocol_doc_refs(protocols):
    """Playbooks and runtime policies cross-reference each other by `<name>.md`;
    a rename or deletion must not dangle there either (missions are covered by
    validate_skill — without this pass, only skills/ is guarded). The instruction
    budget is enforced on the same walk."""
    failures = []
    caps = {PLAYBOOKS_DIR: PLAYBOOK_MAX_LINES, RUNTIME_DIR: RUNTIME_MAX_LINES}
    for d in (PLAYBOOKS_DIR, RUNTIME_DIR):
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            for e in md_ref_errors(text, protocols):
                failures.append(f"{f.relative_to(ROOT)}: {e}")
            lines = len(text.splitlines())
            if lines > caps[d]:
                failures.append(
                    f"{f.relative_to(ROOT)}: instruction budget: {lines} lines > "
                    f"{caps[d]} ({d.name} cap)"
                )
    return failures


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

    doc_failures = check_protocol_doc_refs(protocols)
    if doc_failures:
        all_passed = False
        print("\nFAIL protocol cross-references — dangling refs in playbooks/runtime:")
        for failure in doc_failures:
            print(f"   - {failure}")

    print()
    if all_passed:
        print(f"All {total} missions valid; three-layer separation holds.")
        return 0
    print("Validation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
