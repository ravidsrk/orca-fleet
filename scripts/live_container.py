#!/usr/bin/env python3
"""live_container.py — the container-based live harness: ONE paid live arm in a fresh, disposable
Linux container, destroyed after (PR #668; docs/guides/live-harness.md is the operator's guide).

  build   build the harness image from scripts/live_container.Dockerfile: the base pinned by
          digest, git, and Claude Code pinned to one version by its official installer, installed
          as the non-root user every arm runs as (the only step that downloads anything)
  run     run one arm in a fresh container of that image and destroy it:
              wip_curve     scripts/wip_curve.py ARGS
              ablation      scripts/ablation.py ARGS
              hint_replay   scripts/hint_replay.py ARGS
              trajectories  scripts/eval.py run --suite trajectories ARGS
              first_run     runtime/scripts/first_run.py ARGS
          ARGS follow `--`; inside the container the repository is /repo (read-only) and the
          results directory is /results, the working directory, where every output must go

Why a container. Process containment (runtime/scripts/containment.py) finds every process of a
paid call by the OF_CALL_ID marker in its environment. On macOS no sweep can see every
descendant: an Apple system binary's environment is hidden from `ps -E`. So every paid live path
refuses on a plain host, and lifts only inside a container this launcher started (containment.
harness_problem): a container marker, the launcher's attestation whose nonce is the container's
own hostname, and the strong probe passing, which it does on Linux. Destroying the container is
the final backstop for anything in-process containment misses, a process that clears its own
environment included.

What the container gets: the image's non-root user, --rm, a pids/memory/CPU limit, no capability,
no-new-privileges, no privileged flag and no host namespace; the subscription token as a read-only
file mount (SECRET) of the operator's 0600 token file, never in the container's environment, so
`docker inspect` never shows it, nor any command line or log (inside, scripts/live_container_bin/
claude, first on PATH, reads it and execs the pinned Claude Code with the token in that process's
own environment); a clean export of the checkout's HEAD, read-only (the launcher refuses a dirty tree, and nothing the container writes reaches the
checkout, its .git or its ignored files); one read-write results directory, so the spend ledger
and the evidence outlive the container; and the attestation, read-only. A wall-clock limit ends
it: the launcher kills and removes the container, then verifies with `docker ps -a --filter`
that it no longer exists. The receipt, written outside every mount, records all of it.

The limit, honestly: this guards against accidents on the host, never against an operator who
deliberately fakes a container (as root: a /.dockerenv, an attestation, a hostname). The
attestation proves which launch a container came from to the receipt, not to an adversary.

Exit: the arm's exit status, once the container is verified destroyed · 2 usage or a refused
start (nothing was created) · 3 the container could not be verified destroyed (fail closed) ·
124 the wall-clock limit ended it (verified destroyed) · 128+N on signal N (verified destroyed).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import secrets
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT  # the checkout whose HEAD runs (a Python-level seam for the launcher's own tests)
DOCKERFILE = ROOT / "scripts" / "live_container.Dockerfile"
CLAUDE_CODE = "2.1.304"
IMAGE = f"open-fleet-live:claude-{CLAUDE_CODE}"
LABEL = "org.open-fleet.live-harness"  # every harness container carries it: its value is the nonce
DOCKERFILE_LABEL = "org.open-fleet.dockerfile-sha256"
TOKEN_ENV = "CLAUDE_CODE_OAUTH_TOKEN"  # set by the in-container wrapper in claude's own process, nowhere else
TOKEN_FILE = "~/of-live/oauth-token"
RECEIPTS = "~/of-live/receipts"
USER = "10001:10001"  # the image's `runner`, never root
REPO_IN, RESULTS_IN = "/repo", "/results"
SECRET = "/run/secrets/claude_token"  # the token: a read-only file mount, never the container's environment
WRAPPER_DIR = "scripts/live_container_bin"  # its `claude` reads SECRET and execs the pinned Claude Code
# The container's whole PATH: the wrapper first, and never ~/.local/bin, where the raw binary lies.
CONTAINER_PATH = f"{REPO_IN}/{WRAPPER_DIR}:/usr/local/bin:/usr/bin:/bin"
ARMS = {
    "wip_curve": ("scripts/wip_curve.py",),
    "ablation": ("scripts/ablation.py",),
    "hint_replay": ("scripts/hint_replay.py",),
    "trajectories": ("scripts/eval.py", "run", "--suite", "trajectories"),
    "first_run": ("runtime/scripts/first_run.py",),
}
LIMITS = {"pids": 4096, "memory": "8g", "cpus": "4"}
BACKSTOP_S = 120  # the in-container `timeout`, past the launcher's limit: a dead launcher still ends it
DESTROY_WAIT_S = 30
RECEIPT_SCHEMA = "open-fleet.live-container-receipt/1"
EXIT_USAGE, EXIT_NOT_DESTROYED, EXIT_TIMED_OUT = 2, 3, 124


def _load(name, path):
    """A runtime module by path, writing no bytecode beside it."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    prior, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = prior
    return mod


# The attestation contract (its path, schema and hostname) is containment.py's: one definition,
# read by the check inside the container and written here. Git runs hardened (#629).
containment = _load("live_container_containment", ROOT / "runtime" / "scripts" / "containment.py")
gitexec = _load("live_container_gitexec", ROOT / "runtime" / "scripts" / "gitexec.py")


class Refused(Exception):
    """A refused start: nothing was created (exit 2)."""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def docker_env():
    """The launcher's environment for a docker client, without a token it may have inherited."""
    return {k: v for k, v in os.environ.items() if k != TOKEN_ENV}


def docker(*args, timeout=120):
    """`docker ARGS` (whatever `docker` PATH names), captured; never raises on a nonzero exit."""
    exe = shutil.which("docker")
    if not exe:
        raise Refused("no `docker` on PATH (OrbStack or Docker Engine)")
    return subprocess.run([exe, *args], env=docker_env(), stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, errors="replace", timeout=timeout)


def git(repo, *args, timeout=300):
    proc = subprocess.run(gitexec.argv("-C", str(repo), *args), env=gitexec.env(), stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, errors="replace", timeout=timeout)
    if proc.returncode != 0:
        raise Refused(f"git {' '.join(args[:3])} in {repo}: {proc.stderr.strip()[:300]}")
    return proc.stdout


def read_token(path):
    """The subscription token from the operator's file: a regular file (never a link) only its
    owner can read. Every refusal names the file, never a byte of it."""
    path = Path(path).expanduser()
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as err:
        raise Refused(f"the token file {path} cannot be opened ({err.strerror}); write the token from "
                      "`claude setup-token` there, mode 0600") from None
    with os.fdopen(fd, "rb") as fh:
        st = os.fstat(fh.fileno())
        if not stat.S_ISREG(st.st_mode):
            raise Refused(f"the token file {path} is not a regular file")
        if st.st_mode & 0o077:
            raise Refused(f"the token file {path} is readable by others (mode {st.st_mode & 0o777:o}): chmod 600")
        raw = fh.read()
    try:
        token = raw.decode("ascii").strip()
    except UnicodeDecodeError:
        raise Refused(f"the token file {path} is not one ASCII line") from None
    if not token or any(c.isspace() for c in token):
        raise Refused(f"the token file {path} must hold the token alone, on one line")
    return token


def pinned_commit(repo):
    """The checkout's HEAD, or Refused when its tree is dirty: what runs is what was committed."""
    dirty = git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
    if dirty:
        shown = ", ".join(line[3:] for line in dirty[:5]) + (" …" if len(dirty) > 5 else "")
        raise Refused(f"the checkout {repo} is dirty ({shown}): commit or remove it, so the container runs a commit")
    return git(repo, "rev-parse", "--verify", "HEAD^{commit}").strip()


def export_checkout(repo, commit, dest):
    """A self-contained, shallow clone of `commit` at `dest`: git works inside the container (a
    worktree's .git names a host path), and no host .git, untracked or ignored file is mounted."""
    git(dest.parent, "init", "-q", str(dest))
    git(dest, "fetch", "-q", "--depth=1", "--no-tags", f"file://{Path(repo).resolve()}", commit)
    git(dest, "-c", "advice.detachedHead=false", "checkout", "-q", "--detach", "FETCH_HEAD")
    head = git(dest, "rev-parse", "HEAD").strip()
    if head != commit:
        raise Refused(f"the export is at {head}, not the pinned {commit}")


def image_facts(image):
    """The image's id, digests and labels; Refused when it is not built."""
    proc = docker("image", "inspect", "--format", "{{json .}}", image)
    if proc.returncode != 0:
        raise Refused(f"no image {image}: build it first (live_container.py build): {proc.stderr.strip()[:200]}")
    doc = json.loads(proc.stdout)
    labels = (doc.get("Config") or {}).get("Labels") or {}
    committed = sha256_file(DOCKERFILE) if DOCKERFILE.is_file() else None
    return {"ref": image, "id": doc.get("Id"), "repo_digests": doc.get("RepoDigests") or [], "labels": labels,
            "dockerfile_sha256": labels.get(DOCKERFILE_LABEL), "committed_dockerfile_sha256": committed,
            "from_committed_dockerfile": bool(committed) and labels.get(DOCKERFILE_LABEL) == committed}


def leftovers():
    """Every harness container that still exists: one arm at a time, and a leftover is looked at."""
    proc = docker("ps", "-a", "--filter", f"label={LABEL}", "--format", "{{.ID}}")
    if proc.returncode != 0:
        raise Refused(f"docker ps failed: {proc.stderr.strip()[:200]}")
    return proc.stdout.split()


def create_argv(image_id, nonce, arm, cmd, export, results, attestation, token_file, limits):
    """`docker create` for one arm. The token is a read-only file mount, never an environment
    variable: the container's environment is the image's and PATH alone. No privileged flag, no
    host namespace, no capability, no device."""
    mem = str(limits["memory"])
    return ["create", "--rm", "--init", "--user", USER,
            "--hostname", containment.HARNESS_HOSTNAME + nonce,
            "--label", f"{LABEL}={nonce}", "--label", f"org.open-fleet.arm={arm}",
            "--pids-limit", str(limits["pids"]), "--memory", mem, "--memory-swap", mem, "--cpus", str(limits["cpus"]),
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--log-driver", "none",
            "--env", f"PATH={CONTAINER_PATH}",
            "--mount", f"type=bind,src={export},dst={REPO_IN},readonly",
            "--mount", f"type=bind,src={results},dst={RESULTS_IN}",
            "--mount", f"type=bind,src={attestation},dst={containment.ATTESTATION},readonly",
            "--mount", f"type=bind,src={token_file},dst={SECRET},readonly",
            "--workdir", RESULTS_IN, image_id, *cmd]


def destroy(cid):
    """Kill and remove the container, then verify it no longer exists (`docker ps -a --filter`)."""
    docker("kill", cid, timeout=60)
    docker("rm", "-f", cid, timeout=60)
    check = ["ps", "-a", "--filter", f"id={cid}", "--format", "{{.ID}}"]
    deadline = time.monotonic() + DESTROY_WAIT_S
    while True:
        proc = docker(*check, timeout=60)
        if proc.returncode == 0 and not proc.stdout.strip():
            return {"verified": True, "check": ["docker", *check], "output": ""}
        if time.monotonic() > deadline:
            return {"verified": False, "check": ["docker", *check],
                    "output": (proc.stdout + proc.stderr).strip()[:300]}
        docker("rm", "-f", cid, timeout=60)  # --rm removes it asynchronously; ask again
        time.sleep(0.5)


def write_new(path, data, mode=0o600):
    """A new file, never through a link or over an existing one."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())


def inside(path, other):
    return path == other or other in path.parents


def run(args):
    """Run one arm in a fresh container, destroy it, and write the receipt. Returns the exit code."""
    if args.arm not in ARMS:
        raise Refused(f"unknown arm {args.arm!r}: one of {', '.join(ARMS)}")
    if args.timeout <= 0:
        raise Refused("--timeout must be a positive number of seconds")
    results = Path(args.results).expanduser().resolve()
    receipts = Path(args.receipts).expanduser().resolve()
    token_file = Path(args.token_file).expanduser().absolute()
    repo = Path(REPO).resolve()
    for what, path in (("--results", results), ("--receipts", receipts)):
        if inside(path, repo) or inside(repo, path):
            raise Refused(f"{what} {path} overlaps the checkout {repo}")
    for what, path in (("--results", results), ("--receipts", receipts), ("--token-file", token_file)):
        if "," in str(path):
            raise Refused(f"{what} {path} holds a comma, which a docker --mount cannot carry")
    if inside(receipts, results) or inside(results, receipts):
        raise Refused(f"--receipts {receipts} overlaps --results {results}: the container writes to the "
                      "results, and the receipt must be out of its reach")
    token = read_token(token_file)  # its value only to check the file and to redact the output
    commit = pinned_commit(repo)
    image = image_facts(args.image)
    if leftovers():
        raise Refused(f"a harness container already exists (docker ps -a --filter label={LABEL}): one arm runs "
                      "at a time; inspect it, then `docker rm -f` it")
    nonce = secrets.token_hex(16)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = receipts / f"{stamp}-{args.arm}-{nonce[:8]}"
    log_path = base.with_suffix(".log")
    staging = Path(tempfile.mkdtemp(prefix="of-live-"))
    limits = {"pids": args.pids_limit, "memory": args.memory, "cpus": args.cpus}
    script, *prefix = ARMS[args.arm]
    cmd = ["timeout", "--kill-after=30", str(int(args.timeout) + BACKSTOP_S),
           "python3", f"{REPO_IN}/{script}", *prefix, *args.arm_args]
    receipt = {"schema": RECEIPT_SCHEMA, "arm": args.arm, "arm_args": args.arm_args, "argv": cmd,
               "commit": commit, "repo": str(repo), "image": image, "nonce": nonce,
               "hostname": containment.HARNESS_HOSTNAME + nonce,
               "token": {"env": TOKEN_ENV, "file": str(token_file), "mounted_at": SECRET,
                         "passed": f"a read-only file mount; {WRAPPER_DIR}/claude sets {TOKEN_ENV} in the "
                                   "pinned claude's own process alone"},
               "container": {"id": None, "user": USER, "limits": limits, "network": "default bridge",
                             "mounts": {REPO_IN: "the export of the commit, read-only", RESULTS_IN: str(results),
                                        containment.ATTESTATION: "the attestation, read-only",
                                        SECRET: "the token file, read-only"}, "path": CONTAINER_PATH},
               "wall_clock_limit_s": args.timeout, "started_at": None, "ended_at": None, "elapsed_s": None,
               "timed_out": False, "interrupted": None, "exit_status": None,
               "destroyed": {"verified": False, "check": None, "output": "no container was created"},
               "log": str(log_path), "token_redactions": 0}
    cid = None
    try:
        export = staging / "repo"
        export_checkout(repo, commit, export)
        for need in (script, f"{WRAPPER_DIR}/claude"):
            if not (export / need).is_file():
                raise Refused(f"{need} is not in commit {commit[:12]}")
        attestation = staging / "attestation.json"
        doc = {"schema": containment.ATTESTATION_SCHEMA, "nonce": nonce, "commit": commit, "arm": args.arm,
               "image": image["id"], "created_at": now()}
        write_new(attestation, (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode(), mode=0o644)
        results.mkdir(parents=True, exist_ok=True)
        receipts.mkdir(parents=True, exist_ok=True, mode=0o700)
        proc = docker(*create_argv(image["id"], nonce, args.arm, cmd, export, results, attestation, token_file,
                                   limits))
        if proc.returncode != 0:
            raise Refused(f"docker create failed: {proc.stderr.strip()[:300]}")
        cid = proc.stdout.strip().splitlines()[-1]
        receipt["container"]["id"] = cid
        receipt["started_at"], started = now(), time.monotonic()
        exe = shutil.which("docker")
        with open(log_path, "xb") as log:
            attach = subprocess.Popen([exe, "start", "--attach", cid], env=docker_env(), stdin=subprocess.DEVNULL,
                                      stdout=log, stderr=subprocess.STDOUT)
            try:
                receipt["exit_status"] = attach.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                receipt["timed_out"] = True
            finally:
                receipt["ended_at"], receipt["elapsed_s"] = now(), round(time.monotonic() - started, 1)
                if attach.poll() is None:
                    receipt["destroyed"] = destroy(cid)
                    attach.kill()
                    attach.wait()
        if not receipt["destroyed"]["verified"]:
            receipt["destroyed"] = destroy(cid)
    except (KeyboardInterrupt, SystemExit) as err:
        receipt["interrupted"] = getattr(err, "code", None) or 128 + signal.SIGINT
        raise
    finally:
        if cid and not receipt["destroyed"]["verified"]:
            receipt["destroyed"] = destroy(cid)
        shutil.rmtree(staging, ignore_errors=True)
        if cid:
            receipt["token_redactions"] = redact(log_path, token)
            text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
            if token in text:  # never: nothing above holds it
                raise RuntimeError("the receipt would carry the token")
            write_new(base.with_suffix(".json"), text.encode())
            print(f"live_container: receipt {base.with_suffix('.json')}", file=sys.stderr)
    if not receipt["destroyed"]["verified"]:
        print(f"live_container: FAIL-CLOSED: container {cid} could not be verified destroyed: "
              f"{receipt['destroyed']['output']}", file=sys.stderr)
        return EXIT_NOT_DESTROYED
    if receipt["timed_out"]:
        return EXIT_TIMED_OUT
    code = receipt["exit_status"]
    return code if code >= 0 else 128 - code  # the attach client died of signal -code


def redact(path, token):
    """Replace every occurrence of the token in the container's output; how many there were."""
    try:
        data = Path(path).read_bytes()
    except OSError:
        return 0
    count = data.count(token.encode())
    if count:
        Path(path).write_bytes(data.replace(token.encode(), b"[REDACTED]"))
    return count


def build(args):
    """docker build of the committed Dockerfile, from an empty context, labelled with its digest."""
    dockerfile = Path(args.dockerfile).resolve()
    if not dockerfile.is_file():
        raise Refused(f"no Dockerfile at {dockerfile}")
    with tempfile.TemporaryDirectory(prefix="of-live-build-") as ctx:
        context = Path(args.context).resolve() if args.context else Path(ctx)
        argv = ["build", "-f", str(dockerfile), "-t", args.image,
                "--label", f"{DOCKERFILE_LABEL}={sha256_file(dockerfile)}", str(context)]
        exe = shutil.which("docker")
        if not exe:
            raise Refused("no `docker` on PATH (OrbStack or Docker Engine)")
        return subprocess.run([exe, *argv], stdin=subprocess.DEVNULL).returncode


def parser():
    p = argparse.ArgumentParser(prog="live_container.py", description=__doc__.split("\n", 1)[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog="exit: the arm's status · 2 refused · 3 not verified destroyed · 124 timed out")
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="build the harness image (downloads the base and Claude Code)")
    b.add_argument("--image", default=IMAGE)
    b.add_argument("--dockerfile", default=str(DOCKERFILE), help=argparse.SUPPRESS)
    b.add_argument("--context", default=None, help=argparse.SUPPRESS)
    r = sub.add_parser("run", help="run one arm in a fresh container, then destroy it")
    r.add_argument("--arm", required=True, choices=sorted(ARMS))
    r.add_argument("--results", required=True, help="the host results directory, /results inside")
    r.add_argument("--timeout", type=float, required=True, help="wall-clock limit, seconds")
    r.add_argument("--token-file", default=TOKEN_FILE, dest="token_file",
                   help=f"the subscription token, mode 0600 (default {TOKEN_FILE})")
    r.add_argument("--receipts", default=RECEIPTS, help=f"where the receipt goes (default {RECEIPTS})")
    r.add_argument("--image", default=IMAGE)
    r.add_argument("--pids-limit", type=int, default=LIMITS["pids"], dest="pids_limit")
    r.add_argument("--memory", default=LIMITS["memory"])
    r.add_argument("--cpus", default=LIMITS["cpus"])
    r.add_argument("arm_args", nargs=argparse.REMAINDER, help="-- then the arm's own arguments")
    return p


def _signalled(signum, _frame):
    raise SystemExit(128 + signum)


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == "run":
        args.arm_args = args.arm_args[1:] if args.arm_args[:1] == ["--"] else args.arm_args
    previous = {s: signal.signal(s, _signalled) for s in (signal.SIGTERM, signal.SIGHUP)}
    try:
        return build(args) if args.command == "build" else run(args)
    except Refused as err:
        print(f"live_container: refused: {err}", file=sys.stderr)
        return EXIT_USAGE
    except KeyboardInterrupt:  # the container is already destroyed and the receipt written
        return 128 + signal.SIGINT
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)


if __name__ == "__main__":
    sys.exit(main())
