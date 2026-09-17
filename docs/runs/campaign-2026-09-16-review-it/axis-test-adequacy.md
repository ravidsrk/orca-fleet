# Axis — Test-adequacy, judged statically (router: matt)

The diff ships no production change (docs report + seed fixtures + one git
bundle artifact), so the "would a revert fail a test" question has no
production subject — revert-prediction is N/A, and per the playbook this axis
judges statically: no suite was executed, no revert was run (executed controls
belong to the fix missions). GO here is not a substitute for those.

The adequacy subject for a report diff is its re-derivation binding: every
numbered claim below was re-derived by read-only inspection (git plumbing
reads against a `/tmp` clone of the embedded bundle; no target code executed).

## Re-derivation record (all at reviewed_sha `c46d4b3f`)

| # | claim (quoted) | re-derivation | result |
|---|---|---|---|
| 1 | `integrity-inventory.txt` hashes | `sha256sum -c` in the report dir | 27/27 OK, exit 0 |
| 2 | `RESTORE.md:3-4` "full leg-1 history … 9 commits" | `git bundle verify` → "complete history"; `git rev-list --count` | OK, 9 total (seed + 8) |
| 3 | 9 cited SHAs (seed, 3 unit heads, 4 landings, tip) | `git cat-file -e` for each in the bundle clone | 9/9 resolve |
| 4 | seed→tip ancestry | `git merge-base --is-ancestor` | OK |
| 5 | 4 wtree bindings in unit manifests + rollup | `git rev-parse <sha>^{tree}` × 4 | 4/4 match (`3ebf9ca2…`, `f7a2983f…`, `d8fc6166…`, `7f032459…`) |
| 6 | `RESTORE.md:14` full-diff hash `b5d9e400…` | `git diff <seed> <tip> \| sha256sum` vs `sha256sum full-diff.txt` | equal |
| 7 | "`seed-*` … reconstruct every byte" | `git show <seed>:<f> \| sha256sum` vs seed files × 3 | byte-identical |
| 8 | "77 lines" (`CHAIN-REPORT.md:81`, ledger G-REVIEW) | line count of `full-diff.txt` | exactly 77 |
| 9 | NC transcripts RED with assertion failures | read `nc-f3-red.txt`, `nc-f5-red.txt` | real `AssertionError`s (`assert True is False`; md5-vs-sha256 hex), not stillborn |
| 10 | suite arithmetic (4 → 5/5/4 → 6) | read `leg1-*.txt` transcripts | consistent: baseline 4; +1 test each for F3/F5; doc-only F6 stays 4; tip 6 |
| 11 | F6 NC exits narrated (clean 0 / control 1) | `git show <head\|base>:README.md \| grep -q 'plaintext (no encryption'` | exit 0 / exit 1 as claimed |
| 12 | F7 "verified true once F3 landed" | static read of `full-diff.txt:31` (`if token is not None and token == ADMIN_TOKEN`) + `seed-notes.py:102` (`denied` branch) | predicts `denied` for None — consistent; NOT executed |

Transcripts: `transcripts/after-restore.txt` (bundle verify, SHAs, wtrees,
diff hash, seed bytes, F6 grep), `transcripts/inventory-rehash.txt`.

## Findings

### TA-FYI1 (FYI) — F6 negative control has no transcript artifact

`manifest-f6.json` carries `"artifact": null` with narrated exits ("observed,
transcript in chain report re-enumeration section"). The claim re-verified
(row 11), and the grep command is re-executable by anyone holding the bundle,
so nothing is lost — but a pasted transcript would have removed the one
narrated link in the NC chain. No action (post-merge record).

## Axis verdict

No Critical, no Required. Worst: FYI. (Self-verified — no independent verifier.)
