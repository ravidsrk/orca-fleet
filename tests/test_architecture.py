#!/usr/bin/env python3
"""
Contract tests for the orca-fleet architecture (ARCHITECTURE.md).

These lock in the invariants that justify the repo existing separately from a pile
of vendor-named skills. They use only the standard library. Run:

    python3 -m unittest discover -s tests -v
    # or
    python3 tests/test_architecture.py
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
PLAYBOOKS = ROOT / "playbooks"
RUNTIME = ROOT / "runtime"

# The upstream packs are sources of recipes, never the name of a mission. A mission
# named for its ingredient is the exact anti-pattern this repo removes.
VENDOR_TOKENS = ("matt", "gstack", "addy", "osmani", "garry", "orca", "fleet", "swarm")

EXPECTED_MISSIONS = {
    "ship-it", "clean-sweep", "oss-contribute", "harden-it", "speed-it",
    "modernize-it", "prove-it", "deflake-it", "review-it", "map-it", "root-cause",
}


def mission_dirs():
    return [d for d in sorted(SKILLS.iterdir())
            if d.is_dir() and not d.name.startswith((".", "_"))]


def frontmatter_description(text):
    # crude but sufficient: pull the description block from YAML frontmatter
    m = re.search(r"(?ms)^description:\s*>-?\s*\n(.*?)^\w", text)
    if m:
        return " ".join(l.strip() for l in m.group(1).splitlines() if l.strip())
    m = re.search(r"(?m)^description:\s*(.+)$", text)
    return m.group(1).strip() if m else ""


class TestArchitecture(unittest.TestCase):

    # Nine missions quote a ledger-header template (ship-it and review-it quote none);
    # a mission may not silently drop its template to dodge the WIP assertion in
    # test_mission_header_templates_carry_wip.
    MISSIONS_WITH_HEADER_TEMPLATE = {
        "clean-sweep", "harden-it", "speed-it", "modernize-it", "prove-it",
        "deflake-it", "map-it", "root-cause", "oss-contribute",
    }

    def test_validator_passes(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, f"validate.py failed:\n{r.stdout}\n{r.stderr}")

    def test_exactly_the_expected_missions(self):
        found = {d.name for d in mission_dirs()}
        self.assertEqual(found, EXPECTED_MISSIONS)

    def test_missions_are_outcome_named_not_vendor_named(self):
        for d in mission_dirs():
            for tok in VENDOR_TOKENS:
                self.assertNotIn(
                    tok, d.name,
                    f"mission '{d.name}' is named for an ingredient ('{tok}'), "
                    f"not an outcome — see ARCHITECTURE.md",
                )

    def test_three_layer_separation(self):
        # Only skills/ may contain SKILL.md. Playbooks and runtime are callable, not
        # discoverable — a SKILL.md under them recreates routing collisions.
        for layer in (PLAYBOOKS, RUNTIME):
            leaks = list(layer.rglob("SKILL.md"))
            self.assertEqual(leaks, [], f"SKILL.md leaked into {layer.name}/: {leaks}")

    def test_every_mission_has_convergence_proof_and_anti_patterns(self):
        # The evidence-based definition of done and the failure catalog are the
        # discipline that made clean-sweep / spec-to-ship reliable.
        for d in mission_dirs():
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(
                text, r"(?i)convergence proof|definition of done",
                f"{d.name} has no convergence proof / definition of done",
            )
            self.assertRegex(text, r"(?im)^##\s*Anti-patterns",
                             f"{d.name} has no Anti-patterns section")

    def test_every_description_has_a_use_when_trigger(self):
        for d in mission_dirs():
            desc = frontmatter_description((d / "SKILL.md").read_text(encoding="utf-8"))
            self.assertRegex(
                desc.lower(), r"use when|use for|use to",
                f"{d.name} description has no 'Use when' trigger phrase",
            )

    def test_no_orphan_playbooks_or_runtime_policies(self):
        # Every callable protocol must be composed by at least one mission, via an
        # EXPLICIT reference form: `name` backticked or name.md. Prose coincidence is
        # not a composition — "landed" containing "land", or a bare phase name in a
        # description, must not keep an orphan alive.
        bodies = "\n".join((d / "SKILL.md").read_text(encoding="utf-8") for d in mission_dirs())
        for proto_dir in (PLAYBOOKS, RUNTIME):
            for f in proto_dir.glob("*.md"):
                stem = re.escape(f.stem)
                self.assertRegex(
                    bodies,
                    rf"`{stem}`|(?<![\w-]){stem}\.md(?![\w.-])",
                    f"{proto_dir.name}/{f.name} is composed by no mission (orphan)",
                )

    def test_wip_cap_is_a_ledger_header_contract(self):
        # The 2026-07-15 chimely run dispatched a 4-builder wave with no WIP field in
        # its ledger header — the cap existed only as doctrine, so nothing held the
        # wave. The header template and the producer-side policy must both carry the
        # field; an edit that drops either re-opens it.
        header_spec = (RUNTIME / "liveness-resume.md").read_text(encoding="utf-8")
        self.assertIn(
            "WIP: builders=", header_spec,
            "liveness-resume.md header template lost the WIP field",
        )
        budget = (RUNTIME / "attention-budget.md").read_text(encoding="utf-8")
        self.assertRegex(
            budget, r"(?i)required ledger-header field",
            "attention-budget.md no longer declares WIP a required header field",
        )
        # The pane-counting rule is the root-cause fix (a dual-writer respawn is how
        # a planned 4-builder wave peaked at 5); softening it back to task-counting
        # must not pass silently.
        self.assertRegex(
            budget, r"(?i)counts live panes, not tasks",
            "attention-budget.md lost the pane-counting rule — respawned panes "
            "would stop counting against the cap",
        )

    def test_mission_header_templates_carry_wip(self):
        # attention-budget.md declares `WIP: builders=<n> reviewers=<n>` a required
        # ledger-header field written at T0, and liveness-resume.md's canonical header
        # ends with it. A mission template that stops at SOURCE teaches coordinators
        # to write capless headers — the same hole test_wip_cap_is_a_ledger_header_contract
        # closes on the producer side.
        found = set()
        for d in mission_dirs():
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            for m in re.finditer(r"liveness-resume\.md: `([^`]+)`", text):
                found.add(d.name)
                self.assertIn(
                    "WIP", m.group(1),
                    f"{d.name} ledger-header template omits the required WIP field",
                )
        # On sets, assertGreaterEqual asserts the superset relation: every mission
        # known to quote a template must still quote one (removal fails here).
        self.assertGreaterEqual(
            found, self.MISSIONS_WITH_HEADER_TEMPLATE,
            "a mission dropped its ledger-header template instead of carrying WIP",
        )

    def test_attention_budget_wip_curve_is_a_named_protocol(self):
        # The WIP caps rest on a single field run and the doc said "override if
        # measured" without defining measurement (#51). Publishing the caps as a
        # convention requires a named protocol: the metrics a run records, where
        # they land, and an explicit evidence level on the caps until a measured
        # curve replaces the asserted one.
        budget = (RUNTIME / "attention-budget.md").read_text(encoding="utf-8")
        self.assertRegex(
            budget, r"(?i)wip-curve protocol",
            "attention-budget.md no longer names the WIP-curve protocol",
        )
        # Row-anchored: "WIP settings" in the revision-rule prose must not satisfy
        # the check for the table's "WIP setting" row (the curve's independent
        # variable), so every metric is asserted as a leading table cell.
        for metric in ("WIP setting", "builder throughput", "verification latency",
                       "rework rate", "freshness violations"):
            self.assertRegex(
                budget, r"(?im)^\|\s*" + re.escape(metric) + r"\s*\|",
                f"attention-budget.md WIP-curve table lost its {metric!r} row",
            )
        self.assertIn(
            "docs/runs/", budget,
            "attention-budget.md no longer says where WIP-curve metrics are logged",
        )
        self.assertRegex(
            budget, r"(?i)evidence level",
            "attention-budget.md caps lost their evidence-level annotation",
        )

    def test_verifier_audits_criterion_test_binding(self):
        # 2025-2026 grader research (SWE-bench Verified retired after defects in
        # ≥59% of its hard subset; ImpossibleBench's spec-conflicting tests
        # exploited 54-76% of the time) showed a green suite proves nothing when
        # a test does not exercise the criterion it claims to cover. The verifier
        # table must carry the criterion↔test binding audit, and the manifest
        # schema must carry the coverage field that audit logs to (#50).
        manifest = (RUNTIME / "evidence-manifest.md").read_text(encoding="utf-8")
        self.assertRegex(
            manifest, r"(?i)binding audit",
            "evidence-manifest.md verification table lost the criterion↔test "
            "binding-audit step",
        )
        self.assertIn(
            '"binding_audit"', manifest,
            "evidence-manifest.md manifest schema lost the binding_audit "
            "audit-coverage field",
        )

    def test_row_flags_are_the_record(self):
        # The chimely run advanced BUILD_DONE/REVIEWED only as dispatch-log prose; every
        # unit row still read all-f at run close, which would have broken a crash
        # RESUME (it reads row flags, not narration).
        ledger = (RUNTIME / "ledger-contract.md").read_text(encoding="utf-8")
        self.assertRegex(
            ledger, r"(?i)row is the record",
            "ledger-contract.md lost the row-is-the-record rule",
        )

    def test_per_unit_flag_is_build_done_not_built(self):
        # `BUILT` used to name two opposite pipeline positions: the release
        # wave-state (BUILT → PROMOTION_READY → RELEASED, release.md) AND the
        # per-unit ledger boolean. The per-unit flag is BUILD_DONE; only the
        # wave-state keeps the name BUILT (#30).
        ledger = (RUNTIME / "ledger-contract.md").read_text(encoding="utf-8")
        self.assertIn(
            "`BUILD_DONE`", ledger,
            "ledger-contract.md lost the BUILD_DONE per-unit flag",
        )
        self.assertNotRegex(
            ledger, r"\bBUILT\b",
            "ledger-contract.md names the per-unit flag BUILT — collides with "
            "the release wave-state (#30)",
        )
        # No doc may use BUILT in a per-unit-flag shape: bare row cell, t-flip,
        # flag range, or the unit gate chain. Wave-state shapes (`BUILT` →
        # `PROMOTION_READY`, BUILT-WITH-PARKED, {{BUILT}}) stay legal.
        per_unit_shape = re.compile(
            r"\|\s*BUILT\s*\|"          # bare row-header cell: | BUILT |
            r"|\bBUILT[ =]t\b"          # row value / prose flip: BUILT t, BUILT=t
            r"|`BUILT`…"                # flag-range prose: `BUILT`…`WT_CLEAN`
            r"|BUILT\s*→\s*PR_OPEN"     # unit gates (wave-state → PROMOTION_READY)
        )
        offenders = [
            f"{path.relative_to(ROOT)}:{n}: {line.strip()}"
            for path in sorted(ROOT.rglob("*.md"))
            if ".git" not in path.parts
            for n, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1)
            if per_unit_shape.search(line)
        ]
        self.assertEqual(
            [], offenders,
            "per-unit ledger flag still named BUILT (rename to BUILD_DONE):\n"
            + "\n".join(offenders),
        )
        # The rename is one-sided: the release wave-state keeps BUILT.
        release = (PLAYBOOKS / "release.md").read_text(encoding="utf-8")
        self.assertRegex(
            release, r"\bBUILT\b",
            "release.md lost the BUILT wave-state — #30 renamed only the "
            "per-unit flag",
        )

    def test_pm_parses_heartbeat_interleaved_stream(self):
        # pm.py's whole job: decode message batches from a stream that interleaves
        # _heartbeat objects and malformed segments, and print each message WITH its id
        # (reply --id depends on it).
        import tempfile, os
        stream = (
            '{"_heartbeat": true}\n'
            '{"result": {"messages": [{"id": "msg-42", "from_handle": "w1", '
            '"type": "worker_done", "subject": "done", "body": "b", "payload": null}]}}\n'
            "this line is not json\n"
            '{"_heartbeat": true}\n'
        )
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(stream)
            path = fh.name
        try:
            r = subprocess.run(
                [sys.executable, str(RUNTIME / "scripts" / "pm.py"), path],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("MESSAGES: 1", r.stdout)
            self.assertIn("msg-42", r.stdout, "message id must be printed (reply --id needs it)")
            self.assertIn("skipped 1 malformed segment", r.stderr)
        finally:
            os.unlink(path)

    def test_pm_missing_file_fails_clean(self):
        # pm.py feeds the coordinator's stall/respawn decisions (liveness-resume.md);
        # a missing inbox must be a one-line diagnostic and exit 2, not a raw traceback.
        r = subprocess.run(
            [sys.executable, str(RUNTIME / "scripts" / "pm.py"), "/nonexistent-inbox.json"],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 2, f"expected exit 2, got {r.returncode}")
        self.assertNotIn("Traceback", r.stderr, "missing file must not dump a raw traceback")
        self.assertIn("nonexistent-inbox.json", r.stderr, "error must name the unreadable path")

    def test_pm_warns_on_unrecognized_message_envelope(self):
        # A top-level {"messages": [...]} envelope (no "result" wrapper) is a real inbox
        # in a shape pm.py doesn't parse; it must warn on stderr instead of silently
        # reporting MESSAGES: 0 as if the inbox were empty.
        import tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write('{"messages": [{"id": "m1", "subject": "s", "body": "b"}]}\n')
            path = fh.name
        try:
            r = subprocess.run(
                [sys.executable, str(RUNTIME / "scripts" / "pm.py"), path],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("MESSAGES: 0", r.stdout)
            self.assertIn("WARN", r.stderr, "unrecognized envelope shape must not be silent")
            self.assertIn("messages", r.stderr, "warning must say what looked message-like")
        finally:
            os.unlink(path)

    def test_pm_warns_on_message_like_keys_at_any_path(self):
        # Review R1/N1/N2 on the envelope guard: 'messages' misplaced at ANY path —
        # wrong-typed under result, nested under an unknown wrapper, or riding inside
        # a heartbeat envelope — must warn, never silently count as an empty inbox
        # (and a non-list batch must not be iterated as characters).
        import tempfile, os
        shapes = {
            "wrong-typed result.messages": '{"result": {"messages": "notalist"}}\n',
            "nested under data": '{"data": {"messages": [{"id": "x"}]}}\n',
            "inside heartbeat envelope": '{"_heartbeat": true, "messages": [{"id": "x"}]}\n',
        }
        for label, stream in shapes.items():
            with self.subTest(shape=label):
                with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
                    fh.write(stream)
                    path = fh.name
                try:
                    r = subprocess.run(
                        [sys.executable, str(RUNTIME / "scripts" / "pm.py"), path],
                        capture_output=True, text=True,
                    )
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertIn("MESSAGES: 0", r.stdout)
                    self.assertIn("WARN", r.stderr, f"{label}: silent zero on message-like envelope")
                finally:
                    os.unlink(path)

    def test_pm_legitimately_empty_inbox_stays_quiet(self):
        # Negative control for the envelope warning: a well-formed empty inbox
        # (empty batch + heartbeats) is genuinely empty — any warning here would
        # train coordinators to ignore the real one.
        import tempfile, os
        stream = (
            '{"_heartbeat": true}\n'
            '{"result": {"messages": []}}\n'
            '{"_heartbeat": true}\n'
        )
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(stream)
            path = fh.name
        try:
            r = subprocess.run(
                [sys.executable, str(RUNTIME / "scripts" / "pm.py"), path],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("MESSAGES: 0", r.stdout)
            self.assertEqual(r.stderr, "", "empty inbox must not emit a false warning")
        finally:
            os.unlink(path)

    def test_runtime_scripts_present_and_executable_shape(self):
        # The shared tooling must exist, be non-trivial, be executable, and actually parse —
        # a zero-byte or syntax-broken script must fail here, not mid-run.
        import os
        for script in ("spawn_worker.sh", "preflight.py", "pm.py"):
            p = RUNTIME / "scripts" / script
            self.assertTrue(p.exists(), f"runtime/scripts/{script} missing")
            self.assertGreater(p.stat().st_size, 200, f"{script} is suspiciously small")
            self.assertTrue(os.access(p, os.X_OK), f"{script} is not executable")
            if script.endswith(".py"):
                import ast
                ast.parse(p.read_text(encoding="utf-8"))
            else:
                r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"bash -n {script}: {r.stderr}")

    def test_every_mission_declares_proof_status(self):
        # Honesty gate: the predecessor presented 12 missions with 2 proven and died
        # of it. Every mission states how proven it is; the validator enforces the
        # evidence link when a mission claims more than doctrine.
        for d in mission_dirs():
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(
                text, r"(?m)^proof: (doctrine-only|self-run|external-run)$",
                f"{d.name} declares no proof status",
            )

    def test_budget_boundary_not_off_by_one(self):
        # Greptile P1 on PR #5: text.count("\n")+1 overcounts newline-terminated files
        # by one, silently shrinking every cap. A mission of EXACTLY the cap's lines
        # (POSIX newline-terminated) must pass the budget check.
        import importlib.util, tempfile, shutil
        spec = importlib.util.spec_from_file_location("v", ROOT / "scripts" / "validate.py")
        v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v)
        d = Path(tempfile.mkdtemp()) / "cap-mission"
        d.mkdir()
        header = (
            "---\nname: cap-mission\ndescription: x. Use when testing.\n"
            "proof: doctrine-only\n---\n\nComposes `diagnose`.\n"
        )
        pad = v.MISSION_MAX_LINES - len(header.splitlines())
        (d / "SKILL.md").write_text(header + "b\n" * pad)  # exactly MISSION_MAX_LINES lines
        try:
            errors = v.validate_skill(d, v.known_protocol_names())
            budget_errors = [e for e in errors if "instruction budget" in e]
            self.assertEqual(
                budget_errors, [],
                f"a file of exactly {v.MISSION_MAX_LINES} lines must not breach the cap",
            )
        finally:
            shutil.rmtree(d.parent)

    def test_liveness_resume_exit_codes_match_spawn_worker(self):
        # Issue #31: the respawn bullet glossed exit 2 as "state moved, re-triage
        # uncounted", but spawn_worker.sh exits 2 on EVERY usage/policy refusal
        # (bad args, unknown agent, unmet deps, danger without opt-in) — the old
        # gloss taught coordinators to silently retry policy refusals. The script
        # header is the contract; the doc's inline decision table must match it,
        # and the pane-read caveat (dispatch-lifecycle.md: codex workers emit no
        # heartbeats, so exit 3 is a possible false negative) must sit at the
        # respawn decision point, not only in the other file.
        doc = (RUNTIME / "liveness-resume.md").read_text(encoding="utf-8")
        script = (RUNTIME / "scripts" / "spawn_worker.sh").read_text(encoding="utf-8")
        self.assertRegex(
            script, r"(?m)^#.*\b2\b.*usage or policy refusal",
            "spawn_worker.sh exit-2 contract moved — realign liveness-resume.md "
            "and this test together",
        )
        m = re.search(r"(?s)^- Respawn a dead worker:.*?(?=^- )", doc, re.M)
        self.assertIsNotNone(m, "liveness-resume.md lost its respawn bullet")
        bullet = m.group(0)
        self.assertNotRegex(
            bullet, r"(?i)state moved",
            "exit 2 is ANY usage/policy refusal (spawn_worker.sh:12), not 'state "
            "moved' — misclassifying it hides policy failures as uncounted re-triage",
        )
        self.assertRegex(
            bullet, r"(?i)exit 2 = usage or policy refusal",
            "exit-2 gloss must match spawn_worker.sh verbatim",
        )
        self.assertRegex(
            bullet, r"(?i)read the pane",
            "pane-read-before-respawn caveat missing at the respawn decision point",
        )
        self.assertRegex(
            bullet, r"(?i)false negative",
            "exit 3 must be flagged a possible false negative "
            "(heartbeats are agent-dependent)",
        )

    def test_runtime_scripts_never_interpolate_code(self):
        # The predecessor shipped a P0 RCE by interpolating values into `python -c`
        # (live even under --dry-run). Values pass as argv or heredoc stdin, never
        # inside a double-quoted code string; no eval.
        for f in sorted((RUNTIME / "scripts").iterdir()):
            if f.suffix not in (".sh", ".py"):
                continue
            text = f.read_text(encoding="utf-8")
            self.assertNotRegex(
                text, r"python3? -c \"",
                f"{f.name}: python -c with a double-quoted (interpolatable) code string",
            )
            self.assertNotRegex(
                text, r"\beval[ (]",
                f"{f.name}: eval on constructed input",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
