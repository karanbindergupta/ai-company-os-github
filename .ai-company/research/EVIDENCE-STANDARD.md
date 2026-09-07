# EVIDENCE STANDARD

## The evidence record

Every material claim is represented as:

```yaml
claim: "Competitor X charges $49/month for the Pro tier"
type: FACT                    # FACT | INFERENCE | HYPOTHESIS | ASSUMPTION | UNKNOWN
source: "X official pricing page"
source_type: TIER_1
source_url: "https://..."
date_published: 2026-08-01    # or "undated" - never guess
date_accessed: 2026-09-07
evidence: "Pricing table lists Pro at $49/mo billed monthly"
confidence: HIGH              # HIGH | MEDIUM | LOW | UNKNOWN
independent_confirmation: "Brave result [S12] shows same figure from an independent index"
contradicting_evidence: "none found"
```

Records live in `.ai-company/research/evidence/`. Reports cite them inline: `[E07]`.

## Confidence

| Level | Meaning |
|---|---|
| **HIGH** | Strong primary-source evidence, and/or independent confirmation from a separate index |
| **MEDIUM** | Good evidence, limited independent verification |
| **LOW** | Weak, indirect or incomplete evidence |
| **UNKNOWN** | Insufficient evidence to judge |

**For any Level 3 or 4 decision, LOW and UNKNOWN claims trigger additional research** before the
decision proceeds. If more research will not resolve it, the claim is escalated as a known
unknown — not quietly upgraded.

## What must never happen

- A number appearing in a report with no source
- A URL that was not actually retrieved
- A statistic reconstructed from memory
- A hypothesis losing its label as it moves between documents
- A Tier 3 anecdote becoming a percentage
- Confidence rising because a claim was repeated

## Confidence does not travel upward

If a conclusion rests on a MEDIUM claim, the conclusion is at most MEDIUM. Synthesis cannot
manufacture confidence by combining weak inputs. **State the weakest load-bearing link.**

## Reporting an absence

```
INSUFFICIENT EVIDENCE — searched Exa ("<query>"), Brave ("<query>"), and the official site.
No published figure found. Recommend treating as UNKNOWN rather than estimating.
```

That is a complete, professional answer. It is far more useful than an invented number.
