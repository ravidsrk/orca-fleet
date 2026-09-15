# T8 — U387P: ledger/process remediation for the #387 Greptile threads

## Problem
Seven Greptile threads on rollup PR #387 dispute the run's own process records
(ledger flags, review/integrate templates, one manifest field). Triage verdicts
(all read + checked against BASE f66bd20 by the coordinator):

- REAL, fix here: T1/T2/T3 use park class `proof-park`, which
  `runtime/ledger-contract.md` does not allow (threads 4009585869-pt2,
  real on all three rows); `u385-manifest.json` head_tree `022dc9a` !=
  `git rev-parse d6fc2cc^{tree}` = `4ee55a0` (thread 4008769533, verified);
  `review-template.md` abbreviates worker_done as "Contract flags as usual"
  (thread 4008414640) and has no TARGET checkout line, so instantiated specs
  carry the malformed `git fetch origin + checkout <sha>` (thread 4008842923,
  still in the newest review-364ff specs); no template names the close-refresh
  actor (thread 4008046401), the union-invalidates rule (thread 4008218867),
  or the option-A self-reference rule (threads 4009130325, 4010139829).
- DEFENDED (builder implements the cited trace, coordinator replies):
  T1/T2 REVIEWED=t stands — blind-verdict GO at reviewed==head
  (T1 R2 GO 5202783703, T2 R3 GO 5203193997); the contract's REVIEWED is a
  build-blind PASS, the verify.py INDEPENDENCE bar is the separately disclosed
  RED leg + needs-human park. T3 REVIEWED=t stands — the maintainer's stated
  condition (reply 4011794979: f "until T6 lands and receives a passing
  review") is met by T6 GO 5205447863 + verify 6/6; this unit adds the missing
  GO citation to T3's evidence (thread 4011637662).

## Criteria
- C-1: T1/T2/T3 park reads `needs-human:` + the existing ask text + run ref;
  no other flag changes; T3 evidence cites T6 GO 5205447863; T4 evidence notes
  the C-2 correction. No `proof-park` remains in the ledger.
- C-2: u385-manifest.json head_tree = 4ee55a0, narrative consistent, and
  verify.py for U385 re-run: scope leg green, all other legs unchanged
  (review leg still RED-disclosed — expected, record it).
- C-3: review-template.md carries a TARGET line with a correct separator
  (`git fetch origin && git checkout <sha>`) and an explicit worker_done
  contract (`--outcome succeeded|failed`, `--report-path`, `--files-modified`,
  preamble `--from`/`--dispatch-capability`); no "as usual" remains.
- C-4: new taskspecs/conductor-close.md documents CLOSE (clean-worktree
  re-runs at the merge tip, coordinator records appended, head/head_tree
  re-bind, pr fill, verify.py, chore(run) commit), the option-A rule
  (head_sha = code tip at build; conductor re-binds to the reviewed tip at
  close — a commit cannot name its own SHA), the union-invalidates rule
  (pre-union bindings are stale until re-run at the tip), and the
  out-of-process-merge rule (disclose actor + re-verify, T6 precedent).
- C-5: `python3 -m unittest discover -s tests` and `scripts/validate.py` green.

## Negative control (probes, one per fix)
Record each probe as a shell one-liner + output in u387p-negctrl.txt, both
directions (fix reverted = RED exit nonzero; fix applied = GREEN exit zero):
- C-1 probe: `git show <reverted>:ledger | grep -c proof-park` nonzero / zero.
- C-2 probe: `head_tree == $(git rev-parse <head_sha>^{tree})` mismatch / match.
- C-3 probe: `grep -c 'fetch origin + \|as usual' review-template.md` non/zero.
- C-4 probe: `test -f conductor-close.md && grep -c option-A` etc, absent/present.

## Red-first
Probes written + RED before the fixes; quote the RED outputs in the manifest.

## Hot files (ONLY these)
- `docs/runs/2026-09-14-clean-sweep-tracker.md` (T1/T2/T3/T4 rows only)
- `docs/runs/2026-09-14-clean-sweep-tracker/u385-manifest.json`
- `docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/review-template.md`
- `docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/conductor-close.md` (new)
- `docs/runs/2026-09-14-clean-sweep-tracker/u387p-manifest.json` (new)
- `docs/runs/2026-09-14-clean-sweep-tracker/u387p-negctrl.txt` (new)

## Out of scope / frozen
- Historical instantiated specs (fix-*/review-*/integrate-*.md) stay FROZEN —
  they are evidence of what was issued, not living docs. Do not touch them.
- No flag changes beyond C-1 (REVIEWED/MERGED/etc. untouched).
- No code, no evals, no badge regen (no test-count change expected; if the
  suite count moves, regen in its own commit per run convention).

## Worker protocol (run conventions)
- Ownership: ONLY the hot files above. Commit locally on your unit branch, one
  concern per commit. Do NOT push, merge, or touch BASE.
- Manifest: follow the u388-manifest.json schema (files block mirrors
  u385-manifest.json's shape for doc-only changes). `contract.source` +
  `digest` are given in your TASK preamble. `head_sha` = your tip (coordinator
  re-binds at close). unit_class: `build-change` (U385 precedent; verify.py
  treats it as mutation, so the NC below must be replayable).
- The four C-1..C-4 probes JOIN into ONE negative_control.command
  (`sh -c 'probe1 && probe2 && probe3 && probe4'`, self-contained: git show +
  grep/python one-liners on committed content only) so verify.py can replay it
  reverted (RED) and fixed (GREEN).
- worker_done: three-sentence summary + explicit --outcome, tip SHA, quoted
  gate outputs + RED-first evidence, --files-modified, --report-path = manifest.
