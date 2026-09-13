# Source-bound acceptance walkthrough

Pre-fix assessment (before editing production, 2026-09-12)
Base: 9eb2e6f6171845100b969e2d59e65b0d34ddf86f.
All quotations below were read from that base's files, not copied from audit narration.

AC-1 — RED (semantic walkthrough, not a command exit):
Old docs/compliance-provenance.md: “Its optional `provenance` block closes the remaining gap,
turning the manifest into a regulated audit record”; “AI-output disclosure (Art-50)” is mapped
to “`claim` + `provenance.model`”. The executable provenance probe passes the presence checker
with four fixture strings and no runtime logger or marked output. Deleting retention is the
positive control: the checker rejects incomplete change metadata. Thus accepting provenance
is useful evidence validation, but not operation-level conformance. Official Art 12 requires
system-event logging; Art 50(2) requires output marking for its scoped systems; Art 26(6) concerns
controlled runtime logs and retention. The old blanket 2 August 2026 date contradicts the
current Art 113(c) category dates, and Art 111(4) has a separate existing-system transition.

AC-2 — RED (semantic walkthrough, not a command exit):
Old docs/distribution.md: “the claim is checked by mechanism, outside the run that made it”.
Actual native hook execution permits Stop when no manifest is configured (exit 0), without
creating any off-worker verifier. TaskCompleted without evidence blocks (exit 2), retaining
useful local defense. runtime/scripts/run_report.py explicitly says it does not rerun verify.py
and its ledger remains worker-written; docs/verify-gate.md calls native hooks advisory.
Positive claims must identify deterministic structural/hash checks and coordinator-owned
execution separately from recorded worker evidence. Installing a plugin is not the latter.

AC-3 — RED (executable contract check exit 1 plus semantic walkthrough):
Old docs/runs/README.md oncall row requires a live incident/replayed postmortem and RESOLVED.
The real mission's terminal definitions are OPERABLE and OPERABLE-WITH-PARKED: the probe
extracts those declarations independently and rejects the row's nonexistent RESOLVED state.
Concrete false-positive scenario: an incident is resolved using old telemetry, without a
new question-to-signal map, test-fire receipt or instrumentation-removal control. Concrete
false-negative scenario: a healthy service lacks telemetry and needs operability work now,
without any live incident. Valid positive scenario: frozen path/questions, queried signals,
symptom alerts/runbooks and receipt, induced staging failure found by one fresh source-blind
worker, and a second fresh source-blind worker unable to locate it after instrumentation
removal. Existing telemetry that still locates it after removal cannot certify the change.

Coordinator accepted this walkthrough plan for built-for-review completion only. Meaning and
completeness require independent spec/standards review; validator replay is structural only.
No live incident, alert, external disclosure or blind-worker mission run was performed.

Post-fix assessment (same concrete scenarios, 2026-09-12)

AC-1 — GREEN (semantic walkthrough): the opening now calls provenance “supporting records,
not a regulatory conformance guarantee” and identifies presence checking, with truth and
operational compliance outside its scope. The fixture with accepted strings and no logger or
marking is now represented accurately. The field table still gives valid positive uses:
revision/content binding, declared scope and policy context, review attribution, and a retention
reference; the operational table separately calls for actual runtime logs, retention, marked
outputs and recipient-facing disclosures. Art 113(c)'s two category dates and Art 111(4)'s
transition agree with the fetched consolidated Act; the Commission FAQ corroborates the main
applicability dates. Determining a particular deployment's role/exceptions remains outside this
engineering mapping. Existing ProvenanceCheck tests remain 3/3 passing. This is no claim that
any actual system was tested for conformance.

AC-2 — GREEN (semantic walkthrough): four explicit authorities now distinguish “Deterministic
checks”, “Worker-attested records”, “Coordinator-owned reruns” and “Advisory native hooks”.
The same native-hook counterexample fits the corrected copy: installation alone performs no
coordinator rerun, while local checks retain their value. The worker ledger limitation agrees
with run_report.py; clean-environment test ownership agrees with evidence-manifest.md and
verify.py check_commands. The copy ties each benefit to its actual mechanism. Navigation tests
remain 19/19 passing; they test navigation/count references, not this semantic verdict.

AC-3 — GREEN (executable terminal-state contract check exit 0 plus semantic walkthrough):
The row now names OPERABLE/OPERABLE-WITH-PARKED and a bounded staging path/question set.
The added proof paragraph requires queried signals, symptom alerts/two severities/thresholds,
runbooks, destination receipts, and both fresh source-blind oracle runs, with removal RED.
The resolved-incident-only scenario is explicitly insufficient. A healthy service is eligible;
a positive proof requires the mission's evidence. A failure still identifiable after removal
is RED on the acceptance walkthrough: it cannot satisfy the paragraph's second oracle.
Missing prerequisites/evidence park the path instead of certifying it. Actual blind runs remain
future field-proof work; neither the prose nor this documentation check performs that mission.

Revert-control interpretation: restoring the three original docs restores all three semantic
counterexamples. The source-based oncall terminal check can replay that narrow mismatch; it does
not evaluate completeness of the blind-oracle prose. The coordinator-authorized validate.py
command is only a structural floor and cannot kill the inaccurate-prose control. A surviving
validator control must remain SURVIVED / semantic replay unsupported. No stronger semantic
verification is claimed; independent spec/standards review and GitHub approval remain pending.
