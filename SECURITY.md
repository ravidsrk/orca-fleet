# Security policy

## Reporting a vulnerability

Please **do not** open a public GitHub issue for a security report.

1. Use GitHub's private vulnerability reporting on this repository
   (Security → Report a vulnerability), or
2. Email **ravidsrk@gmail.com** with a description, impact, and a repro
   that does not include live secrets.

You should receive an acknowledgement within 72 hours. We will confirm
whether the report is in scope and what the fix path is.

## Scope

In scope: `runtime/scripts/` (especially `verify.py`, `verify-gate.sh`,
`dispatch-sign.py`, `ed25519.py`, `pm.py`), secret handling around
`.secrets/` and `ORCA_DISPATCH_*`, and anything that would let a worker
forge a green completion verdict.

Out of scope: vulnerabilities in the Orca runtime, Claude Code, or
`gh` themselves — report those upstream.

## Secrets in this repo

Never commit private keys. `.gitignore` excludes `.env` and `.secrets/*`
except `*.pub`. Coordinator keys are generated with
`runtime/scripts/dispatch-sign.py gen-key` **outside** the clone unless
you pass the documented in-repo override.

The native Stop/TaskCompleted hook is **advisory** in-session; the
soundness boundary is off-worker. See `docs/verify-gate.md`.
