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

raw = open(sys.argv[1]).read()

dec = json.JSONDecoder()
i = 0
msgs = []
skipped = 0
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
    result = obj.get("result") or {}
    batch = result.get("messages") if isinstance(result, dict) else None
    if "_heartbeat" in obj and not batch:
        continue  # heartbeat-only envelope; a mixed object still yields its messages below
    for m in batch or []:
        if isinstance(m, dict):
            msgs.append(m)

print("MESSAGES:", len(msgs))
for m in msgs:
    print("=" * 60)
    print("FROM:", m.get("from_handle", "?"), "| TYPE:", m.get("type", "?"))
    print("SUBJ:", m.get("subject", "?"))
    print("BODY:", m.get("body", ""))
    print("PAYLOAD:", m.get("payload"))
if skipped:
    print(f"pm.py: WARN: skipped {skipped} malformed segment(s)", file=sys.stderr)
