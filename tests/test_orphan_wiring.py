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
