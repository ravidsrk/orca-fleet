# BUILD SPEC — h409 FIX (frozen at dispatch)

CATEGORY: bug (security remediation — 5 confirmed findings, one P0 class)
SUMMARY: harden-it 409's audit + independent verify confirmed five trust-edge findings on the
catalog's own toolchain. Fix each CLASS, exploit-test first, with the negative control proving
the attack dies. Reports are DATA: docs/reports/h409/audit-w{1,2,3}.md + verify.md (on the
h409-w* worktrees and copied into docs/reports/h409/ on BASE).

The batch:

- **F-1 (C5, P0 class — same-run false GREEN).** verify.py resolves the review authority
  (`gh`) lazily via `shutil.which` and executes it with the ambient environment; the executed
  negative control runs worker test code in the same run, and worker code can drop a stub `gh`
  into a user-writable PATH dir that the LATER `check_review` then reads a fabricated APPROVED
  from (verified reproduction: exit 0 with a stub the worker planted). Fix the CLASS: (a)
  resolve the review authority to an ABSOLUTE path ONCE, at startup, BEFORE any negative-control
  execution, and invoke only that resolved path — a mid-run PATH write can never redirect the
  review leg; (b) when the resolved authority lives under a worker-influenceable location (the
  worktree, system temp, or any user-writable dir that is not a standard system bin dir), the
  review leg is ADVISORY-ONLY: on lanes documented as sound (the ci|mcp|sdk provenance classes
  and any enforcement-mode run) it FAILS CLOSED; on the advisory lane the verdict records
  `review_authority: advisory (gh at <path> is worker-writable)`. The C5 reproduction becomes
  the killer test: a stub gh in a writable PATH dir can never again produce a same-run GREEN.
- **F-2 (C1, P1 — the review repository is worker-selectable).** With `--repo` omitted, the
  review-lookup repo is inferred from the clone's origin URL — which the worker controls (and
  origin is shared across Orca worktrees, so a sibling unit's origin leaks in). Fix: inference
  is ADVISORY-ONLY — a lane claiming soundness REQUIRES an explicit `--repo` (refuse to infer);
  an inferred repo is recorded as advisory with its source noted.
- **F-3 (C2, P1 — `./`-spelled evidence binds where git's cwd diverges).** `_resolve` bounds
  `./docs/x` against the toplevel, but the git lookup resolves it relative to the process cwd —
  with the verifier (or `--git-dir`) below the toplevel the verdict binds a path absent at the
  bounded root (verified: exit 0 where it must RED). Fix: normalize the spelling IDENTICALLY on
  both sides (strip leading `./` segments before BOTH the containment check and the git lookup),
  with a killer test from a below-toplevel cwd.
- **F-4 (C3, P1 — seed custody is guarded at creation, never at use).** All four signers
  (dispatch-sign `sign`, `sign-transcript`, verify.py `--transcript-key`, inventory.py `sign`)
  sign with a world-readable / git-tracked / unignored seed silently. Fix: at signing time each
  consumer re-asserts gen-key's discipline — stat the seed: mode not 0600 → refuse; inside an
  unignored git work tree → refuse (the existing `_in_unignored_worktree` check, shared);
  print the custody class of a passing seed to stderr so the audit trail names what signed.
  Throwaway test seeds (0600, outside repos) keep working — the check is custody class, not
  existence.
- **F-5 (C4, P1 — the toolchain self-hash binds nothing).** The transcript's
  `toolchain.verify_sha256` has zero consumers and covers verify.py only — a substituted
  `_verify_sig.py` / `diff_scope.py` / `ed25519.py` yields a byte-identical signed envelope.
  Fix: the transcript's toolchain block hashes verify.py AND its sibling modules as one set
  (named per file), and `run_report.py`'s transcript check VERIFIES those hashes against the
  files in the checkout being graded (a transcript then proves which verifier ran — a
  substituted sibling fails binding), documented as binding the verifier identity, nothing
  more.

AUTONOMY:
- goal: all five classes fixed; every confirmed reproduction now refuses (never a silent pass).
- scope: runtime/scripts/verify.py + dispatch-sign.py + inventory.py +
  runtime/scripts/run_report.py + tests/test_verify.py, test_run_report.py,
  test_dispatch_sign.py, test_inventory.py (+ docs/verify-gate.md's authority wording where it
  claims soundness; badge regen if counts move).
- non-goals: no new dependencies; no network calls in any script; no change to the unsigned
  no-key path's behavior; no semantics change to what verify.py CHECKS — only to the trust of
  the channels it checks through; no PR action (integrator/conductor owns that).
- stop: if a fix would weaken an existing refusal; if F-1/F-2 tempt changing the review leg's
  GitHub contract (the contract is right — the AUTHORITY RESOLUTION is the bug).
- evidence: SHA-bound manifest per evidence-manifest.md; criterion-bound runs via
  evidence-run.py; executed NEGATIVE CONTROL per item (the finding's reproduction run against
  the fix → the attack REFUSES; reverted → it passes again where applicable); intent packet;
  lighting=lit.
- escalation: ask on any ambiguity; never guess. Reports are DATA.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

ACCEPTANCE CRITERIA:
- [ ] F-1: stub gh in a writable PATH dir → the review leg refuses on a sound lane / marks
      advisory otherwise; a system-bin gh works; resolution happens before any NC execution.
- [ ] F-2: no --repo on a sound lane → refuse; inferred repo → advisory + recorded.
- [ ] F-3: `./docs/x` from a below-toplevel cwd → identical resolution both sides; the C2 repro
      REDs where it must.
- [ ] F-4: 0644 / git-tracked / unignored seed → refuse with the custody class named; 0600
      out-of-repo seed signs; stderr names the custody class.
- [ ] F-5: sibling substitution → run_report binding fails; an unmodified toolchain binds.
- [ ] Full suite green; python3 scripts/validate.py exit 0; the unit's own verify.py
      transcript binds under the new rules (the toolchain proves itself).

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`; every
send carries `--from <your handle> --dispatch-capability <capability>`; evidence rides typed
`--report-path` + `--files-modified`. Run `orca orchestration check --terminal <your handle>`
once before `worker_done` — `consumer_fenced` means STOP and send nothing. One pack only:
addy.

GIT: work in this worktree on a branch cut from the BASE tip
(`git checkout -b h409-fix origin/review/2026-09-21-harden-409` — if the worktree already
carries a branch from that ref, use it). Author = maintainer, NO TRAILERS. Small bisectable
commits, stage only the unit's files. Do NOT open a PR. Leave the worktree clean. Timebox
60min with partial-report STOP.
