# Compliance provenance — mapping the evidence manifest to EU AI Act Art-12/50

The [evidence manifest](../runtime/evidence-manifest.md) already records most of what the EU AI Act's
transparency + logging obligations expect of a change to a high-risk AI system. Its optional
`provenance` block closes the remaining gap, turning the manifest into a regulated audit record.

> Not legal advice. A dated mapping (2026-08-28) to inform an `attest-it`-style conformance run;
> the authoritative text is the Act and the Commission's guidance.

## Why this exists

EU AI Act **Article 12** (automatic, tamper-evident event logging for high-risk systems),
**Article 26(6)** (deployer log retention ≥ 6 months), and **Article 50** (AI-output transparency /
machine-readable marking) became enforceable **2 Aug 2026**. Guidance expects per-change provenance:
governing spec/policy version, model lineage, reviewer identity + timestamp, test outcomes,
security-scan results, and immutable/append-only storage. That is structurally the manifest.

## Field mapping

| Regulatory expectation | Manifest field | Notes |
|---|---|---|
| Immutable event record of the change | `base_sha` → `head_sha`, `commands[]` (+ exit codes, artifacts), run-close **sha256 inventory** | git + the integrity inventory are the tamper-evident log |
| What was required (scope, frozen) | `contract.source` @ `contract.digest`, `criterion_ids`, `criteria[]` | the denominator can't be shrunk (§1/§2) |
| Independent verification that it holds | §2 independent verifier (re-derive from git, clean-env test, negative control) | "verified, not asserted" |
| Governing spec / policy version | `provenance.spec_version` | e.g. `security-policy@v3` |
| Model lineage | `provenance.model` | implementing model + version |
| Reviewer identity + timestamp | `provenance.reviewer`, `pr.reviewed_sha`, `reviewer_mode` | who reviewed, at which SHA, how independent |
| Retention / immutability | `provenance.retention` | pointer to the append-only store meeting Art-26(6) |
| Which standard is being attested | `provenance.standard` | `EU-AI-Act-Art-12` \| `SOC2` \| `SSDF` \| `none` |
| AI-output disclosure (Art-50) | `claim` + `provenance.model` | marks the change as agent-produced |

## Gaps a full conformance run still owns

- **Retention infrastructure** (the append-only store itself) is deployment-specific — the manifest
  points at it; it does not provide it.
- **Per-obligation coverage** across a whole standard is the job of the proposed `attest-it` mission
  (#84): one unit per obligation from a frozen `standard@version` catalog, each independently
  re-derived, `CONFORMANT` / `CONFORMANT-WITH-GAPS`.

## Sources (accessed 2026-08-28)

- EU transparency-obligations guidance — <https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems>
- Commission, "safer and more transparent AI" (2 Aug 2026) — <https://commission.europa.eu/news-and-media/news/safer-and-more-transparent-ai-2026-08-02_en>
