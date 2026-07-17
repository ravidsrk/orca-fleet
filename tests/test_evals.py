#!/usr/bin/env python3
"""
Contract tests for the orca-fleet eval layer.

Locks in:
- every mission has a valid per-skill evals.json (ported from marketingskills)
- the central routing eval exists and covers all eleven missions
- the eval runner can validate and score without errors
- the routing baseline stays above a minimum threshold
"""
import argparse
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EVALS = ROOT / "evals"

_spec = importlib.util.spec_from_file_location("eval", ROOT / "scripts" / "eval.py")
eval_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eval_mod)

EXPECTED_MISSIONS = {
    "ship-it", "clean-sweep", "oss-contribute", "harden-it", "speed-it",
    "modernize-it", "prove-it", "deflake-it", "review-it", "map-it", "root-cause",
}

ROUTING_MIN_SCORE = 0.60


class TestEvalInfrastructure(unittest.TestCase):

    def test_eval_script_is_executable(self):
        self.assertTrue((ROOT / "scripts" / "eval.py").exists())
        self.assertGreater((ROOT / "scripts" / "eval.py").stat().st_size, 200)

    def test_routing_eval_exists_and_is_valid_json(self):
        self.assertTrue((EVALS / "routing.json").exists())
        data = eval_mod.load_json(EVALS / "routing.json")
        self.assertIn("evals", data)
        self.assertIsInstance(data["evals"], list)
        self.assertGreater(len(data["evals"]), 0)

    def test_routing_eval_covers_all_missions(self):
        data = eval_mod.load_json(EVALS / "routing.json")
        covered = {ev["expected_mission"] for ev in data["evals"] if ev.get("type") == "positive"}
        self.assertEqual(covered, EXPECTED_MISSIONS)

    def test_every_mission_has_per_skill_evals(self):
        for d in sorted(SKILLS.iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            with self.subTest(mission=d.name):
                self.assertTrue(
                    (d / "evals" / "evals.json").exists(),
                    f"{d.name} is missing evals/evals.json",
                )

    def test_every_skill_eval_has_valid_schema(self):
        errors = []
        for d in sorted(SKILLS.iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            errors.extend(eval_mod.validate_skill_eval(d))
        self.assertEqual(errors, [], f"schema errors: {errors}")

    def test_validate_subcommand_passes(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "eval.py"), "validate"],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, f"stderr: {r.stderr}\nstdout: {r.stdout}")

    def test_run_routing_meets_minimum_score(self):
        result = eval_mod.run_routing_eval()
        self.assertGreaterEqual(
            result["score"], ROUTING_MIN_SCORE,
            f"routing score {result['score']:.0%} below minimum {ROUTING_MIN_SCORE:.0%}; "
            f"failures: {result['failures']}",
        )

    def test_run_skills_eval_has_no_errors(self):
        result = eval_mod.run_skills_eval()
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["skill_evals"]), len(EXPECTED_MISSIONS))
        self.assertGreaterEqual(result["total_evals"], len(EXPECTED_MISSIONS) * 2)

    def test_run_routing_eval_returns_error_on_bad_json(self):
        with patch.object(eval_mod, "load_json", side_effect=ValueError("boom")):
            result = eval_mod.run_routing_eval()
        self.assertIn("error", result)
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["score"], 0.0)

    def test_run_routing_eval_returns_error_on_missing_evals_key(self):
        with patch.object(eval_mod, "load_json", return_value={}):
            result = eval_mod.run_routing_eval()
        self.assertIn("error", result)
        self.assertIn("missing or non-list 'evals'", result["error"])
        self.assertEqual(result["total"], 0)

    def test_run_routing_eval_returns_error_on_missing_entry_keys(self):
        with patch.object(eval_mod, "load_json", return_value={"evals": [{"id": 1}]}):
            result = eval_mod.run_routing_eval()
        self.assertIn("error", result)
        self.assertIn("missing", result["error"])
        self.assertEqual(result["total"], 0)

    def _routing_errors(self, missions, routing_data):
        # Issue #48 harness: a synthetic catalog + routing.json, so coverage is
        # provably keyed to skills/ dirs and not to the MISSION_TRIGGERS dict.
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            for m in missions:
                (skills / m).mkdir(parents=True)
                (skills / m / "SKILL.md").write_text("x", encoding="utf-8")
            routing = Path(tmp) / "routing.json"
            routing.write_text(json.dumps(routing_data), encoding="utf-8")
            with patch.object(eval_mod, "ROOT", Path(tmp)), \
                 patch.object(eval_mod, "SKILLS_DIR", skills), \
                 patch.object(eval_mod, "ROUTING_EVAL", routing):
                return eval_mod.validate_routing_eval()

    def test_new_mission_dir_without_routing_example_fails(self):
        errors = self._routing_errors(["brand-new-mission"], {"evals": []})
        self.assertTrue(any("brand-new-mission" in e for e in errors), errors)

    def test_new_mission_dir_with_routing_example_passes(self):
        errors = self._routing_errors(["brand-new-mission"], {"evals": [{
            "id": 1, "prompt": "do the new thing",
            "expected_mission": "brand-new-mission",
            "type": "positive", "reason": "direct trigger",
        }]})
        self.assertEqual(errors, [])

    def test_cmd_run_reports_routing_json_error(self):
        bad_result = {
            "total": 0, "correct": 0, "score": 0.0,
            "failures": [], "error": "malformed routing.json",
        }
        captured = io.StringIO()
        with patch.object(eval_mod, "run_routing_eval", return_value=bad_result):
            with patch.object(sys, "stdout", captured):
                args = argparse.Namespace(suite="routing", threshold=0.0)
                code = eval_mod.cmd_run(args)
        self.assertEqual(code, 1)
        self.assertIn("Routing eval error", captured.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
