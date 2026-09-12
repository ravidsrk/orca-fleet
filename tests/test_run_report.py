#!/usr/bin/env python3
"""Contract tests for runtime/scripts/run_report.py — the proof-tier artifact binding.

docs/reviews/2026-09-10-review.md §2.2 / issue #259: before this, `proof: self-run` needed only a file under
docs/runs/ whose name and body mentioned the mission, so a three-line fabricated
report advanced a tier past every gate. These tests are the bypasses, run against
the checker: each one has to be refused.

The fixtures build real git repos, because the mechanism is "re-hash the recorded
paths at the recorded commit" — a fake that never touches git would test nothing.
"""
import hashlib
import importlib.util
import json
import shlex
import subprocess
import sys
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


def _report(mission, tier, rev, manifest, verifier, inventory, body=None):
    rows = "\n".join(f"{digest}  {path}" for digest, path in inventory)
    shown = body if body is not None else (
        f"    python3 runtime/scripts/verify.py --manifest {manifest} --unit-class mutation\n"
        f"    exit {0 if verifier == 'GREEN' else 2}\n"
    )
    return (
        f"# Run report — {mission} {tier}\n\n"
        f"RUN: mission={mission} tier={tier} inventory_at={rev} "
        f"manifest={manifest} verifier={verifier}\n\n"
        f"## Verifier outcome (recorded exactly)\n\n{shown}\n"
        f"{INVENTORY_HEADING}\n\n```\n{rows}\n```\n"
    )


class ExecutionIdentity(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name).resolve()
        self.verifier = self.repo / "runtime/scripts/verify.py"
        self.verifier.parent.mkdir(parents=True)
        self.verifier.write_text("#!/usr/bin/env python3\nprint('REPOSITORY VERIFIER')\n")
        self.verifier.chmod(0o755)
        self.shadow = self.repo / "shadow/runtime/scripts/verify.py"
        self.shadow.parent.mkdir(parents=True)
        self.shadow.write_text("print('SHADOW')\n")
        (self.repo / "inline_module.py").write_text("print('MODULE')\n")

    def observed(self, prefix, script="runtime/scripts/verify.py"):
        argv = [*prefix, script, "--manifest", "m.json"]
        result = subprocess.run(argv, cwd=self.repo, input="", capture_output=True,
                                text=True, timeout=10)
        return shlex.join(argv), result

    def test_interpreter_options_that_skip_the_script_are_rejected(self):
        options = [["-cpass"], ["-ucpass"], ["-c", "pass"], ["-minline_module"],
                   ["-Bm", "inline_module"], ["-m", "inline_module"],
                   ["--version"], ["-V"], ["-VV"], ["-uV"], ["-h"], ["-?"],
                   ["--help"], ["--help-env"], ["--help-xoptions"], ["--help-all"],
                   ["--unknown-option"]]
        for flags in options:
            with self.subTest(flags=flags):
                cmd, result = self.observed([sys.executable, *flags])
                self.assertNotEqual(result.stdout.strip(), "REPOSITORY VERIFIER")
                self.assertFalse(run_report.executes_verifier(cmd, "m.json", self.repo), cmd)

    def test_valid_interpreter_options_still_execute_the_verifier(self):
        for flags in ([], ["-u"], ["-IB"], ["-OO"], ["-W", "ignore"], ["-Wignore"],
                      ["-X", "dev"], ["-Xdev"], ["-uW", "ignore"],
                      ["--check-hash-based-pycs", "always"], ["--"]):
            with self.subTest(flags=flags):
                cmd, result = self.observed([sys.executable, *flags])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "REPOSITORY VERIFIER")
                self.assertTrue(run_report.executes_verifier(cmd, "m.json", self.repo), cmd)

    def test_only_the_exact_repository_script_counts(self):
        for script in ("shadow/runtime/scripts/verify.py", str(self.shadow)):
            with self.subTest(script=script):
                cmd, result = self.observed([sys.executable], script)
                self.assertEqual(result.stdout.strip(), "SHADOW")
                self.assertFalse(run_report.executes_verifier(cmd, "m.json", self.repo), cmd)
        for prefix, script in (([sys.executable], str(self.verifier)),
                               ([sys.executable], "./runtime/scripts/verify.py"),
                               ([], "./runtime/scripts/verify.py")):
            with self.subTest(prefix=prefix, script=script):
                cmd, result = self.observed(prefix, script)
                self.assertEqual(result.stdout.strip(), "REPOSITORY VERIFIER")
                self.assertTrue(run_report.executes_verifier(cmd, "m.json", self.repo), cmd)

    def test_xoption_values_that_abort_initialization_are_rejected(self):
        # CPython 3.13 --help-xoptions and using/cmdline.html define these value constraints.
        options = ["int_max_str_digits", "int_max_str_digits=1", "int_max_str_digits=-1",
                   "int_max_str_digits=abc", "int_max_str_digits=2147483648",
                   "utf8=", "utf8=2", "frozen_modules=bad",
                   "tracemalloc=-1", "tracemalloc=abc", "tracemalloc=65536",
                   "tracemalloc=2147483648"]
        if sys.version_info >= (3, 13):  # cpu_count/gil were introduced in 3.13
            options += ["cpu_count", "cpu_count=0", "cpu_count=-1", "cpu_count=abc",
                        "cpu_count=2147483648", "gil", "gil=2"]
        for option in options:
            for flags in (["-X", option], ["-uX" + option]):
                with self.subTest(flags=flags):
                    cmd, result = self.observed([sys.executable, *flags])
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("REPOSITORY VERIFIER", result.stdout)
                    self.assertFalse(run_report.executes_verifier(cmd, "m.json", self.repo), cmd)

    def test_valid_xoption_values_preserve_actual_script_execution(self):
        options = ["int_max_str_digits=0", "int_max_str_digits=640", "int_max_str_digits=",
                   "int_max_str_digits=+640", "utf8", "utf8=0", "utf8=1",
                   "frozen_modules", "frozen_modules=", "frozen_modules=on", "frozen_modules=off",
                   "tracemalloc", "tracemalloc=", "tracemalloc=0", "tracemalloc=1", "dev",
                   "arbitrary=value"]
        if sys.version_info >= (3, 13):
            options += ["cpu_count=default", "cpu_count=1", "gil=1"]
        for option in options:
            for flags in (["-X", option], ["-X" + option]):
                with self.subTest(flags=flags):
                    cmd, result = self.observed([sys.executable, *flags])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), "REPOSITORY VERIFIER")
                    self.assertTrue(run_report.executes_verifier(cmd, "m.json", self.repo), cmd)

    def test_repeated_xoptions_use_the_first_initialization_value(self):
        for values, expected in ((["utf8=1", "utf8=2"], True), (["utf8=2", "utf8=1"], False)):
            with self.subTest(values=values):
                cmd, result = self.observed([sys.executable, "-X", values[0], "-X", values[1], "--"])
                self.assertEqual(result.stdout.strip() == "REPOSITORY VERIFIER", expected)
                self.assertEqual(run_report.executes_verifier(cmd, "m.json", self.repo), expected)


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
        self.manifest = "docs/runs/2026-01-01-demo-it-selfrun/build-manifest.json"
        (self.run_dir / "build-manifest.json").write_text('{"unit": "u1"}\n', encoding="utf-8")
        (self.run_dir / "negctrl.txt").write_text("mutant KILLED\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "artifacts")
        # #286: a tier costs a command EXECUTION, so the graded manifest carries a commands[]
        # record of the verifier running against itself, bound to a tree that really exists here.
        # Written in a second commit because the record has to name the first commit's tree.
        tree = _git(self.repo, "rev-parse", "HEAD^{tree}")
        self.verifier_cmd = f"python3 runtime/scripts/verify.py --manifest {self.manifest}"
        (self.run_dir / "build-manifest.json").write_text(json.dumps({
            "unit": "u1",
            "commands": [{
                "label": "verify", "cmd": self.verifier_cmd,
                "cmd_sha256": hashlib.sha256(self.verifier_cmd.encode("utf-8")).hexdigest(),
                "exit": 0, "wtree": tree,
            }],
        }) + "\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "manifest with a verifier ledger record")
        self.rev = _git(self.repo, "rev-parse", "HEAD")
        self.nc = "docs/runs/2026-01-01-demo-it-selfrun/negctrl.txt"
        self.nc_sha = self._blob_sha(self.rev, self.nc)
        self.manifest_sha = self._blob_sha(self.rev, self.manifest)
        self.path = self.repo / "docs" / "runs" / "2026-01-01-demo-it-self-run.md"

    def tearDown(self):
        self._tmp.cleanup()

    def _blob_sha(self, rev, path):
        blob = subprocess.run(
            ["git", "cat-file", "blob", f"{rev}:{path}"],
            cwd=str(self.repo), stdout=subprocess.PIPE, check=True,
        ).stdout
        return hashlib.sha256(blob).hexdigest()

    def _inventory(self):
        """The default inventory: this run's own artifacts, the manifest among them."""
        return [(self.manifest_sha, self.manifest), (self.nc_sha, self.nc)]

    def _write(self, **kw):
        args = dict(
            mission="demo-it", tier="self-run", rev=self.rev, manifest=self.manifest,
            verifier="GREEN", inventory=self._inventory(),
        )
        args.update(kw)
        self.path.write_text(_report(**args), encoding="utf-8")
        return self.path

    def _check(self, mission="demo-it", tier="self-run"):
        return run_report.check_report(self.path, mission, tier, root=self.repo)

    # --- the shape that must pass ------------------------------------------
    def _remanifest(self, payload):
        """Rewrite the graded manifest and re-pin the report to the new commit."""
        (self.run_dir / "build-manifest.json").write_text(
            json.dumps(payload) + "\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "manifest rewritten")
        self.rev = _git(self.repo, "rev-parse", "HEAD")
        self.manifest_sha = self._blob_sha(self.rev, self.manifest)
        self.nc_sha = self._blob_sha(self.rev, self.nc)
        self._write()

    def test_a_recorded_command_is_read_as_argv_not_matched(self):
        """PR #308 review. A regex over a ledger record accepts `echo verify.py --manifest <m>`:
        it hashes true, names a real tree, and invokes nothing. This module already carries the
        scar tissue for the same class — _invocation_re was tightened twice, first because any
        prose mentioning verify.py matched, then because `--manifest \\S+` matched this module's
        own docstring. A recorded command is argv, so it is read as argv."""
        m = self.manifest
        V = "runtime/scripts/verify.py"
        for cmd in (f"python3 {V} --manifest {m}",
                    f"python3 ./{V} --manifest {m}",
                    f"/usr/bin/python3 -u {V} --contract-source c --manifest {m}",
                    f"env FOO=1 python3 {V} --manifest={m}",
                    # argparse keeps the LAST --manifest, so a trailing graded one is a real run.
                    f"python3 {V} --manifest other.json --manifest {m}",
                    # Flags this function does not model must not disbelieve a real run.
                    f"python3 {V} --contract-source c --execute-nc --nc-command 'pytest -q' "
                    f"--manifest {m}"):
            self.assertTrue(run_report.executes_verifier(cmd, m), cmd)
        for cmd in (f"echo {V} --manifest {m}",
                    f"true # {V} --manifest {m}",
                    f"sh -c '{V} --manifest {m}'",
                    f"python3 -c 'print(\"{V} --manifest {m}\")'",
                    f"cat {V} --manifest {m}",
                    f"python3 {V} --manifest other.json",
                    # A script the worker wrote is not this repository's verifier.
                    f"python3 /tmp/verify.py --manifest {m}",
                    f"python3 verify.py --manifest {m}",
                    f"python3 /tmp/{V} --manifest {m}",
                    f"python3 ../../tmp/{V} --manifest {m}",
                    # ...and argparse would read the LAST one, which is not the graded manifest.
                    f"python3 {V} --manifest {m} --manifest other.json",
                    # A dangling option: argparse refuses the whole command line, so the verifier
                    # never started. A hand-rolled scan kept the earlier value instead.
                    f"python3 {V} --manifest {m} --manifest",
                    f"python3 {V} --manifest"):
            self.assertFalse(run_report.executes_verifier(cmd, m), cmd)

    def test_an_echoed_invocation_does_not_buy_a_tier(self):
        # The same thing end to end: a fabricated report whose ledger only echoes the command.
        cmd = f"echo runtime/scripts/verify.py --manifest {self.manifest}"
        self._remanifest({"unit": "u1", "commands": [{
            "label": "verify", "cmd": cmd,
            "cmd_sha256": hashlib.sha256(cmd.encode("utf-8")).hexdigest(),
            "exit": 0, "wtree": self.rev}]})
        errs = self._check()
        self.assertTrue(any("records no commands[] entry" in e for e in errs), errs)

    def test_an_actual_inline_execution_does_not_buy_a_tier(self):
        argv = [sys.executable, "-cpass", "runtime/scripts/verify.py", "--manifest", self.manifest]
        result = subprocess.run(argv, cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        cmd = shlex.join(argv)
        self._remanifest({"unit": "u1", "commands": [{
            "label": "verify", "cmd": cmd,
            "cmd_sha256": hashlib.sha256(cmd.encode()).hexdigest(),
            "exit": result.returncode, "wtree": _git(self.repo, "rev-parse", "HEAD^{tree}")}]})
        errs = self._check()
        self.assertTrue(any("records no commands[] entry" in e for e in errs), errs)

    def test_a_manifest_with_no_verifier_run_is_refused(self):
        # #286. THE case: a fabricated map-it self-run — seven files, 32 lines, one commit —
        # reported "bound" in under fifteen minutes, because every artifact a worker writes and
        # commits hashes true at the commit containing it. Writing a command line costs nothing;
        # running one costs a run.
        self._remanifest({"unit": "u1"})
        errs = self._check()
        self.assertTrue(any("records no commands[] entry" in e for e in errs), errs)

    def test_a_verifier_record_for_another_manifest_does_not_count(self):
        # The record has to show the verifier run against THIS manifest, not a neighbour's.
        other = "docs/runs/2026-01-01-demo-it-selfrun/other-manifest.json"
        cmd = f"python3 runtime/scripts/verify.py --manifest {other}"
        self._remanifest({"unit": "u1", "commands": [{
            "label": "verify", "cmd": cmd,
            "cmd_sha256": hashlib.sha256(cmd.encode("utf-8")).hexdigest(),
            "exit": 0, "wtree": self.rev}]})
        errs = self._check()
        self.assertTrue(any("records no commands[] entry" in e for e in errs), errs)

    def test_a_verifier_record_whose_digest_does_not_match_is_refused(self):
        # A decorative cmd_sha256 would let the line be edited after the run.
        cmd = f"python3 runtime/scripts/verify.py --manifest {self.manifest}"
        self._remanifest({"unit": "u1", "commands": [{
            "label": "verify", "cmd": cmd, "cmd_sha256": "0" * 64,
            "exit": 0, "wtree": self.rev}]})
        errs = self._check()
        self.assertTrue(any("binds to nothing" in e and "cmd_sha256" in e for e in errs), errs)

    def test_a_verifier_record_bound_to_no_tree_is_refused(self):
        cmd = f"python3 runtime/scripts/verify.py --manifest {self.manifest}"
        self._remanifest({"unit": "u1", "commands": [{
            "label": "verify", "cmd": cmd,
            "cmd_sha256": hashlib.sha256(cmd.encode("utf-8")).hexdigest(), "exit": 0}]})
        errs = self._check()
        self.assertTrue(any("no wtree" in e for e in errs), errs)

    def test_a_verifier_record_naming_a_tree_that_does_not_exist_is_refused(self):
        cmd = f"python3 runtime/scripts/verify.py --manifest {self.manifest}"
        self._remanifest({"unit": "u1", "commands": [{
            "label": "verify", "cmd": cmd,
            "cmd_sha256": hashlib.sha256(cmd.encode("utf-8")).hexdigest(),
            "exit": 0, "wtree": "0" * 40}]})
        errs = self._check()
        self.assertTrue(any("is not an object in this repository" in e for e in errs), errs)

    def test_a_recorded_red_verifier_run_still_counts_as_a_run(self):
        # A RED is a legitimate recorded outcome — the point is that the verifier RAN.
        cmd = f"python3 runtime/scripts/verify.py --manifest {self.manifest}"
        tree = _git(self.repo, "rev-parse", "HEAD^{tree}")
        self._remanifest({"unit": "u1", "commands": [{
            "label": "verify", "cmd": cmd,
            "cmd_sha256": hashlib.sha256(cmd.encode("utf-8")).hexdigest(),
            "exit": 2, "wtree": tree}]})
        self.path.write_text(_report(
            mission="demo-it", tier="self-run", rev=self.rev, manifest=self.manifest,
            verifier="RED", inventory=self._inventory()), encoding="utf-8")
        errs = self._check()
        self.assertEqual([e for e in errs if "commands[]" in e or "binds to nothing" in e], [], errs)

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

    def test_verifier_outcome_described_in_prose_is_refused(self):
        # The original weakness: any body mentioning verify.py satisfied the gate.
        self.path.write_text(
            _report("demo-it", "self-run", self.rev, self.manifest, "GREEN", self._inventory(),
                    body="We ran verify.py and it went fine.\n"),
            encoding="utf-8")
        errs = self._check()
        self.assertTrue(any("no verify.py invocation against" in e for e in errs), errs)

    def test_an_invocation_naming_a_placeholder_path_is_refused(self):
        # The SECOND weakness, found by this module's own docstring satisfying it:
        # `--manifest <path>` parses as a command with an argument. The argument has
        # to be the manifest this report is actually graded on.
        self.path.write_text(
            _report("demo-it", "self-run", self.rev, self.manifest, "GREEN", self._inventory(),
                    body="    python3 runtime/scripts/verify.py --manifest <path>\n"),
            encoding="utf-8")
        errs = self._check()
        self.assertTrue(any("no verify.py invocation against" in e for e in errs), errs)

    def test_an_invocation_against_a_different_manifest_is_refused(self):
        self.path.write_text(
            _report("demo-it", "self-run", self.rev, self.manifest, "GREEN", self._inventory(),
                    body="    python3 runtime/scripts/verify.py --manifest /tmp/other.json\n"),
            encoding="utf-8")
        errs = self._check()
        self.assertTrue(any("no verify.py invocation against" in e for e in errs), errs)

    def test_the_graded_manifest_must_be_pinned_by_the_inventory(self):
        # Hashing a neighbouring artifact while the document the verdict rests on
        # floats free binds nothing that matters (PR #277 review, P1).
        self._write(inventory=[(self.nc_sha, self.nc)])
        errs = self._check()
        self.assertTrue(any("the graded manifest" in e for e in errs), errs)

    def test_this_runs_own_artifact_going_absent_is_refused(self):
        # A path elsewhere may legitimately have moved; one of THIS run's own
        # artifacts being absent means the evidence was not retained.
        self._write(inventory=self._inventory() + [
            ("0" * 64, "docs/runs/2026-01-01-demo-it-selfrun/never-committed.txt")])
        errs = self._check()
        self.assertTrue(any("are absent at" in e for e in errs), errs)

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

    def test_ship_its_artifacts_still_hash_true_but_its_transcript_is_missing(self):
        """The four-of-five state, pinned so neither half drifts.

        Its inventory re-derives at `748b328` and its manifest is in its own run
        directory — that much is real and should keep working. What is absent is the
        `verify.py … --manifest` invocation the recorded RED came from, which is why
        ship-it sits at doctrine-only.

        Since #286 that absence is reported twice, at two levels, and both are the same
        gap: the report body shows no invocation, AND the graded manifest's commands[]
        ledger records no verifier run. The run really did not write the command line
        down — its own report says so — so a gate that costs a run must fail it here.
        """
        errs = run_report.check_report(
            "docs/runs/2026-08-28-ship-it-self-run.md", "ship-it", "self-run"
        )
        missing_transcript = [e for e in errs
                              if "invocation" in e or "records no commands[] entry" in e
                              or "RUN: tier=doctrine-only" in e]
        self.assertEqual(
            [e for e in errs if e not in missing_transcript], [],
            "only the missing verifier transcript should stop this report binding",
        )
        self.assertTrue(any("invocation" in e for e in errs), "the prose leg stopped reporting")
        self.assertTrue(any("records no commands[] entry" in e for e in errs),
                        "the ledger leg (#286) stopped reporting")
        # And the header itself now refuses the claim: asked whether this report supports
        # `self-run`, it answers with what it actually declares.
        self.assertTrue(any("RUN: tier=doctrine-only" in e for e in errs),
                        "the RUN: header no longer states the tier the body supports")

    def test_demoted_reports_are_kept_and_say_why(self):
        # Demoting is only honest if the record survives and explains itself.
        for name in (
            "2026-07-13-clean-sweep-self-run.md",
            "2026-07-13-review-it-external-run.md",
            "2026-07-16-oss-contribute-external-run.md",
            "2026-08-28-ship-it-self-run.md",
        ):
            text = (ROOT / "docs" / "runs" / name).read_text(encoding="utf-8")
            self.assertIn("Evidence binding", text, f"{name} was demoted without saying why")

    def test_the_readme_does_not_claim_the_tier_gate_re_derives(self):
        """#281. The gate hashes artifacts at a named commit; it does not re-run the verifier, and
        run_report.py's own docstring says so at :33-38. The README claimed a tier "re-derives",
        which a fabricated map-it self-run disproved in fifteen minutes. Guard the honest wording:
        a doc claim that outruns its mechanism is the failure this repository exists to refuse."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        start = readme.index("## Proof status")
        section = " ".join(readme[start:readme.index("\n## ", start + 1)].split())
        self.assertNotIn("it is a report that re-derives", section,
                         "the README is claiming the tier gate re-derives again (#281)")
        self.assertIn("hash true at a named commit", section)
        self.assertIn("it hashes, it does not re-run the verifier", section,
                      "the section must state the limit, not only the capability")


if __name__ == "__main__":
    unittest.main()
