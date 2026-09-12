#!/usr/bin/env python3
"""Tests for the content-bound evidence ledger — `runtime/scripts/evidence-run.py` and the
`wtree.sh` fingerprint it records (audit §3 item 3; gstack `bin/gstack-evidence`/`bin/gstack-wtree`).

Two properties carry the mechanism:

  1. **Transparency.** The wrapper must never change a run's outcome. The child's exit code is the
     wrapper's exit code, its output reaches stdout unchanged, and every bookkeeping failure is a
     warning. A wrapper that can turn green tests red gets routed around, and then the ledger
     records nothing at all.
  2. **Content binding.** The recorded `wtree` is the fingerprint of the tree the command RAN
     AGAINST, so on a clean checkout of `head_sha` it equals `git rev-parse <head_sha>^{tree}` —
     which is exactly what `verify.py check_commands` demands. Untracked source changes it;
     committing identical content does not.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "runtime" / "scripts"
RUNNER = SCRIPTS / "evidence-run.py"
WTREE = SCRIPTS / "wtree.sh"


class LedgerCase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.repo = Path(self._td.name).resolve()
        self.git("init", "-q", "-b", "main")
        (self.repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.commit("base")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def wtree(self):
        r = subprocess.run(["sh", str(WTREE)], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def run_wrapped(self, *cmd, label="tests", manifest="m.json", artifact=None, cwd=None):
        argv = [sys.executable, str(RUNNER), "--label", label, "--manifest", manifest]
        if artifact:
            argv += ["--artifact", artifact]
        if cwd is not None:
            argv += ["--cwd", str(cwd)]
        argv += ["--", *cmd]
        return subprocess.run(argv, cwd=self.repo, capture_output=True, text=True)

    def records(self, manifest="m.json"):
        return json.loads((self.repo / manifest).read_text(encoding="utf-8"))["commands"]


class Transparency(LedgerCase):
    def test_child_exit_code_passes_through(self):
        r = self.run_wrapped(sys.executable, "-c", "raise SystemExit(7)")
        self.assertEqual(r.returncode, 7, r.stderr)
        self.assertEqual(self.records()[0]["exit"], 7)

    def test_zero_exit_passes_through(self):
        self.assertEqual(self.run_wrapped(sys.executable, "-c", "pass").returncode, 0)

    def test_child_output_reaches_stdout(self):
        r = self.run_wrapped(sys.executable, "-c", "print('hello from the child')")
        self.assertIn("hello from the child", r.stdout)

    def test_bookkeeping_failure_never_changes_the_verdict(self):
        # An unwritable manifest path is a WARNING, not a failure: the run still passes.
        (self.repo / "blocked").mkdir()
        r = self.run_wrapped(sys.executable, "-c", "pass", manifest="blocked")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("WARNING", r.stderr)

    def test_outside_a_repo_still_runs_and_warns(self):
        with tempfile.TemporaryDirectory() as plain:
            r = subprocess.run(
                [sys.executable, str(RUNNER), "--label", "t", "--manifest", "m.json",
                 "--", sys.executable, "-c", "raise SystemExit(3)"],
                cwd=plain, capture_output=True, text=True)
            self.assertEqual(r.returncode, 3)
            self.assertIn("fingerprint", r.stderr)
            self.assertIsNone(json.loads(Path(plain, "m.json").read_text())["commands"][0]["wtree"])

    def test_missing_command_is_a_usage_error(self):
        r = subprocess.run([sys.executable, str(RUNNER), "--label", "t", "--manifest", "m.json"],
                           cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)  # argparse usage exit


class RecordShape(LedgerCase):
    def test_record_carries_the_full_contract(self):
        self.run_wrapped(sys.executable, "-c", "pass", artifact="docs/out.txt")
        rec = self.records()[0]
        for field in ("label", "ts", "cmd", "cmd_sha256", "exit", "duration_s", "commit",
                      "wtree", "artifact"):
            self.assertIn(field, rec)
        self.assertEqual(rec["label"], "tests")
        self.assertEqual(rec["commit"], self.git("rev-parse", "HEAD"))
        self.assertEqual(rec["artifact"], "docs/out.txt")

    def test_cmd_sha256_is_the_hash_of_the_exact_command_line(self):
        import hashlib
        self.run_wrapped(sys.executable, "-c", "pass")
        rec = self.records()[0]
        self.assertEqual(rec["cmd_sha256"],
                         hashlib.sha256(rec["cmd"].encode("utf-8")).hexdigest())

    def test_artifact_is_written_with_the_child_output(self):
        self.run_wrapped(sys.executable, "-c", "print('recorded')", artifact="docs/out.txt")
        self.assertIn("recorded", (self.repo / "docs" / "out.txt").read_text(encoding="utf-8"))

    def test_manifest_is_created_when_absent_and_appended_when_not(self):
        self.assertFalse((self.repo / "m.json").exists())
        self.run_wrapped(sys.executable, "-c", "pass")
        self.assertEqual(len(self.records()), 1)
        self.run_wrapped(sys.executable, "-c", "pass", label="lint")
        self.assertEqual([r["label"] for r in self.records()], ["tests", "lint"])

    def test_existing_manifest_fields_survive(self):
        (self.repo / "m.json").write_text(json.dumps({"unit": "u", "head_sha": "abc"}),
                                          encoding="utf-8")
        self.run_wrapped(sys.executable, "-c", "pass")
        data = json.loads((self.repo / "m.json").read_text(encoding="utf-8"))
        self.assertEqual(data["unit"], "u")
        self.assertEqual(len(data["commands"]), 1)


class ContentBinding(LedgerCase):
    def test_recorded_wtree_is_head_tree_on_a_clean_checkout(self):
        # THE property verify.py check_commands relies on: a run on clean, committed content
        # records that content's tree. Note the fingerprint is taken BEFORE the run, so the
        # wrapper's own manifest/artifact writes cannot perturb it.
        self.run_wrapped(sys.executable, "-c", "pass", artifact="docs/out.txt")
        self.assertEqual(self.records()[0]["wtree"], self.git("rev-parse", "HEAD^{tree}"))

    def test_untracked_source_changes_the_fingerprint(self):
        clean = self.wtree()
        (self.repo / "extra.py").write_text("VALUE = 2\n", encoding="utf-8")
        self.assertNotEqual(self.wtree(), clean)

    def test_committing_identical_content_keeps_the_fingerprint(self):
        (self.repo / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
        dirty = self.wtree()
        self.commit("same content, now committed")
        self.assertEqual(self.wtree(), dirty)
        self.assertEqual(self.wtree(), self.git("rev-parse", "HEAD^{tree}"))

    def test_same_size_rewrite_in_the_same_second_still_changes_it(self):
        # gstack's #2687 hole: a `cp`-seeded temp index stamped "now" marks every entry non-racy,
        # so a same-size rewrite inside the same second can keep its stale stat-cache entry and
        # vanish from the fingerprint. `touch -r` restores the racy window; this pins that.
        before = self.wtree()
        (self.repo / "app.py").write_text("VALUE = 9\n", encoding="utf-8")  # same byte length
        self.assertNotEqual(self.wtree(), before)

    def test_wtree_fails_closed_outside_a_repo(self):
        with tempfile.TemporaryDirectory() as plain:
            r = subprocess.run(["sh", str(WTREE)], cwd=plain, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "", "no fingerprint must mean NO output, not empty-tree")

    def test_wtree_does_not_touch_the_real_index(self):
        (self.repo / "extra.py").write_text("x\n", encoding="utf-8")
        before = self.git("status", "--porcelain")
        self.wtree()
        self.assertEqual(self.git("status", "--porcelain"), before,
                         "wtree.sh staged into the REAL index")

    def test_wtree_accepts_a_target_directory(self):
        r = subprocess.run(["sh", str(WTREE), str(self.repo)], cwd=os.path.dirname(str(self.repo)),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), self.git("rev-parse", "HEAD^{tree}"))


class ExplicitWorkingDirectory(LedgerCase):
    def setUp(self):
        super().setUp()
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        self.target = Path(other.name).resolve()
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.target)], check=True)
        for repo, name, code in ((self.repo, "CALLER", 7), (self.target, "TARGET", 0)):
            (repo / "probe.py").write_text(
                f"from pathlib import Path\nprint({name!r}, Path.cwd())\nraise SystemExit({code})\n")
            (repo / "blocked").write_text("a file, not an artifact directory\n")
            subprocess.run(["git", "add", "probe.py", "blocked"], cwd=repo, check=True)
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit",
                            "-qm", "distinct fixture outcome"], cwd=repo, check=True)
        self.target_head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.target, text=True).strip()
        self.target_tree = subprocess.check_output(
            ["git", "rev-parse", "HEAD^{tree}"], cwd=self.target, text=True).strip()
        self.assertNotEqual(self.target_head, self.git("rev-parse", "HEAD"))
        self.assertNotEqual(self.target_tree, self.git("rev-parse", "HEAD^{tree}"))

    def assert_target_execution(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), f"TARGET {self.target}")
        manifest = self.target / "reports/manifest.json"
        self.assertTrue(manifest.is_file(), "relative manifest belongs in the explicit cwd")
        self.assertFalse((self.repo / "reports/manifest.json").exists())
        rec = json.loads(manifest.read_text())["commands"][0]
        self.assertEqual(rec["commit"], self.target_head)
        self.assertEqual(rec["wtree"], self.target_tree)
        self.assertEqual(rec["exit"], 0)
        return rec

    def test_explicit_cwd_without_artifact_binds_the_actual_repository(self):
        r = self.run_wrapped(sys.executable, "probe.py", cwd=self.target,
                             manifest="reports/manifest.json")
        self.assertIsNone(self.assert_target_execution(r)["artifact"])

    def test_relative_cwd_with_artifact_binds_the_actual_repository(self):
        r = self.run_wrapped(sys.executable, "probe.py", cwd=os.path.relpath(self.target, self.repo),
                             manifest="reports/manifest.json", artifact="reports/output.txt")
        rec = self.assert_target_execution(r)
        self.assertEqual(rec["artifact"], "reports/output.txt")
        self.assertEqual((self.target / rec["artifact"]).read_text(), r.stdout)
        self.assertFalse((self.repo / "reports/output.txt").exists())

    def test_artifact_open_failure_keeps_the_explicit_cwd(self):
        r = self.run_wrapped(sys.executable, "probe.py", cwd=self.target,
                             manifest="reports/manifest.json", artifact="blocked/output.txt")
        self.assert_target_execution(r)
        self.assertIn("cannot open artifact", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
