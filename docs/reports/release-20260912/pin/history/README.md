# Frozen prior states of the pin report

Two snapshots of `docs/reports/release-20260912/pin/` as it stood earlier in the 2026-09-12
release audit:

| Directory   | What it holds |
|-------------|---------------|
| `e2e7adab/` | the state at commit `e2e7adab` — claim inventory, outstanding claims, audit result, integrity, manifest, parked register |
| `snapshot/` | the first-atomization state — the frozen claim inventory and atomization the live report's corrections are measured against |

## Their relative links do not resolve from here, and that is correct

Both snapshots are byte-faithful copies. Their markdown carries the links the live report carried —
`](claim-atomization.json)`, `](receipts/orchestration-full.json)` — which resolved against the live
`pin/` directory and do not resolve against a snapshot that was never given those siblings. Roughly
960 links are dead in this sense.

They are left dead on purpose. Re-pointing them would edit the bytes of a record whose entire value
is that the bytes are unchanged: a snapshot you have rewritten is no longer evidence of what was
there. Read a snapshot's links against
[the live report](../) — that is the tree they were written in.

`tests/test_docs_navigation.py::NavigableDocsHaveNoDeadLinks` excludes `docs/reports/**` for this
reason and states it, so the exclusion is a documented rule rather than a silent hole. Everything a
reader navigates is still checked.

## The duplicates are free

`snapshot/claim-atomization.json` and `snapshot/claim-inventory.frozen.json` are byte-identical to
their live counterparts. Git is content-addressed, so identical content is stored once — both paths
point at the same blob. The duplication costs working-tree bytes, not repository size, and deleting
it would trade evidence for nothing.
