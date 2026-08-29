#!/usr/bin/env python3
"""
Validate orca-fleet against its own architecture (see ARCHITECTURE.md).

Three things are checked:

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

3. The eval layer (ported from marketingskills) is self-consistent:
   - `evals/routing.json` is valid JSON and has at least one positive example per
     mission.
   - Every `skills/<name>/evals/evals.json` is valid JSON, its `skill_name` matches
     the folder, and each eval has the required fields.

Exit code: 0 if all valid, 1 if any failure.

Spec: https://agentskills.io/specification
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Load the eval validator so `scripts/validate.py` also catches broken eval JSON.
_eval_spec = importlib.util.spec_from_file_location("_eval_validator", ROOT / "scripts" / "eval.py")
_eval_validator = importlib.util.module_from_spec(_eval_spec)
_eval_spec.loader.exec_module(_eval_validator)
SKILLS_DIR = ROOT / "skills"
PLAYBOOKS_DIR = ROOT / "playbooks"
RUNTIME_DIR = ROOT / "runtime"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PROOF_VALUES = {"doctrine-only", "self-run", "external-run"}
AUTONOMY_VALUES = {"L0", "L1", "L2", "L3", "L4", "L5"}
# Mutating missions land code; they must ride the SHA-bound evidence protocol so
# completion is never graded on worker narration. Report-only / planning /
# diagnosis missions bind evidence differently and are not in this set.
MUTATING_MISSIONS = {
    "ship-it",
    "clean-sweep",
    "oss-contribute",
    "harden-it",
    "speed-it",
    "modernize-it",
    "prove-it",
    "deflake-it",
    "access-it",
}
# Instruction budget (lines, whole file). The predecessor's mandatory instruction
# surface hit ~42K tokens with no counterpressure; these caps are the counterpressure.
MISSION_MAX_LINES = 130
PLAYBOOK_MAX_LINES = 90
RUNTIME_MAX_LINES = 160
# A single 166KB line beats a line-count cap; a byte budget (generous headroom over the largest
# real file) also catches instruction surface packed into a few very long lines.
_MAX_BYTES_PER_LINE = 240
MISSION_MAX_BYTES = MISSION_MAX_LINES * _MAX_BYTES_PER_LINE
PLAYBOOK_MAX_BYTES = PLAYBOOK_MAX_LINES * _MAX_BYTES_PER_LINE
RUNTIME_MAX_BYTES = RUNTIME_MAX_LINES * _MAX_BYTES_PER_LINE
# A mission declares what it composes in a "Composes ... rides ..." clause. Capture
# each such clause through the END of its paragraph — terminating at the first
# sentence break lets an abbreviation ("e.g. ") truncate the clause and smuggle
# dangling names past the check — and verify every backtick name in it resolves.
# RIDES (all-caps) is accepted alongside Rides/rides, matching COMPOSES handling.
COMPOSE_CLAUSE_RE = re.compile(
    r"\b(?:Composes|COMPOSES|composes|Rides|RIDES|rides)\b\s+(.+?)(?:\n\n|\Z)", re.DOTALL
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


def read_text_safe(path):
    """Read UTF-8 text. Return (text, None) or (None, error). Never raises.

    One corrupt SKILL.md must not abort validation of the rest of the catalog
    (issue #71 / TODOS.md). Same guard for playbooks/ and runtime/.
    """
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "unreadable: not valid UTF-8"
    except OSError as err:
        return None, f"unreadable: {err}"


def validate_skill(skill_dir, protocols):
    errors = []
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["missing SKILL.md"]

    text, read_err = read_text_safe(skill_md)
    if read_err:
        return [read_err]
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
        ev_path = (ROOT / evidence).resolve() if evidence else None
        runs_dir = (ROOT / "docs" / "runs").resolve()
        if (
            not ev_path
            or not ev_path.is_relative_to(runs_dir)
            or ev_path.suffix != ".md"
            or not ev_path.is_file()
        ):
            errors.append(
                f"proof '{proof}' requires proof_evidence: a docs/runs/*.md run report that exists"
            )
        else:
            # content correlation: the report must be THIS mission's run — not merely a file that
            # exists, and not another mission's report that mentions this one in prose (#133). The
            # coordinator names a run report after its mission, so require the name both as a
            # hyphen-delimited token in the filename AND in the report body.
            name = data.get("name") or ""
            named_in_file = bool(name and re.search(rf"(?:^|-){re.escape(name)}(?:-|$)", ev_path.stem))
            report, _ = read_text_safe(ev_path)  # None on unreadable / non-UTF-8 — never raises
            named_in_body = bool(name and report and name in report)
            if not (named_in_file and named_in_body):
                errors.append(
                    f"proof '{proof}': proof_evidence {evidence} must be mission '{name}'s run report "
                    f"— name the mission in the filename (docs/runs/<date>-{name}-*.md) and the body"
                )

    # autonomy level (Osmani L0-L5): a first-class, machine-readable claim sibling to
    # proof — the level a mission safely runs at, gated by how cheaply it is verified.
    autonomy = data.get("autonomy")
    if autonomy is None:
        errors.append("missing 'autonomy' field (L0-L5)")
    elif autonomy not in AUTONOMY_VALUES:
        errors.append(f"autonomy '{autonomy}' invalid (want one of {sorted(AUTONOMY_VALUES)})")

    lines = len(text.splitlines())
    if lines > MISSION_MAX_LINES:
        errors.append(
            f"instruction budget: {lines} lines > {MISSION_MAX_LINES} (mission cap)"
        )
    nbytes = len(text.encode("utf-8"))
    if nbytes > MISSION_MAX_BYTES:
        errors.append(
            f"instruction budget: {nbytes} bytes > {MISSION_MAX_BYTES} (mission byte cap)"
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
    byte_caps = {PLAYBOOKS_DIR: PLAYBOOK_MAX_BYTES, RUNTIME_DIR: RUNTIME_MAX_BYTES}
    for d in (PLAYBOOKS_DIR, RUNTIME_DIR):
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            text, read_err = read_text_safe(f)
            if read_err:
                failures.append(f"{f.relative_to(ROOT)}: {read_err}")
                continue
            for e in md_ref_errors(text, protocols):
                failures.append(f"{f.relative_to(ROOT)}: {e}")
            lines = len(text.splitlines())
            if lines > caps[d]:
                failures.append(
                    f"{f.relative_to(ROOT)}: instruction budget: {lines} lines > "
                    f"{caps[d]} ({d.name} cap)"
                )
            nbytes = len(text.encode("utf-8"))
            if nbytes > byte_caps[d]:
                failures.append(
                    f"{f.relative_to(ROOT)}: instruction budget: {nbytes} bytes > "
                    f"{byte_caps[d]} ({d.name} byte cap)"
                )
    return failures


# Repo content is what git TRACKS: an untracked local dot-dir (.venv, .tox, a tool's cache) is not
# repo content, a TRACKED dot-dir (.github, .claude-plugin) is — and only git knows which. The scan
# uses git ls-files when the root is a work tree, and a filesystem heuristic otherwise (synthetic tests).
_LAYER_SCAN_SKIP = {".git", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}


def _tracked_skill_mds(root):
    """Relative paths of git-TRACKED SKILL.md files, or None if root is not the root of a git work
    tree (a synthetic test dir, or a temp dir nested inside an unrelated repo → filesystem fallback)."""
    try:
        top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10)
        if top.returncode != 0 or Path(top.stdout.strip()).resolve() != Path(root).resolve():
            return None
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return [Path(x) for x in r.stdout.split("\0") if x and Path(x).name == "SKILL.md"]


def check_layer_separation(root=None):
    """Only skills/<name>/ may hold a SKILL.md. AGENTS.md states the rule repo-wide, so the scan is
    repo-wide too — a stray SKILL.md in docs/, .github/, .claude-plugin/, or the repo root auto-triggers
    just as badly as one in playbooks/ or runtime/. Scope is git-TRACKED files: a tracked dot-dir is in
    scope, an untracked local one (.venv/.tox) is not."""
    root = root or ROOT  # resolve at call time so a monkeypatched validate.ROOT is honored
    tracked = _tracked_skill_mds(root)
    if tracked is not None:
        candidates = tracked
    else:  # not a git work tree (synthetic test root): filesystem walk minus VCS/caches/local dot-dirs
        candidates = []
        for p in root.rglob("SKILL.md"):
            segs = p.relative_to(root).parts[:-1]
            if any(d in _LAYER_SCAN_SKIP for d in segs):
                continue
            if any(d.startswith(".") and d != ".claude-plugin" for d in segs):
                continue  # untracked local dot-dir (.venv/.tox/.greptile-internal/…) — not repo content
            candidates.append(p.relative_to(root))
    leaks = []
    for rel in candidates:
        parts = rel.parts
        if parts[0] == "skills" and len(parts) == 3:
            continue  # skills/<name>/SKILL.md — the one discoverable form
        leaks.append(str(rel))
    return sorted(leaks)


def check_evals():
    """Eval JSON files must be valid and self-consistent (ported marketingskills pattern)."""
    return _eval_validator.validate_all()


# Human-facing doc surfaces where a hardcoded catalog count would rot on every new
# mission. The count must never be spelled out here — the README badges read it
# dynamically (assets/badges/, plugin.json version), and this lint fails the build
# if a number creeps back. Adding a mission must not mean rewriting counts everywhere.
COUNT_LINT_FILES = (
    "README.md", "ARCHITECTURE.md", "AGENTS.md", "docs/concepts.md",
    "docs/getting-started.md",
    "CONTRIBUTING.md", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
)
# Catalog-SIZE phrasings only: a digit or spelled number in the catalog range, landing
# on a catalog noun ("11 missions", "eleven missions", "10 outcome-named"), hyphenated
# ("ten-mission set"), or through one adjective and markdown emphasis ("Ten **autonomous
# fleets**"). A bare "one mission" / "two missions" in the mission-identity prose is NOT
# a catalog count and must not trip — so small spelled numbers are excluded.
_SPELLED = ("ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
            "nineteen|twenty")
_NUM = rf"(?:\d+|{_SPELLED})"
# Separator between count, optional adjective, and noun: a hyphen (ten-mission) or
# whitespace with optional markdown emphasis markers (Ten **autonomous fleets**).
_SEP = r"(?:-|[\s*_]+)"
_CATALOG_NOUN = r"(?:missions?|fleets?|outcome-named|callable)"
COUNT_LINT_RE = re.compile(
    rf"\b{_NUM}{_SEP}(?:[a-z]+{_SEP})?{_CATALOG_NOUN}\b",
    re.IGNORECASE,
)
# "all ten" / "all 11" carries a catalog count with no noun at all; it only reads as a
# catalog count on a line that is talking about the catalog. Bare "catalog" is kept
# deliberately: in COUNT_LINT_FILES the word only ever means the mission catalog, and
# a false positive here is a cheap rephrase while a false negative is silent rot.
ALL_COUNT_RE = re.compile(rf"\ball\s+{_NUM}\b", re.IGNORECASE)
MISSION_CONTEXT_RE = re.compile(r"\b(?:missions?|fleets?|catalog)\b", re.IGNORECASE)


def check_doc_counts():
    """Fail on a hardcoded catalog count in a human doc surface. The predecessor's own
    mission count (a historical fact about a different repo) is the one allowed exception."""
    failures = []
    for rel in COUNT_LINT_FILES:
        p = ROOT / rel
        if not p.exists():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            m = COUNT_LINT_RE.search(line)
            if not m and MISSION_CONTEXT_RE.search(line):
                m = ALL_COUNT_RE.search(line)
            if not m:
                continue
            # The predecessor's own count is history, not this catalog — but only when
            # "predecessor" precedes the matched count, so a line carrying BOTH a current
            # count and a predecessor mention is still flagged.
            if "predecessor" in line[: m.start()].lower():
                continue
            failures.append(
                f"{rel}:{i}: hardcoded catalog count '{m.group(0).strip()}' — phrase it "
                f"count-agnostically (the badges read the count dynamically)"
            )
    return failures


def check_manifest_keywords():
    """Every mission dir must be a plugin.json keyword — discovery, and a guard that a new
    mission is not silently dropped from the manifest now that the description no longer lists them."""
    pj = ROOT / ".claude-plugin" / "plugin.json"
    try:
        keywords = set(json.loads(pj.read_text(encoding="utf-8")).get("keywords", []))
    except (OSError, ValueError) as err:
        return [f".claude-plugin/plugin.json: unreadable ({err})"]
    return [
        f".claude-plugin/plugin.json: mission '{d.name}' is not in keywords"
        for d in sorted(SKILLS_DIR.iterdir())
        if d.is_dir() and not d.name.startswith((".", "_")) and (d / "SKILL.md").exists()
        and d.name not in keywords
    ]


def check_badge_freshness():
    """The generated badge JSON (assets/badges/) must match current repo state, so the
    dynamically-read README badges never go stale. Regenerate with scripts/gen-badges.py."""
    gen = ROOT / "scripts" / "gen-badges.py"
    if not gen.is_file():
        return [f"scripts/gen-badges.py missing at {gen} — the badge pipeline is gone"]
    spec = importlib.util.spec_from_file_location("_gen_badges", gen)
    if spec is None or spec.loader is None:
        return [f"scripts/gen-badges.py unloadable at {gen}"]
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.check()


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
            print(f"   - {leak} (only skills/<name>/ may hold a SKILL.md)")

    doc_failures = check_protocol_doc_refs(protocols)
    if doc_failures:
        all_passed = False
        print("\nFAIL protocol cross-references — dangling refs in playbooks/runtime:")
        for failure in doc_failures:
            print(f"   - {failure}")

    eval_errors = check_evals()
    if eval_errors:
        all_passed = False
        print("\nFAIL eval schema — invalid eval JSON or routing coverage:")
        for error in eval_errors:
            print(f"   - {error}")

    count_failures = check_doc_counts()
    if count_failures:
        all_passed = False
        print("\nFAIL count-agnostic docs — a hardcoded catalog count would rot on every new mission:")
        for failure in count_failures:
            print(f"   - {failure}")

    keyword_failures = check_manifest_keywords()
    if keyword_failures:
        all_passed = False
        print("\nFAIL manifest keywords — a mission is missing from plugin.json keywords:")
        for failure in keyword_failures:
            print(f"   - {failure}")

    badge_failures = check_badge_freshness()
    if badge_failures:
        all_passed = False
        print("\nFAIL badge freshness — run scripts/gen-badges.py and commit:")
        for failure in badge_failures:
            print(f"   - {failure}")

    print()
    if all_passed:
        print(f"All {total} missions valid; three-layer separation holds; evals valid.")
        return 0
    print("Validation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
