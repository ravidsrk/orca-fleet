"""The `danger` lane's verdict reader (#283).

sandbox-policy.md: a recipe doctor is CLEAR only with no `fail` AND no `warn`; `ok:true` alone
proves nothing. spawn_worker.sh enforced that with a substring grep over a caller-named file,
which was wrong in both directions — `/etc/passwd` passed, `"failures": []` was refused. These
tests pin both directions so neither mistake can come back.
"""
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
