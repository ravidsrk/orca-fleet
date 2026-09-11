#!/usr/bin/env python3
"""Contract tests for runtime/scripts/egress.py.

Three properties define the receipt ledger: it is content-free (the payload text
never lands on disk), it is tamper-evident (an edited line breaks the chain), and
it is fail-closed on write (a sink that cannot receipt must not send). Each has a
test that would fail if the property were quietly dropped.
"""
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EGRESS = ROOT / "runtime" / "scripts" / "egress.py"


class EgressBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="egress-")
        self.ledger = Path(self.tmp) / "state" / "egress.jsonl"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_egress(self, *args, ledger=None, env=None):
        return subprocess.run(
            [sys.executable, str(EGRESS), "--ledger", str(ledger or self.ledger), *args],
            capture_output=True, text=True, env=env,
        )

    def write_one(self, sink="pr-open", host="github.com", payload_class="pr-body",
                  consent="grant:pr-open", extra=()):
        return self.run_egress("write", "--sink", sink, "--host", host,
                               "--payload-class", payload_class, "--consent", consent, *extra)

    def lines(self):
        return [ln for ln in self.ledger.read_text(encoding="utf-8").splitlines() if ln]

    def records(self):
        return [json.loads(ln) for ln in self.lines()]


class TestWrite(EgressBase):
    def test_write_creates_the_ledger_and_prints_an_id(self):
        r = self.write_one()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.ledger.exists())
        self.assertRegex(r.stdout.strip(), r"^[0-9a-f]{64}$")

    def test_record_carries_every_contracted_field(self):
        self.write_one()
        record = self.records()[0]
        for field in ("id", "ts", "sink", "host", "payload_class", "bytes",
                      "payload_sha256", "consent", "prev"):
            self.assertIn(field, record)

    def test_ledger_file_is_owner_only(self):
        self.write_one()
        mode = stat.S_IMODE(self.ledger.stat().st_mode)
        self.assertEqual(mode, 0o600, f"the ledger must be 0600, got {oct(mode)}")

    def test_first_record_has_an_empty_prev(self):
        self.write_one()
        self.assertEqual(self.records()[0]["prev"], "")

    def test_second_record_chains_to_the_first_raw_line(self):
        self.write_one()
        first_raw = self.lines()[0]
        self.write_one(sink="issue-close")
        expected = hashlib.sha256(first_raw.encode("utf-8")).hexdigest()
        self.assertEqual(self.records()[1]["prev"], expected)

    def test_payload_file_is_hashed_and_never_stored(self):
        payload = Path(self.tmp) / "body.md"
        secret_text = "the entire PR body, which must never reach the ledger"
        payload.write_text(secret_text, encoding="utf-8")
        r = self.write_one(extra=("--payload-file", str(payload)))
        self.assertEqual(r.returncode, 0, r.stderr)
        record = self.records()[0]
        self.assertEqual(record["payload_sha256"],
                         hashlib.sha256(secret_text.encode("utf-8")).hexdigest())
        self.assertEqual(record["bytes"], len(secret_text.encode("utf-8")))
        self.assertNotIn(secret_text, self.ledger.read_text(encoding="utf-8"))

    def test_payload_sha_may_be_absent_when_a_subprocess_owns_the_bytes(self):
        self.write_one()
        self.assertIsNone(self.records()[0]["payload_sha256"])

    def test_a_malformed_payload_sha_is_refused(self):
        r = self.write_one(extra=("--payload-sha256", "not-a-hash"))
        self.assertEqual(r.returncode, 3)

    def test_an_unwritable_ledger_fails_closed_with_exit_3(self):
        # A directory where the ledger file belongs: the append cannot succeed,
        # whatever the process's privileges are.
        blocked = Path(self.tmp) / "blocked" / "egress.jsonl"
        blocked.mkdir(parents=True)
        r = self.run_egress("write", "--sink", "s", "--host", "h", "--payload-class", "c",
                            "--consent", "k", ledger=blocked)
        self.assertEqual(r.returncode, 3, "a sink that cannot receipt must not send")
        self.assertIn("EGRESS_RECEIPT_FAILED", r.stderr)

    def test_a_newline_in_a_field_is_refused(self):
        r = self.write_one(payload_class="pr\nbody")
        self.assertEqual(r.returncode, 3)

    def test_the_ledger_env_var_is_honored(self):
        env = dict(os.environ)
        env["ORCA_EGRESS_LEDGER"] = str(self.ledger)
        r = subprocess.run(
            [sys.executable, str(EGRESS), "write", "--sink", "s", "--host", "h",
             "--payload-class", "c", "--consent", "k"],
            capture_output=True, text=True, env=env, cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.ledger.exists())


class TestVerify(EgressBase):
    def test_an_intact_chain_verifies(self):
        self.write_one()
        self.write_one(sink="issue-close")
        r = self.run_egress("verify")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("2 receipt(s)", r.stdout)

    def test_a_missing_ledger_is_an_empty_intact_chain(self):
        r = self.run_egress("verify")
        self.assertEqual(r.returncode, 0)
        self.assertIn("0 receipt(s)", r.stdout)

    def test_an_edited_earlier_line_breaks_the_chain(self):
        self.write_one()
        self.write_one(sink="issue-close")
        lines = self.lines()
        record = json.loads(lines[0])
        record["host"] = "elsewhere.invalid"
        lines[0] = json.dumps(record, separators=(",", ":"))
        self.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        r = self.run_egress("verify")
        self.assertEqual(r.returncode, 3)
        self.assertIn("TAMPER", r.stderr)

    def test_an_edited_field_breaks_its_own_record_id(self):
        self.write_one()
        record = self.records()[0]
        record["consent"] = "grant:something-else"
        self.ledger.write_text(json.dumps(record, separators=(",", ":")) + "\n", encoding="utf-8")
        r = self.run_egress("verify")
        self.assertEqual(r.returncode, 3)
        self.assertIn("id does not match", r.stderr)

    def test_a_deleted_line_breaks_the_chain(self):
        self.write_one()
        self.write_one(sink="issue-close")
        self.write_one(sink="deploy-trigger")
        lines = self.lines()
        del lines[1]
        self.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        r = self.run_egress("verify")
        self.assertEqual(r.returncode, 3)

    def test_an_unparseable_line_breaks_the_chain(self):
        self.write_one()
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write("not json at all\n")
        r = self.run_egress("verify")
        self.assertEqual(r.returncode, 3)
        self.assertIn("unparseable", r.stderr)

    def test_appending_after_a_verify_keeps_the_chain_intact(self):
        self.write_one()
        self.run_egress("verify")
        self.write_one(sink="comment")
        self.assertEqual(self.run_egress("verify").returncode, 0)


class TestAnchoredHead(EgressBase):
    """#312: a hash chain is tamper-evident against EDITS to a known chain. It says nothing about a
    chain replaced wholesale, because the replacement is internally perfect — it starts at its own
    genesis and every link checks out. Only a head digest kept where the writer cannot reach it
    tells the two apart."""

    def _head(self):
        """Computed from the ledger, not scraped from the output under test — an expectation read
        out of the thing being tested cannot disagree with it."""
        lines = self.lines()
        return hashlib.sha256(lines[-1].encode("utf-8")).hexdigest() if lines else ""

    def test_verify_reports_the_head_so_there_is_something_to_anchor(self):
        self.write_one()
        r = self.run_egress("verify")
        self.assertEqual(r.returncode, 0, r.stderr)
        want = hashlib.sha256(self.lines()[-1].encode("utf-8")).hexdigest()
        self.assertIn(want, r.stdout, f"verify must print the head digest: {r.stdout}")

    def test_a_wholesale_rewrite_is_caught_by_the_anchor(self):
        self.write_one()
        self.write_one(sink="issue-close")
        anchored = self._head()
        # The rewrite uses the SAME tool, legally: remove the ledger and write two fresh receipts
        # with a different host. The chain that results is flawless on its own terms.
        self.ledger.unlink()
        self.write_one(host="evil.example")
        self.write_one(sink="issue-close", host="evil.example")
        plain = self.run_egress("verify")
        self.assertEqual(plain.returncode, 0,
                         "a rewritten chain is internally intact — that is the finding, not a bug")
        r = self.run_egress("verify", "--expect-head", anchored)
        self.assertEqual(r.returncode, 3, f"the anchor must catch the rewrite: {r.stdout}{r.stderr}")
        self.assertIn("TAMPER", r.stderr)

    def test_the_anchor_passes_on_the_chain_it_names(self):
        self.write_one()
        self.write_one(sink="issue-close")
        r = self.run_egress("verify", "--expect-head", self._head())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("anchored", r.stdout)

    def test_an_appended_receipt_moves_the_head_past_the_anchor(self):
        # An anchor pins one moment. Honest growth past it is not tamper, but it is not the
        # anchored chain either — the caller re-anchors, and until it does, verify says so.
        self.write_one()
        anchored = self._head()
        self.write_one(sink="issue-close")
        self.assertEqual(self.run_egress("verify").returncode, 0)
        self.assertEqual(self.run_egress("verify", "--expect-head", anchored).returncode, 3)


class TestGrants(EgressBase):
    def test_grants_lists_each_consent_once(self):
        self.write_one(consent="grant:pr-open")
        self.write_one(consent="grant:pr-open", sink="pr-comment")
        self.write_one(consent="grant:deploy", sink="deploy-trigger")
        r = self.run_egress("grants", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = json.loads(r.stdout)
        self.assertEqual([row["consent"] for row in rows], ["grant:deploy", "grant:pr-open"])
        by_key = {row["consent"]: row for row in rows}
        self.assertEqual(by_key["grant:pr-open"]["uses"], 2)
        self.assertEqual(by_key["grant:pr-open"]["sinks"], ["pr-comment", "pr-open"])

    def test_grants_on_an_empty_ledger_says_so(self):
        r = self.run_egress("grants")
        self.assertEqual(r.returncode, 0)
        self.assertIn("no consents recorded", r.stdout)

    def test_grants_human_output_names_the_host(self):
        self.write_one(host="api.github.com")
        r = self.run_egress("grants")
        self.assertIn("api.github.com", r.stdout)


class TestScriptShape(unittest.TestCase):
    def test_executable_and_shebanged(self):
        self.assertTrue(os.access(EGRESS, os.X_OK))
        self.assertTrue(EGRESS.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"))

    def test_help_exits_zero_and_names_the_subcommands(self):
        r = subprocess.run([sys.executable, str(EGRESS), "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        for sub in ("write", "verify", "grants"):
            self.assertIn(sub, r.stdout)

    def test_threat_model_is_stated_not_overclaimed(self):
        text = EGRESS.read_text(encoding="utf-8")
        self.assertIn("not an exfiltration control", text)

    def test_default_ledger_is_repo_local(self):
        self.assertIn('DEFAULT_LEDGER = ".orca/egress.jsonl"', EGRESS.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
