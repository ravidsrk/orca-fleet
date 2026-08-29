#!/usr/bin/env python3
"""#163: demo/negative-control/run.sh must compute its contract digest portably — sha256sum
(GNU) or `shasum -a 256` (macOS), whichever exists. Each test runs the demo end-to-end under a
hermetic PATH exposing exactly ONE spelling (a python shim computing the real digest), so both
halves of the fallback are exercised on any host.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN_SH = ROOT / "demo" / "negative-control" / "run.sh"

# Accepts both spellings' argv shapes (`sha256sum FILE`, `shasum -a 256 FILE`); prints the
# digest first, which is all run.sh's awk reads.
_DIGEST_SHIM = """#!/usr/bin/env python3
import hashlib, sys
path = sys.argv[-1]
print(hashlib.sha256(open(path, "rb").read()).hexdigest() + "  " + path)
"""


def _hermetic_path(bindir: Path, digest_tool: str) -> str:
    """A PATH dir with the demo's tool deps symlinked in and exactly one digest spelling shimmed."""
    for tool in ("dirname", "date", "awk", "git"):
        real = shutil.which(tool)
        if real:
            os.symlink(real, bindir / tool)
    os.symlink(sys.executable, bindir / "python3")
    shim = bindir / digest_tool
    shim.write_text(_DIGEST_SHIM, encoding="utf-8")
    shim.chmod(0o755)
    return str(bindir)


class NegativeControlDigestPortability(unittest.TestCase):
    def _run_demo(self, digest_tool: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as d:
            env = {"PATH": _hermetic_path(Path(d), digest_tool),
                   "HOME": os.environ.get("HOME", "")}
            return subprocess.run(["/bin/sh", str(RUN_SH)], capture_output=True, text=True,
                                  cwd=ROOT, env=env)

    def test_demo_passes_with_gnu_sha256sum_only(self):
        r = self._run_demo("sha256sum")
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("PASS:", r.stdout)

    def test_demo_passes_with_macos_shasum_only(self):
        r = self._run_demo("shasum")
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("PASS:", r.stdout)


if __name__ == "__main__":
    unittest.main()
