#!/usr/bin/env python3
"""document-it self-test claim check: every factual claim in docs/runtime-scripts.md binds.

Claim kinds (parsed from the doc section, verified against authoritative state):
  FLAGS       backticked `--token` in a CLI section -> must appear in that CLI's
              --help output (help_exit==0 per surface.json) else in its source.
  SUBCOMMANDS backticked names on the `Subcommands:` line -> same text.
  API         backticked names on the `API:` line (import-only libs) -> `def name(` in source.
  KEYS        `| `+"`key`"+` |` rows in a Keys table (config sections) -> member of the JSON
              (top-level keys, or doors[].id for one-way-doors.json).
  PATHS       backticked tokens ending .py/.sh/.json/.md -> file must exist.
  EXITS       integers on the `Exits:` line -> must appear in the source text
              (coarse tripwire; the per-cell rename control uses flags/keys).

Sections are `## `+"`name`"+` headers. Usage:
  claimcheck.py [--cell <section-name>] [doc-path]
Exit 0 = every claim bound; 1 = at least one unbound (prints each).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "docs/runs/campaign-2026-09-16-document-it"
DOC_DEFAULT = ROOT / "docs/runtime-scripts.md"

FLAG_RE = re.compile(r"`(--[A-Za-z][A-Za-z0-9_-]*)`")
PATH_RE = re.compile(r"`((?:[\w.][\w./-]*)\.(?:py|sh|json|md)(?::\d+(?:-\d+)?)?)`")
SECTION_RE = re.compile(r"^## `([^`]+)`\s*$")
SUBCMD_LINE = re.compile(r"^Subcommands:\s*(.+)$")
API_LINE = re.compile(r"^API:\s*(.+)$")
EXITS_LINE = re.compile(r"^Exits:\s*(.+)$")
KEY_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|")
TICKED = re.compile(r"`([^`]+)`")


def load_surface():
    return json.loads((RUN / "extractor/surface.json").read_text())


def split_sections(text):
    sections, cur, name = {}, [], None
    for line in text.splitlines():
        m = SECTION_RE.match(line)
        if m:
            if name:
                sections[name] = cur
            name, cur = m.group(1), []
        elif name is not None:
            cur.append(line)
    if name:
        sections[name] = cur
    return sections


def help_text(source):
    p = ROOT / source
    try:
        if p.suffix == ".py":
            cmd = [sys.executable, str(p), "--help"]
        else:
            cmd = ["bash", str(p), "--help"]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout + r.stderr
    except Exception as e:  # noqa: BLE001 - check must report, not crash
        return -1, f"<capture failed: {e}>"


def check_section(name, lines, surface):
    failures = []
    ent = next((e for e in surface["entities"] if e["source"].endswith(name)), None)
    if ent is None:
        return [f"{name}: no surface entity ends with this section name"]
    src_path = ROOT / ent["source"]
    try:
        src_text = src_path.read_text()
    except OSError as e:
        return [f"{name}: cannot read source {ent['source']}: {e}"]
    body = "\n".join(lines)

    # PATHS: existence
    for m in PATH_RE.finditer(body):
        tok = m.group(1).split(":")[0]
        if not (ROOT / tok).exists():
            failures.append(f"{name}: PATH `{tok}` does not exist")

    if ent["kind"] == "cli":
        help_exit = ent.get("help_exit", -1)
        if help_exit == 0:
            _, help_out = help_text(ent["source"])
            # Concatenated: subcommand flags live in `prog sub --help` and in
            # source, not in top-level --help. A rename in source breaks both.
            text, origin = help_out + "\n" + src_text, "help+source"
        else:
            text, origin = src_text, "source"
        for m in FLAG_RE.finditer(body):
            flag = m.group(1)
            if flag not in text:
                failures.append(f"{name}: FLAG `{flag}` not in {origin} of {ent['source']}")
        for line in lines:
            m = SUBCMD_LINE.match(line)
            if m:
                for tok in TICKED.findall(m.group(1)):
                    if tok not in text:
                        failures.append(f"{name}: SUBCOMMAND `{tok}` not in {origin}")
            m = API_LINE.match(line)
            if m:
                for tok in TICKED.findall(m.group(1)):
                    if f"def {tok}(" not in src_text:
                        failures.append(f"{name}: API `{tok}` has no `def {tok}(` in {ent['source']}")
            m = EXITS_LINE.match(line)
            if m:
                for num in re.findall(r"\b(\d+)\b", m.group(1)):
                    if num not in src_text:
                        failures.append(f"{name}: EXIT {num} not found in {ent['source']}")
    elif ent["kind"] == "config":
        try:
            data = json.loads(src_text)
        except json.JSONDecodeError as e:
            return [f"{name}: source JSON unparseable: {e}"]
        if isinstance(data, dict) and isinstance(data.get("doors"), list):
            members = {d.get("id") for d in data["doors"] if isinstance(d, dict)}
        elif isinstance(data, dict):
            members = set(data.keys())
        else:
            members = set()
        for line in lines:
            m = KEY_ROW.match(line)
            if m and m.group(1) not in members:
                failures.append(f"{name}: KEY `{m.group(1)}` not in {ent['source']}")
    return failures


def main(argv):
    cell = None
    doc = DOC_DEFAULT
    args = list(argv)
    if "--cell" in args:
        i = args.index("--cell")
        cell = args[i + 1]
        del args[i:i + 2]
    if args:
        doc = Path(args[0])
    if not doc.exists():
        print(f"claimcheck: {doc} does not exist (no sections landed yet)")
        return 1
    surface = load_surface()
    sections = split_sections(doc.read_text())
    if cell:
        if cell not in sections:
            print(f"claimcheck: no section `## `{cell}`` in {doc}")
            return 1
        sections = {cell: sections[cell]}
    failures = []
    for name, lines in sections.items():
        failures.extend(check_section(name, lines, surface))
    for f in failures:
        print("UNBOUND:", f)
    print(f"claimcheck: {len(sections)} section(s), {len(failures)} unbound claim(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
