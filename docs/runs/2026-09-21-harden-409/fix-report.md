# h409 FIX — builder report (task_b879ad45c5b2, worktree h409-w2)

**Branch:** `h409-fix`, cut from BASE `0d552ec9` (`review/2026-09-21-harden-409`). **Pack:** addy. **Lighting:** lit.
**Spec:** `docs/runs/2026-09-21-harden-409/build-fix.md@0d552ec9` (sha256 `af9c014f…`). No PR opened (integrator owns it).
**Content commits (base_sha..head_sha = 0d552ec9..81a25d4e):** F-3 `4f1e1e1c` · F-4 `f4da24db` · F-5 `e5221944` · F-1/F-2 `8265f0cf` · test-fixture split `81a25d4e`.
**Manifest:** `fix-manifest.json` (this directory) — criteria F-1..F-5 with witnesses, executed revert control, receipts pinned in `artifacts[]`.

## Per item — exploit-test first, revert proves the test bites

| # | Reproduction (from verify.md) | After the fix | Pre-fix (negative control) |
|---|---|---|---|
| F-1 (C5) | check.py plants a `gh` in an empty writable dir first on PATH during `--execute-nc`; the later review leg reads its APPROVED → exit 0 | `_Authority.resolve()` pins gh ABSOLUTE in `main()` before any check; the planted gh is never consulted (its log stays empty); the pre-pinned authority answers → exit 2. Worker-writable gh: fatal on `--provenance ci\|mcp\|sdk\|dispatch` / enforcement; `NOTE: review_authority: advisory (gh at <path> is worker-writable)` on the native lane | `AssertionError: 0 != 2` — the false GREEN |
| F-2 (C1) | `--repo` omitted → repo from `origin` (`evil/mirror`) | sound lane: `review_repo: … requires an explicit --repo; fail-closed`; native: `NOTE: review_repo: advisory ('evil/mirror' inferred from origin …)`; `--provenance` signed in the transcript | ERROR (no `_Authority`) |
| F-3 (C2) | `./reports/u/nc.txt` from cwd=`<root>/docs` or `--git-dir <root>/docs` → exit 0 | both git lookups use `Path(path).as_posix()`, the spelling `_resolve` bounded → RED at the root, and the true spelling reads from any cwd | 4/4 RED |
| F-4 (C3) | 0644 / committed-unignored seed signs silently, 4/4 signers | shared `dispatch-sign._seed` refuses `mode 0644 — readable beyond its owner` and `inside a git work tree that does not ignore it`; stderr names `seed custody: <path> mode 0600, outside any unignored work tree` on a pass; verify.py `_Transcript.seed` now loads that one reader | 10/10 RED across dispatch-sign (sign + sign-transcript), verify.py, inventory.py |
| F-5 (C4) | substituted `_verify_sig.py` → byte-identical signed envelope | `toolchain.files` hashes verify.py + `_verify_sig.py`, `diff_scope.py`, `ed25519.py`, `dispatch-sign.py`; `run_report.signed_transcript` refuses an absent / partial / mismatched set against `runtime/scripts/<name>` at the pin | 4/4 ERROR (no `TOOLCHAIN_FILES`) |

Negative control receipt: `fix-negctrl.txt` — the three scripts reverted to `0d552ec9`, tests at head, the seven killer classes: **58 ran, 15 failures + 43 errors**.
Tests receipt: `fix-tests.txt` — the five affected modules at head: **633 OK**. Full suite (all 44 modules): **1999 OK**. `python3 scripts/validate.py` exit 0; `ruff check` clean; the verify.py width pin holds at 91 (`_Authority` paid for by folding `_WAIVER_NEEDS_EXECUTED_NC` into `check_review`).

## Decisions the spec left open (taken, not guessed silently)

- `dispatch` provenance is treated as sound alongside ci|mcp|sdk — verify-gate.sh's own sound case lists all four; the stricter direction.
- Custody classification applies the "standard system bin dir" carve-out to the PATH entry's directory (`/opt/homebrew/bin` included); the realpath decides work-tree / temp-dir / user-writable. Homebrew's Cellar is user-owned, and the spec carves system bins out by convention.
- The custody check at use covers `write --key` on inventory.py too (same `_read_seed`).
- Test fixtures that wrote seeds 0644 in-repo were the same blind spot as C3 and now create seeds the way gen-key leaves them; two test classes that inherited their parents' tests were split into test-less fixtures.

## The unit's own verify.py run (fix-transcript.json, unsigned — no coordinator seed on this worker)

Run with `--execute-nc --nc-command <the seven killer classes>` and `--transcript-out`: `toolchain.files` names the five verifier files at head, exit 2. The executor did NOT run in this invocation — verify.py admits the executed control only on a clean admission (`execute_nc and not fatal`), and the structural REDs below block it; the executed revert evidence for this unit is the `evidence-run.py` negative-control receipt (`fix-negctrl.txt`, scripts reverted to base, 58 RED), not a verify.py replay. The REDs, all structural: (1) no `pr.number` — no PR by spec; (2) `head_sha` not yet an ancestor of the base — pre-merge; (3) `scope: no criterion ids in the authoritative contract` — build-fix.md writes its items as `**F-1 (C5 …)**` bold bullets, which `CRIT_ID_RE` does not anchor on (the contract is frozen; a `criterion_ids` JSON companion or `- F-1:` spelling on the coordinator side would let scope bind). The manifest declares `contract.criterion_ids` F-1..F-5 explicitly; (4) #352 — the fresh exit-0 ledger record is the five-module suite, not the seven-class control command named to `--nc-command` here (the coordinator names the real one at dispatch; a receipt for that exact command is a 10 s clean-tree re-run).

## Not done / owed

- No PR (by spec). Review threads: none yet.
- The transcript is unsigned (the coordinator's seed is off-worker, as it should be); `dispatch-sign.py sign-transcript` over `fix-transcript.json` binds it once the integrator signs.
