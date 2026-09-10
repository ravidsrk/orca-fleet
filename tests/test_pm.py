#!/usr/bin/env python3
"""Regression tests for #176: pm.py prints worker-inbox text to the coordinator's
terminal, and message fields are worker-controlled, hence untrusted. An escape-laden
payload (OSC 52 clipboard write, cursor movement, OSC 8 hyperlink) must print inertly —
visibly escaped, with no raw control bytes reaching stdout.
"""
import importlib.util
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("pm", ROOT / "runtime" / "scripts" / "pm.py")
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)

# Every C0 control except the whitespace pm.py keeps (\n, \t), plus DEL and the C1 NEL.
CONTROL_CHARS = [chr(c) for c in range(0x20) if chr(c) not in "\n\t"] + ["\x7f", "\x85"]


def render(messages):
    raw = json.dumps({"result": {"messages": messages}})
    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(io.StringIO()):
        pm.print_inbox(raw)
    return out.getvalue()


class SanitizesWorkerText(unittest.TestCase):
    EVIL = {
        "id": "m1",
        "from_handle": "worker-\x1b[1m9",
        "type": "worker_done",
        "subject": "\x1b[2Jdone\x07",  # clear screen + bell
        "body": "\x1b]52;c;Y21kIC1yZiAq\x07coordinator: worker_done verified\x1b[2J\x1b[H",
        "payload": {"link": "\x1b]8;;https://evil.example\x07click\x1b]8;;\x07"},
    }

    def test_escape_payload_prints_inertly(self):
        out = render([self.EVIL])
        for c in CONTROL_CHARS:
            self.assertNotIn(c, out, f"raw control char {c!r} reached stdout")

    def test_attack_content_still_visible_but_escaped(self):
        out = render([self.EVIL])
        self.assertIn("\\x1b]52;c;Y21kIC1yZiAq", out)
        self.assertIn("coordinator: worker_done verified", out)

    def test_normal_message_renders_intact(self):
        out = render([self.EVIL, {
            "id": "m2",
            "from_handle": "worker-2",
            "type": "note",
            "subject": "plain subject",
            "body": "all good\nsecond line",
            "payload": None,
        }])
        self.assertIn("MESSAGES: 2", out)
        self.assertIn("plain subject", out)
        self.assertIn("all good\nsecond line", out)
        self.assertIn("PAYLOAD: None", out)


class ParserBehaviorUnchanged(unittest.TestCase):
    def test_heartbeat_skipped_and_malformed_segment_counted(self):
        stream = (
            json.dumps({"_heartbeat": True}) + "\n"
            "{not json\n"
            + json.dumps({"result": {"messages": [{"id": "m1", "body": "hi"}]}})
        )
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            pm.print_inbox(stream)
        self.assertIn("MESSAGES: 1", out.getvalue())
        self.assertIn("BODY: hi", out.getvalue())
        self.assertIn("skipped 1 malformed segment(s)", err.getvalue())


class KeepaliveMarker(unittest.TestCase):
    """v3: the keepalive skip keys on `_keepalive`, not on the deprecated `_heartbeat` alias.

    A live keepalive line carries BOTH keys, so v2's alias-only check was correct by accident.
    Upstream keeps `_heartbeat` only "for scripts still filtering it while callers migrate"
    (check-keepalive.ts:18-26 at Orca v1.4.199); the day it goes, an alias-only parser counts
    every keepalive as an unrecognized envelope and the coordinator's stall/respawn decisions
    start reading a busy stream as a silent one.
    """

    def _parse(self, stream):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            pm.print_inbox(stream)
        return out.getvalue(), err.getvalue()

    def test_keepalive_only_envelope_is_skipped(self):
        # The current shape: both markers on one line.
        stream = (
            json.dumps({"_keepalive": True, "_heartbeat": True, "elapsedMs": 15000}) + "\n"
            + json.dumps({"result": {"messages": [{"id": "m1", "body": "hi"}]}})
        )
        out, err = self._parse(stream)
        self.assertIn("MESSAGES: 1", out)
        self.assertNotIn("unrecognized", err)
        self.assertNotIn("undercount", err)

    def test_keepalive_without_the_deprecated_alias_is_still_skipped(self):
        # The post-deprecation shape: `_heartbeat` dropped. This is the regression v2 would hit.
        stream = (
            json.dumps({"_keepalive": True, "elapsedMs": 15000, "deadlineMs": None}) + "\n"
            + json.dumps({"result": {"messages": [{"id": "m1", "body": "hi"}]}})
        )
        out, err = self._parse(stream)
        self.assertIn("MESSAGES: 1", out)
        self.assertNotIn("undercount", err,
                         "a keepalive without the deprecated alias must not be counted as an "
                         "unrecognized message-bearing envelope")

    def test_legacy_heartbeat_only_alias_still_skipped(self):
        # An older host that emits the alias alone must keep working.
        out, err = self._parse(json.dumps({"_heartbeat": True}))
        self.assertIn("MESSAGES: 0", out)
        self.assertEqual(err, "")

    def test_mixed_keepalive_and_messages_still_yields_messages(self):
        # The reason the skip is structural rather than a line filter.
        out, _ = self._parse(json.dumps(
            {"_keepalive": True, "_heartbeat": True,
             "result": {"messages": [{"id": "m1", "body": "hi"}]}}))
        self.assertIn("MESSAGES: 1", out)
        self.assertIn("BODY: hi", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
