#!/usr/bin/env python3
"""
Generate shields.io endpoint-badge JSON from repo state, so the README badges
never drift as missions and tests are added.

Writes:
  assets/badges/missions.json  — count of skills/<name>/ mission dirs
  assets/badges/tests.json     — count of `def test_*` methods under tests/

The README references these via a shields ENDPOINT badge
(https://img.shields.io/endpoint?url=<raw>/assets/badges/<name>.json), and the
version badge reads .claude-plugin/plugin.json directly via a shields DYNAMIC
badge — so no count lives in hand-written prose or in the badge markup.

`scripts/validate.py` calls `compute()` and fails CI if the committed JSON is
stale (someone added a mission without regenerating). Run this to refresh:

    python3 scripts/gen-badges.py           # write the files
    python3 scripts/gen-badges.py --check    # exit 1 if any file is stale
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
TESTS_DIR = ROOT / "tests"
BADGES_DIR = ROOT / "assets" / "badges"

TEST_DEF_RE = re.compile(r"^\s*def (test_\w+)\(", re.MULTILINE)


def mission_count() -> int:
    return sum(
        1
        for d in SKILLS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith((".", "_")) and (d / "SKILL.md").exists()
    )


def test_count() -> int:
    total = 0
    for f in sorted(TESTS_DIR.glob("test_*.py")):
        total += len(TEST_DEF_RE.findall(f.read_text(encoding="utf-8")))
    return total


def badge(label: str, message: str, color: str) -> dict:
    # shields.io endpoint schema (https://shields.io/badges/endpoint-badge)
    return {"schemaVersion": 1, "label": label, "message": message, "color": color}


def compute() -> dict:
    missing = [d.name for d in (SKILLS_DIR, TESTS_DIR) if not d.is_dir()]
    if missing:
        raise RuntimeError(
            f"cannot compute badges: missing director{'ies' if len(missing) > 1 else 'y'} "
            + ", ".join(f"{m}/" for m in missing)
        )
    return {
        "missions.json": badge("missions", str(mission_count()), "1f6feb"),
        "tests.json": badge("contract tests", f"{test_count()} passing", "2ea043"),
    }


def check() -> list[str]:
    """Return a list of stale-badge errors (empty if all committed files are current)."""
    errors = []
    try:
        wanted = compute()
    except RuntimeError as err:
        return [str(err)]
    for name, want in wanted.items():
        path = BADGES_DIR / name
        if not path.exists():
            errors.append(f"assets/badges/{name} missing — run scripts/gen-badges.py")
            continue
        try:
            have = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            errors.append(f"assets/badges/{name}: invalid JSON ({err})")
            continue
        if have != want:
            errors.append(
                f"assets/badges/{name} is stale (have {have.get('message')!r}, "
                f"want {want.get('message')!r}) — run scripts/gen-badges.py"
            )
    return errors


def write() -> None:
    BADGES_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in compute().items():
        (BADGES_DIR / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"wrote assets/badges/{name}: {data['message']}")


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        errs = check()
        for e in errs:
            print(e, file=sys.stderr)
        sys.exit(1 if errs else 0)
    write()
