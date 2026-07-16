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

    def test_mutating_mission_prose_rides_does_not_count(self):
        # Greptile P2: mid-sentence "rides `…`" in anti-patterns must not satisfy.
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "ship-it"
            d.mkdir()
            (d / "SKILL.md").write_text(
                "---\nname: ship-it\ndescription: Use when shipping.\n"
                "proof: doctrine-only\n---\n\n"
                "Composes `diagnose`.\n\n"
                "## Anti-patterns\n\n"
                "If the worker rides `evidence-manifest` out of turn, ignore it.\n",
                encoding="utf-8",
            )
            errs = validate.validate_skill(
                d, PROTOCOLS | {"diagnose", "evidence-manifest"}
            )
            self.assertTrue(
                any("must ride `evidence-manifest`" in e for e in errs), errs
            )

    def test_mutating_mission_all_caps_rides_counts(self):
        # Greptile P2: RIDES must match like COMPOSES.
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "ship-it"
            d.mkdir()
            (d / "SKILL.md").write_text(
                "---\nname: ship-it\ndescription: Use when shipping.\n"
                "proof: doctrine-only\n---\n\n"
                "Composes `diagnose`.\n\nRIDES `evidence-manifest`.\n",
                encoding="utf-8",
            )
            errs = validate.validate_skill(
                d, PROTOCOLS | {"diagnose", "evidence-manifest"}
            )
            self.assertFalse(
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


class TestCountAgnosticGuards(unittest.TestCase):
    """The count-lint, keyword-check, and badge-freshness guards must each be able to fire —
    a mission is added by a human, so the guards that keep the docs count-agnostic and the
    manifest/badges in sync are the safety net."""

    def test_count_lint_matches_catalog_counts(self):
        for s in ("11 missions", "eleven missions", "twelve missions", "10 outcome-named",
                  "11 callable", "eleven outcome-named", "twelve callable"):
            self.assertRegex(s, validate.COUNT_LINT_RE, s)

    def test_count_lint_ignores_mission_identity_prose(self):
        # "one mission" / "two missions" in the identity discussion are NOT catalog counts.
        for s in ("are one mission (clean-sweep)", "two workflows are the same mission",
                  "each mission is one outcome", "the missions genuinely differ",
                  "assets/badges/missions.json"):
            self.assertIsNone(validate.COUNT_LINT_RE.search(s), s)

    def test_check_doc_counts_flags_hardcoded_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text("orca-fleet ships eleven missions.\n",
                                                 encoding="utf-8")
            with mock.patch.object(validate, "ROOT", Path(tmp)), \
                 mock.patch.object(validate, "COUNT_LINT_FILES", ("README.md",)):
                failures = validate.check_doc_counts()
        self.assertTrue(any("eleven missions" in f for f in failures), failures)

    def test_check_doc_counts_exempts_predecessor(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text(
                "Its predecessor shipped twelve missions with two proven.\n", encoding="utf-8")
            with mock.patch.object(validate, "ROOT", Path(tmp)), \
                 mock.patch.object(validate, "COUNT_LINT_FILES", ("README.md",)):
                self.assertEqual(validate.check_doc_counts(), [])

    def test_check_doc_counts_predecessor_after_count_still_flags(self):
        # The exemption is positional: a CURRENT catalog count followed by a predecessor
        # mention on the same line must still fail the lint.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text(
                "We now have 12 missions, improving on the predecessor's approach.\n",
                encoding="utf-8")
            with mock.patch.object(validate, "ROOT", Path(tmp)), \
                 mock.patch.object(validate, "COUNT_LINT_FILES", ("README.md",)):
                failures = validate.check_doc_counts()
        self.assertTrue(any("12 missions" in f for f in failures), failures)

    def test_check_manifest_keywords_flags_missing_mission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "plugin.json").write_text(
                '{"keywords": ["ship-it"]}', encoding="utf-8")
            skills = root / "skills"
            for m in ("ship-it", "new-mission"):
                (skills / m).mkdir(parents=True)
                (skills / m / "SKILL.md").write_text("x", encoding="utf-8")
            with mock.patch.object(validate, "ROOT", root), \
                 mock.patch.object(validate, "SKILLS_DIR", skills):
                failures = validate.check_manifest_keywords()
        self.assertTrue(any("new-mission" in f for f in failures), failures)
        self.assertFalse(any("ship-it" in f for f in failures), failures)

    def test_guards_pass_on_the_real_repo(self):
        # The valid corpus must be green on all three guards.
        self.assertEqual(validate.check_doc_counts(), [])
        self.assertEqual(validate.check_manifest_keywords(), [])
        self.assertEqual(validate.check_badge_freshness(), [])

    def test_badge_check_flags_stale(self):
        # tests.json is written CURRENT so the only error can come from missions.json's
        # staleness — a "missing file" error must not be able to satisfy this test.
        import json as _json
        spec = importlib.util.spec_from_file_location("_gb", ROOT / "scripts" / "gen-badges.py")
        gb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gb)
        current = gb.compute()
        with tempfile.TemporaryDirectory() as tmp:
            bd = Path(tmp) / "badges"
            bd.mkdir()
            (bd / "missions.json").write_text(
                '{"schemaVersion": 1, "label": "missions", "message": "999", "color": "1f6feb"}',
                encoding="utf-8")
            (bd / "tests.json").write_text(_json.dumps(current["tests.json"]), encoding="utf-8")
            with mock.patch.object(gb, "BADGES_DIR", bd):
                errs = gb.check()
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("missions.json", errs[0])
        self.assertIn("stale", errs[0])

    def test_badge_check_reports_missing_dirs_cleanly(self):
        # A fresh checkout without skills/ must produce an error string, not a traceback.
        spec = importlib.util.spec_from_file_location("_gb2", ROOT / "scripts" / "gen-badges.py")
        gb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gb)
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(gb, "SKILLS_DIR", Path(tmp) / "nope"):
                errs = gb.check()
        self.assertTrue(errs and "missing" in errs[0], errs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
