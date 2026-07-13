# Playbook — risk-review  (REVIEW: scope-gated specialist lenses)

Recipe: Addy specialist skills (security, performance, accessibility, data-migration) + gstack
scope-gating + adaptive suppression. NOT run on every diff — DISPATCHED when the change surface
triggers the lens.

## Two invocation modes

Diff-triggered (the default, below) — a lens runs when the change surface signals it. TREE-WIDE
(harden-it's audit waves): the fixed point is the whole codebase at the BASE head; scope-gating is
bypassed and every requested lens runs over the full surface.

## Dispatch rule (scope-gated, diff-triggered mode)

Run a lens only when the diff signals it (auth/query/route/dep change → security; render/query/bundle
→ perf; component/markup → a11y; schema/migration → data-migration). Adaptive gating: a lens with 0
findings across 10+ dispatches auto-gates off; security and data-migration are NEVER_GATE (their
value is the miss they'd catch).

## The lenses (each a fresh-context worker, its own protocol)

- **Security:** threat-model-first (STRIDE per trust boundary) → OWASP Top 10 + OWASP LLM Top 10 +
  supply-chain. Treat model output as untrusted (no eval/SQL/shell/innerHTML); block dep scripts
  before first run, never `audit fix --force`; SSRF allowlist with a TOCTOU caveat. A finding needs a
  concrete step-by-step exploit scenario; never test live APIs. One verified finding → grep the whole
  tree for VARIANTS. (Full audit→re-attack loop is `harden-it`; this is the bounded review lens.)
- **Performance:** measure-first (no optimizing without a baseline); symptom→cause tree (slow load →
  bundle vs TTFB); CWV targets; every fix carries a before→after to its metric contract; add a CI
  regression budget (GUARD).
- **Accessibility:** WCAG 2.1 AA (keyboard, ARIA, focus, 4.5:1 contrast, empty/error/loading states)
  + the anti-AI-aesthetic check (no purple/gradient/rounded-2xl slop, no lorem hero).
- **Data-migration:** expand→migrate→contract (additive first, destructive last-and-alone); every
  migration has a TESTED down path written and run before merge; a schema change and its dependent
  code never ship in one deploy (Hyrum's Law + the Churn Rule).

## Completion

Every triggered lens ran (or is a recorded gate-off); each finding names its lens, severity, and (for
security) an exploit scenario; findings emit in the shared schema for the mission's ledger.
