#!/usr/bin/env python3
"""Contract tests for runtime/scripts/gate-batch.py (#419).

Human gates used to be hand-appended prose in a run's gate-batch.md — no
schema, no state machine, and a renumbered gate silently orphaned every
parked-unit citation. The tool stores typed records; these tests pin the
state machine (owed moves exactly once), the staleness boundary, the
2026-09-14 migration's byte-identical round-trip, and the warn-not-error
citation check.
"""
import datetime
import importlib.util
import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "gate_batch", ROOT / "runtime" / "scripts" / "gate-batch.py")
gb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gb)

RUN_DIR = ROOT / "docs" / "runs" / "2026-09-14-clean-sweep-tracker"
REAL_JSON = RUN_DIR / "gate-batch.json"
REAL_MD = RUN_DIR / "gate-batch.md"
SCHEMA = ROOT / "runtime" / "schemas" / "gate-batch.schema.json"


def fresh_batch(tmp, **kwargs):
    path = Path(tmp) / "gate-batch.json"
    kwargs.setdefault("run_id", "run_test")
    kwargs.setdefault("run_title", "test run")
    return path, gb.init_batch(path, **kwargs)


def add_owed(data, gid="G1", asked="2026-09-14", **kwargs):
    kwargs.setdefault("title", f"ask {gid}")
    kwargs.setdefault("question", f"the question {gid}")
    return gb.add_gate(data, gid=gid, asked=asked, **kwargs)


class StateTransitions(unittest.TestCase):
    def test_add_creates_an_owed_gate_with_the_next_auto_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, data = fresh_batch(tmp)
            g1 = gb.add_gate(data, title="first", question="q1")
            g2 = gb.add_gate(data, title="second", question="q2")
            self.assertEqual((g1["id"], g1["status"]), ("G1", "owed"))
            self.assertEqual((g2["id"], g2["status"]), ("G2", "owed"))
            self.assertIsNone(g1["answer"])
            self.assertIsNone(g1["answered"])
            gb.save_batch(path, data)
            self.assertEqual(gb.load_batch(path)["gates"], data["gates"])

    def test_add_with_a_duplicate_id_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1")
            with self.assertRaises(gb.GateError):
                add_owed(data, "G1")

    def test_answer_moves_owed_to_answered_with_text_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1", asked="2026-09-14")
            gate = gb.transition(data, "G1", "answered", "the vault holds it",
                                 answered="2026-09-15")
            self.assertEqual(gate["status"], "answered")
            self.assertEqual(gate["answer"], "the vault holds it")
            self.assertEqual(gate["answered"], "2026-09-15")

    def test_waive_moves_owed_to_waived_with_the_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G3", asked="2026-09-14")
            gate = gb.transition(data, "G3", "waived", "blind verdict suffices",
                                 answered="2026-09-16")
            self.assertEqual((gate["status"], gate["answer"]),
                             ("waived", "blind verdict suffices"))

    def test_overtake_needs_no_note_when_the_body_says_why(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G4", asked="2026-09-14",
                     question="built before the pick; disclosed for the record")
            gate = gb.transition(data, "G4", "overtaken", None,
                                 answered="2026-09-14")
            self.assertEqual(gate["status"], "overtaken")
            self.assertIsNone(gate["answer"])

    def test_a_answered_gate_never_moves_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1", asked="2026-09-14")
            gb.transition(data, "G1", "answered", "yes", answered="2026-09-15")
            for status, text in (("answered", "second"), ("waived", "moot"),
                                 ("overtaken", None)):
                with self.subTest(status=status):
                    with self.assertRaises(gb.GateError):
                        gb.transition(data, "G1", status, text,
                                      answered="2026-09-16")
            self.assertEqual(
                gb.find_gate(data, "G1")["answer"], "yes",
                "the failed re-transition must not touch the record")

    def test_transitioning_an_unknown_gate_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1")
            with self.assertRaises(gb.GateError):
                gb.transition(data, "G9", "answered", "yes",
                              answered="2026-09-15")

    def test_a_recorded_date_before_asked_is_refused_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1", asked="2026-09-14")
            with self.assertRaises(gb.GateError):
                gb.transition(data, "G1", "answered", "yes",
                              answered="2026-09-13")
            gate = gb.find_gate(data, "G1")
            self.assertEqual(gate["status"], "owed")
            self.assertIsNone(gate["answered"])

    def test_answer_and_waive_without_text_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1", asked="2026-09-14")
            add_owed(data, "G2", asked="2026-09-14")
            with self.assertRaises(gb.GateError):
                gb.transition(data, "G1", "answered", "  ",
                              answered="2026-09-15")
            with self.assertRaises(gb.GateError):
                gb.transition(data, "G2", "waived", "", answered="2026-09-15")
            self.assertEqual(gb.find_gate(data, "G1")["status"], "owed")


class StaleBoundary(unittest.TestCase):
    ASKED = "2026-09-10"

    def _stale_ids(self, today, days):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1", asked=self.ASKED)
            return [g["id"] for g, _ in
                    gb.stale_gates(data, days, datetime.date(*today))]

    def test_a_gate_owed_n_minus_1_days_is_quiet(self):
        # Asked 09-10, today 09-16: 6 days owed against --days 7.
        self.assertEqual(self._stale_ids((2026, 9, 16), 7), [])

    def test_a_gate_owed_exactly_n_days_is_flagged(self):
        # Asked 09-10, today 09-17: 7 days owed against --days 7.
        self.assertEqual(self._stale_ids((2026, 9, 17), 7), ["G1"])

    def test_a_settled_gate_is_never_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp)
            add_owed(data, "G1", asked="2026-01-01")
            gb.transition(data, "G1", "answered", "long ago",
                          answered="2026-01-02")
            self.assertEqual(
                gb.stale_gates(data, 7, datetime.date(2026, 9, 17)), [])


def _parse_legacy_md(text):
    """Split a hand-written batch into (run_id, run_title, intro, gates, resolved).

    Test-only: the migration ran once through the CLI; this replays the md->json
    direction so the round-trip test does not trust the committed JSON alone.
    """
    body = text[:-1]  # the file ends in exactly one newline
    m = re.match(r"# Run-close human-gate batch \u2014 (\S+) \((.*)\)\n"
                 r"\n(.*?)\n\n(## G1 .*)\Z", body, re.S)
    run_id, run_title, intro, rest = m.groups()
    gates, resolved = [], ""
    for chunk in re.split(r"\n(?=## )", rest):
        head, _, qbody = chunk.partition("\n\n")
        if head.startswith("## Resolved"):
            resolved = qbody
            continue
        gid, title = re.match(r"## (G[0-9]+) \u00b7 (.*)", head).groups()
        # The CLI rstrips ingested prose; the replay honors the same rule.
        gates.append((gid, title, qbody.rstrip("\n")))
    return run_id, run_title, intro, gates, resolved


# The migration's store-only judgments: what each gate relates to and blocks,
# and G4's overtaken status (its heading says it: the question was resolved
# by events before the human replied). Pinned here, not re-derived.
MIGRATED_META = {
    "G1": {"asked": "2026-09-14", "status": "owed", "related": ["#386"],
           "blocking": ["#386"], "answer": None, "answered": None},
    "G2": {"asked": "2026-09-14", "status": "owed", "related": ["#397"],
           "blocking": [], "answer": None, "answered": None},
    "G3": {"asked": "2026-09-14", "status": "owed",
           "related": ["#392", "#391", "#395", "#400", "#402", "#403", "#401",
                       "#404"], "blocking": [], "answer": None,
           "answered": None},
    "G4": {"asked": "2026-09-14", "status": "overtaken", "related": ["#364"],
           "blocking": [], "answer": None, "answered": "2026-09-14"},
}


def _rebuild_from_md(md_text):
    run_id, run_title, intro, gates, resolved = _parse_legacy_md(md_text)
    data = {"schema": gb.SCHEMA_TAG, "run_id": run_id, "run_title": run_title,
            "intro": intro, "gates": [], "resolved_by_events": resolved}
    for gid, title, question in gates:
        meta = MIGRATED_META[gid]
        gb.add_gate(data, gid=gid, title=title, question=question,
                    asked=meta["asked"], related=meta["related"],
                    blocking=meta["blocking"])
    for gid, meta in MIGRATED_META.items():
        if meta["status"] != "owed":
            gb.transition(data, gid, meta["status"], meta["answer"],
                          answered=meta["answered"])
    return data


class MigrationRoundTrip(unittest.TestCase):
    def test_the_real_batch_round_trips_byte_identical(self):
        md_text = REAL_MD.read_text(encoding="utf-8")
        rebuilt = _rebuild_from_md(md_text)
        self.assertEqual(
            rebuilt, json.loads(REAL_JSON.read_text(encoding="utf-8")),
            "the committed JSON is not what the committed .md migrates to")
        self.assertEqual(
            gb.render_batch(rebuilt), md_text,
            "md -> json -> md lost or added a byte")
        committed = json.loads(REAL_JSON.read_text(encoding="utf-8"))
        gb.validate_batch(committed)
        self.assertEqual(gb.render_batch(committed), md_text)

    def test_recorded_answer_text_renders_as_an_annotation(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, data = fresh_batch(tmp, run_id="r", run_title="t",
                                  intro="i")
            add_owed(data, "G1", asked="2026-09-14", title="ask",
                     question="q?")
            gb.transition(data, "G1", "answered", "yes", answered="2026-09-15")
            rendered = gb.render_batch(data)
            self.assertIn("**Answered 2026-09-15:** yes", rendered)
            self.assertIn("q?", rendered.split("**Answered")[0])


class DanglingCitationsWarn(unittest.TestCase):
    def _run_dir_with(self, tmp, cited_text):
        path = Path(tmp) / "gate-batch.json"
        data = gb.init_batch(path, run_id="r", run_title="t")
        add_owed(data, "G1")
        gb.save_batch(path, data)
        (Path(tmp) / "u1-manifest.json").write_text(
            json.dumps({"note": cited_text}), encoding="utf-8")
        return path

    def test_a_manifest_citing_an_unknown_gate_warns_but_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._run_dir_with(
                tmp, "parked needs-human, ref gate-batch.json G9")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = gb.main(["--file", str(path), "list"])
            self.assertEqual(code, 0)
            self.assertIn("G9", err.getvalue())
            self.assertIn("u1-manifest.json", err.getvalue())
            self.assertIn("G1 [owed]", out.getvalue())

    def test_known_ids_and_bare_prose_never_warn(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._run_dir_with(
                tmp, "ref gate-batch.json G1; the G9 ASK body was reworded; "
                     "see gate-batch.md G1 too")
            data = gb.load_batch(path)
            self.assertEqual(gb.check_citations(data, Path(tmp)), [])

    def test_the_real_run_dir_is_citation_clean(self):
        data = gb.load_batch(REAL_JSON)
        self.assertEqual(gb.check_citations(data, RUN_DIR), [])

    def test_line_anchored_and_range_citations_resolve(self):
        # Forms the 2026-09-14 corpus actually uses: drain-387-threads cites
        # "gate-batch.md:22 (G2 ...)", the run report "gate-batch.md G1-G4".
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "u1-manifest.json").write_text(
                json.dumps({"a": "4012708598 gate-batch.md:22 (G2 branch)",
                            "b": "wrote gate-batch.md G1-G4 at close"}),
                encoding="utf-8")
            cited = gb.cited_gate_ids(Path(tmp))
            self.assertEqual(set(cited), {"G1", "G2", "G4"})
            self.assertEqual(cited["G2"], ["u1-manifest.json"])


class HelpAndWiring(unittest.TestCase):
    SUBCOMMANDS = ("init", "add", "answer", "waive", "overtake", "list",
                   "stale", "show", "render")

    def test_every_subcommand_help_carries_an_example(self):
        for sub in self.SUBCOMMANDS:
            with self.subTest(subcommand=sub):
                out = io.StringIO()
                with redirect_stdout(out), self.assertRaises(SystemExit) as cm:
                    gb.main([sub, "--help"])
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("example:", out.getvalue())

    def test_conductor_close_names_the_mechanism(self):
        # Orphan-wiring philosophy (#284): the close playbook's gate rule is
        # doctrine wearing a mechanism's clothes unless it names the tool.
        text = (ROOT / "playbooks" / "conductor-close.md").read_text(
            encoding="utf-8")
        self.assertIn("gate-batch.py", text)
        self.assertIn("stale", text)
        self.assertIn("overtaken", text)

    def test_the_schema_file_and_the_module_agree(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        enum = schema["$defs"]["gate"]["properties"]["status"]["enum"]
        self.assertEqual(enum, list(gb.STATUSES))
        required = schema["$defs"]["gate"]["required"]
        self.assertEqual(set(required), set(gb.REQUIRED_GATE_KEYS))


if __name__ == "__main__":
    unittest.main()
