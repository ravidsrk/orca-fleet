#!/usr/bin/env python3
"""Contract tests for runtime/scripts/diff_scope.py.

The classification table is easy to test and easy to get wrong in a way nobody
notices. What matters more is the exit contract: "we could not look" and
"nothing matched" must both be loud, because a silent all-false gates every
review lens off and records a legitimate-looking zero.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCOPE = ROOT / "runtime" / "scripts" / "diff_scope.py"


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check)


def write(repo, rel, text=""):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class ScopeBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="diffscope-")
        self.repo = Path(self.tmp) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.invalid")
        git(self.repo, "config", "user.name", "t")
        write(self.repo, "README.md", "# base\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")
        git(self.repo, "checkout", "-q", "-b", "work")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_scope(self, *args):
        return subprocess.run([sys.executable, str(SCOPE), "--repo", str(self.repo), *args],
                              capture_output=True, text=True)

    def flags(self, *args):
        r = self.run_scope("--base", "main", "--json", *args)
        return json.loads(r.stdout), r

    def assert_flag(self, name, rel, content=""):
        write(self.repo, rel, content)
        data, r = self.flags()
        self.assertIsNone(data["error"], r.stdout + r.stderr)
        self.assertTrue(data["flags"][name], f"{rel} should set SCOPE_{name}: {data['flags']}")


class TestExitContract(ScopeBase):
    def test_unresolvable_base_is_no_base_and_exit_2(self):
        r = self.run_scope("--base", "origin/nope")
        self.assertEqual(r.returncode, 2, "a green here would mean we could not look")
        self.assertIn("SCOPE_ERROR=no_base", r.stdout)
        self.assertIn("SCOPE_FRONTEND=false", r.stdout)

    def test_no_changes_is_a_legitimate_clean_zero(self):
        r = self.run_scope("--base", "main")
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("SCOPE_ERROR", r.stdout)
        self.assertIn("SCOPE_BACKEND=false", r.stdout)

    def test_changed_but_unmatched_is_exit_2_and_prints_the_paths(self):
        write(self.repo, "weirdlayout/thing.qqq", "x")
        r = self.run_scope("--base", "main")
        self.assertEqual(r.returncode, 2)
        self.assertIn("SCOPE_ERROR=unmatched", r.stdout)
        self.assertIn("# unmatched: weirdlayout/thing.qqq", r.stdout)

    def test_output_is_shell_safe(self):
        write(self.repo, "src/app.py", "x = 1\n")
        r = self.run_scope("--base", "main")
        for line in r.stdout.splitlines():
            self.assertTrue(line.startswith("#") or "=" in line,
                            f"non-sourceable line: {line!r}")

    def test_help_exits_zero(self):
        r = subprocess.run([sys.executable, str(SCOPE), "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("--base", r.stdout)

    def test_every_flag_is_printed_even_when_false(self):
        r = self.run_scope("--base", "main")
        for name in ("FRONTEND", "BACKEND", "PROMPTS", "TESTS", "DOCS", "CONFIG",
                     "MIGRATIONS", "API", "AUTH", "SECURITY", "A11Y", "PERF"):
            self.assertIn(f"SCOPE_{name}=", r.stdout)


class TestPathClassification(ScopeBase):
    def test_frontend_component(self):
        self.assert_flag("FRONTEND", "app/components/Button.tsx", "export const B = () => null;\n")

    def test_frontend_stylesheet(self):
        self.assert_flag("FRONTEND", "styles/main.scss", ".a { color: red; }\n")

    def test_backend_source(self):
        self.assert_flag("BACKEND", "lib/worker.py", "def go():\n    return 1\n")

    def test_backend_excludes_frontend_view_files(self):
        write(self.repo, "app/components/Button.tsx", "export const B = () => null;\n")
        data, _ = self.flags()
        self.assertTrue(data["flags"]["FRONTEND"])
        self.assertFalse(data["flags"]["BACKEND"], "a view file is not backend")

    def test_tests_directory(self):
        self.assert_flag("TESTS", "tests/test_worker.py", "def test_x():\n    assert True\n")

    def test_spec_suffix(self):
        self.assert_flag("TESTS", "lib/worker.spec.ts", "it('x', () => {});\n")

    def test_docs(self):
        self.assert_flag("DOCS", "docs/guide.md", "# guide\n")

    def test_config_yaml(self):
        self.assert_flag("CONFIG", ".github/workflows/ci.yml", "on: push\n")

    def test_config_manifest(self):
        self.assert_flag("CONFIG", "package.json", "{}\n")

    def test_migrations(self):
        self.assert_flag("MIGRATIONS", "db/migrate/20260101_add_users.rb", "class X; end\n")

    def test_api_route_file(self):
        self.assert_flag("API", "app/controllers/users_controller.rb", "class C; end\n")

    def test_api_schema(self):
        self.assert_flag("API", "schema/public.graphql", "type Q { a: Int }\n")

    def test_auth_path(self):
        self.assert_flag("AUTH", "lib/session_store.py", "SESSION = {}\n")

    def test_security_path(self):
        self.assert_flag("SECURITY", "lib/crypto_helpers.py", "KEY = 1\n")

    def test_a11y_path(self):
        self.assert_flag("A11Y", "docs/a11y-notes.md", "# notes\n")

    def test_perf_path(self):
        self.assert_flag("PERF", "bench/throughput.py", "N = 1\n")

    def test_prompts_path(self):
        self.assert_flag("PROMPTS", "skills/ship-it/SKILL.md", "---\nname: x\n---\n")


class TestContentClassification(ScopeBase):
    def test_security_by_content(self):
        self.assert_flag("SECURITY", "lib/tool.py", "import subprocess\nsubprocess.run(['ls'], shell=True)\n")

    def test_a11y_by_content(self):
        self.assert_flag("A11Y", "web/page.html", '<button aria-label="close">x</button>\n')

    def test_perf_by_content(self):
        self.assert_flag("PERF", "lib/hot.py", "from functools import lru_cache\n@lru_cache\ndef f():\n    return 1\n")

    def test_auth_by_content(self):
        self.assert_flag("AUTH", "lib/entry.py", "def handler():\n    return authorize(current_user)\n")

    def test_api_by_content(self):
        self.assert_flag("API", "lib/server.py", "@app.route('/x')\ndef x():\n    return 1\n")

    def test_prompts_by_content(self):
        self.assert_flag("PROMPTS", "lib/gen.py", 'TEMPLATE = "You are a helpful assistant."\n')

    def test_a_deleted_file_contributes_only_path_signals(self):
        write(self.repo, "lib/session_thing.py", "x = 1\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "add")
        (self.repo / "lib" / "session_thing.py").unlink()
        data, r = self.flags()
        self.assertTrue(data["flags"]["AUTH"], r.stdout)


class TestUnionOfSources(ScopeBase):
    def test_untracked_file_counts(self):
        write(self.repo, "db/migrate/20260202_new.rb", "class Y; end\n")
        data, _ = self.flags()
        self.assertTrue(data["flags"]["MIGRATIONS"], "a new migration is untracked until the commit")

    def test_committed_change_counts(self):
        write(self.repo, "lib/thing.py", "x = 1\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "add")
        data, _ = self.flags()
        self.assertTrue(data["flags"]["BACKEND"])

    def test_staged_but_uncommitted_change_counts(self):
        write(self.repo, "lib/staged.py", "x = 1\n")
        git(self.repo, "add", "-A")
        data, _ = self.flags()
        self.assertTrue(data["flags"]["BACKEND"])

    def test_json_shape(self):
        write(self.repo, "lib/thing.py", "x = 1\n")
        data, _ = self.flags()
        self.assertEqual(sorted(data.keys()), ["base", "error", "flags", "unmatched"])
        self.assertEqual(len(data["flags"]), 12)


class TestScriptShape(unittest.TestCase):
    def test_executable_and_shebanged(self):
        self.assertTrue(os.access(SCOPE, os.X_OK))
        self.assertTrue(SCOPE.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"))

    def test_docstring_carries_the_classification_table(self):
        text = SCOPE.read_text(encoding="utf-8")
        for flag in ("SCOPE_FRONTEND", "SCOPE_MIGRATIONS", "SCOPE_A11Y", "SCOPE_PERF"):
            self.assertIn(flag, text.split('"""')[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
