#!/usr/bin/env python3
"""Contract tests for runtime/scripts/run_report.py — the proof-tier artifact binding.

REVIEW.md §2.2 / issue #259: before this, `proof: self-run` needed only a file under
docs/runs/ whose name and body mentioned the mission, so a three-line fabricated
report advanced a tier past every gate. These tests are the bypasses, run against
the checker: each one has to be refused.

The fixtures build real git repos, because the mechanism is "re-hash the recorded
paths at the recorded commit" — a fake that never touches git would test nothing.
"""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "run_report", ROOT / "runtime" / "scripts" / "run_report.py"
)
run_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_report)

INVENTORY_HEADING = "## Run-close integrity inventory (sha256)"


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, check=True,
    ).stdout.strip()


def _report(mission, tier, rev, manifest, verifier, inventory):
    rows = "\n".join(f"{digest}  {path}" for digest, path in inventory)
    return (
        f"# Run report — {mission} {tier}\n\n"
        f"RUN: mission={mission} tier={tier} inventory_at={rev} "
        f"manifest={manifest} verifier={verifier}\n\n"
        f"Ran verify.py against the manifest.\n\n"
        f"{INVENTORY_HEADING}\n\n```\n{rows}\n```\n"
    )


class RunReportBinding(unittest.TestCase):
    """One temp repo per test: a run directory, its manifest, a committed artifact."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _git(self.repo, "init", "-q", ".")
        _git(self.repo, "config", "user.email", "t@example.com")
        _git(self.repo, "config", "user.name", "t")
        self.run_dir = self.repo / "docs" / "runs" / "2026-01-01-demo-it-selfrun"
        self.run_dir.mkdir(parents=True)
        (self.run_dir / "build-manifest.json").write_text('{"unit": "u1"}\n', encoding="utf-8")
        (self.run_dir / "negctrl.txt").write_text("mutant KILLED\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "artifacts")
        self.rev = _git(self.repo, "rev-parse", "HEAD")
        self.manifest = "docs/runs/2026-01-01-demo-it-selfrun/build-manifest.json"
        self.nc = "docs/runs/2026-01-01-demo-it-selfrun/negctrl.txt"
        self.nc_sha = subprocess.run(
            ["git", "cat-file", "blob", f"{self.rev}:{self.nc}"],
            cwd=str(self.repo), stdout=subprocess.PIPE, check=True,
        ).stdout
        import hashlib
        self.nc_sha = hashlib.sha256(self.nc_sha).hexdigest()
        self.path = self.repo / "docs" / "runs" / "2026-01-01-demo-it-self-run.md"

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, **kw):
        args = dict(
            mission="demo-it", tier="self-run", rev=self.rev, manifest=self.manifest,
            verifier="GREEN", inventory=[(self.nc_sha, self.nc)],
        )
        args.update(kw)
        self.path.write_text(_report(**args), encoding="utf-8")
        return self.path

    def _check(self, mission="demo-it", tier="self-run"):
        return run_report.check_report(self.path, mission, tier, root=self.repo)

    # --- the shape that must pass ------------------------------------------
    def test_a_bound_report_passes(self):
        self._write()
        self.assertEqual(self._check(), [])

    def test_a_recorded_red_verifier_still_binds(self):
        # A solo run cannot manufacture an independent approver; recording that
        # RED is honest and must not cost the tier.
        self._write(verifier="RED")
        self.assertEqual(self._check(), [])

    # --- the bypasses ------------------------------------------------------
    def test_no_run_header_is_refused(self):
        self.path.write_text(
            f"# Run report — demo-it self-run\n\nIt ran. verify.py was green.\n\n"
            f"{INVENTORY_HEADING}\n\n```\n{self.nc_sha}  {self.nc}\n```\n",
            encoding="utf-8",
        )
        self.assertTrue(any("no 'RUN:' header" in e for e in self._check()), self._check())

    def test_two_run_headers_are_refused(self):
        self._write()
        self.path.write_text(
            self.path.read_text(encoding="utf-8")
            + f"\nRUN: mission=demo-it tier=self-run inventory_at={self.rev} "
              f"manifest={self.manifest} verifier=GREEN\n",
            encoding="utf-8",
        )
        self.assertTrue(any("'RUN:' headers" in e for e in self._check()), self._check())

    def test_missing_field_is_refused(self):
        self.path.write_text(
            "# Run report — demo-it self-run\n\nRUN: mission=demo-it tier=self-run\n",
            encoding="utf-8",
        )
        self.assertTrue(any("missing" in e for e in self._check()), self._check())

    def test_report_pointed_at_another_mission_is_refused(self):
        self._write()
        errs = self._check(mission="other-it")
        self.assertTrue(any("belongs to the mission that ran" in e for e in errs), errs)

    def test_tier_disagreeing_with_frontmatter_is_refused(self):
        self._write(tier="self-run")
        errs = self._check(tier="external-run")
        self.assertTrue(any("frontmatter claims external-run" in e for e in errs), errs)

    def test_unresolvable_commit_is_refused(self):
        self._write(rev="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertTrue(
            any("is not a commit in this repository" in e for e in self._check()), self._check()
        )

    def test_borrowed_manifest_from_another_run_is_refused(self):
        # The B2 bypass: fabricate a report and point it at a REAL other run's
        # artifacts. Everything hashes; nothing about it is this mission's run.
        other = self.repo / "docs" / "runs" / "2026-01-01-someone-else-selfrun"
        other.mkdir(parents=True)
        (other / "build-manifest.json").write_text('{"unit": "theirs"}\n', encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "other run")
        rev = _git(self.repo, "rev-parse", "HEAD")
        self._write(rev=rev, manifest="docs/runs/2026-01-01-someone-else-selfrun/build-manifest.json")
        errs = self._check()
        self.assertTrue(any("outside this run's own directory" in e for e in errs), errs)

    def test_inventory_of_only_borrowed_artifacts_is_refused(self):
        other = self.repo / "docs" / "runs" / "2026-01-01-someone-else-selfrun"
        other.mkdir(parents=True)
        borrowed = other / "artifact.txt"
        borrowed.write_text("theirs\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "other run")
        rev = _git(self.repo, "rev-parse", "HEAD")
        import hashlib
        digest = hashlib.sha256(b"theirs\n").hexdigest()
        self._write(
            rev=rev,
            inventory=[(digest, "docs/runs/2026-01-01-someone-else-selfrun/artifact.txt")],
        )
        errs = self._check()
        self.assertTrue(any("own directory" in e for e in errs), errs)

    def test_a_hash_that_does_not_re_derive_is_refused(self):
        self._write(inventory=[("0" * 64, self.nc)])
        errs = self._check()
        self.assertTrue(any("recorded 000000000000" in e for e in errs), errs)

    def test_inventory_naming_only_absent_paths_verifies_nothing(self):
        import hashlib
        self._write(inventory=[(hashlib.sha256(b"x").hexdigest(), "docs/runs/gone.txt")])
        errs = self._check()
        self.assertTrue(any("verified nothing" in e for e in errs), errs)

    def test_no_inventory_block_is_refused(self):
        self.path.write_text(
            f"# Run report — demo-it self-run\n\nRUN: mission=demo-it tier=self-run "
            f"inventory_at={self.rev} manifest={self.manifest} verifier=GREEN\n\n"
            "Ran verify.py. Artifacts retained elsewhere.\n",
            encoding="utf-8",
        )
        errs = self._check()
        self.assertTrue(any("integrity inventory" in e for e in errs), errs)

    def test_verifier_outcome_without_the_invocation_is_refused(self):
        text = _report("demo-it", "self-run", self.rev, self.manifest, "GREEN",
                       [(self.nc_sha, self.nc)]).replace("Ran verify.py against the manifest.", "It went fine.")
        self.path.write_text(text, encoding="utf-8")
        errs = self._check()
        self.assertTrue(any("never shows the verify.py invocation" in e for e in errs), errs)

    def test_unknown_verifier_outcome_is_refused(self):
        self._write(verifier="PROBABLY")
        errs = self._check()
        self.assertTrue(any("verifier=PROBABLY" in e for e in errs), errs)

    def test_missing_report_is_refused(self):
        errs = run_report.check_report(
            "docs/runs/never-written.md", "demo-it", "self-run", root=self.repo
        )
        self.assertTrue(any("does not exist" in e for e in errs), errs)


class LiveCatalog(unittest.TestCase):
    """The repo's own claims, checked by the same code CI runs."""

    def test_every_advanced_tier_binds(self):
        code = run_report.main([])
        self.assertEqual(code, 0, "a mission claims a tier its run report cannot re-derive")

    def test_ship_it_self_run_binds_at_its_recorded_commit(self):
        # The one report that does bind — five hashes re-derived from git objects.
        errs = run_report.check_report(
            "docs/runs/2026-08-28-ship-it-self-run.md", "ship-it", "self-run"
        )
        self.assertEqual(errs, [])

    def test_demoted_reports_are_kept_and_say_why(self):
        # Demoting is only honest if the record survives and explains itself.
        for name in (
            "2026-07-13-clean-sweep-self-run.md",
            "2026-07-13-review-it-external-run.md",
            "2026-07-16-oss-contribute-external-run.md",
        ):
            text = (ROOT / "docs" / "runs" / name).read_text(encoding="utf-8")
            self.assertIn("Evidence binding", text, f"{name} was demoted without saying why")


if __name__ == "__main__":
    unittest.main()
