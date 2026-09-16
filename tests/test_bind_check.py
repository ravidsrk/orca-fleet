#!/usr/bin/env python3
"""Contract tests for scripts/bind_check.py — the per-PR submission intake.

The fixtures build real git repos, because the mechanism under test starts
from `git merge-base`/`git diff` of the PR range: a fake that never touches
git would test nothing. The bound-report recipe mirrors
tests/test_run_report.py's (hand-written commands[] record naming a real
tree is the test convention there, not the guide's evidence-run path).
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("bind_check", ROOT / "scripts" / "bind_check.py")
bind_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bind_check)

MISSION = "demo-it"
TIER = "self-run"
DATE = "2026-01-02"
RUN_DIR = f"docs/runs/{DATE}-{MISSION}-selfrun"
MANIFEST = f"{RUN_DIR}/build-manifest.json"
REPORT = f"docs/runs/{DATE}-{MISSION}-self-run.md"
ENVELOPE = f"docs/reports/{MISSION}-selfrun/README.md"

SKILL = (
    "---\nname: demo-it\ndescription: fixture mission for bind-check tests\n"
    "metadata:\n  proof: doctrine-only\n---\n# demo-it\n"
)


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, check=True,
    ).stdout.strip()


def _commit(repo, message):
    _git(repo, "add", "-A")
    _git(repo, "-c", "commit.gpgsign=false", "commit", "-qm", message)


def _blob_sha(repo, rev, path):
    blob = subprocess.run(
        ["git", "cat-file", "blob", f"{rev}:{path}"],
        cwd=str(repo), stdout=subprocess.PIPE, check=True,
    ).stdout
    return hashlib.sha256(blob).hexdigest()


def _report(rev, manifest_blob_sha, nc_blob_sha, manifest=MANIFEST,
            mission=MISSION, tier=TIER, verifier="GREEN"):
    return (
        f"# Run report — {mission} {tier}\n\n"
        f"RUN: mission={mission} tier={tier} inventory_at={rev} "
        f"manifest={manifest} verifier={verifier}\n\n"
        "## Verifier outcome (recorded exactly)\n\n"
        f"    python3 runtime/scripts/verify.py --manifest {manifest} --unit-class mutation\n"
        f"    exit {0 if verifier == 'GREEN' else 2}\n\n"
        "## Run-close integrity inventory (sha256)\n\n"
        "```\n"
        f"{manifest_blob_sha}  {manifest}\n"
        f"{nc_blob_sha}  docs/runs/{DATE}-{mission}-selfrun/negctrl.txt\n"
        "```\n"
    )


class BindCheckPrRange(unittest.TestCase):
    """One temp repo per test: a base commit, then the PR's commits."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.repo = Path(self._tmp.name).resolve()
        _git(self.repo, "init", "-q", ".")
        _git(self.repo, "config", "user.email", "t@example.com")
        _git(self.repo, "config", "user.name", "t")
        _git(self.repo, "config", "commit.gpgsign", "false")
        (self.repo / "skills" / MISSION).mkdir(parents=True)
        (self.repo / "skills" / MISSION / "SKILL.md").write_text(SKILL, encoding="utf-8")
        _commit(self.repo, "base")
        self.base = _git(self.repo, "rev-parse", "HEAD")

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, base=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = bind_check.main(
                ["--base", base or self.base, "--root", str(self.repo)])
        return code, out.getvalue()

    def _bound_core(self, with_envelope=True):
        """Commit a core that binds, optionally with its envelope. Returns the rev."""
        run_dir = self.repo / RUN_DIR
        run_dir.mkdir(parents=True)
        (run_dir / "build-manifest.json").write_text('{"unit": "u1"}\n', encoding="utf-8")
        (run_dir / "negctrl.txt").write_text("mutant KILLED\n", encoding="utf-8")
        _commit(self.repo, "artifacts")
        tree = _git(self.repo, "rev-parse", "HEAD^{tree}")
        cmd = f"python3 runtime/scripts/verify.py --manifest {MANIFEST}"
        (run_dir / "build-manifest.json").write_text(json.dumps({
            "unit": "u1",
            "commands": [{
                "label": "verify", "cmd": cmd,
                "cmd_sha256": hashlib.sha256(cmd.encode("utf-8")).hexdigest(),
                "exit": 0, "wtree": tree,
            }],
        }) + "\n", encoding="utf-8")
        _commit(self.repo, "manifest with a verifier ledger record")
        rev = _git(self.repo, "rev-parse", "HEAD")
        (self.repo / REPORT).write_text(
            _report(rev, _blob_sha(self.repo, rev, MANIFEST),
                    _blob_sha(self.repo, rev, f"{RUN_DIR}/negctrl.txt")),
            encoding="utf-8")
        if with_envelope:
            env_dir = self.repo / f"docs/reports/{MISSION}-selfrun"
            env_dir.mkdir(parents=True)
            (env_dir / "README.md").write_text(
                f"# {MISSION} run\n\nBindable core: `../../runs/{DATE}-{MISSION}-self-run.md`.\n",
                encoding="utf-8")
            (env_dir / "negctrl.txt").write_text("mutant KILLED\n", encoding="utf-8")
        _commit(self.repo, "report + envelope")
        return rev

    def test_no_candidates_passes(self):
        (self.repo / "docs" / "concepts.md").parent.mkdir(parents=True, exist_ok=True)
        (self.repo / "docs" / "concepts.md").write_text("prose\n", encoding="utf-8")
        _commit(self.repo, "unrelated docs edit")
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("no candidate run reports changed", out)

    def test_unbound_core_fails_with_binder_output(self):
        (self.repo / REPORT).parent.mkdir(parents=True)
        (self.repo / REPORT).write_text(
            f"# Run report\n\nRUN: mission={MISSION} tier={TIER} inventory_at={self.base} "
            f"manifest={MANIFEST} verifier=GREEN\n\n"
            "## Verifier outcome (recorded exactly)\n\n"
            f"    python3 runtime/scripts/verify.py --manifest {MANIFEST}\n    exit 0\n\n"
            "## Run-close integrity inventory (sha256)\n\n```\n```\n",
            encoding="utf-8")
        _commit(self.repo, "unbound report")
        code, out = self._run()
        self.assertEqual(code, 1)
        self.assertIn(f"FAIL {MISSION} ({TIER})", out)
        # The binder's own words, not a paraphrase: the manifest is absent at
        # the pinned commit and the inventory block is empty.
        self.assertIn("does not exist at", out)

    def test_bound_core_with_envelope_passes(self):
        self._bound_core(with_envelope=True)
        code, out = self._run()
        self.assertEqual(code, 0, out)
        self.assertIn(f"bound {MISSION} ({TIER}) — {REPORT}", out)
        self.assertIn("envelope docs/reports/demo-it-selfrun — core", out)

    def test_new_envelope_without_core_fails(self):
        env_dir = self.repo / f"docs/reports/{MISSION}-selfrun"
        env_dir.mkdir(parents=True)
        (env_dir / "README.md").write_text("# run\n", encoding="utf-8")
        _commit(self.repo, "envelope only")
        code, out = self._run()
        self.assertEqual(code, 1)
        self.assertIn("FAIL envelope docs/reports/demo-it-selfrun", out)
        self.assertIn("bindable core", out)

    def test_bound_core_without_envelope_fails(self):
        self._bound_core(with_envelope=False)
        code, out = self._run()
        self.assertEqual(code, 1, out)
        self.assertIn("missing its envelope", out)

    def test_hyphenated_envelope_spelling_satisfies_the_bundle(self):
        self._bound_core(with_envelope=False)
        env_dir = self.repo / f"docs/reports/{MISSION}-self-run"
        env_dir.mkdir(parents=True)
        (env_dir / "README.md").write_text("# run\n", encoding="utf-8")
        _commit(self.repo, "hyphenated envelope")
        code, out = self._run()
        self.assertEqual(code, 0, out)

    def test_doctrine_only_core_is_skipped(self):
        (self.repo / REPORT).parent.mkdir(parents=True)
        (self.repo / REPORT).write_text(
            f"# Run report\n\nRUN: mission={MISSION} tier=doctrine-only "
            f"inventory_at={self.base} manifest={MANIFEST} verifier=GREEN\n",
            encoding="utf-8")
        _commit(self.repo, "recorded history")
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("tier=doctrine-only advances nothing", out)

    def test_unknown_mission_is_skipped(self):
        path = self.repo / f"docs/runs/{DATE}-not-a-mission-self-run.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "# Run report\n\nRUN: mission=not-a-mission tier=self-run "
            f"inventory_at={self.base} manifest={MANIFEST} verifier=GREEN\n",
            encoding="utf-8")
        _commit(self.repo, "foreign report")
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("names no catalog mission", out)

    def test_run_together_tier_fails_with_spelling_guidance(self):
        (self.repo / REPORT).parent.mkdir(parents=True)
        (self.repo / REPORT).write_text(
            f"# Run report\n\nRUN: mission={MISSION} tier=selfrun "
            f"inventory_at={self.base} manifest={MANIFEST} verifier=GREEN\n",
            encoding="utf-8")
        _commit(self.repo, "run-together tier")
        code, out = self._run()
        self.assertEqual(code, 1)
        self.assertIn("want exactly self-run | external-run", out)

    def test_malformed_run_header_fails(self):
        (self.repo / REPORT).parent.mkdir(parents=True)
        (self.repo / REPORT).write_text(
            f"# Run report\n\nRUN: mission={MISSION}\n", encoding="utf-8")
        _commit(self.repo, "malformed header")
        code, out = self._run()
        self.assertEqual(code, 1)
        self.assertIn("RUN: header is missing", out)

    def test_tracker_without_run_header_is_ignored(self):
        path = self.repo / "docs/runs/2026-01-03-note.md"
        path.parent.mkdir(parents=True)
        path.write_text("# coordinator notes\n\nno header here\n", encoding="utf-8")
        _commit(self.repo, "notes")
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("no candidate run reports changed", out)

    def test_non_envelope_reports_dirs_are_ignored(self):
        other = self.repo / "docs/reports/release-20260912/notes.md"
        other.parent.mkdir(parents=True)
        other.write_text("# snapshot\n", encoding="utf-8")
        _commit(self.repo, "non-submission content")
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("no candidate run reports changed", out)

    def test_readme_and_template_edits_are_not_candidates(self):
        runs = self.repo / "docs/runs"
        runs.mkdir(parents=True)
        (runs / "TEMPLATE.md").write_text(
            "# template\n\nRUN: mission=<mission> tier=<tier> inventory_at=<c> "
            "manifest=<m> verifier=<v>\n", encoding="utf-8")
        _commit(self.repo, "template touch")
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("no candidate run reports changed", out)

    def test_unresolvable_base_returns_2(self):
        code, out = self._run(base="does-not-exist-anywhere")
        self.assertEqual(code, 2)


class BindCheckPureHelpers(unittest.TestCase):
    MISSIONS = {"demo-it", "review-it"}

    def test_envelope_claim_accepts_both_tier_spellings(self):
        self.assertEqual(
            bind_check.envelope_claim(
                "docs/reports/demo-it-selfrun/README.md", self.MISSIONS),
            ("demo-it", "selfrun"))
        self.assertEqual(
            bind_check.envelope_claim(
                "docs/reports/demo-it-self-run/README.md", self.MISSIONS),
            ("demo-it", "self-run"))

    def test_envelope_claim_prefers_the_longest_mission_prefix(self):
        self.assertEqual(
            bind_check.envelope_claim(
                "docs/reports/review-it-externalrun/README.md",
                self.MISSIONS | {"review"}),
            ("review-it", "externalrun"))

    def test_envelope_claim_rejects_non_submission_shapes(self):
        for path in ("docs/reports/release-20260912/notes.md",
                     "docs/reports/demo-it-selfrun/negctrl.txt",
                     "docs/reports/demo-it/README.md",
                     "docs/reports/unknown-mission-selfrun/README.md",
                     "docs/runs/2026-01-02-demo-it-self-run.md"):
            self.assertIsNone(
                bind_check.envelope_claim(path, self.MISSIONS), path)

    def test_is_core_path(self):
        self.assertTrue(bind_check.is_core_path(
            "docs/runs/2026-01-02-demo-it-self-run.md"))
        for path in ("docs/runs/README.md", "docs/runs/TEMPLATE.md",
                     "docs/reports/demo-it-selfrun/README.md",
                     "docs/runs/notes.txt"):
            self.assertFalse(bind_check.is_core_path(path), path)

    def test_normalize_tier(self):
        self.assertEqual(bind_check.normalize_tier("self-run"), "selfrun")
        self.assertEqual(bind_check.normalize_tier("ExternalRun"), "externalrun")


if __name__ == "__main__":
    unittest.main()
