#!/usr/bin/env python3
"""Contract tests for VF-Bench v0 (#79).

VF-Bench measures verifier SOUNDNESS (false-done rate), not agent capability. The property under
test: orca-fleet's sound verifier is fooled by NO trap (0% false-done), a self-scoring gate is
fooled by at least one (else there is no contrast), and the sound gate still passes a valid control
(it is not trivially always-RED).
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
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


class VFBenchAncestryLeg(unittest.TestCase):
    """#172: vf-bench scores exit codes only, so a RED verdict on the non-ancestor-sha trap would
    not by itself prove the ancestry leg fired. Pin the right reason: when the sound gate runs
    that trap, the verifier's fatals must include the ancestry error (a phantom head_sha also
    trips the real-commit leg — see the trap note — so both messages are asserted)."""

    @classmethod
    def setUpClass(cls):
        # The trap's ancestry leg runs against the AMBIENT repo (vf-bench cwd=ROOT by design);
        # check_ancestry itself skips with a NOTE when origin/<base> is absent, so the diagnostic
        # this test asserts only exists where refs/remotes/origin/main does. Skip there rather
        # than mutate the ambient clone's refs.
        r = subprocess.run(["git", "rev-parse", "--verify", "origin/main"],
                           capture_output=True, cwd=vfbench.ROOT)
        if r.returncode != 0:
            raise unittest.SkipTest("ambient repo has no refs/remotes/origin/main — "
                                    "check_ancestry's skip-NOTE semantics apply")

    def test_non_ancestor_trap_is_red_via_the_ancestry_leg(self):
        trap = next(t for t in vfbench.load_traps() if t["class"] == "non-ancestor-sha")
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(trap["manifest"], fh)
            path = fh.name
        try:
            r = subprocess.run(
                [sys.executable, str(vfbench.VERIFY), "--manifest", path,
                 "--contract-source", trap["contract_source"],
                 "--contract-digest", trap["contract_digest"],
                 "--unit-class", trap["unit_class"], "--base", trap["base"]],
                capture_output=True, text=True, cwd=vfbench.ROOT)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("not an ancestor of origin/main", r.stderr)
        self.assertIn("is not a real commit", r.stderr)


class VFBenchReviewLeg(unittest.TestCase):
    """#174: vf-bench scores exit codes only, so a RED verdict on the review-fetch-fail-closed
    trap would not by itself prove check_review ran past the pr.number guard. Pin the right
    reason twice: (1) with the ambient environment the trap fails CLOSED at the review fetch
    (the trap's repo owner contains an underscore, which GitHub usernames forbid, so the lookup
    404s even authenticated; without gh the same leg reports 'gh not on PATH' — both wordings
    carry 'cannot fetch reviews'), and (2) with a stubbed gh serving review pages the verdict is
    decided by review_ok ALONE — COMMENTED-only stays RED, an independent APPROVED at head_sha
    flips GREEN — so a regression that accepts COMMENTED reviews turns this trap into a
    false-done. The ancestry leg is #172's non-ancestor-sha trap — referenced, not duplicated."""

    @classmethod
    def setUpClass(cls):
        cls.trap = next(t for t in vfbench.load_traps() if t["class"] == "review-fetch-fail-closed")

    def _run_verify(self, env=None):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(self.trap["manifest"], fh)
            path = fh.name
        try:
            return subprocess.run(
                [sys.executable, str(vfbench.VERIFY), "--manifest", path,
                 "--contract-source", self.trap["contract_source"],
                 "--contract-digest", self.trap["contract_digest"],
                 "--unit-class", self.trap["unit_class"], "--repo", self.trap["repo"]],
                capture_output=True, text=True, cwd=vfbench.ROOT, env=env)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_review_trap_is_red_via_the_fail_closed_fetch(self):
        r = self._run_verify()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("no pr.number", r.stderr)  # the leg ran PAST the pr.number guard
        self.assertIn("cannot fetch reviews", r.stderr)  # and failed CLOSED at the fetch

    def test_review_trap_verdict_tracks_review_ok(self):
        head = self.trap["manifest"]["head_sha"]
        r = subprocess.run(["git", "cat-file", "-e", f"{head}^{{commit}}"], cwd=vfbench.ROOT)
        if r.returncode != 0:
            raise unittest.SkipTest("shallow clone without the trap's pinned commit — "
                                    "the GREEN half cannot run here")

        def env_with_stub(reviews):
            stub = (
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "endpoint = sys.argv[-1]\n"
                "if endpoint.endswith('/reviews'):\n"
                f"    print(json.dumps({json.dumps(reviews)}))\n"
                "elif '/pulls/' in endpoint:\n"
                "    print(json.dumps({'user': {'login': 'vf-author'}}))\n"
                "else:\n"
                "    sys.exit(1)\n"
            )
            d = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, d, True)
            p = Path(d) / "gh"
            p.write_text(stub, encoding="utf-8")
            p.chmod(0o755)
            return {**os.environ, "PATH": f"{d}{os.pathsep}{os.environ['PATH']}"}

        commented = [{"user": {"login": "vf-reviewer"}, "state": "COMMENTED", "commit_id": head}]
        approved = [{"user": {"login": "vf-reviewer"}, "state": "APPROVED", "commit_id": head}]
        r = self._run_verify(env=env_with_stub(commented))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("no INDEPENDENT APPROVED review at head_sha", r.stderr)
        r = self._run_verify(env=env_with_stub(approved))
        self.assertEqual(r.returncode, 0, f"every non-review check must pass: {r.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
