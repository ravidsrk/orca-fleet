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
import importlib.util
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)
DOCS = ROOT / "docs"
RUNTIME = ROOT / "runtime"


class TestDocsNavigation(unittest.TestCase):

    def test_plugin_version_matches_changelog_heading(self):
        # Issue #209: plugin.json lagged Unreleased. Version is one number,
        # written in three places — they must agree with the latest dated
        # CHANGELOG heading.
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        market = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        version = plugin["version"]
        self.assertEqual(market["metadata"]["version"], version)
        self.assertEqual(market["plugins"][0]["version"], version)
        heading = re.search(
            r"^## \[(\d+\.\d+\.\d+)\] - ",
            (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        self.assertIsNotNone(heading, "CHANGELOG has no dated version heading")
        self.assertEqual(
            heading.group(1),
            version,
            "plugin.json version does not match the latest dated CHANGELOG heading",
        )

    def test_ops_doc_names_accounts_and_incident(self):
        # Issue #215: bus-factor-1 with no inventory and no 2 a.m. paragraph.
        # Issue #233 (G-20): step 4's merge-shaped rollback was unbound —
        # reverting `git revert -m 1` stayed green. Pin it on this test; it
        # already owns the 2 a.m. Incident section.
        text = (DOCS / "ops.md").read_text(encoding="utf-8")
        for tok in ("GitHub", "plugin marketplace", "greptile", "agentskills",
                    "Incident", "Rollback"):
            self.assertIn(tok, text, f"docs/ops.md lost its {tok!r} surface")
        # Scoped per #244 review: the full actionable command must live in the
        # numbered rollback step itself — the bare substring anywhere in the
        # doc (e.g. only in explanatory prose) is not enough.
        m = re.search(r"(?ms)^\d+\. Rollback.*?(?=^\d+\. |\Z)", text)
        step = m.group(0) if m else ""
        self.assertIn(
            "git revert -m 1 <merge-sha>",
            step,
            "docs/ops.md rollback step lost its actionable -m 1 command",
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertRegex(
            readme,
            r'href="docs/ops\.md"|\]\(docs/ops\.md\)',
            "README has no working Ops navigation link",
        )

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
            # First-sentence cut is deliberate (clean-sweep caveat names
            # `runtime-prove` without composing it) — see
            # validate.guide_declared_protocol_names.
            declared = set(validate.guide_declared_protocol_names(skill))
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
            named = set(validate.BACKTICK_RE.findall(section.group(1)))
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
            tier = re.search(r"(?m)^  proof:\s*(\S+)",
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
            level = re.search(r"(?m)^  autonomy:\s*(L\d)",
                              (d / "SKILL.md").read_text(encoding="utf-8")).group(1)
            guide = (DOCS / "missions" / f"{d.name}.md").read_text(encoding="utf-8")
            m = re.search(r"(?m)^> \*\*Autonomy:\*\*\s*(L\d)", guide)
            self.assertIsNotNone(m, f"docs/missions/{d.name}.md has no Autonomy callout")
            self.assertEqual(m.group(1), level,
                             f"docs/missions/{d.name}.md Autonomy != skills/{d.name} frontmatter")

    def test_every_changelog_release_has_a_cut_commit(self):
        # #274: nine dated CHANGELOG headings, no immutable ref binding any of them
        # to a commit. Tags live in the repo's ref namespace rather than in a
        # branch, so a fresh clone (and CI) cannot see one; docs/releases.json is
        # the committed half a checkout can actually verify.
        releases = json.loads((DOCS / "releases.json").read_text(encoding="utf-8"))["releases"]
        by_version = {r["version"]: r for r in releases}
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        headings = re.findall(r"(?m)^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})", changelog)
        self.assertTrue(headings, "CHANGELOG has no dated release headings")
        for version, _date in headings:
            self.assertIn(version, by_version, f"CHANGELOG {version} has no docs/releases.json row")
            row = by_version[version]
            self.assertRegex(row["commit"], r"^[0-9a-f]{40}$", version)
            self.assertEqual(row["tag"], f"v{version}")
            found = subprocess.run(
                ["git", "cat-file", "-e", f"{row['commit']}^{{commit}}"],
                cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            self.assertEqual(
                found.returncode, 0,
                f"docs/releases.json {version} names {row['commit'][:12]}, not a commit here",
            )

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
        # Key extraction, not substring: "artifact" in "artifact_path" must not count (#196).
        declared_nested = {
            parent: set(re.findall(r'"([a-z_]+)":', chunk))
            for parent, chunk in chunks.items()
        }
        bad = sorted((p, s) for p, s in nested if s not in declared_nested.get(p, set()))
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
        example = (ROOT / ".env.example").read_text(encoding="utf-8")
        missing_ex = sorted(v for v in reads if v not in example)
        self.assertEqual(
            missing_ex, [],
            f"verify-gate.sh reads env vars .env.example never names: {missing_ex}",
        )
        # #200 review pinned "ORCA_EXECUTE_NC is an unimplemented flag that fail-closes"; #255
        # implemented the replay, so the doc must now describe what it actually DOES — the control
        # is executed in a throwaway worktree — and #256's rule that the two review-waiver lanes
        # require it. An inverted assertion, not a dropped one: the doc must not drift back into
        # promising a replay that is not there, nor omit the lanes that depend on it.
        self.assertRegex(
            doc, r"(?is)ORCA_EXECUTE_NC.{0,600}(executes the\s+negative control|throwaway worktree)",
            "docs/verify-gate.md must describe what --execute-nc does: EXECUTE the negative "
            "control in a throwaway worktree at head_sha",
        )
        for lane in ("ORCA_NO_GH", "ORCA_LIGHTING"):
            section = doc.split(f"- `{lane}`", 1)[1].split("\n- `", 1)[0]
            self.assertIn(
                "ORCA_EXECUTE_NC", section,
                f"{lane} waives the review, so the doc must say it requires ORCA_EXECUTE_NC (#256)",
            )
        _, heading, rest = doc.partition("## Trust boundary")
        self.assertTrue(heading, "docs/verify-gate.md has no trust-boundary section")
        # Bound to this H2 — a later sibling section must not keep this green (#200).
        trust = rest.split("\n## ", 1)[0]
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


class QuotationsAreAttributedToWhatTheySay(unittest.TestCase):
    """#304: a research file carried a quotation its cited source does not contain.

    The sentence was a paraphrase of a real rule from a DIFFERENT article. A repository whose
    thesis is that claims must be checkable does not get to carry an unchecked quotation, so the
    fabricated one is pinned here by its text — if it ever comes back, this fails.
    """

    PLAN = ROOT / "docs" / "research" / "2026-08-28-forward-roadmap-and-defensibility-plan.md"

    def test_the_fabricated_sentence_is_gone(self):
        text = self.PLAN.read_text(encoding="utf-8")
        body = "\n".join(ln for ln in text.splitlines() if "Correction (#304)" not in ln)
        self.assertNotIn("the level you can safely reach is exactly the level you can cheaply "
                         "prove", body,
                         "the misattributed quotation is back in the body")

    def test_the_replacement_names_the_article_it_is_from(self):
        text = self.PLAN.read_text(encoding="utf-8")
        self.assertIn("Back pressure is the rule that you can only hand a loop as much autonomy "
                      "as you can cheaply and reliably verify, and not one inch more.", text,
                      "the verified sentence is not there")
        self.assertIn("Software Factories, Light and Dark", text,
                      "the quotation does not name the article it comes from")
        self.assertIn("addyosmani.com/blog/software-factories", text,
                      "the quotation is not linked to a source a reader can check")


class EveryReleaseHasTheTagItDescribes(unittest.TestCase):
    """#307: docs/releases.json bound nine versions to commits and `git tag` was empty.

    The mapping was true and the artifact it describes did not exist — no version was fetchable by
    tag, and `git describe` had nothing to work with.

    The first cut SKIPPED when no release tag was present, reasoning that an unfetched clone
    cannot prove anything about tags. That made the gate toothless in exactly the state it was
    written for — the repository's own — and CI fetches tags anyway (`fetch-depth: 0`), so the
    skip could not tell "not fetched" from "never published" where it mattered (PR #308 review,
    P1). It fails now. A gate that cannot fire in the condition it was added to detect is the
    shape this catalog refuses.
    """

    RELEASES = ROOT / "docs" / "releases.json"

    def _releases(self):
        return json.loads(self.RELEASES.read_text(encoding="utf-8"))["releases"]

    @staticmethod
    def _git(*args):
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)

    def test_every_release_names_a_commit_that_exists(self):
        # True with or without tags — the half that never needs a fetch.
        for rel in self._releases():
            with self.subTest(version=rel["version"]):
                self.assertEqual(
                    self._git("cat-file", "-e", rel["commit"] + "^{commit}").returncode, 0,
                    f"{rel['tag']} names a commit this repository does not have")

    def test_every_release_is_tagged_at_the_commit_it_names(self):
        releases = self._releases()
        present = {t for t in self._git("tag").stdout.split()}
        wanted = {rel["tag"] for rel in releases}
        missing = sorted(wanted - present)
        self.assertEqual(
            missing, [],
            f"released but untagged: {missing}\n"
            "docs/releases.json binds these versions to commits, so the mapping is true and the "
            "tags it describes do not exist — no version is fetchable by tag and `git describe` "
            "has nothing to work with (#307).\n"
            "Publish them with the command in docs/releases.json's _comment:\n"
            "  jq -r '.releases[] | \"git tag -a \\(.tag) \\(.commit) -m \\\"orca-fleet "
            "\\(.version)\\\"\"' docs/releases.json | sh && git push origin --tags\n"
            "If this is a shallow or --no-tags checkout, fetch them first "
            "(actions/checkout with fetch-depth: 0).")
        for rel in releases:
            with self.subTest(version=rel["version"]):
                at = self._git("rev-list", "-n", "1", rel["tag"]).stdout.strip()
                self.assertEqual(at, rel["commit"],
                                 f"{rel['tag']} points at {at[:12]}, not the commit "
                                 f"docs/releases.json names ({rel['commit'][:12]})")

    def test_the_file_documents_how_to_publish_them(self):
        # The durable half: a reader who finds the tags missing must be told what to run.
        comment = json.loads(self.RELEASES.read_text(encoding="utf-8"))["_comment"]
        self.assertIn("git tag -a", comment)
        self.assertIn("git push origin --tags", comment)


if __name__ == "__main__":
    unittest.main(verbosity=2)
