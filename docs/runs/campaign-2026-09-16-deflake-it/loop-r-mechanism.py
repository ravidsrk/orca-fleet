"""LOOP-R: mechanism loop for the OSError-39 teardown race (#340 class).

Faithful construct pair from tests/test_verify.py in the gitleaks-PATH CI leg:
  BARE    = tempfile.TemporaryDirectory()                       (FreshnessCheck:320, RawByteDigest:880,
                                                                 GitAuthorityChecks:1111, InferRepoFromOrigin:1177)
  FLAGGED = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)  (RepoCase:61, the #340 mitigation)

Each trial builds a tiny temp git repo (init+commit, as the failing test does),
then races a concurrent writer thread creating files under .git/ (the #340
condition: "gitleaks-on-PATH can leave a file in .git/objects while rmtree runs")
against the context-manager teardown. Records OSError (incl. errno 39) per trial.

Usage: python3 loop-r-mechanism.py <trials-per-arm> <out-log>
Exit 0 always (rates are data); prints the rate table.
"""
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
LOG = sys.argv[2] if len(sys.argv) > 2 else "loop-r.log"


def make_repo(path: str) -> None:
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "PATH": "/usr/bin:/bin:/opt/homebrew/bin"}
    for args in (("init", "-q"), ("add", "."), ("commit", "-qm", "one")):
        if args[0] == "add":
            Path(path, "f.txt").write_text("same content")
        subprocess.run(["git", *args], cwd=path, env=env,
                       capture_output=True, check=True)


def trial(flagged: bool) -> str:
    """One race trial. Returns 'ok' or the OSError string."""
    stop = threading.Event()

    def writer(repo: str) -> None:
        i = 0
        target = Path(repo) / ".git" / "objects"
        while not stop.is_set():
            try:
                (target / f"late-{os.getpid()}-{i}.tmp").write_bytes(b"x")
            except OSError:
                pass  # repo already gone: the race window closed
            i += 1

    try:
        if flagged:
            td = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        else:
            td = tempfile.TemporaryDirectory()
        with td:
            make_repo(td.name)
            t = threading.Thread(target=writer, args=(td.name,), daemon=True)
            t.start()
            # exit the context while the writer is still running: teardown races
            # the late writes exactly as the #340 condition describes
        stop.set()
        t.join(timeout=5)
        return "ok"
    except OSError as e:  # noqa: BLE001 - the raced outcome IS the datum
        stop.set()
        return f"OSError errno={e.errno}: {e.strerror}"
    finally:
        stop.set()


def main() -> None:
    with open(LOG, "w") as fh:
        fh.write(f"LOOP-R start trials-per-arm={N}\n")
        for label, flagged in (("BARE", False), ("FLAGGED", True)):
            fails = 0
            examples = []
            for i in range(N):
                r = trial(flagged)
                if r != "ok":
                    fails += 1
                    if len(examples) < 3:
                        examples.append(f"trial {i}: {r}")
            rate = fails / N
            fh.write(f"{label}: fail={fails}/{N} rate={rate:.3f} e.g. {examples}\n")
            print(f"{label}: fail={fails}/{N} rate={rate:.3f} e.g. {examples}", flush=True)
        fh.write("LOOP-R end\n")


if __name__ == "__main__":
    main()
