"""Copy-install acceptance tests with independently named protocol dependencies."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bundle", ROOT / "scripts" / "bundle.py")
bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bundle)


class BundleClosureTests(unittest.TestCase):
    def run_command(self, cwd, *args):
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("PYTHON", "GIT_"))}
        return subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                              text=True, timeout=30)

    def test_transitive_protocol_calls_are_installed(self):
        # Audit witnesses: remediate-finding calls build-change; release calls observe.
        with tempfile.TemporaryDirectory() as tmp:
            built, problems = bundle.build(tmp)
            self.assertEqual((built, problems), (21, []))
            for mission, dependency in (("pin-it", "build-change"),
                                        ("migrate-it", "observe"),
                                        ("review-it", "build-change")):
                with self.subTest(mission=mission, dependency=dependency):
                    root = Path(tmp) / "skills" / mission
                    self.assertTrue((root / "references" / f"{dependency}.md").is_file())
                    self.assertIn(f"`{dependency}`", (root / "references/README.md").read_text())

    def test_installed_entry_points_work_without_source_checkout(self):
        with tempfile.TemporaryDirectory() as install_tmp:
            installed = Path(install_tmp) / "copied mission"
            with tempfile.TemporaryDirectory() as build_tmp:
                bundle.build(build_tmp)
                shutil.copytree(Path(build_tmp) / "skills/clean-sweep", installed)
            # Build output is gone; isolated Python cannot import from the checkout.
            project = Path(install_tmp) / "project"
            project.mkdir()
            for args in (("init", "-b", "main"),
                         ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                          "commit", "--allow-empty", "-m", "fixture"),
                         ("branch", "integration")):
                result = self.run_command(project, "git", *args)
                self.assertEqual(result.returncode, 0, result.stderr)
            for name in ("verify.py", "evidence-run.py", "preflight.py"):
                result = self.run_command(project, sys.executable, "-I",
                                          str(installed / "runtime/scripts" / name), "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)
            script = str(installed / "runtime/scripts/preflight.py")
            for base, expected in (("integration", 0), ("main", 2)):
                result = self.run_command(project, sys.executable, "-I", script,
                                          "--offline", "--base", base, "--default", "main")
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            manifest = Path(install_tmp) / "evidence.json"
            result = self.run_command(
                project, sys.executable, "-I", str(installed / "runtime/scripts/evidence-run.py"),
                "--label", "fixture", "--manifest", str(manifest), "--",
                sys.executable, "-I", "-c", "print('installed recorder executed')")
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(manifest.read_text())["commands"][0]
            tree = self.run_command(project, "git", "rev-parse", "HEAD^{tree}").stdout.strip()
            self.assertEqual(record["wtree"], tree)
            self.assertEqual(record["exit"], 0)
            self.assertNotIn("WARNING", result.stderr)
            for relative in ("runtime/scripts/diff_scope.py", "runtime/scripts/ed25519.py",
                             "runtime/one-way-doors.json", "runtime/pins.json"):
                self.assertEqual((installed / relative).read_bytes(), (ROOT / relative).read_bytes())
            index = (installed / "references/README.md").read_text()
            for name in ("verify.py", "evidence-run.py", "preflight.py"):
                self.assertIn(f'"$ORCA_FLEET_ROOT/runtime/scripts/{name}"', index)

    def test_missing_runtime_helper_data_or_transitive_protocol_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle.build(tmp)
            root = Path(tmp) / "skills/pin-it"
            self.assertEqual(bundle.dangling(root), [])
            for relative in ("runtime/scripts/verify.py", "runtime/scripts/wtree.sh",
                             "runtime/scripts/ed25519.py", "runtime/one-way-doors.json",
                             "runtime/pins.json", "references/build-change.md"):
                with self.subTest(missing=relative):
                    path = root / relative
                    # Also exercises the original bug, where runtime files were never copied.
                    original = path.read_bytes() if path.exists() else None
                    if original is not None:
                        path.unlink()
                    try:
                        problems = bundle.dangling(root)
                        self.assertTrue(any(Path(relative).name in p for p in problems), problems)
                    finally:
                        if original is not None:
                            path.write_bytes(original)
            self.assertEqual(bundle.dangling(root), [])

    def test_check_rejects_files_omitted_during_copy(self):
        copy = shutil.copy2
        missing = {"verify.py", "ed25519.py", "one-way-doors.json", "build-change.md"}

        def omit(source, target, **kwargs):
            if Path(source).name not in missing:
                return copy(source, target, **kwargs)

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(bundle.shutil, "copy2", omit):
            built, problems = bundle.build(tmp)
            self.assertEqual(built, 21)
            for name in missing:
                self.assertTrue(any(name in p for p in problems), (name, problems))

    def test_missing_or_malformed_inventory_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle.build(tmp)
            root = Path(tmp) / "skills/clean-sweep"
            inventory = root / "references/bundle-files.json"
            for contents in (None, "{", "{}"):
                with self.subTest(contents=contents):
                    if contents is None:
                        inventory.unlink(missing_ok=True)
                    else:
                        inventory.write_text(contents)
                    self.assertTrue(bundle.dangling(root))

    def test_all_missions_preserve_installed_interfaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            built, problems = bundle.build(tmp)
            self.assertEqual((built, problems), (21, []))
            for source in sorted((ROOT / "skills").glob("*/SKILL.md")):
                installed = Path(tmp) / "skills" / source.parent.name
                with self.subTest(mission=source.parent.name):
                    self.assertEqual(source.read_text().split("---", 2)[1],
                                     (installed / "SKILL.md").read_text().split("---", 2)[1])
                    self.assertEqual(bundle.dangling(installed), [])
                    self.assertEqual(list(installed.rglob("*.pyc")), [])
                    for extra in source.parent.rglob("*"):
                        if extra.is_file() and extra != source:
                            self.assertEqual(extra.read_bytes(),
                                             (installed / extra.relative_to(source.parent)).read_bytes())
                    for name in ("verify.py", "evidence-run.py", "preflight.py"):
                        result = self.run_command(tmp, sys.executable, "-I",
                                                  str(installed / "runtime/scripts" / name), "--help")
                        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
