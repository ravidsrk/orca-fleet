#!/usr/bin/env python3
"""Contract tests for VF-Bench v0 (#79).

VF-Bench measures verifier SOUNDNESS (false-done rate), not agent capability. The property under
test: orca-fleet's sound verifier is fooled by NO trap (0% false-done), a self-scoring gate is
fooled by at least one (else there is no contrast), and the sound gate still passes a valid control
(it is not trivially always-RED).
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("vfbench", ROOT / "bench" / "vf-bench" / "vfbench.py")
vfbench = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vfbench)


class VFBenchCorpus(unittest.TestCase):
    def test_corpus_nonempty_and_well_formed(self):
        traps = vfbench.load_traps()
        self.assertGreaterEqual(len(traps), 4)
        for t in traps:
            for k in ("id", "class", "sound_expected", "manifest"):
                self.assertIn(k, t, t)
            self.assertIn(t["sound_expected"], ("RED", "GREEN"))


class VFBenchSoundness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = vfbench.run()

    def test_sound_gate_scores_zero_false_done(self):
        sound = self.res["orca-fleet verify.py (sound)"]
        self.assertEqual(sound["false_done"], 0, "the sound verifier must not be fooled by any trap")

    def test_naive_self_scorer_is_fooled(self):
        naive = self.res["self-scoring (naive)"]
        self.assertGreater(naive["false_done"], 0, "a self-scoring gate must be fooled (else no contrast)")

    def test_sound_gate_passes_the_valid_control(self):
        rows = {r["id"]: r for r in self.res["orca-fleet verify.py (sound)"]["rows"]}
        self.assertEqual(rows["valid-control-1"]["verdict"], "GREEN", "sound gate must not be always-RED")

    def test_readme_result_table_matches_computed(self):
        # #125: the hand-typed result table must match the computed corpus (was a stale 4/4·0/4).
        import re
        readme = (ROOT / "bench" / "vf-bench" / "README.md").read_text(encoding="utf-8")
        naive, sound = self.res["self-scoring (naive)"], self.res["orca-fleet verify.py (sound)"]
        self.assertRegex(readme, rf"self-scoring \(naive\)\s*\|\s*{naive['false_done']}/{naive['red_total']}\b")
        self.assertRegex(readme, rf"verify\.py.*\|\s*{sound['false_done']}/{sound['red_total']}\b")


class VFBenchForwarding(unittest.TestCase):
    """#140 review: base/repo (and unit_class) are best-effort at the verdict level, so a regression
    that drops or swaps their forwarding into verify.py would pass unnoticed by verdicts alone.
    Assert the argv the sound gate builds carries every dispatch input, correctly paired."""

    def test_sound_gate_forwards_dispatch_inputs(self):
        captured = {}

        class _R:
            returncode = 0

        def fake_run(cmd, *a, **k):
            captured["cmd"] = cmd
            return _R()

        orig = vfbench.subprocess.run
        vfbench.subprocess.run = fake_run
        try:
            vfbench.sound_gate({
                "manifest": {"head_sha": "H"},
                "contract_source": "c@ref", "contract_digest": "sha256:x",
                "unit_class": "mutation", "base": "main", "repo": "o/r",
            })
        finally:
            vfbench.subprocess.run = orig
        cmd = captured["cmd"]
        for flag, val in (("--unit-class", "mutation"), ("--base", "main"), ("--repo", "o/r"),
                          ("--contract-source", "c@ref"), ("--contract-digest", "sha256:x")):
            self.assertIn(flag, cmd)
            self.assertEqual(cmd[cmd.index(flag) + 1], val, f"{flag} value not forwarded")


class VFBenchRobustness(unittest.TestCase):
    """#100 review: the harness must not leak temp manifests, and a broken verifier (exit 1) must not
    be scored as a caught trap."""

    def test_sound_gate_removes_temp_manifest(self):
        captured = {}

        class _R:
            returncode = 2
            stderr = ""

        def fake_run(cmd, *a, **k):
            captured["path"] = cmd[cmd.index("--manifest") + 1]
            return _R()

        orig = vfbench.subprocess.run
        vfbench.subprocess.run = fake_run
        try:
            vfbench.sound_gate({"manifest": {"head_sha": "H"}})
        finally:
            vfbench.subprocess.run = orig
        self.assertFalse(Path(captured["path"]).exists(), "sound_gate leaked its temp manifest")

    def test_sound_gate_raises_on_broken_verifier(self):
        class _R:
            returncode = 1  # usage/dependency error — not a 0/2 verdict
            stderr = "dependency: git not on PATH"

        orig = vfbench.subprocess.run
        vfbench.subprocess.run = lambda *a, **k: _R()
        try:
            with self.assertRaises(RuntimeError):
                vfbench.sound_gate({"manifest": {"head_sha": "H"}})
        finally:
            vfbench.subprocess.run = orig


if __name__ == "__main__":
    unittest.main(verbosity=2)
