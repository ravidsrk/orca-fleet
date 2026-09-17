# doc-r01 — cli:runtime/scripts/decisions.py × reference

Status: LANDED (sha in ledger row).

## Blind-fix expectation (written before re-reading the section)

Expected: one section naming decisions.py as the DECISIONS-log writer/validator,
four subcommands (append/active/tally/check), --file/--doors globals, the one-way
refusal rules, exits 0/1/2. Confidence: high — argparse table + docstring read first.

## Review (instructed-isolation self-review — weaker guarantee, D3)

- Standards: matches page template (anchor line, Usage, Subcommands, Flags, Exits);
  no secrets; prose minimal. No voice nits blocking.
- Spec: frozen cell = reference for decisions.py (coverage-map.md GAP critical).
  Section states what/options/defaults/exits from `runtime/scripts/decisions.py:1-63`
  + argparse (`:380-404`) + constants (`:75-90`). No scope creep (no how-to/tutorial).
- Test-adequacy: claimcheck --cell decisions.py GREEN (11 flags, 4 subcommands,
  4 paths, 3 exits bound); rename --lens→--omitted turned it RED (nc-doc-r01.txt);
  restored after. Reverting the section fails the re-map (section grep) — adequate.

## Anchors

- `python3 docs/runs/campaign-2026-09-16-document-it/extractor/claimcheck.py --cell decisions.py` → exit 0, 0 unbound.
- NC transcript: `evidence/nc-doc-r01.txt` (claimcheck exit 1, file restored).
- Lesson (carried): renames must not contain the original as a substring
  (`--lens`→`--lens-x` stayed GREEN); all later NCs use disjoint tokens.
