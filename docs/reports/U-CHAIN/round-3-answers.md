# U-CHAIN round 3 — answer to every round-2 Required finding

Round 2 returned NO-GO on all three axes with six Required findings. Each is answered below
with the change that closes it and the receipt that proves it. Head SHA is recorded in
`manifest.json`; every receipt in this directory was produced through
`runtime/scripts/evidence-run.py` or by the committed harnesses.

| Round-2 finding | Axis | Spec item | Status |
|---|---|---|---|
| BOT-4 / SPEC-R2-1 / S-R2-1 — resume ancestry uses a possibly stale `origin/<default>` | spec, standards, tests | G-1 | CLOSED |
| BOT-5 / S-R2-2 — committed harness needs an unpublished fixture | standards, tests | G-2 | CLOSED |
| R2-HARNESS / S-R2-3 — mutation errors and failed controls accepted as success | standards, tests | G-3 | CLOSED |
| R2-TA-441 — resume assertions permit reversed or missing conditions (6 survivors) | tests | G-4 | CLOSED |
| R2-TA-443 — carry schema and missing-log semantics unbound (3 survivors) | tests | G-5 | CLOSED |
| R2-TA-444 — reconstruction can lose history / retrieval / integrity data (3 survivors) | tests | G-6 | CLOSED |

## G-1 — the default ref must be fresh (BOT-4)

The reviewers reproduced the hole in isolated scratch repos: a human fast-forwards `main` to
leg N's BASE tip from another checkout, and the coordinator's cached `origin/main` answers
`--is-ancestor` with exit 1 — a false negative that strands a chain that really was promoted.
Nothing in mission-chaining, merge-serialization or liveness-resume prescribed a refresh at
that boundary, and leg N+1's own preflight runs *after* the resume decision.

`runtime/mission-chaining.md` now says, inside resume alternative 1, that for a REMOTE target
`origin/<default>` is REFRESHED immediately before the check (`git fetch origin <default>`)
with the resolved default SHA written down — following `runtime/scripts/preflight.py`'s own
contract that an online default resolves through `refs/remotes/origin/<branch>` and never a
possibly stale local namesake — and that **a `<default-ref>` whose freshness cannot be
established leaves the promotion UNPROVEN and the chain parked, never landed**. The offline
branch is unchanged in force and now explicitly named: a valid LOCAL ref, the local default
branch, for an explicitly OFFLINE target with no remote, never a nonexistent `origin/…`.

Both sentences are bound separately by the contract test (`REFRESHED immediately before the
check`, `git fetch origin`, `freshness cannot be established … UNPROVEN`, `never landed`) and
each has its own mutant: `own-freshness-refresh-removed` and `own-freshness-unproven-reversed`
in `mutants-r3.txt`, both RED.

This is a *fail-safe* hole made correct, not a loosened gate: the human promotion gate,
the "an agent-executed promotion is neither" rule, and "a coordinator may not resume its own
promotion park" are untouched.

## G-2 — the harness publishes its own baseline (BOT-5)

`run_mutants-r2.py` opened an untracked `base-policy.md` at import, so a clean-checkout replay
raised `FileNotFoundError` and ran zero mutants — the 13/13 transcript was real but not
reproducible from the commit.

`mutants_core.baseline()` now derives the pre-fix policy from a pinned Git object,
`ed51fe11de5f7329ecf02ffb933bf50648ae5654:runtime/mission-chaining.md`, and checks the bytes
against sha256 `1bacd1fe7be765311b08abba787f45844b39658a8908096fbc853a09a4a26e72` — the exact
fixture hash the round-2 reviewer recorded, and also the blob at `a58bf71a`, the SHA the
round-2 transcript pinned. A mismatch is fatal, so the battery cannot silently run against the
wrong baseline.

Receipt: `clean-checkout-replay-r3.txt` — a `git clone --no-local` of this branch, with
`base-policy.md` neither tracked nor on disk, runs **both** batteries to completion and exits 0.

## G-3 — a nonzero exit is not a kill (R2-HARNESS)

The old classifier was `"KILLED (RED)" if p.returncode != 0`, and `sys.exit(1 if surv else 0)`
ignored the controls entirely. The reviewers exhibited two invalid proofs the harness accepted:
an ImportError raised only for mutated policy bytes (zero assertions ran, 13/13 "KILLED",
exit 0), and a contract test failing only at the original hash (both controls RED, exit 0).

`mutants_core.classify()` now returns RED only when the covering test ran *and* an assertion
failed (`AssertionError` plus `FAILED (failures=N)`); `Ran 0 tests`, a loader error, an
ImportError, or any other nonzero exit without an assertion failure is **STILLBORN** and fails
the harness. Either positive control not being GREEN fails the harness. A mutant expected GREEN
that goes red (the neutral reflows) fails it too.

Receipt: `harness-trust-probes-r3.txt` re-runs both of the reviewers' probes against the
committed, unmodified harness in a disposable clone. Probe A: 31 STILLBORN, `HARNESS_EXIT=1`.
Probe B: `fixed-head: exit=1; RED`, `head-restored: exit=1; RED`, `HARNESS_EXIT=1`. Reverting
the probe patches returns the harness to `HARNESS_EXIT=0`, so the failures are the probes and
not a latent defect.

## G-4/G-5/G-6 — the twelve executed survivors

Round 2's survivors all had the same shape: every matched noun stays, the relationship or
condition it governs disappears. The fix is stronger binding, never a weakened probe — no
assertion from round 2 was deleted or relaxed.

**G-4 (#441).** Park-wide assertions could not see *which* alternative lost its condition, so
each numbered alternative is now extracted from the park bullet and bound inside its own
segment: alternative 1 gets the ancestry direction (`BASE tip is an ancestor of the DEFAULT`),
the pinned ancestry subject, the `git merge-base --is-ancestor` command, G-1's two freshness
sentences and the offline LOCAL-ref rule; alternative 2 gets the named human's explicit
decision, the UNPROMOTED fork and the granted SHA written down. The park-level
"REQUIRES exactly one of two facts" / "nothing else is sufficient" framing is retained.

**G-5 (#443).** The whole-schema deletion died on "two sections, both required" before it could
show the individual fields were protected. The carry table's full field set is now bound —
`carry id`, `from` with its source class, `content` pinned to file:line, `input status` with
the `OWED` rule — along with the gate record's `which gate, its state, the human who owns it,
and what resumes it` and the rule that a MISSING handoff log is an unfinished chain, never an
empty one.

**G-6 (#444).** Bound: `reproduces every cited commit and its ancestry` (a commit list without
history is not a reconstruction), `the remote and the pushed refs written down` (an
unreachable mirror publishes nothing), and `Every published artifact is hashed into the
run-close integrity inventory` (unhashed bytes can move under the citation), alongside the
retained `git bundle` and `SUPPLEMENTAL and never sufficient on their own` assertions.

All twelve survivors are re-run in `run_mutants-r3.py` as `own-*` cases. Each is RED, and each
dies on the assertion written for it — the per-case `AssertionError` line in `mutants-r3.txt`
names the obligation, so none dies by collateral damage from a neighbouring probe:

| survivor | dies on |
|---|---|
| `own-promoted-ancestry-inverted` | resume fact 1 must assert the leg's own BASE tip IS an ancestor of DEFAULT |
| `own-promoted-wrong-commit` | resume fact 1 must assert the leg's own BASE tip IS an ancestor of DEFAULT |
| `own-grant-no-sha` | resume fact 2 must record WHICH SHA was granted |
| `own-grant-no-unpromoted-fork` | resume fact 2 exists for the UNPROMOTED tip |
| `own-grant-promoted-only` | resume fact 2 exists for the UNPROMOTED tip |
| `own-offline-nonexistent-ref` | the offline branch must keep a valid LOCAL ref |
| `own-carry-source-content-removed` | the carry table must declare its `from` field |
| `own-gate-identity-state-removed` | the gate record must declare gate identity and state |
| `own-missing-handoff-empty` | a missing log must read as an unfinished chain |
| `own-reconstruct-ancestry-removed` | the artifact must reproduce the cited commits AND their ancestry |
| `own-mirror-ref-fields-removed` | the pushed mirror must record remote and pushed refs |
| `own-artifact-hash-removed` | published bytes must be hashed into the integrity inventory |

Three neutral reflows (`neutral-soft-wrap-park`, `neutral-soft-wrap-publish`,
`neutral-soft-wrap-freshness`) stay GREEN, so the battery is not merely asserting on where the
prose happens to wrap.

## Round-3 receipt index

| Receipt | What it shows |
|---|---|
| `contract-test-r3.txt` | the covering test GREEN at head, through evidence-run.py |
| `validate-r3.txt` | `scripts/validate.py` exit 0 (line caps, reference resolution) |
| `negctrl-r3.txt` | policy reverted to the unit BASE blob, test kept → RED, exit 1 |
| `poscontrol-r3.txt` | policy restored → GREEN, exit 0 |
| `mutants-r3.txt` | 31 cases: 28 RED for the right reason, 3 neutral GREEN, both controls GREEN |
| `mutants-r2-replay.txt` | the round-2 battery, 13/13, now replaying without a fixture |
| `clean-checkout-replay-r3.txt` | both batteries run from a fresh `git clone` (BOT-5) |
| `harness-trust-probes-r3.txt` | the harness fails closed on stillborn mutants and red controls (R2-HARNESS) |
| `suite-r3.txt` | the full suite at head |

One invalid `suite` record is kept in `manifest.json`'s `commands[]` (exit 1, an
`unittest discover -t .` invocation that is not importable in this layout). It is a malformed
command, not a failing suite, and it is retained rather than pruned because an evidence ledger
that drops its own bad records is not an evidence ledger. The valid `suite` record follows it.
