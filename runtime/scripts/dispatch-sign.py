#!/usr/bin/env python3
"""dispatch-sign.py — the COORDINATOR's out-of-band signer for #135 (native-hook soundness).

The native Stop/TaskCompleted hook runs IN the graded worker's session, so the worker controls the
env (`ORCA_CONTRACT_DIGEST`, `ORCA_UNIT_CLASS`, …) and could substitute a weaker denominator or
downgrade its class. To make the native path SOUND, the coordinator — which runs OFF the worker
(a separate session, CI, or the human's machine) and holds a private key the worker never sees —
signs the dispatch tuple at dispatch time. The gate (verify.py) verifies that signature against the
repo-pinned PUBLIC key, so an in-session substitution is detected.

    dispatch-sign.py gen-key --out ~/.orca-fleet/dispatch-key
        # writes the 32-byte seed to <out> (keep OFF the worker AND out of this repo) and the
        # public key to <out>.pub; commit <out>.pub as .orca/dispatch-pubkey to turn on
        # enforcement (docs/verify-gate.md). gen-key refuses to write a seed inside a git work
        # tree unless the path is git-ignored (or --in-repo-ok is given).

    dispatch-sign.py sign --key ~/.orca-fleet/dispatch-key \\
        --manifest-id <unit-id> --contract-digest sha256:… --unit-class mutation [--lighting lit]
        # prints the signed envelope JSON the gate consumes via --dispatch-record.

Stdlib-only; the signature scheme is runtime/scripts/ed25519.py (vendored, RFC 8032).
"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load_ed25519():
    spec = importlib.util.spec_from_file_location("ed25519", _HERE / "ed25519.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The signed fields — the dispatch tuple a worker must not be able to forge. Canonicalized the same
# way here and in verify.py so the bytes over which the signature is computed are identical.
_RECORD_FIELDS = ("manifest_id", "contract_digest", "unit_class", "lighting")


def canonical_record(record: dict) -> bytes:
    """Deterministic bytes for signing/verifying: only the signed fields, sorted, no whitespace."""
    subset = {k: record[k] for k in _RECORD_FIELDS if record.get(k) is not None}
    return json.dumps(subset, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _in_unignored_worktree(path: Path) -> bool:
    """True when `path` may be inside a git work tree without ignore coverage.

    A seed written there is one `git add -A` away from being committed (#166), so gen-key refuses
    unless the caller passes --in-repo-ok. `git add -A` can reach the path only if git resolves a
    repository from (a) a `.git` ancestor (dir, or worktree/submodule file) or (b) the ambient
    environment (GIT_DIR / core.worktree) — so we probe both. (a) is a filesystem walk, immune to
    rev-parse's conflation of "not a repo" with real errors; (b) is rev-parse, which honors the
    env. Once git control is established, ignore status comes from `git check-ignore`; git missing
    or an inconclusive result fails CLOSED — an unknown ignore status is not "safe" for a key.
    """
    resolved = path.resolve()
    probe = resolved.parent
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    under_git = False
    ancestor = probe
    while True:
        if (ancestor / ".git").exists():
            under_git = True
            break
        if ancestor == ancestor.parent:
            break
        ancestor = ancestor.parent
    if not under_git:
        # No .git ancestor — the only remaining way `git add` could stage this path is a repo
        # resolved from the environment (GIT_DIR, core.worktree). Ask git itself.
        try:
            top = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                 cwd=probe, capture_output=True, text=True)
        except OSError:
            return False  # no .git ancestor AND no git binary: nothing can stage the file
        if top.returncode != 0:
            return False  # proven: no work tree claims the path — the out-of-repo layout
        toplevel = Path(top.stdout.strip()).resolve()
        under_git = resolved == toplevel or toplevel in resolved.parents
    if not under_git:
        return False
    try:
        check = subprocess.run(["git", "check-ignore", "-q", "--", str(resolved)],
                               cwd=probe, capture_output=True)
    except OSError:
        return True  # in a work tree but git won't run — cannot prove the path is ignored
    return check.returncode != 0  # 0 = ignored (safe); 1 = not ignored; anything else = unknown


def gen_key(out: Path, in_repo_ok: bool = False) -> int:
    if _in_unignored_worktree(out) and not in_repo_ok:
        print(f"dispatch-sign: REFUSING to write a private seed at {out}", file=sys.stderr)
        print("  the path is (or could not be proven NOT) inside a git work tree and is NOT",
              file=sys.stderr)
        print("  verified git-ignored — one `git add -A` would commit the key and void every",
              file=sys.stderr)
        print("  signed-dispatch guarantee.", file=sys.stderr)
        print("  pick an out-of-repo path (e.g. ~/.orca-fleet/dispatch-key), git-ignore it,",
              file=sys.stderr)
        print("  or pass --in-repo-ok if you really mean it.", file=sys.stderr)
        return 2
    ed = _load_ed25519()
    seed = os.urandom(32)
    pub = ed.publickey(seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    # The seed gets its final permissions AT CREATION (os.open mode 0o600), then fchmod on the
    # open fd covers re-generation over a pre-existing permissive file — never create-under-umask
    # then chmod, which leaves the seed world-readable between the two calls (#163).
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        os.fchmod(fh.fileno(), 0o600)
        fh.write(seed.hex() + "\n")
    pub_path = out.with_suffix(out.suffix + ".pub") if out.suffix else Path(str(out) + ".pub")
    pub_path.write_text(pub.hex() + "\n", encoding="utf-8")
    print(f"private seed: {out} (0600 — keep OFF the graded worker)", file=sys.stderr)
    print(f"public key:   {pub_path} (commit as .orca/dispatch-pubkey to enforce)", file=sys.stderr)
    return 0


def sign(key: Path, record: dict) -> int:
    ed = _load_ed25519()
    seed = bytes.fromhex(key.read_text(encoding="utf-8").strip())
    if len(seed) != 32:
        print("dispatch-sign: key must be a 32-byte hex seed", file=sys.stderr)
        return 1
    pub = ed.publickey(seed)
    sig = ed.signature(canonical_record(record), seed, pub)
    envelope = {
        "record": {k: record[k] for k in _RECORD_FIELDS if record.get(k) is not None},
        "sig_b64": base64.b64encode(sig).decode("ascii"),
    }
    print(json.dumps(envelope, indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Coordinator dispatch-record signer (#135).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen-key", help="generate an Ed25519 keypair")
    g.add_argument("--out", required=True, help="path for the private seed; <out>.pub gets the pubkey")
    g.add_argument("--in-repo-ok", action="store_true",
                   help="allow writing the seed inside a git work tree even when it is not ignored")

    s = sub.add_parser("sign", help="sign a dispatch record")
    s.add_argument("--key", required=True, help="private seed file from gen-key")
    s.add_argument("--manifest-id", required=True, help="the unit/manifest id this dispatch binds")
    s.add_argument("--contract-digest", required=True, help="sha256:… of the frozen contract")
    s.add_argument("--unit-class", required=True, help="mutation | report-only | planning")
    s.add_argument("--lighting", default=None, help="lit | dark-eligible (optional)")

    args = ap.parse_args(argv)
    if args.cmd == "gen-key":
        return gen_key(Path(args.out), in_repo_ok=args.in_repo_ok)
    record = {
        "manifest_id": args.manifest_id,
        "contract_digest": args.contract_digest,
        "unit_class": args.unit_class,
        "lighting": args.lighting,
    }
    return sign(Path(args.key), record)


if __name__ == "__main__":
    sys.exit(main())
