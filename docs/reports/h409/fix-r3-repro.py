"""h409 round-3 repros: R1 / R2 / R3 driven against runtime/scripts/verify.py as a SUBPROCESS
with a crafted PATH on top of the suite's real mutation fixture (a real two-commit repo, a full
valid manifest, an executable revert control). Run from the repo root: python3 docs/reports/h409/fix-r3-repro.py R1|R2|R3"""
import os, sys, shlex, shutil, subprocess, tempfile, unittest
from pathlib import Path
sys.path.insert(0, os.getcwd())
from tests import test_verify as tv

V = str(Path("runtime/scripts/verify.py").resolve())


class Repro(tv.MutationFixture):
    def setUp(self):
        super().setUp()
        self.root = Path(tempfile.mkdtemp(prefix="orca-r3-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.tools = self.root / "tools"; self.tools.mkdir()
        os.symlink(shutil.which("git"), self.tools / "git")
        self.log = self.root / "consulted.log"

    def stub_gh(self, where, extra=""):
        where.parent.mkdir(parents=True, exist_ok=True)
        where.write_text("#!/bin/sh\n" + extra +
                         f"echo \"GH ARGV: $*\" >> {shlex.quote(str(self.log))}\n"
                         "case \"$*\" in *reviews*) echo '[{\"state\":\"APPROVED\",\"commit_id\":\"" + self.head_sha + "\","
                         "\"user\":{\"login\":\"carol\"}}]';; *) echo '{\"user\":{\"login\":\"alice\"}}';; esac\n")
        where.chmod(0o755)

    def run_verify(self, path_dirs, *extra, env_extra=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GH_")}
        env["PATH"] = os.pathsep.join(str(d) for d in path_dirs)
        env["ORCA_HEAD"] = self.head_sha
        env.update(env_extra or {})
        p = subprocess.run([sys.executable, V, "--manifest", self._manifest(nc=self._revert_nc()),
                            "--contract-source", self.contract, "--contract-digest", self.digest,
                            "--unit-class", "mutation", "--repo", "o/r", "--execute-nc",
                            "--nc-command", self.proof_cmd, *extra],
                           cwd=self.repo, env=env, capture_output=True, text=True)
        print("rc=", p.returncode); print("OUT:", p.stdout.strip()); print("ERR:", p.stderr.strip())
        return p

    def test_R1(self):
        # a gh planted by the worker in a user-writable dir whose NAME is on SYSTEM_BINS
        listed = Path("/opt/homebrew/sbin")
        if not (listed.is_dir() and os.access(listed, os.W_OK)):
            self.skipTest("no user-writable listed dir on this host")
        stub = listed / "gh"
        self.assertFalse(stub.exists(), "refusing to overwrite an existing gh")
        self.stub_gh(stub)
        self.addCleanup(lambda: stub.unlink(missing_ok=True))
        print("which gh (crafted PATH) ->", shutil.which("gh", path=f"{listed}{os.pathsep}{self.tools}"))
        print("== SOUND lane (--provenance ci), worker-planted gh in", listed)
        self.run_verify([listed, self.tools], "--provenance", "ci")
        print("stub gh CONSULTED?:", self.log.exists())
        print("== N2a symlink in listed dir -> worker-writable target; N2b plain file in listed dir")
        target = self.root / "evil-gh"; self.stub_gh(target)
        link = listed / "gh"; link.unlink(); link.symlink_to(target)
        print("classify(symlink in listed dir) ->", tv.verify._Authority.classify(str(link)))
        link.unlink(); self.stub_gh(stub)
        print("classify(plain file in listed dir) ->", tv.verify._Authority.classify(str(stub)))
        print("classify(/usr/bin/gh) ->", tv.verify._Authority.classify("/usr/bin/gh"))

    def test_R2(self):
        # the executed control plants a LOGGING git stub in an empty dir first on PATH
        drop = self.root / "drop"; drop.mkdir()
        realgh = self.root / "realgh"
        stub = ("#!/bin/sh\n" f"echo \"PLANTED-GIT ARGV: $*\" >> {shlex.quote(str(self.log))}\nexit 1\n")
        self.write("check.py", "import pathlib\n"
                   f"g = pathlib.Path({str(drop / 'git')!r}); g.write_text({stub!r}); g.chmod(0o755)\n"
                   "import app\nassert app.f() == 2, 'AC-1 violated'\n")
        self.head_sha = self.commit("head: proof command that plants a git")
        self.head_tree = self.git("rev-parse", "HEAD^{tree}")
        self.stub_gh(realgh / "gh")
        print("== NATIVE lane, control plants git into", drop)
        self.run_verify([drop, realgh, self.tools])
        print("planted git?:", (drop / "git").exists(), "| CONSULTED post-control?:", self.log.exists() and "PLANTED-GIT" in self.log.read_text())
        if self.log.exists(): print(self.log.read_text())
        print("== SOUND lane, git first on PATH is in a worker-writable dir at startup")
        (drop / "git").unlink(missing_ok=True); os.symlink(shutil.which("git"), drop / "git")
        self.log.unlink(missing_ok=True)
        self.run_verify([drop, realgh, self.tools], "--provenance", "ci")

    def test_R3(self):
        realgh = self.root / "realgh"
        self.stub_gh(realgh / "gh", extra=f"/usr/bin/env | /usr/bin/grep -E '^(GH_|HOME=|PATH=|GITHUB_)' | /usr/bin/cut -d= -f1 >> {shlex.quote(str(self.root / 'env.log'))}\n")
        print("== NATIVE lane, ambient GH_HOST=attacker.example GH_CONFIG_DIR=/evil")
        self.run_verify([realgh, self.tools], env_extra={"GH_HOST": "attacker.example", "GH_CONFIG_DIR": "/evil",
                                                          "GH_TOKEN": "tok-present"})
        envlog = self.root / "env.log"
        print("gh saw env:\n" + (envlog.read_text() if envlog.exists() else "(gh never ran)"))


if __name__ == "__main__":
    suite = unittest.TestSuite([Repro(f"test_{sys.argv[1]}")])
    unittest.TextTestRunner(verbosity=0).run(suite)
