#!/usr/bin/env python3
"""Phase-1 red-capable loop for root-cause self-test (issue #440).

Replicates `test_verify.FreshnessCheck.test_wtree_equivalence_relaxes_a_content_identical_head_move`
in a tight loop WITHOUT editing the test, catching teardown races red-handed:
on ENOTEMPTY the tmpdir survives (TemporaryDirectory.__exit__ raised before removal),
so the harness lists the leftover entries (the single most diagnostic evidence),
plus a process snapshot, then force-removes and continues.

Modes:
  replica N        run the exact test method N times, count teardown failures
  suite-strip      run the FULL test_verify suite once with ignore_cleanup_errors
                   forced OFF everywhere (masked-writer eruption check)
  gc-gate          replicate the scratch repo + git sequence, then report
                   count-objects, gc.log presence, lingering git processes
  positive-control run the replica with a deliberate concurrent writer to prove
                   the catcher reports the exact CI signature (OSError 39 on .git)

Usage: python3 phase1-harness.py <mode> [N]
"""
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent  # docs/runs/campaign-.../ -> repo root
sys.path.insert(0, str(REPO / "tests"))

import test_verify  # noqa: E402


def snapshot_procs():
    try:
        p = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=10)
        lines = [ln for ln in p.stdout.splitlines()
                 if "git" in ln.lower() or "gitleaks" in ln.lower()]
        return lines[:20]
    except OSError as e:
        return [f"<ps failed: {e}>"]


def list_leftovers(tmp):
    out = []
    for dirpath, dirnames, filenames in os.walk(tmp):
        rel = os.path.relpath(dirpath, tmp)
        for d in sorted(dirnames):
            out.append(os.path.join(rel, d) + "/")
        for f in sorted(filenames):
            out.append(os.path.join(rel, f))
    return sorted(out)


class CatchingTD(tempfile.TemporaryDirectory):
    """TemporaryDirectory that reports leftovers instead of just raising."""
    failures = []

    def __exit__(self, exc, val, tb):
        try:
            return super().__exit__(exc, val, tb)
        except OSError as e:
            left = list_leftovers(self.name) if os.path.isdir(self.name) else ["<gone>"]
            CatchingTD.failures.append({
                "error": f"{type(e).__name__}: {e}",
                "leftovers": left,
                "procs": snapshot_procs(),
            })
            shutil.rmtree(self.name, ignore_errors=True)
            raise


def mode_replica(n):
    import unittest.mock as mock
    fails = 0
    CatchingTD.failures.clear()
    with mock.patch.object(tempfile, "TemporaryDirectory", CatchingTD):
        for i in range(n):
            t = test_verify.FreshnessCheck(
                "test_wtree_equivalence_relaxes_a_content_identical_head_move")
            try:
                t.test_wtree_equivalence_relaxes_a_content_identical_head_move()
            except OSError:
                fails += 1
                print(f"--- teardown failure on iteration {i} ---")
                print(traceback.format_exc(limit=3))
    print(f"REPLICA: {fails}/{n} teardown failures")
    for f in CatchingTD.failures:
        print("LEFTOVERS:", f["leftovers"][:40])
        print("PROCS:", f["procs"][:10])
    return fails


def mode_suite_strip():
    import unittest.mock as mock
    real_td = tempfile.TemporaryDirectory

    class StrippedTD(real_td):
        def __init__(self, *a, **k):
            k["ignore_cleanup_errors"] = False
            super().__init__(*a, **k)

    enotempty = []
    with mock.patch.object(tempfile, "TemporaryDirectory", StrippedTD):
        loader = unittest.TestLoader()
        suite = loader.discover(str(REPO / "tests"), pattern="test_verify.py")
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
        result = runner.run(suite)
    for t, tb in result.errors + result.failures:
        if "Errno 39" in tb:
            enotempty.append((str(t), tb.strip().splitlines()[-1]))
    print(f"SUITE-STRIP: {result.testsRun} tests, "
          f"{len(result.errors)} errors, {len(result.failures)} failures, "
          f"{len(enotempty)} ENOTEMPTY")
    for name, tail in enotempty[:20]:
        print(f"  {name}: {tail}")
    return len(enotempty)


def mode_gc_gate():
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "PATH": "/usr/bin:/bin"}

    def g(tmp, *a):
        return subprocess.run(["git", *a], cwd=tmp, env=env,
                              capture_output=True, text=True)

    tmp = tempfile.mkdtemp()
    try:
        g(tmp, "init", "-q")
        Path(tmp, "f.txt").write_text("same content")
        g(tmp, "add", ".")
        g(tmp, "commit", "-qm", "one")
        g(tmp, "commit", "--amend", "-qm", "one amended")
        g(tmp, "add", ".")
        g(tmp, "commit", "-qm", "two")
        co = g(tmp, "count-objects", "-v")
        print("count-objects -v:")
        print(co.stdout)
        print("gc.log exists:", Path(tmp, ".git", "gc.log").exists())
        print("gc.pid exists:", Path(tmp, ".git", "gc.pid").exists())
        print("git processes now:", [ln for ln in snapshot_procs()])
        cfg = subprocess.run(["git", "config", "--list", "--show-origin"],
                             capture_output=True, text=True, cwd=tmp, env=env)
        print("effective gitconfig lines mentioning gc/maintenance:")
        print("\n".join(ln for ln in cfg.stdout.splitlines()
                        if "gc." in ln or "maintenance" in ln) or "<none>")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def mode_positive_control():
    import threading
    import time
    import unittest.mock as mock
    stop = threading.Event()

    def writer(path_holder):
        while not stop.is_set():
            tmp = path_holder.get("tmp")
            if tmp and os.path.isdir(os.path.join(tmp, ".git")):
                try:
                    with open(os.path.join(tmp, ".git", "PROBE-WRITER"), "w") as fh:
                        fh.write("x")
                except OSError:
                    pass
            time.sleep(0.0005)

    holder = {}
    real_td = tempfile.TemporaryDirectory

    class SpyTD(real_td):
        def __enter__(self):
            name = super().__enter__()
            holder["tmp"] = name
            return name

        def __exit__(self, *a):
            try:
                return super().__exit__(*a)
            finally:
                holder["tmp"] = None

    th = threading.Thread(target=writer, args=(holder,), daemon=True)
    th.start()
    try:
        with mock.patch.object(tempfile, "TemporaryDirectory", SpyTD):
            t = test_verify.FreshnessCheck(
                "test_wtree_equivalence_relaxes_a_content_identical_head_move")
            try:
                t.test_wtree_equivalence_relaxes_a_content_identical_head_move()
                print("POSITIVE-CONTROL: unexpectedly green (writer missed window)")
                return 0
            except OSError as e:
                print(f"POSITIVE-CONTROL: reproduced signature -> {e}")
                return 1
    finally:
        stop.set()
        th.join(timeout=5)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "replica"
    if mode == "replica":
        sys.exit(1 if mode_replica(int(sys.argv[2]) if len(sys.argv) > 2 else 200) else 0)
    elif mode == "suite-strip":
        sys.exit(1 if mode_suite_strip() else 0)
    elif mode == "suite-strip-all":
        import unittest.mock as mock
        real_td = tempfile.TemporaryDirectory

        class StrippedTD(real_td):
            def __init__(self, *a, **k):
                k["ignore_cleanup_errors"] = False
                super().__init__(*a, **k)

        enotempty = []
        with mock.patch.object(tempfile, "TemporaryDirectory", StrippedTD):
            loader = unittest.TestLoader()
            suite = loader.discover(str(REPO / "tests"))
            runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
            result = runner.run(suite)
        for t, tb in result.errors + result.failures:
            if "Errno 39" in tb or "Errno 66" in tb:
                enotempty.append((str(t), tb.strip().splitlines()[-1]))
        print(f"SUITE-STRIP-ALL: {result.testsRun} tests, "
              f"{len(result.errors)} errors, {len(result.failures)} failures, "
              f"{len(enotempty)} ENOTEMPTY")
        for name, tail in enotempty[:20]:
            print(f"  {name}: {tail}")
        sys.exit(1 if enotempty else 0)
    elif mode == "gc-gate":
        mode_gc_gate()
    elif mode == "positive-control":
        mode_positive_control()
    else:
        sys.exit(f"unknown mode {mode}")
