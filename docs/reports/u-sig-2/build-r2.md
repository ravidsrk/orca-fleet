# BUILD REPORT — U-SIG-2 round 2 (fix batch G-1..G-5)

unit=U-SIG-2 round=2 branch=ravidsrk/sig-2 head=0558cda9 (last content commit; the evidence
commit follows) base=origin/review/2026-09-20-sign-386 @ 749b5bad (merged as c91642ad — no conflict)
spec=docs/runs/2026-09-20-sign-386/build-u-sig-2-r2.md (frozen) pack=matt (test-first, one pack)
manifest=docs/runs/2026-09-20-sign-386/u-sig-2-r2-manifest.json lighting=lit
worker=task_243c2c439eaa / ctx_8c25f2e6f7fc window=07:08–07:4x IST 2026-09-21 (40-min box)

## What changed (production)

**G-1 — validity is an affirmative value.** `verify_signature` no longer returns `None` for
"verified" and a string for "why not". It returns the signed inventory digest and raises
`SignatureRefused` on every refusal; `decode_signature` turns a base64 error OR a wrong length
into `SignatureRefused("sig_b64 is malformed …")`. Both callers (`cmd_check`,
`run_report.signed_inventory`) catch the exception and then compare the returned digest to
`inventory_digest(entries)` — so the only path to "signature verified" runs through
`checkvalid` on real signature bytes. The M14 mutant (`return None` in the decode branch) now
produces `None` where a digest is demanded and is refused; its `verify_signature`-level twin
(M14b) likewise. The envelope format is untouched (U-SIG-1's).

**G-2 — the envelope lives only inside the blocks.** `find_signature` computes `find_blocks`
and accepts a `SIGNATURE_LINE` match only at `start < idx < end`; any match outside raises
`InventoryError("… sits outside every inventory block — not an envelope; refused")` (exit 2)
before anything is rewritten, so `sign` / `write --key` never touch prose (the reproduction in
review-standards R-1 now exits 2 with the document byte-identical). `_place_signature` still
appends inside the first block; a test now asserts the written envelope's index falls in a
`find_blocks` range (kills M13). `cmd_write` no longer reads the envelope on the no-key path:
`_stale_envelope()` is advisory only and swallows `InventoryError`, so plain `write` exits 0,
prints exactly the pre-#386 line, and writes the pre-#386 bytes — STD-R1's second half.
**Deviation note:** the tests and standards axes asked for a stray prose line to be IGNORED;
the frozen spec says REFUSED as a would-be forgery. The spec was followed (fail-closed; a
run-report author who pastes the example into prose gets a named exit-2, not a silent pass).

**G-3 / G-4** — both refusals already existed; each now has a killer test, and M12 / M15 die
on exactly that test.

**G-5** — `enforcement_key()` returns `(32 key bytes | None, at, why)`; a malformed pin returns
`at=None` with the refusal in `why`, which both legs already return verbatim. The two verbatim
parse copies in `signed_inventory` / `signed_transcript` are gone (`bytes.fromhex` appears once
in run_report.py). The transcript leg's own `sig_b64` decode keeps its own try with a message
that now names the transcript, not the pin.

## Tests (RED first, then GREEN)

11 new tests: 8 in `SignedInventory`, 3 in `SignedInventoryRequired`. Negative control
(`u-sig-2-r2-negctrl.txt`, evidence-run label `negative-control`): both scripts restored from
the round-1 head 5c87eb05 with the tests kept → **FAILED (failures=6, errors=1) = 7 RED**
(G-1 ×3 incl. the keyless forgery, G-2 ×3, G-5 ×1). The G-3/G-4 pins and the gate's malformed-
sig mirror are green pre-fix by design — those refusals held already; their proof is the kill.

Mutant re-run against the fixed code (`u-sig-2-r2-mutants.txt`), covering classes = 67 tests:

| mutant | result |
|---|---|
| M12 two envelope lines → first wins | KILLED — test_two_envelope_lines_are_refused |
| M13 envelope inserted at line 0 | KILLED — 15 FAIL + 2 ERROR (every sign→check roundtrip refuses the stray line; test_sign_places_the_envelope_inside_an_inventory_block) |
| M14 decode error → `return None` | KILLED — test_a_keyless_forgery_with_a_malformed_sig_b64_is_refused; gate mirror ERRORs |
| M14b verify_signature swallows SignatureRefused → None | KILLED — 3 RED |
| M15 non-envelope line → unsigned | KILLED — test_a_signature_line_that_is_not_an_envelope_is_refused_not_unsigned |
| M16 stray line outside the blocks ignored | KILLED — 3 RED (both directions + the gate) |
| M17 enforcement_key returns the raw pin blob | KILLED — 4 RED |

`tests` receipt (evidence-run, `u-sig-2-r2-tests.txt`): `python3 -m unittest tests.test_inventory
tests.test_run_report` at 0558cda9 → OK, `wtree == 0558cda9^{tree}` (8c29372e). Full
`python3 -m unittest discover -s tests` on the head tree: **Ran 1908 tests in 345.136s / OK**.
`python3 scripts/validate.py` → "All 21 missions valid; three-layer separation holds; evals
valid." after `scripts/gen-badges.py` (1798 → 1809). `ruff check` on the four touched files:
All checks passed.

## Round-1 Required → answer

| finding | answer |
|---|---|
| TEST-F1 (M14 keyless forgery) | G-1: fixed 46c52a08; killer + valid-base64 tests; M14/M14b killed |
| TEST-F2 / BOT-1 / STD-R1 / SPEC-F1 (document-wide envelope, sign overwrites prose, write exits 2) | G-2: fixed 46c52a08; 4 inventory tests + 1 gate test; M13/M16 killed; unsigned write byte-identical |
| TEST-F3 (M12) | G-3: pinned 46c52a08; M12 killed |
| TEST-F4 (M15) | G-4: pinned 46c52a08; M15 killed |
| STD-R2 (pin parse duplicated) | G-5: fixed d697e361; one parse in enforcement_key; M17 killed |

Not touched (non-goals): the envelope format, dispatch-sign.py, verify.py, docs beyond this
report and the receipts, BOT-2. Nothing pushed; no PR action. Worktree left clean.
