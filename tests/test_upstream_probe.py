#!/usr/bin/env python3
"""upstream_probe.py — the drift probe against the Orca pin.

Upstream cuts about a release a day and the catalog re-pins quarterly (runtime/orca-pin.md);
this probe is the cheap signal in between. Four contracts are pinned here: which tags count
(stable `vX.Y.Z` only), how drift and the patch threshold decide the exit, that every
could-not-run path is exit 2 and never 0, and that `capture`/`diff` speak the receipt shape
the last re-pin archived (docs/runs/2026-09-28-pin-it-500/). Exit codes are asserted on the
script run as a subprocess; pure helpers are imported by path. The tag API is stood in for by
a local stdlib HTTP server, so pagination, the bearer header and the HTTP-error paths are
exercised for real rather than mocked away.
"""
import http.server
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "scripts" / "upstream_probe.py"
RECEIPTS = ROOT / "docs" / "runs" / "2026-09-28-pin-it-500"
WORKFLOW = ROOT / ".github" / "workflows" / "upstream-drift.yml"
DOC = ROOT / "docs" / "runtime-scripts.md"
PIN = "v1.4.215"
PROBE_ENV = ("GITHUB_TOKEN", "ORCA_CLI_COMMAND", "ORCA_DEV_REPO_ROOT")


def load_probe():
    spec = importlib.util.spec_from_file_location("upstream_probe", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args, env=None, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                          text=True, env=env, cwd=cwd, timeout=120)


def clean_env(**extra):
    """The ambient environment minus every variable the probe reads, plus `extra`."""
    env = {k: v for k, v in os.environ.items() if k not in PROBE_ENV}
    env.update(extra)
    return env


def write_pins(directory, version=PIN):
    path = Path(directory) / "pins.json"
    path.write_text(json.dumps({"orca": {"version": version}}), encoding="utf-8")
    return str(path)


def write_tags(directory, names, name="tags.json"):
    path = Path(directory) / name
    path.write_text(json.dumps([{"name": n, "commit": {"sha": "0" * 40}} for n in names]),
                    encoding="utf-8")
    return str(path)


def patch_tags(count, start=216):
    """`count` stable patch tags above the v1.4.215 pin."""
    return [f"v1.4.{start + i}" for i in range(count)]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


# --- latest: which tags count ---------------------------------------------------------------

class StableTagFiltering(unittest.TestCase):
    """Only `vX.Y.Z` counts. Upstream also tags `-rc` candidates and `mobile-*` builds, and
    neither is a release the pin could move to."""

    def latest(self, names, version=PIN, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            r = run("latest", "--pins", write_pins(tmp, version), "--tags-json",
                    write_tags(tmp, names), "--json", *extra, env=clean_env())
        payload = json.loads(r.stdout) if r.returncode in (0, 3) else None
        return r, payload

    def test_rc_mobile_and_unversioned_tags_are_skipped(self):
        r, out = self.latest(["v1.4.216-rc.1", "mobile-1.9.0", "v2.0.0-beta", "1.4.300",
                              "v1.4", "v1.4.216", "v1.4.215", "v1.4.210"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out, {"pin": PIN, "latest": "v1.4.216", "drift": "patch",
                               "patches_behind": 1})

    def test_no_stable_tag_at_all_is_could_not_run(self):
        r, _ = self.latest(["v1.4.216-rc.1", "mobile-1.9.0"])
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("no stable", r.stderr)
        self.assertEqual(r.stdout, "")

    def test_versions_compare_numerically_not_lexically(self):
        r, out = self.latest(["v1.9.9", "v1.10.0"], "v1.9.9")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertEqual(out["latest"], "v1.10.0")
        self.assertEqual(out["drift"], "minor")

    def test_tags_at_or_below_the_pin_do_not_count(self):
        r, out = self.latest(["v1.4.100", "v1.3.999", "v1.4.215"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out, {"pin": PIN, "latest": PIN, "drift": "none", "patches_behind": 0})

    def test_a_pin_ahead_of_every_tag_is_no_drift(self):
        # pins.json may name a build ahead of the newest tag (a pre-release line, see the
        # 2026-09-13 run); that must not read as drift.
        r, out = self.latest(["v1.4.214", "v1.4.215"], "v1.4.216")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out["drift"], "none")
        self.assertEqual(out["patches_behind"], 0)

    def test_bare_string_tags_are_tolerated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tags.json"
            path.write_text(json.dumps(["v1.4.216", "v1.4.217", 7, None]), encoding="utf-8")
            r = run("latest", "--pins", write_pins(tmp), "--tags-json", str(path), "--json",
                    env=clean_env())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["patches_behind"], 2)


class DriftClassification(unittest.TestCase):
    """`none`/`patch` ride; `minor`/`major` are a re-pin trigger on their own (orca-pin.md)."""

    CASES = {
        "none": (["v1.4.215"], 0),
        "patch": (["v1.4.216"], 0),
        "minor": (["v1.5.0"], 3),
        "major": (["v2.0.0"], 3),
    }

    def latest(self, names, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            return run("latest", "--pins", write_pins(tmp), "--tags-json",
                       write_tags(tmp, names), *extra, env=clean_env())

    def test_each_class_maps_to_its_exit(self):
        for drift, (names, exit_code) in self.CASES.items():
            with self.subTest(drift=drift):
                r = self.latest(names, "--json")
                self.assertEqual(r.returncode, exit_code, r.stderr)
                self.assertEqual(json.loads(r.stdout)["drift"], drift)

    def test_json_is_exactly_the_four_keys(self):
        r = self.latest(["v1.4.216"], "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(list(json.loads(r.stdout)), ["pin", "latest", "drift", "patches_behind"])
        self.assertEqual(r.stdout.count("\n"), 1, "one JSON object, nothing else on stdout")

    def test_the_human_line_names_pin_latest_and_verdict(self):
        r = self.latest(["v1.5.0"])
        self.assertEqual(r.returncode, 3, r.stderr)
        for needle in (PIN, "v1.5.0", "minor", "RE-PIN DUE"):
            self.assertIn(needle, r.stdout)
        r = self.latest(["v1.4.216"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("no re-pin due", r.stdout)

    def test_the_committed_pin_is_read_by_default_from_any_cwd(self):
        pinned = json.loads((ROOT / "runtime" / "pins.json").read_text(encoding="utf-8"))
        version = pinned["orca"]["version"]
        with tempfile.TemporaryDirectory() as tmp:
            r = run("latest", "--tags-json", write_tags(tmp, [version]), "--json",
                    env=clean_env(), cwd=tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout),
                         {"pin": version, "latest": version, "drift": "none", "patches_behind": 0})


class PatchThreshold(unittest.TestCase):
    """Patch bumps ride — until enough pile up. The boundary is inclusive at N: N-1 newer
    stable tags is exit 0, N is exit 3."""

    def exit_for(self, count, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            r = run("latest", "--pins", write_pins(tmp), "--tags-json",
                    write_tags(tmp, patch_tags(count)), "--json", *extra, env=clean_env())
        self.assertIn(r.returncode, (0, 3), r.stderr)
        self.assertEqual(json.loads(r.stdout)["patches_behind"], count)
        return r.returncode

    def test_default_threshold_is_ten(self):
        self.assertEqual(self.exit_for(9), 0)
        self.assertEqual(self.exit_for(10), 3)

    def test_explicit_threshold_boundary(self):
        self.assertEqual(self.exit_for(2, "--max-patches", "3"), 0)
        self.assertEqual(self.exit_for(3, "--max-patches", "3"), 3)

    def test_older_tags_in_the_payload_do_not_inflate_the_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            names = patch_tags(9) + ["v1.4.200", "v1.4.215", "v1.3.0", "v1.4.216-rc.2"]
            r = run("latest", "--pins", write_pins(tmp), "--tags-json", write_tags(tmp, names),
                    "--json", env=clean_env())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["patches_behind"], 9)

    def test_a_threshold_below_one_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run("latest", "--pins", write_pins(tmp), "--tags-json",
                    write_tags(tmp, [PIN]), "--max-patches", "0", env=clean_env())
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("--max-patches", r.stderr)


class CouldNotRunIsNeverExitZero(unittest.TestCase):
    """A probe that could not look must not read as "nothing moved"."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = self.tmp.name

    def assert_exit_2(self, *args, mentions=None):
        r = run("latest", *args, "--json", env=clean_env())
        self.assertEqual(r.returncode, 2, f"stdout={r.stdout!r} stderr={r.stderr!r}")
        self.assertEqual(r.stdout, "", "nothing on stdout that a caller could mistake for a verdict")
        if mentions:
            self.assertIn(mentions, r.stderr)

    def test_missing_pins_file(self):
        tags = write_tags(self.dir, [PIN])
        self.assert_exit_2("--pins", str(Path(self.dir) / "absent.json"), "--tags-json", tags,
                           mentions="absent.json")

    def test_pins_without_a_version(self):
        pins = Path(self.dir) / "pins.json"
        pins.write_text(json.dumps({"orca": {"commit": "abc"}}), encoding="utf-8")
        self.assert_exit_2("--pins", str(pins), "--tags-json", write_tags(self.dir, [PIN]),
                           mentions="orca.version")

    def test_pins_with_a_prerelease_version(self):
        self.assert_exit_2("--pins", write_pins(self.dir, "v1.4.216-rc.1"), "--tags-json",
                           write_tags(self.dir, [PIN]), mentions="orca.version")

    def test_pins_that_are_not_json(self):
        pins = Path(self.dir) / "pins.json"
        pins.write_text("{not json", encoding="utf-8")
        self.assert_exit_2("--pins", str(pins), "--tags-json", write_tags(self.dir, [PIN]))

    def test_tags_payload_that_is_not_a_list(self):
        tags = Path(self.dir) / "tags.json"
        tags.write_text(json.dumps({"tags": [PIN]}), encoding="utf-8")
        self.assert_exit_2("--pins", write_pins(self.dir), "--tags-json", str(tags),
                           mentions="expected a JSON list")

    def test_missing_tags_file(self):
        self.assert_exit_2("--pins", write_pins(self.dir), "--tags-json",
                           str(Path(self.dir) / "absent.json"), mentions="absent.json")

    def test_a_refused_connection_is_exit_2(self):
        port = free_port()
        env = clean_env(NO_PROXY="127.0.0.1,localhost", no_proxy="127.0.0.1,localhost")
        r = run("latest", "--pins", write_pins(self.dir), "--tags-url",
                f"http://127.0.0.1:{port}/tags", "--timeout", "5", "--json", env=env)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertEqual(r.stdout, "")
        self.assertIn("could not reach", r.stderr)
        self.assertIn(f"127.0.0.1:{port}", r.stderr)


# --- latest: the tags API, stood in for by a local server -----------------------------------

class _TagsHandler(http.server.BaseHTTPRequestHandler):
    """A stand-in for api.github.com: fixed routes, plus `/endless` that always pages on."""

    routes = {}      # request path (with query) -> (status, extra headers, body)
    requests = []    # (path, lower-cased headers) in arrival order

    def log_message(self, *_args):
        pass

    def do_GET(self):
        type(self).requests.append((self.path, {k.lower(): v for k, v in self.headers.items()}))
        host, port = self.server.server_address[:2]
        base = f"http://{host}:{port}"
        if self.path.startswith("/endless"):
            page = int(self.path.split("page=")[1]) if "page=" in self.path else 1
            status, headers = 200, {"Link": f'<{base}/endless?page={page + 1}>; rel="next"'}
            body = json.dumps([{"name": f"v1.4.{215 + page}"}]).encode("utf-8")
        else:
            status, headers, body = type(self).routes.get(self.path, (404, {}, "[]"))
            headers = {k: v.replace("BASE", base) for k, v in headers.items()}
            body = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TagsApiOverHttp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _TagsHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        _TagsHandler.routes = {}
        _TagsHandler.requests = []
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pins = write_pins(self.tmp.name)

    def probe(self, path, **extra):
        env = clean_env(NO_PROXY="127.0.0.1,localhost", no_proxy="127.0.0.1,localhost", **extra)
        return run("latest", "--pins", self.pins, "--tags-url", self.base + path,
                   "--timeout", "10", "--json", env=env)

    def test_follows_rel_next_across_pages(self):
        _TagsHandler.routes = {
            "/tags?per_page=100": (
                200,
                {"Link": '<BASE/tags?page=2>; rel="next", <BASE/tags?per_page=100>; rel="first"'},
                json.dumps([{"name": "v1.4.216"}, {"name": "v1.4.217"}])),
            "/tags?page=2": (200, {}, json.dumps([{"name": "v1.4.218"}, {"name": "v1.4.219-rc.1"}])),
        }
        r = self.probe("/tags?per_page=100")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout),
                         {"pin": PIN, "latest": "v1.4.218", "drift": "patch", "patches_behind": 3})
        self.assertEqual([path for path, _ in _TagsHandler.requests],
                         ["/tags?per_page=100", "/tags?page=2"])

    def test_stops_after_five_pages(self):
        r = self.probe("/endless?page=1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(_TagsHandler.requests), 5, "the page cap is five")
        self.assertEqual(json.loads(r.stdout), {"pin": PIN, "latest": "v1.4.220",
                                                "drift": "patch", "patches_behind": 5})

    def test_sends_bearer_only_when_github_token_is_set(self):
        _TagsHandler.routes = {"/tags": (200, {}, json.dumps([{"name": PIN}]))}
        r = self.probe("/tags", GITHUB_TOKEN="probe-test-token")
        self.assertEqual(r.returncode, 0, r.stderr)
        headers = _TagsHandler.requests[-1][1]
        self.assertEqual(headers.get("authorization"), "Bearer probe-test-token")
        self.assertIn("upstream_probe", headers.get("user-agent", ""))
        _TagsHandler.requests = []
        r = self.probe("/tags")
        self.assertEqual(r.returncode, 0, r.stderr)
        headers = _TagsHandler.requests[-1][1]
        self.assertNotIn("authorization", headers)
        self.assertIn("upstream_probe", headers.get("user-agent", ""))

    def test_http_errors_are_exit_2(self):
        _TagsHandler.routes = {"/forbidden": (403, {}, '{"message": "API rate limit exceeded"}'),
                               "/boom": (500, {}, "oops")}
        for path, code in (("/forbidden", "403"), ("/boom", "500")):
            with self.subTest(path=path):
                r = self.probe(path)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertEqual(r.stdout, "")
                self.assertIn(code, r.stderr)
        r = self.probe("/forbidden")
        self.assertIn("GITHUB_TOKEN", r.stderr, "a 403 points at the rate-limit remedy")

    def test_a_body_that_is_not_json_is_exit_2(self):
        _TagsHandler.routes = {"/html": (200, {}, "<html>maintenance</html>")}
        r = self.probe("/html")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("did not return JSON", r.stderr)

    def test_a_payload_that_is_not_a_list_is_exit_2(self):
        _TagsHandler.routes = {"/object": (200, {}, json.dumps({"message": "moved"}))}
        r = self.probe("/object")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("expected a JSON list", r.stderr)


# --- capture: resolving the CLI ---------------------------------------------------------------

class CliResolution(unittest.TestCase):
    """`capture` resolves the executable the way upstream's skill stubs do — ORCA_CLI_COMMAND,
    then orca-dev under ORCA_DEV_REPO_ROOT, then orca-ide on Linux, else orca — and never
    guesses past a command that is not on PATH."""

    def setUp(self):
        self.probe = load_probe()

    def resolve(self, env, platform="linux", on_path=()):
        return self.probe.resolve_cli(
            env, platform, which=lambda name: f"/bin/{name}" if name in on_path else None)

    def test_orca_cli_command_wins_when_on_path(self):
        env = {"ORCA_CLI_COMMAND": "my-orca", "ORCA_DEV_REPO_ROOT": "/src/orca"}
        self.assertEqual(self.resolve(env, on_path=("my-orca", "orca-dev", "orca-ide")),
                         ("my-orca", "ORCA_CLI_COMMAND"))

    def test_orca_cli_command_not_on_path_refuses_rather_than_falling_back(self):
        with self.assertRaises(self.probe.ProbeError) as ctx:
            self.resolve({"ORCA_CLI_COMMAND": "ghost-orca"}, on_path=("orca-ide", "orca"))
        self.assertIn("ghost-orca", str(ctx.exception))

    def test_a_blank_override_is_ignored(self):
        self.assertEqual(self.resolve({"ORCA_CLI_COMMAND": "  "}, on_path=("orca-ide",))[0],
                         "orca-ide")

    def test_orca_dev_when_the_dev_root_is_set_and_it_is_on_path(self):
        self.assertEqual(self.resolve({"ORCA_DEV_REPO_ROOT": "/src/orca"},
                                      on_path=("orca-dev", "orca-ide"))[0], "orca-dev")

    def test_a_dev_root_without_orca_dev_falls_through_to_the_platform_default(self):
        self.assertEqual(self.resolve({"ORCA_DEV_REPO_ROOT": "/src/orca"},
                                      on_path=("orca-ide",))[0], "orca-ide")

    def test_linux_is_orca_ide_and_elsewhere_is_orca(self):
        self.assertEqual(self.resolve({}, "linux", ("orca-ide", "orca"))[0], "orca-ide")
        self.assertEqual(self.resolve({}, "darwin", ("orca-ide", "orca"))[0], "orca")
        self.assertEqual(self.resolve({}, "win32", ("orca",))[0], "orca")

    def test_nothing_on_path_names_the_command_and_the_override(self):
        with self.assertRaises(self.probe.ProbeError) as ctx:
            self.resolve({}, "linux", ())
        self.assertIn("orca-ide", str(ctx.exception))
        self.assertIn("ORCA_CLI_COMMAND", str(ctx.exception))


# --- capture and diff: a shim binary and the receipt shape ------------------------------------

SHIM = r'''#!@@PYTHON@@
import json, os, sys
SURFACE = json.loads(@@SURFACE@@)
args = sys.argv[1:]
fail_on = os.environ.get("SHIM_FAIL_ON")
if fail_on and fail_on in " ".join(args):
    sys.stderr.write("shim: simulated failure for " + fail_on + "\n")
    sys.exit(1)
if args == ["agent-context", "--json"]:
    if os.environ.get("SHIM_GARBAGE_JSON"):
        sys.stdout.write("<not json>\n")
    else:
        sys.stdout.write(json.dumps(SURFACE["agent_context"], indent=2) + "\n")
elif args == ["--help"]:
    sys.stdout.write(SURFACE["help_root"])
elif args == ["terminal", "--help"]:
    sys.stdout.write(SURFACE["terminal_help"])
elif len(args) >= 3 and args[:2] == ["skills", "get"] and args[2] in SURFACE["guides"]:
    topic, rest = SURFACE["guides"][args[2]], args[3:]
    if rest == []:
        sys.stdout.write(topic["kernel"])
    elif rest == ["--references"]:
        sys.stdout.write("".join(name + "\n" for name in topic["refs"]))
    elif len(rest) == 2 and rest[0] == "--reference" and rest[1] in topic["references"]:
        sys.stdout.write(topic["references"][rest[1]])
    else:
        sys.stderr.write("shim: bad skills get arguments\n")
        sys.exit(1)
else:
    sys.stderr.write("shim: unknown command " + " ".join(args) + "\n")
    sys.exit(1)
'''


def surface(commands=("agent-context", "skills get", "terminal list"),
            linear="Read Linear ticket context", loop_note="v1",
            refs=("coordinator-loop", "worker-contract")):
    """A whole CLI surface, in the shapes the pinned receipts hold."""
    return {
        "agent_context": {
            "schemaVersion": 1,
            "commandCount": len(commands),
            "commands": [{"command": c, "path": c.split(" "), "summary": f"{c} summary",
                          "flags": ["help", "json"]} for c in commands],
        },
        "help_root": ("orca\n\nUsage: orca <command> [options]\n\nLinear:\n"
                      f"  linear                    {linear}\n"),
        "terminal_help": "orca terminal\n\nCommands:\n  list               List live terminals\n",
        "guides": {
            "orchestration": {
                "kernel": "---\nname: orchestration\n---\n# Orca orchestration\n",
                "refs": list(refs),
                "references": {name: f"# {name}\n{loop_note}\n" for name in refs},
            },
            "orca-cli": {
                "kernel": "---\nname: orca-cli\n---\n# Orca CLI\n",
                "refs": ["browser"],
                "references": {"browser": "# Built-in browser commands\n"},
            },
        },
    }


def make_shim(bin_dir, surface_dict, name="orca-shim"):
    path = Path(bin_dir) / name
    text = SHIM.replace("@@PYTHON@@", sys.executable)
    text = text.replace("@@SURFACE@@", repr(json.dumps(surface_dict)))
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


def write_surface(directory, surface_dict, version=None):
    """`surface_dict` on disk — in `capture`'s naming, or with `version` in the pinned
    receipts' naming (agent-context-<v>.json, ..., guides-<v>/, plus a probe receipt that
    the diff must ignore)."""
    suffix = f"-{version}" if version else ""
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"agent-context{suffix}.json").write_text(
        json.dumps(surface_dict["agent_context"], indent=2) + "\n", encoding="utf-8")
    (d / f"help-root{suffix}.txt").write_text(surface_dict["help_root"], encoding="utf-8")
    (d / f"terminal-help{suffix}.txt").write_text(surface_dict["terminal_help"], encoding="utf-8")
    guides = d / f"guides{suffix}"
    guides.mkdir()
    for topic, entry in surface_dict["guides"].items():
        (guides / f"{topic}.md").write_text(entry["kernel"], encoding="utf-8")
        (guides / f"{topic}.refs.txt").write_text("".join(n + "\n" for n in entry["refs"]),
                                                  encoding="utf-8")
        for name, body in entry["references"].items():
            (guides / f"{topic}--{name}.md").write_text(body, encoding="utf-8")
    if version:
        (d / f"probe-status-{version}.json").write_text('{"ok": false}\n', encoding="utf-8")
    return d


class CaptureAgainstAShim(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.out = self.root / "fresh"

    def env(self, command="orca-shim", **extra):
        return clean_env(PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
                         ORCA_CLI_COMMAND=command, **extra)

    def test_capture_writes_every_receipt_surface(self):
        make_shim(self.bin, surface())
        r = run("capture", "--out", str(self.out), env=self.env())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("cli: orca-shim (ORCA_CLI_COMMAND)", r.stdout)
        expected = {
            "agent-context.json", "help-root.txt", "terminal-help.txt",
            "guides/orchestration.md", "guides/orchestration.refs.txt",
            "guides/orchestration--coordinator-loop.md",
            "guides/orchestration--worker-contract.md",
            "guides/orca-cli.md", "guides/orca-cli.refs.txt", "guides/orca-cli--browser.md",
        }
        found = {p.relative_to(self.out).as_posix() for p in self.out.rglob("*") if p.is_file()}
        self.assertEqual(found, expected)
        context = json.loads((self.out / "agent-context.json").read_text(encoding="utf-8"))
        self.assertEqual(context["commandCount"], 3)
        self.assertEqual((self.out / "guides" / "orca-cli--browser.md").read_text(encoding="utf-8"),
                         "# Built-in browser commands\n")
        self.assertEqual((self.out / "guides" / "orchestration.refs.txt").read_text(encoding="utf-8"),
                         "coordinator-loop\nworker-contract\n")
        for rel in sorted(expected):
            self.assertIn(f"wrote {rel} (", r.stdout)

    def test_reference_names_as_the_guide_spells_them_are_normalized(self):
        probe = load_probe()
        self.assertEqual(probe.reference_names("references/recovery-and-cleanup.md\n"
                                               "- worker-contract\n\nplacement.md\n"
                                               "Available references:\nworker-contract\n"),
                         ["recovery-and-cleanup", "worker-contract", "placement"])

    def test_a_cli_that_is_not_on_path_is_exit_2(self):
        r = run("capture", "--out", str(self.out), env=self.env("no-such-orca"))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("no-such-orca", r.stderr)
        self.assertFalse((self.out / "agent-context.json").exists())

    def test_a_failing_command_fails_the_capture(self):
        make_shim(self.bin, surface())
        r = run("capture", "--out", str(self.out), env=self.env(SHIM_FAIL_ON="terminal --help"))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("terminal --help", r.stderr)
        self.assertIn("simulated failure", r.stderr, "the command's own stderr is relayed")
        self.assertNotIn("wrote terminal-help.txt", r.stdout)

    def test_a_failing_reference_fetch_fails_the_capture(self):
        make_shim(self.bin, surface())
        r = run("capture", "--out", str(self.out),
                env=self.env(SHIM_FAIL_ON="--reference worker-contract"))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("worker-contract", r.stderr)

    def test_agent_context_that_is_not_json_fails_the_capture(self):
        make_shim(self.bin, surface())
        r = run("capture", "--out", str(self.out), env=self.env(SHIM_GARBAGE_JSON="1"))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("did not print JSON", r.stderr)

    def test_an_out_path_that_is_a_file_is_exit_2(self):
        make_shim(self.bin, surface())
        self.out.write_text("", encoding="utf-8")
        r = run("capture", "--out", str(self.out), env=self.env())
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("not a directory", r.stderr)

    def test_commands_are_argv_lists_never_a_shell(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("shell=True", "os.system(", "os.popen("):
            self.assertNotIn(forbidden, text)

    def test_without_the_override_the_platform_default_runs(self):
        # The default is whatever runtime/scripts/orca_cli.py says for this host (orca-ide on
        # Linux, orca elsewhere), so the test runs on every platform instead of skipping.
        spec = importlib.util.spec_from_file_location(
            "orca_cli_for_probe_test", ROOT / "runtime" / "scripts" / "orca_cli.py")
        orca_cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orca_cli)
        default = orca_cli.resolve(env={})
        self.assertEqual(default, "orca-ide" if sys.platform.startswith("linux") else "orca")
        make_shim(self.bin, surface(), name=default)
        env = clean_env(PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}")
        r = run("capture", "--out", str(self.out), env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"cli: {default} (platform default)", r.stdout)


class CaptureThenDiff(unittest.TestCase):
    """The round trip that makes the receipts diff-able: a capture of an unchanged binary
    reads identical against the pinned naming, and a moved binary is named move by move."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()

    def capture(self, surface_dict):
        make_shim(self.bin, surface_dict)
        out = self.root / "fresh"
        env = clean_env(PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
                        ORCA_CLI_COMMAND="orca-shim")
        r = run("capture", "--out", str(out), env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out

    def test_an_unchanged_binary_is_identical_against_the_receipt_naming(self):
        base = write_surface(self.root / "receipts", surface(), version="9.9.9")
        out = self.capture(surface())
        r = run("diff", "--baseline", str(base), "--fresh", str(out), env=clean_env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("VERDICT: identical", r.stdout)
        for name in ("agent-context-9.9.9.json", "help-root-9.9.9.txt",
                     "terminal-help-9.9.9.txt", "guides-9.9.9/"):
            self.assertIn(name, r.stdout, "the summary names the receipt it compared against")

    def test_a_moved_binary_is_drift_and_every_move_is_named(self):
        base = write_surface(self.root / "receipts", surface(), version="9.9.9")
        moved = surface(commands=("agent-context", "skills get", "host name"),
                        linear="Read and write Linear issues", loop_note="v2 --model for muse",
                        refs=("coordinator-loop", "worker-contract", "placement"))
        moved["agent_context"]["commands"][1]["flags"].append("full")
        out = self.capture(moved)
        r = run("diff", "--baseline", str(base), "--fresh", str(out), env=clean_env())
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        for needle in (
            "added: host name", "removed: terminal list", "changed: skills get",
            "help-root.txt: CHANGED (+1/-1 lines)",
            "-  linear                    Read Linear ticket context",
            "+  linear                    Read and write Linear issues",
            "terminal-help.txt: identical",
            "orchestration--coordinator-loop.md", "orchestration--worker-contract.md",
            "added: orchestration--placement.md", "orchestration.refs.txt",
            "VERDICT: DRIFT",
        ):
            self.assertIn(needle, r.stdout)


class DiffOnFixtureDirectories(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base = write_surface(self.root / "base", surface(), version="1.4.215")

    def diff(self, fresh, *extra):
        return run("diff", "--baseline", str(self.base), "--fresh", str(fresh), *extra,
                   env=clean_env())

    def test_identical_in_capture_naming_and_in_receipt_naming(self):
        r = self.diff(write_surface(self.root / "fresh", surface()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("VERDICT: identical", r.stdout)
        r = self.diff(write_surface(self.root / "fresh2", surface(), version="1.4.215"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_json_report_carries_the_verdict_and_the_lists(self):
        r = self.diff(write_surface(self.root / "fresh", surface()), "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        report = json.loads(r.stdout)
        self.assertFalse(report["drift"])
        self.assertEqual(report["agent_context"]["added"], [])
        self.assertEqual(report["help_root"]["status"], "identical")
        self.assertEqual(report["guides"]["identical"], 7)
        moved = surface(commands=("agent-context", "skills get"), linear="Read and write")
        r = self.diff(write_surface(self.root / "fresh2", moved), "--json")
        self.assertEqual(r.returncode, 3, r.stderr)
        report = json.loads(r.stdout)
        self.assertTrue(report["drift"])
        self.assertEqual(report["agent_context"]["removed"], ["terminal list"])
        self.assertEqual(report["help_root"]["status"], "changed")
        self.assertEqual((report["help_root"]["added_lines"], report["help_root"]["removed_lines"]),
                         (1, 1))

    def test_a_changed_command_entry_with_the_same_name_is_drift(self):
        moved = surface()
        moved["agent_context"]["commands"][0]["summary"] = "reworded"
        r = self.diff(write_surface(self.root / "fresh", moved))
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("changed: agent-context", r.stdout)

    def test_command_names_derive_from_path_when_command_is_absent(self):
        pathed = surface()
        for entry in pathed["agent_context"]["commands"]:
            del entry["command"]
        shutil.rmtree(self.base)
        self.base = write_surface(self.root / "base", pathed, version="1.4.215")
        r = self.diff(write_surface(self.root / "fresh", pathed))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("3 -> 3 commands", r.stdout)
        missing = surface(commands=("agent-context", "skills get"))
        r = self.diff(write_surface(self.root / "fresh2", missing))
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("removed: terminal list", r.stdout, "names derived from `path` still diff")

    def test_an_added_command_is_named(self):
        moved = surface(commands=("agent-context", "skills get", "terminal list", "host name"))
        r = self.diff(write_surface(self.root / "fresh", moved))
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("added: host name", r.stdout)
        self.assertIn("3 -> 4 commands", r.stdout)

    def test_a_removed_guide_file_is_drift(self):
        fresh = write_surface(self.root / "fresh", surface())
        (fresh / "guides" / "orca-cli--browser.md").unlink()
        r = self.diff(fresh)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("removed: orca-cli--browser.md", r.stdout)

    def test_a_trailing_newline_alone_is_not_drift(self):
        fresh = write_surface(self.root / "fresh", surface())
        path = fresh / "help-root.txt"
        path.write_text(path.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
        r = self.diff(fresh)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_missing_directory_is_exit_2(self):
        r = self.diff(self.root / "absent")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("absent", r.stderr)
        r = run("diff", "--baseline", str(self.root / "absent"), "--fresh", str(self.base),
                env=clean_env())
        self.assertEqual(r.returncode, 2, r.stdout)

    def test_an_incomplete_directory_is_exit_2_naming_the_missing_surface(self):
        fresh = write_surface(self.root / "fresh", surface())
        (fresh / "terminal-help.txt").unlink()
        r = self.diff(fresh)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("terminal-help", r.stderr)
        shutil.rmtree(self.base / "guides-1.4.215")
        r = self.diff(write_surface(self.root / "fresh2", surface()))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("guides", r.stderr)

    def test_several_versions_in_one_receipts_directory_resolve_to_the_highest(self):
        # docs/runs/2026-09-23-pin-it-488/ holds 1.4.204 and 1.4.209 side by side.
        older = surface(linear="older wording", commands=("agent-context",))
        write_surface(self.base, older, version="1.4.204")
        r = self.diff(write_surface(self.root / "fresh", surface()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("agent-context-1.4.215.json", r.stdout)
        self.assertNotIn("1.4.204", r.stdout)


class ThePinnedReceiptsAreDiffable(unittest.TestCase):
    """The mapping is only worth anything if it resolves the real receipts."""

    def test_the_receipts_diff_against_themselves_as_identical(self):
        r = run("diff", "--baseline", str(RECEIPTS), "--fresh", str(RECEIPTS), env=clean_env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in ("agent-context-1.4.215.json", "help-root-1.4.215.txt",
                     "terminal-help-1.4.215.txt", "guides-1.4.215/", "VERDICT: identical"):
            self.assertIn(name, r.stdout)

    def test_a_capture_named_copy_of_the_receipts_is_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "fresh"
            fresh.mkdir()
            shutil.copy(RECEIPTS / "agent-context-1.4.215.json", fresh / "agent-context.json")
            shutil.copy(RECEIPTS / "help-root-1.4.215.txt", fresh / "help-root.txt")
            shutil.copy(RECEIPTS / "terminal-help-1.4.215.txt", fresh / "terminal-help.txt")
            shutil.copytree(RECEIPTS / "guides-1.4.215", fresh / "guides")
            r = run("diff", "--baseline", str(RECEIPTS), "--fresh", str(fresh), env=clean_env())
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            (fresh / "help-root.txt").write_text(
                (fresh / "help-root.txt").read_text(encoding="utf-8").replace(
                    "Read and write Linear issues", "Read Linear ticket context"),
                encoding="utf-8")
            r = run("diff", "--baseline", str(RECEIPTS), "--fresh", str(fresh), env=clean_env())
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("help-root.txt: CHANGED (+1/-1 lines)", r.stdout)

    def test_command_names_derive_from_the_receipt(self):
        probe = load_probe()
        doc = json.loads((RECEIPTS / "agent-context-1.4.215.json").read_text(encoding="utf-8"))
        entries = probe.command_entries(doc, "receipt")
        self.assertEqual(len(entries), doc["commandCount"])
        for name in ("agent-context", "skills get", "terminal read", "orchestration worker-list"):
            self.assertIn(name, entries)


# --- the weekly workflow and the reference doc ------------------------------------------------

def run_blocks(lines):
    """The shell text of every `run:` step — block scalars and one-liners alike."""
    blocks, i = [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].lstrip()
        if stripped.startswith("run:"):
            indent = len(line) - len(line.lstrip())
            rest = stripped[len("run:"):].strip()
            if rest in ("|", "|-", ">", ">-"):
                body = []
                i += 1
                while i < len(lines) and (not lines[i].strip()
                                          or len(lines[i]) - len(lines[i].lstrip()) > indent):
                    body.append(lines[i])
                    i += 1
                blocks.append("\n".join(body))
                continue
            blocks.append(rest)
        i += 1
    return blocks


class TheDriftWorkflowIsShapedSafely(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")
        self.lines = self.text.splitlines()
        self.body = [ln for ln in self.lines if not ln.lstrip().startswith("#")]

    def test_it_runs_weekly_and_by_hand(self):
        self.assertIn("- cron: '17 6 * * 1'", self.text)
        self.assertRegex(self.text, r"(?m)^  workflow_dispatch:\s*$")

    def test_permissions_are_read_contents_and_write_issues_only(self):
        block, active = [], False
        for line in self.body:
            if line.startswith("permissions:"):
                active = True
                continue
            if active:
                if line.startswith(" ") and line.strip():
                    block.append(line.strip())
                elif line.strip():
                    break
        self.assertEqual(set(block), {"contents: read", "issues: write"})

    def test_every_action_is_pinned_to_a_commit(self):
        uses = re.findall(r"uses:\s*(\S+)", self.text)
        self.assertEqual(len(uses), 2, "checkout and setup-python, nothing else to pin")
        for action in uses:
            with self.subTest(action=action):
                self.assertRegex(action, r"@[0-9a-f]{40}$")
        self.assertIn("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", self.text)
        self.assertIn("actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97", self.text)
        self.assertIn('python-version: "3.13"', self.text)

    def test_no_expression_is_interpolated_into_a_shell_command(self):
        blocks = run_blocks(self.lines)
        self.assertGreaterEqual(len(blocks), 4, "the parser found almost no run steps")
        for block in blocks:
            with self.subTest(block=block[:60]):
                self.assertNotIn("${{", block, "use env:, never an expression inside run:")

    def test_the_run_block_parser_can_see_an_interpolation(self):
        planted = ["    steps:", "      - run: |", "          echo ${{ github.ref }}",
                   "      - run: echo ${{ steps.x.outputs.y }}", "      - name: after"]
        self.assertEqual(sum("${{" in b for b in run_blocks(planted)), 2)

    def test_it_runs_the_probe_and_files_the_labeled_issue_without_duplicating(self):
        for needle in (
            "python3 runtime/scripts/upstream_probe.py latest --json",
            "gh label create upstream-drift --force",
            "gh issue list --label upstream-drift --state open",
            "gh issue comment",
            "gh issue create",
            'title="Orca moved past the pin: ${LATEST} vs ${PIN}"',
            "GH_TOKEN: ${{ github.token }}",
            "GITHUB_STEP_SUMMARY",
        ):
            self.assertIn(needle, self.text)

    def test_exit_two_fails_the_job_and_exit_three_files(self):
        self.assertIn("steps.probe.outputs.code != '0' && steps.probe.outputs.code != '3'",
                      self.text)
        self.assertIn("steps.probe.outputs.code == '3'", self.text)
        self.assertIn("steps.probe.outputs.code == '0'", self.text)
        self.assertRegex(self.text, r"(?m)^\s+exit 1\s*$")


class TheReferenceDocDescribesTheProbe(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")
        self.section = self.text.split("## `upstream_probe.py`", 1)[1].split("\n## ", 1)[0]

    def test_the_section_sits_between_its_alphabetical_neighbours(self):
        heads = re.findall(r"(?m)^## `([^`]+)`", self.text)
        i = heads.index("upstream_probe.py")
        self.assertEqual(heads[i - 1], "terminal_ops.py")
        self.assertEqual(heads[i + 1], "watchdog.py")

    def test_the_section_binds_to_source_test_subcommands_mapping_and_exits(self):
        for needle in ("runtime/scripts/upstream_probe.py:", "tests/test_upstream_probe.py",
                       "`latest`", "`capture`", "`diff`", "Usage:", "Subcommands:", "Flags:",
                       "> Why:", "agent-context-", "help-root-", "terminal-help-", "guides-",
                       "ORCA_CLI_COMMAND", "GITHUB_TOKEN", "upstream-drift"):
            self.assertIn(needle, self.section)
        exits = re.search(r"(?m)^Exits: (.+(?:\n(?!\n).+)*)", self.section)
        self.assertIsNotNone(exits, "no Exits: line")
        for code in ("0 ", "2 ", "3 "):
            self.assertIn(code, exits.group(1))

    def test_the_source_anchor_covers_the_header_docstring(self):
        m = re.search(r"runtime/scripts/upstream_probe\.py:1-(\d+)", self.section)
        self.assertIsNotNone(m, "the source anchor is not a 1-N line range")
        lines = SCRIPT.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[int(m.group(1)) - 1].strip(), '"""',
                         "the anchored range must end where the header docstring closes")


class ScriptHygiene(unittest.TestCase):
    def test_executable_and_shebanged(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), "upstream_probe.py must be executable")
        self.assertEqual(SCRIPT.read_text(encoding="utf-8").splitlines()[0], "#!/usr/bin/env python3")

    def test_help_exits_zero_for_every_subcommand(self):
        for args in ((), ("latest",), ("capture",), ("diff",)):
            with self.subTest(args=args):
                r = run(*args, "--help", env=clean_env())
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_no_subcommand_is_a_usage_error(self):
        self.assertEqual(run(env=clean_env()).returncode, 2)

    def test_the_header_states_the_exit_contract_and_the_env(self):
        header = SCRIPT.read_text(encoding="utf-8").split('"""', 2)[1]
        for needle in ("Exit codes", "GITHUB_TOKEN", "ORCA_CLI_COMMAND", "ORCA_DEV_REPO_ROOT",
                       "orca-ide", "never exit 0"):
            self.assertIn(needle, header)


if __name__ == "__main__":
    unittest.main()
