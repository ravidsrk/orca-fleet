#!/usr/bin/env python3
"""orca_cli.py — resolve the Orca CLI command name the way upstream documents it (#510).

Every fleet script that talks to Orca resolves the executable through this module, so one
rule holds everywhere. The order is upstream's own, from `skill-stubs/_shared/cli-resolution.md`
in stablyai/orca:

  1. `ORCA_CLI_COMMAND` when set. Orca exports it inside the sessions it manages (structured
     worker sessions, managed WSL sessions), and the test suite points it at a stub.
  2. `orca-dev` when `ORCA_DEV_REPO_ROOT` is set — a dev checkout's launcher.
  3. `orca-ide` on Linux, WSL included. Orca's Linux executable, `.deb` and `.rpm` are all
     `orca-ide` by construction (`src/main/cli/bundled-cli-launcher-path.ts`
     LINUX_CLI_COMMAND_NAME). Bare `orca` on a Linux host outside an Orca terminal normally
     resolves to the GNOME Orca screen reader at /usr/bin/orca and starts speech on the
     user's machine — upstream's stated reason, not folklore.
  4. `orca` everywhere else (macOS, Windows).

Resolution never consults PATH: the name is a policy decision, and a missing executable is
reported by the caller (or by `--path` below), never silently swapped for another build.

Usage:
  python3 orca_cli.py            # print the resolved command name
  python3 orca_cli.py --path     # print the resolved absolute path; exit 1 when not on PATH
Library:
  from orca_cli import resolve
  argv = [resolve(), "orchestration", "check", "--json"]

Exit: 0 printed · 1 (`--path`) the resolved command is not on PATH · 2 usage.
"""
from __future__ import annotations

import os
import platform
import shutil
import sys

LINUX_COMMAND = "orca-ide"
DEFAULT_COMMAND = "orca"
DEV_COMMAND = "orca-dev"


def resolve(env=None, system=None) -> str:
    """The command name to execute, per the order in the module docstring.

    `env` and `system` are injectable for tests; production callers pass nothing.
    """
    env = os.environ if env is None else env
    configured = (env.get("ORCA_CLI_COMMAND") or "").strip()
    if configured:
        return configured
    if (env.get("ORCA_DEV_REPO_ROOT") or "").strip():
        return DEV_COMMAND
    system = platform.system() if system is None else system
    if system == "Linux":
        return LINUX_COMMAND
    return DEFAULT_COMMAND


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == []:
        print(resolve())
        return 0
    if argv == ["--path"]:
        name = resolve()
        found = shutil.which(name)
        if not found:
            print(f"orca_cli: `{name}` is not on PATH", file=sys.stderr)
            return 1
        print(found)
        return 0
    print("usage: orca_cli.py [--path]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
