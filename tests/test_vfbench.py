#!/usr/bin/env python3
"""Contract tests for VF-Bench v0 (#79).

VF-Bench measures verifier SOUNDNESS (false-done rate), not agent capability. The property under
test: orca-fleet's sound verifier is fooled by NO trap (0% false-done), a self-scoring gate is
fooled by at least one (else there is no contrast), and the sound gate still passes a valid control
(it is not trivially always-RED).
"""
import contextlib
import importlib.util
import io
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
        # #163: the wrong-sha trap's RED verdict rests on verify.py's git commit-existence leg,
        # which degrades to a NOTE outside a git work tree — there the trap flips GREEN and the
        # soundness score silently measures nothing. Skip loudly instead of grading ambient state.
        r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, cwd=vfbench.ROOT)
        if r.returncode != 0:
            raise unittest.SkipTest("vf-bench traps rely on the ambient git clone — verify.py's "
                                    "commit-existence leg is NOTE-skipped outside one")
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

    def test_sound_gate_passes_the_mutation_valid_control(self):
        # #257: the report-only control only exercises the scope leg. THIS one drives every
        # mutation authority at once — an executed revert, an independent APPROVED review, a
        # pinned artifact inventory, a fresh commands ledger — so "not always-RED" is proven for
        # the class docs/reviews/2026-09-10-review.md's bypass log broke.
        rows = {r["id"]: r for r in self.res["orca-fleet verify.py (sound)"]["rows"]}
        self.assertIn("mutation-valid-control-1", rows,
                      "the mutation-class positive control was skipped or dropped")
        self.assertEqual(rows["mutation-valid-control-1"]["verdict"], "GREEN",
                         "a real mutation unit with an EXECUTED negative control must pass")

    def test_waiver_lane_traps_are_red(self):
        # #256: dark-eligible and no-gh both waive the review; with a merely-READ control they
        # must be RED. These are docs/reviews/2026-09-10-review.md A1/A2/A4/A6/A9 in the corpus.
        rows = {r["id"]: r for r in self.res["orca-fleet verify.py (sound)"]["rows"]}
        for trap_id in ("fabricated-nc-dark-eligible-1", "fabricated-nc-no-gh-1"):
            self.assertEqual(rows[trap_id]["verdict"], "RED", trap_id)

    def test_readme_result_table_matches_computed(self):
        # #125: the hand-typed result table must match the computed corpus (was a stale 4/4·0/4).
        import re
        if self.res["orca-fleet verify.py (sound)"]["skipped"]:
            self.skipTest("traps were skipped on this checkout — the corpus totals the README "
                          "pins are the FULL-clone ones (see test_shallow_skips_are_named)")
        readme = (ROOT / "bench" / "vf-bench" / "README.md").read_text(encoding="utf-8")
        naive, sound = self.res["self-scoring (naive)"], self.res["orca-fleet verify.py (sound)"]
        self.assertRegex(readme, rf"self-scoring \(naive\)\s*\|\s*{naive['false_done']}/{naive['red_total']}\b")
        self.assertRegex(readme, rf"verify\.py.*\|\s*{sound['false_done']}/{sound['red_total']}\b")


class VFBenchShallowSkips(unittest.TestCase):
    """#257 / docs/reviews/2026-09-10-review.md P2 item 22: a trap that pins a real commit cannot be scored on a shallow
    clone. It must be SKIPPED BY NAME — in the corpus report and in --json — never silently
    scored, because a degraded leg reads as a RED the gate did not earn."""

    def test_skip_reason_names_the_missing_commit(self):
        trap = {"id": "x", "class": "y", "requires_commits": ["0" * 40]}
        reason = vfbench.skip_reason(trap)
        self.assertIsNotNone(reason)
        self.assertIn("shallow clone", reason)
        self.assertIn("0" * 12, reason)

    def test_no_skip_when_the_commit_is_present(self):
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                              cwd=vfbench.ROOT)
        if head.returncode != 0:
            raise unittest.SkipTest("no ambient git clone")
        self.assertIsNone(vfbench.skip_reason({"requires_commits": [head.stdout.strip()]}))

    def test_review_leg_trap_declares_its_pinned_commits(self):
        trap = next(t for t in vfbench.load_traps() if t["class"] == "review-fetch-fail-closed")
        self.assertEqual(sorted(trap["requires_commits"]),
                         sorted([trap["manifest"]["base_sha"], trap["manifest"]["head_sha"]]))

    def test_report_names_skipped_traps(self):
        rows = {"id": "pinned-trap-1", "class": "review-fetch-fail-closed",
                "reason": "shallow clone: pinned commit deadbeefdead is not in this checkout"}
        res = {"g": {"false_done": 0, "red_total": 1, "rate": 0.0, "rows": [], "skipped": [rows]}}
        buf = io.StringIO()
        orig = vfbench.run
        vfbench.run = lambda: res
        try:
            with contextlib.redirect_stdout(buf):
                vfbench.main([])
        finally:
            vfbench.run = orig
        out = buf.getvalue()
        self.assertIn("NOT SCORED", out)
        self.assertIn("pinned-trap-1", out)
        self.assertIn("fetch-depth: 0", out)


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
    trips the real-commit leg — see the trap note — so both messages are asserted).

    Hermetic: check_ancestry reads origin/<base> from cwd, so this test builds a temp repo with
    refs/remotes/origin/main instead of skipping when the ambient clone is a shallow CI checkout
    (#201 review). #267 refuses evidence paths outside the toplevel, so the trap's contract fixture
    is COPIED into that temp repo and named relatively — the coordinator's contract has to live in
    the tree the verifier is auditing."""

    def test_non_ancestor_trap_is_red_via_the_ancestry_leg(self):
        trap = next(t for t in vfbench.load_traps() if t["class"] == "non-ancestor-sha")
        tmp = Path(tempfile.mkdtemp())
        try:
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp,
                           check=True, capture_output=True)
            (tmp / "README").write_text("x\n", encoding="utf-8")
            contract_rel = "contract.md"
            (tmp / contract_rel).write_bytes(
                (vfbench.ROOT / trap["contract_source"]).read_bytes())
            subprocess.run(["git", "add", "-A"], cwd=tmp, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                            "commit", "-qm", "init"], cwd=tmp, check=True, capture_output=True)
            subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
                           cwd=tmp, check=True, capture_output=True)
            path = tmp / "manifest.json"
            path.write_text(json.dumps(trap["manifest"]), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(vfbench.VERIFY), "--manifest", str(path),
                 "--contract-source", contract_rel,
                 "--contract-digest", trap["contract_digest"],
                 "--unit-class", trap["unit_class"], "--base", trap["base"]],
                capture_output=True, text=True, cwd=tmp)
        finally:
            shutil.rmtree(tmp, True)
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
        # Aggregation, not fail-fast: a missing trap SHA still runs check_review, so
        # this pin holds on a shallow clone. Skipping would hide a fetch-leg regression.
        r = self._run_verify()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("no pr.number", r.stderr)  # the leg ran PAST the pr.number guard
        self.assertIn("cannot fetch reviews", r.stderr)  # and failed CLOSED at the fetch

    def test_review_trap_verdict_tracks_review_ok(self):
        head = self.trap["manifest"]["head_sha"]
        # #257: the same named skip vfbench.py reports — a shallow checkout cannot score a trap
        # pinned to a real commit, and saying so beats measuring the checkout.
        reason = vfbench.skip_reason(self.trap)
        if reason:
            raise unittest.SkipTest(f"{reason} — the GREEN half cannot run here; "
                                    "CI must check out with fetch-depth: 0")

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


class TheFourRefusedControlClassesAreSampled(unittest.TestCase):
    """#306: "0% false-done" only means something if the suite samples what actually gets through.

    The bypass log landed nine of thirteen gaming manifests against this mechanism, so the number
    was measuring the traps that had been chosen, not the gate's strength. These four are the
    classes the review found, and building them found a real gap: the path bind ran only on the
    --execute-nc leg, so a NARRATED decoy path or oracle revert passed. The bench read 2/17
    false-done until that was fixed.
    """

    TRAPS = ROOT / "bench" / "vf-bench" / "traps"
    REQUIRED = {"decoy-path", "oracle-mutation", "stillborn-mutant", "grep-command",
                "decoy-hand-diff"}

    def _traps(self):
        return {t["class"]: t for t in
                (json.loads(p.read_text(encoding="utf-8")) for p in self.TRAPS.glob("*.json"))}

    def test_every_refused_class_has_a_trap(self):
        missing = sorted(self.REQUIRED - set(self._traps()))
        self.assertEqual(missing, [], "a control class the review found is no longer sampled")

    def test_each_is_expected_to_be_refused(self):
        for name, trap in self._traps().items():
            if name in self.REQUIRED:
                with self.subTest(trap=name):
                    self.assertEqual(trap["sound_expected"], "RED",
                                     "a gaming manifest the gate must refuse")
                    self.assertEqual(trap.get("unit_class"), "mutation")

    def test_the_decoy_and_oracle_traps_stay_in_the_narrated_lane(self):
        """Executed, both are no-ops that #255 refuses — which is the right verdict for the wrong
        reason, and would have passed before #280 existed. Narrated, the static path bind is the
        only thing between the manifest and a GREEN, which is what these traps are for."""
        for name in ("decoy-path", "oracle-mutation"):
            with self.subTest(trap=name):
                self.assertFalse(self._traps()[name].get("execute_nc"),
                                 "executed, this trap measures #255 rather than the path bind")

    # The refusal each trap must earn. A RED alone is not evidence the benchmark still measures
    # the advertised bypass: a trap refused as MALFORMED, or by an unrelated prerequisite, scores
    # the same 0/18 and says nothing (PR #308 review, P2). This is not hypothetical — the
    # stillborn trap shipped in a first draft refused for exactly that reason, its diff in a
    # `negative_control.diff` field the manifest reader rejects, never reaching the check it names.
    REFUSAL = {
        "decoy-path": "which base_sha..head_sha does not change",
        "oracle-mutation": "which is a TEST path",
        "stillborn-mutant": "STILLBORN MUTANT",
        "grep-command": "produced NO output at all",
        "decoy-hand-diff": "the hand mutant's diff names",
    }

    def test_each_trap_is_refused_for_the_reason_it_exists_to_test(self):
        """Run the gate and read WHY, not just the verdict."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_vfbench_reasons", ROOT / "bench" / "vf-bench" / "vfbench.py")
        vb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vb)
        traps = self._traps()
        for name, want in self.REFUSAL.items():
            with self.subTest(trap=name):
                self.assertIn(name, traps, "the trap is gone")
                fails = self._refusals(vb, traps[name])
                self.assertTrue(fails, f"{name} was not refused at all")
                self.assertTrue(
                    any(want in f for f in fails),
                    f"{name} was refused, but not for its own reason.\n"
                    f"  wanted a line containing: {want!r}\n"
                    f"  got: " + "\n       ".join(f[:160] for f in fails))

    @staticmethod
    def _refusals(vb, trap):
        """The FAIL lines verify.py emits for one fixture-backed trap."""
        import os
        import subprocess
        import sys
        import tempfile
        holder = Path(tempfile.mkdtemp(prefix="vfbench-reason-"))
        try:
            repo = holder / "repo"
            facts = vb.build_mutation_fixture(repo)
            (repo / "vf-manifest.json").write_text(
                json.dumps(vb._render(trap["manifest"], facts)), encoding="utf-8")
            cmd = [sys.executable, str(vb.VERIFY), "--manifest", str(repo / "vf-manifest.json"),
                   "--contract-source", "contract.md",
                   "--contract-digest", facts["contract_digest"],
                   "--unit-class", trap.get("unit_class", "mutation")]
            if trap.get("lighting"):
                cmd += ["--lighting", trap["lighting"]]
            if trap.get("execute_nc"):
                cmd.append("--execute-nc")
                if trap.get("nc_command"):
                    cmd += ["--nc-command", vb._render(trap["nc_command"], facts)]
            if trap.get("repo"):
                cmd += ["--repo", trap["repo"]]
            env = dict(os.environ)
            if trap.get("gh_stub"):
                env["PATH"] = (vb._gh_stub(holder / "bin", facts["head_sha"])
                               + os.pathsep + env["PATH"])
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env)
            return [ln.strip() for ln in (r.stdout + r.stderr).splitlines()
                    if ln.startswith("FAIL:")]
        finally:
            shutil.rmtree(holder, ignore_errors=True)

    def test_the_stillborn_trap_quotes_a_real_diff_in_its_artifact(self):
        # It first carried the diff in a `negative_control.diff` field, which got the manifest
        # refused as MALFORMED — a trap refused for the wrong reason measures nothing.
        trap = self._traps()["stillborn-mutant"]
        nc = trap["manifest"]["negative_control"]
        self.assertEqual(nc["tool"], "hand")
        self.assertNotIn("diff", nc, "the diff belongs in the artifact, where verify.py reads it")
        self.assertTrue(nc["artifact"].endswith("nc-stillborn.txt"))
        vf = (ROOT / "bench" / "vf-bench" / "vfbench.py").read_text(encoding="utf-8")
        self.assertIn("FIXTURE_NC_STILLBORN", vf, "the fixture no longer writes that artifact")
        self.assertIn("nc_stillborn_sha256", vf, "the artifact's digest is not exposed as a fact")


if __name__ == "__main__":
    unittest.main(verbosity=2)
