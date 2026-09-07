---
name: evidence-standard
description: How this company handles evidence, sources and confidence. Load before ANY research, market sizing, competitive analysis, financial modelling or claim-making task. Defines what counts as a source, how to state confidence, and the prohibition on fabrication.
---

# The evidence standard

The single most damaging thing an AI organization can do is produce confident, well-formatted,
invented facts. Everything downstream inherits the error and nobody can tell.

## Absolute prohibitions
- **Never invent a statistic.** No market sizes, growth rates, CACs, conversion rates or
  benchmarks that you did not find.
- **Never invent a citation, URL, report title, or author.**
- **Never attribute a quotation to anyone unless you retrieved it.**
- **Never name a competitor, product or company you did not verify exists.**

If you cannot find it: write `unknown`, say what you searched for, and move on. An honest gap is
infinitely more useful than a plausible fabrication.

## What counts as a source
| Strength | Example |
|---|---|
| Strong | Primary data, regulatory filings, official statistics, the company's own documentation |
| Moderate | Reputable industry analysis, peer-reviewed work, established trade press |
| Weak | Vendor marketing about its own market, undated blog posts, content-farm listicles |
| Not a source | Your own prior output, a search snippet you did not open, "commonly known" |

Read the actual page with `WebFetch`. A search snippet is a lead, not evidence.

## Recording sources
Save to `.ai-company/research/sources/` and cite inline:
> Market grew 14% in 2025 [S12]

```markdown
[S12] Title — publisher — URL — retrieved 2026-09-07 — strength: moderate
```

## Confidence, stated every time
- **High** — multiple independent strong sources agree
- **Medium** — one strong source, or several moderate ones
- **Low** — weak sources, or inference from adjacent data

## Inference must be labelled
Write "inferred from X" or "assumption:". Never present reasoning as a finding.

## Contradictions are findings
When sources disagree, report the disagreement. Do not pick the convenient one.

## Triangulate anything load-bearing
If a number drives a decision, find it twice from independent sources. Say so if you could not.
