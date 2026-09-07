# SOURCE HIERARCHY

Not all evidence is equal. Every source is tagged with its tier in the evidence record.

## TIER 1 — PRIMARY (highest authority)

Government bodies · regulators · official company websites · official documentation ·
official pricing pages · company filings · original datasets · academic papers ·
original announcements · first-party research.

**A Tier 1 source settles a question.** Prefer it over any number of Tier 2 summaries.

## TIER 2 — REPUTABLE SECONDARY

Established financial publications · respected industry publications · research organizations ·
established analysts · reputable specialist publications.

Good for context, synthesis and figures the primary source does not publish. **Always ask what
the Tier 2 source's own source was** — often it is a Tier 1 document you should read directly.

## TIER 3 — COMMUNITY

Reddit · forums · reviews · social media · community discussions.

**Genuinely valuable** — often the only honest source — for: customer pain, complaints, feature
requests, real-world experience, sentiment, and how a product actually behaves in practice.

**The trap:** isolated community posts are anecdotes, not statistics.

- Correct: "Multiple users on [forum] report X [S14][S15][S16] — INFERENCE: X is a recurring
  complaint. Frequency unquantified."
- Wrong: "Users find X frustrating" stated as an established fact from three posts.

Never convert a handful of posts into a percentage. Never present sentiment as measured.

## Circular sourcing

Three outlets republishing one press release is **one source**, not three. Trace each claim to its
origin before counting it as corroboration. Independent confirmation means an independently
produced source.

## Recency beats authority for volatile facts

A Tier 1 pricing page from two years ago loses to a Tier 2 article from last week **on price** —
and both lose to today's pricing page. Always record the publication date, not just the tier.

## Recording

```markdown
[S07] Title — Publisher — URL — published 2026-03-11 — retrieved 2026-09-07 — TIER 1
```
Kept in `.ai-company/research/sources/`.
