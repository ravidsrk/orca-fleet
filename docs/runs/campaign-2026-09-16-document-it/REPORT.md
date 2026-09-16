# Run report — document-it self-test vs orca-fleet (campaign 2026-09-16)

RUN: document-it self-test · BASE: campaign/document-it-selftest @
6390743815f8f435181fa410cce374587128b30a (origin/main tip) · FINAL:
c064b27c9cce4a46aecf5c1a55fcb11bf77dd524 · waves=1 · worker pack: matt (sole router)

**Verdict: DOCUMENTED.** The map re-derived at the final head shows zero critical gaps;
all 16 frozen reference cells and all 16 frozen explanation cells are filled; every
factual claim in the landed page binds to a checked anchor and every cell's rename
control went RED; the page is reachable in one hop from README; diagrams
cross-reference clean (zero orphans). Zero cells parked.

This is a campaign self-test run, not a proof-tier submission: it does not advance
`document-it` past `doctrine-only` (no `proof_evidence:` change, no promotion PR —
promotion is out of scope per the mission and the workflow constraints).

## Pipeline evidence

SELF-ORIENT: read `skills/document-it/SKILL.md` in full, `AGENTS.md`, `ARCHITECTURE.md`,
and every composed/ridden playbook and runtime policy (`doc-coverage`,
`remediate-finding`, `acceptance-review`, `compound-learn`; `evidence-manifest`,
`merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle`,
`liveness-resume`, `ledger-contract`, `attention-budget`, `gate-classification`).

EXTRACT (script, not a reading) at BASE:

```
python3 docs/runs/campaign-2026-09-16-document-it/extractor/extract.py \
  docs/runs/campaign-2026-09-16-document-it/extractor
→ surface digest sha256:058e51cdf0384da8e4f1d958f115a5beac080c453fc796c1849921a00022993a
  @ 6390743815f8f435181fa410cce374587128b30a
  A skills: 21  B clis: 29  C config: 7  (57 entities)
```

Output: [extractor/surface.json](extractor/surface.json),
[evidence/extract-output.txt](evidence/extract-output.txt). Sub-surfaces: published
skills (frontmatter `name`), script CLIs (`runtime/scripts`, `scripts`, `hooks/*.sh`
with `--help` capture), config keys (`hooks.json`, `settings-snippet.json`,
`runtime/*.json`, `.env.example`, `ruff.toml`).

MAP (grep-able evidence per quadrant, user-facing homes only): [coverage-map.md](coverage-map.md)
with judged verdicts; raw hits [evidence/map-raw.txt](evidence/map-raw.txt),
[evidence/map-table.md](evidence/map-table.md). Result: skills 21/21 fully covered (all
four quadrants — every guide carries Invoke/worked-example/When sections, line-verified);
13 covered CLIs/configs; **16 critical gaps** (14 CLIs + 2 configs, zero coverage
anywhere). Diagrams: 18 skill tokens across README + guide mermaid blocks, zero orphans
([evidence/diagram-entities.txt](evidence/diagram-entities.txt)).

FREEZE (human gate — spawned auto-resolve, each logged in [DECISIONS.md](DECISIONS.md)
and `docs/DECISIONS.md`): 16 reference cells FROZEN-FILL; 16 explanation cells
FROZEN-ATTEMPT (fill where rationale is in-tree, else park `explanation-needs-author`);
all B/C tutorial cells bounded OUT (per-script tutorials are the mission's named
anti-pattern); common-gap explanations for covered entities deferred to backlog (never
frozen). Frozen list never grew mid-run.

BOOTSTRAP: `preflight.py --base campaign/document-it-selftest --fork-point 6390743…`
→ OK (fresh-branch WARN, expected). Ledger: [LEDGER.md](LEDGER.md)
(`RUN solo-no-orca-run · BASE campaign/document-it-selftest · FORK_POINT 6390743… ·
WIP builders=1 reviewers=1`).

PER CELL (reference-first; same-file serialized chain, one commit per cell; no-gh lane):
WRITE from code archaeology (implementation + pinning tests read, never the old docs) →
CLAIM-VERIFY (`extractor/claimcheck.py`: flags/subcommands/API/keys/paths/exits/anchors)
→ instructed-isolation self-review (D3, labeled weaker) → LAND as one commit on BASE.
Table below; per-cell notes in [cells/](cells/); rename transcripts in
[evidence/nc-*.txt](evidence/).

RE-MAP at FINAL (`c064b27c`, same extractor, new SHA — never the frozen copy):
entity set identical (57/57), CLI flags identical, zero all-dash rows (was 15 + 2
mention-only). Raw: [evidence/map-raw-final.txt](evidence/map-raw-final.txt),
[evidence/map-table-final.md](evidence/map-table-final.md),
[evidence/surface-final.json](evidence/surface-final.json). Re-derivation is stable:
tagged re-run byte-identical (TABLES-IDENTICAL, RAW-IDENTICAL).

Claim check at FINAL: `claimcheck.py` → 16 section(s), 0 unbound claim(s), exit 0.
The run-close commit after `c064b27c` touches the run directory only — no quadrant-home
content changed since the re-map (verify: `git diff c064b27c..HEAD --stat`).
Reachability: `README.md:542` → `docs/runtime-scripts.md` (one hop); all 16 sections and
16 Why blocks live on that page. Diagrams unchanged by a docs-only run; no new orphans.

Gates: `scripts/validate.py` → all 21 missions valid; `unittest discover` → 1490 tests,
2 errors found and fixed pre-close (both mine: remap file moves vs tracked names —
commit below), targeted re-run 170/170 OK; full-suite re-run at close below.

## Per-cell ledger (32/32 terminal, 0 parked)

| cell | entity | quadrant | commit | NC control (all RED) |
|---|---|---|---|---|
| doc-r01 | decisions.py | reference | 107df88 | --lens→--omitted |
| doc-r02 | deny-hook.sh | reference | 1aa143a | --settings→--opts |
| doc-r03 | diff_scope.py | reference | 909445a | --strict→--rigid |
| doc-r04 | ed25519.py | reference | d32fb07 | def checkvalid(→def qcheck( |
| doc-r05 | egress.py | reference | 8ac13c7 | --payload-class→--kind |
| doc-r06 | floor_guard.py | reference | 0f840c5 | --constraints→--limits |
| doc-r07 | gate-batch.py | reference | aade22d | --question-file→--qfile |
| doc-r08 | guard_text.py | reference | 19db585 | --timeout→--pause |
| doc-r09 | hitl-loop.template.sh | reference | b452bb0 | --rounds→--loops |
| doc-r10 | pm.py | reference | 6036c0a | PATH move tests/test_pm.py |
| doc-r11 | sandbox_doctor.py | reference | a6cedd3 | PATH move tests/test_sandbox_doctor.py |
| doc-r12 | spawn_worker.sh | reference | 65fb669 | --mark-ready→--ready2 |
| doc-r13 | watchdog.py | reference | 52d9f20 | --heartbeats→--pulses |
| doc-r14 | wtree.sh | reference | 0e6db58 | PATH move tests/test_evidence_run.py |
| doc-r15 | one-way-doors.json | reference | 80da007 | scope-change→scope-drift |
| doc-r16 | watchdog.json | reference | 29a3d24 | wedge_frozen_s→wedge_idle_s |
| doc-x01 | decisions.py | explanation | 3bbbabd | NEVER_GATE→ALWAYS_GATE |
| doc-x02 | deny-hook.sh | explanation | e03c695 | permissionDecision→verdictChoice |
| doc-x03 | diff_scope.py | explanation | 5577128 | ScopeError→ScopeFault |
| doc-x04 | ed25519.py | explanation | 6ab1093 | hashlib→hashmagic |
| doc-x05 | egress.py | explanation | b219fe5 | head_digest→tip_digest |
| doc-x06 | floor_guard.py | explanation | e735c7f | _WAIVER_ID_PREFIX→_EXCUSE_PREFIX |
| doc-x07 | gate-batch.py | explanation | b03989d | TERMINAL→FINALS |
| doc-x08 | guard_text.py | explanation | 85566a4 | FORGED_BANNER→FAKE_BANNER |
| doc-x09 | hitl-loop.template.sh | explanation | 4be0a02 | REPRODUCED→CONFIRMED |
| doc-x10 | pm.py | explanation | 220a552 | _INVISIBLE→_HIDDEN |
| doc-x11 | sandbox_doctor.py | explanation | 2b8426d | names_recipe→titles_recipe |
| doc-x12 | spawn_worker.sh | explanation | 6d8f343 | MARK_READY→FLAG_READY |
| doc-x13 | watchdog.py | explanation | 7401e49 | SETTLED→FINISHED |
| doc-x14 | wtree.sh | explanation | 0cd6cfe | TMPIDX→SCRATCHIDX |
| doc-x15 | one-way-doors.json | explanation | 208552d | live-credentials→live-tokens |
| doc-x16 | watchdog.json | explanation | c064b27 | max_nudges_per_dispatch→max_pokes |

Flagless CLIs (pm, sandbox_doctor, wtree) used PATH-anchor controls — the check verifies
their anchored test paths, and moving the file went RED. Every control ran on a
throwaway `nc-throwaway-*` branch, deleted after, with the mutated file verified
restored.

## Deviations (carried from LEDGER.md)

- D1 no-orca-run: no Orca Run namespace, no dispatches. Liveness/resume/dispatch
  mechanics unexercised by this solo self-test.
- D2 no-gh: local-merge commit chain instead of PRs (workflow constraint). Promotion PR
  owed, out of scope.
- D3 review-not-independent: instructed-isolation self-review per cell, labeled weaker.
  The terminal rests on the mechanical oracle, never the review.
- D4 freeze-gate auto-resolve: spawned session, recommended options, all logged.
- D5 (run-evidence hygiene): the full suite caught 2 errors from my remap file renames
  (tracked `map-raw.txt`/`map-table.md` moved aside); fixed by restoring tracked names
  and adding tagged map outputs. No unit bounced; rework=0.
- Lesson learned mid-run: a rename containing the original as a substring
  (`--lens`→`--lens-x`) stays GREEN — all controls use disjoint tokens.

## WIP-curve protocol row

Single dispatch wave (solo builder, self-review):

| wave | WIP | throughput | latency_median | latency_max | rework | freshness |
|---|---|---|---|---|---|---|
| wave=1 | builders=1 reviewers=1 | throughput=112.2 (32 verified-CLOSED in 1027s; micro-cells — single doc sections, disclosed) | latency_median=30s | latency_max=114s | rework=0 | freshness=0 |

Latency measured as land-commit spacing (build→verify→land per cell, solo proxy).

## Backlog (noticed, not frozen)

- Common-gap explanation cells for 10 covered B/C entities (coverage-map.md §Backlog).
- JPG architecture diagrams are not machine-extractable (sidecar entity list, future run).
- `proof_evidence:` for document-it still absent by design (campaign run, no tier claim).

## Run-close integrity inventory (sha256)

Command: `sha256sum` over every file under `docs/runs/campaign-2026-09-16-document-it/`
except this REPORT.md (whose integrity is its git blob). Re-hash to verify.

```
ec3a6f59617229800f0ac5b231706cb71e168ac909ce75ef8a9b16407d3c039d  cells/doc-r01.md
e2faf7d7cba4cf9c8a25b257add01dce05870c76ddf2d9038c63ee2a8abdce45  cells/doc-r02.md
a8ead9dbf76a9b40bf0fc97e117f0ddcc3976b0c6b350b13d1b4fde64486db7a  cells/doc-r03.md
fc3d568e1a13f08735c1cf68bb2085866c96146dfc0e7f00352052d3db5919d2  cells/doc-r04.md
9d45e2a3f0293fedd8db2f5cd65d45aa26b605b614c08db483e5e8e34d9bbd3e  cells/doc-r05.md
a22dae526107afe20ac225b0370e76be4d8162604551017631a588cbf0cddfc1  cells/doc-r06.md
9ebb3ab7ead53719bd40e3237afb0864b8b5fa096d781b03a9e6e1b6f731cba1  cells/doc-r07.md
5f40007d354ee9cba86ed371ee95ba45dfd345fe42cae2299339d6e185216690  cells/doc-r08.md
93ad14eee8dab9cafbbeae0dac120763f24bab7b0f478e963d1d51b27a95eba9  cells/doc-r09.md
044bf0f08a35fdaff3f9a5b8def35f3b0a7bf9571b62f2c454a30a2105983aee  cells/doc-r10.md
f46335942d0177db5068f2a38401ab8e06f06a74b494cf36d6c3adc3ea7e14b6  cells/doc-r11.md
ccdf80d9d9a72f7880db2d5d34f81af003c332066c714faae8bf753be546c02a  cells/doc-r12.md
0942f0141c040bfbbaac6dfd8629b8acbca29f8833d3551ba91b734314bfcecb  cells/doc-r13.md
93c3a6cf3a0e3406bbdcf2f522dd6daa03837eea087ccc939a5d0b07a271f767  cells/doc-r14.md
71cb7abc08c2d9af9576bbd2646cb6bb9001339baf4b9cdd8301694d6f0792cf  cells/doc-r15.md
7e438cc71d08da3c220215d10345bf78453d3cc18e93bbbe1026b452905e21ef  cells/doc-r16.md
ef1b94a53b80dca42f5c8d7cb46749fbfcae46484d3aa384e71db7518873af41  cells/doc-x01.md
a8a8074bbcd3d829e686e87bdf49c7c3f3931d44cc248dcfc97e29ddf7b10a52  cells/doc-x02.md
503e796a9e778f9bcc2ea65c4a420d9b22452462105b9dc0f7e3799c0a2d081a  cells/doc-x03.md
b28d7ba5e8afb30b48f4327e63612502bee36070bf73d224e0a44601fba7807c  cells/doc-x04.md
39014c322fbc2557254daa699a5c3520e50714fbf7e1d02dfd1b75365cc579e8  cells/doc-x05.md
9b443b9065e878a2a5736b63962d7acd49fce2fbf7aa853d63dcae1aed5c71fb  cells/doc-x06.md
0d4d620b89a12da6d3ff9607ac1bdea014917de4c97a7a52d3a93c72a5826727  cells/doc-x07.md
57c105ab9e1561bcd0aecc8a23f4f04b914d63b905284424186c0e2694d04c26  cells/doc-x08.md
4a61b926ded63ce6b7de539cf4dfee136e9eabebd1c0e15ea6fd7053efa2fa5d  cells/doc-x09.md
e528ac96ea177c6ea77b2ff77aa26def2114d3b790ad22a251eeececb864bb7b  cells/doc-x10.md
0bef7f6adfa3a9f3fadc1b7afda52d48ad706905181423ee044721ac69dae519  cells/doc-x11.md
cc93782c9164e314bf300c528b4c17aafd750e226e1ea85deef2203728b40ac7  cells/doc-x12.md
f62c22f17fcc811a3bd1fc82d05f994329f7a3ead321c9fcdfd1eac2e15a7c09  cells/doc-x13.md
5d6d4cfecf8326aaef398f15d4bb5cf2bd111d292eb7d2bde9bd18d27d4dec13  cells/doc-x14.md
cb47872ee1888aefab464cc9ab888252e0bad7b54f1be2503003fb18f76b7ed4  cells/doc-x15.md
f228b7d148adecc2fa766c2f3ec8832cc319344ccb8a84db9102b19b65112369  cells/doc-x16.md
1d2a49ce94665536e6bb30c877502d21bd2c8f97ed1e652f79056da2e3194f0e  coverage-map.md
3efacf3e5bd9837efcccdd3d3973797f7771b3d921c9c444bae9ce778d81ccbb  DECISIONS.md
c80d14804006020ce4992829ecdf568e5f666e84a11a77f400dbff7fb0fc7ca9  evidence/diagram-entities.txt
a4033248aaf27141be9a96eb5b107b935f1913ee1ff80ae167f5404d73d16ac9  evidence/extract-final-output.txt
8ac20e0ca17ee28bff02fb3e82061c2cbb6733e4a9d52472a69b3347d7165b41  evidence/extract-output.txt
2635dacb8b3b1dbd68b29329538e913c7db39a59f5c4b116326785a373ba92f9  evidence/map-raw-final.txt
edeeb08eaa057d2fda9fb4d01c6195b083e59893212bb69ce792649ce5817286  evidence/map-raw.txt
c92c5232fef612a20649bb9a7af020b6f4329fd42b9753f16daa82f5c6be52dc  evidence/map-table-final.md
c92c5232fef612a20649bb9a7af020b6f4329fd42b9753f16daa82f5c6be52dc  evidence/map-table-run-final.txt
a30e7e2756bc87f70d650fbd1e2b956c7e660b0fdc40db338913e9717f5bc691  evidence/map-table-run.txt
a30e7e2756bc87f70d650fbd1e2b956c7e660b0fdc40db338913e9717f5bc691  evidence/map-table.md
9ccf72196b7b9f9ee5da5d39c518b71866a6446adbed66900ea7014cb8446149  evidence/nc-doc-r01.txt
5db466156056c2be6214fe2c24d0cce2b9720d6e846900497534f769504469de  evidence/nc-doc-r02.txt
52becd76d7a64c377f32a87d25e730867d7d0aed2736da0749b00d4c91f05c77  evidence/nc-doc-r03.txt
77ffdd2dd95134e142261f08d159c1377e0809e0932c94da8aeaddb89e712117  evidence/nc-doc-r04.txt
479b1c346c7fb31bbd8bf14323323089edd9ba2bc0f2d773cfbe2d80d619f055  evidence/nc-doc-r05.txt
40b235e84ee6b34b3a72020648742a7f631e50f5add67afb9cfc49ab757a0ddb  evidence/nc-doc-r06.txt
b88ac05cb6d52c03d8d41e66a84902de47bde32dd66717afa06a8191d3ea5031  evidence/nc-doc-r07.txt
3070e0bb2ec14814cc54fd963df209d20010644c65e1c6eff167c9f3ada811e1  evidence/nc-doc-r08.txt
a33ee0647fe5c9a5a472e47c7ee72740cb888663248f3a8054a3a10fd8b9916a  evidence/nc-doc-r09.txt
8fccdec6b31b463344506a84ccc2450e28bd76686116a33c4275173685da309f  evidence/nc-doc-r10.txt
e50e7f571a15f72c68ef41c87377f6ffa0e1fc9ff9ea12b9060f415eeb2b1f2a  evidence/nc-doc-r11.txt
f8bfd7a0a96a73ddc8731a13fa175bebeddb683301ed5f56a88322902dd8f3ce  evidence/nc-doc-r12.txt
42d1d27a491b101c0a6e275d4b5ab1a6aafde5eb88b27d2b980005c4aa52f058  evidence/nc-doc-r13.txt
7523953e3dd5bbb36a10254cb07982a2100069d02a7f8981c27590ed1b085518  evidence/nc-doc-r14.txt
aa439e021a350566cb8f76b91aa4cdd49c1dcb33ccbf41588a7a6ece9bdb8805  evidence/nc-doc-r15.txt
6acf02710f0722d59b376bc026d0a70787122d67786c442ee4dc366f785b20b7  evidence/nc-doc-r16.txt
73ed2685f8512b001d35bec4dc772f78d9f9bf029bcc967313985b36f6d6b27c  evidence/nc-doc-x01.txt
08b5e6023522ed66b261136deedf6ab2e57d9ab16019941598b747d0ffd1847f  evidence/nc-doc-x02.txt
ee5d814a12972a0f04259e5f4af97a2567ac5dacf64193e97f5f48533576e37f  evidence/nc-doc-x03.txt
65c7798bef30c568b5a10c544b2b04eaf498e8201a5857011ab6c859473257d5  evidence/nc-doc-x04.txt
fc1304feb82cff82002ce9d49e25848cd835911e9a1974b57e1c4a270da90926  evidence/nc-doc-x05.txt
a0703974f476573fb67781a9a1178ea87bd75d228516ff936aa20ab52cb196f8  evidence/nc-doc-x06.txt
533329eda62a96fe5e1b455f22afcd210c0ca42e1ec8e7a2a5256285d9296003  evidence/nc-doc-x07.txt
45d990aa80aa253585c4f489910f3907749ca35c3b55389f32b811cdb25cd596  evidence/nc-doc-x08.txt
5db4490d13ec65253d0e7bb3db52de6da243f9eebdd44d90040dd119add70e73  evidence/nc-doc-x09.txt
3aabbecce30bd70c1802dcb14b5aa01204f5aae506183ea9b8107cea6659d243  evidence/nc-doc-x10.txt
136183717de692abde907e5fc9c8c156b33171f403fc5ef2f347d4b5d5a0afaf  evidence/nc-doc-x11.txt
9790506b89536b15f3e5ab368285f5952c5b2d0bce53cc609efd34e3a6d0420b  evidence/nc-doc-x12.txt
336cbbdffe0a3ff3072378f7753fce4de0dc88d01dd8abd1225310dc194940ff  evidence/nc-doc-x13.txt
eb8690a2e99fe9befed66a5a66e532b099a278450679dd499688586098bd282a  evidence/nc-doc-x14.txt
2ec6e3fe95e5af8bc29d1234d1b5097e3a7b08ca16a5fe2a43fb3f52fe8dc47e  evidence/nc-doc-x15.txt
1ec3e99336a572b7c90c933c5673bbd36cb890dbce77e4fada5e745e0900cd29  evidence/nc-doc-x16.txt
a350db28c56edfe97ef1ef121e386c6bae4672383abbb91572f43eb08a9c0974  evidence/surface-final.json
154398eb854c8536c2ff408ff40011d4d2b32a62d2fcc78e6743077bfc8e26e7  extractor/claimcheck.py
a06f44b5cf25184077fb081f32476e6a4c6ce54331417708cf281a800115f172  extractor/extract.py
18db4e0d3beaf0759f5741e80e1cb4230cf8c06edfdecfc667f228fbdba3689d  extractor/map.py
f2b5813ccc52c1e2a3d295fbbd91a7d254abcf26ad0f12a0b442374b147a3ca4  extractor/nc-run.sh
058e51cdf0384da8e4f1d958f115a5beac080c453fc796c1849921a00022993a  extractor/surface.json
8ac20e0ca17ee28bff02fb3e82061c2cbb6733e4a9d52472a69b3347d7165b41  extractor/surface.txt
96be1774362d9a8120281a76e380c0493bdf9b8eb2371ad5765ca0b027b18d57  LEDGER.md
d4fc8010074f84b88d9b8fc17606c10d9228a041fad36a7b4194e9a40153a784  REFLECTION.md
```
