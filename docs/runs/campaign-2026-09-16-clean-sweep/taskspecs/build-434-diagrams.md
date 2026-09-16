# Taskspec — U434: regenerate proof-ladder diagrams post-first-promotion

Unit: T434 · Issue: #434 · Source: tracker enumeration T0 2026-09-16T09:59:44Z
BASE: campaign/clean-sweep-selftest · base_sha: 6390743815f8f435181fa410cce374587128b30a
Worker pack: matt (tdd) — the run's one pack.

## Goal

Remove the stale time-indexed callout baked into the proof-ladder diagrams and every
text that repeats it, replacing it with a standing callout that stays true across
promotions (issue's own suggestion: name the archive as the live state).

## Scope (exact paths)

- `assets/diagrams/generator/specs_new.py` (proof-ladder prompt note)
- `assets/diagrams/proof-ladder.jpg` + `assets/diagrams/proof-ladder-light.jpg` (regen via gen.py)
- `assets/diagrams/generator/wire_docs.py` (proof-ladder alt text)
- `README.md` + `docs/concepts.md` (alt refresh via wire_docs.py + caption-note removal)
- `tests/test_proof_ladder_callout.py` (NEW — the criterion-bound oracle)

## Non-goals

Proof-tier semantics; any other diagram; the #410 promotion itself.

## Frozen callout (verbatim — test oracle pins this text)

- Spec note: `the run archive is the live state — a rung counts only with the run report that binds it`
- Alt tail: `; the run archive is the live state — a rung counts only with the run report that binds it`
- Forbidden (time-indexed): `today every mission reads`

## Acceptance criteria

- AC-1: Neither diagram image renders a claim the catalog state contradicts (new amber
  note rendered; pixels reviewed before commit per the generator README).
- AC-2: Both alt texts describe their image's actual content (`wire_docs.py --dry-run`
  fixed point green; alt tail matches the rendered note).
- AC-3: The dated caption notes are removed from `README.md` and `docs/concepts.md`.
- AC-4: `tests/test_proof_ladder_callout.py` + `tests/test_wire_docs.py` green, full
  `tests/` suite green, `scripts/validate.py` green at head.

## Stop

Regen needs the provisioned `OPENROUTER_API_KEY` (env only, never in-tree). If the key
is missing, quota-exhausted, or the network is unreachable: STOP, park needs-human
with the attempt logged — do NOT hand-edit pixels or ship alt text that mismatches pixels.

## Evidence

- Manifest `docs/runs/campaign-2026-09-16-clean-sweep/u434-manifest.json`
- Criterion command via `evidence-run.py --label tests`
- Negative control: `revert` over the 6 production paths (spec, wire, README,
  concepts, both JPGs); the NEW test file is the oracle and is NOT reverted.
- NC command (coordinator-named): `python3 -m unittest tests.test_proof_ladder_callout -v`
- Review: instructed-isolation (solo — no second identity exists; independence NOT claimed)

## Escalation / budget

Round budget ≤3. Spend ≈2 image calls (~$0.28) on the host-provisioned key per
DECISIONS `css-u434-regen-key` (taste, human may veto).
