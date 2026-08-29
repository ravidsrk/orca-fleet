#!/usr/bin/env python3
"""dispatch-sign.py — the COORDINATOR's out-of-band signer for #135 (native-hook soundness).

The native Stop/TaskCompleted hook runs IN the graded worker's session, so the worker controls the
env (`ORCA_CONTRACT_DIGEST`, `ORCA_UNIT_CLASS`, …) and could substitute a weaker denominator or
downgrade its class. To make the native path SOUND, the coordinator — which runs OFF the worker
(a separate session, CI, or the human's machine) and holds a private key the worker never sees —
signs the dispatch tuple at dispatch time. The gate (verify.py) verifies that signature against the
repo-pinned PUBLIC key, so an in-session substitution is detected.

    dispatch-sign.py gen-key --out .secrets/dispatch-key
        # writes the 32-byte seed to <out> (keep OFF the worker) and the public key to <out>.pub;
        # commit <out>.pub as .orca/dispatch-pubkey to turn on enforcement (docs/verify-gate.md).

    dispatch-sign.py sign --key .secrets/dispatch-key \\
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


def gen_key(out: Path) -> int:
    ed = _load_ed25519()
    seed = os.urandom(32)
    pub = ed.publickey(seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(seed.hex() + "\n", encoding="utf-8")
    os.chmod(out, 0o600)
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

    s = sub.add_parser("sign", help="sign a dispatch record")
    s.add_argument("--key", required=True, help="private seed file from gen-key")
    s.add_argument("--manifest-id", required=True, help="the unit/manifest id this dispatch binds")
    s.add_argument("--contract-digest", required=True, help="sha256:… of the frozen contract")
    s.add_argument("--unit-class", required=True, help="mutation | report-only | planning")
    s.add_argument("--lighting", default=None, help="lit | dark-eligible (optional)")

    args = ap.parse_args(argv)
    if args.cmd == "gen-key":
        return gen_key(Path(args.out))
    record = {
        "manifest_id": args.manifest_id,
        "contract_digest": args.contract_digest,
        "unit_class": args.unit_class,
        "lighting": args.lighting,
    }
    return sign(Path(args.key), record)


if __name__ == "__main__":
    sys.exit(main())
