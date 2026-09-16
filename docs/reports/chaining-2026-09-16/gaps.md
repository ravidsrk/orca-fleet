# Protocol gaps exposed by the chaining run (#417)

Each gap = a place mission-chaining.md (or a doc it rides) didn't say what to
do and judgment filled in. Filed as follow-up issues (numbers below once filed).

## G1 — mission-chaining.md names no inter-mission promotion lane (PRINCIPAL)

The doc says each link is a FULL run with its own BASE and that carry-over is
explicit-human — but never states that every chain therefore parks for a human
promotion between legs (clean-sweep "open the promotion PR, stop";
merge-serialization no-gh "stops at BASE"; gate-classification promotion
one-way-always). In a no-gh / headless / scratch context the chain necessarily
stops after leg 1 with carry produced-but-owed. This run stopped one step
earlier (leg-1 gate unsatisfied, review-owed — G-REVIEW) with G-PROMO-1
analyzed and certain immediately behind it; either way the promotion hold has no
named terminal, no lane, and no resume procedure in the chaining doc, whose stop
rules cover degraded terminals only. Suggested: name the park
(e.g. `PARKED-AT-PROMOTION`), define what resumes it (landed promotion SHA or
recorded BASE-carry grant), and state plainly that chains are human-paced at
every link boundary.
Issue: #441

## G2 — evidence-manifest.md / verify.py assume unit repo == evidence repo

The chaining report lives in the fleet repo; the leg SHAs live in the target
repo. verify.py resolves evidence paths under one git toplevel and the SHAs
under (the same) cwd — a cross-repo chain manifest satisfies neither invocation.
This run executed the §2 procedure manually with transcripts (limitation L1).
Suggested: a `--git-dir` / `--evidence-root` split, or a chaining evidence
layout the verifier understands.
Issue: #442

## G3 — deferral carry has no artifact shape

"Mission N's parked items, backlog file, and noticed-but-not-touched list are
handed to mission N+1" — as WHAT? File, ledger section, manifest field? This
run proposed `handoff-log.md` (carry table + gate record, one file per chain).
Suggested: bless a shape (this one or another) so consumers can rely on it.
Issue: #443

## G4 — re-derivability for local-only (no-remote) targets is undefined

Acceptance criterion 5 ("a second person can re-derive each leg's outcome from
the cited SHAs") is unachievable by SHA citation alone when the target has no
remote — the SHAs don't resolve anywhere else. This run embedded `seed-*` +
`full-diff.txt` so the bytes reconstruct. Suggested: the chaining doc should
require embedded reconstruction artifacts (or a pushed mirror) for local-only
targets.
Issue: #444

## O1 — clean-sweep refuted-close gate kind (mission-level, NOT chaining)

Refuted/duplicate closes need "a batch human gate (or a once-per-run recorded
grant)". This run ruled F4's refuted close MECHANICAL (executed deterministic
repro) without opening a gate. Either the mission should say refuted-with-repro
is mechanical, or every refuted close truly parks for a human (expensive).
Noted here; filing left to the clean-sweep owner — NOT filed by this run.
