# THROWAWAY — unbound review-it report to prove #415 bind-check goes RED

This file exists only to exercise the `bind-check` CI job added for
https://github.com/ravidsrk/orca-fleet/issues/415 — it proves no mission
ran, it binds to nothing, and the branch carrying it is deleted after the
job output is captured. Do not merge.

RUN: mission=review-it tier=external-run inventory_at=e639f4212bb5f7ad8f89fdcbc4e36e9b5fa79a86 manifest=docs/runs/2026-09-16-review-it-externalrun/manifest.json verifier=GREEN

## Verifier outcome (recorded exactly)

No verifier ever ran. The invocation below is deliberately absent, so the
binder must refuse the report for want of a transcript — among other legs.

## Run-close integrity inventory (sha256)

No entries. The manifest named above was never written, so there is
nothing to pin and nothing re-derives at the pinned commit.
