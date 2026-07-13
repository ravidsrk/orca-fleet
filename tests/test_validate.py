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

    def test_path_prefixed_ref_is_flagged(self):
        # Basename-only resolution would let playbooks/sandbox-policy.md pass even
        # though the file lives in runtime/ — the convention is bare names.
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. See playbooks/diagnose.md.\n"), PROTOCOLS)
            self.assertTrue(any("path-prefixed reference" in e for e in errs), errs)

    def test_uppercase_doc_mentions_exempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. Read ../../ARCHITECTURE.md once.\n"),
                PROTOCOLS)
            self.assertEqual(errs, [])

    def test_abbreviation_inside_clause_does_not_truncate_scan(self):
        # ". " after "e.g" used to end the clause capture; names after it escaped.
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose` (e.g. `bogus-one`), `bogus-two`.\n"),
                PROTOCOLS)
            self.assertTrue(any("`bogus-one`" in e for e in errs), errs)
            self.assertTrue(any("`bogus-two`" in e for e in errs), errs)

    def test_capitalized_rides_clause_is_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`.\n\nRides `bogus-policy` at runtime.\n"),
                PROTOCOLS)
            self.assertTrue(any("`bogus-policy`" in e for e in errs), errs)

    def test_url_md_link_not_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(
                    tmp,
                    "Composes `diagnose`. See https://example.com/upstream-guide.md too.\n"),
                PROTOCOLS)
            self.assertEqual(errs, [])

    def test_case_typo_of_protocol_is_flagged(self):
        # The uppercase exemption must not shelter a typo of a real protocol name.
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. See Diagnose.md for the loop.\n"),
                PROTOCOLS)
            self.assertTrue(any("case/underscore typo" in e for e in errs), errs)


class TestProtocolDocRefs(unittest.TestCase):
    """Dangling .md refs inside playbooks/ and runtime/ must fail the build too."""

    def _with_dirs(self, doc_text):
        with tempfile.TemporaryDirectory() as tmp:
            playbooks = Path(tmp) / "playbooks"
            runtime = Path(tmp) / "runtime"
            playbooks.mkdir()
            runtime.mkdir()
            (playbooks / "demo.md").write_text(doc_text, encoding="utf-8")
            old = validate.PLAYBOOKS_DIR, validate.RUNTIME_DIR, validate.ROOT
            validate.PLAYBOOKS_DIR, validate.RUNTIME_DIR, validate.ROOT = (
                playbooks, runtime, Path(tmp))
            try:
                return validate.check_protocol_doc_refs(PROTOCOLS)
            finally:
                validate.PLAYBOOKS_DIR, validate.RUNTIME_DIR, validate.ROOT = old

    def test_dangling_ref_in_playbook_fails(self):
        failures = self._with_dirs("The LAND phase runs per land.md as always.\n")
        self.assertTrue(any("land.md" in f for f in failures), failures)

    def test_resolving_ref_in_playbook_passes(self):
        failures = self._with_dirs("Escalate per diagnose.md when the loop stalls.\n")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
