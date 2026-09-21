# U-SIG-2 — builder report (signed inventory + the retention anchor, #386)

Spec: `docs/runs/2026-09-20-sign-386/build-u-sig-2.md` @ 648fcf77 (sha256 356e2860…).
Range: 648fcf77..98fb8aae on `ravidsrk/sig-2` (four commits; the evidence commit follows).
Manifest: `docs/runs/2026-09-20-sign-386/u-sig-2-manifest.json` (report-path). Pack: matt (tdd, one worker).

## What was built

**1. `inventory.py sign` / `check --pubkey` / `write --key`.** The signature is over the document's ENTRY SET —
every block's `(path, sha256)` pairs, deduplicated and sorted, `json.dumps(separators=(",",":"))` — not over the
block text: order and block membership are presentation, and #315 already says the claim is the union. The
record is `{"entries": N, "inventory_sha256": sha256(canonical set)}` in dispatch-sign.py's `{record, sig_b64}`
envelope over `canonical_record(record, SIGNED_FIELDS)`, written as ONE line inside the first block:

    <!-- inventory-signature {"record": {"entries": 2, "inventory_sha256": "…"}, "sig_b64": "…"} -->

Neither `SHA_LINE` nor `TABLE_ROW` can match it, so `find_blocks`/`parse_entries` read past it unchanged (pinned:
`test_every_existing_shape_still_parses_with_the_envelope_present`, both shapes, same "N verified" before and
after). `sign` re-derives from disk first and refuses a stale or absent path (a stale hash is not something to
attest). `check --pubkey` refuses an unsigned inventory (exit 1, "UNSIGNED"), a set that differs from the signed
digest ("an entry was added, dropped or changed after signing"), a bad signature, a foreign key; a malformed
pubkey is could-not-run (exit 2). Without `--pubkey` the envelope is never read. `write --key` re-signs the
refreshed set; `write` alone leaves a now-stale envelope in place and says so on stderr — evidence is never
dropped silently, and `check --pubkey` will then refuse it, which is the honest state. The signer is loaded
lazily (`_dispatch_sign()`), so a bundle's plain write/check paths never import it.

**2. `run_report.py signed_inventory()` + `enforcement_key()`.** U-SIG-1's key resolution (`key_rev`: the pin
when it is on the grading base's ancestry, the base otherwise; the pin's own key when the base carries none) was
lifted out of `signed_transcript` into `enforcement_key(rev, root, base) -> (pin, at, why)` and both legs call it,
so they cannot disagree about whether enforcement is on. `signed_inventory` reads the envelope from the report
text `check_report` already loads (the report is written after the pin it names — reading it at the pin would
read nothing) and verifies it with `inventory.verify_signature` over the entries `check_entries` is about to
hash. G-4's absence rule is mirrored: no key + no envelope → `[]`; envelope + no key → refuse; key + no envelope
→ refuse; key + envelope → verify and bind. The ancestry shapes are covered through the shared helper
(`test_post_key_work_pinned_to_a_pre_key_fork_needs_a_signed_inventory`, `…keeps_the_unsigned_inventory`).
Tests: `SignedKeyFixture` now holds the shared key/verdict/ancestry helpers (no tests of its own);
`SignedTranscriptRequired` and `SignedInventoryRequired` both derive from it. The three transcript tests that
assert a clean bind with the key committed now also sign the inventory — one key switches both legs, and they
are the transcript's tests, so the inventory leg is satisfied rather than asserted on.

**3. `provenance.retention` (evidence-manifest.md §1 rule + JSON placeholder + the run-close paragraph) and
the compliance-provenance.md row.** The anchor is a Rekor-style transparency-log RECEIPT — `log_index`,
`entry_uuid`, `signature` over the signed inventory's digest (the same `inventory_sha256` the envelope carries)
— committed beside the inventory. Uploading is an OPTIONAL coordinator-side step recorded with an `egress.py`
receipt, never a gate dependency; no gate script makes a network call. The check owed is OFFLINE: fields present
and binding the digest. Said plainly in both places: PROVEN, once that check runs, is that the receipt covers
exactly these inventory bytes; NOT proven is that the log entry exists, is reachable or is trustworthy (a live
`entry_uuid` lookup the maintainer runs out of band); and `verify.py` TODAY checks only that `retention` is a
non-empty string when a standard is named — the field-binding check is specified, not implemented (verify.py is
out of this unit's scope; parked with a gate).

Byte budget: evidence-manifest.md is ridden by all 21 missions and clean-sweep sat at 33,997/34,000 activation
tokens. The new clauses were paid for by compressing narrative asides in the same file (the intro, the #279
history in the negative-control row, the 2026-09-10-review and flagship-quarantine asides, a few connectives) —
no rule was removed. 22,330 → 22,326 bytes, 160 → 158 lines; load 33,997 after.

## Evidence

- RED first: `SignedInventory` 14 F + 1 E on base (the first cut of `test_sign_refuses_a_report_with_no_inventory`
  passed on argparse's exit 2 for the unknown subcommand and was tightened to assert the parser's own message);
  `SignedInventoryRequired` 6/8 RED on base (the 2 unsigned-path pins pass on base by design).
- `tests` receipt (evidence-run.py, clean checkout of 98fb8aae before any artifact existed): exit 0, 258 tests,
  wtree 6e4826c8 == 98fb8aae^{tree}. Artifact `u-sig-2-tests.txt`.
- Negative control (evidence-run.py `--cwd` a scratch worktree at 98fb8aae with `inventory.py` + `run_report.py`
  restored from 648fcf77): exit 1, FAILED (failures=16, errors=8) — 24 RED, listed in the manifest. Artifact
  `u-sig-2-negctrl.txt`. Not witnessed: the two unsigned-path regression pins (pass on both sides by design; RED
  under the inverse mutation, seen by hand during development).
- `verify.py --manifest <this> --unit-class mutation --lighting lit --no-gh`: "NOTE: commands ledger FRESH — 1
  exit-0 record(s) bound to head_sha's tree 6e4826c86d24"; the three FAIL lines are the contract flags and
  `review.artifact` the integrator supplies, as for U-SIG-1.
- `python3 scripts/validate.py`: exit 0 — "All 21 missions valid; three-layer separation holds; evals valid."
- Full suite (`python3 -m unittest discover -s tests`, the CI runner) at 98fb8aae with the working tree carrying
  this manifest: "Ran 1897 tests in 303.800s / OK". `ruff check scripts runtime/scripts tests bench demo`: All checks passed.

## Parked

- verify.py's offline receipt field-binding check — specified in both docs, stated as not implemented; maintainer
  gate (G1 follow-up).
- `SignedInventoryRequired` re-runs `RunReportBinding`'s ~31 tests through the fixture inheritance, as the
  pre-existing `SignedTranscriptRequired` already did; a test-layout nit for review, not changed here.
