#!/usr/bin/env python3
"""document-it self-test mapper: grep quadrant homes per entity, emit raw hit table.

Quadrant homes are user-facing docs only (NOT runs/reports/reviews/research/completion).
A hit here is CANDIDATE evidence; the coordinator's coverage-map.md records the verdict
(real quadrant content vs passing mention) with a citing file:line.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "docs/runs/campaign-2026-09-16-document-it"

REF_HOMES = ["README.md", "AGENTS.md", "ARCHITECTURE.md", "CONTRIBUTING.md",
             "docs/missions", "docs/verify-gate.md", "docs/ops.md", "docs/concepts.md",
             "docs/install.md", "docs/about.md", "docs/distribution.md",
             "docs/run-submission-guide.md", "docs/compliance-provenance.md",
             "docs/platform-ride.md", "docs/runtime-scripts.md"]
HOWTO_HOMES = ["docs/getting-started.md", "docs/run-submission-guide.md", "docs/ops.md",
               "docs/install.md", "CONTRIBUTING.md", "docs/guides", "docs/missions"]
TUT_HOMES = ["docs/getting-started.md"]
EXP_HOMES = ["ARCHITECTURE.md", "docs/concepts.md", "docs/platform-ride.md",
             "docs/compliance-provenance.md", "docs/distribution.md", "docs/missions",
             "docs/runtime-scripts.md"]


def grep_files(pattern, homes, max_hits=3):
    """Return [file:line:text] hits for pattern in homes (fixed-string, word-ish)."""
    paths = []
    for h in homes:
        p = ROOT / h
        if p.is_dir():
            paths.extend(sorted(p.glob("*.md")))
        elif p.exists():
            paths.append(p)
    hits = []
    rx = re.compile(pattern)
    for p in paths:
        try:
            for i, line in enumerate(p.read_text().splitlines(), 1):
                if rx.search(line):
                    hits.append(f"{p.relative_to(ROOT)}:{i}:{line.strip()[:110]}")
                    if len(hits) >= max_hits:
                        return hits
        except OSError:
            continue
    return hits


def main(tag=None):
    manifest = json.loads((RUN / "extractor/surface.json").read_text())
    suffix = f"-{tag}" if tag else ""
    out = [f"# Raw coverage hits @ {manifest['base_sha']}",
           "# pattern | reference hits | how-to hits | tutorial hits | explanation hits", ""]
    table = ["entity | reference | how-to | tutorial | explanation",
             "---|---|---|---|---"]
    for e in manifest["entities"]:
        if e["kind"] == "skill":
            pat = r"\b" + re.escape(e["name"]) + r"\b"
            label = e["id"]
        elif e["kind"] == "cli":
            base = e["name"].split("/")[-1].replace(".", r"\.")
            pat = r"(?<![A-Za-z0-9_.-])" + base + r"(?![A-Za-z0-9_])"
            label = e["id"]
        else:
            base = e["name"].split("/")[-1].replace(".", r"\.")
            pat = r"(?<![A-Za-z0-9_.-])" + base + r"(?![A-Za-z0-9_])"
            label = e["id"]
        r = grep_files(pat, REF_HOMES)
        h = grep_files(pat, HOWTO_HOMES)
        t = grep_files(pat, TUT_HOMES)
        x = grep_files(pat, EXP_HOMES)
        cell = lambda hits: (hits[0].rsplit(":", 1)[0] if False else (hits[0].split(":", 1)[0] + ":" + hits[0].split(":")[1] if hits else "—"))
        table.append(f"{label} | {cell(r)} | {cell(h)} | {cell(t)} | {cell(x)}")
        out.append(f"## {label}  /{pat}/")
        out.append(f"  REF: {r if r else '—'}")
        out.append(f"  HOW: {h if h else '—'}")
        out.append(f"  TUT: {t if t else '—'}")
        out.append(f"  EXP: {x if x else '—'}")
        out.append("")
    (RUN / "evidence" / f"map-raw{suffix}.txt").write_text("\n".join(out) + "\n")
    (RUN / "evidence" / f"map-table{suffix}.md").write_text("\n".join(table) + "\n")
    print("\n".join(table))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
