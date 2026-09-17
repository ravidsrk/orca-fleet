#!/usr/bin/env python3
"""document-it self-test extractor: machine-derive the orca-fleet public surface.

Sub-surfaces:
  A. published skills  (skills/<name>/SKILL.md frontmatter `name`)
  B. script CLIs       (runtime/scripts/*.{py,sh}, scripts/*.{py,sh}) + --help text
  C. config keys/env   (hooks/hooks.json, runtime/*.json, ruff.toml, .env.example)

Output: JSON manifest on stdout; writes <outdir>/surface.json + surface.txt.
The manifest carries the base SHA so a verifier re-derives it at any head.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # extractor/ -> run dir -> docs/runs -> ... fix below
# __file__ = docs/runs/<run>/extractor/extract.py -> parents: extractor, <run>, runs, docs, ROOT
ROOT = Path(__file__).resolve().parents[4]


def git_head():
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()


def extract_skills():
    ents = []
    for d in sorted((ROOT / "skills").iterdir()):
        sk = d / "SKILL.md"
        if not sk.exists():
            continue
        head = sk.read_text().split("---", 2)
        name = None
        if len(head) >= 3:
            m = re.search(r"^name:\s*(\S+)", head[1], re.M)
            name = m.group(1) if m else None
        ents.append({
            "id": f"skill:{d.name}",
            "kind": "skill",
            "name": d.name,
            "frontmatter_name": name,
            "source": f"skills/{d.name}/SKILL.md",
        })
    return ents


def help_text(path: Path):
    """Best-effort --help capture. Returns (exit, first_40_lines)."""
    try:
        if path.suffix == ".py":
            cmd = [sys.executable, str(path), "--help"]
        else:
            cmd = ["bash", str(path), "--help"]
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=30)
        out = (p.stdout + p.stderr).splitlines()[:40]
        return p.returncode, out
    except Exception as e:  # noqa: BLE001 - extractor must not die on one file
        return -1, [f"<capture failed: {e}>"]


def extract_clis():
    ents = []
    for sub in ("runtime/scripts", "scripts", "hooks"):
        for p in sorted((ROOT / sub).iterdir()):
            if p.suffix not in (".py", ".sh") or not p.is_file():
                continue
            if sub == "hooks" and p.suffix != ".sh":
                continue
            code, out = help_text(p)
            flags = sorted(set(re.findall(r"--[a-zA-Z0-9][a-zA-Z0-9_-]*", "\n".join(out))))
            ents.append({
                "id": f"cli:{sub}/{p.name}",
                "kind": "cli",
                "name": f"{sub}/{p.name}",
                "source": f"{sub}/{p.name}",
                "help_exit": code,
                "flags": flags,
            })
    return ents


def extract_config():
    ents = []
    # hooks.json: event keys
    hj = ROOT / "hooks" / "hooks.json"
    if hj.exists():
        data = json.loads(hj.read_text())
        hooks = data.get("hooks", data) if isinstance(data, dict) else data
        keys = list(hooks.keys()) if isinstance(hooks, dict) else []
        ents.append({"id": "config:hooks/hooks.json", "kind": "config",
                     "name": "hooks/hooks.json", "source": "hooks/hooks.json", "keys": keys})
    sj = ROOT / "hooks" / "settings-snippet.json"
    if sj.exists():
        try:
            data = json.loads(sj.read_text())
            keys = list(data.keys()) if isinstance(data, dict) else []
        except json.JSONDecodeError:
            keys = []
        ents.append({"id": "config:hooks/settings-snippet.json", "kind": "config",
                     "name": "hooks/settings-snippet.json",
                     "source": "hooks/settings-snippet.json", "keys": keys})
    for jf in sorted((ROOT / "runtime").glob("*.json")):
        try:
            data = json.loads(jf.read_text())
        except json.JSONDecodeError:
            continue
        keys = list(data.keys()) if isinstance(data, dict) else [f"[{len(data)} items]"]
        ents.append({"id": f"config:runtime/{jf.name}", "kind": "config",
                     "name": f"runtime/{jf.name}", "source": f"runtime/{jf.name}", "keys": keys})
    env = ROOT / ".env.example"
    if env.exists():
        vars_ = sorted(set(re.findall(r"^#?\s*([A-Z][A-Z0-9_]+)=", env.read_text(), re.M)))
        ents.append({"id": "config:.env.example", "kind": "config",
                     "name": ".env.example", "source": ".env.example", "keys": vars_})
    rt = ROOT / "ruff.toml"
    if rt.exists():
        ents.append({"id": "config:ruff.toml", "kind": "config",
                     "name": "ruff.toml", "source": "ruff.toml",
                     "keys": sorted(set(re.findall(r"^([a-z][a-z0-9_-]*)", rt.read_text(), re.M)))})
    return ents


def main(outdir: str):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    skills = extract_skills()
    clis = extract_clis()
    configs = extract_config()
    manifest = {
        "base_sha": git_head(),
        "command": "python3 docs/runs/campaign-2026-09-16-document-it/extractor/extract.py "
                   "docs/runs/campaign-2026-09-16-document-it/extractor",
        "sub_surfaces": {
            "A_skills": len(skills),
            "B_clis": len(clis),
            "C_config": len(configs),
        },
        "entities": skills + clis + configs,
    }
    blob = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (out / "surface.json").write_text(blob)
    import hashlib
    digest = hashlib.sha256(blob.encode()).hexdigest()
    lines = [f"surface digest sha256:{digest} @ {manifest['base_sha']}",
             f"A skills: {len(skills)}  B clis: {len(clis)}  C config: {len(configs)}", ""]
    for e in manifest["entities"]:
        extra = ""
        if e["kind"] == "cli":
            extra = f" help_exit={e['help_exit']} flags={','.join(e['flags'][:12])}"
            if len(e["flags"]) > 12:
                extra += f"+{len(e['flags']) - 12}"
        elif e["kind"] == "config":
            extra = f" keys={','.join(e['keys'][:10])}"
        lines.append(f"{e['id']} <= {e['source']}{extra}")
    (out / "surface.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/runs/campaign-2026-09-16-document-it/extractor")
