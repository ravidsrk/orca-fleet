"""Copy-install acceptance tests with independently named protocol dependencies."""
import importlib.util
import base64
import hashlib
import json
import os
import re
import shlex
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
                entry = installed / "runtime/scripts" / name
                self.assertTrue(entry.is_file(), str(entry))
                self.assertEqual(entry.stat().st_mode & 0o111, 0o111,
                                 f"{name} must retain its executable interface")
                result = self.run_command(project, str(entry), "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)
            script = str(installed / "runtime/scripts/preflight.py")
            for base, expected in (("integration", 0), ("main", 2)):
                result = self.run_command(project, sys.executable, "-I", script,
                                          "--offline", "--base", base, "--default", "main")
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            manifest = Path(install_tmp) / "evidence.json"
            # Execute the protocol's recorder invocation using the index's substitution rule.
            protocol = (installed / "references/build-change.md").read_text()
            invocation = next(line for line in protocol.splitlines()
                              if line.startswith("runtime/scripts/evidence-run.py --label"))
            invocation = invocation.replace("runtime/scripts/evidence-run.py",
                                            '"$ORCA_FLEET_ROOT/runtime/scripts/evidence-run.py"')
            invocation = invocation.replace("<m.json>", '"$2"').replace(
                "<criterion-bound command>", shlex.join(
                    [sys.executable, "-I", "-c", "print('installed recorder executed')"]))
            self.assertFalse((project / "runtime").exists())
            result = self.run_command(
                project, "/bin/sh", "-c", "ORCA_FLEET_ROOT=$1\n" + invocation,
                "installed-flow", str(installed), str(manifest))
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
            self.assert_installed_verification(installed, project, manifest)

    def assert_installed_verification(self, installed, project, manifest):
        # A real local report-only range can pass without any review claim or network call.
        base = self.run_command(project, "git", "rev-parse", "HEAD").stdout.strip()
        (project / "report.md").write_text("Fixture report, no production changes.\n")
        self.assertEqual(self.run_command(project, "git", "add", "report.md").returncode, 0)
        result = self.run_command(project, "git", "-c", "user.name=Fixture",
                                  "-c", "user.email=fixture@example.invalid",
                                  "commit", "-m", "fixture report")
        self.assertEqual(result.returncode, 0, result.stderr)
        head = self.run_command(project, "git", "rev-parse", "HEAD").stdout.strip()
        contract = project / "contract.json"
        contract.write_text('{"criterion_ids": ["AC-1"]}\n')
        digest = "sha256:" + hashlib.sha256(contract.read_bytes()).hexdigest()
        evidence = {"unit": "installed-fixture", "base_sha": base, "head_sha": head,
                    "contract": {"digest": digest, "criterion_ids": ["AC-1"]},
                    "criteria": [{"id": "AC-1", "addressed": True}]}
        manifest.write_text(json.dumps(evidence))
        command = (sys.executable, "-I", str(installed / "runtime/scripts/verify.py"),
                   "--manifest", str(manifest), "--contract-source", "contract.json",
                   "--contract-digest", digest)
        result = self.run_command(project, *command, "--unit-class", "report-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verify: OK", result.stdout)
        self.assertIn("report-only (unsupervised)", result.stdout)
        evidence["criteria"] = []
        manifest.write_text(json.dumps(evidence))
        result = self.run_command(project, *command, "--unit-class", "report-only")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("authoritative criteria not addressed", result.stderr)
        # Mutation mode exercises diff_scope's lazy load through real changed-path binding.
        # Its missing review gate must remain RED; this is never a production approval.
        evidence["criteria"] = [{"id": "AC-1", "addressed": True}]
        (project / "control.txt").write_text(result.stderr)
        evidence["negative_control"] = {"tool": "revert", "paths": ["report.md"],
                                        "result": "RED", "artifact": "control.txt"}
        evidence["artifacts"] = [{"path": "control.txt", "sha256": hashlib.sha256(
            (project / "control.txt").read_bytes()).hexdigest()}]
        manifest.write_text(json.dumps(evidence))
        # Public RFC 8032 test-vector key, deliberately invalid signature, no private key.
        (project / "public.txt").write_text(
            "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
        (project / "dispatch.json").write_text(json.dumps(
            {"record": {}, "sig_b64": base64.b64encode(bytes(64)).decode()}))
        args = (*command, "--unit-class", "mutation", "--dispatch-record", "dispatch.json",
                "--dispatch-pubkey", "public.txt")
        result = self.run_command(project, *args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("signature INVALID", result.stderr)
        self.assertIn("no pr.number", result.stderr)
        self.assertNotIn("could not be loaded", result.stderr)
        self.assertNotIn("negative_control.paths", result.stderr)
        for helper, diagnostic in (("diff_scope.py", "diff_scope.py could not be loaded"),
                                   ("ed25519.py", "Ed25519 verifier is unavailable")):
            path = installed / "runtime/scripts" / helper
            saved = path.read_bytes()
            path.unlink()
            try:
                result = self.run_command(project, *args)
                self.assertEqual(result.returncode, 2)
                self.assertIn(diagnostic, result.stderr)
            finally:
                path.write_bytes(saved)

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

    def test_installed_verifier_oracle_rejects_a_usage_only_decoy(self):
        copy = shutil.copy2

        def decoy(source, target, **kwargs):
            result = copy(source, target, **kwargs)
            if Path(source).name == "verify.py":
                Path(target).write_text("#!/usr/bin/env python3\nprint('usage: decoy')\n")
            return result

        with mock.patch.object(bundle.shutil, "copy2", decoy):
            with self.assertRaisesRegex(AssertionError, "verify: OK"):
                self.test_installed_entry_points_work_without_source_checkout()

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

    def test_installed_oracle_rejects_stripped_executable_permissions(self):
        copy = shutil.copy2

        def strip_mode(source, target, **kwargs):
            result = copy(source, target, **kwargs)
            if Path(source).name == "evidence-run.py":
                Path(target).chmod(Path(target).stat().st_mode & ~0o111)
            return result

        with mock.patch.object(bundle.shutil, "copy2", strip_mode):
            with self.assertRaisesRegex(AssertionError, "executable"):
                self.test_installed_entry_points_work_without_source_checkout()

    def test_check_rejects_required_inputs_missing_before_discovery(self):
        # Copy build inputs so omission never mutates the shared source checkout.
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp).resolve() / "source"
            for directory in ("skills", "playbooks", "runtime", "docs"):
                shutil.copytree(ROOT / directory, source / directory)
            shutil.copy2(ROOT / "ARCHITECTURE.md", source / "ARCHITECTURE.md")
            with mock.patch.object(bundle, "ROOT", source), \
                    mock.patch.object(bundle, "SKILLS_DIR", source / "skills"), \
                    mock.patch.object(bundle.validate, "PLAYBOOKS_DIR", source / "playbooks"), \
                    mock.patch.object(bundle.validate, "RUNTIME_DIR", source / "runtime"):
                self.assertEqual(bundle.build(Path(tmp) / "out"), (21, []))
                for relative in ("runtime/scripts/ed25519.py", "runtime/scripts/diff_scope.py",
                                 "runtime/scripts/wtree.sh", "runtime/scripts/verify.py",
                                 "runtime/one-way-doors.json", "playbooks/build-change.md",
                                 "playbooks/observe.md", "runtime/evidence-manifest.md",
                                 "docs/runs/TEMPLATE.md"):
                    with self.subTest(missing=relative):
                        path = source / relative
                        saved = path.read_bytes()
                        path.unlink()
                        try:
                            _built, problems = bundle.build(Path(tmp) / "out")
                            self.assertTrue(any(Path(relative).name in p for p in problems),
                                            (relative, problems))
                        finally:
                            path.write_bytes(saved)

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

    def test_transitive_run_report_template_has_an_installed_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(bundle.build(tmp), (21, []))
            root = Path(tmp) / "skills/pin-it"
            protocol_path = root / "references/build-change.md"
            self.assertTrue(protocol_path.is_file(), "missing mandatory build-change protocol")
            protocol = protocol_path.read_text()
            self.assertIn("docs/runs/TEMPLATE.md", protocol)
            index = (root / "references/README.md").read_text()
            matches = re.findall(r'"\$ORCA_FLEET_ROOT/([^"\n]*TEMPLATE.md)"', index)
            self.assertTrue(matches, "mandatory template needs an explicit installed path")
            template = root / matches[0]
            self.assertTrue(template.is_file())
            self.assertIn("RUN: mission=<mission>", template.read_text())
            self.assertIn("## Verifier outcome", template.read_text())
            # Copy just the mission, then execute the reporting procedure in another repo.
            with tempfile.TemporaryDirectory() as separate:
                installed = Path(separate) / "copied mission"
                shutil.copytree(root, installed)
                self.assert_installed_reporting(installed, Path(separate) / "project")
            template.unlink()
            self.assertTrue(any("TEMPLATE.md" in p for p in bundle.dangling(root)))

    def assert_installed_reporting(self, installed, project):
        project.mkdir()
        (project / "checks").mkdir()
        (project / ".gitignore").write_text("docs/runs/\ncontract.json\n__pycache__/\n")
        (project / "value.txt").write_text("42\n")
        (project / "check.py").write_text(
            "from pathlib import Path\nassert int(Path('value.txt').read_text()) > 0\n")
        (project / "checks/test_value.py").write_text(
            "import unittest\nfrom pathlib import Path\nclass Target(unittest.TestCase):\n"
            " def test_value(self):\n  self.assertEqual(Path('value.txt').read_text(), '42\\n')\n")
        for args in (("init", "-b", "main"),
                     ("add", ".gitignore", "check.py", "checks", "value.txt")):
            self.assertEqual(self.run_command(project, "git", *args).returncode, 0)
        commit = ("git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                  "commit", "-m", "fixture")
        self.assertEqual(self.run_command(project, *commit).returncode, 0)
        base = self.run_command(project, "git", "rev-parse", "HEAD").stdout.strip()
        (project / "report.md").write_text("Report-only fixture.\n")
        self.assertEqual(self.run_command(project, "git", "add", "report.md").returncode, 0)
        self.assertEqual(self.run_command(project, *commit).returncode, 0)
        head = self.run_command(project, "git", "rev-parse", "HEAD").stdout.strip()
        run_dir = "docs/runs/2026-09-12-pin-it-external-run"
        evidence = project / run_dir
        evidence.mkdir(parents=True)
        manifest = run_dir + "/manifest.json"
        (project / "contract.json").write_text('{"criterion_ids": ["AC-1"]}\n')
        digest = "sha256:" + hashlib.sha256((project / "contract.json").read_bytes()).hexdigest()
        (project / manifest).write_text(json.dumps({
            "unit": "installed-report", "base_sha": base, "head_sha": head,
            "contract": {"digest": digest, "criterion_ids": ["AC-1"]},
            "criteria": [{"id": "AC-1", "addressed": True}]}))
        template = (installed / "docs/runs/TEMPLATE.md").read_text()
        replacements = {"<manifest>": manifest, "<run-dir>": run_dir,
                        "<contract-source>": "contract.json", "<contract-digest>": digest,
                        "<unit-class>": "report-only",
                        "<project-validation-command>": "python3 check.py",
                        "<project-test-command>": "python3 -m unittest discover -s checks"}

        def execute(command, suffix=""):
            for placeholder, value in replacements.items():
                command = command.replace(placeholder, value)
            command = command.replace(".txt --", suffix + ".txt --")
            # Apply the index's path rule; shlex.join preserves a spaced install path.
            argv = [sys.executable if p == "python3" else
                    str(installed / p) if p.startswith("runtime/scripts/") else p
                    for p in shlex.split(command)]
            result = self.run_command(project, *argv)
            return result, shlex.join(argv)

        gates = template.split("## Gates\n", 1)[1].split("## Catalog proof promotion", 1)[0]
        commands = re.findall(r"`(python3 [^`]+)`", gates)
        self.assertTrue(commands, "missing target validation/test instructions")
        for command in commands:
            result, invocation = execute(command)
            self.assertEqual(result.returncode, 0, invocation + "\n" + result.stderr)
        records = json.loads((project / manifest).read_text())["commands"]
        self.assertEqual([r["label"] for r in records], ["validation", "tests"])
        self.assertIn("Ran 1 test", (evidence / "tests.txt").read_text())
        # Both required target checks must detect a real bad value and retain their exits.
        (project / "value.txt").write_text("-1\n")
        for command in commands:
            result, invocation = execute(command, "-red")
            self.assertEqual(result.returncode, 1, invocation + "\n" + result.stderr)
        (project / "value.txt").write_text("42\n")
        for command in commands:
            self.assertEqual(execute(command, "-restored")[0].returncode, 0)
        data = json.loads((project / manifest).read_text())
        self.assertEqual([r["exit"] for r in data["commands"]], [0, 0, 1, 1, 0, 0])
        data["artifacts"] = [{"path": p.relative_to(project).as_posix(),
                              "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                             for p in evidence.glob("*.txt")]
        (project / manifest).write_text(json.dumps(data))
        verifier = re.findall(r"`(python3 [^`]+)`", template.split(
            "## Verifier outcome", 1)[1].split("## WIP-curve", 1)[0])
        self.assertEqual(len(verifier), 1)
        result, invocation = execute(verifier[0])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("verify: OK", result.stdout)
        data = json.loads((project / manifest).read_text())
        self.assertEqual(data["commands"][-1]["label"], "verifier")
        self.assertEqual(data["commands"][-1]["cmd"], invocation.split(" -- ", 1)[1])
        tree = self.run_command(project, "git", "rev-parse", "HEAD^{tree}").stdout.strip()
        self.assertEqual(data["commands"][-1]["wtree"], tree)
        # No source-clone/catalog layout is available in the project.
        for missing in ("runtime", "scripts", "skills", "tests", "docs/runs/README.md"):
            self.assertFalse((project / missing).exists(), missing)
        report = run_dir + ".md"
        replacements["<report>"] = report
        inventory_commands = re.findall(r"`(python3 [^`]+)`", template.split(
            "## Run-close integrity inventory", 1)[1].split("## Gates", 1)[0])
        self.assertEqual(len(inventory_commands), 3)
        rows = "\n".join(f"| `{p.relative_to(project)}` | `{'0' * 64}` | fixture |"
                         for p in sorted(evidence.iterdir()))
        (project / report).write_text(
            f"# Installed reporting fixture\n\n"
            f"RUN: mission=pin-it tier=doctrine-only inventory_at=uncommitted "
            f"manifest={manifest} verifier=GREEN\n\n"
            f"Target: isolated external project; BASE main at {base}; head {head}; "
            f"frozen contract contract.json at {digest}.\n"
            f"Mission location: {installed}; source revision: fixture build.\n"
            "Coordinator/workers: local unittest fixture, no dispatched workers.\n"
            "Orca and human gates: inapplicable to this offline reporting fixture.\n\n"
            "## Terminal state\nReporting procedure exercised; no mission completion claimed.\n"
            "## Convergence proof\nFixture AC-1 is a report-only Git range; no live oracle.\n"
            f"## Pipeline evidence\nExact commands and exits: {manifest}.\n"
            "## WIP-curve protocol row\nInapplicable: external report-only fixture.\n"
            "## Deviations and lessons\nNo live mission run or proof promotion is claimed.\n"
            f"## Gates\nTarget validation and one target test passed; "
            f"bad-value controls failed, then restored controls passed (see {manifest}).\n"
            "## Evidence binding\nAll owned artifacts retained in the inventory commit.\n"
            "## Verifier outcome\n"
            f"{invocation}\nexit 0\n{result.stdout}\n"
            f"## Run-close integrity inventory (sha256)\n{rows}\n")
        for command in inventory_commands[:2]:
            result, invocation = execute(command)
            self.assertEqual(result.returncode, 0, invocation + "\n" + result.stderr)
            self.assertNotIn("MISSING", result.stdout)
        # A changed owned artifact must fail the actual installed inventory checker.
        saved = (evidence / "tests.txt").read_bytes()
        (evidence / "tests.txt").write_text("tampered\n")
        self.assertEqual(execute(inventory_commands[1])[0].returncode, 1)
        (evidence / "tests.txt").unlink()
        result, _ = execute(inventory_commands[1])
        self.assertIn("MISSING", result.stdout)  # The procedure rejects missing owned evidence too.
        (evidence / "tests.txt").write_bytes(saved)
        self.assertEqual(self.run_command(project, "git", "add", "-f", run_dir,
                                         "contract.json").returncode, 0)
        self.assertEqual(self.run_command(project, *commit).returncode, 0)
        evidence_sha = self.run_command(project, "git", "rev-parse", "HEAD").stdout.strip()
        replacements["<inventory_at>"] = evidence_sha
        report_path = project / report
        report_path.write_text(report_path.read_text().replace(
            "inventory_at=uncommitted", "inventory_at=" + evidence_sha))
        result, invocation = execute(inventory_commands[2])
        self.assertEqual(result.returncode, 0, invocation + "\n" + result.stderr)
        self.assertNotIn("MISSING", result.stdout)

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
                        entry = installed / "runtime/scripts" / name
                        self.assertTrue(entry.is_file(), str(entry))
                        self.assertEqual(entry.stat().st_mode & 0o111, 0o111,
                                         f"{name} must retain its executable interface")
                        result = self.run_command(tmp, str(entry), "--help")
                        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
