# Current scope and claim audit

The effective inventory is [claim-current.json](claim-current.json), with explicit additive changes and retractions in [claim-corrections.json](claim-corrections.json). The [correction report](INVENTORY-CORRECTION.md) gives exact IDs, source refutations and receipt limits. This is an inventory correction, with full runtime pinning and AC-1 still unfinished.

Corrigendum: **309 original records = 134 proposed exclusions + 175 mechanics parents → 429 original children**. The former wording “309 mechanics-bearing parent records” was wrong. The original report is retained [byte-for-byte](history/e2e7adab/CLAIM-AUDIT.md), and the separate [snapshot](history/snapshot/CLAIM-AUDIT.md) is also preserved.

The additive correction retains all 309 original IDs, restores mechanics in four mixed exclusions, appends C310–C316 and 52 children, and explicitly corrects 22 existing children. Current accounting: **316 parents = 130 whole exclusions + 186 mechanics parents → 481 child records**; **104 narrow witnesses, 4 historical patched children, 350 TODO and 23 PARTIAL-TODO**. The 373 unfinished children remain in [CONTINUATION.md](CONTINUATION.md). Counts include conjunctions and duplicate source predicates; they are not counts of independent experiments or successful source exclusions.

Historical [claim-atomization.json](claim-atomization.json) remains unchanged for byte preservation. Its old witness labels are superseded where named by the correction companion; consuming that file alone does not give the current state. The six withdrawn witness labels are C040.03, C066.01, C096.02, C169.01, C232.01 and C235.01. C183.02 is retained only as an unsupported fixture hypothesis, with unqualified source doctrine in C183.03.
