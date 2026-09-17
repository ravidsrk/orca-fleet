# Frozen contract — absorb-it self-test queue denominator

Denominator: the inbound open-PR queue of ravidsrk/orca-fleet (default branch
main), pinned base 6390743815f8f435181fa410cce374587128b30a.

T0 2026-09-16T10:00:41Z/10:00:44Z, open count 0 (routes: gh pr list limit 200;
REST pulls paginated per_page 100; gh search prs). T1
2026-09-16T10:00:54Z/10:00:55Z, open count 0. Most recent close before T0: PR
438, merged 2026-09-16T09:01:10Z.

- AQ-1: Full paginated enumeration of every open inbound PR at T0 is recorded with transcripts (no truncated listing).
- AQ-2: Re-enumeration confirms zero open inbound PRs outside a terminal class; PRs opened or closed since T0 are reconciled.
- AQ-3: Terminal verdict ABSORBED is recorded with a ledger; no absorb / receipt / land / close phases are owed on an empty queue.
