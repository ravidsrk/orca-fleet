#!/usr/bin/env python3
"""
Negative-path tests for scripts/validate.py on synthetic fixtures.

test_architecture.py proves the validator passes the real (always-valid) corpus;
from that suite's perspective every failure branch is dead code — a regression
that stops the validator from firing would ship green. These tests lock each
error branch to a fixture that must trip it.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)

PROTOCOLS = {"diagnose"}


def make_skill(tmp, body):
    d = Path(tmp) / "demo-skill"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: A fixture. Use when testing.\n---\n" + body,
        encoding="utf-8",
    )
    return d


class TestValidatorFailureBranches(unittest.TestCase):

    def test_clause_without_backticked_names_fails(self):
        # The old ship-it shape: a Composes clause the regex can't see into.
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes the playbooks directory.\n"), PROTOCOLS)
            self.assertTrue(
                any("no machine-checkable composition" in e for e in errs), errs)

    def test_dangling_backticked_composition_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `nonexistent-playbook`. \n"), PROTOCOLS)
            self.assertTrue(any("dangling composition" in e for e in errs), errs)

    def test_dangling_md_mention_outside_clause_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. See land.md for landing.\n"), PROTOCOLS)
            self.assertTrue(
                any("dangling reference: land.md" in e for e in errs), errs)

    def test_path_prefixed_lowercase_md_ref_resolves(self):
        # The rsplit basename strip: playbooks/diagnose.md must resolve, not dangle.
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. See playbooks/diagnose.md.\n"), PROTOCOLS)
            self.assertEqual(errs, [])

    def test_uppercase_doc_mentions_exempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. Read ../../ARCHITECTURE.md once.\n"),
                PROTOCOLS)
            self.assertEqual(errs, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
