# Playbook — upstream-contribution  (contributing to a repo you do not control)

The delta between fixing your OWN backlog (remediate-finding + merge-serialization) and CONTRIBUTING
one upstream. You have READ on the target, so you never merge, never own a BASE, and never run a merge
conductor. The unit's terminal state is a PR OPEN and internally reviewed, not a merged SHA. This
playbook supplies the fork topology, the overlap check, the contribution decision, and the etiquette;
build-change and acceptance-review are unchanged.

## Fork topology (no integration BASE, no conductor)

- Work on a FORK you can push to (`gh repo fork --remote`); the target repo is `upstream`, READ-only.
- One unit = one branch on the fork, forked from `upstream/<default>` (not a fleet integration BASE
  there is none). PR head is `<fork-owner>:<branch>`, base is `upstream:<default>`.
- No merge-serialization: nothing merges to a base you control. reviewed-sha-freshness still holds
  (a late push voids the internal review), and the PR is opened only AFTER the internal review PASS.

## Overlap discovery (the enumeration step clean-sweep lacks)

REDUNDANCY for `source=tracker` on an upstream repo is TWO queries, not one. Codebase search AND
`gh pr list --repo <upstream> --search "<issue#> in:body OR <issue#> in:title" --state open` PER ISSUE,
before FREEZE. Re-run the PR query before opening each unit's PR — a competitor PR can appear mid-run.
An issue with an in-flight PR is `already-has-PR` class, never `skip`.

## The contribution decision (a classified gate, gate-classification.md)

For an `already-has-PR` issue, choose per the diff you can see, never silently:

| Choice | When | Action |
|--------|------|--------|
| **assist** | their PR is sound; our review found confirmable issues in THEIR diff | Post ONE contributor-tone comment: only findings you can quote in their code, each with a concrete failure scenario, an offer of your test. No verdict, no approve/request-changes. |
| **alternative** | our independent implementation differs materially or fixes bugs theirs has | Open our PR, cross-linking theirs up front ("alternative to #N, take whichever you prefer"), AND post the assist comment. Never a silent duplicate. |
| **stand-down** | their PR covers it and our artifacts add nothing | Park `externally-covered`. No hollow comment. |

A literal same-issue duplicate you already opened is closed with a courteous pointer. `complement, not
compete` is the default posture; opening an alternative is a taste gate (log it), not a one-way door.

## Etiquette (conformance is part of done)

- Read `CONTRIBUTING`, the PR template, and the DCO/CLA requirement FIRST; conform (sign-off, commit
  style, scope). A contribution that ignores house rules wastes a maintainer's time.
- Reference the issue; use a closing keyword ONLY on a concrete issue, NEVER on an RFC/meta/tracking
  issue (auto-closing a tracker the maintainers still use is presumptuous) — reference it instead.
- The maintainer is the sole merge authority. Never self-merge, never `--admin`, never assume a merge.
  Reconcile review-bot and maintainer feedback as fix rounds on the same branch (dispatch-lifecycle.md).

## Post-open follow-up (a PR is not fire-and-forget)

Opening the PR is not the unit's terminus. Maintainer reviews, review-bot comments (Greptile et al.),
and CI all arrive AFTER open, and a contribution that ignores them rots. Until the PR is merged,
closed, or its feedback goes quiet:

- WATCH the PR: new review threads and CI, on a cadence or when notified (`gh pr view <n> --json
  reviews,comments,statusCheckRollup`, `gh api .../pulls/<n>/comments`). Assist comments on others'
  PRs draw replies too.
- TRIAGE each new thread against the CURRENT head, never the commit it was filed on — an earlier fix
  round may already resolve it: RESOLVED-ALREADY (reply with the fixing sha, never re-fix), VALID
  (fix), FALSE-POSITIVE / DELIBERATE (reply with the quoted rationale).
- FIX valid ones as fix rounds on the SAME branch (build-change discipline). A push re-triggers the
  bots and re-runs CI; reviewed-sha-freshness still applies. ANSWER every thread — silence reads as
  abandonment.
- TERMINAL: merged or closed by the maintainer, OR all addressable feedback resolved and quiet →
  park `awaiting-maintainer-merge`. Bounded: after THREE follow-up rounds without convergence (a bot
  that re-flags its own fix, a thread needing a maintainer decision) park `needs-human` naming the
  thread — the same round budget acceptance-review.md sets; only a recorded human gate extends it.

## Evidence (evidence-manifest.md, PR-open variant)

Same SHA-bound manifest as any mutating unit — base_sha → head_sha, criteria, commands+exit, a real
negative control (revert the fix → the test goes RED) — EXCEPT the merge checks are replaced by:
PR open against `upstream:<default>`, `baseRefName == <default>` asserted, `headRefOid == reviewed_sha`
(fresh), and bot/CI green-or-reconciled. `parked` names the maintainer-merge dependency. There is no
`git merge-base --is-ancestor` check because the fleet never performs the merge.

## Rules

- Close a unit off a PR that is OPEN + internally reviewed + etiquette-conformant — never off a merge
  you cannot perform, never off worker memory.
- One issue = one branch = one PR (or one assist comment). An alternative PR is not a duplicate when
  it cross-links the parallel PR.
- The mission owns "is the actionable set drained"; this owns "is one issue contributed correctly".
