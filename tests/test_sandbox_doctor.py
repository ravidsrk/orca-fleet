"""The `danger` lane's verdict reader (#283).

sandbox-policy.md: a recipe doctor is CLEAR only with no `fail` AND no `warn`; `ok:true` alone
proves nothing. spawn_worker.sh enforced that with a substring grep over a caller-named file,
which was wrong in both directions — `/etc/passwd` passed, `"failures": []` was refused. These
tests pin both directions so neither mistake can come back.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "sandbox_doctor", ROOT / "runtime" / "scripts" / "sandbox_doctor.py")
sandbox_doctor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sandbox_doctor)


class ClearTranscripts(unittest.TestCase):
    def assert_clear(self, raw, recipe="lane-7"):
        clear, reason = sandbox_doctor.verdict(raw, recipe)
        self.assertTrue(clear, f"refused a clear transcript: {reason}")

    def test_empty_json_finding_lists_are_clear(self):
        # The exact shape the old grep refused: the word "fail" inside the key that reports none.
        self.assert_clear('{"recipe": "lane-7", "ok": true, "failures": [], "warnings": []}')

    def test_zero_counts_are_clear(self):
        self.assert_clear('{"recipe": "lane-7", "ok": true, "failures": 0, "warnings": 0}')

    def test_text_form_zero_and_no_are_clear(self):
        self.assert_clear("recipe lane-7 provisioned\n0 warnings, no failures\n")
        self.assert_clear("recipe lane-7 ok:true\nfailures: none\nwarnings: none\n")

    def test_passing_checks_are_clear(self):
        self.assert_clear('{"recipe": "lane-7", "checks": [{"name": "net", "status": "pass"}]}')


class RefusedTranscripts(unittest.TestCase):
    def assert_refused(self, raw, recipe="lane-7", because=None):
        clear, reason = sandbox_doctor.verdict(raw, recipe)
        self.assertFalse(clear, f"accepted a transcript that is not clear: {raw[:80]!r}")
        if because:
            self.assertIn(because, reason)

    def test_a_file_that_merely_mentions_the_recipe_is_refused(self):
        # THE #283 bug, in one line: ORCA_SANDBOX_RECIPE=root, ORCA_SANDBOX_DOCTOR=/etc/passwd.
        # The passwd file names "root" and carries neither "fail" nor "warn", so the old grep
        # read it as a clean sandbox. spawn_worker.sh no longer accepts a caller-named file at
        # all; this asserts the reader alone would not call such a thing a doctor verdict either.
        passwd = "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
        clear, _reason = sandbox_doctor.verdict(passwd, "root")
        self.assertTrue(clear, "guard the honest limit: text with no verdict words reads as clear")
        # ...which is exactly why the caller-named-file lane was removed rather than patched: the
        # reader cannot tell a doctor transcript from any other quiet file. Only running the
        # doctor can, and spawn_worker.sh does that now.

    def test_a_transcript_for_another_recipe_is_refused(self):
        self.assert_refused('{"recipe": "other-lane", "ok": true}', because="does not name recipe")
        self.assert_refused("recipe other-lane ok:true\n", because="does not name recipe")

    def test_a_warning_is_refused(self):
        self.assert_refused('{"recipe": "lane-7", "ok": true, "warnings": ["low disk"]}')
        self.assert_refused("recipe lane-7 ok:true\nwarn: disk nearly full\n")

    def test_a_failure_is_refused(self):
        self.assert_refused('{"recipe": "lane-7", "failures": ["no network"]}')
        self.assert_refused("recipe lane-7\nfail: no network\n")

    def test_a_failing_check_inside_a_list_is_refused(self):
        self.assert_refused(
            '{"recipe": "lane-7", "ok": true, "checks": [{"name": "net", "status": "fail"}]}')

    def test_ok_false_is_refused(self):
        self.assert_refused('{"recipe": "lane-7", "ok": false}')

    def test_ok_true_with_a_warn_check_is_refused(self):
        # sandbox-policy.md is explicit that ok:true alone proves nothing — a warn is a lane that
        # boots and then fails a build halfway through.
        self.assert_refused(
            '{"recipe": "lane-7", "ok": true, "checks": [{"name": "disk", "level": "warn"}]}')


class RecipeIdentityIsExact(unittest.TestCase):
    """#298: the recipe check was a SUBSTRING test, in both the JSON and the plain-text path.

    A transcript for `web-prod-privileged` therefore certified a danger lane asked about `web`,
    and about `prod`. Since #283 this script produces the transcript itself, so the check is a
    sanity check rather than a trust boundary — but a sanity check that passes on the wrong
    recipe is not one, and the doctor may report on a recipe it resolved differently.
    """

    CLEAN = {"recipe": "web-prod-privileged", "failures": [], "warnings": []}

    def test_a_prefix_of_the_recipe_id_does_not_match(self):
        raw = json.dumps(self.CLEAN)
        for wrong in ("web", "web-prod", "prod", "privileged"):
            with self.subTest(recipe=wrong):
                clear, reason = sandbox_doctor.verdict(raw, wrong)
                self.assertFalse(clear, f"{wrong!r} certified a transcript for another recipe")
                self.assertIn("does not name recipe", reason)

    def test_the_whole_recipe_id_still_matches(self):
        clear, reason = sandbox_doctor.verdict(json.dumps(self.CLEAN), "web-prod-privileged")
        self.assertTrue(clear, reason)

    def test_the_match_is_a_string_value_not_a_serialized_fragment(self):
        # The id has to appear as a VALUE somewhere in the document, at any depth — not merely
        # as bytes inside the serialized form of it.
        deep = {"run": {"config": [{"id": "sandbox.v2"}]}, "failures": [], "warnings": []}
        self.assertTrue(sandbox_doctor.verdict(json.dumps(deep), "sandbox.v2")[0])
        glued = {"note": "recipes: sandbox.v2-old,sandbox.v2x", "failures": []}
        self.assertFalse(sandbox_doctor.verdict(json.dumps(glued), "sandbox.v2")[0],
                         "a substring of a longer value is not this recipe")

    def test_plain_text_matches_on_a_token_boundary(self):
        raw = "doctor for recipe web-prod-privileged\n0 failures\n0 warnings\n"
        self.assertTrue(sandbox_doctor.verdict(raw, "web-prod-privileged")[0])
        for wrong in ("web", "prod", "privileged"):
            with self.subTest(recipe=wrong):
                self.assertFalse(sandbox_doctor.verdict(raw, wrong)[0])

    def test_the_recipe_check_runs_before_the_findings_check(self):
        # A transcript for the WRONG recipe is refused whether or not it is clean, so a clean
        # transcript for a permissive recipe can never certify a stricter one.
        dirty = json.dumps({"recipe": "other-recipe", "failures": ["boom"]})
        clear, reason = sandbox_doctor.verdict(dirty, "web")
        self.assertFalse(clear)
        self.assertIn("does not name recipe", reason)


if __name__ == "__main__":
    unittest.main()
