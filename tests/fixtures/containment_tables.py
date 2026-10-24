"""Test fixture: a process table that hides what macOS hides (PR #668 review).

`blind_to_system_binaries(read)` wraps a process-table reader and strips every containment marker
from any process that is not a Python: the view macOS's `ps -E` gives of an Apple system binary
(/bin/sh, /bin/sleep). Every paid runner's host probe must refuse such a table, on any host. It
is injected as a Python argument or attribute in tests only; nothing in production reads it.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

MARKERS = ("OF_CALL_ID", "OF_DISPATCH_TAG")


def _name(pid):
    comm = Path("/proc", str(pid), "comm")
    try:
        return comm.read_text(encoding="utf-8").strip()  # Linux: no ps in a slim image
    except OSError:
        return subprocess.run(["ps", "-o", "comm=", "-p", str(pid)], capture_output=True, text=True).stdout


def blind_to_system_binaries(read):
    def table():
        out = {}
        for pid, (ppid, pgid, env) in read().items():
            if any(tok.split("=", 1)[0] in MARKERS for tok in env) and "python" not in _name(pid).lower():
                env = tuple(tok for tok in env if tok.split("=", 1)[0] not in MARKERS)
            out[pid] = (ppid, pgid, env)
        return out
    return table


# A runner started as its own process (for the signals a test process cannot take in-process) gets
# the same Python-level injection: this boot loads the entry script as a module, puts a proven host
# probe where `inject` says, and calls its main(). A test of the live machinery lifts the live
# tier's refusal (PR #668: disabled outside the container harness) the same way, with `lifted`
# where `inject` says, in that process alone. No environment variable or flag is involved.
BOOT = """
import importlib.util, sys
spec = importlib.util.spec_from_file_location("proven_host_entry", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def proven(system_binary=True):
    return None


def lifted():
    return None


{inject}
sys.exit(mod.main(sys.argv[2:]))
"""


def proven_host(python, script, inject):
    """argv prefix: `script` run as its own process, its host probe injected as proven by `inject`
    (Python run against the loaded entry module `mod`)."""
    return [python, "-c", BOOT.format(inject=inject), str(script)]


def running(pid):
    """The process lives and is not a zombie: /proc on Linux (no procps needed), `ps` elsewhere."""
    stat = Path("/proc", str(pid), "stat")
    if Path("/proc/self").is_dir():
        try:
            return stat.read_text(encoding="utf-8").rsplit(")", 1)[-1].split()[0] not in ("Z", "X")
        except (OSError, IndexError):
            return False
    state = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    return bool(state) and not state.startswith("Z")


def kill(pid):
    """SIGKILL a pid this test started, if it still runs (os.kill: no `kill` binary needed)."""
    import os
    import signal
    try:
        os.kill(int(pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, ValueError):
        pass
