"""Execute published merge/precheck commands against disposable state, never live services."""
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def inline_commands(path):
    return re.findall(r"`([^`\n]+)`", (ROOT / path).read_text())


class MergeCommands(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="Fixture",
                        GIT_AUTHOR_EMAIL="fixture@example.invalid",
                        GIT_COMMITTER_NAME="Fixture",
                        GIT_COMMITTER_EMAIL="fixture@example.invalid")
        self.git("init", "-b", "base")
        self.git("commit", "--allow-empty", "-m", "base")
        self.git("checkout", "-b", "candidate")
        self.git("commit", "--allow-empty", "-m", "reviewed")
        self.reviewed = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "base")
        self.commands = inline_commands("runtime/merge-serialization.md")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, check=True)

    def advance(self):
        self.git("checkout", "candidate")
        self.git("commit", "--allow-empty", "-m", "unreviewed")
        moved = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "base")
        return moved

    def local_merge(self):
        command = next(c for c in self.commands if "git merge --no-ff" in c)
        command = command.replace("<branch>", "candidate").replace(
            "<reviewed_sha>", self.reviewed)
        return subprocess.run(["sh", "-c", command], cwd=self.repo, env=self.env,
                              capture_output=True, text=True)

    def test_local_merge_preserves_reviewed_commit(self):
        self.assertEqual(self.local_merge().returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD^2").stdout.strip(), self.reviewed)

    def test_local_advanced_head_refuses_without_moving_base(self):
        self.advance()
        before = self.git("rev-parse", "HEAD").stdout
        result = self.local_merge()
        self.assertNotEqual(result.returncode, 0, "concurrent unreviewed head was merged")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, before)

    def test_local_move_after_guard_cannot_substitute_unreviewed_commit(self):
        moved = self.advance()
        self.git("update-ref", "refs/heads/candidate", self.reviewed)
        real_git = shutil.which("git")
        shim = self.repo / "git"
        # Advance after the read-side guard, immediately before the actual merge.
        shim.write_text(f"#!{sys.executable}\nimport os, subprocess, sys\n" +
                        f"git = {real_git!r}\n" +
                        "if sys.argv[1] == 'merge':\n" +
                        "    subprocess.run([git, 'update-ref', 'refs/heads/candidate', " +
                        f"{moved!r}], check=True)\n" +
                        "os.execv(git, [git, *sys.argv[1:]])\n")
        shim.chmod(0o755)
        self.env["PATH"] = f"{self.repo}:{os.environ['PATH']}"
        self.assertEqual(self.local_merge().returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD^2").stdout.strip(), self.reviewed)
        self.assertEqual(self.git("rev-parse", "candidate").stdout.strip(), moved)

    def github_merge(self, current):
        # gh's documented expected-head precondition, isolated from GitHub.
        fake = self.repo / "gh"
        fake.write_text(f"#!{sys.executable}\n" +
                        "import os, sys\na = sys.argv[1:]\n" +
                        "expected = a[a.index('--match-head-commit') + 1] " +
                        "if '--match-head-commit' in a else os.environ['CURRENT_HEAD']\n" +
                        "sys.exit(0 if expected == os.environ['CURRENT_HEAD'] else 1)\n")
        fake.chmod(0o755)
        command = next(c for c in self.commands if c.startswith("gh pr merge <n>"))
        command = command.replace("<n>", "1").replace("<reviewed_sha>", self.reviewed)
        return subprocess.run(shlex.split(command), cwd=self.repo, capture_output=True,
                              env=dict(self.env, PATH=f"{self.repo}:{os.environ['PATH']}",
                                       CURRENT_HEAD=current))

    def test_github_unchanged_reviewed_head_merges(self):
        self.assertEqual(self.github_merge(self.reviewed).returncode, 0)

    def test_github_advanced_head_refuses(self):
        self.assertNotEqual(self.github_merge(self.advance()).returncode, 0,
                            "merge by PR number accepted an unreviewed head")


class ScheduledPrechecks(unittest.TestCase):
    def run_precheck(self, kind, result):
        commands = inline_commands("runtime/mission-scheduling.md")
        command = next(c for c in commands if f"gh {kind} list" in c)
        command = command.replace("<label>", "audit")
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "gh"
            # The fixture enforces gh's JSON/jq argument contract and models its
            # exit behavior: selecting null still exits zero; API errors do not.
            fake.write_text(f"#!{sys.executable}\n" + """
import os, sys
a = sys.argv[1:]
if ('-q' in a or '--jq' in a) and '--json' not in a:
    print('cannot use --jq without specifying --json', file=sys.stderr)
    sys.exit(1)
if '--json' not in a or a[a.index('--json') + 1] != 'number':
    sys.exit(2)
state = os.environ['FIXTURE_RESULT']
if state == 'api-error':
    print('1')  # A partial response must not override the failed command.
    sys.exit(1)
flag = '--jq' if '--jq' in a else '-q'
query = a[a.index(flag) + 1]
if query == 'length':
    print(1 if state == 'nonempty' else 0)
elif query == '.[0]':
    print('{"number": 1}' if state == 'nonempty' else 'null')
else:
    sys.exit(2)
""")
            fake.chmod(0o755)
            return subprocess.run(["sh", "-c", command], capture_output=True, text=True,
                                  env=dict(os.environ, PATH=f"{tmp}:{os.environ['PATH']}",
                                           FIXTURE_RESULT=result))

    def test_nonempty_backlog_runs(self):
        for kind in ("issue", "pr"):
            with self.subTest(kind=kind):
                result = self.run_precheck(kind, "nonempty")
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_backlog_skips(self):
        for kind in ("issue", "pr"):
            with self.subTest(kind=kind):
                self.assertNotEqual(self.run_precheck(kind, "empty").returncode, 0)

    def test_api_failure_skips(self):
        for kind in ("issue", "pr"):
            with self.subTest(kind=kind):
                self.assertNotEqual(self.run_precheck(kind, "api-error").returncode, 0)
