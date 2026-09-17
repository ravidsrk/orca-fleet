#!/usr/bin/env python3
"""Independent re-derivation for the attest-it self-run (NIST-SP-800-218@1.0.0).

Reads ONLY: the frozen catalog, git objects at TARGET_SHA, the working-tree run
dir, and the evidence files' claims. Re-derives every checkable claim:
quote existence at TARGET_SHA, absence/no-match claims, obligation-text
fidelity, manifest provenance + digests, and release/tag binding.
Exit 0 iff every check passes. Writes rederive.log beside itself.
"""
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
TARGET_SHA = "6390743815f8f435181fa410cce374587128b30a"
FROZEN = "NIST-SP-800-218@1.0.0"
SOURCE_SHA256 = "b01634a5fdb382e7a12660c379a4d0bc3a2b8e29abccf2861834880005137117"

fails, passes = [], []
def check(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))

def git(*args):
    p = subprocess.run(["git", *args], capture_output=True, text=True, cwd=RUN.parent.parent.parent)
    return p

# 0. frozen source integrity
src = RUN / "catalog" / "NIST_SP800-218_ver1_catalog.json"
check("source-bytes-sha256", hashlib.sha256(src.read_bytes()).hexdigest() == SOURCE_SHA256)
frozen = json.loads((RUN / "catalog" / "frozen-catalog.json").read_text())
obs = {o["id"]: o for o in frozen["obligations"]}
check("catalog-count-42", len(obs) == 42, f"got {len(obs)}")
check("catalog-version", frozen["version"] == "1.0.0" and frozen["standard"] == "NIST-SP-800-218")

tracked = git("ls-tree", "-r", "--name-only", TARGET_SHA).stdout.splitlines()
file_cache = {}
def target_lines(path):
    if path not in file_cache:
        p = git("show", f"{TARGET_SHA}:{path}")
        file_cache[path] = None if p.returncode else p.stdout.splitlines()
    return file_cache[path]

evdir = RUN / "evidence"
evfiles = sorted(evdir.glob("*.md"))
check("evidence-count-42", len(evfiles) == 42, f"got {len(evfiles)}")
missing = [i for i in obs if not (evdir / f"{i}.md").exists()]
check("evidence-covers-denominator", not missing, f"missing {missing}")

Q = re.compile(r'^\s*-\s*`(RUN:)?([^`]+):(\d+)`:\s*"(.*)"\s*$')
ABS = re.compile(r'^\s*-\s*Absent:\s*`([^`]+)`\s*$')
NOM = re.compile(r'^\s*-\s*NoMatch:\s*`([^`]+)`\s*::\s*`([^`]+)`\s*$')
OBL = re.compile(r'^- Obligation \(frozen [^)]*\):\s*"(.*)"\s*$', re.M)
VER = re.compile(r'^- Verdict:\s*(VERIFIED|GAP)\s*$', re.M)

for oid, o in sorted(obs.items()):
    p = evdir / f"{oid}.md"
    if not p.exists():
        continue
    text = p.read_text()
    lines = text.splitlines()
    m = VER.search(text)
    check(f"{oid}.verdict-present", bool(m))
    verdict = m.group(1) if m else None
    m = OBL.search(text)
    check(f"{oid}.statement-fidelity", bool(m) and m.group(1) == o["statement"],
          "statement differs from frozen catalog" if m else "no obligation line")
    nq = 0
    for ln in lines:
        q = Q.match(ln)
        if q:
            nq += 1
            is_run, path, lno, want = q.group(1), q.group(2), int(q.group(3)), q.group(4)
            if is_run:
                rp = RUN / path
                got = rp.read_text().splitlines() if rp.exists() else None
                ok = got is not None and 0 < lno <= len(got) and got[lno - 1] == want
                check(f"{oid}.runquote:{path}:{lno}", ok,
                      f"want {want!r} got {(got[lno-1] if got and 0 < lno <= len(got) else None)!r}")
            else:
                got = target_lines(path)
                ok = got is not None and 0 < lno <= len(got) and got[lno - 1] == want
                check(f"{oid}.quote:{path}:{lno}", ok,
                      f"want {want!r} got {(got[lno-1] if got and 0 < lno <= len(got) else None)!r}")
        a = ABS.match(ln)
        if a:
            pat = a.group(1).lower()
            hits = [t for t in tracked if fnmatch.fnmatch(t.lower(), pat)]
            check(f"{oid}.absent:{a.group(1)}", not hits, f"exists at TARGET: {hits[:3]}")
        n = NOM.match(ln)
        if n:
            got = target_lines(n.group(1))
            hit = got is not None and re.search(n.group(2), "\n".join(got))
            check(f"{oid}.nomatch:{n.group(1)}:{n.group(2)[:40]}", got is not None and not hit,
                  "pattern matched" if hit else "file missing at TARGET")
    if verdict == "VERIFIED":
        check(f"{oid}.has-quotes", nq >= 1, "VERIFIED with no quoted artifact")
    if verdict == "GAP":
        check(f"{oid}.gap-owner", bool(re.search(r'^- Owner: \S', text, re.M)), "no owner")
        check(f"{oid}.gap-handoff", bool(re.search(r'^- Handoff: gaps/\S+\.md', text, re.M)), "no handoff")

# manifests
mandir = RUN / "manifests"
mf = sorted(mandir.glob("*.json")) if mandir.exists() else []
check("manifest-count-42", len(mf) == 42, f"got {len(mf)}")
for oid, o in sorted(obs.items()):
    mp = mandir / f"{oid}.json"
    if not mp.exists():
        check(f"{oid}.manifest-exists", False)
        continue
    m = json.loads(mp.read_text())
    prov = m.get("provenance", {})
    check(f"{oid}.prov-standard", prov.get("standard") == "SSDF")
    check(f"{oid}.prov-spec", prov.get("spec_version") == FROZEN,
          f"got {prov.get('spec_version')!r}")
    check(f"{oid}.prov-fields", all(prov.get(k) for k in ("model", "reviewer", "retention")))
    tspec = RUN / "taskspecs" / f"{oid}.json"
    want_digest = hashlib.sha256(tspec.read_bytes()).hexdigest() if tspec.exists() else None
    check(f"{oid}.contract-digest", m.get("contract", {}).get("digest") == want_digest)
    crit = (m.get("criteria") or [{}])[0]
    check(f"{oid}.criteria-text", crit.get("id") == oid and crit.get("text") == o["statement"])
    check(f"{oid}.sha-binding", m.get("base_sha") == TARGET_SHA and m.get("head_sha") == TARGET_SHA)
    for a in m.get("artifacts", []):
        ap = RUN.parent.parent.parent / a["path"]
        ok = ap.exists() and hashlib.sha256(ap.read_bytes()).hexdigest() == a["sha256"]
        check(f"{oid}.artifact:{a['path']}", ok)

# cross-checks: release/tag binding (PS.2.1/PS.3.1), suite receipt (PW.8.2)
rel = json.loads(target_lines("docs/releases.json") and "\n".join(target_lines("docs/releases.json")))
for r in rel["releases"]:
    c = git("cat-file", "-e", r["commit"]).returncode == 0
    t = git("rev-parse", f"{r['tag']}^{{commit}}").stdout.strip()
    check(f"release.{r['version']}.binding", c and t == r["commit"], f"tag->{t}")
slog = (RUN / "receipts" / "suite-2026-09-16.log").read_text()
check("suite.receipt-ok", "Ran 1490 tests" in slog and "\nOK\n" in slog.replace("\r", ""))

print(f"\n{len(passes)} passed, {len(fails)} failed")
# The log holds no volatile counts: in the green state its bytes are constant
# across runs, so manifests can pin it by sha256 and the pin converges.
(RUN / "rederive" / "rederive.log").write_text(
    f"TARGET={TARGET_SHA} FROZEN={FROZEN} RESULT={'FAIL' if fails else 'PASS'}\n"
    + "".join(f"FAIL {f}\n" for f in fails))
sys.exit(1 if fails else 0)
