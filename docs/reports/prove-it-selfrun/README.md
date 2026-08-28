# prove-it — mutation-binding demonstration (2026-08-28)

**Scope (honest):** this is a **scoped mutation-binding demonstration** against one real criterion,
not a full `prove-it` mission run over a critical surface. It proves the criterion↔test↔negative-control
mechanism end-to-end and adds one real coverage test. It **does not advance `prove-it` past
`doctrine-only`** — a tier advance requires the full mission (map the critical surface, multi-criterion
audit, builder wave, and the WIP-curve row `docs/runs/README.md` requires of the next mutating self-run,
per #51). Presenting it as more would violate the repo's "never more proven than its evidence" rule.

## Criterion PF-1

> A YAML block-scalar frontmatter value (`key: >` / `key: |` followed by indented continuation
> lines) parses to a single **space-joined** string carrying every continuation line.

Load-bearing: missions fold `description:` and `compatibility:` with `>`/`>-`; a regression in the
fold path would silently truncate them past the compose-clause and description checks. The fold path
(`scripts/validate.py` `parse_frontmatter`, ~lines 156–181) had **no direct test** before this.

## Bound test

`tests/test_validate.py::ParseFrontmatterBindingTest::test_block_scalar_folds_to_space_joined_string`
calls `validate.parse_frontmatter` directly and asserts the folded value equals `"first line second line"`.

## Negative control (the proof that the test earns its keep)

Pinned mutant — the mutmut string-mutation `" " -> ""` on the fold join at `scripts/validate.py:181`
(the final-key branch), applied and reverted:

| Step | State | PF-1 result |
|------|-------|-------------|
| 1 | clean HEAD | **OK** |
| 2–3 | mutant applied (`"".join`) | **FAIL — mutant KILLED** (`"first linesecond line"` ≠ expected) |
| 4–5 | mutant reverted | **OK** |

Full transcript: [`negctrl.txt`](negctrl.txt). Reproduce the full sweep with
`uv run --with mutmut mutmut run --paths-to-mutate scripts/validate.py` (the pinned mutant above is
one of its string mutations on line 181).

## Integrity inventory (sha256)

| Artifact | sha256 | producer |
|----------|--------|----------|
| `negctrl.txt` | `98b8ba35c2304029941f67c52c8773c4fdd8f6b9aa770c28d2c02fa4cb00ed63` | `python3 -m unittest` (2026-08-28) |

## Follow-up to reach `self-run`

A full `prove-it` self-run over the repo's correctness surface (`scripts/validate.py`, `scripts/eval.py`,
`scripts/gen-badges.py`, `runtime/scripts/`) with a multi-criterion mutation audit + the WIP-curve row —
that report would land in `docs/runs/` and advance the tier.
