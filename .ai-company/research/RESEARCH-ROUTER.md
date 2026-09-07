# RESEARCH ROUTER

The Research Director routes each question to the cheapest engine that can answer it well.

> **Do not send every question to all three engines.** That is expensive, slow, and produces
> three versions of the same answer rather than corroboration.

## Live status (verified 2026-09-07)

| Engine | Status | Access | Limits |
|---|---|---|---|
| **Exa** | **WORKING** | Anonymous tier — no key | ~3 QPS, ~150 calls/day. OAuth or an API key raises this |
| **Tavily** | **WORKING** | Keyless — no key | Capped keyless quota; `tvly auth` raises it |
| **Brave** | Configured, dormant | Needs `BRAVE_API_KEY` | Deferred by founder decision |
| **WebSearch / WebFetch** | **WORKING** | Native | None |

Two independent engines plus the native pair are live, so cross-engine verification works today
**without any credential**. Brave would add a third independent index; until then, use Exa and
Tavily as the two independent checks, and note in reports that Brave was unavailable.

## Engine selection

### EXA — deep and semantic
**Prefer for:** deep research · semantic discovery · technical questions · code research · finding
relevant people and companies · competitor intelligence · academic research · difficult multi-step
questions · high-signal source discovery.

Exa's strength is finding the *right* source rather than many sources. Reach for it when the
question is "who is doing X well" or "what is the authoritative source on Y".

### BRAVE — independent and current
**Prefer for:** broad current web search · news · **independent verification of an Exa finding** ·
alternative sources · freshness-sensitive information · second opinions · broad market discovery.

Brave runs its **own web index**, which is the point: it is the company's independence check. When
a claim matters, confirming it through a different index is real corroboration.

### TAVILY — extraction and crawling
**Prefer for:** crawling a site · extracting page content · multi-page research · structured
research · investigating one website thoroughly · collecting information across many pages ·
filling gaps another engine left.

Tavily is not a third search button. Use it when the task is **"read this site properly"** rather
than "find me a site". Note: keyless access covers search and extract; **map, crawl and research
require authentication**.

### Native fallback — always available
`WebSearch` and `WebFetch` are built in, verified working, and need no credentials. They are the
**guaranteed floor**: if Exa, Brave or Tavily is unavailable, unconfigured or failing, research
continues here rather than stopping. `WebFetch` is also the simplest route to a primary source
once you have its URL.

## Routing by question shape

| The question is... | Route |
|---|---|
| "What is the current price of X?" | Primary source directly (`WebFetch` the pricing page). Engine only to find the URL |
| "Who competes in X?" | Exa (discovery) → Brave (independent check) → Tavily/WebFetch (their sites) |
| "Is this claim still true?" | Brave (freshness) → primary source |
| "What does this API support?" | Official docs via `WebFetch`. Never a blog |
| "What do users complain about?" | Brave/Exa into community sources — Tier 3, weight accordingly |
| "Everything about this one company" | Tavily crawl/extract on their site + Exa for third-party signal |
| "What is the regulation?" | Regulator's own site. **Nothing else is authoritative** |
| Conceptual or definitional | Level 0 — no engine needed |

## Depth to engine mapping

| Level | Engines |
|---|---|
| 0 | None |
| 1 | One engine, or `WebFetch` straight to a known primary source |
| 2 | One engine + primary sources + at least one corroborating source |
| 3 | Exa + Brave (independent) + Tavily where extraction helps + primary sources + audit |
| 4 | Level 3 + mandatory independent auditor + explicit confidence assessment per claim |

## Parallel decomposition

For Level 3+, decompose before dispatching. Independent tracks run **in one message** so they run
concurrently:

```
MASTER QUESTION
  ├── Market          ├── Competitor      ├── Customer
  ├── Pricing         ├── Regulatory      ├── Technology
  ├── Financial       ├── Distribution    └── Risk
```

Tracks are independent when neither consumes the other's output. **Regulatory research often
gates everything else** — if legality is in question, run it first and alone.

## Cost discipline

- A simple question gets a simple answer. Do not run Level 3 to look thorough.
- Do not re-research what `.ai-company/research/` already holds and is still fresh — check
  `RESEARCH-FRESHNESS.md` first.
- Prefer one good primary source over five secondary summaries of it.
- Stop when the answer is established. Additional confirming sources have diminishing value.
