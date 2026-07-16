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
    "ship-it", "clean-sweep", "oss-contribute", "harden-it", "speed-it",
    "modernize-it", "prove-it", "deflake-it", "review-it", "map-it", "root-cause",
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

    def test_exactly_the_expected_missions(self):
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
        # Every callable protocol must be composed by at least one mission, via an
        # EXPLICIT reference form: `name` backticked or name.md. Prose coincidence is
        # not a composition — "landed" containing "land", or a bare phase name in a
        # description, must not keep an orphan alive.
        bodies = "\n".join((d / "SKILL.md").read_text(encoding="utf-8") for d in mission_dirs())
        for proto_dir in (PLAYBOOKS, RUNTIME):
            for f in proto_dir.glob("*.md"):
                stem = re.escape(f.stem)
                self.assertRegex(
                    bodies,
                    rf"`{stem}`|(?<![\w-]){stem}\.md(?![\w.-])",
                    f"{proto_dir.name}/{f.name} is composed by no mission (orphan)",
                )

    def test_wip_cap_is_a_ledger_header_contract(self):
        # The 2026-07-15 chimely run dispatched a 4-builder wave with no WIP field in
        # its ledger header — the cap existed only as doctrine, so nothing held the
        # wave. The header template, the producer-side policy, and the row-flag rule
        # must all carry the contract; an edit that drops any one of them re-opens it.
        header_spec = (RUNTIME / "liveness-resume.md").read_text(encoding="utf-8")
        self.assertIn(
            "WIP: builders=", header_spec,
            "liveness-resume.md header template lost the WIP field",
        )
        budget = (RUNTIME / "attention-budget.md").read_text(encoding="utf-8")
        self.assertRegex(
            budget, r"(?i)required ledger-header field",
            "attention-budget.md no longer declares WIP a required header field",
        )
        ledger = (RUNTIME / "ledger-contract.md").read_text(encoding="utf-8")
        self.assertRegex(
            ledger, r"(?i)row is the record",
            "ledger-contract.md lost the row-is-the-record rule",
        )

    def test_pm_parses_heartbeat_interleaved_stream(self):
        # pm.py's whole job: decode message batches from a stream that interleaves
        # _heartbeat objects and malformed segments, and print each message WITH its id
        # (reply --id depends on it).
        import tempfile, os
        stream = (
            '{"_heartbeat": true}\n'
            '{"result": {"messages": [{"id": "msg-42", "from_handle": "w1", '
            '"type": "worker_done", "subject": "done", "body": "b", "payload": null}]}}\n'
            "this line is not json\n"
            '{"_heartbeat": true}\n'
        )
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(stream)
            path = fh.name
        try:
            r = subprocess.run(
                [sys.executable, str(RUNTIME / "scripts" / "pm.py"), path],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("MESSAGES: 1", r.stdout)
            self.assertIn("msg-42", r.stdout, "message id must be printed (reply --id needs it)")
            self.assertIn("skipped 1 malformed segment", r.stderr)
        finally:
            os.unlink(path)

    def test_runtime_scripts_present_and_executable_shape(self):
        # The shared tooling must exist, be non-trivial, be executable, and actually parse —
        # a zero-byte or syntax-broken script must fail here, not mid-run.
        import os
        for script in ("spawn_worker.sh", "preflight.py", "pm.py"):
            p = RUNTIME / "scripts" / script
            self.assertTrue(p.exists(), f"runtime/scripts/{script} missing")
            self.assertGreater(p.stat().st_size, 200, f"{script} is suspiciously small")
            self.assertTrue(os.access(p, os.X_OK), f"{script} is not executable")
            if script.endswith(".py"):
                import ast
                ast.parse(p.read_text(encoding="utf-8"))
            else:
                r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"bash -n {script}: {r.stderr}")

    def test_every_mission_declares_proof_status(self):
        # Honesty gate: the predecessor presented 12 missions with 2 proven and died
        # of it. Every mission states how proven it is; the validator enforces the
        # evidence link when a mission claims more than doctrine.
        for d in mission_dirs():
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(
                text, r"(?m)^proof: (doctrine-only|self-run|external-run)$",
                f"{d.name} declares no proof status",
            )

    def test_budget_boundary_not_off_by_one(self):
        # Greptile P1 on PR #5: text.count("\n")+1 overcounts newline-terminated files
        # by one, silently shrinking every cap. A mission of EXACTLY the cap's lines
        # (POSIX newline-terminated) must pass the budget check.
        import importlib.util, tempfile, shutil
        spec = importlib.util.spec_from_file_location("v", ROOT / "scripts" / "validate.py")
        v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v)
        d = Path(tempfile.mkdtemp()) / "cap-mission"
        d.mkdir()
        header = (
            "---\nname: cap-mission\ndescription: x. Use when testing.\n"
            "proof: doctrine-only\n---\n\nComposes `diagnose`.\n"
        )
        pad = v.MISSION_MAX_LINES - len(header.splitlines())
        (d / "SKILL.md").write_text(header + "b\n" * pad)  # exactly MISSION_MAX_LINES lines
        try:
            errors = v.validate_skill(d, v.known_protocol_names())
            budget_errors = [e for e in errors if "instruction budget" in e]
            self.assertEqual(
                budget_errors, [],
                f"a file of exactly {v.MISSION_MAX_LINES} lines must not breach the cap",
            )
        finally:
            shutil.rmtree(d.parent)

    def test_runtime_scripts_never_interpolate_code(self):
        # The predecessor shipped a P0 RCE by interpolating values into `python -c`
        # (live even under --dry-run). Values pass as argv or heredoc stdin, never
        # inside a double-quoted code string; no eval.
        for f in sorted((RUNTIME / "scripts").iterdir()):
            if f.suffix not in (".sh", ".py"):
                continue
            text = f.read_text(encoding="utf-8")
            self.assertNotRegex(
                text, r"python3? -c \"",
                f"{f.name}: python -c with a double-quoted (interpolatable) code string",
            )
            self.assertNotRegex(
                text, r"\beval[ (]",
                f"{f.name}: eval on constructed input",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
