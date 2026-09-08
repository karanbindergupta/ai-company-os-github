---
artifact: cross-engine-verification-test
role: research-director
phase: infrastructure-verification
status: complete
volatility: HIGH
retrieved: 2026-09-07
refresh_after: 2026-10-07
confidence: HIGH
---
# Cross-Engine Verification Test — Brave Search API pricing

## Why this question
It exercises the full architecture on a real, current, decision-relevant fact — and the founder
needs the answer anyway to decide whether to enable Brave.

**Depth: Level 2** (pricing decision). Engines available this session: native `WebSearch` +
`WebFetch` only — Exa, Brave and Tavily load at next session start or await credentials. Running
on the fallback path is exactly what Constitution §8 prescribes, and it tested the most important
mechanism in the whole system.

## Result: the secondary sources were wrong

### DISCOVERY — `WebSearch` (7 results, all TIER 2/3 aggregators)
Consensus across aggregator sites: **"$4 per 1,000 requests"**, "$0.003–$0.005 per query",
"free tier eliminated February 2026".

### PRIMARY SOURCE — `WebFetch` on https://brave.com/search/api/ (TIER 1)
| Plan | Price | Included | Rate limit |
|---|---|---|---|
| **Search** | **$5 per 1,000 requests** | $5 free credits/month | 50 queries/sec |
| **Answers** | **$4 per 1,000 requests** + $5 per million tokens | $5 free credits/month | 2 queries/sec |
| Enterprise | Not published — contact Brave | — | — |

### EVIDENCE CONFLICT — resolved
**SOURCE A** — aggregator sites [S-agg], TIER 2/3, 2026 — claim: Search API costs $4/1,000.
**SOURCE B** — brave.com/search/api/ [S-brave], TIER 1, retrieved 2026-09-07 — Search is
**$5**/1,000; **$4**/1,000 is the *Answers* plan.

**WHY THEY DIFFER:** the aggregators appear to have collapsed two distinct plans into one figure,
quoting the Answers price as the Search price. Several also repeat each other — likely **circular
sourcing** from a common origin rather than independent confirmation.

**MOST DEFENSIBLE CONCLUSION:** Brave Search API = **$5 per 1,000 requests** with $5 monthly
credit and a 50 qps limit. **CONFIDENCE: HIGH** (Tier 1, primary, retrieved today).

**The aggregator claim of "free tier eliminated" is UNVERIFIED** — the primary page shows $5
monthly credits rather than a free query allowance, which is consistent but not confirmation of
the timeline. Marked `INFERENCE`, not fact.

## What this proves about the architecture
| Mechanism | Verified |
|---|---|
| Discovery via search engine | Yes — 7 candidate sources surfaced |
| **Primary-source override** | **Yes — and it corrected a wrong consensus** |
| Source tiering | Yes — Tier 1 beat seven Tier 2/3 sources |
| Conflict detection and resolution | Yes — recorded, not averaged |
| Circular-sourcing detection | Yes — flagged repeated aggregator claims |
| Claim typing and confidence | Yes — FACT vs INFERENCE separated |
| Graceful degradation | Yes — full Level 2 completed with only fallback engines |

**This is the single most valuable result of the installation.** Seven sources agreed on a number
that the authoritative source contradicts. A company operating on search-result consensus would
have budgeted at 80% of the real Search API cost.

## Practical note for the founder
Brave now requires a credit card and bills usage with **no default spending cap**. Set a cap or
budget alert when enabling it.
