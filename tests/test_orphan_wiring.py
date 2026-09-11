"""Every mechanism the doctrine leans on is NAMED where its guarantee is stated (#284).

The 2026-09-11 review found seven scripts that ship, pass CI, and are invoked by nothing: zero
references across 21 missions and 28 playbooks. A guarantee backed by an uncalled script is
doctrine wearing a mechanism's clothes, and `guard_text.py:55-56` went further — it cited a
contract test that did not exist.

So each of these asserts the raw invocation is present in the document whose guarantee depends on
it. Deleting the line turns a test red, which is the whole point: the doc and the mechanism can no
longer drift apart silently.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
PLAYBOOKS = ROOT / "playbooks"
RUNTIME = ROOT / "runtime"


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class WiredMechanisms(unittest.TestCase):
    def test_guard_text_is_named_where_the_trust_boundary_is_stated(self):
        text = read("runtime/sandbox-policy.md")
        self.assertIn("guard_text.py", text,
                      "the trust boundary says external text is DATA and names no fence")
        self.assertIn("--fetch gh issue view", text, "the fence is named but not its invocation")

    def test_decisions_is_named_where_one_way_gates_are_stated(self):
        text = read("runtime/gate-classification.md")
        self.assertIn("decisions.py", text,
                      "one-way gates are doctrine with no ledger that enforces them")
        self.assertIn("--source human:", text)

    def test_floor_guard_is_named_by_floor_its_guard_step(self):
        text = read("skills/floor-it/SKILL.md")
        self.assertIn("floor_guard.py", text,
                      "floor-it describes check_constraints-style validation without naming it")

    def test_diff_scope_is_named_by_the_scope_gated_review(self):
        text = read("playbooks/risk-review.md")
        self.assertIn("diff_scope.py", text,
                      "risk-review gates lenses by prose, so a missed signal is silent")

    def test_diff_scope_is_the_verifiers_definition_of_a_test_path(self):
        # #280 gave diff_scope its first caller: verify.py binds the negative control's paths with
        # the same SCOPE_TESTS rule the lens gate uses, so the two cannot drift apart.
        self.assertIn("diff_scope", read("runtime/scripts/verify.py"))


class TheFenceIsTheOnlyPath(unittest.TestCase):
    """The contract test `guard_text.py`'s docstring has always claimed (#284).

    It said: "A contract test that greps missions and playbooks for raw `gh issue view` outside
    this script is what keeps the fence the only path." No such test existed. This is it.
    """

    # `gh pr view` is not the only way in: inline review comments come from `gh api …/comments`,
    # and a fence that covers one and not the other is not a fence (PR #308 review).
    RAW_FETCH = re.compile(r"gh\s+(?:issue|pr)\s+view\b|gh\s+api\b[^`\n]*(?:comments|issues|pulls)")

    def _offenders(self, directory):
        bad = []
        for path in sorted(directory.rglob("*.md")):
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not self.RAW_FETCH.search(line):
                    continue
                if "guard_text.py" in line:  # through the fence — the sanctioned form
                    continue
                bad.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:90]}")
        return bad

    def test_no_mission_fetches_tracker_text_outside_the_fence(self):
        self.assertEqual(self._offenders(SKILLS), [],
                         "a mission reads issue/PR text raw; route it through guard_text.py")

    def test_no_playbook_fetches_tracker_text_outside_the_fence(self):
        self.assertEqual(self._offenders(PLAYBOOKS), [],
                         "a playbook reads issue/PR text raw; route it through guard_text.py")

    def test_every_gh_api_list_fetch_paginates(self):
        # PR #308 review. `gh api` returns 30 items per page. verify.py:409 already carries the
        # lesson in a comment — "without it GitHub returns the first 30 reviews only" — and the
        # playbooks did not apply it, so a busy upstream PR silently truncates to its first page
        # and the WATCH loop reads that as the discussion going quiet.
        listing = re.compile(r"gh\s+api\b[^`\n]*/(?:comments|reviews|issues|pulls)\b")
        bad = []
        for directory in (SKILLS, PLAYBOOKS):
            for path in sorted(directory.rglob("*.md")):
                for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    for hit in listing.finditer(line):
                        if "--paginate" not in hit.group(0):
                            bad.append(f"{path.relative_to(ROOT)}:{i}: {hit.group(0)[:70]}")
        self.assertEqual(bad, [], "a list fetch without --paginate truncates at 30 items")


class TheVerifierInvocationIsWrittenDown(unittest.TestCase):
    """#285. The catalog's whole claim rests on verify.py, and no SKILL.md or playbook contained the
    string `--execute-nc`, `--nc-command` or `evidence-run.py`. The one place a verifier command line
    was written out was docs/runs/TEMPLATE.md — a template, not a pipeline. A coordinator following a
    mission end to end was told the outcome is verified and never told what verifies it.
    """

    def test_build_change_names_the_recorder(self):
        text = read("playbooks/build-change.md")
        self.assertIn("evidence-run.py", text,
                      "the BUILD phase produces evidence without naming the recorder that binds it")
        self.assertIn("--label", text)

    def test_build_change_names_the_verifier_and_its_lane_flags(self):
        text = read("playbooks/build-change.md")
        self.assertIn("verify.py", text)
        for flag in ("--contract-source", "--contract-digest", "--unit-class",
                     "--execute-nc", "--nc-command"):
            self.assertIn(flag, text, f"the invocation omits {flag}, so a coordinator must guess it")

    def test_the_invocation_says_the_coordinator_supplies_the_authorities(self):
        # The flags are worthless if a worker fills them in: that is #279 in one sentence.
        text = read("playbooks/build-change.md")
        self.assertIn("COORDINATOR", text)
        self.assertIn("never from the manifest", text)

    def test_the_evidence_contract_points_at_the_invocation(self):
        # evidence-manifest.md is ridden by all 21 missions and sits at both its caps, so it carries
        # a pointer rather than a copy — the shared-doctrine shape the playbook layer exists for.
        text = read("runtime/evidence-manifest.md")
        self.assertIn("build-change.md", text,
                      "the evidence contract says what is checked and never where to run it")


class DoctrineSaysWhatTheCatalogDoes(unittest.TestCase):
    """Four places where the doctrine had drifted from the catalog it describes (#289)."""

    def test_the_mission_test_is_six_part(self):
        # It counts six identity points; one guide still called it five.
        self.assertNotIn("five-part mission test", read("docs/missions/oss-contribute.md"))

    def test_modernize_it_hands_stateful_migration_to_migrate_it(self):
        # migrate-it landed 2026-09-10 and owns expand -> dual-write -> backfill -> switch ->
        # contract. modernize-it's handoff still pointed at a sequence of ship-it runs, so a
        # coordinator following it could not find the mission that does the work.
        text = read("skills/modernize-it/SKILL.md")
        self.assertIn("migrate-it", text,
                      "modernize-it describes a handoff without naming the mission that takes it")

    def test_the_rejection_ledger_records_what_was_admitted(self):
        # Its own footer asks for this: "when one lands or is dropped, record the outcome here".
        text = read("docs/research/REJECTED.md")
        self.assertIn("landed on", text.lower().replace("**", ""),
                      "the four 2026-09-10 admissions are not recorded in the ledger")

    def test_pin_it_is_argued_not_assumed(self):
        # #289 asked whether pin-it folds into clean-sweep. It does not, and ARCHITECTURE.md
        # already argued why; the number is what was missing.
        text = read("ARCHITECTURE.md")
        self.assertIn("finding is withdrawn", text)
        import importlib.util
        spec = importlib.util.spec_from_file_location("v", ROOT / "scripts" / "validate.py")
        validate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate)
        def identity(name):
            data, _err = validate.parse_frontmatter(
                (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8"))
            return data["metadata"]
        a, b = identity("clean-sweep"), identity("pin-it")
        near = sum(1 for k in validate.IDENTITY_KEYS
                   if validate._point_similarity(a[k], b[k]) >= validate.IDENTITY_POINT_NEAR)
        self.assertEqual(near, 0,
                         "clean-sweep and pin-it have started to converge; re-argue ARCHITECTURE.md")


class SharedDoctrineLivesOnce(unittest.TestCase):
    """#290. prove-it and reshape-it each wrote out the characterization protocol. Duplicated
    doctrine is the failure the playbook layer exists to prevent: two copies drift, and a reader
    cannot tell which is authoritative. reshape-it's reference was worse than a copy — it pointed
    at `skills/prove-it/SKILL.md` from inside a code block, which the composition scan cannot see,
    so the dependency was invisible to the load accounting and the orphan checks alike.
    """

    def test_the_characterize_playbook_exists(self):
        self.assertTrue((PLAYBOOKS / "characterize.md").is_file())

    def test_both_missions_compose_it_visibly(self):
        # Through the Composes clause, so validate.py counts it — not a path in a code block.
        import importlib.util
        spec = importlib.util.spec_from_file_location("v", ROOT / "scripts" / "validate.py")
        validate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate)
        for mission in ("prove-it", "reshape-it"):
            _total, parts = validate.transitive_load(SKILLS / mission)
            self.assertIn("playbooks/characterize.md", parts,
                          f"{mission} names characterize where the validator cannot see it")

    def test_the_mutation_rule_is_stated_once(self):
        # The load-bearing sentence — a compile break is not proof — belongs in the playbook, and
        # nowhere else restates the tool list it governs.
        playbook = read("playbooks/characterize.md")
        self.assertIn("a compile break is not proof", playbook.lower())
        for mission in ("prove-it", "reshape-it"):
            text = read(f"skills/{mission}/SKILL.md")
            self.assertNotIn("cargo-mutants", text,
                             f"{mission} still restates the mutation tool list characterize owns")

    def test_reshape_it_no_longer_points_into_another_skill_file(self):
        self.assertNotIn("skills/prove-it/SKILL.md", read("skills/reshape-it/SKILL.md"))

    def test_the_playbook_names_the_fields_the_verifier_reads(self):
        """A playbook that tells a worker what to record must name the SCHEMA fields, not describe
        them (PR #308 review). The first cut said "pinned mutant" and "target assertion" and left
        out `artifact` entirely — so a worker following the authoritative table would produce
        evidence verify.py refuses, and the shared playbook would be worse than the two copies it
        replaced.
        """
        playbook = read("playbooks/characterize.md")
        # Read the TABLE rows, not the whole file: every one of these words also appears in the
        # surrounding prose, so a substring check passes even with the row deleted. (Confirmed by
        # removing the artifact row and watching the first version of this test stay green.)
        rows = {line.split("|")[1].strip() for line in playbook.splitlines()
                if line.startswith("|") and line.count("|") >= 3}
        for field in ("tool", "mutant", "artifact", "result"):
            self.assertIn(f"`{field}`", rows,
                          f"characterize.md's record table has no row for negative_control.{field}")
        verifier = read("runtime/scripts/verify.py")
        self.assertIn('negative_control.artifact (an evidence path) is required', verifier,
                      "the verifier no longer requires artifact; re-check the playbook's table")
        self.assertIn("negative_control.mutant (a pinned mutant id) is required", verifier,
                      "the verifier no longer requires mutant; re-check the playbook's table")


class DormantMechanismsSaySo(unittest.TestCase):
    """Two of the seven cannot be wired from inside the repository, so they say so instead.

    #284 allows either: name the invocation, or remove the sentence claiming the guarantee holds.
    For these the second is the honest answer, and the honesty has to be pinned or it rots back.
    """

    def test_deny_hook_is_not_claimed_as_an_enforced_boundary(self):
        # It prints a registration a host must paste, and on the supervised lane nothing can.
        readme = read("README.md")
        self.assertIn("deny-hook.sh", readme)
        self.assertIn("unregistered by construction", readme,
                      "the README claims a boundary deny-hook.sh cannot enforce unregistered")

    def test_signed_dispatch_records_that_it_is_dormant(self):
        # The scheme is sound where the key is off-worker; no mission signs and no key is
        # committed, so nothing exercises it today.
        text = read("docs/verify-gate.md")
        self.assertIn("dispatch-sign.py", text)
        self.assertIn("no mission or playbook signs a dispatch", text,
                      "signed dispatch reads as live; no .orca/dispatch-pubkey is committed")

    def test_egress_records_that_it_has_no_caller(self):
        text = (RUNTIME / "scripts" / "egress.py").read_text(encoding="utf-8")
        self.assertIn("no caller", text,
                      "egress.py claims to receipt every off-repo write and nothing calls it")


if __name__ == "__main__":
    unittest.main()
