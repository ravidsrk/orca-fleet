# Playbook — release  (the release state machine; version → promote → deploy)

Recipe: gstack `ship` (version state machine, verification gate, bisectable commits) + `land-and-deploy`
(staged rollout, revert-at-every-failure). Release is a STATE MACHINE, not one phase. Named states:

`BUILT → PROMOTION_READY → RELEASED → DEPLOYED_AND_VERIFIED`

Which state is reachable depends on authorization and deploy availability — a mission stops at the
highest state it is authorized and able to reach and names it.

## PROMOTION_READY

Version bump: a deterministic classifier reads state (FRESH / ALREADY_BUMPED / DRIFT_STALE / **DRIFT_
UNEXPECTED → STOP**); the bump LEVEL stays agent judgment; workspace-queue-aware slot pick avoids
version collisions. Changelog + bisectable dependency-ordered commits. **Fresh-evidence verification
gate:** if ANY code changed since the last test run, re-run — "should work now → RUN IT". Open the
BASE→default promotion PR with the traceability table. STOP here unless a human authorizes promotion.

## RELEASED (human-gated, one-way)

The human merges the promotion PR. Verify state=MERGED on default + greppable. Merge ≠ deploy.

## DEPLOYED_AND_VERIFIED (OPS/authorized)

Deploy-strategy auto-detect (fly/render/vercel/netlify/heroku/railway + Actions); staging-first option
(same health checks on staging before prod); a REVERT option offered at EVERY failure point (deploy
fail, canary fail: `git revert <merge-sha>` or a revert-PR if branch-protected). The DEPLOYED revision
must equal the RELEASED SHA (evidence-manifest.md). Then hand to `observe`.

## Completion

The manifest names the terminal state reached with its evidence (merge SHA / deploy revision) and,
if stopped early, the authorization it is blocked on. Never claim a higher state than reached.
