# RESEARCH FRESHNESS

Old research silently becoming "what the company knows" is one of the most dangerous failure
modes available to an autonomous organization. Every research artifact carries a volatility class
and a retrieval date.

## Volatility classes

### HIGH — refresh aggressively (assume stale after ~30 days)
prices · news · regulations · APIs · software versions · competitor features · funding ·
financial information · platform and app-store policies · availability

**Never reuse a HIGH-volatility finding for a decision without re-checking it.** Re-verification
is usually one `WebFetch` to the primary source.

### MEDIUM — refresh periodically (assume stale after ~6 months)
market data · industry statistics · customer trends · technology trends · competitive positioning

### LOW — refresh when specifically challenged
historical facts · fundamental concepts · established principles · definitions

## Required frontmatter

```yaml
volatility: HIGH | MEDIUM | LOW
retrieved: 2026-09-07
refresh_after: 2026-10-07     # retrieved + class interval
```

## Before reusing any stored research

1. Read its `volatility` and `retrieved` date.
2. If past `refresh_after`, treat it as **UNVERIFIED**, not as fact.
3. Re-verify the load-bearing claims — not necessarily the whole report.
4. Update `retrieved` and note what changed. **If something changed, that is itself a finding**
   worth reporting.

## Decision-time rule

A decision at Level 3 or 4 may not rest on a HIGH-volatility claim older than 30 days. The
Research Auditor checks this and fails the audit if violated.

## Refresh is cheaper than re-research

Reports keep their sources and URLs precisely so refresh is a re-check, not a redo. That is why
`EVIDENCE-STANDARD.md` requires the URL and access date on every claim.
