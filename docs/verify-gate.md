# The verify gate — native hooks, with an enterprise fallback

Packages the independent verifier ([`runtime/scripts/verify.py`](../runtime/scripts/verify.py)) as a
**completion gate**: a unit cannot be marked done until its evidence manifest passes. The gate
*mechanism* is native (Claude Code hooks); its **content** — an independent second-session verdict
that anchors to authorities OUTSIDE the worker's manifest (the coordinator's frozen contract for
scope, GitHub for review, the artifact/replay for the negative control) — is the differentiator, and
it runs the same `verify.py` no matter which surface fires it.

## Install paths, and which ones carry the gate

| Install | `${CLAUDE_PLUGIN_ROOT}` | Gate |
|---|---|---|
| `/plugin install orca-fleet` | set by Claude Code | wired by [`hooks/hooks.json`](../hooks/hooks.json) — nothing to do |
| `ln -s … ~/.claude/skills/<mission>` | **unset** | **none until you wire it**: `sh hooks/print-settings-snippet.sh` and merge the output into `settings.json` |
| `npx skills add …` (copy installer) | unset | same as symlink — wire the snippet, and check the `../../` references survived the copy |

This is issue #262: the README recommends the symlink path for trying the catalog out, and that
path loads no plugin, so the hook file below never fires. A mission installed that way runs with
no completion gate and nothing says so at runtime.
[`hooks/settings-snippet.json`](../hooks/settings-snippet.json) is the same two hooks with an
absolute path; [`hooks/print-settings-snippet.sh`](../hooks/print-settings-snippet.sh) resolves
that path against your clone (`--check` verifies the gate script is there).

## Native path — plugin hooks (set `${CLAUDE_PLUGIN_ROOT}`)

[`hooks/hooks.json`](../hooks/hooks.json) wires two events to
[`runtime/scripts/verify-gate.sh`](../runtime/scripts/verify-gate.sh), passing `--event task|stop`:

- **`TaskCompleted`** (`--event task`, agent-teams) — **exit 2 → prevent completion + return
  feedback**. Per-unit by construction; with no manifest it blocks (a unit completing must have one).
- **`Stop`** (`--event stop`) — fires on **every** turn end, so a turn with **no unit in progress**
  (`ORCA_MANIFEST` unset) has nothing to verify and is **allowed**; a turn that IS mid-unit is
  verified and **exit 2 refuses the turn end** until the manifest passes.

`verify-gate.sh` is **fail-closed**: if a manifest is named but missing, if no authoritative
contract is supplied (`ORCA_CONTRACT_SOURCE`/`ORCA_CONTRACT_DIGEST` — without it the scope check
cannot be certified, so it blocks), or the verifier errors, it blocks (exit 2) — an un-runnable
verifier is never a green light. The one carve-out is the `Stop` semantics above: `Stop` with
`ORCA_MANIFEST` unset (no unit in progress) is ALLOWED, while `TaskCompleted` with no manifest is a
mis-dispatch and blocks.

```
coordinator sets the gate env (every input verify-gate.sh reads, enumerated below) — NOT the worker
   → TaskCompleted / Stop hook fires verify-gate.sh
       → verify.py re-derives against authorities outside the manifest; the unit CLASS that decides
         whether review + negative control run comes from the dispatch (ORCA_UNIT_CLASS), never the
         manifest — missing/unknown ⇒ mutation (fail-safe)
         (scope ← coordinator contract · review ← GitHub · negative control ← EXECUTED replay in a
          throwaway worktree · commands ← a wtree-bound exit-0 record · redaction · commits · freshness)
           → exit 0 allow · exit 2 BLOCK (with feedback)
```

**The gate env surface** — every `ORCA_*` variable `verify-gate.sh` reads, all coordinator-set (never
worker-set; anything else in the environment is ignored):

- `ORCA_MANIFEST` — path to the unit's evidence manifest (required; named-but-missing ⇒ BLOCK;
  unset ⇒ BLOCK on `TaskCompleted`, allowed on `Stop` with no unit in progress).
- `ORCA_CONTRACT_SOURCE` / `ORCA_CONTRACT_DIGEST` — the frozen contract `path@ref` and its sha256;
  without both, the scope check fail-closes.
- `ORCA_UNIT_CLASS` — `mutation | report-only | planning`, from dispatch; missing/unknown ⇒ mutation.
  On the native path the worker owns this variable, and the downgrade it buys is the whole
  mutation lane at once — negative control, intent packet, lighting legality, reviewer_mode.
  So an **unsigned** `report-only`/`planning` claim is measured against what
  `base_sha..head_sha` actually changes: production paths changed ⇒ RED; an unresolvable
  range ⇒ RED (the shas are worker-supplied too, so "cannot tell" must not beat "changed");
  `base_sha == head_sha` or a test-only change ⇒ passes, marked `(unsupervised)` in the
  verdict. A dispatch record signed by the coordinator authorizes the class and skips all of
  this — that is what signing it is for (#310).
- `ORCA_REPO` — `owner/name` for the independent GitHub review lookup (optional; inferred from origin).
- `ORCA_BASE` / `ORCA_SYMBOL` — ancestry-check base branch / a unit symbol to grep on it (optional).
- `ORCA_NC_COMMAND` — the **authoritative** criterion-bound command the negative control must turn
  RED, supplied out of band exactly as the frozen contract is. It is forwarded as `--nc-command`,
  and the manifest's own `negative_control.command` must agree with it or the run is RED — a unit
  does not get to choose what proves it. It is **REQUIRED whenever `ORCA_EXECUTE_NC` is set**
  (#279): there is no fallback. verify.py used to accept the manifest's own command when that
  command was already in the content-bound `commands[]` ledger, but the ledger is written by
  `evidence-run.py` *on the worker*, from what the worker hands it — so the manifest and the ledger
  are the same authority twice, and binding one to the other is circular. A worker that writes both
  can nominate `grep -q FIXED calc.py` as its "criterion-bound proof", record it green at
  `head_sha`'s tree, and clear the executed-control gate without running a test. That is attack A12
  of the 2026-09-11 review, and A15 is the same move in the strongest lane the repo documents.
- `ORCA_EXECUTE_NC` — set (to anything non-empty) to forward `--execute-nc`, which **executes the
  negative control** instead of reading it. verify.py checks out `head_sha` in a throwaway worktree,
  applies the control from the manifest — `tool: revert` restores `negative_control.paths` from
  `base_sha` (falling back to `git revert --no-commit base..head` only when no paths are given and
  the range is linear); `tool: hand` applies the unified diff quoted in the NC artifact — and
  requires `negative_control.command` to exit **non-zero** there, then **zero** in a second clean
  worktree at `head_sha`. Requires `ORCA_NC_COMMAND` — without it the run is RED before any
  worktree is built, so a command the worker nominated is never executed. The control must bind to
  the change (#280): the paths it restores, and the `+++` targets of a `hand` diff, must be
  production paths `base_sha..head_sha` really changes — not a decoy, and not a test file; the
  range-revert fallback is refused when the unit touches a test module; and the RED must carry an
  assertion failure rather than an ImportError, a SyntaxError, or silence. Fail-closed on anything
  else too: a tool with no replay, a missing command/paths, a git error, a control that changes
  nothing, or a command that passes under the control ("tautological — the proof does not go RED"). It is **REQUIRED** in the two review-waiver
  lanes below; elsewhere it is the stronger form of the same check. Budget ~2 worktree checkouts +
  2 runs of the bound command (600 s cap each).
- `ORCA_NO_GH` — set to take the **no-gh lane**: review authority switches from the GitHub lookup to a
  local reviewer artifact — a downgrade, see [Trust boundary](#trust-boundary). **Requires
  `ORCA_EXECUTE_NC`**: with the GitHub authority gone, the negative control is the only oracle left,
  and a control nobody ran is a file the worker wrote.
- `ORCA_LIGHTING` — the coordinator's lighting decision (`dark-eligible` waives the build-blind human
  review; gate-classification.md). `dark-eligible` **requires `ORCA_EXECUTE_NC`** for the same
  reason: six of the ten manifest-gaming attacks in the 2026-09-10 review landed in these two lanes,
  every one of them on a negative-control artifact nobody executed.
- `ORCA_PROVENANCE` — `ci|mcp|sdk|dispatch` asserts the env came from OFF the worker; suppresses the
  advisory `NOTE`.
- `ORCA_DISPATCH_RECORD` — the coordinator-signed dispatch envelope (path, or `path@ref`) binding the
  contract digest, unit class, and lighting (#135).
- `ORCA_DISPATCH_PUBKEY` — the Ed25519 verifying key, overriding key discovery; trustworthy only when
  set off-worker (see below).

## Fallback path — where `allowManagedHooksOnly` disables plugin hooks

Managed/enterprise settings can set `allowManagedHooksOnly`, which blocks user/project/plugin hooks.
The gate is therefore **also** runnable off the hook surface, running the identical `verify.py`:

1. **CI gate** — run the verifier in the PR pipeline (reference snippet; adapt to your CI):

   ```yaml
   # .github/workflows/verify-gate.yml (reference — not enabled in this repo)
   - run: python3 runtime/scripts/verify.py --manifest "$ORCA_MANIFEST"
       --contract-source "$ORCA_CONTRACT_SOURCE" --contract-digest "$ORCA_CONTRACT_DIGEST"
       --repo "$GITHUB_REPOSITORY" --base "$GITHUB_BASE_REF"
   ```

2. **MCP Task** — expose `verify.py` as an MCP Task the coordinator awaits before advancing a unit
   (rides the MCP Tasks extension; see [platform-ride](platform-ride.md)).
3. **SDK subprocess** — the coordinator invokes `verify-gate.sh` directly as a headless
   subprocess at the unit boundary (works with no hook surface at all).

All three are the same deterministic re-derivation; the hook is just the most ergonomic trigger.

## Why the gate is native but the moat isn't

Anyone can ship a `Stop`-hook gate — the mechanism is a platform primitive (see the absorption-risk
register in [platform-ride](platform-ride.md), R3). What a competitor cannot cheaply copy is what this
gate *checks*: an independent, different-session verdict that re-derives against authorities the
worker does not control — the coordinator's frozen denominator, GitHub's review state, the negative
control's artifact/replay. Keep the differentiation in `verify.py`, not in the hook.

## Trust boundary

The verifier re-derives against authorities the worker does not control — **but those authorities are
only as sound as the provenance of the inputs that name them.** The scope denominator
(`--contract-source`/`--contract-digest`) and the unit class (`--unit-class`) are supplied via env; if
the worker can set that env, it can choose its own denominator and class.

- **Native `Stop`/`TaskCompleted` hook — ADVISORY by default.** The gate runs *inside the graded
  worker's session*, so the worker can set `ORCA_*`. With no signed dispatch record it is
  defense-in-depth (it still catches an honest mistake or a lazy manifest), **not a soundness
  boundary** — it emits a `NOTE` saying so unless `ORCA_PROVENANCE` asserts off-worker origin.
- **Native hook + signed dispatch — still ADVISORY (#135).** The signature only helps if the worker
  cannot control the *verifying key*, and in-session it can: every key source the gate consults
  (the env var, the local `origin/HEAD` ref, the working-tree file) is worker-influenceable, so a
  self-signed record verifies (see below). The record's soundness value is **off-worker**
  re-verification, never the in-session verdict.
- **CI / MCP-Task / SDK-subprocess — SOUND.** On these surfaces the coordinator (not the worker) sets
  the env, so the frozen denominator and unit class are trustworthy and the guarantee holds. Set
  `ORCA_PROVENANCE=ci|mcp|sdk|dispatch` there to suppress the advisory `NOTE`.
- **The no-gh lane downgrades review authority — disclose it wherever the env is templated.** Setting
  `ORCA_NO_GH` switches the review check from the independent GitHub lookup to a **local
  `review.artifact`**: worker-forgeable on its own, so verify.py fail-closes unless an out-of-band
  coordinator contract (`--contract-source` + `--contract-digest`) corroborates the run — and even
  then the review is only **coordinator-attested**, not GitHub-verified, and the verdict carries a
  `NOTE` naming the weaker guarantee (merge-serialization.md). The lane exists for sanctioned
  offline/no-`gh` operation; on the sound surfaces the coordinator owns the env, so `ORCA_NO_GH` must
  not leak into a CI template a unit can influence — its presence there silently downgrades the review
  verification on the one surface meant to be sound.

### Signed dispatch — what it binds, and where the key comes from (#135)

> **Dormant today (#284).** The scheme below is sound where the key originates off the graded
> worker, and `verify.py` implements it. But no mission or playbook signs a dispatch with
> `runtime/scripts/dispatch-sign.py`, and no `.orca/dispatch-pubkey` is committed, so the check
> never runs on a real unit. Read this section as the contract a signed dispatch would satisfy,
> not as a boundary currently standing.

The native hook can't trust `ORCA_CONTRACT_DIGEST` / `ORCA_UNIT_CLASS` / `ORCA_LIGHTING` on its own —
the worker sets them. Bind them to a **coordinator-signed dispatch record**. The whole scheme rests on
one thing: **the verifying public key must originate off the graded worker.** A worker that could set
the key would just self-sign. The gate discovers the key from three sources, in this code order
(precedence pinned by `VerifyGateDispatchPinDiscovery` in `tests/test_verify_gate.py`):

1. **`ORCA_DISPATCH_PUBKEY` env.** Honored whenever set — a worker-set value is used, not ignored;
   `ORCA_PROVENANCE` decides only whether the advisory `NOTE` is emitted, never whether the key is
   used. Trustworthy only when an **off-worker orchestrator** sets it
   (`ORCA_PROVENANCE=ci|mcp|sdk|dispatch`).
2. **The pin blob at the local `origin/HEAD` ref** — `.orca/dispatch-pubkey` read from
   `refs/remotes/origin/HEAD`, resolved **locally**. The blob's *content* was landed by a reviewed PR,
   but the ref itself is a local remote-tracking ref: in-session the worker can repoint it with
   `git update-ref`, no push access needed. Trustworthy only when read off-worker against a
   fetch-verified ref.
3. **The working-tree `.orca/dispatch-pubkey`** — fallback when the ref read fails. A plain file in
   the worker's own checkout; fully worker-writable in-session.

On the native in-session path **all three** are worker-influenceable, so a key that verifies
in-session proves nothing about who signed (see [Trust boundary](#trust-boundary)).

**Setup and per-dispatch flow:**

1. **Once:** off the worker, `dispatch-sign.py gen-key --out <secret>` — keep `<secret>` private and
   land `<secret>.pub` as **`.orca/dispatch-pubkey`** through a reviewed PR to the default branch.
   Committing it turns the signed-dispatch check on — the gate then requires a valid record; what
   that check *proves* still depends on where the gate runs (see the soundness condition below).
2. **Per dispatch (off-worker):** `dispatch-sign.py sign --key <secret> --manifest-id <unit-id>
   --contract-digest <d> --unit-class <c> [--lighting <l>]` — hand the envelope to the gate as
   `ORCA_DISPATCH_RECORD` (a path, or a `path@ref` fetched out-of-band). The record may be
   worker-supplied: a forged one won't verify against the off-worker key.
3. **At the gate:** `verify.py` verifies the Ed25519 signature against that key, asserts each signed
   field equals the value the run used, **and** that `manifest_id` names *this* unit (so a valid record
   from another unit can't be replayed). Substitution, forgery, replay, or a pinned key with no valid
   record all **fail closed** — against whatever key was discovered, which in-session may be the
   worker's own (the sources above); the fail-closed guarantee bites only where the key is
   off-worker-anchored.

**Soundness condition, stated honestly:** signed dispatch makes a verdict sound *exactly where the
worker cannot influence the verifying key* — i.e., **off the worker's box**, where the orchestrator
(not the worker) owns any injected env and the pin is read against a fetch-verified remote ref. On
the native in-session path the worker controls the env, the local `origin/HEAD` ref, and the working
tree, so the gate stays **advisory** there (the #112 result; ARCHITECTURE.md states the same). The
signature still gives durable value: a CI job, reviewer, or auditor can verify the coordinator's
signature **off-worker** and detect a run that used substituted inputs. Ed25519 is the vendored
`runtime/scripts/ed25519.py` (RFC 8032), so
the gate stays dependency-free.
