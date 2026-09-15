# Run-close human-gate batch — run_0607bdc681e6 (2026-09-14 clean-sweep tracker)

Open asks for the maintainer (one round, at close). Parked units reference these
entries as their human/OPS ref.

## G1 · Q2 / #386 (S2): sign the manifest/inventory — key custody + backend

#386 stays needs-human parked. Triage-confirmed: the retention pointer is a
placeholder, the run-close inventory is hash-only, and the prerequisite
transcript was never built. An agent CAN implement signing against the existing
key scheme and specify a backend on paper. NEEDS: (a) key custody / role
separation (the private key stays out of band by design — who holds it?);
(b) retention backend choice (a concrete tamper-evident store, or a
Sigstore/Rekor anchor); (c) whether to re-open/track the transcript
prerequisite — or park the whole unit. No unit work until answered.

## G2 · Branch protection on review/2026-09-14-holistic-fixes

PR #397 was merged by the maintainer ~7 min before its verdict (out-of-process,
disclosed, verify 6/6 after). No protocol binds a direct human merge. ASK:
enable branch protection requiring a passing review before merge on the review
branch (and main, if not already). Closes Greptile thread 4011973700's ask.

## G3 · Merged-unit needs-human parks: post-merge independent APPROVE (2nd login)

One GitHub identity exists on this host, so merged unit PRs carry blind-verdict
GOs but no independent APPROVED review, and their verify.py review legs stay
RED (5/6, disclosed). ASK: with a second login, independently approve each
merged head below — or rule the blind-verdict + executed-negative-control
compensation sufficient and waive, with the waiver recorded here. Reviewed heads
so far: #392 U388 c680ee0, #391 U389 51019fb, #395 U364 8323c98 (merged as
1b64781), #400 U393 7630815, #402 U387G 318542b (merged as a769a64e; appended
2026-09-15T07:50Z per R387P-r3 STANDARDS S3-2 — T9's close omitted it),
#403 U387P 19be7a1 (merged as b9b71df6; review leg GREEN via Greptile APPROVED —
listed for completeness, no ask), #401 U387W 0d55f10 (merged as bff42ff1).
Later units append theirs at close. Pre-existing ask, restated at close.

## G4 · Q1 overtaken: fixtures + oracle built without the maintainer's pick

Q1 asked fixtures-as-specified vs fixtures-plus-oracle vs downgrade for #364
(S1). Pre-takeover, the run BUILT fixtures-plus-oracle (U364, merged 1b64781;
the sticking F-1 remediated by T6, merged 01d954e) and closed #364. Disclosed
for retro-confirmation; the work is evidence-bound either way. No blocking ask.

## Resolved by events (report only, no ask)

- Q3 (#385 diagrams): all 21 mission guides now embed diagrams; the parity
  suite passes with KNOWN_GAPS empty.
- #235 (H-02 marketplace submissions): remains needs-human parked (external
  accounts/listings); the maintainer works it directly.
