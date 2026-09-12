#!/usr/bin/env python3
"""
Generate shields.io endpoint-badge JSON from repo state, so the README badges
never drift as missions and tests are added.

Writes:
  assets/badges/missions.json  — count of skills/<name>/ mission dirs
  assets/badges/tests.json     — source inventory of `def test_*` definitions under tests/;
                                 no test execution or pass/fail result
  docs/missions/<name>.md      — the "Activation load" callout, measured by
                                 scripts/validate.py's transitive_load (issue #276)

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
GUIDES_DIR = ROOT / "docs" / "missions"
# The callout sits directly under the Autonomy one in every mission guide.
LOAD_CALLOUT_RE = re.compile(r"(?m)^> \*\*Activation load:\*\* .*$")
AUTONOMY_CALLOUT_RE = re.compile(r"(?m)^> \*\*Autonomy:\*\* .*$")
LOAD_ROUND = 100  # tokens — small doc edits must not churn 21 guides


def _validate_module():
    """Load scripts/validate.py lazily.

    validate.py loads THIS module inside check_badge_freshness(); loading it back
    at import time would recurse. Inside a function, each side only ever executes
    the other's module body once.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_validate", ROOT / "scripts" / "validate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def activation_loads() -> dict:
    """{mission: rounded token estimate} for every mission guide callout."""
    v = _validate_module()
    return {
        name: round(tokens / LOAD_ROUND) * LOAD_ROUND
        for name, tokens in v.load_report()
    }


def load_callout(mission: str, tokens: int) -> str:
    return (
        f"> **Activation load:** ~{tokens:,} tokens — this SKILL.md plus every playbook and "
        f"runtime doc its Composes/rides clause makes mandatory "
        f"([why it is measured](../../ARCHITECTURE.md#instruction-budget))"
    )


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
        "tests.json": badge("test definitions", f"{test_count()} in source", "6e7781"),
    }


def check_guides() -> list[str]:
    """Stale/missing Activation load callouts in docs/missions/*.md."""
    errors = []
    if not GUIDES_DIR.is_dir():
        return [f"docs/missions/ missing at {GUIDES_DIR}"]
    for mission, tokens in activation_loads().items():
        guide = GUIDES_DIR / f"{mission}.md"
        if not guide.is_file():
            errors.append(f"docs/missions/{mission}.md missing — every mission needs a guide")
            continue
        text = guide.read_text(encoding="utf-8")
        want = load_callout(mission, tokens)
        found = LOAD_CALLOUT_RE.search(text)
        if not found:
            errors.append(
                f"docs/missions/{mission}.md has no Activation load callout "
                "— run scripts/gen-badges.py"
            )
        elif found.group(0) != want:
            errors.append(
                f"docs/missions/{mission}.md Activation load is stale "
                f"(want ~{tokens:,} tokens) — run scripts/gen-badges.py"
            )
    return errors


def write_guides() -> None:
    for mission, tokens in activation_loads().items():
        guide = GUIDES_DIR / f"{mission}.md"
        if not guide.is_file():
            print(f"skip docs/missions/{mission}.md: no guide")
            continue
        text = guide.read_text(encoding="utf-8")
        want = load_callout(mission, tokens)
        if LOAD_CALLOUT_RE.search(text):
            new_text = LOAD_CALLOUT_RE.sub(lambda _m: want, text, count=1)
        else:
            m = AUTONOMY_CALLOUT_RE.search(text)
            if not m:
                print(f"skip docs/missions/{mission}.md: no Autonomy callout to anchor to")
                continue
            new_text = text[: m.end()] + "\n" + want + text[m.end():]
        if new_text != text:
            guide.write_text(new_text, encoding="utf-8")
            print(f"wrote docs/missions/{mission}.md: ~{tokens:,} tokens")


# --- ARCHITECTURE.md's activation-load table -----------------------------------------
# It was written by hand and drifted 150-280 tokens within a day of being published (#303) —
# and again during the work that fixed it, by which point the ORDERING had changed too
# (clean-sweep was the heaviest mission; ship-it is). A table a human retypes is a claim with
# no mechanism, which is the shape this catalog exists to refuse.
ARCH = ROOT / "ARCHITECTURE.md"
ARCH_BEGIN = "<!-- BEGIN GENERATED: activation-load — scripts/gen-badges.py -->"
ARCH_END = "<!-- END GENERATED: activation-load -->"
ARCH_BLOCK_RE = re.compile(
    re.escape(ARCH_BEGIN) + r".*?" + re.escape(ARCH_END), re.S)


def load_table() -> str:
    """The generated block: every mission at or above the three-heaviest mark, plus headroom."""
    v = _validate_module()
    rows = v.load_report()
    cap = v.MISSION_MAX_LOAD_TOKENS
    lines = [ARCH_BEGIN,
             "",
             "| Mission | Activation load | Headroom to the cap |",
             "|---|---|---|"]
    for name, tokens in rows[:3]:
        lines.append(f"| `{name}` | ~{round(tokens / LOAD_ROUND) * LOAD_ROUND:,} | "
                     f"~{round((cap - tokens) / LOAD_ROUND) * LOAD_ROUND:,} |")
    lightest, light_tokens = rows[-1]
    lines += [
        "",
        f"The cap is **{cap:,}**. The lightest mission, `{lightest}`, is "
        f"~{round(light_tokens / LOAD_ROUND) * LOAD_ROUND:,}, so the whole catalog sits in a "
        f"~{round((rows[0][1] - light_tokens) / LOAD_ROUND) * LOAD_ROUND:,}-token band.",
        ARCH_END,
    ]
    return "\n".join(lines)


def check_architecture() -> list[str]:
    if not ARCH.is_file():
        return [f"{ARCH.name} missing at {ARCH}"]
    text = ARCH.read_text(encoding="utf-8")
    found = ARCH_BLOCK_RE.search(text)
    if not found:
        return [f"{ARCH.name} has no generated activation-load block — run scripts/gen-badges.py"]
    if found.group(0) != load_table():
        return [f"{ARCH.name} activation-load table is stale — run scripts/gen-badges.py"]
    return []


def write_architecture() -> None:
    if not ARCH.is_file():
        print(f"skip {ARCH.name}: missing")
        return
    text = ARCH.read_text(encoding="utf-8")
    if not ARCH_BLOCK_RE.search(text):
        print(f"skip {ARCH.name}: no generated block markers to fill")
        return
    new_text = ARCH_BLOCK_RE.sub(lambda _m: load_table(), text, count=1)
    if new_text != text:
        ARCH.write_text(new_text, encoding="utf-8")
        print(f"wrote {ARCH.name}: activation-load table")


def check() -> list[str]:
    """Return a list of stale-artifact errors (empty if everything committed is current)."""
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
    return errors + check_guides() + check_architecture()


def write() -> None:
    BADGES_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in compute().items():
        (BADGES_DIR / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"wrote assets/badges/{name}: {data['message']}")
    write_guides()
    write_architecture()


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        errs = check()
        for e in errs:
            print(e, file=sys.stderr)
        sys.exit(1 if errs else 0)
    write()
