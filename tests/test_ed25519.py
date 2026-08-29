#!/usr/bin/env python3
"""Correctness tests for the vendored Ed25519 (runtime/scripts/ed25519.py), #135.

Hand-vendored crypto is only trustworthy if it reproduces the standard's own test vectors, so this
pins RFC 8032 §7.1 Test 2 (public key, signature, and verification all exact) plus round-trip,
tamper-rejection, and wrong-key-rejection. A regression in the field arithmetic fails here, not at a
dispatch gate.
"""
import binascii
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ed25519", ROOT / "runtime" / "scripts" / "ed25519.py")
ed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ed)


def h(s):
    return binascii.unhexlify(s)


class Ed25519RFC8032(unittest.TestCase):
    # RFC 8032 §7.1, Test 2 (1-byte message).
    SEED = h("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb")
    PUB = h("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c")
    MSG = h("72")
    SIG = h("92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
            "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00")

    def test_public_key_matches_rfc(self):
        self.assertEqual(ed.publickey(self.SEED), self.PUB)

    def test_signature_matches_rfc(self):
        self.assertEqual(ed.signature(self.MSG, self.SEED, self.PUB), self.SIG)

    def test_verify_rfc_signature(self):
        self.assertTrue(ed.checkvalid(self.SIG, self.MSG, self.PUB))

    def test_tampered_message_rejected(self):
        self.assertFalse(ed.checkvalid(self.SIG, b"\x73", self.PUB))

    def test_wrong_key_rejected(self):
        other = ed.publickey(h("9d61b19deffebc3f6a2e77c58c8f5cbd68bdc60df06135e4a5e58d54c8e8b7b6"))
        self.assertFalse(ed.checkvalid(self.SIG, self.MSG, other))

    def test_round_trip(self):
        seed = bytes(range(32))
        pub = ed.publickey(seed)
        sig = ed.signature(b"dispatch tuple", seed, pub)
        self.assertTrue(ed.checkvalid(sig, b"dispatch tuple", pub))
        self.assertFalse(ed.checkvalid(sig, b"dispatch tuplE", pub))


class Ed25519Malleability(unittest.TestCase):
    # RFC 8032 leaves S unbounded; (R, S+L) verifies against the same key and message.
    SEED = h("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb")
    PUB = h("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c")
    MSG = h("72")
    SIG = h("92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
            "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00")

    def test_s_plus_group_order_rejected(self):
        S = int.from_bytes(self.SIG[32:], "little")
        mauled = self.SIG[:32] + (S + ed._L).to_bytes(32, "little")
        self.assertFalse(ed.checkvalid(mauled, self.MSG, self.PUB))

    def test_s_at_group_order_rejected(self):
        sig = self.SIG[:32] + ed._L.to_bytes(32, "little")
        self.assertFalse(ed.checkvalid(sig, self.MSG, self.PUB))


class Ed25519SmallOrderKeys(unittest.TestCase):
    # Issue #175 attack: with an attacker-chosen small-order key A, pick any s, set R = sB,
    # and (R, s) satisfies the verification equation because Hint(...)*A collapses.
    def assert_forgery_rejected(self, pub):
        msg = b"forged dispatch record"
        s = 0xDEADBEEF
        R = ed._scalarmult(ed._B, s)
        sig = ed._encodepoint(R) + s.to_bytes(32, "little")
        self.assertFalse(ed.checkvalid(sig, msg, pub))

    def test_identity_key_rejected(self):
        # The identity point encodes as y = 1, x = 0.
        identity_pub = b"\x01" + b"\x00" * 31
        self.assert_forgery_rejected(identity_pub)

    def test_order_two_key_rejected(self):
        # The order-2 point (0, -1): also small-order, also collapses under the cofactor.
        order_two_pub = (ed._q - 1).to_bytes(32, "little")
        self.assert_forgery_rejected(order_two_pub)

    def test_noncanonical_key_encoding_rejected(self):
        # y = _q + 1 is a non-canonical encoding of the identity point (y == 1 mod q);
        # without the canonical check it decodes to the identity and the forgery verifies.
        noncanonical_identity = (ed._q + 1).to_bytes(32, "little")
        self.assert_forgery_rejected(noncanonical_identity)

    def test_decodepoint_rejects_noncanonical_y(self):
        with self.assertRaises(ValueError):
            ed._decodepoint((ed._q + 1).to_bytes(32, "little"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
