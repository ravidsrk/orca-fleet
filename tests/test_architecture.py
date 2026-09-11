#!/usr/bin/env python3
"""
Contract tests for the orca-fleet architecture (ARCHITECTURE.md).

These lock in the invariants that justify the repo existing separately from a pile
of vendor-named skills. They use only the standard library. Run:

    python3 -m unittest discover -s tests -v
    # or
    python3 tests/test_architecture.py
"""
import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)
SKILLS = ROOT / "skills"
PLAYBOOKS = ROOT / "playbooks"
RUNTIME = ROOT / "runtime"

# The upstream packs are sources of recipes, never the name of a mission. A mission
# named for its ingredient is the exact anti-pattern this repo removes.
VENDOR_TOKENS = ("matt", "gstack", "addy", "osmani", "garry", "orca", "fleet", "swarm")

EXPECTED_MISSIONS = {
    "ship-it", "clean-sweep", "oss-contribute", "harden-it", "speed-it", "modernize-it",
    "prove-it", "deflake-it", "review-it", "map-it", "root-cause", "attest-it", "access-it",
    "pin-it", "floor-it", "reshape-it", "field-test-it", "migrate-it", "oncall-it",
    "absorb-it", "document-it",
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

    # Missions WITHOUT a quoted `liveness-resume.md: `...`` ledger-header template, each with
    # its reason. test_mission_header_templates_carry_wip pins found == all missions − exempt,
    # so a new mission fails there until its header story is decided — no silent escape (#163).
    MISSIONS_WITHOUT_QUOTED_HEADER_TEMPLATE = {
        "ship-it": "ledger WIP sizing rides the referenced attention-budget.md, no inline template",
        "review-it": "read-only verdict — keeps no coordinator ledger",
        "attest-it": "quotes the canonical header inline (WIP: builders=<n> …)",
        "access-it": "quotes the header inline via ledger-contract.md (WIP: builders=<n> …)",
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
        # Every callable protocol must be composed by at least one mission, via the
        # SAME explicit-reference grammar the validator checks (issue #216): a
        # backticked name inside a Composes/rides clause, or a bare name.md token.
        # A Related-section backtick is not composition — "landed" containing "land"
        # is not either.
        referenced = set()
        for d in mission_dirs():
            referenced |= validate.explicit_protocol_refs(
                (d / "SKILL.md").read_text(encoding="utf-8")
            )
        for proto_dir in (PLAYBOOKS, RUNTIME):
            for f in proto_dir.glob("*.md"):
                self.assertIn(
                    f.stem,
                    referenced,
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
        # Every mission either quotes a WIP-carrying template or is a NAMED exemption — the old
        # hand-maintained superset check let a mission that never quotes a template escape the
        # WIP assertion silently (#163).
        self.assertEqual(
            found,
            {d.name for d in mission_dirs()} - set(self.MISSIONS_WITHOUT_QUOTED_HEADER_TEMPLATE),
            "a mission's ledger-header template story changed — quote a WIP-carrying template "
            "or record a reasoned exemption in MISSIONS_WITHOUT_QUOTED_HEADER_TEMPLATE",
        )
        # The inline-header exemptions keep a ledger too — their header must still carry WIP.
        for name in ("attest-it", "access-it"):
            self.assertIn(
                "WIP: builders=",
                (SKILLS / name / "SKILL.md").read_text(encoding="utf-8"),
                f"{name} ledger header lost the required WIP field",
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

    def test_intent_packet_is_required_on_mutation_manifests(self):
        # Agentic review / intent-debt: discarded agent reasoning must land on
        # the manifest, distinct from claim (still non-oracle).
        manifest = (RUNTIME / "evidence-manifest.md").read_text(encoding="utf-8")
        self.assertIn('"intent"', manifest)
        for key in ("goal", "ruled_out", "why"):
            self.assertIn(f'"{key}"', manifest, f"intent packet lost {key}")
        self.assertRegex(
            manifest, r"(?i)intent packet is present",
            "evidence-manifest.md verification table lost the intent-packet check",
        )

    def test_lighting_classification_defaults_lit(self):
        gates = (RUNTIME / "gate-classification.md").read_text(encoding="utf-8")
        self.assertRegex(gates, r"(?i)dark-eligible")
        # #163: the default declaration must bind `default` to `lit` specifically — a bare
        # (?i)default matches near-universally ("merge to default", "BASE→default promotion").
        self.assertRegex(
            gates, r"(?i)default\s*\*{0,2}`lit`",
            "gate-classification.md lost the lit-is-the-default declaration",
        )
        self.assertRegex(
            gates, r"(?i)recording nothing means\s*\*{0,2}`?lit`?",
            "gate-classification.md lost the omit-means-lit rule",
        )
        ledger = (RUNTIME / "ledger-contract.md").read_text(encoding="utf-8")
        self.assertIn("lighting", ledger)

    def test_autonomy_contract_is_on_the_task_spec(self):
        decomp = (PLAYBOOKS / "decompose-dag.md").read_text(encoding="utf-8")
        self.assertRegex(decomp, r"(?i)AUTONOMY")
        for field in ("goal", "scope", "non-goals", "stop", "escalation", "budget"):
            self.assertIn(field, decomp, f"decompose-dag autonomy block lost {field}")
        remediate = (PLAYBOOKS / "remediate-finding.md").read_text(encoding="utf-8")
        self.assertRegex(remediate, r"(?i)autonomy block")

    def test_mutating_missions_compose_compound_learn(self):
        # E5: compound-learn is the retro; a mutating mission that omits it
        # silently drops the learning loop.
        need = {
            "ship-it", "clean-sweep", "harden-it", "speed-it", "modernize-it",
            "prove-it", "deflake-it", "oss-contribute",
        }
        found = set()
        for d in mission_dirs():
            if d.name not in need:
                continue
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            if re.search(r"`compound-learn`", text):
                found.add(d.name)
        self.assertEqual(found, need)

    def test_promotion_names_accountable_human(self):
        release = (PLAYBOOKS / "release.md").read_text(encoding="utf-8")
        self.assertIn("accountable:", release)

    def test_release_playbook_pins_merge_shaped_rollback(self):
        # Plain `git revert` is rejected on a merge commit (T-12 transcript:
        # "error: commit … is a merge but no -m option was given"). Pin the
        # full command, so reverting that fix — or keeping the substring only
        # in inert prose while losing the actionable form — cannot stay green
        # (#233; scoped per #244 review).
        release = (PLAYBOOKS / "release.md").read_text(encoding="utf-8")
        self.assertIn("git revert -m 1 <merge-sha>", release)

    def test_chain_terminals_are_decidable_by_rule(self):
        # #129: the chaining gate listed degraded terminals as an open ellipsis. #147 review: the rule
        # wrongly degraded `awaiting-maintainer-merge` (oss-contribute's NORMAL terminal). #148 review:
        # the check must compare against the mission DECLARATIONS, not a hand-list — so this derives the
        # terminal set from every guide's "## Terminal …" section and cross-checks the documented rule
        # against each guide's own `degraded` / `NORMAL terminal` self-annotations.
        chain = (RUNTIME / "mission-chaining.md").read_text(encoding="utf-8")
        self.assertRegex(chain, r"(?i)degradation marker")
        DEGRADE_MARKERS = ("-WITH-PARKED", "-WITH-OPEN-ITEMS", "-WITH-GAPS", "-WITH-MANUAL-PARKED",
                           "-WITH-BLOCKED", "-WITH-QUARANTINE", "-WITH-PINNED")
        DEGRADE_TERMINALS = ("NO-GO", "INCONCLUSIVE")
        for tok in DEGRADE_MARKERS + DEGRADE_TERMINALS:
            self.assertIn(tok, chain, f"mission-chaining.md dropped the {tok} classification")

        def classify(name):
            if any(mk in name for mk in DEGRADE_MARKERS) or name in DEGRADE_TERMINALS:
                return "degraded"
            return "clean"

        # Derive DECLARED terminals from each guide's "## Terminal …" section (backticked tokens), so a
        # renamed or added terminal is pulled in automatically rather than silently uncovered.
        declared, degraded_annotated, normal_annotated = set(), set(), set()
        for g in sorted((ROOT / "docs" / "missions").glob("*.md")):
            text = g.read_text(encoding="utf-8")
            sect = re.search(r"(?ms)^## Terminal.*?(?=^## |\Z)", text)
            if sect:
                declared.update(re.findall(r"`([A-Za-z][\w.-]*)`", sect.group(0)))
            # guide self-annotations: the authoritative intent the rule must agree with, parsed
            # precisely (heterogeneous phrasings) rather than by fragile proximity.
            degraded_annotated.update(re.findall(r"`([A-Za-z][\w.-]*)`\s+is a\s+degraded", text))
            for pat in (r"`([A-Za-z][\w.-]*)`[^\n]*?NORMAL terminal",
                        r"degraded\s+\w+\s+is never reported as\s+`([A-Za-z][\w.-]*)`",
                        r"reporting (?:it|them) as\s+`([A-Za-z][\w.-]*)`"):
                normal_annotated.update(re.findall(pat, text))

        self.assertTrue(declared, "no terminal declarations parsed from docs/missions/*.md")
        # 1) Every declared terminal is DECIDABLE (the rule is total — no ambiguity, no crash).
        for t in declared:
            self.assertIn(classify(t), ("clean", "degraded"), t)
        # 2) A terminal carrying a degradation marker MUST be degraded.
        for t in declared:
            if any(mk in t for mk in DEGRADE_MARKERS):
                self.assertEqual(classify(t), "degraded", f"marker-bearing terminal {t!r} not degraded")
        # 3) The rule must AGREE with each guide's own annotation — catches a new marker the rule
        #    misses, or a NORMAL terminal wrongly degraded (the #147 regression class).
        for t in degraded_annotated:
            self.assertEqual(classify(t), "degraded", f"guide annotates {t!r} degraded; rule says clean")
        for t in normal_annotated:
            self.assertEqual(classify(t), "clean", f"guide annotates {t!r} a NORMAL terminal; rule degrades it")
        # 4) The specific regression: awaiting-maintainer-merge is oss-contribute's normal terminal.
        self.assertIn("awaiting-maintainer-merge", declared)
        self.assertEqual(classify("awaiting-maintainer-merge"), "clean")
        self.assertRegex(chain, r"(?i)handoff, not a degradation")
        self.assertIn("awaiting-maintainer-merge", chain)

    def test_scheduling_rule_includes_report_only_conformance(self):
        # #129: mission-scheduling listed a closed set that omitted attest-it, contradicting
        # attest-it's own report-only nature. The fix is a rule (value lands before any one-way
        # gate) that names attest-it as a clean-scheduling report-only sweep.
        sched = (RUNTIME / "mission-scheduling.md").read_text(encoding="utf-8")
        self.assertRegex(sched, r"(?i)before any one-way gate")
        self.assertIn("attest-it", sched,
                      "mission-scheduling.md must classify attest-it (report-only) as clean-scheduling")

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
            r"|\bBUILT[ =][tf]\b"       # row value / prose flip: BUILT t/f, BUILT=t/f
            r"|`BUILT`…"                # flag-range prose: `BUILT`…`WT_CLEAN`
            r"|BUILT\s*→\s*PR_OPEN"     # unit gate chain (wave-state uses → PROMOTION_READY, not → PR_OPEN)
        )
        # #163: scan TRACKED files only (git ls-files) — an rglob of the working tree grades
        # untracked local scratch files, so the verdict used to depend on the checkout's litter.
        tracked = subprocess.run(["git", "ls-files", "-z", "--", "*.md"],
                                 capture_output=True, text=True, cwd=ROOT)
        if tracked.returncode != 0:
            raise unittest.SkipTest("needs an ambient git clone to enumerate tracked .md files")
        offenders = [
            f"{path.relative_to(ROOT)}:{n}: {line.strip()}"
            for path in sorted(ROOT / p for p in tracked.stdout.split("\0") if p)
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
                text, r"(?m)^  proof: (doctrine-only|self-run|external-run)$",
                f"{d.name} declares no proof status under metadata:",
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
            "metadata:\n  proof: doctrine-only\n---\n\nComposes `diagnose`.\n"
        )
        body_head = 2  # the blank line and the Composes line after the closing ---
        pad = v.MISSION_BODY_MAX_LINES - body_head
        # exactly MISSION_BODY_MAX_LINES body lines
        (d / "SKILL.md").write_text(header + "b\n" * pad)
        try:
            errors = v.validate_skill(d, v.known_protocol_names())
            budget_errors = [e for e in errors if "budget" in e]
            self.assertEqual(
                budget_errors, [],
                f"a body of exactly {v.MISSION_BODY_MAX_LINES} lines must not breach the cap",
            )
        finally:
            shutil.rmtree(d.parent)

    def test_liveness_resume_exit_codes_match_spawn_worker(self):
        # Issue #31: the respawn bullet glossed exit 2 as "state moved, re-triage
        # uncounted", but spawn_worker.sh exits 2 on EVERY usage/policy refusal
        # (bad args, unknown agent, unmet deps, danger without opt-in) — the old
        # gloss taught coordinators to silently retry policy refusals. The script
        # header is the contract; the doc's inline decision table must match it,
        # and the pane-read caveat (exit 3 is a possible false negative) must sit
        # at the respawn decision point, not only in the other file.
        #
        # v5 adds exit 4 (state=outcome_unknown). It is the one code that must
        # NEVER reach the respawn path: the start neither proved nor disproved the
        # worker, so a respawn puts a second writer beside a possibly-live pane.
        # Both files must carry that, or a coordinator reading only one of them
        # rebuilds the 2026-07-15 dual-writer failure.
        doc = (RUNTIME / "liveness-resume.md").read_text(encoding="utf-8")
        script = (RUNTIME / "scripts" / "spawn_worker.sh").read_text(encoding="utf-8")
        self.assertRegex(
            script, r"(?m)^#.*\b2\b.*usage or policy refusal",
            "spawn_worker.sh exit-2 contract moved — realign liveness-resume.md "
            "and this test together",
        )
        self.assertRegex(
            script, r"(?m)^#\s+4\s+supervised state=outcome_unknown",
            "spawn_worker.sh must document exit 4 = outcome_unknown in its "
            "exit-code table",
        )
        self.assertRegex(
            script, r"(?is)outcome_unknown.{0,400}?never respawn",
            "the script's outcome_unknown contract must say inspect, never respawn",
        )
        m = re.search(r"(?s)^- Respawn a dead worker:.*?(?=^- )", doc, re.M)
        self.assertIsNotNone(m, "liveness-resume.md lost its respawn bullet")
        # Collapse the bullet's wrapping: where the prose happens to break a line
        # is not part of the contract, and asserting on it makes a reflow look
        # like a doctrine change.
        bullet = " ".join(m.group(0).split())
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
            "(an unobserved turn start is not a dead worker)",
        )
        # Every nonzero code the script actually returns has to appear here. Exit 5
        # (LAUNCHED_UNUSABLE) shipped without this and nothing noticed; a code the
        # script returns and the doctrine never names is a coordinator branching on
        # something nobody wrote down.
        used = {int(c) for c in re.findall(r"^\s*exit ([0-9])\s*$", script, re.M)} - {0}
        self.assertTrue(used, "no exit codes found — the regex stopped matching the script")
        undocumented = sorted(c for c in used if not re.search(rf"[Ee]xit {c}\b", bullet))
        self.assertEqual(undocumented, [], f"spawn_worker.sh returns {undocumented} and the "
                                           "respawn bullet never says what they mean")
        self.assertRegex(
            bullet, r"(?i)exit 5.{0,120}?never respawn",
            "exit 5 is a LIVE worker that cannot do the work — stopping it, not "
            "respawning beside it, is the whole point of having a code for it",
        )
        self.assertRegex(
            bullet, r"(?i)exit 4 \(`?outcome_unknown`?\).{0,80}?never respawn",
            "exit 4 (outcome_unknown) must be INSPECT, never respawn, at the "
            "respawn decision point — respawning an unproven start is the "
            "dual-writer class",
        )
        # The pane read is a COMMAND with a receipt, not an instruction to squint
        # at a TUI: the runtime's own answer is `terminal read --screen` /
        # `worker-read`. Naming it is what makes the caveat executable.
        self.assertRegex(
            bullet, r"--screen|worker-read",
            "the pane-read caveat must name the command that performs it "
            "(terminal read --screen / worker-read), not just say 'read the pane'",
        )

    def test_watch_reads_fleet_projections_not_folklore(self):
        # §3 #5 / §7 item 5: `worker-list`'s projection.liveness is the fleet
        # verdict for the AGENT; `worker-show`'s observation.status is PTY
        # liveness only, so a live terminal can still hold a dead agent. The doc
        # taught this inverted, and the heuristics it grew instead of reading the
        # runtime are what produced the dual-writer class. WATCH must escalate to
        # the projection and then run the runtime's own literal nextAction.argv.
        doc = (RUNTIME / "liveness-resume.md").read_text(encoding="utf-8")
        for needle, why in [
            (r"projection\.liveness", "the fleet liveness verdict must be named"),
            (r"observation\.status", "worker-show must be scoped to PTY liveness"),
            (r"attention\.requiresAction",
             "WATCH must act on the rows the runtime flags"),
            (r"nextAction\.argv",
             "WATCH must execute the runtime's literal next action, not a heuristic"),
            (r"--terminal-state reclaimable",
             "the end-of-run gate must be the reclaimable projection"),
            (r"outcome_unknown", "the start-state vocabulary must include outcome_unknown"),
            (r"unverifiable", "absence must be named and must authorize nothing"),
        ]:
            self.assertRegex(doc, needle, f"liveness-resume.md: {why}")
        self.assertNotRegex(
            doc, r"(?i)`worker-show[^`]*`\s*is the per-worker truth",
            "the authority is inverted: worker-list's projection is the fleet "
            "verdict, worker-show is PTY-only",
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


class TestMutatingMissionSet(unittest.TestCase):
    """#117: the mutating-mission set is defined once (scripts/validate.py) and every other
    authority must agree — a unit that lands code must not escape the SHA-bound floor because
    two lists drifted."""

    def _canonical(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return set(mod.MUTATING_MISSIONS)

    def test_evidence_manifest_mutation_list_matches_validate(self):
        text = (RUNTIME / "evidence-manifest.md").read_text(encoding="utf-8")
        m = re.search(r"\*\*Mutation units\*\*\s*\(([^)]*)\)", text, re.DOTALL)
        self.assertIsNotNone(m, "evidence-manifest.md §3 must list the Mutation units")
        listed = {n.strip() for n in m.group(1).replace("\n", " ").split(",") if n.strip()}
        self.assertEqual(listed, self._canonical(),
                         "evidence-manifest.md §3 Mutation-units list has drifted from "
                         "scripts/validate.py MUTATING_MISSIONS")

    def test_canonical_set_is_the_code_landing_missions(self):
        # Guards the intent: report-only / planning / diagnosis missions are NOT in the set.
        canonical = self._canonical()
        for m in ("review-it", "map-it", "root-cause"):
            self.assertNotIn(m, canonical)
        for m in ("ship-it", "oss-contribute", "access-it"):
            self.assertIn(m, canonical)

class TestBundleForCopyInstallers(unittest.TestCase):
    """scripts/bundle.py — the copy-install fix (docs/reviews/2026-09-10-review.md §8 P2-18).

    Three-layer separation means a mission names its protocols by bare name and
    they live two directories up. That is exactly what a copy installer severs.
    The bundle vendors them; these tests keep it honest about doing so.
    """

    def _bundle(self):
        import importlib.util, tempfile
        spec = importlib.util.spec_from_file_location("_bundle", ROOT / "scripts" / "bundle.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, tempfile

    def test_check_mode_passes_on_the_live_catalog(self):
        mod, _tempfile = self._bundle()
        self.assertEqual(mod.main(["--check"]), 0)

    def test_every_mission_is_self_contained_after_bundling(self):
        mod, tempfile = self._bundle()
        with tempfile.TemporaryDirectory() as tmp:
            built, problems = mod.build(tmp)
            self.assertEqual(problems, [])
            self.assertEqual(built, len(mission_dirs()))
            for mission in mission_dirs():
                out = Path(tmp) / "skills" / mission.name
                text = (out / "SKILL.md").read_text(encoding="utf-8")
                self.assertNotIn("../../", text, f"{mission.name} still points out of its directory")
                index = out / "references" / "README.md"
                self.assertTrue(index.is_file(), f"{mission.name} has no references index")
                # Every protocol the mission names must have a copy beside it.
                names = set(validate.explicit_protocol_refs(
                    (mission / "SKILL.md").read_text(encoding="utf-8")
                )) & validate.known_protocol_names()
                for name in names:
                    self.assertTrue(
                        (out / "references" / f"{name}.md").is_file(),
                        f"{mission.name} did not vendor {name}.md",
                    )

    def test_dist_is_not_committed(self):
        # 21 copies of the doctrine tree in git would rot between runtime edits.
        self.assertIn("dist/", (ROOT / ".gitignore").read_text(encoding="utf-8"))
        self.assertFalse((ROOT / "dist").exists() and any((ROOT / "dist").iterdir())
                         and (ROOT / "dist" / ".git").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
