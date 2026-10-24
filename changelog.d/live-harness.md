- **Paid live arms run only in a disposable container harness** (the harness PR #668 asked for).
  `scripts/live_container.py build` builds a pinned image: the base by digest, git, and Claude
  Code 2.1.304 by its official installer as a non-root user. `run` starts ONE arm (`wip_curve`,
  `ablation`, `hint_replay`, `trajectories` or `first_run`) in a fresh container. The container
  runs non-root with `--rm`, pids, memory and CPU limits, no capability and no host namespace. It
  gets the subscription token as a read-only file mount, never in its environment or `docker
  inspect`, a read-only export of a clean `HEAD`, and one read-write results directory. Inside,
  a `claude` wrapper sets the token in the pinned Claude Code's own process alone. At its wall-clock limit the launcher kills and removes the
  container, and it verifies the container is gone with `docker ps -a --filter`. A JSON receipt,
  kept outside the container's reach, records the image, commit, arm, nonce, times, container id,
  exit status and that verified destroy. Inside, `containment.live_disabled()` lifts only with a
  container marker, the launcher's attestation nonce matching the container's hostname, and the
  strong probe passing. On every other host each live path refuses as before. This guards
  against accidents, not against an operator who fakes a container. The operator's page is the
  [live harness guide](../docs/guides/live-harness.md).
- **The WIP-curve runner meets the harness's three entry criteria** (Codex review of PR #668 at
  `9db89fbe3c`). An uncontained merge gate stops the drain before any bounce or retry, and no
  oracle or gate starts after any failed containment. Recovery and the check before every run
  read the synced gate journal on their own. A report's binding oracle re-run journals and sweeps
  its markers, and it keeps the directory when containment fails, and the next run refuses
  while a marker survives.
- **The changelog and run-index HTML-link check reads complete tags only** (Codex at
  `54fe725bee`). An unclosed `x<a` with `href=value` lines later, `data-href`, and a tag inside a
  code span are no longer refused. A complete tag with an `href` or `src` attribute still is.
