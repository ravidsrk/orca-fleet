#!/usr/bin/env python3
"""U1 negative-control probe (coordinator-supplied --nc-command target).

Installs THIS worktree's .github/ci-tools.lock into a fresh venv with
`pip --require-hashes --only-binary :all:` (the same flags CI uses), then
asserts the installed ruff reports EXPECTED and agentskills runs.

Exit 0 iff the lockfile in this tree resolves to the upgraded ruff.
Under the revert control (lock restored from base_sha) the ruff assertion
fails with AssertionError (RED); at the clean head it passes.

Resolves the repo root from its own path, so it runs identically at any
checkout (including verify.py's throwaway worktrees).
"""

import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED_RUFF = "0.16.7"


def run(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, check=False, **kw)


def main() -> int:
    repo = Path(__file__).resolve().parents[3]
    lock = repo / ".github" / "ci-tools.lock"
    assert lock.is_file(), f"lockfile missing: {lock}"
    with tempfile.TemporaryDirectory(prefix="modernize-nc-") as tmp:
        venv = Path(tmp) / "venv"
        p = run([sys.executable, "-m", "venv", str(venv)])
        assert p.returncode == 0, f"venv create failed: {p.stderr[-2000:]}"
        pip = str(venv / "bin" / "pip")
        p = run([pip, "install", "--quiet", "--require-hashes",
                 "--only-binary", ":all:", "-r", str(lock)])
        assert p.returncode == 0, f"hash-pinned install failed: {p.stderr[-2000:]}"
        p = run([str(venv / "bin" / "ruff"), "--version"])
        assert p.returncode == 0, f"ruff --version failed: {p.stderr[-2000:]}"
        got = (p.stdout + p.stderr).strip()
        assert EXPECTED_RUFF in got, (
            f"expected installed ruff {EXPECTED_RUFF}, got: {got}")
        p = run([str(venv / "bin" / "agentskills"), "--version"])
        assert p.returncode == 0, f"agentskills --version failed: {p.stderr[-2000:]}"
    print(f"NC probe GREEN: lock installs hashed-clean; ruff {EXPECTED_RUFF}; "
          f"agentskills runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
