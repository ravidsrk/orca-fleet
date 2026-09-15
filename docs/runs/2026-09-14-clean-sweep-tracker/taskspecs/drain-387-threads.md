You are the clean-sweep THREAD-DRAIN worker for PR #387 (methodology pack: matt —
read $HOME/.agents/skills/tdd/SKILL.md and follow its verify-first spirit; load no
other pack). Fresh terminal in the MAIN checkout on BASE
(review/2026-09-14-holistic-fixes @f7d1081 or later — verify with git log; do NOT
checkout anything else). READ-ONLY on the repo: commit NOTHING (verify with git
log that no commit carries your session, say so in worker_done). rw by lane: gh
reads (ALL fenced via guard_text.py --source pr --fetch <gh ...>; non-zero = NO
data) + gh reply/resolve posts (each receipted FIRST: egress.py write --sink
pr-comment --host github.com --payload-class thread-reply|thread-resolve --consent
run-2026-09-14-clean-sweep:tracker-writes).

CONTEXT: PR #387 is the holistic review-base PR. Wave 1 (T1-T6) and wave 2
(T7 #400 U393 7630815 merged 6d9e46a; T9 #402 U387G 318542b merged a769a64e;
T8 #403 U387P 19be7a1 merged b9b71df6; T10 #401 U387W 0d55f10 merged bff42ff1)
are all merged. 6 replies were posted at takeover; wire_docs already resolved.
22 Greptile threads are UNRESOLVED now (verified by the coordinator via
GraphQL). Your job: drain every one to replied+resolved, or park it with a
precise reason. FIX NO CODE — this is a reply+resolve round only.

THE 22 THREADS (comment id, path:line — read each body fenced first):
DOCS (frozen run records — specs are point-in-time instructions for CLOSED
units, manifests are evidence, gate-batch is the human park; verify each claim
against BASE before replying, never assume):
4008046401 integrate-388.md:25 · 4008218867 fix-385-r2.md:48 · 4008414640
review-385r2-spec.md:24 · 4008842923 review-388-spec.md:7 · 4009130325
fix-388-r2.md:56 · 4010139829 fix-364-r1.md:60 · 4012317538 integrate-387w.md:34
· 4012606285 u393-manifest.json:8 · 4012708598 gate-batch.md:22 (G2 branch
protection — HUMAN ask, park lives in gate-batch.md) · 4012849332
u387g-manifest.json:8 · 4013413615 verdict-387w-r3.md:48 · 4013413622
u387p-manifest.json:8 · 4013474629 fix-387w-r4.md:66 · 4014047033
fix-387w-r5.md:84 · 4014275315 review-387wr5-spec.md:24 · 4014424185
fix-387w-r6.md:57 · 4015125022 review-387wr7-standards.md:7.
CODE (verify against the MERGED code at BASE, not the PR diff):
4009895678 run_report.py:489 (T10 finding — fixed by U387W, merged bff42ff1;
reply cites the fix + merge, then resolve) · 4012510839 evidence-run.py:138
(T7's file: legacy-wrapper first-append race; T7 shipped opportunistic
flock + mixed-version test in 6d9e46a — verify whether the exact claimed
shape is covered, refuted, or NEW-REAL) · 4012783264 scripts/eval.py:965
(T9's file: env/virtualenv denylist vs legit first-party dirs — check T9's
survey/decision, then disposition) · 4012783267 scripts/eval.py:975 (T9's
file: glob-then-filter perf — needs a timeout/evidence check, else accept
with reason) · 4015351682 run_report.py:558 (nested ### Deviations — the
r7 TEST axis already adjudicated this EXACT shape as Nit T7-1, accepted,
non-blocking; reply cites the r7 adjudication + GO 5209642813, then resolve).

DISPOSITION RULES (per thread, recorded in worker_done):
- FIXED: cite the fix commit + merge SHA + PR; reply, resolve.
- SUPERSEDED/STALE/HISTORICAL: cite what overtook it (later round, merged
  unit, frozen record); reply, resolve.
- FALSE-POSITIVE: reproduce-or-refute with CONCRETE evidence (a command you
  ran, a line you read, an oracle result) — never bare assertion; reply,
  resolve.
- HUMAN-PARK: the ask lives in gate-batch.md (cite the item); reply saying
  so, resolve (the gate batch is the durable park, not the thread).
- NEW-REAL: a live defect in merged code with a repro you ran. Do NOT fix.
  Do NOT reply yet. PARK with: exact file:line, minimal repro, oracle
  evidence, and which criterion/unit it escapes. The coordinator specs it.
- UNVERIFIABLE: after genuine attempts, park with what you tried and what
  would settle it. Never fake a disposition.

RESOLVE MECHANISM: GraphQL resolveReviewThread (gh api graphql -F
threadId=<full PRRT id> -f query='mutation($threadId:ID!){
resolveReviewThread(input:{threadId:$threadId}){thread{isResolved}}}').
Get full thread ids from the reviewThreads query (first 60, match by
comment databaseId). Reply FIRST (REST
/pulls/387/comments/<id>/replies), verify the reply id, THEN resolve,
then verify isResolved=true. Receipt per send (reply AND resolve are
separate sends).

worker_done: per-thread table (id → disposition + reply id + resolved?)
+ NEW-REAL/UNVERIFIABLE parks with full detail. Omit --to. Preamble
--from + --dispatch-capability on every send; consumer_fenced = stop.
STOP: over 75 min (report partial per-thread status — done vs to-do by
id); any gh write fails twice; anything asks for code changes. No
sub-dispatch. Comment current.
