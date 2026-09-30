"""Current-status claims in TODOS.md, docs/ops.md and runtime/dispatch-lifecycle.md.

Each surface drifted from the state it describes: TODOS.md said no 2026-09-28
release-readiness finding had been filed after #510-#525 were; docs/ops.md said the
workflow directory held three workflows with no publishing job while release.yml and
publish-dist.yml publish on tags; dispatch-lifecycle.md called v1.4.209 the live pin
after runtime/pins.json advanced to v1.4.215. Expectations are derived from the
authoritative source (pins.json, the pin-it run records, the workflow files) where the
tree holds one; the tracker snapshot, which the tree cannot re-read, is frozen below.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/ravidsrk/orca-fleet"

# Tracker snapshot at the 2026-09-30 sweep T0 (independently triaged): the release-readiness
# review's findings were filed as #510-#525 under this label; three were still open. The
# road-to-1.0 epic is #526. TODOS.md must point at the live query, not restate a count.
READINESS_LABEL = "release-readiness-2026-09-28"
READINESS_FILED = (510, 525)
READINESS_OPEN_AT_T0 = (511, 515, 518)
ROAD_TO_1_0 = 526


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def flat(text):
    return " ".join(text.split())


class TodosPointsAtTheFiledReadinessIssues(unittest.TestCase):
    TEXT = read("TODOS.md")

    def entry(self):
        m = re.search(r"(?ms)^- \*\*The 2026-09-28 release-readiness review\*\*.*?(?=^- \*\*|\Z)", self.TEXT)
        self.assertIsNotNone(m, "TODOS.md lost its 2026-09-28 release-readiness entry")
        return flat(m.group(0))

    def test_no_claim_that_nothing_was_filed(self):
        entry = self.entry()
        for stale in ("none of its findings is filed", "not filed", "filing them is"):
            self.assertNotIn(stale, entry, f"TODOS.md still says {stale!r} after #510-#525 were filed")
        # Paraphrases of the same stale claim: a finding with no issue, or filing still to come.
        for pattern in (r"(?i)\b(no|none of (its|the|these))\s+findings?\b[^.]{0,40}\b(filed|issues?|tracked)\b",
                        r"(?i)\b(not|never|yet to be)\s+(yet\s+)?(filed|tracked)\b", r"(?i)\bunfiled\b"):
            with self.subTest(pattern=pattern):
                self.assertNotRegex(entry, pattern, "TODOS.md says a 2026-09-28 finding has no issue")
        lo, hi = READINESS_FILED
        self.assertRegex(entry, rf"findings are filed as #{lo}[–-]#?{hi}")

    def test_links_the_live_label_query_and_the_filed_range(self):
        entry = self.entry()
        self.assertIn(f"{REPO_URL}/issues?q=label%3A{READINESS_LABEL}", entry)
        lo, hi = READINESS_FILED
        self.assertRegex(entry, rf"#{lo}[–-]#?{hi}")

    def test_names_the_open_findings_and_the_epic_as_links(self):
        entry = self.entry()
        for n in READINESS_OPEN_AT_T0 + (ROAD_TO_1_0,):
            with self.subTest(issue=n):
                self.assertIn(f"]({REPO_URL}/issues/{n})", entry)

    def test_keeps_the_historical_review_pointer(self):
        self.assertIn("(docs/reviews/2026-09-28-release-readiness-review.md)", self.entry())


class OpsRollbackNamesThePublishingWorkflows(unittest.TestCase):
    TEXT = read("docs/ops.md")
    WORKFLOWS = ROOT / ".github" / "workflows"

    def step(self, n):
        m = re.search(rf"(?ms)^{n}\. .*?(?=^\d+\. |^## |\Z)", self.TEXT.split("## Incident", 1)[1])
        self.assertIsNotNone(m, f"docs/ops.md incident step {n} is missing")
        return flat(m.group(0))

    def publishing_workflows(self):
        # A workflow publishes when a tag push triggers it and it holds write access.
        out = set()
        for wf in self.WORKFLOWS.glob("*.yml"):
            body = wf.read_text(encoding="utf-8")
            if re.search(r"(?m)^\s+tags:", body) and "contents: write" in body:
                out.add(wf.name)
        return out

    def test_the_repo_really_has_publishing_workflows(self):
        # The two documented publishers must stay; a further tag publisher is legitimate and
        # test_rollback_separates_merge_from_publication already requires step 4 to name it.
        self.assertLessEqual({"release.yml", "publish-dist.yml"}, self.publishing_workflows())

    def test_rollback_does_not_claim_a_closed_workflow_list(self):
        step = self.step(4)
        self.assertNotIn("contains only", step)
        self.assertNotIn("no deploy job", step)
        # Paraphrases of a closed list: "the only workflows are …", "no other workflow", "no publishing job".
        for pattern in (r"(?i)\b(only|sole)\b[^.]{0,30}\bworkflows?\b", r"(?i)\bworkflows?\b[^.]{0,30}\b(are|is) (only|just)\b",
                        r"(?i)\bno other workflows?\b", r"(?i)\bno (publishing|release|deploy)\w* (job|workflow)s?\b"):
            with self.subTest(pattern=pattern):
                self.assertNotRegex(step, pattern, "rollback claims a closed workflow list")
        for name in re.findall(r"[\w.-]+\.yml", step):
            with self.subTest(workflow=name):
                self.assertTrue((self.WORKFLOWS / name).is_file(), f"rollback names absent {name}")

    def test_rollback_separates_merge_from_publication(self):
        step = self.step(4)
        for wf in sorted(self.publishing_workflows()):
            with self.subTest(workflow=wf):
                self.assertIn(wf, step)
        self.assertIn("git revert -m 1 <merge-sha>", step)
        # A merge changes the tree clones and the marketplace install; only tags publish versions.
        self.assertNotIn("publishes nothing", step)
        self.assertIn("marketplace", step)
        self.assertIn("new version", step, "a bad release is corrected with a new version, not a re-tag")
        self.assertIn("exact cut", step, "rollback must route re-publication through the cut authorization")

    def test_a_published_release_is_never_retagged(self):
        step = self.step(4)
        self.assertIn("a published bad release is never re-tagged or deleted", step,
                      "rollback lost the immutable-tag promise")
        for m in re.finditer(r"(?i)\bre-?tag\w*", step):
            with self.subTest(claim=step[max(0, m.start() - 40):m.end()]):
                self.assertRegex(step[max(0, m.start() - 40):m.start()], r"(?i)\b(never|not|no)\b",
                                 "rollback permits re-tagging a published release")

    def test_exact_cut_authorization_rule_is_intact(self):
        self.assertIn(
            "The maintainer must authorize the exact cut SHA and version before creating or publishing its tag.",
            flat(self.TEXT))

    def test_incident_poll_targets_main_push_runs_and_handles_stale_or_absent(self):
        step = self.step(1)
        m = re.search(r"`(gh run list [^`]*)`", step)
        self.assertIsNotNone(m, "incident step 1 lost its external polling query")
        query = m.group(1)
        self.assertTrue((self.WORKFLOWS / "validate.yml").is_file())
        # The same filter main-health.yml applies, so an in-progress run never pages.
        health = (self.WORKFLOWS / "main-health.yml").read_text(encoding="utf-8")
        for tok in ("--workflow validate.yml", "--branch main", "--event push", "--status completed",
                    "updatedAt"):
            self.assertIn(tok, health, f"main-health.yml no longer polls with {tok!r}")
            with self.subTest(token=tok):
                self.assertIn(tok, query)
        for tok in ("stale", "absent", "success", "#528"):
            with self.subTest(handling=tok):
                self.assertIn(tok, step)


    def test_external_monitor_claims_bind_to_source_and_drill(self):
        step = self.step(1)
        for token in ("outside Actions", "paused", "scripts/external-ci-monitor.py",
                      "24 hours", "T-13-external-monitor-drill.txt", "#537"):
            with self.subTest(token=token):
                self.assertIn(token, step)
        self.assertNotIn("No such monitor is installed yet", step)
        self.assertTrue((ROOT / "scripts/external-ci-monitor.py").is_file())
        receipt = read("docs/completion/evidence/T-13-external-monitor-drill.txt")
        self.assertIn("36146072394", receipt)
        self.assertIn("https://github.com/ravidsrk/orca-fleet/issues/537", receipt)
        self.assertIn("scheduled heartbeat firing are not claimed", receipt)


class DispatchLifecycleNamesTheCurrentPin(unittest.TestCase):
    TEXT = read("runtime/dispatch-lifecycle.md")
    PIN = json.loads(read("runtime/pins.json"))["orca"]["version"]

    def pin_report(self):
        # The run record whose title advances the pin TO the pinned version.
        hits = [p for p in sorted((ROOT / "docs" / "runs").glob("*pin-it-*.md"))
                if re.search(rf"→ {re.escape(self.PIN)}\)", p.read_text(encoding="utf-8").splitlines()[0])]
        self.assertEqual(len(hits), 1, f"expected one pin-it record advancing to {self.PIN}: {hits}")
        return hits[0].relative_to(ROOT).as_posix()

    def test_live_probe_section_names_the_pinned_version_and_its_witness(self):
        section = flat(self.TEXT.split("## Live probes owed (pin-it)", 1)[1])
        self.assertIn(f"The live PIN is {self.PIN} (`{self.pin_report()}`", section)

    def test_no_other_version_is_called_live_or_current(self):
        text = flat(self.TEXT)
        for m in re.finditer(r"(?i)(live pin|current pin|current at|CURRENT at|pin is|currently pins?|currently pinned(?: at| to)?"
                             r"|now pins?|pins? currently|pinned version is)\W{0,4}(v?1\.4\.\d+)", text):
            with self.subTest(claim=m.group(0)):
                self.assertEqual(m.group(2).lstrip("v"), self.PIN.lstrip("v"))
        for m in re.finditer(r"(?i)(v?1\.4\.\d+)[^.;()]{0,12}the (live|current) PIN"
                             r"|(v?1\.4\.\d+) is (?:what|the version) [^;()]{0,20}\b(?:currently|now) pins?", text):
            with self.subTest(claim=m.group(0)):
                self.assertEqual((m.group(1) or m.group(3)).lstrip("v"), self.PIN.lstrip("v"))

    def test_historical_witnesses_and_citations_survive(self):
        for token in ("docs/runs/2026-09-16-pin-it-416", "docs/runs/2026-09-23-pin-it-488.md",
                      "docs/runs/2026-09-20-pin-it-427.md", "`local-worker-start.ts:263`",
                      "`worker-start-readiness-settlement.ts:91-129`", "`cli/specs/skills.ts:50-56`",
                      "`orchestration-worker-specs.ts:101`", "witnessed at v1.4.204"):
            with self.subTest(token=token):
                self.assertIn(token, self.TEXT)

    def test_parked_live_probes_survive(self):
        section = flat(self.TEXT.split("## Live probes owed (pin-it)", 1)[1])
        for probe in ("doctor verdict shapes", "legacy-takeover live replay",
                      "roster/remote/OS/isolated-runtime probes"):
            with self.subTest(probe=probe):
                self.assertIn(probe, section)
        self.assertIn("live re-probe stays parked", flat(self.TEXT))


if __name__ == "__main__":
    unittest.main()
