#!/usr/bin/env python3
"""
Contract test for runtime/pins.json (issue #271).

Every mission's `compatibility:` frontmatter names Orca plus one or more upstream
packs, and those are the dependencies the missions actually execute against. Until
this file existed the only pins were prose in a dated research doc that no check
read. The contract: every pack a `compatibility:` field names has an entry in
runtime/pins.json carrying a 7-40 hex commit and a witness date; every entry is
named by at least one mission (no dead pins); dates are real and not in the future.

    python3 -m unittest tests.test_pins -v
"""
import json
import re
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINS = ROOT / "runtime" / "pins.json"
SKILLS = ROOT / "skills"

HEX_COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# An owner/repo slug in prose names an upstream explicitly; it must resolve to a pin.
SLUG = re.compile(r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b")
REQUIRED = ("repo", "commit", "version", "witnessed", "witness", "aliases")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def compatibility_text(fm):
    """The `compatibility:` value — the key line's remainder plus every following
    indented continuation line (the catalog writes it as a `>-` folded scalar)."""
    out, active = [], False
    for line in fm.splitlines():
        if re.match(r"^compatibility:", line):
            out.append(line.split(":", 1)[1])
            active = True
        elif active and re.match(r"^[ \t]+\S", line):
            out.append(line)
        elif active:
            break
    return " ".join(out)


def load_pins():
    data = json.loads(PINS.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def missions():
    for d in sorted(SKILLS.iterdir()):
        if d.is_dir() and not d.name.startswith((".", "_")) and (d / "SKILL.md").is_file():
            yield d.name, (d / "SKILL.md").read_text(encoding="utf-8")


class TestPins(unittest.TestCase):

    def test_pins_file_well_formed(self):
        pins = load_pins()
        self.assertTrue(pins, "runtime/pins.json pins nothing")
        today = date.today()
        for name, entry in pins.items():
            for field in REQUIRED:
                self.assertIn(field, entry, f"pins.json[{name}] lacks {field!r}")
            self.assertRegex(
                entry["commit"], HEX_COMMIT,
                f"pins.json[{name}].commit must be a 7-40 hex commit, got {entry['commit']!r}",
            )
            self.assertRegex(entry["witnessed"], ISO_DATE, f"pins.json[{name}].witnessed is not YYYY-MM-DD")
            witnessed = date.fromisoformat(entry["witnessed"])  # raises on an impossible date
            self.assertLessEqual(witnessed, today, f"pins.json[{name}] was witnessed in the future")
            self.assertRegex(entry["repo"], r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", f"pins.json[{name}].repo is not owner/repo")
            self.assertTrue(entry["aliases"], f"pins.json[{name}] has no aliases to match compatibility text")
            self.assertIn(
                entry["repo"].lower(), [a.lower() for a in entry["aliases"]],
                f"pins.json[{name}].aliases must include its own repo slug",
            )

    def test_every_named_pack_is_pinned(self):
        pins = load_pins()
        alias_to_pin = {}
        for name, entry in pins.items():
            for alias in entry["aliases"]:
                alias_to_pin[alias.lower()] = name
        referenced = set()
        for mission, text in missions():
            compat = compatibility_text(frontmatter(text))
            self.assertTrue(compat.strip(), f"skills/{mission} has no compatibility: field")
            low = compat.lower()
            hits = set()
            for alias, pin in alias_to_pin.items():
                if re.search(rf"(?<![A-Za-z0-9_/]){re.escape(alias)}(?![A-Za-z0-9_])", low):
                    hits.add(pin)
            # an owner/repo slug under a pinned upstream's owner must resolve to a
            # pin — a sibling repo of a pinned author (another pack from the same
            # source) is exactly the unpinned dependency; plain prose slashes
            # ("review/verify") are not slugs.
            owners = {e["repo"].split("/")[0].lower() for e in pins.values()}
            for slug in SLUG.findall(compat):
                owner = slug.split("/")[0].lower()
                if owner in owners and slug.lower() not in alias_to_pin:
                    self.fail(
                        f"skills/{mission} compatibility names {slug!r}, which runtime/pins.json "
                        "does not pin — add an entry (commit + witnessed date) or drop the reference"
                    )
            self.assertIn(
                "orca", hits,
                f"skills/{mission} compatibility does not name the Orca substrate",
            )
            referenced |= hits
        unreferenced = sorted(set(pins) - referenced)
        self.assertEqual(
            unreferenced, [],
            f"pins.json pins packs no mission's compatibility names: {unreferenced}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
