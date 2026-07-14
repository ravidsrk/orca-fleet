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
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)

PROTOCOLS = {"diagnose"}


def make_skill(tmp, body, frontmatter_extra="proof: doctrine-only\n"):
    d = Path(tmp) / "demo-skill"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: A fixture. Use when testing.\n"
        + frontmatter_extra + "---\n" + body,
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

    def test_non_protocol_path_that_exists_is_fine(self):
        # proof_evidence and doc links are legitimate path references — the
        # path-prefix rule only guards PROTOCOL names (found by the first self-run,
        # whose closure commit tripped the old rule).
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. Evidence: docs/getting-started.md.\n"),
                PROTOCOLS)
            self.assertEqual(errs, [])

    def test_non_protocol_path_that_does_not_exist_dangles(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`. Evidence: docs/runs/never-happened.md.\n"),
                PROTOCOLS)
            self.assertTrue(any("dangling path" in e for e in errs), errs)

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


class TestProofStatus(unittest.TestCase):
    """The predecessor died presenting unproven missions as proven — machine-check it."""

    def test_missing_proof_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`.\n", frontmatter_extra=""), PROTOCOLS)
            self.assertTrue(any("missing 'proof'" in e for e in errs), errs)

    def test_invalid_proof_value_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`.\n",
                           frontmatter_extra="proof: battle-tested\n"), PROTOCOLS)
            self.assertTrue(any("proof 'battle-tested' invalid" in e for e in errs), errs)

    def test_advanced_proof_without_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            errs = validate.validate_skill(
                make_skill(tmp, "Composes `diagnose`.\n",
                           frontmatter_extra="proof: self-run\n"), PROTOCOLS)
            self.assertTrue(any("requires proof_evidence" in e for e in errs), errs)

    def test_over_budget_mission_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = "Composes `diagnose`.\n" + ("filler line\n" * validate.MISSION_MAX_LINES)
            errs = validate.validate_skill(make_skill(tmp, body), PROTOCOLS)
            self.assertTrue(any("instruction budget" in e for e in errs), errs)

    def test_mutating_mission_must_ride_evidence_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Folder name is the mission name used by the mutator check.
            d = Path(tmp) / "ship-it"
            d.mkdir()
            (d / "SKILL.md").write_text(
                "---\nname: ship-it\ndescription: Use when shipping.\n"
                "proof: doctrine-only\n---\n\nComposes `diagnose`.\n",
                encoding="utf-8",
            )
            errs = validate.validate_skill(d, PROTOCOLS | {"diagnose"})
            self.assertTrue(
                any("must ride `evidence-manifest`" in e for e in errs), errs
            )

    def test_mutating_mission_compose_mention_alone_does_not_count(self):
        # Codex P2: backticks in a Composes paragraph must not satisfy the ride.
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "ship-it"
            d.mkdir()
            (d / "SKILL.md").write_text(
                "---\nname: ship-it\ndescription: Use when shipping.\n"
                "proof: doctrine-only\n---\n\n"
                "Composes `diagnose`; unlike other missions it does not ride "
                "`evidence-manifest`.\n",
                encoding="utf-8",
            )
            errs = validate.validate_skill(
                d, PROTOCOLS | {"diagnose", "evidence-manifest"}
            )
            self.assertTrue(
                any("must ride `evidence-manifest`" in e for e in errs), errs
            )

    def test_mutating_mission_with_evidence_manifest_passes_that_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "ship-it"
            d.mkdir()
            (d / "SKILL.md").write_text(
                "---\nname: ship-it\ndescription: Use when shipping.\n"
                "proof: doctrine-only\n---\n\n"
                "Composes `diagnose`; rides `evidence-manifest`.\n",
                encoding="utf-8",
            )
            errs = validate.validate_skill(
                d, PROTOCOLS | {"diagnose", "evidence-manifest"}
            )
            self.assertFalse(
                any("must ride `evidence-manifest`" in e for e in errs), errs
            )


class TestProtocolDocRefs(unittest.TestCase):
    """Dangling .md refs inside playbooks/ and runtime/ must fail the build too."""

    def _with_dirs(self, doc_text):
        with tempfile.TemporaryDirectory() as tmp:
            playbooks = Path(tmp) / "playbooks"
            runtime = Path(tmp) / "runtime"
            playbooks.mkdir()
            runtime.mkdir()
            (playbooks / "demo.md").write_text(doc_text, encoding="utf-8")
            with mock.patch.object(validate, "PLAYBOOKS_DIR", playbooks), \
                 mock.patch.object(validate, "RUNTIME_DIR", runtime), \
                 mock.patch.object(validate, "ROOT", Path(tmp)):
                return validate.check_protocol_doc_refs(PROTOCOLS)

    def test_dangling_ref_in_playbook_fails(self):
        failures = self._with_dirs("The LAND phase runs per land.md as always.\n")
        self.assertTrue(any("land.md" in f for f in failures), failures)

    def test_resolving_ref_in_playbook_passes(self):
        failures = self._with_dirs("Escalate per diagnose.md when the loop stalls.\n")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
