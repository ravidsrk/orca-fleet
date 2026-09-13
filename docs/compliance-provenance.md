# Compliance provenance — supporting evidence for AI-system changes

The [evidence manifest](../runtime/evidence-manifest.md) records change scope, revisions,
commands and review references. Its optional `provenance` block adds context for an audit;
these are supporting records, not a regulatory conformance guarantee. The verifier checks
that required provenance strings are present when a standard is named. It does not validate
their truth or establish that the operating AI system meets that standard.

## Applicability checked 2026-09-12

Determine the system's scope, operator role, risk category and exceptions before selecting
obligations. Under Article 113(c), Chapter III Sections 1–3 (except Article 6(5)) apply from
**2 December 2027** for Article 6(2)/Annex III systems and **2 August 2028** for Article 6(1)/Annex I
systems. Articles 12 and 26 fall within those sections; Article 111 adds existing-system
transitions. [Consolidated AI Act, Articles 111 and 113](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng).

Article 50 generally applies from **2 August 2026**, with obligation-specific exceptions.
Article 111(4) gives providers of covered synthetic-content systems placed on the market before
that date until **2 December 2026** to comply with Article 50(2).
[Consolidated AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng);
[Commission applicability FAQ](https://digital-strategy.ec.europa.eu/en/faqs/navigating-ai-act).

## What the manifest can support

| Change evidence | Field | Limit |
|---|---|---|
| Revision and recorded checks | `base_sha`, `head_sha`, `commands[]`, artifact hashes | Hashes bind retained bytes; the coordinator still owns clean-environment reruns |
| Frozen acceptance scope | `contract.source`, `contract.digest`, `criteria[]` | Scope completeness needs comparison with the authoritative contract |
| Governing policy and implementing model | `provenance.spec_version`, `provenance.model` | Declared context; a model name does not characterize the deployed AI system |
| Review attribution | `provenance.reviewer`, `pr.reviewed_sha`, `reviewer_mode` | Review identity and SHA require independent verification |
| Retention reference | `provenance.retention` | A pointer does not provide storage, retention enforcement or access controls |
| Intended assessment | `provenance.standard` | Naming `EU-AI-Act-Art-12`, `SOC2` or `SSDF` does not establish conformance |

## Obligations for the operating AI system need separate evidence

| Scoped obligation | Evidence the change manifest does not supply |
|---|---|
| Article 12: automatic lifetime event logging for high-risk systems | Runtime logging capability and operational records |
| Article 26(6): deployers retain controlled system logs appropriately, at least six months unless applicable law provides otherwise | Actual retained logs and retention enforcement |
| Article 50(2): providers mark covered synthetic outputs in machine-readable form | Output marking and detectability checks; `claim` and `provenance.model` do not mark outputs |
| Article 50(1), (3)–(5): applicable interaction/content disclosures | Recipient-facing disclosures at interaction or exposure, subject to the specified exceptions |

These obligations concern the operating system and its outputs, independently of build records.
[Consolidated AI Act, Articles 12, 26 and 50](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng).
A full [attest-it](missions/attest-it.md) run must freeze the applicable obligations and obtain
separate evidence for each; missing capability or evidence remains an explicit gap. This mapping
is an engineering evidence aid, not an assessment of a particular deployment's legal compliance.
