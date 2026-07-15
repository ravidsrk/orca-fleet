# 🤝 oss-contribute — landed contributions to a repo you do not control

> Point it at a set of issues on an upstream project you can only fork. Come back to a set of open,
> internally-reviewed, etiquette-correct pull requests (and quoted review-assist comments where a
> maintainer PR already exists) — every one built on a fork with a test that failed before the fix.
> Merge is left to the maintainers; that is the point, not a shortfall.

**Skill:** [`skills/oss-contribute/SKILL.md`](../../skills/oss-contribute/SKILL.md) · **Layer:** mission (discoverable) · **Fix authority:** on the fork, yes; merge authority: never

---

## What it does

`oss-contribute` is the upstream-contribution fleet. A **coordinator** — a thin loop-holder that never
reviews, codes, opens PRs, or comments — enumerates a bounded set of upstream issues, dispatches every
one through the per-issue pipeline, verifies each against authoritative state, and stops when a full
re-enumeration finds nothing actionable left un-contributed.

It is `clean-sweep` forked for a repo you do **not** control. The build and review machinery is shared;
three things differ, and by orca-fleet's own five-part mission test that makes it a distinct mission:

- **Convergence proof.** `clean-sweep` closes each issue with a merged SHA. `oss-contribute` cannot —
  you have READ on the target. The terminal is a PR **open and internally reviewed**; merge is the
  maintainer's.
- **State machine.** It adds an overlap-discovery step (search the upstream OPEN PRs per issue, not
  just the code) and a contribution decision (assist / alternative / stand-down), and it drops the
  merge step and the merge-serialization conductor entirely.
- **Parking semantics.** `awaiting-maintainer-merge` and `externally-covered` are NORMAL terminals
  here, not degraded ones.

## The contribution decision

When an issue already has a maintainer's open PR, the fleet does not blindly open its own. It chooses,
and logs the choice:

- **assist** — their PR is sound but our independent review found confirmable issues in their diff:
  post one contributor-tone comment, findings quoted from their code, no verdict.
- **alternative** — our implementation differs materially or fixes bugs theirs has: open our PR,
  cross-linking theirs ("take whichever you prefer"), and post the assist comment too.
- **stand-down** — their PR covers it and we add nothing: park `externally-covered`, no hollow comment.

## Etiquette is part of done

Read `CONTRIBUTING`, the PR template, and the DCO/CLA requirement first, and conform. Reference the
issue; use a closing keyword only on a concrete issue, never on an RFC or tracking issue. The
maintainer is the sole merge authority — the fleet never self-merges and never assumes a merge.

## Proof

`external-run` — see [the 2026-07-16 run](../runs/2026-07-16-oss-contribute-external-run.md) against
`dodopayments/chimely`: 5 upstream PRs and 4 review-assist comments (10 quoted findings), the run this
mission was extracted from.

## Not this mission

- A backlog you **own** and can merge → [`clean-sweep`](clean-sweep.md) (merged-SHA closure).
- Building a net-new project or feature → [`ship-it`](ship-it.md).
- A read-only verdict with no PRs → [`review-it`](review-it.md).
