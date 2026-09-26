#!/usr/bin/env python3
"""Contract tests for scripts/install.sh `orca status` readiness (S23).

Assessment: `orca status --json` readiness IS machine-checkable
(app.running + runtime.reachable + runtime.state == ready; graph is folded
into runtime.state upstream). But install.sh's orca prerequisites are SOFT
by doctrine — warnings only, since the catalog installs without a running
app. So readiness lands as a soft WARN like the version floor, and the HARD
gate stays PARKED (needs-human policy: it would refuse headless/CI installs
where the app simply is not launched yet).

These tests pin the soft behavior via --check: ready → no readiness warn;
not-ready/unreadable → WARN, still exit 0.
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / "scripts" / "install.sh"

READY = {"app": {"running": True, "pid": 123},
         "runtime": {"state": "ready", "reachable": True,
                     "runtimeId": "rt_1"},
         "graph": {"state": "ready"}}
NOT_RUNNING = {"app": {"running": False, "pid": None},
               "runtime": {"state": "not_running", "reachable": False,
                           "runtimeId": None},
               "graph": {"state": "not_running"}}
GRAPH_DOWN = {"app": {"running": True, "pid": 123},
              "runtime": {"state": "graph_not_ready", "reachable": True,
                          "runtimeId": "rt_1"},
              "graph": {"state": "starting"}}


def run_check(status_payload="__ready__", version="1.4.209", no_orca=False):
    """Run install.sh --check with a stub orca; return (rc, stdout, stderr).

    status_payload: dict for `status --json`, "garbage" for unparseable, or
    "__ready__" for the READY receipt.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        bindir = tmp / "bin"
        bindir.mkdir()
        skills = tmp / "skills"
        skills.mkdir()
        for d in (ROOT / "skills").iterdir():
            if d.is_dir() and (d / "SKILL.md").is_file() \
                    and not d.name.startswith((".", "_")):
                (skills / d.name).symlink_to(d)
        if not no_orca:
            status_doc = READY if status_payload == "__ready__" \
                else status_payload
            status_text = status_doc if isinstance(status_doc, str) \
                else json.dumps({"result": status_doc})
            (bindir / "status.txt").write_text(status_text)
            stub = bindir / "orca"
            stub.write_text(
                "#!/bin/sh\n"
                f"if [ \"$1\" = \"status\" ]; then cat \"{bindir / 'status.txt'}\";\n"
                f"else echo \"{version}\"; fi\n")
            stub.chmod(0o755)
        env = dict(os.environ)
        base = os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
        if no_orca:
            # Drop every dir shipping an orca binary so the stub-less run
            # really sees no orca CLI.
            base = [d for d in base if not (
                (Path(d) / "orca").exists()
                or (Path(d) / "orca-ide").exists())]
        env["PATH"] = os.pathsep.join([str(bindir), *base])
        env["HOME"] = str(tmp)
        p = subprocess.run(["sh", str(INSTALL), "--check",
                            f"--skills-dir={skills}"],
                           env=env, capture_output=True, text=True, timeout=120)
        return p.returncode, p.stdout, p.stderr


class TestReadinessWarn(unittest.TestCase):
    def test_ready_status_warns_nothing_about_readiness(self):
        rc, out, err = run_check()
        self.assertEqual(rc, 0, err)
        blob = out + err
        self.assertNotIn("not ready", blob)
        self.assertNotIn("readiness", blob)

    def test_app_not_running_warns_but_install_verifies(self):
        rc, out, err = run_check(status_payload=NOT_RUNNING)
        self.assertEqual(rc, 0, err)
        self.assertIn("not ready", out + err)

    def test_graph_not_ready_warns(self):
        rc, out, err = run_check(status_payload=GRAPH_DOWN)
        self.assertEqual(rc, 0, err)
        self.assertIn("not ready", out + err)

    def test_unreadable_status_warns(self):
        rc, out, err = run_check(status_payload="garbage{{{")
        self.assertEqual(rc, 0, err)
        self.assertIn("readiness", out + err)

    def test_no_orca_keeps_the_old_warn_only(self):
        rc, out, err = run_check(no_orca=True)
        self.assertEqual(rc, 0, err)
        self.assertIn("no orca CLI", out + err)


if __name__ == "__main__":
    unittest.main()
