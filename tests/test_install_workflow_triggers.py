#!/usr/bin/env python3
"""
Contract test for the trigger scope of .github/workflows/install.yml.

release_check.py gate 4 (`check_workflow_green_at_head`) needs the latest `install` run on
main to be a success AT the release HEAD — a stale green from another SHA does not count
(tests/test_release_check.py `test_a_workflow_run_is_green_only_at_this_head` holds that
side). So every push to main must be able to start the workflow. A `push.paths` filter
broke that: e7089cbf (merge of a video-only commit, assets/orca-fleet-reel.mp4) touched no
listed path, no run started, and the newest install success stayed pinned at 284a3d81 —
the gate could never go green at HEAD without an unrelated edit.

The expected behaviour comes from GitHub's documented trigger semantics, not from this
file: "If you define both branches/branches-ignore and paths/paths-ignore, the workflow
will only run when both filters are satisfied" (docs.github.com/en/actions/reference/
workflows-and-actions/workflow-syntax). The PR path list is frozen here as it stood at
e7089cbf: PRs keep the cheap path gate; only the main push loses it.

Stdlib only — no yaml on the host (see test_repo_hygiene.py), so the `on:` block is read
with a line parser that covers exactly the shapes this workflow uses.

    python3 -m unittest tests.test_install_workflow_triggers -v
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "install.yml"

# The PR path filter at e7089cbf — the scope this fix must not change.
PR_PATHS = [
    "scripts/install.sh",
    "scripts/validate.py",
    "runtime/scripts/verify-gate.sh",
    "hooks/**",
    "skills/*/SKILL.md",
    "runtime/pins.json",
    "README.md",
    "docs/install.md",
    "docs/distribution.md",
    "docs/getting-started.md",
    ".claude-plugin/**",
    ".github/workflows/install.yml",
]

# Main pushes that touch no install path. The first is the real e7089cbf change set.
UNRELATED_MAIN_PUSHES = [
    ["assets/orca-fleet-reel.mp4"],
    ["docs/runs/README.md"],
    ["assets/badges/tests.json", "docs/runs/2026-09-30-install-gate/REPORT.md"],
]


def parse_triggers(text):
    """The `on:` block as {event: {key: [values]} | {}}.

    Handles: `event:` with nothing under it, `key: [a, b]` flow lists, and `key:` followed
    by `- item` block lists. Anything else under `on:` fails loudly rather than being
    silently misread.
    """
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if re.match(r"^(on|\"on\"|'on'):\s*$", ln))
    except StopIteration:
        raise AssertionError("install.yml has no block-form `on:` key")
    events, event, key = {}, None, None
    for ln in lines[start + 1:]:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if not ln.startswith(" "):
            break  # next top-level key
        indent = len(ln) - len(ln.lstrip())
        body = ln.strip().split(" #", 1)[0].rstrip()
        if indent == 2:
            m = re.fullmatch(r"([A-Za-z_-]+):", body)
            if not m:
                raise AssertionError(f"unparsed event line under on: {ln!r}")
            event, key = m.group(1), None
            events[event] = {}
        elif indent == 4 and event:
            m = re.fullmatch(r"([A-Za-z_-]+):\s*(\[.*\])?", body)
            if not m:
                raise AssertionError(f"unparsed filter line under {event}: {ln!r}")
            key = m.group(1)
            flow = m.group(2)
            events[event][key] = ([v.strip().strip("'\"") for v in flow[1:-1].split(",") if v.strip()]
                                  if flow else [])
        elif indent == 6 and event and key and body.startswith("- "):
            events[event][key].append(body[2:].strip().strip("'\""))
        else:
            raise AssertionError(f"unparsed line under on: {ln!r}")
    return events


def glob_match(pattern, path):
    """GitHub filter glob: `**` spans directories, `*` stays inside one segment."""
    rx = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            rx += ".*"
            i += 2
        elif pattern[i] == "*":
            rx += "[^/]*"
            i += 1
        else:
            rx += re.escape(pattern[i])
            i += 1
    return re.fullmatch(rx, path) is not None


def starts(filters, branch, changed):
    """Would this event start the workflow? Branch AND path filters must both hold;
    an absent filter imposes nothing (docs: both filters must be satisfied)."""
    if "branches" in filters and not any(glob_match(b, branch) for b in filters["branches"]):
        return False
    if "paths-ignore" in filters and all(
            any(glob_match(p, f) for p in filters["paths-ignore"]) for f in changed):
        return False
    if "paths" in filters and not any(glob_match(p, f) for p in filters["paths"] for f in changed):
        return False
    return True


class InstallWorkflowTriggers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        cls.on = parse_triggers(cls.text)

    def test_every_main_push_starts_install_whatever_it_changed(self):
        push = self.on.get("push")
        self.assertIsNotNone(push, "install.yml no longer runs on push")
        for changed in UNRELATED_MAIN_PUSHES:
            with self.subTest(changed=changed):
                self.assertTrue(starts(push, "main", changed),
                                f"a main push touching only {changed} does not start install — "
                                "gate 4 can never be green at that HEAD")

    def test_the_push_trigger_is_main_only_with_no_path_filter(self):
        push = self.on["push"]
        self.assertEqual(push.get("branches"), ["main"])
        self.assertNotIn("paths", push, "a push.paths filter skips main SHAs gate 4 must bind to")
        self.assertNotIn("paths-ignore", push)
        self.assertFalse(starts(push, "feature/x", ["scripts/install.sh"]),
                         "non-main pushes must stay out; PRs cover branches")

    def test_the_pull_request_path_gate_is_unchanged(self):
        pr = self.on.get("pull_request")
        self.assertIsNotNone(pr, "install.yml no longer runs on pull_request")
        self.assertEqual(pr, {"paths": PR_PATHS})
        self.assertTrue(starts(pr, "any", ["scripts/install.sh"]))
        self.assertTrue(starts(pr, "any", ["skills/ship-it/SKILL.md"]))
        self.assertFalse(starts(pr, "any", ["assets/orca-fleet-reel.mp4"]))
        self.assertFalse(starts(pr, "any", ["skills/ship-it/notes/SKILL.md"]))

    def test_a_manual_dispatch_exists_for_retry_and_backfill(self):
        self.assertEqual(self.on.get("workflow_dispatch"), {},
                         "workflow_dispatch lets a skipped or failed main SHA be re-run by hand")

    def test_no_other_trigger_widens_the_workflow(self):
        self.assertEqual(sorted(self.on), ["pull_request", "push", "workflow_dispatch"])

    def test_permissions_and_job_stay_read_only_from_scratch(self):
        self.assertRegex(self.text, r"(?m)^permissions:\n  contents: read\n\n?jobs:\n  from-scratch:\n")
        self.assertIn("sh scripts/install.sh --check", self.text)

    def test_the_parser_reads_the_filter_shapes_it_claims(self):
        sample = ("on:\n  push:\n    branches: [main]\n    paths:\n      - a/**\n"
                  "  workflow_dispatch:\n\njobs:\n")
        self.assertEqual(parse_triggers(sample),
                         {"push": {"branches": ["main"], "paths": ["a/**"]}, "workflow_dispatch": {}})
        self.assertTrue(glob_match("hooks/**", "hooks/a/b.sh"))
        self.assertFalse(glob_match("skills/*/SKILL.md", "skills/a/b/SKILL.md"))


if __name__ == "__main__":
    unittest.main()
