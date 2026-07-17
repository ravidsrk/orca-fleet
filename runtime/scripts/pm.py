#!/usr/bin/env python3
# pm.py — tolerant parser for `orca orchestration inbox/check` JSON output. (v2)
# The stream interleaves `_heartbeat` objects with real message batches, which breaks naive json.load.
# This decodes successive JSON objects, skips heartbeat-only envelopes STRUCTURALLY (not by line
# filtering, which could drop a mixed heartbeat+messages object), and prints each message.
#
# v2 (Codex review E3 remediation): a malformed segment no longer hides everything after it —
# the parser skips to the next line and keeps going, reporting the skip count at the end.
# Missing message fields print as '?' instead of raising KeyError.
#
# Usage:  orca orchestration inbox --json > inbox.json && python3 pm.py inbox.json
import json
import sys

if len(sys.argv) < 2:
    print("usage: pm.py <inbox.json>", file=sys.stderr)
    sys.exit(1)


def _has_messages_key(node):
    # True if a 'messages' key exists anywhere in the decoded structure.
    if isinstance(node, dict):
        return "messages" in node or any(_has_messages_key(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_messages_key(v) for v in node)
    return False

try:
    raw = open(sys.argv[1]).read()
except OSError as e:
    print(f"pm.py: ERROR: cannot read {sys.argv[1]}: {e.strerror or e}", file=sys.stderr)
    sys.exit(2)

dec = json.JSONDecoder()
i = 0
msgs = []
skipped = 0
unrecognized = 0
while i < len(raw):
    while i < len(raw) and raw[i] in " \t\r\n":
        i += 1
    if i >= len(raw):
        break
    try:
        obj, j = dec.raw_decode(raw, i)
        i = j
    except Exception:
        # Malformed segment: skip to the next line instead of aborting the whole stream.
        skipped += 1
        nl = raw.find("\n", i)
        if nl == -1:
            break
        i = nl + 1
        continue
    if not isinstance(obj, dict):
        continue
    result = obj.get("result")
    batch = result.get("messages") if isinstance(result, dict) else None
    if not isinstance(batch, list):
        batch = None  # a wrong-typed 'messages' (e.g. a string) is not a batch
    if batch is None and _has_messages_key(obj):
        # Message-bearing shape we don't parse — 'messages' misplaced at any depth
        # ({"messages": [...]}, {"data": {"messages": [...]}}, wrong-typed, or riding
        # inside a heartbeat envelope). Checked BEFORE the heartbeat skip so it can't
        # be swallowed; counting it as empty would misread a real inbox as empty.
        unrecognized += 1
        continue
    if "_heartbeat" in obj and not batch:
        continue  # heartbeat-only envelope; a mixed object still yields its messages below
    for m in batch or []:
        if isinstance(m, dict):
            msgs.append(m)

print("MESSAGES:", len(msgs))
for m in msgs:
    print("=" * 60)
    print("ID:", m.get("id", "?"), "| FROM:", m.get("from_handle", "?"), "| TYPE:", m.get("type", "?"))
    print("SUBJ:", m.get("subject", "?"))
    print("BODY:", m.get("body", ""))
    print("PAYLOAD:", m.get("payload"))
if skipped:
    print(f"pm.py: WARN: skipped {skipped} malformed segment(s)", file=sys.stderr)
if unrecognized:
    print(
        f"pm.py: WARN: {unrecognized} envelope(s) carried a 'messages' key outside the "
        "expected {'result': {'messages': [...]}} shape — the count above may undercount",
        file=sys.stderr,
    )
