#!/usr/bin/env python3
"""Contract tests for runtime/scripts/decisions.py.

Two properties carry the weight. First, the writer refuses what the log must
never hold: an unclassifiable decision, a pasted credential, or a one-way door
dressed as a mechanical auto-resolve. Second, the tally is deterministic —
two coordinators reading the same file must reach the same gate verdict.
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "runtime" / "scripts" / "decisions.py"
DOORS = ROOT / "runtime" / "one-way-doors.json"

_spec = importlib.util.spec_from_file_location("decisions", DECISIONS)
decisions = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(decisions)


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


class TestNeverGateMatchesThePolicy(unittest.TestCase):
    """The executable tuple and the sentence it implements cannot drift (PR #277 review).

    playbooks/risk-review.md named three NEVER_GATE lenses; decisions.py enforced two.
    Nothing failed — privacy simply became eligible to auto-gate off after ten quiet
    reviews, which is precisely the lens whose value is the miss it would catch. This
    test reads the policy sentence rather than restating it, so the next edit to either
    side has to move both.
    """

    def test_the_tuple_is_exactly_what_the_playbook_declares(self):
        text = (ROOT / "playbooks" / "risk-review.md").read_text(encoding="utf-8")
        m = re.search(r"([a-z,\s\-]+?)\s+are NEVER_GATE", text)
        self.assertIsNotNone(m, "risk-review.md no longer declares a NEVER_GATE list")
        declared = {
            w.strip() for w in m.group(1).replace(" and ", ",").replace("\n", " ").split(",")
            if w.strip()
        }
        self.assertEqual(
            declared, set(decisions.NEVER_GATE),
            f"risk-review.md declares {sorted(declared)} NEVER_GATE, decisions.py enforces "
            f"{sorted(decisions.NEVER_GATE)}",
        )

    def test_a_never_gate_lens_never_gates_off(self):
        # The behavioural property is exercised per lens in TestTally
        # (test_no_never_gate_lens_gates_off) — a membership re-assertion here
        # would prove nothing (the loop it replaces was tautological, #381).
        self.assertIn("privacy", decisions.NEVER_GATE)


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

    def test_an_out_of_order_line_does_not_become_the_active_one(self):
        # #318: "newest per id wins" resolved by FILE POSITION, never comparing ts. Any merge,
        # reorder or out-of-order append silently changed which decision was live — and a ledger
        # whose ordering guarantee is "whoever wrote last" is not a ledger.
        self.seed([
            "2026-09-02T00:00:00Z · gate-9 · taste · option-b · reconsidered · t-1",
            "2026-09-01T00:00:00Z · gate-9 · taste · option-a · first pass · t-1",
        ])
        r = self.run_dec("active")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("option-b", r.stdout, "the older line won on position alone")
        self.assertNotIn("option-a", r.stdout)

    def test_a_timezone_offset_is_compared_as_an_instant_not_as_text(self):
        # PR #308 review, P1. TS_PREFIX accepts anything starting with a date, so a record can
        # carry an offset — and `2026-09-11T01:00:00+05:00` IS `2026-09-10T20:00:00Z`, earlier
        # than `2026-09-11T00:00:00Z`. Compared as text it sorted later and the OLDER decision won.
        self.seed([
            "2026-09-11T01:00:00+05:00 · gate-12 · taste · option-old · = 2026-09-10T20:00Z · t-1",
            "2026-09-11T00:00:00Z · gate-12 · taste · option-new · genuinely later · t-1",
        ])
        r = self.run_dec("active")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("option-new", r.stdout, "an offset stamp beat a genuinely later UTC one")
        self.assertNotIn("option-old", r.stdout)

    def test_a_date_only_stamp_sorts_before_the_same_days_timed_ones(self):
        self.seed([
            "2026-09-11T00:00:01Z · gate-13 · taste · option-timed · one second in · t-1",
            "2026-09-11 · gate-13 · taste · option-dateonly · midnight · t-1",
        ])
        r = self.run_dec("active")
        self.assertIn("option-timed", r.stdout, r.stdout)

    def test_an_unreadable_stamp_never_displaces_a_readable_one(self):
        self.seed([
            "2026-09-01T00:00:00Z · gate-14 · taste · option-real · dated · t-1",
            "2026-13-45nonsense · gate-14 · taste · option-junk · unparseable · t-1",
        ])
        r = self.run_dec("active")
        self.assertIn("option-real", r.stdout, f"a junk stamp won on position: {r.stdout}")

    def test_identical_timestamps_fall_back_to_file_order(self):
        # Ties are real: two decisions can share a timestamp. Position is the tiebreak, which is
        # the old behaviour preserved exactly where it is the only information available.
        self.seed([
            "2026-09-01T00:00:00Z · gate-10 · taste · option-a · first · t-1",
            "2026-09-01T00:00:00Z · gate-10 · taste · option-b · second · t-1",
        ])
        r = self.run_dec("active")
        self.assertIn("option-b", r.stdout)
        self.assertNotIn("option-a", r.stdout)

    def test_an_out_of_order_supersede_still_retires_the_id(self):
        self.seed([
            "2026-09-02T00:00:00Z · gate-11 · taste · superseded · dropped · t-1",
            "2026-09-01T00:00:00Z · gate-11 · taste · option-a · first pass · t-1",
        ])
        r = self.run_dec("active")
        self.assertNotIn("gate-11", r.stdout)

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

    def test_no_never_gate_lens_gates_off(self):
        # The behavioural property over the whole tuple, not two named lenses (#381): a lens the
        # registry adds later inherits the refusal without anyone remembering a test.
        for lens in decisions.NEVER_GATE:
            with self.subTest(lens=lens):
                self._zeros(lens, 40)
                data = json.loads(self.run_dec("tally", "--lens", lens, "--json").stdout)
                self.assertTrue(data["never_gate"])
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


class DecisionsInProcBase(DecisionsBase):
    """Drive decisions.main() in-process: same argv, same assertions, no fork.

    The classes above prove the CLI over subprocess; these prove the same
    behavior calling main() directly, which is also what lets the coverage
    floor (CONSTRAINTS.md D9) observe the module instead of a child process.
    """

    def run_main(self, *args, log=None):
        argv = ["--file", str(log or self.log), *args]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = decisions.main(argv)
        return code, out.getvalue(), err.getvalue()


class TestParseLineUnits(unittest.TestCase):
    def test_format_then_parse_round_trips_all_fields(self):
        line = decisions.format_line("2026-09-10T09:00:00Z", "gate-7", "taste",
                                     "option-b", "reversible", "t-3")
        record = decisions.parse_line(line)
        self.assertEqual(record["ts"], "2026-09-10T09:00:00Z")
        self.assertEqual(record["id"], "gate-7")
        self.assertEqual(record["class"], "taste")
        self.assertEqual(record["answer"], "option-b")
        self.assertEqual(record["why"], "reversible")
        self.assertEqual(record["task_id"], "t-3")

    def test_missing_task_id_reads_as_empty(self):
        record = decisions.parse_line(
            decisions.format_line("2026-09-10T09:00:00Z", "g", "mechanical", "yes", "why"))
        self.assertEqual(record["task_id"], "")

    def test_the_format_legend_is_not_a_record(self):
        self.assertIsNone(decisions.parse_line(
            "`ts · gate-or-ask-id · class · answer · why · task_id?`"))

    def test_prose_and_short_lines_are_not_records(self):
        for line in ("# DECISIONS", "", "just a sentence", "2026-09-10 · only-two",
                     "- a bullet without a date · x · y · z · w"):
            with self.subTest(line=line):
                self.assertIsNone(decisions.parse_line(line))

    def test_a_backticked_stamp_is_unwrapped(self):
        record = decisions.parse_line("`2026-09-10T09:00:00Z` · g · mechanical · yes · why · t-1")
        self.assertIsNotNone(record)
        self.assertEqual(record["ts"], "2026-09-10T09:00:00Z")

    def test_a_leading_bullet_is_stripped(self):
        record = decisions.parse_line("- 2026-09-10T09:00:00Z · g · mechanical · yes · why · t-1")
        self.assertIsNotNone(record)
        self.assertEqual(record["id"], "g")

    def test_extra_separators_fold_into_why_with_the_last_as_task(self):
        record = decisions.parse_line(
            "2026-09-10T09:00:00Z · g · mechanical · yes · first part · second part · t-9")
        self.assertIsNotNone(record)
        self.assertIn("first part", record["why"])
        self.assertIn("second part", record["why"])
        self.assertEqual(record["task_id"], "t-9")


class TestValidateUnits(unittest.TestCase):
    def _record(self, ident="g", klass="mechanical", answer="yes", why="a reason"):
        return decisions.parse_line(
            decisions.format_line("2026-09-10T09:00:00Z", ident, klass, answer, why, "t-1"))

    def test_a_clean_record_has_no_problems(self):
        self.assertEqual(decisions.validate(self._record(), []), [])

    def test_empty_id_answer_and_why_are_each_reported(self):
        self.assertTrue(any("empty gate-or-ask id" in p
                            for p in decisions.validate(self._record(ident=""), [])))
        self.assertTrue(any("empty answer" in p
                            for p in decisions.validate(self._record(answer=""), [])))
        self.assertTrue(any("empty why" in p
                            for p in decisions.validate(self._record(why=""), [])))

    def test_an_unknown_class_is_reported(self):
        problems = decisions.validate(self._record(klass="vibes"), [])
        self.assertTrue(any("vibes" in p and "mechanical" in p for p in problems))

    def test_every_secret_shape_is_named_never_echoed(self):
        # Halves, never the contiguous literal: this file is committed, and the
        # secret scan reads committed bytes. Each half is inert; the joined
        # runtime string is what the shape matcher sees.
        shapes = {
            "aws-access-key": ("AKIA", "IOSFODNN7EXAMPLE"),
            "github-token": ("ghp_", "abcdefghij1234567890"),
            "slack-token": ("xoxb-", "123456789012"),
            "private-key-block": ("-----BEGIN RSA PRIVATE ", "KEY-----"),
            "bearer-literal": ("Bearer ", "abcdefghij1234567890"),
            "provider-secret-key": ("sk-", "abcdefghij1234567890"),
            "assigned-secret": ("api" + "_key", "=" + "abcdefghijklmnop1234"),
        }
        for name, (left, right) in shapes.items():
            with self.subTest(shape=name):
                value = left + right
                problems = decisions.validate(self._record(why=f"pasted {value} here"), [])
                hit = [p for p in problems if "credential-shaped" in p]
                self.assertEqual(len(hit), 1, f"{name} was not refused: {problems}")
                self.assertIn(name, hit[0])
                self.assertNotIn(value, hit[0])

    def test_secret_hits_are_sorted_shape_names(self):
        value = "AKIA" + "IOSFODNN7EXAMPLE"
        self.assertEqual(decisions.secret_hits(f"key {value} here"), ["aws-access-key"])
        self.assertEqual(decisions.secret_hits("the token bucket refilled"), [])

    def test_a_net_match_classed_mechanical_names_the_door(self):
        net = decisions.load_doors()
        self.assertTrue(net, "the default door registry loaded empty")
        door_id = net[0][0]
        keyword = next(kw for did, kw in net if did == door_id)
        problems = decisions.validate(
            self._record(why=f"the plan is to {keyword} next"), net)
        self.assertTrue(any(door_id in p and "one-way net" in p for p in problems), problems)

    def test_a_net_match_classed_one_way_with_source_is_clean(self):
        net = decisions.load_doors()
        keyword = net[0][1]
        record = self._record(klass="one-way", answer="approved",
                              why=f"we will {keyword} [source=human:maintainer]")
        self.assertEqual(decisions.validate(record, net), [])

    def test_one_way_without_a_human_source_is_reported(self):
        problems = decisions.validate(
            self._record(klass="one-way", answer="approved", why="a plain reason"), [])
        self.assertTrue(any("no human source" in p for p in problems), problems)

    def test_door_hits_fold_case_and_sort(self):
        net = [("b-door", "alpha"), ("a-door", "beta")]
        self.assertEqual(decisions.door_hits("ALPHA and  beta", net), ["a-door", "b-door"])
        self.assertEqual(decisions.door_hits("nothing relevant", net), [])

    def test_fold_collapses_whitespace_and_case(self):
        self.assertEqual(decisions.fold("  Merge\n\tTo   MAIN "), "merge to main")


class TestOrderingUnits(unittest.TestCase):
    def test_z_suffix_and_lowercase_z_read_as_utc(self):
        upper = decisions._instant("2026-09-11T00:00:00Z")
        lower = decisions._instant("2026-09-11T00:00:00z")
        self.assertEqual(upper, lower)
        self.assertIsNotNone(upper.tzinfo)

    def test_an_offset_is_compared_as_an_instant(self):
        offset = decisions._instant("2026-09-11T01:00:00+05:00")
        utc = decisions._instant("2026-09-11T00:00:00Z")
        self.assertLess(offset, utc)

    def test_a_naive_stamp_is_read_as_utc(self):
        moment = decisions._instant("2026-09-11")
        self.assertIsNotNone(moment.tzinfo)
        self.assertEqual(moment, decisions._instant("2026-09-11T00:00:00Z"))

    def test_an_unparseable_stamp_sorts_before_everything(self):
        self.assertEqual(decisions._instant("2026-13-45nonsense"), decisions._UNDATED)
        self.assertEqual(decisions._instant(""), decisions._UNDATED)

    def test_recency_breaks_timestamp_ties_by_position(self):
        record = {"ts": "2026-09-01T00:00:00Z"}
        self.assertLess(decisions.recency(record, 0), decisions.recency(record, 1))

    def test_active_prefers_newest_by_instant_not_position(self):
        def rec(ts, answer):
            return {"ts": ts, "id": "g", "answer": answer}
        rows = decisions.active([rec("2026-09-02T00:00:00Z", "new"),
                                 rec("2026-09-01T00:00:00Z", "old")])
        self.assertEqual([r["answer"] for r in rows], ["new"])

    def test_active_retires_a_mixed_case_superseded(self):
        def rec(ts, answer):
            return {"ts": ts, "id": "g", "answer": answer}
        rows = decisions.active([rec("2026-09-01T00:00:00Z", "option-a"),
                                 rec("2026-09-02T00:00:00Z", "Superseded")])
        self.assertEqual(rows, [])

    def test_tally_counts_only_the_trailing_zero_run(self):
        def rec(day, answer):
            return {"ts": f"2026-09-{day:02d}T00:00:00Z", "id": "lens-tally:perf",
                    "answer": answer}
        rows = [rec(1, "0"), rec(2, "2"), rec(3, "0"), rec(4, "00")]
        result = decisions.tally(rows, "perf")
        self.assertEqual(result["dispatches"], 4)
        self.assertEqual(result["zero_streak"], 2)
        self.assertFalse(result["never_gate"])
        self.assertFalse(result["may_gate_off"])

    def test_tally_gates_off_at_ten_for_a_gating_lens(self):
        rows = [{"ts": f"2026-09-{d:02d}T00:00:00Z", "id": "lens-tally:a11y", "answer": "0"}
                for d in range(1, 11)]
        result = decisions.tally(rows, "a11y")
        self.assertTrue(result["may_gate_off"])
        self.assertEqual(decisions.tally(rows, "security")["dispatches"], 0)


class TestLoadDoorsUnits(unittest.TestCase):
    def test_the_default_registry_loads_a_nonempty_net(self):
        net = decisions.load_doors()
        self.assertTrue(net)
        door_ids = {did for did, _kw in net}
        declared = {d["id"] for d in json.loads(DOORS.read_text(encoding="utf-8"))["doors"]}
        self.assertEqual(door_ids, declared)

    def test_an_explicit_registry_path_is_honored(self):
        with tempfile.TemporaryDirectory(prefix="doors-") as tmp:
            reg = Path(tmp) / "doors.json"
            reg.write_text(json.dumps({"doors": [{"id": "d", "keywords": ["Kw"]}]}),
                           encoding="utf-8")
            self.assertEqual(decisions.load_doors(str(reg)), [("d", "kw")])

    def test_a_missing_registry_is_a_could_not_run(self):
        with self.assertRaises(decisions.DecisionsError):
            decisions.load_doors("/nonexistent/doors.json")

    def test_invalid_json_is_a_could_not_run(self):
        with tempfile.TemporaryDirectory(prefix="doors-") as tmp:
            reg = Path(tmp) / "doors.json"
            reg.write_text("{nope", encoding="utf-8")
            with self.assertRaises(decisions.DecisionsError):
                decisions.load_doors(str(reg))

    def test_a_registry_with_no_doors_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="doors-") as tmp:
            reg = Path(tmp) / "doors.json"
            reg.write_text(json.dumps({"doors": []}), encoding="utf-8")
            with self.assertRaises(decisions.DecisionsError):
                decisions.load_doors(str(reg))

    def test_a_door_without_a_keyword_net_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="doors-") as tmp:
            reg = Path(tmp) / "doors.json"
            for bad in ({"id": "d"}, {"id": "d", "keywords": []}, {"keywords": ["x"]}):
                reg.write_text(json.dumps({"doors": [bad]}), encoding="utf-8")
                with self.subTest(door=bad), self.assertRaises(decisions.DecisionsError):
                    decisions.load_doors(str(reg))


class TestMainInProc(DecisionsInProcBase):
    def test_append_writes_the_header_once_then_the_line(self):
        code, out, err = self.run_main("append", "--id", "g-1", "--class", "mechanical",
                                       "--answer", "yes", "--why", "one defensible answer",
                                       "--ts", "2026-09-10T09:00:00Z")
        self.assertEqual(code, 0, err)
        text = self.log.read_text(encoding="utf-8")
        self.assertEqual(text.count("# DECISIONS"), 1)
        self.assertIn("2026-09-10T09:00:00Z · g-1 · mechanical · yes", out)
        self.run_main("append", "--id", "g-2", "--class", "taste",
                      "--answer", "b", "--why", "reversible")
        self.assertEqual(self.log.read_text(encoding="utf-8").count("# DECISIONS"), 1)

    def test_append_adds_the_source_marker_once(self):
        code, _out, err = self.run_main(
            "append", "--id", "g-3", "--class", "one-way", "--answer", "approved",
            "--why", "deploy [source=human:lia]", "--source", "human:lia")
        self.assertEqual(code, 0, err)
        text = self.log.read_text(encoding="utf-8")
        self.assertEqual(text.count("source=human:lia"), 1)

    def test_append_refuses_a_malformed_source(self):
        code, _out, err = self.run_main(
            "append", "--id", "g-4", "--class", "one-way", "--answer", "approved",
            "--why", "deploy", "--source", "lia")
        self.assertEqual(code, 1)
        self.assertIn("--source must be shaped human:<name>", err)

    def test_append_refuses_a_separator_or_newline_in_any_field(self):
        for field, value in (("--id", "a · b"), ("--answer", "a\nb"),
                             ("--why", "has · sep"), ("--task", "t\n1")):
            with self.subTest(field=field):
                code, _out, err = self.run_main(
                    "append", "--id", "g", "--class", "mechanical",
                    "--answer", "yes", "--why", "why", field, value)
                self.assertEqual(code, 1)
                self.assertIn("one record, one line", err)

    def test_append_refuses_an_undated_line_as_unparseable(self):
        code, _out, err = self.run_main(
            "append", "--id", "g", "--class", "mechanical", "--answer", "yes",
            "--why", "why", "--ts", "not-a-date")
        self.assertEqual(code, 1)
        self.assertIn("unparseable", err)

    def test_append_refuses_and_names_a_validation_failure(self):
        code, _out, err = self.run_main(
            "append", "--id", "g", "--class", "mechanical", "--answer", "yes", "--why", "")
        self.assertEqual(code, 1)
        self.assertIn("refused", err)
        self.assertIn("empty why", err)

    def test_append_below_a_regular_file_is_a_could_not_run(self):
        blocker = Path(self.tmp) / "blocker"
        blocker.write_text("a file, not a directory", encoding="utf-8")
        code, _out, err = self.run_main(
            "append", "--id", "g", "--class", "mechanical", "--answer", "yes",
            "--why", "why", log=str(blocker / "DECISIONS.md"))
        self.assertEqual(code, 2)
        self.assertIn("could not run", err)

    def test_active_json_carries_the_record_shape(self):
        self.seed(["2026-09-01T00:00:00Z · gate-5 · taste · a · why · t-1"])
        code, out, err = self.run_main("active", "--json")
        self.assertEqual(code, 0, err)
        (row,) = json.loads(out)
        self.assertEqual(row, {"ts": "2026-09-01T00:00:00Z", "id": "gate-5",
                               "class": "taste", "answer": "a", "why": "why",
                               "task_id": "t-1"})

    def test_tally_human_readable_names_all_three_verdicts(self):
        def seed(lens, n):
            self.seed([f"2026-09-{i + 1:02d}T00:00:00Z · lens-tally:{lens} · mechanical · 0 · "
                       f"dispatch {i} clean · t-{i}" for i in range(n)])
        seed("a11y", 10)
        code, out, err = self.run_main("tally", "--lens", "a11y")
        self.assertEqual(code, 0, err)
        self.assertIn("may auto-gate off", out)
        seed("security", 40)
        _code, out, _err = self.run_main("tally", "--lens", "security")
        self.assertIn("NEVER_GATE", out)
        seed("perf", 3)
        _code, out, _err = self.run_main("tally", "--lens", "perf")
        self.assertIn("stays on", out)

    def test_check_reports_each_failure_with_its_line(self):
        self.seed(["2026-09-01T00:00:00Z · gate-1 · nonsense · yes · fine · t-1"])
        code, _out, err = self.run_main("check")
        self.assertEqual(code, 1)
        self.assertRegex(err, r":5: class 'nonsense'")

    def test_a_broken_door_registry_is_exit_2_through_main(self):
        code, _out, err = self.run_main("--doors", str(Path(self.tmp) / "nope.json"), "check")
        self.assertEqual(code, 2)
        self.assertIn("could not run", err)

    def test_a_directory_as_the_log_is_exit_2(self):
        code, _out, err = self.run_main("check", log=str(Path(self.tmp)))
        self.assertEqual(code, 2)
        self.assertIn("could not run", err)

    def test_active_on_a_missing_log_is_empty_in_process(self):
        code, out, err = self.run_main("active")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "")

    def test_append_stamps_a_fresh_source_marker(self):
        code, _out, err = self.run_main(
            "append", "--id", "g-5", "--class", "one-way", "--answer", "approved",
            "--why", "deploy tonight", "--source", "human:lia")
        self.assertEqual(code, 0, err)
        self.assertIn("[source=human:lia]",
                      [ln for ln in self.log.read_text(encoding="utf-8").splitlines()
                       if "g-5" in ln][0])

    def test_active_plain_prints_the_raw_records(self):
        self.seed(["2026-09-01T00:00:00Z · gate-6 · taste · a · why · t-1"])
        code, out, err = self.run_main("active")
        self.assertEqual(code, 0, err)
        self.assertIn("2026-09-01T00:00:00Z · gate-6 · taste · a · why · t-1", out)

    def test_tally_json_carries_the_gate_verdict(self):
        self.seed(["2026-09-01T00:00:00Z · lens-tally:a11y · mechanical · 0 · clean · t-1"])
        code, out, err = self.run_main("tally", "--lens", "a11y", "--json")
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual((data["lens"], data["zero_streak"], data["may_gate_off"]),
                         ("a11y", 1, False))

    def test_an_argparse_rejection_exits_2_through_system_exit(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                decisions.main(["--file", str(self.log), "append", "--id", "g",
                                "--class", "vibes", "--answer", "y", "--why", "w"])
        self.assertEqual(ctx.exception.code, 2)

    def test_the_module_entry_point_runs_check_and_exits_zero(self):
        self.seed(["2026-09-01T00:00:00Z · gate-1 · mechanical · yes · fine · t-1"])
        argv = ["decisions.py", "--file", str(self.log), "check"]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch.object(sys, "argv", argv):
                with self.assertRaises(SystemExit) as ctx:
                    runpy.run_path(str(DECISIONS), run_name="__main__")
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("1 record(s) valid", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
canary_api_key = "9f86d081884c7d659a2feaa0c55ad015a2f3b4c5"
