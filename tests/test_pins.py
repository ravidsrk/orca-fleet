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


LOCK = ROOT / ".github" / "ci-tools.lock"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


class CiToolsArePinnedByHash(unittest.TestCase):
    """#301: `uv`, `skills-ref` and `ruff` were three version strings and nothing else.

    No checksum, no test, nothing that noticed a bump — "a version string with no hash and no
    test guarding it is a comment." The workflow argued a lockfile would be needed to hash them
    honestly, which was right; `.github/ci-tools.lock` is that lockfile.
    """

    # Every package the lock must carry, direct and transitive. A resolver that quietly drops
    # or adds one is a different tool tree than the one that was proven to work.
    PINNED = {"ruff": "0.16.5", "skills-ref": "0.1.1", "click": "8.5.0",
              "strictyaml": "1.7.3", "python-dateutil": "2.9.0.post0", "six": "1.17.0"}
    def _entries(self):
        """Parse the lock the way PIP does, continuation markers included.

        A forgiving parser is worse than none here: drop the trailing backslash from a
        `name==version` line and pip reads a requirement with NO hashes, which
        --require-hashes rejects outright — while a parser that merely scans for
        `--hash` nearby still sees them and calls the lock fine. The negative control
        caught exactly that, so the continuation is tracked rather than assumed.
        """
        entries, current, continued = {}, None, False
        for raw in LOCK.read_text(encoding="utf-8").splitlines():
            if raw.lstrip().startswith("#"):
                continue
            line = raw.split(" #", 1)[0].rstrip()
            if not line:
                continue
            opens = re.match(r"^([A-Za-z0-9_.-]+)==(\S+?)\s*(\\?)$", line)
            if opens:
                current = opens.group(1).lower()
                entries[current] = {"version": opens.group(2), "hashes": []}
                continued = bool(opens.group(3))
                continue
            if current and continued:
                # Capture the token, don't pre-filter it to well-formed hex: a regex that
                # only matches 64 hex chars SKIPS a truncated hash, and an entry with other
                # good hashes then looks fine while pip rejects the file. Shape is asserted
                # below, where a bad one can be reported. (Another survivor found this.)
                entries[current]["hashes"] += re.findall(r"--hash=sha256:(\S+)", line)
                continued = line.endswith("\\")
            else:
                current, continued = None, False
        return entries

    def test_the_lock_pins_exactly_the_expected_tree(self):
        got = {name: e["version"] for name, e in self._entries().items()}
        self.assertEqual(got, self.PINNED,
                         "the CI tool tree changed — regenerate the lock AND update this test, "
                         "so a bump is deliberate rather than whatever the index served")

    def test_every_pinned_package_carries_at_least_one_hash(self):
        for name, entry in self._entries().items():
            with self.subTest(package=name):
                self.assertTrue(entry["hashes"],
                                f"{name} is pinned by version alone — that is the defect #301 "
                                "exists to close, one row down")
                for h in entry["hashes"]:
                    self.assertRegex(h, r"^[0-9a-f]{64}$",
                                     f"{name} carries a malformed sha256 — pip rejects the "
                                     "whole lock on one, so this is not a cosmetic problem")

    def test_the_workflow_installs_from_the_lock_with_hashes_required(self):
        wf = WORKFLOW.read_text(encoding="utf-8")
        run = "\n".join(ln for ln in wf.splitlines() if not ln.lstrip().startswith("#"))
        self.assertIn("--require-hashes", run,
                      "pip accepts a lock without --require-hashes and ignores every hash in it")
        self.assertIn(".github/ci-tools.lock", run, "the workflow does not read the lock")

    def test_no_tool_is_re_resolved_outside_the_lock(self):
        # A second `pip install ruff==...` would defeat the lock by installing whatever the
        # index serves, under a name that looks pinned.
        wf = WORKFLOW.read_text(encoding="utf-8")
        loose = [ln.strip() for ln in wf.splitlines()
                 if not ln.lstrip().startswith("#")
                 and re.search(r"pip install(?!.*--require-hashes)", ln)]
        self.assertEqual(loose, [], "a tool is installed outside the hashed lock")
        self.assertNotIn("uvx ", wf,
                         "uvx resolves skills-ref's dependency tree at run time, which is the "
                         "unpinned path the lock replaced")


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
