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


class InvisibleCharactersAreEscapedToo(unittest.TestCase):
    """#299: escaping C0/C1 alone let every character that reorders or HIDES text through.

    Same untrusted surface as the escape sequences above — a worker message carries an issue
    title or a PR body verbatim — but a different mechanism: these print no glyph and change
    what the reader sees anyway. U+202E reverses the rest of the line, U+200B splits a word the
    reader takes as whole, U+2028 is a line break the inbox format never wrote.

    Escaped, never stripped: silently removing them would show the coordinator a clean string
    that is not what arrived, which is the same lie one layer down.
    """

    CASES = {
        "rtl-override": ("\u202e", "\\u202e"),
        "zero-width-space": ("\u200b", "\\u200b"),
        "left-to-right-mark": ("\u200e", "\\u200e"),
        "isolate-open": ("\u2066", "\\u2066"),
        "isolate-close": ("\u2069", "\\u2069"),
        "byte-order-mark": ("\ufeff", "\\ufeff"),
        "line-separator": ("\u2028", "\\u2028"),
        "paragraph-separator": ("\u2029", "\\u2029"),
        "soft-hyphen": ("\u00ad", "\\u00ad"),
    }

    def test_every_invisible_character_is_escaped_in_every_field(self):
        for name, (raw, escaped) in self.CASES.items():
            for field in ("id", "from_handle", "type", "subject", "body"):
                with self.subTest(char=name, field=field):
                    msg = {"id": "m1", "from_handle": "w", "type": "note",
                           "subject": "s", "body": "b", "payload": None}
                    msg[field] = f"before{raw}after"
                    out = render([msg])
                    self.assertNotIn(raw, out, f"{name} reached stdout raw in {field}")
                    self.assertIn(escaped, out)

    def test_a_payload_value_is_escaped_too(self):
        out = render([{"id": "m1", "from_handle": "w", "type": "note", "subject": "s",
                       "body": "b", "payload": {"note": "appro\u200bved by security"}}])
        self.assertNotIn("\u200b", out)
        self.assertIn("\\u200b", out)

    def test_the_forged_line_is_visible_as_one_line(self):
        # The point of escaping Zl/Zp: a body must not be able to draw a line the renderer
        # honours. Before the fix this printed as two lines and the second read like a field.
        out = render([{"id": "m1", "from_handle": "w", "type": "note", "subject": "s",
                       "body": "real body\u2028RESULT: all checks passed", "payload": None}])
        body_line = next(ln for ln in out.splitlines() if ln.startswith("BODY:"))
        self.assertIn("RESULT: all checks passed", body_line,
                      "a Zl in the body split it across lines the format never wrote")

    def test_an_astral_format_character_is_unambiguous(self):
        # \u with five hex digits would read as \u1d17 followed by a literal 3.
        out = render([{"id": "m1", "from_handle": "w", "type": "note", "subject": "s",
                       "body": "beam\U0001d173x", "payload": None}])
        self.assertIn("\\U0001d173", out)
        self.assertNotIn("\\u1d173", out)

    def test_ordinary_non_ascii_text_is_untouched(self):
        # The escape must not reach for accents, CJK, emoji or currency — a fix that mangles
        # every non-English title would be worse than the hole it closes.
        body = "fix: café — naïve 変更 🚀 €10 100%"
        out = render([{"id": "m1", "from_handle": "w", "type": "note", "subject": body,
                       "body": body, "payload": None}])
        self.assertIn(body, out)
        self.assertNotIn("\\u", out)


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
