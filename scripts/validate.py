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
_rr_spec = importlib.util.spec_from_file_location(
    "run_report", ROOT / "runtime" / "scripts" / "run_report.py"
)
_run_report = importlib.util.module_from_spec(_rr_spec)
_rr_spec.loader.exec_module(_run_report)
SKILLS_DIR = ROOT / "skills"
PLAYBOOKS_DIR = ROOT / "playbooks"
RUNTIME_DIR = ROOT / "runtime"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PROOF_VALUES = {"doctrine-only", "self-run", "external-run"}
AUTONOMY_VALUES = {"L0", "L1", "L2", "L3", "L4", "L5"}
# agentskills.io allowlist (skills-ref / `agentskills validate`). Repo extras
# are first-class, machine-checked claims — not `metadata:` bags. A fourth
# top-level extra fails this validator (issue #211). skills-ref itself still
# reports the extras as unexpected; that is expected, not a migrate-to-metadata
# prompt.
SPEC_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}
# The repo's own machine-checked claims live under the spec's extension point,
# `metadata:` (issue #263). Top level is the spec allowlist and nothing else:
# skills-ref (`agentskills validate`), `package_skill.py`, the claude.ai upload
# path and the Skills API all HARD-ERROR on an unexpected top-level key, so a
# repo extra there makes the catalog unpackageable through Anthropic's own paths.
#
# `unit` … `oracle` are the six-point mission-identity tuple of ARCHITECTURE.md
# made machine-readable (issue #265): declaring it is what makes the identity
# test executable instead of a paragraph, and `identity_collisions()` below
# fails the build when two missions declare the same six.
IDENTITY_KEYS = ("unit", "state_machine", "convergence", "ordering", "parking", "oracle")
METADATA_KEYS = {"proof", "autonomy", "proof_evidence", *IDENTITY_KEYS}
METADATA_VALUE_MAX = 160
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
    "pin-it",
    "floor-it",
    "reshape-it",
    "field-test-it",
    "migrate-it",
    "oncall-it",
    "absorb-it",
    "document-it",
}
# Instruction budget. The predecessor's mandatory instruction surface hit ~42K
# tokens with no counterpressure; these caps are the counterpressure.
#
# A mission's budget is split, because a whole-file cap prices declarations and
# instructions the same: a mission that spends 30 lines on machine-readable
# frontmatter would have to delete 30 lines of protocol to pay for it. The BODY
# cap is the instruction surface and is ratcheted to the measured catalog
# maximum (110 lines, pin-it) — no mission has headroom, so a protocol line
# costs a protocol line. The FRONTMATTER cap bounds the declarations separately.
# Raising either is a deliberate diff, which is the point.
MISSION_BODY_MAX_LINES = 110
MISSION_FRONTMATTER_MAX_LINES = 34
MISSION_MAX_LINES = MISSION_BODY_MAX_LINES + MISSION_FRONTMATTER_MAX_LINES
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
# This regex is the shared grammar: the orphan test and the mission-guide compose
# check import it rather than keeping a parallel copy.
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


def compose_clause_backticks(text):
    """Backticked names inside every Composes/rides paragraph."""
    return [
        ref
        for clause in COMPOSE_CLAUSE_RE.findall(text)
        for ref in BACKTICK_RE.findall(clause)
    ]


def _is_url_md_token(text, match):
    """True for https://…/x.md (and //…/x.md) — an external link, not a protocol ref."""
    tok = match.group(0)
    return tok.startswith("//") or text[max(0, match.start() - 1) : match.start()] == ":"


def bare_md_stems(text):
    """Bare `<name>.md` tokens that look like protocol names.

    URLs and path-prefixed forms are excluded: protocols are referenced by bare
    name, and a path-prefixed protocol token is a validator error, not composition.
    """
    stems = []
    for m in MD_TOKEN_RE.finditer(text):
        if _is_url_md_token(text, m):
            continue
        tok = m.group(0)
        if "/" in tok:
            continue
        stem = tok[: -len(".md")]
        if NAME_RE.match(stem):
            stems.append(stem)
    return stems


def explicit_protocol_refs(text):
    """Names that count as an explicit protocol reference.

    Two forms, matching what the validator actually checks:

    - backticked names inside a Composes/rides clause
    - bare `<name>.md` tokens anywhere

    A backticked name in Related/prose is not composition — that is the
    asymmetry the orphan test previously got wrong by accepting backticks
    anywhere. The orphan test imports this helper so the two checkers cannot
    drift.

    A further deliberate cut, *not* this helper: the human-guide compose check
    uses `guide_declared_protocol_names` (first sentence of each clause) so a
    caveat like clean-sweep's "not a full `runtime-prove` pass" does not force
    that protocol into `docs/missions/`. Do not collapse the two.
    """
    return set(compose_clause_backticks(text)) | set(bare_md_stems(text))


def guide_declared_protocol_names(text):
    """Backticked names a human mission guide must list under ## Composes.

    First sentence of each Composes/rides paragraph only. Later sentences are
    caveats (clean-sweep: "not a full `runtime-prove` pass") and must not
    require that protocol in docs/missions/<name>.md.
    """
    names = []
    for clause in COMPOSE_CLAUSE_RE.findall(text):
        first = re.split(r"\.\s+(?=[A-Z])", clause, maxsplit=1)[0]
        names.extend(BACKTICK_RE.findall(first))
    return names


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
        if _is_url_md_token(text, m):
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


def _unquote(val):
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        return val[1:-1]
    return val


def parse_frontmatter(text):
    """Minimal YAML-frontmatter reader: scalars, block scalars, one nested map.

    The nested map is what the agentskills.io spec calls the extension point:
    `metadata:` followed by indented `key: value` lines is returned as a dict.
    A bare `key:` with nothing indented under it still returns "<object>", so
    the "compatibility must be a string" error keeps its shape.
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
    nested_key = None
    for line in block.split("\n"):
        if multiline_indicator and (line.startswith("  ") or line.strip() == ""):
            multiline_value.append(line[2:] if line.startswith("  ") else line)
            continue
        if multiline_indicator:
            data[current_key] = " ".join(l.strip() for l in multiline_value if l.strip())
            multiline_indicator = None
            multiline_value = []
        if nested_key is not None and line.startswith("  ") and line.strip():
            sub = re.match(r"^\s+([a-zA-Z_-][a-zA-Z0-9_-]*):\s*(.*)$", line)
            if sub:
                if data[nested_key] == "<object>":
                    data[nested_key] = {}
                if isinstance(data[nested_key], dict):
                    data[nested_key][sub.group(1)] = _unquote(sub.group(2).strip())
                continue
        m = re.match(r"^([a-zA-Z_-][a-zA-Z0-9_-]*):\s*(.*)$", line)
        if m:
            nested_key = None
            key, val = m.group(1), m.group(2).strip()
            if val in (">", "|", ">-", "|-"):
                current_key = key
                multiline_indicator = val
                multiline_value = []
            elif val == "":
                current_key = key
                nested_key = key
                data[key] = "<object>"
            else:
                data[key] = _unquote(val)
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


def split_budget(text):
    """(frontmatter lines, body lines) — declarations and instructions priced apart."""
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", text, re.S)
    if not m:
        return 0, len(text.splitlines())
    return len(m.group(1).splitlines()) + 2, len(text[m.end():].splitlines())


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

    extras = set(data) - SPEC_FRONTMATTER_FIELDS
    if extras:
        errors.append(
            "unexpected top-level frontmatter fields "
            + ", ".join(f"'{k}'" for k in sorted(extras))
            + " — the spec allowlist is "
            + str(sorted(SPEC_FRONTMATTER_FIELDS))
            + "; repo claims belong under 'metadata:' (issue #263)"
        )

    meta = data.get("metadata")
    if meta is None:
        errors.append(
            "missing 'metadata:' block (proof, autonomy, and the six identity keys live there)"
        )
        meta = {}
    elif not isinstance(meta, dict):
        errors.append("metadata must be a map of string keys to string values")
        meta = {}
    else:
        unknown = set(meta) - METADATA_KEYS
        if unknown:
            errors.append(
                "unexpected metadata keys "
                + ", ".join(f"'{k}'" for k in sorted(unknown))
                + f" — allowed: {sorted(METADATA_KEYS)}"
            )
        for key, value in sorted(meta.items()):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"metadata.{key} must be a non-empty string")
            elif len(value) > METADATA_VALUE_MAX:
                errors.append(
                    f"metadata.{key} is {len(value)} chars > {METADATA_VALUE_MAX} "
                    "— the tuple is a claim, not a paragraph"
                )

    # Six-point mission identity (ARCHITECTURE.md). Each point is declared, so
    # "is this a mission or a mode of another?" is answered by a diff, not a memo.
    for key in IDENTITY_KEYS:
        if not (meta.get(key) or "").strip():
            errors.append(
                f"missing metadata.{key} — all six identity points "
                f"{list(IDENTITY_KEYS)} are required (ARCHITECTURE.md)"
            )

    if "compatibility" in data:
        c = data["compatibility"]
        if c == "<object>":
            errors.append("compatibility must be a string (1-500 chars), got a mapping")
        elif not (1 <= len(c) <= 500):
            errors.append(f"compatibility length {len(c)} out of 1-500")

    # proof status: honest by construction — no mission presents itself as proven
    # without a run report on disk
    proof = meta.get("proof")
    if proof is None:
        errors.append("missing 'proof' field (doctrine-only | self-run | external-run)")
    elif proof not in PROOF_VALUES:
        errors.append(f"proof '{proof}' invalid (want one of {sorted(PROOF_VALUES)})")
    elif proof != "doctrine-only":
        evidence = meta.get("proof_evidence", "")
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
            # …and the report has to be BOUND, not merely named (issue #259): a
            # RUN: header, a manifest inside the run's own directory, and an
            # inventory that re-hashes at the commit it was computed at.
            errors.extend(_run_report.check_report(evidence, name, proof, ROOT))

    # autonomy level (Osmani L0-L5): a first-class, machine-readable claim sibling to
    # proof — the level a mission safely runs at, gated by how cheaply it is verified.
    autonomy = meta.get("autonomy")
    if autonomy is None:
        errors.append("missing 'autonomy' field (L0-L5)")
    elif autonomy not in AUTONOMY_VALUES:
        errors.append(f"autonomy '{autonomy}' invalid (want one of {sorted(AUTONOMY_VALUES)})")

    fm_lines, body_lines = split_budget(text)
    if body_lines > MISSION_BODY_MAX_LINES:
        errors.append(
            f"instruction budget: {body_lines} body lines > {MISSION_BODY_MAX_LINES} "
            "(mission cap; frontmatter is budgeted separately)"
        )
    if fm_lines > MISSION_FRONTMATTER_MAX_LINES:
        errors.append(
            f"frontmatter budget: {fm_lines} lines > {MISSION_FRONTMATTER_MAX_LINES} "
            "(declarations cap)"
        )
    load, _parts = transitive_load(skill_dir, protocols)
    if load > MISSION_MAX_LOAD_TOKENS:
        errors.append(
            f"activation load: ~{load} tokens > {MISSION_MAX_LOAD_TOKENS} — SKILL.md plus "
            "every doc its Composes/rides clause makes mandatory. Move a phase's doc behind "
            "a 'read <doc> when entering <phase>' cue instead of raising the cap"
        )
    nbytes = len(text.encode("utf-8"))
    if nbytes > MISSION_MAX_BYTES:
        errors.append(
            f"instruction budget: {nbytes} bytes > {MISSION_MAX_BYTES} (mission byte cap)"
        )

    # architecture: every playbook/runtime a mission says it Composes/rides must exist,
    # and there must be at least one such name — a clause the regex can't see into
    # (bare directory pointers, prose) would otherwise pass with zero checks.
    clause_refs = compose_clause_backticks(text)
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


def check_lower_layer_frontmatter(root=None):
    """No file under playbooks/ or runtime/ may carry YAML frontmatter (#305).

    AGENTS.md has said "playbooks and runtime policies are plain Markdown with no frontmatter"
    since the layer rule was written, and nothing enforced it — a playbook handed frontmatter
    passed every gate. That sentence was doctrine wearing a mechanism's clothes, which is the
    exact shape this validator exists to refuse.

    Frontmatter is what makes a file DISCOVERABLE: it is where `name:` and `description:` live,
    and a host that indexes a directory reads it. A playbook is meant to be called by name, never
    matched by a router, so the separation is only real while the lower layers stay unindexable.
    """
    root = root or ROOT
    offenders = []
    for layer in ("playbooks", "runtime"):
        base = root / layer
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            text = md.read_text(encoding="utf-8", errors="replace")
            # Frontmatter is an opening `---` on line 1 and a closing one later. A horizontal
            # rule mid-document is not frontmatter, and neither is a `---` on line 1 with no
            # close — that is malformed, and calling it frontmatter would be a false red.
            if not text.startswith("---\n"):
                continue
            # parse_frontmatter is the repo's own reader, so "what counts as frontmatter" has
            # exactly one definition. A `---` on line 1 with no closing fence is malformed, not
            # frontmatter, and it returns an error rather than a block — calling that a leak
            # would be a false red on a document that simply opens with a horizontal rule.
            block, err = parse_frontmatter(text)
            if block is not None and not err:
                offenders.append(str(md.relative_to(root)))
    return offenders


def check_layer_separation(root=None):
    """Only skills/<name>/ may hold a SKILL.md. AGENTS.md states the rule repo-wide, so the scan is
    repo-wide too — a stray SKILL.md in docs/, .github/, .claude-plugin/, or the repo root
    auto-triggers just as badly as one in playbooks/ or runtime/.

    Tracked AND untracked (#305). This was `git ls-files` alone, so an UNTRACKED `SKILL.md` under
    `playbooks/` passed every gate — and the host does not care whether a file is committed. On a
    symlinked checkout, which is the trial path the README recommends first, that file activates.
    The walk is the authority now and the tracked list only adds to it, so a tracked file inside a
    normally-skipped directory is still in scope. Untracked local dot-dirs (.venv/.tox) and caches
    stay out: they are not repo content on any checkout."""
    root = root or ROOT  # resolve at call time so a monkeypatched validate.ROOT is honored
    candidates = []
    for p in root.rglob("SKILL.md"):
        segs = p.relative_to(root).parts[:-1]
        if any(d in _LAYER_SCAN_SKIP for d in segs):
            continue
        if any(d.startswith(".") and d != ".claude-plugin" for d in segs):
            continue  # untracked local dot-dir (.venv/.tox/.greptile-internal/…) — not repo content
        candidates.append(p.relative_to(root))
    for rel in _tracked_skill_mds(root) or []:
        if rel not in candidates:
            candidates.append(rel)
    leaks = []
    for rel in candidates:
        parts = rel.parts
        if parts[0] == "skills" and len(parts) == 3:
            continue  # skills/<name>/SKILL.md — the one discoverable form
        leaks.append(str(rel))
    return sorted(leaks)


# Transitive activation load (issue #276). The line/byte caps above bound each
# FILE; nothing bounded what a mission makes a coordinator read on activation:
# its SKILL.md, every playbook and runtime doc named in its Composes/rides
# clause, and every repo-root doc it links. The current figures are NOT written
# here: load_report() below computes them, ARCHITECTURE.md publishes them from a
# generated block, and a hand-typed copy is how that table drifted twice (#303).
# What is stable enough to state: every mission is several times what
# agentskills.io recommends per activated skill, and the predecessor died of the
# same shape at ~42K.
#
# The cap is a RATCHET, not the recommendation: set at the catalog's measured
# maximum so no mission may grow its activation load, and lowered only by real
# restructuring (per-phase "read <doc> when entering X" cues instead of a single
# read-everything compose clause). Naming the gap honestly and freezing it beats
# a 5K cap that would red every mission on day one and be raised by lunchtime.
TOKENS_PER_BYTE = 0.25  # the crude bytes/4 estimate the docs/reviews/2026-09-10-review.md measurement used
MISSION_MAX_LOAD_TOKENS = 34_000
ROOT_DOC_RE = re.compile(r"\]\((?:\.\./)+([A-Z][A-Z0-9_.-]*\.md)\)")


def _repo_rel(path):
    """Repo-relative when the path is inside ROOT, absolute otherwise.

    A fixture skill dir lives in a temp tree while the protocols it composes are
    the real ones; `Path.relative_to` raises across that boundary.
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def transitive_load(skill_dir, protocols=None):
    """(tokens, {path: tokens}) a coordinator reads to activate this mission.

    SKILL.md + every playbook/runtime doc its Composes/rides clause names + every
    repo-root doc it links (ARCHITECTURE.md and friends). One hop: what a doc
    itself references is the coordinator's on-demand read, not activation load.
    """
    skill_md = skill_dir / "SKILL.md"
    text, err = read_text_safe(skill_md)
    if err or text is None:
        return 0, {}
    parts = {f"skills/{skill_dir.name}/SKILL.md": len(text.encode("utf-8"))}
    protocols = protocols if protocols is not None else known_protocol_names()
    # Only what the Composes/rides clause makes MANDATORY. A protocol named in
    # prose ("see `mission-chaining.md`") is an on-demand pointer, not activation
    # load — counting it would inflate the number and blur what the cap is for.
    mandatory = set()
    for clause in COMPOSE_CLAUSE_RE.findall(text):
        mandatory |= set(BACKTICK_RE.findall(clause))
        mandatory |= set(bare_md_stems(clause))
    for name in sorted(mandatory):
        if name not in protocols:
            continue
        for base in (PLAYBOOKS_DIR, RUNTIME_DIR):
            doc = base / f"{name}.md"
            if doc.is_file():
                body, doc_err = read_text_safe(doc)
                if not doc_err and body is not None:
                    parts[_repo_rel(doc)] = len(body.encode("utf-8"))
                break
    for root_doc in sorted(set(ROOT_DOC_RE.findall(text))):
        doc = ROOT / root_doc
        if doc.is_file():
            body, doc_err = read_text_safe(doc)
            if not doc_err and body is not None:
                parts[root_doc] = len(body.encode("utf-8"))
    tokens = {path: round(n * TOKENS_PER_BYTE) for path, n in parts.items()}
    return sum(tokens.values()), tokens


def load_report(root=None):
    """[(mission, tokens)] descending — the activation-load table."""
    skills_dir = (root or ROOT) / "skills"
    protocols = known_protocol_names()
    rows = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith((".", "_")):
            continue
        if not (skill_dir / "SKILL.md").is_file():
            continue
        total, _parts = transitive_load(skill_dir, protocols)
        rows.append((skill_dir.name, total))
    rows.sort(key=lambda row: (-row[1], row[0]))
    return rows


# Identity-tuple comparison. A point is "the same" when its two declarations
# carry the same content words; six same points means one mission wearing two
# names, which is exactly what ARCHITECTURE.md forbids.
_IDENTITY_STOPWORDS = {
    "a", "an", "and", "any", "are", "as", "at", "be", "by", "every", "for",
    "from", "in", "into", "is", "it", "its", "no", "not", "of", "on", "one",
    "or", "per", "that", "the", "their", "then", "this", "to", "with",
}
IDENTITY_POINT_SAME = 0.85
# Six points that are each merely SIMILAR still describe one mission twice. A synonym swap scores
# ~0.67 a point — under the 0.85 bar on every one of them, and a duplicate all the same (#288).
#
# A paraphrase leaves NO point on which the two missions diverge — some points restated, some left
# alone, none of them actually different. That is the signature, and it is what ARCHITECTURE.md
# already implies: differing on one point is legal-but-surfaced (a WARN) and differing on two is
# silent, so a pair with no divergent point at all is one mission twice, however its words are
# arranged. Neither the mean nor the single weakest point works here — a five-of-six match averages
# high while being a legitimate distinction, and a paraphraser can rewrite one point heavily. The
# live catalog's closest pair has ONE near point out of six, so this has wide clearance.
IDENTITY_POINT_NEAR = 0.4


def _identity_tokens(value):
    """Identity-point tokens, STEMMED and synonym-expanded (#288).

    Raw surface tokens made this a duplicate-string detector wearing an identity test's name: one
    word defeated it. "…backlog drained to zero…" against "…backlog emptied to zero…" scored 0.667
    against a 0.85 bar, so a second mission could restate the first's identity and pass.

    eval.py already owns the repository's tokenizer — the same stemming and synonym table the
    router uses — so the two surfaces now agree on what a word is instead of keeping separate
    definitions. Stemming alone closes the inflection paraphrase ("backlogs", "draining"); a true
    synonym swap is caught by the MEAN gate below, not here.
    """
    try:
        _scoring, synonyms = _eval_validator.routing_config()
        tokens = set(_eval_validator.tokenize(value or "", synonyms))
    except Exception:  # noqa: BLE001 — a tokenizer failure must not silently widen the gate
        tokens = {w for w in re.findall(r"[a-z0-9_]+", (value or "").lower())
                  if w not in _IDENTITY_STOPWORDS}
    return {t for t in tokens if t not in _IDENTITY_STOPWORDS}


def _point_similarity(a, b):
    ta, tb = _identity_tokens(a), _identity_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _identity_sims(ta, tb):
    """Per-point similarity across the six identity points."""
    return [_point_similarity(x, y) for x, y in zip(ta, tb)]


def identity_collisions(root=None):
    """Mission pairs that declare the same six identity points.

    ARCHITECTURE.md: two workflows are the same mission only if they share ALL
    six. So the executable form of that test is — no pair may match on six.
    A pair matching on five is reported as a WARN: legal, but it is the shape
    that the access-it / field-test-it / pin-it argument had to be made for, so
    it should never pass unnoticed.
    """
    skills_dir = (root or ROOT) / "skills"
    tuples = {}
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md" if skill_dir.is_dir() else None
        if not skill_md or not skill_md.exists():
            continue
        text, read_err = read_text_safe(skill_md)
        if read_err:
            continue
        data, err = parse_frontmatter(text)
        if err or not isinstance(data, dict):
            continue
        meta = data.get("metadata")
        if isinstance(meta, dict) and all(meta.get(k) for k in IDENTITY_KEYS):
            tuples[skill_dir.name] = tuple(meta[k] for k in IDENTITY_KEYS)
    errors, warnings = [], []
    names = sorted(tuples)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            same = [
                key
                for key, va, vb in zip(IDENTITY_KEYS, tuples[a], tuples[b])
                if _point_similarity(va, vb) >= IDENTITY_POINT_SAME
            ]
            sims = _identity_sims(tuples[a], tuples[b])
            near = sum(1 for value in sims if value >= IDENTITY_POINT_NEAR)
            mean = sum(sims) / len(sims) if sims else 0.0
            if len(same) == len(IDENTITY_KEYS):
                errors.append(
                    f"{a} and {b} declare the same six identity points — "
                    "one mission with two names (ARCHITECTURE.md); merge them or "
                    "state which point actually differs"
                )
            elif near == len(IDENTITY_KEYS):
                restated = [k for k, value in zip(IDENTITY_KEYS, sims)
                            if value < IDENTITY_POINT_SAME]
                errors.append(
                    f"{a} and {b} restate one identity: all {len(IDENTITY_KEYS)} points are at "
                    f"least similar (mean {mean:.2f}), with {restated} merely reworded rather than "
                    "different. A paraphrase is not a distinction — there is no point on which "
                    "these two missions actually diverge. Merge them, or make one point genuinely "
                    "differ and say so in ARCHITECTURE.md (#288)"
                )
            elif len(same) == len(IDENTITY_KEYS) - 1:
                differs = [k for k in IDENTITY_KEYS if k not in same]
                warnings.append(
                    f"{a} and {b} differ on only {differs[0]} — legal, but the "
                    "argument for keeping both belongs in ARCHITECTURE.md"
                )
    return errors, warnings


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
_SEP = r"(?:-|[\s*_`]+)"
# The proof tiers are catalog nouns too: "21 `doctrine-only`" is a hardcoded catalog count that
# the noun set could not see, and it sat in README.md while this very guard was green (#282).
_CATALOG_NOUN = (r"(?:missions?|fleets?|outcome-named|callable|"
                 r"`?(?:doctrine-only|self-run|external-run)`?)")
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

    framed = check_lower_layer_frontmatter()
    if framed:
        all_passed = False
        print("\nFAIL layer separation — frontmatter under playbooks/ or runtime/:")
        for path in framed:
            print(f"   - {path} (frontmatter is what makes a file discoverable; "
                  "playbooks are called by name, never matched by a router)")

    doc_failures = check_protocol_doc_refs(protocols)
    if doc_failures:
        all_passed = False
        print("\nFAIL protocol cross-references — dangling refs in playbooks/runtime:")
        for failure in doc_failures:
            print(f"   - {failure}")

    identity_errors, identity_warnings = identity_collisions()
    if identity_errors:
        all_passed = False
        print("\nFAIL mission identity — two missions declare the same six points:")
        for error in identity_errors:
            print(f"   - {error}")
    for warning in identity_warnings:
        print(f"WARN mission identity — {warning}")

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
