#!/usr/bin/env python3
"""
Contract tests for the orca-fleet architecture (ARCHITECTURE.md).

These lock in the invariants that justify the repo existing separately from a pile
of vendor-named skills. They use only the standard library. Run:

    python3 -m unittest discover -s tests -v
    # or
    python3 tests/test_architecture.py
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
PLAYBOOKS = ROOT / "playbooks"
RUNTIME = ROOT / "runtime"

# The upstream packs are sources of recipes, never the name of a mission. A mission
# named for its ingredient is the exact anti-pattern this repo removes.
VENDOR_TOKENS = ("matt", "gstack", "addy", "osmani", "garry", "orca", "fleet", "swarm")

EXPECTED_MISSIONS = {
    "ship-it", "clean-sweep", "harden-it", "speed-it", "modernize-it",
    "prove-it", "deflake-it", "review-it", "map-it", "root-cause",
}


def mission_dirs():
    return [d for d in sorted(SKILLS.iterdir())
            if d.is_dir() and not d.name.startswith((".", "_"))]


def frontmatter_description(text):
    # crude but sufficient: pull the description block from YAML frontmatter
    m = re.search(r"(?ms)^description:\s*>-?\s*\n(.*?)^\w", text)
    if m:
        return " ".join(l.strip() for l in m.group(1).splitlines() if l.strip())
    m = re.search(r"(?m)^description:\s*(.+)$", text)
    return m.group(1).strip() if m else ""


class TestArchitecture(unittest.TestCase):

    def test_validator_passes(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, f"validate.py failed:\n{r.stdout}\n{r.stderr}")

    def test_exactly_the_ten_missions(self):
        found = {d.name for d in mission_dirs()}
        self.assertEqual(found, EXPECTED_MISSIONS)

    def test_missions_are_outcome_named_not_vendor_named(self):
        for d in mission_dirs():
            for tok in VENDOR_TOKENS:
                self.assertNotIn(
                    tok, d.name,
                    f"mission '{d.name}' is named for an ingredient ('{tok}'), "
                    f"not an outcome — see ARCHITECTURE.md",
                )

    def test_three_layer_separation(self):
        # Only skills/ may contain SKILL.md. Playbooks and runtime are callable, not
        # discoverable — a SKILL.md under them recreates routing collisions.
        for layer in (PLAYBOOKS, RUNTIME):
            leaks = list(layer.rglob("SKILL.md"))
            self.assertEqual(leaks, [], f"SKILL.md leaked into {layer.name}/: {leaks}")

    def test_every_mission_has_convergence_proof_and_anti_patterns(self):
        # The evidence-based definition of done and the failure catalog are the
        # discipline that made clean-sweep / spec-to-ship reliable.
        for d in mission_dirs():
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(
                text, r"(?i)convergence proof|definition of done",
                f"{d.name} has no convergence proof / definition of done",
            )
            self.assertRegex(text, r"(?im)^##\s*Anti-patterns",
                             f"{d.name} has no Anti-patterns section")

    def test_every_description_has_a_use_when_trigger(self):
        for d in mission_dirs():
            desc = frontmatter_description((d / "SKILL.md").read_text(encoding="utf-8"))
            self.assertRegex(
                desc.lower(), r"use when|use for|use to",
                f"{d.name} description has no 'Use when' trigger phrase",
            )

    def test_no_orphan_playbooks_or_runtime_policies(self):
        # Every callable protocol must be composed by at least one mission; a protocol
        # no mission uses is dead weight the catalog silently carries.
        bodies = "\n".join((d / "SKILL.md").read_text(encoding="utf-8") for d in mission_dirs())
        for proto_dir in (PLAYBOOKS, RUNTIME):
            for f in proto_dir.glob("*.md"):
                self.assertIn(
                    f.stem, bodies,
                    f"{proto_dir.name}/{f.name} is composed by no mission (orphan)",
                )

    def test_runtime_scripts_present_and_executable_shape(self):
        # The shared tooling missions dispatch with must exist.
        for script in ("spawn_worker.sh", "preflight.py", "pm.py"):
            self.assertTrue((RUNTIME / "scripts" / script).exists(),
                            f"runtime/scripts/{script} missing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
