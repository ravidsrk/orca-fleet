# The verify gate — native hooks, with an enterprise fallback

Packages the independent verifier ([`runtime/scripts/verify.py`](../runtime/scripts/verify.py)) as a
**completion gate**: a unit cannot be marked done until its evidence manifest passes. The gate
*mechanism* is native (Claude Code hooks); its **content** — an independent second-session verdict
that anchors to authorities OUTSIDE the worker's manifest (the coordinator's frozen contract for
scope, GitHub for review, the artifact/replay for the negative control) — is the differentiator, and
it runs the same `verify.py` no matter which surface fires it.

## Native path — plugin hooks (default)

[`hooks/hooks.json`](../hooks/hooks.json) wires two events to
[`runtime/scripts/verify-gate.sh`](../runtime/scripts/verify-gate.sh):

- **`TaskCompleted`** (agent-teams) — **exit 2 → prevent completion + return feedback**. The native
  "you cannot mark this task done until it verifies."
- **`Stop`** — **exit 2 → refuse the turn end** until the manifest passes.

`verify-gate.sh` is **fail-closed**: if no manifest is named (`ORCA_MANIFEST` unset / missing), if no
authoritative contract is supplied (`ORCA_CONTRACT_SOURCE`/`ORCA_CONTRACT_DIGEST` — without it the
scope check cannot be certified, so it blocks), or the verifier errors, it blocks (exit 2) — an
un-runnable verifier is never a green light.

```
coordinator sets ORCA_MANIFEST + ORCA_CONTRACT_SOURCE + ORCA_CONTRACT_DIGEST + ORCA_UNIT_CLASS
  (+ ORCA_REPO for the review lookup, ORCA_BASE, ORCA_SYMBOL, ORCA_EXECUTE_NC) — NOT the worker
   → TaskCompleted / Stop hook fires verify-gate.sh
       → verify.py re-derives against authorities outside the manifest; the unit CLASS that decides
         whether review + negative control run comes from the dispatch (ORCA_UNIT_CLASS), never the
         manifest — missing/unknown ⇒ mutation (fail-safe)
         (scope ← coordinator contract · review ← GitHub · negative control ← artifact/replay · commits · freshness)
           → exit 0 allow · exit 2 BLOCK (with feedback)
```

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

- **Native `Stop`/`TaskCompleted` hook — ADVISORY.** The gate runs *inside the graded worker's
  session*, so the worker can set `ORCA_*`. Here the gate is defense-in-depth (it still catches an
  honest mistake or a lazy manifest), **not a soundness boundary.** It emits a `NOTE` saying so
  unless `ORCA_PROVENANCE` asserts off-worker origin.
- **CI / MCP-Task / SDK-subprocess — SOUND.** On these surfaces the coordinator (not the worker) sets
  the env, so the frozen denominator and unit class are trustworthy and the guarantee holds. Set
  `ORCA_PROVENANCE=ci|mcp|sdk|dispatch` there to suppress the advisory `NOTE`.

Treat a green native-hook result as a *strong hint*, and the CI/MCP verdict as the *gate*. Binding the
contract digest + unit class to a signed / out-of-band dispatch record (so the native path is itself
sound) is tracked as a follow-up.
