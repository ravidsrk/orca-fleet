#!/usr/bin/env python3
"""Build self-contained missions for installers that copy skill directories.

The three-layer separation is why the catalog works: a mission references its
playbooks and runtime policies by BARE NAME, and they live two directories up.
A symlink install preserves that. A plugin install copies the whole repo, so it
preserves it too. An installer that copies `skills/<name>/` *out* of the tree
severs every one of those references, and the mission then runs half-blind with
nothing saying so (docs/reviews/2026-09-10-review.md §8 P2-18).

This makes a distribution tree where each mission carries its own copies:

    dist/skills/<name>/SKILL.md
    dist/skills/<name>/references/<protocol>.md      one per composed/ridden doc
    dist/skills/<name>/references/ARCHITECTURE.md    root docs it links
    dist/skills/<name>/runtime/scripts/             executable runtime + helpers
    dist/skills/<name>/runtime/*.json               runtime data
    dist/skills/<name>/docs/runs/TEMPLATE.md        mandatory run-report template

and rewrites the SKILL.md so nothing points outside the mission directory:
`](../../ARCHITECTURE.md)` becomes `](references/ARCHITECTURE.md)`, and one line
points at `references/README.md`, the generated index naming each protocol's local
copy. Bare names in the Composes/rides clause are left alone — they are the
mission's vocabulary, not paths — and that index is what resolves them.

`dist/` is generated, never committed: vendoring 21 copies of the doctrine tree
into git would make every runtime edit a 21-file diff and the copies would rot
between edits. Build it at release time, or before running a copy installer.

    python3 scripts/bundle.py                 # build dist/
    python3 scripts/bundle.py --out /tmp/x    # build somewhere else
    python3 scripts/bundle.py --check         # build to a temp dir and verify only

Exit: 0 built and verified · 1 a reference could not be resolved · 2 could not run.
"""
import argparse
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

_spec = importlib.util.spec_from_file_location("_validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)

# `](../../X.md)` and `](../../dir/X.md)` — the outbound links the rewriter knows how to vendor.
OUTBOUND_LINK_RE = re.compile(r"\]\((?:\.\./)+([A-Za-z0-9_./-]+\.md)(#[^)]*)?\)")
# Every link that leaves the directory, whatever its extension. The rewriter only vendors `.md`,
# but the CHECK has to see the rest: `](../../runtime/scripts/verify.py)` was neither rewritten nor
# flagged, so dist/ could ship a link pointing nowhere with --check green (#316).
OUTBOUND_ANY_RE = re.compile(r"\]\((?:\.\./)+([A-Za-z0-9_./-]+)(#[^)]*)?\)")
# A relative link that does NOT climb out with `../`. A vendored doc keeps the repo-root-relative
# links it was written with — `](runtime/evidence-manifest.md)` — and from `references/` those
# resolve under `references/`, where nothing was copied. They escape nothing, so OUTBOUND_ANY_RE
# never saw them, and 56 of them shipped dead while --check stayed green (PR #308 review, P1).
RELATIVE_LINK_RE = re.compile(
    r"\[([^\]]*)\]\((?!https?:|mailto:|#|/|\.\./)([A-Za-z0-9_./-]+)(#[^)]*)?\)")
REFERENCES = "references"
# The distribution's runtime interface, independent of what survived in the input tree.
# Ship additional runtime files too, but never let discovery shrink this required floor.
REQUIRED_RUNTIME = tuple(f"runtime/scripts/{name}" for name in (
    "decisions.py", "deny-hook.sh", "diff_scope.py", "dispatch-sign.py", "ed25519.py",
    "egress.py", "evidence-run.py", "floor_guard.py", "guard_text.py", "hitl-loop.template.sh",
    "inventory.py", "pm.py", "preflight.py", "proof_status.py", "run_report.py",
    "sandbox_doctor.py", "spawn_worker.sh", "verify-gate.sh", "verify.py", "wtree.sh",
)) + ("runtime/one-way-doors.json", "runtime/pins.json")
# build-change's mandatory reporting input is outside the protocol directories.
SUPPORT_DOCS = ("docs/runs/TEMPLATE.md",)


def missing_inputs(protocols):
    """Check declared requirements before discovered files can define the inventory."""
    problems = [f"missing required source: {name}" for name in (*REQUIRED_RUNTIME, *SUPPORT_DOCS)
                if not (ROOT / name).is_file()]
    for path in [*SKILLS_DIR.glob("*/SKILL.md"), *(ROOT / "playbooks").glob("*.md"),
                 *(ROOT / "runtime").glob("*.md")]:
        for name in sorted(validate.explicit_protocol_refs(path.read_text()) - protocols):
            problems.append(f"{path.relative_to(ROOT)}: missing required protocol: {name}.md")
    return problems


def protocol_docs(text, protocols):
    """Resolve the protocol closure, including calls inside other protocols.

    Playbooks call each other with bare backticks outside Composes/rides clauses.
    Include conditional calls too: they may become mandatory later in a run.
    """
    found = {}
    pending = [text]
    while pending:
        current = pending.pop()
        names = validate.explicit_protocol_refs(current)
        names |= set(re.findall(r"`([a-z][a-z0-9-]+)`", current))
        names |= {Path(m.group(2)).stem for m in RELATIVE_LINK_RE.finditer(current)}
        for name in sorted(names & protocols - found.keys()):
            for base in (ROOT / "playbooks", ROOT / "runtime"):
                doc = base / f"{name}.md"
                if doc.is_file():
                    found[name] = doc
                    pending.append(doc.read_text(encoding="utf-8"))
                    break
    return found


def root_docs(text):
    """{filename: source path} for every repo-root doc the SKILL.md links."""
    found = {}
    for match in OUTBOUND_LINK_RE.finditer(text):
        target = match.group(1)
        source = (ROOT / target).resolve()
        try:
            source.relative_to(ROOT)
        except ValueError:
            continue
        if source.is_file():
            found[Path(target).name] = source
    return found


def rewrite(text, mission, protocols):
    """SKILL.md with outbound links pointed at references/, plus one pointer line.

    The index itself goes in `references/README.md`, not here: the mission body is
    budget-capped (ARCHITECTURE.md "Instruction budget"), and a bundle that blew
    that cap to explain itself would be its own kind of dishonest.
    """
    def local(match):
        anchor = match.group(2) or ""
        return f"]({REFERENCES}/{Path(match.group(1)).name}{anchor})"

    out = OUTBOUND_LINK_RE.sub(local, text)
    if protocol_docs(text, protocols):
        out = out.rstrip("\n") + (
            f"\n\nBundled copy of `{mission}`: every protocol named above is vendored in "
            f"[`{REFERENCES}/`]({REFERENCES}/README.md), not two directories up.\n"
        )
    return out


def reference_index(mission, names):
    """The `references/README.md` a bundled mission ships next to its copies."""
    rows = "\n".join(f"- `{name}` → [{name}.md]({name}.md)" for name in names)
    return (
        f"# `{mission}` bundled references\n\n"
        f"Generated by `scripts/bundle.py`. In the repository these live in `playbooks/` and\n"
        f"`runtime/`, two directories above the mission. An installer that copies skill\n"
        f"directories out of the tree severs that path, so the copies live here instead —\n"
        f"resolve bare protocol names throughout the mission and its protocols against this list.\n\n"
        "## Installed runtime\n\n"
        "Set `ORCA_FLEET_ROOT` to the absolute installed mission directory (the directory\n"
        "containing SKILL.md). Run commands from the PROJECT repository being worked on;\n"
        "keep manifests, contracts and other project paths relative to that repository.\n"
        "For every `runtime/scripts/<file>` invocation in these protocols, use\n"
        '`"$ORCA_FLEET_ROOT/runtime/scripts/<file>"` instead. Runtime JSON lives under\n'
        '`"$ORCA_FLEET_ROOT/runtime/"`; helpers locate it relative to themselves.\n'
        "Read the mandatory `docs/runs/TEMPLATE.md` from\n"
        '`"$ORCA_FLEET_ROOT/docs/runs/TEMPLATE.md"` ([run-report template](../docs/runs/TEMPLATE.md));\n'
        "write the filled report and its evidence into the PROJECT repository.\n"
        "Follow its target-project gates and integrity inventory procedure. The separate\n"
        "catalog proof-promotion section applies only in an orca-fleet catalog clone;\n"
        "recording an external run does not promote the installed mission's proof tier.\n"
        "Python 3, a POSIX shell and git are host prerequisites; live operations also\n"
        "require the external tools and permissions named by their protocols (Orca, gh, etc.).\n\n"
        "```sh\n"
        'python3 "$ORCA_FLEET_ROOT/runtime/scripts/verify.py" --help\n'
        'python3 "$ORCA_FLEET_ROOT/runtime/scripts/evidence-run.py" --help\n'
        'python3 "$ORCA_FLEET_ROOT/runtime/scripts/preflight.py" --help\n'
        "```\n\n"
        "[Payload inventory](bundle-files.json) lists every required installed file.\n\n"
        f"{rows}\n"
    )


def runtime_files():
    """Ship the runtime as one unit so lazy imports and shell helpers stay local."""
    return [path for path in sorted((ROOT / "runtime").rglob("*"))
            if path.is_file() and path.suffix in {".py", ".sh", ".json"}
            and "__pycache__" not in path.parts]


def build(out_dir):
    """Write the distribution tree. Returns (missions built, unresolved refs)."""
    protocols = validate.known_protocol_names()
    problems = missing_inputs(protocols)
    if problems:
        return 0, problems
    skills_out = Path(out_dir) / "skills"
    if skills_out.exists():
        shutil.rmtree(skills_out)
    built, problems = 0, []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or skill_dir.name.startswith((".", "_")) or not skill_md.is_file():
            continue
        text = skill_md.read_text(encoding="utf-8")
        target = skills_out / skill_dir.name
        (target / REFERENCES).mkdir(parents=True)
        inventory = {"SKILL.md"}
        for extra in skill_dir.iterdir():
            if extra.name == "SKILL.md":
                continue
            inventory.update(path.relative_to(skill_dir).as_posix()
                             for path in (extra.rglob("*") if extra.is_dir() else [extra])
                             if path.is_file())
            (shutil.copytree if extra.is_dir() else shutil.copy2)(extra, target / extra.name)
        docs = protocol_docs(text, protocols)
        for name, source in docs.items():
            inventory.add(f"{REFERENCES}/{name}.md")
            shutil.copy2(source, target / REFERENCES / f"{name}.md")
        if docs:
            inventory.add(f"{REFERENCES}/README.md")
            (target / REFERENCES / "README.md").write_text(
                reference_index(skill_dir.name, sorted(docs)), encoding="utf-8"
            )
        for name, source in root_docs(text).items():
            inventory.add(f"{REFERENCES}/{name}")
            shutil.copy2(source, target / REFERENCES / name)
        for source in [*runtime_files(), *(ROOT / name for name in SUPPORT_DOCS)]:
            inventory.add(source.relative_to(ROOT).as_posix())
            destination = target / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        (target / "SKILL.md").write_text(rewrite(text, skill_dir.name, protocols), encoding="utf-8")
        # Record intended copies, not what survived copying: a dropped helper must fail --check.
        (target / REFERENCES / "bundle-files.json").write_text(
            json.dumps(sorted(inventory), indent=2) + "\n", encoding="utf-8")
        relink_vendored(target)   # after every copy: it needs to know what ended up beside it
        problems.extend(dangling(target))
        built += 1
    return built, problems


def relink_vendored(mission_dir):
    """Re-point a vendored doc's repo-root-relative links, or de-link them (PR #308 review, P1).

    The copies under `references/` are verbatim, so they still say `](runtime/evidence-manifest.md)`
    — a path that was right in the repository and resolves to nothing beside the copy. Where the
    same document was vendored too, the link becomes its bare name; where it was not, the link
    becomes plain text naming the repository path, because a dead link is worse than a sentence
    telling the reader where to look."""
    refs = mission_dir / REFERENCES
    if not refs.is_dir():
        return
    available = {path.name for path in refs.glob("*.md")}
    for path in [*sorted(refs.glob("*.md")), *(mission_dir / name for name in SUPPORT_DOCS
                                             if (mission_dir / name).is_file())]:
        text = path.read_text(encoding="utf-8")

        def fix(match, _dir=path.parent):
            label, target, anchor = match.group(1), match.group(2), match.group(3) or ""
            if (_dir / target).exists():
                return match.group(0)
            name = Path(target).name
            if _dir == refs and name in available:
                return f"[{label}]({name}{anchor})"
            if _dir != refs:
                target = (_dir / target).relative_to(mission_dir).as_posix()
            if label.strip().strip("`") in (target, name):
                return f"`{target}`"   # the label WAS the path; saying it twice helps nobody
            return f"{label} (`{target}` in the orca-fleet repository)"

        rewritten = RELATIVE_LINK_RE.sub(fix, text)
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")


def dangling(mission_dir):
    """Links in a bundled mission that still leave its directory, or point at nothing.

    Check every markdown file, not just SKILL.md (#316), after relinking. An upward link
    within the installed mission is valid (the reporting template is outside references/);
    a missing target or escape is not. Check all extensions, including runtime scripts."""
    problems = []
    inventory = mission_dir / REFERENCES / "bundle-files.json"
    if inventory.exists():
        try:
            files = json.loads(inventory.read_text(encoding="utf-8"))
            if not isinstance(files, list) or not all(isinstance(p, str) for p in files):
                raise ValueError("expected a list of payload paths")
            for relative in files:
                path = (mission_dir / relative).resolve()
                if not path.is_relative_to(mission_dir.resolve()) or not path.is_file():
                    problems.append(f"{mission_dir.name}: missing bundle payload: {relative}")
        except (OSError, ValueError) as error:
            problems.append(f"{mission_dir.name}: invalid payload inventory: {error}")
    for path in sorted(mission_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(mission_dir).as_posix()
        for match in OUTBOUND_ANY_RE.finditer(text):
            target = match.group(0)[2:-1].split("#", 1)[0]
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(mission_dir.resolve()) or not resolved.is_file():
                problems.append(f"{mission_dir.name}: link escapes the bundle or is missing "
                                f"({where}): {match.group(0)}")
        for match in re.finditer(rf"\]\({REFERENCES}/([A-Za-z0-9_.-]+\.md)(?:#[^)]*)?\)", text):
            if not (mission_dir / REFERENCES / match.group(1)).is_file():
                problems.append(f"{mission_dir.name}: {REFERENCES}/{match.group(1)} was not vendored")
        for match in RELATIVE_LINK_RE.finditer(text):
            if not (path.parent / match.group(2)).exists():
                problems.append(f"{mission_dir.name}: dead relative link "
                                f"({where}): {match.group(0)}")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="bundle.py",
        description="Vendor each mission's referenced docs so copy installers keep working.",
        epilog="exit 0 built · 1 unresolved reference · 2 could-not-run",
    )
    parser.add_argument("--out", default=str(ROOT / "dist"), help="output directory (default dist/)")
    parser.add_argument("--check", action="store_true",
                        help="build into a temp dir and verify, writing nothing durable")
    args = parser.parse_args(argv)

    if not SKILLS_DIR.is_dir():
        print(f"skills/ not found at {SKILLS_DIR}", file=sys.stderr)
        return 2

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            built, problems = build(tmp)
    else:
        built, problems = build(args.out)
    for problem in problems:
        print(f"FAIL {problem}", file=sys.stderr)
    if problems:
        return 1
    where = "a temp dir" if args.check else args.out
    print(f"bundle: {built} self-contained mission(s) in {where}; no reference leaves its directory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
