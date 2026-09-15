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
import contextlib
import fcntl
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

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

    def test_a_seed_looser_than_the_rewrite_leaves_no_stale_tail(self):
        # The rewrite is in place (#388), so a manifest formatted more loosely than indent=2 is
        # longer than its own rewrite: unless the file is cut to the new length, the seed's tail
        # survives after the new JSON and the ledger no longer parses — with the run still green.
        seed = json.dumps({"unit": "u", "commands": [
            {"label": f"seed-{i}", "exit": 0, "commit": None, "wtree": None, "artifact": None}
            for i in range(1, 9)]}, indent=8) + "\n"
        (self.repo / "m.json").write_text(seed, encoding="utf-8")
        r = self.run_wrapped(sys.executable, "-c", "pass")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([c["label"] for c in self.records()],
                         ["seed-1", "seed-2", "seed-3", "seed-4", "seed-5", "seed-6", "seed-7",
                          "seed-8", "tests"])
        self.assertLess(len((self.repo / "m.json").read_text(encoding="utf-8")), len(seed),
                        "the seed must outlast its rewrite, or this case does not exercise a tail")

    def test_a_pre_existing_empty_manifest_reads_as_a_new_ledger(self):
        # Zero bytes on disk is the same state the wrapper's own create-on-open leaves, so it is
        # recorded into as a new ledger (the sibling-lockfile wrapper warned "Expecting value"
        # and recorded nothing).
        (self.repo / "m.json").write_text("", encoding="utf-8")
        r = self.run_wrapped(sys.executable, "-c", "pass")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("WARNING", r.stderr)
        data = json.loads((self.repo / "m.json").read_text(encoding="utf-8"))
        self.assertEqual(list(data), ["commands"])
        self.assertEqual([c["label"] for c in data["commands"]], ["tests"])


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


class ConcurrentAppends(LedgerCase):
    """#382: parallel wrapped runs used to lose records silently. The append is serialized; this
    releases sixteen runs at once so their appends contend, and demands every record land."""

    RUNS = 16

    def test_sixteen_concurrent_runs_land_sixteen_records(self):
        gate = tempfile.TemporaryDirectory()
        self.addCleanup(gate.cleanup)
        go = Path(gate.name, "go")
        # Each child announces itself, then waits for the shared release, so all sixteen wrappers
        # reach their append within milliseconds of each other.
        child = ("import os, sys, time\n"
                 f"open(os.path.join({gate.name!r}, 'ready-' + sys.argv[1]), 'w').close()\n"
                 f"while not os.path.exists({str(go)!r}):\n"
                 "    time.sleep(0.002)\n")
        procs = []
        for i in range(self.RUNS):
            procs.append(subprocess.Popen(
                [sys.executable, str(RUNNER), "--label", f"run-{i:02d}", "--manifest", "m.json",
                 "--", sys.executable, "-c", child, str(i)],
                cwd=self.repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            self.addCleanup(procs[-1].kill)
        deadline = time.monotonic() + 120
        while len(list(Path(gate.name).glob("ready-*"))) < self.RUNS:
            self.assertLess(time.monotonic(), deadline, "the sixteen children never all started")
            time.sleep(0.01)
        go.touch()
        for p in procs:
            _, err = p.communicate(timeout=120)
            self.assertEqual(p.returncode, 0, err)
        self.assertEqual(sorted(r["label"] for r in self.records()),
                         ["run-00", "run-01", "run-02", "run-03", "run-04", "run-05", "run-06",
                          "run-07", "run-08", "run-09", "run-10", "run-11", "run-12", "run-13",
                          "run-14", "run-15"])


class MixedVersionRollout(LedgerCase):
    """#393: during a rollout, a pre-#388 wrapper (flock `<manifest>.lock` → read → modify → write
    → release) appends to the same manifest as this one. The two locks are different files, so
    unless this wrapper also takes the sidecar when it exists, their read-modify-writes interleave
    and records are lost. Both kinds of writer are released at once through a file gate; the old
    ones keep appending while the new ones reach theirs, and every record must land."""

    NEW_RUNS = 8
    OLD_WRITERS = 4
    OLD_APPENDS = 60

    # The pre-#388 append discipline in shape (e04b0c2's append_record): a bookkeeping failure is
    # a warning and the record is dropped, exactly as that wrapper dropped it.
    OLD_WRITER = (
        "import fcntl, json, os, sys, time\n"
        "from pathlib import Path\n"
        "gate, manifest, who, count = sys.argv[1], Path(sys.argv[2]), sys.argv[3], int(sys.argv[4])\n"
        "lock_path = manifest.with_suffix(manifest.suffix + '.lock')\n"
        "open(os.path.join(gate, 'ready-old-' + who), 'w').close()\n"
        "while not os.path.exists(os.path.join(gate, 'go')):\n"
        "    time.sleep(0.002)\n"
        "for i in range(count):\n"
        "    try:\n"
        "        with open(lock_path, 'a', encoding='utf-8') as lock:\n"
        "            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)\n"
        "            if manifest.exists():\n"
        "                data = json.loads(manifest.read_text(encoding='utf-8'))\n"
        "            else:\n"
        "                data = {'commands': []}\n"
        "            data.setdefault('commands', []).append({'label': f'old-{who}-{i:02d}'})\n"
        "            manifest.write_text(json.dumps(data, indent=2) + '\\n', encoding='utf-8')\n"
        "    except (OSError, ValueError) as err:\n"
        "        print(f'old writer {who}: dropped old-{who}-{i:02d}: {err}', file=sys.stderr)\n")

    def test_old_sidecar_writers_and_new_runs_lose_no_records(self):
        (self.repo / "m.json.lock").touch()  # left behind by an earlier pre-#388 run
        gate = tempfile.TemporaryDirectory()
        self.addCleanup(gate.cleanup)
        go = Path(gate.name, "go")
        child = ("import os, sys, time\n"
                 f"open(os.path.join({gate.name!r}, 'ready-new-' + sys.argv[1]), 'w').close()\n"
                 f"while not os.path.exists({str(go)!r}):\n"
                 "    time.sleep(0.002)\n")
        procs = []
        for i in range(self.NEW_RUNS):
            procs.append(subprocess.Popen(
                [sys.executable, str(RUNNER), "--label", f"new-{i}", "--manifest", "m.json",
                 "--", sys.executable, "-c", child, str(i)],
                cwd=self.repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            self.addCleanup(procs[-1].kill)
        for w in range(self.OLD_WRITERS):
            procs.append(subprocess.Popen(
                [sys.executable, "-c", self.OLD_WRITER, gate.name, str(self.repo / "m.json"),
                 str(w), str(self.OLD_APPENDS)],
                cwd=self.repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            self.addCleanup(procs[-1].kill)
        deadline = time.monotonic() + 120
        while len(list(Path(gate.name).glob("ready-*"))) < len(procs):
            self.assertLess(time.monotonic(), deadline, "the writers never all started")
            time.sleep(0.01)
        go.touch()
        errs = []
        for p in procs:
            _, err = p.communicate(timeout=120)
            self.assertEqual(p.returncode, 0, err)
            errs.append(err)
        expected = ([f"new-{i}" for i in range(8)]
                    + [f"old-{w}-{i:02d}" for w in range(4) for i in range(60)])
        self.assertEqual(len(expected), 248)
        try:
            landed = sorted(r["label"] for r in self.records())
        except json.JSONDecodeError as err:  # two unserialized in-place rewrites overlapped
            self.fail(f"records lost: the ledger no longer parses ({err})")
        self.assertEqual(sorted(set(expected) - set(landed)), [], "records lost")
        self.assertEqual(landed, sorted(expected))
        for err in errs:
            self.assertNotIn("WARNING", err)
            self.assertNotIn("dropped", err)


class _Probe:
    """A stand-in for a module that overrides some callables and delegates everything else."""

    def __init__(self, real, **overrides):
        self._real = real
        self.__dict__.update(overrides)

    def __getattr__(self, name):
        return getattr(self._real, name)


class SidecarCreationRace(LedgerCase):
    """#387 thread 4012510839: the #393 join is check-then-act. With no sidecar on disk the new
    wrapper goes on under the manifest lock alone, and a pre-#388 writer can create and lock
    `<manifest>.lock` after that check. The two read-modify-writes then run under different
    locks, and one record is silently lost. The natural window is too thin to hit by chance
    (0/60 unforced trials), so this test forces the schedule. Probes on the module's own
    `fcntl.flock` and `json.loads` pause the real `append_record` at each step and hand every
    lock and parse to the real call:

        new: no sidecar -> legacy: create + lock the sidecar, read -> new: lock the manifest,
        read (stale) -> legacy: write -> new: write

    A fixed wrapper may block on the sidecar the legacy writer holds before it ever reads.
    That also releases the legacy writer, so the same schedule forces the loss on the broken
    code and cannot deadlock a fixed one."""

    TIMEOUT = 30  # a liveness bound on every wait, never a pacing delay

    def test_a_sidecar_created_after_the_absence_check_loses_no_record(self):
        spec = importlib.util.spec_from_file_location("evidence_run", RUNNER)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        manifest, sidecar = self.repo / "m.json", self.repo / "m.json.lock"
        manifest.write_text(json.dumps({"unit": "u", "commands": [{"label": "seed"}]}),
                            encoding="utf-8")
        new_checked = threading.Event()   # new: saw no sidecar, is about to lock the manifest
        legacy_read = threading.Event()   # legacy: holds the sidecar and has read the manifest
        new_moved = threading.Event()     # new: has read the manifest, or waits on the sidecar
        legacy_wrote = threading.Event()  # legacy: has rewritten the manifest

        def wait(event, what):
            if not event.wait(self.TIMEOUT):
                raise RuntimeError(f"schedule stalled waiting for {what}")

        def flock(fd, op):
            if op & fcntl.LOCK_EX:
                ino = os.fstat(fd).st_ino
                if sidecar.exists() and ino == sidecar.stat().st_ino:
                    new_moved.set()
                elif ino == manifest.stat().st_ino and not new_checked.is_set():
                    new_checked.set()
                    wait(legacy_read, "the legacy writer to lock the sidecar and read")
            return fcntl.flock(fd, op)

        def loads(text, *args, **kwargs):
            data = json.loads(text, *args, **kwargs)
            new_moved.set()
            wait(legacy_wrote, "the legacy writer to write")
            return data

        def legacy():  # e04b0c2's append discipline, one step at a time
            wait(new_checked, "the new wrapper to pass its sidecar check")
            with open(sidecar, "a", encoding="utf-8") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                data = json.loads(manifest.read_text(encoding="utf-8"))
                legacy_read.set()
                wait(new_moved, "the new wrapper to read the manifest or wait on the sidecar")
                data.setdefault("commands", []).append({"label": "legacy"})
                manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                legacy_wrote.set()

        errors = []

        def thread(target, *args):
            def run():
                try:
                    target(*args)
                except BaseException as err:  # surfaced below, not lost with the thread
                    errors.append(err)
            return threading.Thread(target=run, daemon=True)

        threads = [thread(runner.append_record, manifest, {"label": "new"}), thread(legacy)]
        with mock.patch.object(runner, "fcntl", _Probe(fcntl, flock=flock)), \
                mock.patch.object(runner, "json", _Probe(json, loads=loads)), \
                contextlib.redirect_stderr(io.StringIO()) as stderr:
            for t in threads:
                t.start()
            for t in threads:
                t.join(3 * self.TIMEOUT)
        self.assertEqual([t.is_alive() for t in threads], [False, False], "a writer hung")
        self.assertEqual(errors, [])
        self.assertNotIn("WARNING", stderr.getvalue())
        labels = [c["label"] for c in json.loads(manifest.read_text(encoding="utf-8"))["commands"]]
        self.assertEqual(sorted({"seed", "legacy", "new"} - set(labels)), [], "records lost")
        self.assertEqual(labels, ["seed", "legacy", "new"])


class NoLedgerLitter(LedgerCase):
    """#388: whatever serializes the append must not leave a file of its own beside the manifest.
    An untracked sibling fails every clean-tree gate once the manifest is committed, and it is
    content: the next run's fingerprint includes it and no longer equals the committed tree."""

    MANIFEST = "reports/m.json"

    def test_sequential_runs_leave_nothing_beside_the_manifest(self):
        for label in ("tests", "lint", "tests"):
            r = self.run_wrapped(sys.executable, "-c", "pass", label=label, manifest=self.MANIFEST)
            self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(p.name for p in (self.repo / "reports").iterdir()), ["m.json"])
        self.git("add", self.MANIFEST)
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "record")
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=all"), "",
                         "committing the manifest must leave a clean tree")

    def test_no_run_creates_the_rollout_sidecar(self):
        # #393 joins a `<manifest>.lock` only when one is already there; with none on disk the
        # runs must neither create it nor complain that it is missing.
        for label in ("tests", "lint"):
            r = self.run_wrapped(sys.executable, "-c", "pass", label=label, manifest=self.MANIFEST)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("WARNING", r.stderr)
        self.assertFalse((self.repo / "reports" / "m.json.lock").exists(),
                         "a wrapped run created the sidecar")
        self.assertEqual([c["label"] for c in self.records(self.MANIFEST)], ["tests", "lint"])

    def test_a_run_after_committing_the_manifest_records_the_committed_tree(self):
        self.run_wrapped(sys.executable, "-c", "pass", manifest=self.MANIFEST)
        self.git("add", self.MANIFEST)
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "record")
        committed = self.git("rev-parse", "HEAD^{tree}")
        r = self.run_wrapped(sys.executable, "-c", "pass", label="rerun", manifest=self.MANIFEST)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.records(self.MANIFEST)[-1]["wtree"], committed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
