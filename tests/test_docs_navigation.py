#!/usr/bin/env python3
"""
Contract tests for the human documentation surface.

A doc surface that presents itself as complete must be machine-checked against
repo state, or it silently rots: ARCHITECTURE.md's runtime-policy list reads as
the whole runtime surface, docs/runs/README.md is the proof-honesty index the
mission frontmatter leans on, and docs/research/ only exists for readers who
can reach it. Each invariant here failed once (issue number on the test).

    python3 -m unittest discover -s tests -v
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
RUNTIME = ROOT / "runtime"


class TestDocsNavigation(unittest.TestCase):

    def test_architecture_names_every_runtime_policy(self):
        # Issue #34: the "operational details ARE the product" list omitted
        # mission-scheduling.md (and sandbox-policy.md appeared nowhere at all),
        # so a reader auditing the runtime surface off ARCHITECTURE.md missed
        # real policies. Every runtime/*.md must be named somewhere in the file.
        arch = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for f in sorted(RUNTIME.glob("*.md")):
            self.assertIn(
                f.stem, arch,
                f"runtime/{f.name} is a load-bearing policy ARCHITECTURE.md never names",
            )

    def test_run_archive_index_lists_every_report(self):
        # Issue #35: the index predated the newest run — the report that backs
        # oss-contribute's `proof: external-run` frontmatter was invisible from
        # the archive's own index. Every dated report must be a linked row.
        index = (DOCS / "runs" / "README.md").read_text(encoding="utf-8")
        for f in sorted((DOCS / "runs").glob("2*.md")):
            self.assertIn(
                f"({f.name})", index,
                f"docs/runs/{f.name} is not linked from the run-archive index",
            )

    def test_run_archive_integrity_standard_matches_practice(self):
        # Issue #35: the index claimed every report carries a run-close sha256
        # integrity inventory, while the oss-contribute report retains its
        # inventory in the fork worktree. Stated standard must equal actual
        # practice: a report either carries the inline inventory or names where
        # its inventory is retained — and the index's stated standard must
        # acknowledge that retained-elsewhere form the moment any report uses it.
        index = (DOCS / "runs" / "README.md").read_text(encoding="utf-8")
        for f in sorted((DOCS / "runs").glob("2*.md")):
            text = f.read_text(encoding="utf-8")
            if "integrity inventory (sha256)" in text:
                continue  # inline inventory — the strong form
            self.assertRegex(
                text, r"(?i)integrity inventory[^.]*retained",
                f"docs/runs/{f.name} has neither an inline sha256 inventory nor "
                f"a named retention location for one",
            )
            self.assertRegex(
                index, r"(?i)retained",
                f"the index claims every report carries an inline sha256 "
                f"inventory, but docs/runs/{f.name} retains its inventory "
                f"out-of-repo — stated standard != practice",
            )

    def test_research_archive_reachable_and_dated(self):
        # Issue #36: docs/research/ was reachable only from CHANGELOG.md — no
        # navigated surface linked it, so the analysis was invisible to its
        # readers and its staleness invisible to maintainers. It must be linked
        # from at least one navigated doc, every snapshot must be indexed in the
        # archive's README, and each snapshot must open with a dated-snapshot
        # banner so its counts are read as historical, not current.
        navigated = [ROOT / "README.md", DOCS / "concepts.md", DOCS / "getting-started.md"]
        navigated += sorted((DOCS / "missions").glob("*.md"))
        navigated += sorted((DOCS / "guides").glob("*.md"))
        # a missing surface must read as this test's assertion, not a
        # FileNotFoundError traceback; with every surface gone, inbound is
        # empty and the orphan assertion still fires.
        navigated = [p for p in navigated if p.exists()]
        # an actual link target into research/ — prose that happens to contain
        # the word ("research/decision frontier") must not count as navigation.
        link = re.compile(r"\]\((?:\.\./)*(?:docs/)?research/")
        inbound = [p.name for p in navigated
                   if link.search(p.read_text(encoding="utf-8"))]
        self.assertTrue(
            inbound,
            "docs/research/ is linked from no navigated doc surface (orphan)",
        )
        research_index = (DOCS / "research" / "README.md").read_text(encoding="utf-8")
        for f in sorted((DOCS / "research").glob("2*.md")):
            self.assertIn(
                f.name, research_index,
                f"docs/research/{f.name} is missing from the archive index",
            )
            head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:10])
            self.assertIn(
                "Dated snapshot", head,
                f"docs/research/{f.name} carries no dated-snapshot banner",
            )

    def test_mission_guides_name_every_skill_compose_and_ride(self):
        # After E1–E6 the human guides lagged the SKILL compose/rides clauses
        # (missing ledger-contract, evidence-manifest, acceptance-review, …).
        # A guide that omits a protocol the skill declares is a false catalog.
        protocols = {p.stem for p in (ROOT / "playbooks").glob("*.md")}
        protocols |= {p.stem for p in RUNTIME.glob("*.md")}
        compose_clause = re.compile(
            r"\b(?:Composes|COMPOSES|Rides|RIDES|rides)\b\s+(.+?)(?:\n\n|\Z)",
            re.DOTALL,
        )
        backticks = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
        guide_links = re.compile(
            r"\]\(\.\./\.\./(?:playbooks|runtime)/([a-z0-9-]+)\.md\)"
        )
        guide_section = re.compile(
            r"^## Composes\n(.*?)(?=^## |\Z)", re.DOTALL | re.MULTILINE
        )
        skills = ROOT / "skills"
        for d in sorted(skills.iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            skill = (d / "SKILL.md").read_text(encoding="utf-8")
            declared = set()
            for m in compose_clause.finditer(skill):
                # First sentence only — later sentences are caveats
                # ("not a full `runtime-prove` pass", "No `merge-serialization`").
                first = re.split(r"\.\s+(?=[A-Z])", m.group(1), maxsplit=1)[0]
                declared.update(backticks.findall(first))
            declared &= protocols
            guide_path = DOCS / "missions" / f"{d.name}.md"
            self.assertTrue(
                guide_path.is_file(),
                f"docs/missions/{d.name}.md is missing",
            )
            guide = guide_path.read_text(encoding="utf-8")
            section = guide_section.search(guide)
            self.assertIsNotNone(
                section,
                f"docs/missions/{d.name}.md has no ## Composes section",
            )
            named = set(backticks.findall(section.group(1)))
            named.update(guide_links.findall(section.group(1)))
            missing = sorted(declared - named)
            self.assertEqual(
                missing, [],
                f"docs/missions/{d.name}.md Composes omits {missing} "
                f"declared in skills/{d.name}/SKILL.md",
            )

    def test_mission_index_lists_every_skill(self):
        # #125: docs/missions/README.md indexed 11 of 13 (attest-it, access-it missing). The index
        # must link every skills/<name> guide. #143 review: resolve each link target against the
        # index's directory and require it to point at a REAL file — a basename match through a
        # broken path is not a link a reader can follow.
        index_path = DOCS / "missions" / "README.md"
        index = index_path.read_text(encoding="utf-8")
        resolved = set()
        # accept inline links with optional <>, #fragment, and "title" — capture the .md path only.
        for target in re.findall(r"\[[^\]]+\]\(\s*<?([^)>#\s]+\.md)(?:#[^)>\s]*)?>?(?:\s+\"[^\"]*\")?\s*\)", index):
            p = (index_path.parent / target).resolve()
            if p.is_file():
                resolved.add(p)
        for d in sorted((ROOT / "skills").iterdir()):
            if d.is_dir() and not d.name.startswith((".", "_")):
                guide = (DOCS / "missions" / f"{d.name}.md").resolve()
                self.assertIn(guide, resolved,
                              f"docs/missions/README.md omits a followable link to the {d.name} guide "
                              "(a basename match through a broken path is not a link readers can follow)")

    def test_distribution_proof_mix_matches_reality(self):
        # #125: the illustrative proof mix in distribution.md must match the live proof_status rollup,
        # not a stale hand-count (was "2·1·8" for an 11-mission catalog).
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "proof_status", ROOT / "runtime" / "scripts" / "proof_status.py")
        ps = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ps)
        counts = ps.rollup(ps.collect(ROOT / "skills", ROOT))
        text = (DOCS / "distribution.md").read_text(encoding="utf-8")
        for tier in ("doctrine-only", "self-run", "external-run"):
            m = re.search(rf"(\d+)\s+{re.escape(tier)}", text)
            self.assertIsNotNone(m, f"distribution.md omits the {tier} count (live: {counts[tier]})")
            self.assertEqual(int(m.group(1)), counts[tier],
                             f"distribution.md {tier} count is stale (live: {counts[tier]})")

    def test_mission_guides_show_proof_tier(self):
        # #124: every mission guide surfaces its proof tier (matching the SKILL frontmatter), so a
        # doctrine-only, never-run mission does not read as field-proven.
        for d in sorted((ROOT / "skills").iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            tier = re.search(r"(?m)^proof:\s*(\S+)",
                             (d / "SKILL.md").read_text(encoding="utf-8")).group(1)
            guide = (DOCS / "missions" / f"{d.name}.md").read_text(encoding="utf-8")
            m = re.search(r"(?m)^> \*\*Proof:\*\*\s*(\S+)", guide)
            self.assertIsNotNone(m, f"docs/missions/{d.name}.md has no Proof callout")
            self.assertEqual(m.group(1), tier,
                             f"docs/missions/{d.name}.md Proof tier != skills/{d.name} frontmatter")

    def test_mission_guides_show_autonomy(self):
        # #92 review: autonomy is duplicated on the SKILL frontmatter and the guide callout; without a
        # consistency check a later level change leaves one surface stale. Bind them.
        for d in sorted((ROOT / "skills").iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            level = re.search(r"(?m)^autonomy:\s*(L\d)",
                              (d / "SKILL.md").read_text(encoding="utf-8")).group(1)
            guide = (DOCS / "missions" / f"{d.name}.md").read_text(encoding="utf-8")
            m = re.search(r"(?m)^> \*\*Autonomy:\*\*\s*(L\d)", guide)
            self.assertIsNotNone(m, f"docs/missions/{d.name}.md has no Autonomy callout")
            self.assertEqual(m.group(1), level,
                             f"docs/missions/{d.name}.md Autonomy != skills/{d.name} frontmatter")

    def test_verify_manifest_fields_named_in_schema(self):
        # Issue #170: verify.py's no-gh lane required manifest["review"]["artifact"],
        # a field the evidence-manifest §1 schema never declared — a worker authoring
        # its manifest against the schema doc alone produced one the gate failed
        # closed. Every manifest field verify.py reads must be named in the §1 JSON
        # schema. Element reads over list fields (criteria[].id) are covered by the
        # schema's inline object shape, not by this check.
        schema_doc = (RUNTIME / "evidence-manifest.md").read_text(encoding="utf-8")
        block = re.search(r"```json\n(.*?)```", schema_doc, re.DOTALL).group(1)
        # Top-level keys sit at 2-space indent; each key's chunk runs to the next key.
        chunks, current = {}, None
        for line in block.splitlines():
            key = re.match(r'^  "([a-z_]+)":', line)
            if key:
                current = key.group(1)
                chunks[current] = line
            elif current:
                chunks[current] += "\n" + line
        src = (ROOT / "runtime" / "scripts" / "verify.py").read_text(encoding="utf-8")
        # Literal reads — the manifest handle is always `m`.
        reads = set(re.findall(r'\bm\.get\("([a-z_]+)"', src))
        # Nested reads — (m.get("p") or {}).get("s"), or an alias assigned from
        # m.get("p") and later alias.get("s"): s must appear inside p's chunk.
        nested = set(re.findall(r'\(m\.get\("([a-z_]+)"\) or \{\}\)\.get\("([a-z_]+)"\)', src))
        aliases = dict(re.findall(r'(\w+) = m\.get\("([a-z_]+)"\)(?: or \{\})?', src))
        for alias, parent in aliases.items():
            nested |= {(parent, sub) for sub in
                       re.findall(rf'\b{alias}\.get\("([a-z_]+)"\)', src)}
        # Dynamic reads — handle.get(var) where var loops over a literal tuple in
        # the same comprehension/loop (m.get(f), intent.get(k), prov.get(k));
        # resolve each literal in the tuple against the handle's parent.
        for var, vals, handle in re.findall(
                r"for (\w+) in \(([^)]*)\)[^\]]*?\b(\w+)\.get\(\1\)", src, re.DOTALL):
            lits = set(re.findall(r'"([a-z_]+)"', vals))
            if handle == "m":
                reads |= lits
            elif handle in aliases:
                nested |= {(aliases[handle], lit) for lit in lits}
        missing = sorted(reads - set(chunks))
        self.assertEqual(
            missing, [],
            f"verify.py reads manifest fields the §1 schema never declares: {missing}",
        )
        bad = sorted((p, s) for p, s in nested if s not in chunks.get(p, ""))
        self.assertEqual(
            bad, [],
            f"verify.py reads nested manifest fields the §1 schema never declares: {bad}",
        )

    def test_verify_gate_doc_enumerates_every_orca_env_read(self):
        # Issue #177: docs/verify-gate.md is the trust-boundary doc an operator
        # audits to learn which env must be scrubbed, yet its enumeration omitted
        # ORCA_NO_GH / ORCA_LIGHTING while verify-gate.sh honored both — and
        # ORCA_NO_GH silently downgrades review verification to the local-artifact
        # lane. Every ORCA_* the script reads must appear in the doc, and the
        # no-gh downgrade must be stated in the trust-boundary section.
        script = (RUNTIME / "scripts" / "verify-gate.sh").read_text(encoding="utf-8")
        # Actual reads: ${ORCA_X:-…} expansions and $ORCA_X references.
        reads = set(re.findall(r"\$\{?(ORCA_[A-Z_]+)\b", script))
        doc = (DOCS / "verify-gate.md").read_text(encoding="utf-8")
        missing = sorted(v for v in reads if v not in doc)
        self.assertEqual(
            missing, [],
            f"verify-gate.sh reads env vars docs/verify-gate.md never names: {missing}",
        )
        _, heading, trust = doc.partition("## Trust boundary")
        self.assertTrue(heading, "docs/verify-gate.md has no trust-boundary section")
        self.assertIn(
            "ORCA_NO_GH", trust,
            "the trust-boundary section never names ORCA_NO_GH — the no-gh lane's "
            "review-authority downgrade is undisclosed",
        )
        self.assertIn(
            "downgrade", trust.lower(),
            "the trust-boundary section names ORCA_NO_GH without stating its "
            "review-authority downgrade",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
