# The verify gate — native hooks, with an enterprise fallback

Packages the independent verifier ([`runtime/scripts/verify.py`](../runtime/scripts/verify.py)) as a
**completion gate**: a unit cannot be marked done until its evidence manifest passes. The gate
*mechanism* is native (Claude Code hooks); its **content** — independent second-session re-derivation
from git + a mandatory negative control + a frozen denominator — is the differentiator, and it runs the
same `verify.py` no matter which surface fires it.

## Native path — plugin hooks (default)

[`hooks/hooks.json`](../hooks/hooks.json) wires two events to
[`runtime/scripts/verify-gate.sh`](../runtime/scripts/verify-gate.sh):

- **`TaskCompleted`** (agent-teams) — **exit 2 → prevent completion + return feedback**. The native
  "you cannot mark this task done until it verifies."
- **`Stop`** — **exit 2 → refuse the turn end** until the manifest passes.

`verify-gate.sh` is **fail-closed**: if no manifest is named (`ORCA_MANIFEST` unset / missing) or the
verifier errors, it blocks (exit 2) — an un-runnable verifier is never a green light.

```
coordinator sets ORCA_MANIFEST (+ ORCA_BASE, ORCA_SYMBOL)
   → TaskCompleted / Stop hook fires verify-gate.sh
       → verify.py re-derives from git (scope · commits · freshness · negative control)
           → exit 0 allow · exit 2 BLOCK (with feedback)
```

## Fallback path — where `allowManagedHooksOnly` disables plugin hooks

Managed/enterprise settings can set `allowManagedHooksOnly`, which blocks user/project/plugin hooks.
The gate is therefore **also** runnable off the hook surface, running the identical `verify.py`:

1. **CI gate** — run the verifier in the PR pipeline (reference snippet; adapt to your CI):

   ```yaml
   # .github/workflows/verify-gate.yml (reference — not enabled in this repo)
   - run: python3 runtime/scripts/verify.py --manifest "$ORCA_MANIFEST" --base "$GITHUB_BASE_REF"
   ```

2. **MCP Task** — expose `verify.py` as an MCP Task the coordinator awaits before advancing a unit
   (rides the MCP Tasks extension; see [platform-ride](platform-ride.md)).
3. **SDK subprocess** — the coordinator invokes `verify-gate.sh` directly as a headless
   subprocess at the unit boundary (works with no hook surface at all).

All three are the same deterministic re-derivation; the hook is just the most ergonomic trigger.

## Why the gate is native but the moat isn't

Anyone can ship a `Stop`-hook gate — the mechanism is a platform primitive (see the absorption-risk
register in [platform-ride](platform-ride.md), R3). What a competitor cannot cheaply copy is what this
gate *checks*: an independent, different-session, git-re-derived verdict with a mandatory negative
control and a frozen denominator. Keep the differentiation in `verify.py`, not in the hook.
