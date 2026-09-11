#!/usr/bin/env python3
"""Read an `orca vm recipe doctor <recipe> --provision` transcript and say whether it is CLEAR.

sandbox-policy.md states the rule the `danger` lane rests on: clear means **no `fail` AND no
`warn`**; `ok:true` on its own proves nothing, because a warn is a lane that boots and then fails
a build halfway through (`orca-per-workspace-env:110-122`).

`spawn_worker.sh` used to enforce that rule with `grep -qiE '(^|[^a-z])(fail|warn)'` over a file
the CALLER named, which got the answer wrong in both directions (#283):

* `/etc/passwd` passed — it names "root" and carries neither word, so `ORCA_SANDBOX_RECIPE=root`
  plus `ORCA_SANDBOX_DOCTOR=/etc/passwd` spawned a danger worker;
* a genuine transcript carrying `"failures": []` was REFUSED, because the substring "fail" is
  right there inside the word that reports there were none.

The caller-named file is gone — `spawn_worker.sh` runs the doctor itself now and passes its own
output here. What is left for this module is reading the verdict without either mistake: read it
STRUCTURALLY where the output is JSON, and where it is plain text ignore the shapes that mean
"none of these" before looking for the words that mean "some of these".

Exit codes
    0  the transcript is clear for this recipe
    1  it is not (the reason goes to stderr)
    2  usage
"""
from __future__ import annotations

import json
import re
import sys

# Status/level values that are a doctor telling you something is wrong.
BAD_STATUS = {"fail", "failed", "failing", "failure", "error", "errored", "warn", "warning"}
# Keys whose CONTENTS are the findings, so an empty one is good news.
FINDING_KEYS = ("failures", "warnings", "errors", "problems", "issues")
# Keys whose VALUE is a verdict word.
STATUS_KEYS = ("status", "level", "severity", "state", "result")

# "none of these", in the text forms a doctor writes them: "failures": [], failures: 0,
# warnings={}, errors: none, 0 warnings, no failures.
_EMPTY = re.compile(
    r"""["']?(?:fail(?:ure)?s?|warn(?:ing)?s?|errors?|problems?|issues?)["']?\s*[:=]\s*"""
    r"""(?:\[\s*\]|\{\s*\}|0\b|none\b|null\b|false\b)"""
    r"""|\b(?:0|no)\s+(?:fail(?:ure)?s?|warn(?:ing)?s?|errors?|problems?|issues?)\b""",
    re.IGNORECASE,
)
_BAD_WORD = re.compile(r"(^|[^a-z])(fail|warn|error)", re.IGNORECASE)


def findings(obj):
    """Every fail/warn the doctor structurally reports. An empty collection reports nothing."""
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            low = str(key).lower()
            if low in FINDING_KEYS:
                if isinstance(value, (list, tuple, dict)):
                    if len(value):
                        found.append(f"{key}={len(value)}")
                        found += findings(value)
                elif isinstance(value, bool):
                    if value:
                        found.append(f"{key}=true")
                elif isinstance(value, (int, float)):
                    if value:
                        found.append(f"{key}={value}")
                elif isinstance(value, str) and value.strip().lower() not in ("", "none", "0"):
                    found.append(f"{key}={value.strip()[:40]}")
            elif low in STATUS_KEYS and str(value).strip().lower() in BAD_STATUS:
                found.append(f"{key}={value}")
            elif low == "ok" and value is False:
                found.append("ok=false")
            else:
                found += findings(value)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            found += findings(item)
    return found


def verdict(raw, recipe):
    """(clear, reason). `clear` is True only when the transcript is about THIS recipe and reports
    no fail and no warn."""
    try:
        doc = json.loads(raw)
    except ValueError:
        doc = None

    if doc is not None:
        if recipe.lower() not in json.dumps(doc).lower():
            return False, f"doctor output does not name recipe {recipe!r}"
        bad = sorted(set(findings(doc)))
        if bad:
            return False, "doctor reports " + ", ".join(bad[:4])
        return True, ""

    if recipe.lower() not in raw.lower():
        return False, f"doctor output does not name recipe {recipe!r}"
    stripped = _EMPTY.sub(" ", raw)
    if _BAD_WORD.search(stripped):
        line = next((ln.strip() for ln in stripped.splitlines() if _BAD_WORD.search(ln)), "")
        return False, f"doctor is not clear: {line[:120]!r}"
    return True, ""


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2:
        print("usage: sandbox_doctor.py <transcript> <recipe-id>", file=sys.stderr)
        return 2
    path, recipe = argv
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw = fh.read()
    except OSError as err:
        print(f"cannot read the doctor transcript: {err}", file=sys.stderr)
        return 1
    clear, reason = verdict(raw, recipe)
    if not clear:
        print(reason, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
