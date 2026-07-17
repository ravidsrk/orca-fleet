#!/usr/bin/env python3
"""Contract tests for runtime/scripts/spawn_worker.sh hardening (issues #43, #44).

These exercise the real script through its SW_SELFTEST hook, which computes the two
hardened values (validated effort, collision-safe scratch key) and exits before any
orchestration side effect. Standard library only.
"""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPAWN = ROOT / "runtime" / "scripts" / "spawn_worker.sh"


def run(title, agent="claude", effort="high", task="task_test"):
    """Invoke spawn_worker.sh in self-test mode; return (rc, stdout, stderr)."""
    p = subprocess.run(
        ["bash", str(SPAWN), task, "active", title, agent, effort],
        env={"SW_SELFTEST": "1", "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True,
    )
    return p.returncode, p.stdout, p.stderr


class TestSpawnWorkerHardening(unittest.TestCase):

    def test_scratch_key_distinguishes_tr_colliding_titles(self):
        # #44: "Fix: a/b" and "Fix: a\\b" both tr-squash to the same name; the raw-title
        # checksum must keep their scratch keys distinct so parallel spawns don't clobber.
        _, out_a, _ = run("Fix: a/b")
        _, out_b, _ = run("Fix: a\\b")
        key_a = next(l for l in out_a.splitlines() if l.startswith("safe_title="))
        key_b = next(l for l in out_b.splitlines() if l.startswith("safe_title="))
        self.assertNotEqual(key_a, key_b,
                            "tr-colliding titles must yield distinct scratch keys")

    def test_invalid_effort_is_refused(self):
        # #43: effort is interpolated into the codex launch command; an unknown value must
        # be rejected (fail closed), never interpolated verbatim.
        rc, _, err = run("t", effort='high"; touch /tmp/pwned; echo "')
        self.assertNotEqual(rc, 0, "invalid effort must be refused")
        self.assertIn("invalid effort", err)

    def test_valid_effort_accepted(self):
        for eff in ("minimal", "low", "medium", "high", "xhigh"):
            rc, out, _ = run("t", effort=eff)
            self.assertEqual(rc, 0, f"valid effort {eff} should pass")
            self.assertIn(f"effort={eff}", out)


if __name__ == "__main__":
    unittest.main()
