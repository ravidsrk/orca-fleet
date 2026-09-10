#!/usr/bin/env python3
"""Contract tests for runtime/scripts/decisions.py.

Two properties carry the weight. First, the writer refuses what the log must
never hold: an unclassifiable decision, a pasted credential, or a one-way door
dressed as a mechanical auto-resolve. Second, the tally is deterministic —
two coordinators reading the same file must reach the same gate verdict.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "runtime" / "scripts" / "decisions.py"
DOORS = ROOT / "runtime" / "one-way-doors.json"


class DecisionsBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="decisions-")
        self.log = Path(self.tmp) / "docs" / "DECISIONS.md"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_dec(self, *args, log=None):
        return subprocess.run(
            [sys.executable, str(DECISIONS), "--file", str(log or self.log), *args],
            capture_output=True, text=True,
        )

    def append(self, ident, klass, answer, why, extra=()):
        return self.run_dec("append", "--id", ident, "--class", klass,
                            "--answer", answer, "--why", why, *extra)

    def seed(self, lines):
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.log.write_text(
            "# DECISIONS\n\n`ts · gate-or-ask-id · class · answer · why · task_id?`\n\n"
            + "\n".join(lines) + "\n", encoding="utf-8")


class TestAppendValidation(DecisionsBase):
    def test_valid_mechanical_line_is_written(self):
        r = self.append("gate-7", "mechanical", "retry", "transient network error, repo precedent")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.log.read_text(encoding="utf-8")
        self.assertIn("gate-7", text)
        self.assertIn(" · mechanical · ", text)

    def test_line_format_is_the_ledger_contract_shape(self):
        self.append("gate-7", "taste", "option-b", "reversible, matches the surrounding API",
                    extra=("--task", "t-3", "--ts", "2026-09-10T09:00:00Z"))
        line = [ln for ln in self.log.read_text(encoding="utf-8").splitlines() if "gate-7" in ln][0]
        fields = [f.strip() for f in line.split("·")]
        self.assertEqual(len(fields), 6)
        self.assertEqual(fields[0], "2026-09-10T09:00:00Z")
        self.assertEqual(fields[2], "taste")
        self.assertEqual(fields[5], "t-3")

    def test_task_id_is_optional(self):
        self.append("gate-8", "mechanical", "yes", "one defensible answer")
        line = [ln for ln in self.log.read_text(encoding="utf-8").splitlines() if "gate-8" in ln][0]
        self.assertEqual(len([f for f in line.split("·")]), 5)

    def test_unknown_class_is_refused_by_the_parser(self):
        r = self.append("gate-9", "vibes", "yes", "because")
        self.assertEqual(r.returncode, 2)

    def test_empty_why_is_refused(self):
        r = self.append("gate-10", "mechanical", "yes", "")
        self.assertEqual(r.returncode, 1)
        self.assertIn("empty why", r.stderr)

    def test_empty_answer_is_refused(self):
        r = self.append("gate-11", "mechanical", "", "a reason")
        self.assertEqual(r.returncode, 1)

    def test_separator_inside_a_field_is_refused(self):
        r = self.append("gate-12", "mechanical", "a · b", "one record, one line")
        self.assertEqual(r.returncode, 1)
        self.assertIn("one record, one line", r.stderr)

    def test_newline_inside_a_field_is_refused(self):
        r = self.append("gate-13", "mechanical", "a\nb", "one record, one line")
        self.assertEqual(r.returncode, 1)

    def test_nothing_is_written_when_the_append_is_refused(self):
        self.append("gate-14", "mechanical", "yes", "fine")
        before = self.log.read_text(encoding="utf-8")
        self.append("gate-15", "mechanical", "yes", "")
        self.assertEqual(self.log.read_text(encoding="utf-8"), before)


class TestSecretScan(DecisionsBase):
    def test_aws_key_shape_is_refused(self):
        r = self.append("gate-20", "mechanical", "use it", "key AKIAABCDEFGHIJKLMNOP works")
        self.assertEqual(r.returncode, 1)
        self.assertIn("credential-shaped", r.stderr)

    def test_private_key_block_is_refused(self):
        r = self.append("gate-21", "mechanical", "ok", "-----BEGIN RSA PRIVATE KEY----- pasted here")
        self.assertEqual(r.returncode, 1)

    def test_assigned_secret_is_refused(self):
        r = self.append("gate-22", "mechanical", "ok", "set api_key=abcdefghijklmnop1234")
        self.assertEqual(r.returncode, 1)

    def test_the_refusal_never_echoes_the_value(self):
        secret = "AKIAABCDEFGHIJKLMNOP"
        r = self.append("gate-23", "mechanical", "use it", f"key {secret} works")
        self.assertNotIn(secret, r.stderr + r.stdout)

    def test_ordinary_prose_is_not_a_secret(self):
        r = self.append("gate-24", "mechanical", "retry", "the token bucket refilled, so retry once")
        self.assertEqual(r.returncode, 0, r.stderr)


class TestOneWayNet(DecisionsBase):
    def test_a_net_match_classed_mechanical_is_refused(self):
        r = self.append("gate-30", "mechanical", "yes", "we should rotate the credentials now")
        self.assertEqual(r.returncode, 1)
        self.assertIn("one-way net", r.stderr)
        self.assertIn("secret-rotation", r.stderr)

    def test_a_net_match_classed_taste_is_refused(self):
        r = self.append("gate-31", "taste", "yes", "just merge to main and move on")
        self.assertEqual(r.returncode, 1)
        self.assertIn("merge-to-default", r.stderr)

    def test_one_way_without_a_human_source_is_refused(self):
        r = self.append("gate-32", "one-way", "approved", "deploy to production tonight")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no human source", r.stderr)

    def test_one_way_with_a_human_source_is_accepted(self):
        r = self.append("gate-33", "one-way", "approved", "deploy to production tonight",
                        extra=("--source", "human:maintainer"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("source=human:maintainer", self.log.read_text(encoding="utf-8"))

    def test_a_malformed_source_is_refused(self):
        r = self.append("gate-34", "one-way", "approved", "deploy to production",
                        extra=("--source", "the-boss"))
        self.assertEqual(r.returncode, 1)

    def test_every_door_id_can_be_tripped(self):
        doors = json.loads(DOORS.read_text(encoding="utf-8"))["doors"]
        for door in doors:
            with self.subTest(door=door["id"]):
                keyword = door["keywords"][0]
                r = self.append(f"gate-{door['id']}", "mechanical", "yes",
                                f"the plan is to {keyword} next")
                self.assertEqual(r.returncode, 1, f"{keyword!r} must trip {door['id']}")
                self.assertIn(door["id"], r.stderr)

    def test_missing_door_registry_is_a_could_not_run(self):
        r = self.run_dec("--doors", str(Path(self.tmp) / "nope.json"), "check")
        self.assertEqual(r.returncode, 2)
        self.assertIn("could not run", r.stderr)


class TestActive(DecisionsBase):
    def test_newest_line_for_an_id_wins(self):
        self.seed([
            "2026-09-01T00:00:00Z · gate-1 · taste · option-a · first pass · t-1",
            "2026-09-02T00:00:00Z · gate-1 · taste · option-b · reconsidered after review · t-1",
        ])
        r = self.run_dec("active")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("option-b", r.stdout)
        self.assertNotIn("option-a", r.stdout)

    def test_superseded_answer_retires_the_id(self):
        self.seed([
            "2026-09-01T00:00:00Z · gate-2 · taste · option-a · first pass · t-1",
            "2026-09-02T00:00:00Z · gate-2 · taste · superseded · the unit was dropped · t-1",
        ])
        r = self.run_dec("active")
        self.assertNotIn("gate-2", r.stdout)

    def test_distinct_ids_all_stay_active(self):
        self.seed([
            "2026-09-01T00:00:00Z · gate-3 · taste · a · why one · t-1",
            "2026-09-01T00:00:01Z · gate-4 · taste · b · why two · t-2",
        ])
        r = self.run_dec("active", "--json")
        self.assertEqual(len(json.loads(r.stdout)), 2)

    def test_prose_and_the_format_legend_are_not_records(self):
        self.seed(["2026-09-01T00:00:00Z · gate-5 · taste · a · why · t-1"])
        r = self.run_dec("active", "--json")
        rows = json.loads(r.stdout)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "gate-5")

    def test_missing_log_is_an_empty_active_set(self):
        r = self.run_dec("active")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


class TestTally(DecisionsBase):
    def _zeros(self, lens, n, then=None):
        lines = [f"2026-09-{i + 1:02d}T00:00:00Z · lens-tally:{lens} · mechanical · 0 · "
                 f"dispatch {i} found nothing · t-{i}" for i in range(n)]
        if then is not None:
            lines.append(f"2026-09-30T00:00:00Z · lens-tally:{lens} · mechanical · {then} · "
                         f"final dispatch · t-x")
        self.seed(lines)

    def test_zero_streak_is_counted_newest_first(self):
        self._zeros("a11y", 4)
        r = self.run_dec("tally", "--lens", "a11y", "--json")
        data = json.loads(r.stdout)
        self.assertEqual(data["zero_streak"], 4)
        self.assertEqual(data["dispatches"], 4)

    def test_a_nonzero_dispatch_resets_the_streak(self):
        self._zeros("a11y", 12, then="3")
        data = json.loads(self.run_dec("tally", "--lens", "a11y", "--json").stdout)
        self.assertEqual(data["zero_streak"], 0)
        self.assertFalse(data["may_gate_off"])

    def test_ten_zeros_earns_the_auto_gate_off(self):
        self._zeros("a11y", 10)
        data = json.loads(self.run_dec("tally", "--lens", "a11y", "--json").stdout)
        self.assertTrue(data["may_gate_off"])

    def test_nine_zeros_does_not(self):
        self._zeros("a11y", 9)
        data = json.loads(self.run_dec("tally", "--lens", "a11y", "--json").stdout)
        self.assertFalse(data["may_gate_off"])

    def test_security_never_gates_off(self):
        self._zeros("security", 40)
        data = json.loads(self.run_dec("tally", "--lens", "security", "--json").stdout)
        self.assertTrue(data["never_gate"])
        self.assertFalse(data["may_gate_off"], "the value of the security lens is the miss it catches")

    def test_data_migration_never_gates_off(self):
        self._zeros("data-migration", 40)
        data = json.loads(self.run_dec("tally", "--lens", "data-migration", "--json").stdout)
        self.assertFalse(data["may_gate_off"])

    def test_an_unknown_lens_reads_as_zero_dispatches(self):
        self._zeros("a11y", 3)
        data = json.loads(self.run_dec("tally", "--lens", "perf", "--json").stdout)
        self.assertEqual(data["dispatches"], 0)
        self.assertFalse(data["may_gate_off"])

    def test_appended_tallies_are_readable_by_tally(self):
        for i in range(3):
            self.append("lens-tally:perf", "mechanical", "0", f"dispatch {i} clean")
        data = json.loads(self.run_dec("tally", "--lens", "perf", "--json").stdout)
        self.assertEqual(data["zero_streak"], 3)

    def test_human_readable_tally_names_the_verdict(self):
        self._zeros("a11y", 10)
        r = self.run_dec("tally", "--lens", "a11y")
        self.assertIn("zero_streak=10", r.stdout)
        self.assertIn("auto-gate off", r.stdout)


class TestCheck(DecisionsBase):
    def test_a_clean_log_passes(self):
        self.seed([
            "2026-09-01T00:00:00Z · gate-1 · mechanical · retry · transient failure · t-1",
            "2026-09-02T00:00:00Z · gate-2 · one-way · approved · deploy to production "
            "[source=human:maintainer] · t-2",
        ])
        r = self.run_dec("check")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("2 record(s) valid", r.stdout)

    def test_a_mis_classified_one_way_line_fails(self):
        self.seed(["2026-09-01T00:00:00Z · gate-1 · mechanical · yes · rotate the secret today · t-1"])
        r = self.run_dec("check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("secret-rotation", r.stderr)

    def test_the_failure_names_the_line_number(self):
        self.seed([
            "2026-09-01T00:00:00Z · gate-1 · mechanical · yes · fine · t-1",
            "2026-09-02T00:00:00Z · gate-2 · nonsense · yes · fine · t-2",
        ])
        r = self.run_dec("check")
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stderr, r"DECISIONS\.md:\d+:")

    def test_an_empty_log_passes(self):
        self.seed([])
        r = self.run_dec("check")
        self.assertEqual(r.returncode, 0)

    def test_help_exits_zero(self):
        r = subprocess.run([sys.executable, str(DECISIONS), "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        for sub in ("append", "active", "tally", "check"):
            self.assertIn(sub, r.stdout)


class TestScriptShape(unittest.TestCase):
    def test_executable_and_shebanged(self):
        self.assertTrue(os.access(DECISIONS, os.X_OK))
        self.assertTrue(DECISIONS.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"))

    def test_default_log_path_is_the_ledger_contract_path(self):
        self.assertIn('DEFAULT_LOG = "docs/DECISIONS.md"', DECISIONS.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
