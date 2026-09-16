# REFLECTION — clean-sweep campaign self-test 2026-09-16

Run: `docs/runs/campaign-2026-09-16-clean-sweep/` (BASE `campaign/clean-sweep-selftest`).
Compound-learn proposal — human must approve each line before it lands anywhere.

## Surprises

- The only in-scope real finding (#434) died on credential validity, not absence: the
  environment *provides* `OPENROUTER_API_KEY`, but the API answers HTTP 401 "User not
  found". Presence checks (`-z`) do not predict usability — a cheap preflight probe
  (one auth-check call) would have parked U434 in triage instead of mid-build.
- `gh api` with `-f` on a GET endpoint silently becomes a create call (HTTP 422 "title
  wasn't supplied"); explicit `--method GET` with a query string is the safe form.
- `cmd | tail; echo $?` reports tail's exit, not the command's — two transcripts in
  this run initially carried a misleading `EXIT=0`. Redirect-to-file then echo.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: `gh api` infers POST from `-f` — always pass `--method GET` explicitly on reads.
- GOTCHAS: never read an exit code after a pipe — redirect to a file, then `echo $?`.
- GOTCHAS: a present-but-invalid API key fails at first use — probe paid credentials
  in triage (one cheap call) before freezing a unit that needs them.
- TEST_STRATEGY: diagram-regen units pin the frozen callout text in a contract test
  (spec + alt + embeds + caption-notes-absent + JPEG magic bytes) — red-first, and the
  same test is the revert-control oracle since the wire fixed-point passes both ways.
- ARCH_DECISIONS: alt text must match rendered pixels — when regen is blocked, the
  honest state is park-with-disclosure (caption notes stay), never a partial text edit.

## Prompt / playbook tweaks (fleet-side, optional)

- File a backlog item: `triage-state` REDUNDANCY step should probe external credentials
  a fix needs (key validity), not just code/domain existence — this run's U434 lesson.
