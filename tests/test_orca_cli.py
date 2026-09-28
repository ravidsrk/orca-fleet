"""#510: the Orca CLI command name is resolved in one place, the way upstream documents it.

Orca's Linux executable is `orca-ide` (`src/main/cli/bundled-cli-launcher-path.ts`
LINUX_CLI_COMMAND_NAME); bare `orca` on a Linux host outside an Orca terminal is the GNOME
screen reader. Before this, eight operator tools and spawn_worker.sh spelled the executable
`orca` verbatim, so the fleet could not run on the platform most servers use. These tests pin
the resolution order, the CLI entrypoint, and — the part that keeps the bug from returning —
that no script under runtime/scripts/ names the executable itself.
"""
import contextlib
import importlib.util
import io
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "runtime" / "scripts"
RESOLVER = SCRIPTS / "orca_cli.py"

TOOLS = ["check_reply.py", "hitl_ask.py", "search_sessions.py", "send_msg.py", "task_ops.py",
         "terminal_ops.py", "worker_ops.py", "worktree_ops.py"]


def _load():
    spec = importlib.util.spec_from_file_location("orca_cli", RESOLVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ResolutionOrder(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_orca_cli_command_wins_everywhere(self):
        # Orca exports it inside the sessions it manages; tests point it at a stub.
        for system in ("Linux", "Darwin", "Windows"):
            self.assertEqual(self.m.resolve({"ORCA_CLI_COMMAND": "/opt/x/orca"}, system),
                             "/opt/x/orca")

    def test_a_blank_orca_cli_command_is_unset(self):
        self.assertEqual(self.m.resolve({"ORCA_CLI_COMMAND": "  "}, "Darwin"), "orca")

    def test_dev_checkout_uses_orca_dev(self):
        self.assertEqual(self.m.resolve({"ORCA_DEV_REPO_ROOT": "/src/orca"}, "Linux"), "orca-dev")
        self.assertEqual(self.m.resolve({"ORCA_DEV_REPO_ROOT": "/src/orca"}, "Darwin"), "orca-dev")

    def test_linux_is_orca_ide_never_bare_orca(self):
        self.assertEqual(self.m.resolve({}, "Linux"), "orca-ide")

    def test_macos_and_windows_are_orca(self):
        self.assertEqual(self.m.resolve({}, "Darwin"), "orca")
        self.assertEqual(self.m.resolve({}, "Windows"), "orca")

    def test_the_host_platform_is_consulted_when_none_is_given(self):
        import platform
        want = "orca-ide" if platform.system() == "Linux" else "orca"
        self.assertEqual(self.m.resolve({}), want)


class CommandLine(unittest.TestCase):
    """main() in this process (the D9 coverage floor sees it; a subprocess is invisible to
    the shard's tracer) under the environment a subprocess would have had, plus one real
    subprocess call that proves the entry point."""

    def setUp(self):
        self.m = _load()

    def main(self, argv, env):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.m.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_prints_the_name(self):
        code, out, _ = self.main([], {"PATH": os.environ["PATH"], "ORCA_CLI_COMMAND": "orca-stub"})
        self.assertEqual((code, out.strip()), (0, "orca-stub"))

    def test_path_mode_fails_closed_when_the_command_is_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = self.main(["--path"], {"PATH": tmp, "ORCA_CLI_COMMAND": "orca-stub"})
        self.assertEqual(code, 1, err)
        self.assertIn("not on PATH", err)
        self.assertEqual(out, "")

    def test_path_mode_prints_the_resolved_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp) / "orca-stub"
            stub.write_text("#!/bin/sh\nexit 0\n")
            stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
            code, out, _ = self.main(["--path"], {"PATH": tmp, "ORCA_CLI_COMMAND": "orca-stub"})
            self.assertEqual((code, out.strip()), (0, str(stub)))

    def test_unknown_arguments_are_usage(self):
        code, out, err = self.main(["--bogus"], {"PATH": os.environ["PATH"]})
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("usage", err)

    def test_runs_as_a_program(self):
        p = subprocess.run([sys.executable, str(RESOLVER)], capture_output=True, text=True,
                           env={"PATH": os.environ["PATH"], "ORCA_CLI_COMMAND": "orca-stub"})
        self.assertEqual((p.returncode, p.stdout.strip()), (0, "orca-stub"))


class NoScriptNamesTheExecutable(unittest.TestCase):
    """The contract: the executable is a policy decision made once, in orca_cli.py."""

    LITERAL_ARGV = re.compile(r'subprocess\.run\(\s*\[\s*["\']orca["\']')
    SHELL_INVOCATION = re.compile(r'(^|[^\w/`.$-])orca (--version|vm |orchestration |terminal |worktree |"\$@")')

    def test_every_operator_tool_resolves_through_orca_cli(self):
        for name in TOOLS:
            text = (SCRIPTS / name).read_text(encoding="utf-8")
            with self.subTest(tool=name):
                self.assertIn("import orca_cli", text)
                self.assertIn("orca_cli.resolve()", text)
                self.assertIsNone(self.LITERAL_ARGV.search(text),
                                  f"{name} still spells the executable `orca` in an argv")

    def test_no_python_script_builds_a_bare_orca_argv(self):
        for path in sorted(SCRIPTS.glob("*.py")):
            if path.name == "orca_cli.py":
                continue
            with self.subTest(script=path.name):
                self.assertIsNone(self.LITERAL_ARGV.search(path.read_text(encoding="utf-8")))

    def test_spawn_worker_runs_the_resolved_command(self):
        text = (SCRIPTS / "spawn_worker.sh").read_text(encoding="utf-8")
        self.assertIn('ORCA_BIN="$(python3 "$HERE/orca_cli.py")"', text)
        offenders = [line for line in text.splitlines()
                     if not line.lstrip().startswith("#") and self.SHELL_INVOCATION.search(line)]
        self.assertEqual(offenders, [], "spawn_worker.sh invokes a bare `orca`")
        self.assertNotIn("command -v orca ", text)
        self.assertNotIn("command -v orca>", text)

    def test_the_detector_sees_a_planted_bare_invocation(self):
        # A guard that cannot fail is not a guard: the two regexes must catch the shapes
        # that were actually in the tree before #510.
        self.assertIsNotNone(self.LITERAL_ARGV.search('proc = subprocess.run(["orca", *argv, "--json"],'))
        self.assertIsNotNone(self.SHELL_INVOCATION.search('  orca orchestration worker-start --task "$task"'))
        self.assertIsNotNone(self.SHELL_INVOCATION.search('  orca "$@" --json > "$out"'))
        # ...and must not cry wolf on the resolved forms.
        self.assertIsNone(self.SHELL_INVOCATION.search('  "$ORCA_BIN" orchestration worker-start'))
        self.assertIsNone(self.SHELL_INVOCATION.search('  orca_json "$tl" orchestration task-list'))


if __name__ == "__main__":
    unittest.main()
