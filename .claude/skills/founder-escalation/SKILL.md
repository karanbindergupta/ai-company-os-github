---
name: founder-escalation
description: How to escalate to the founder. Load before any escalation. Defines what genuinely warrants their attention and the decision-package format that replaces dumping raw research on them.
---

# Founder escalation

The founder is the final authority, not a task queue. Most escalations are the company failing to
decide something it was equipped to decide.

## Escalate only for
- Mission or strategy change; a pivot away from their idea
- Spend, pricing, or legal commitment
- **Irreversible or outward-facing actions** — deploys, publishing, sending, purchasing, posting
- A security risk being accepted rather than fixed
- A genuine deadlock the CEO cannot resolve on evidence
- Anything requiring a credential or an account

## Never escalate
- "What should I do next?" — decide
- A choice between options with a clear evidential winner
- Anything a role pack already gives you authority over
- Routine progress updates

## The decision package
```markdown
## Decision required
## Recommendation          — lead with this, always
## Why                     — the reasoning, briefly
## Evidence                — with sources
## Alternatives considered — and why each is worse
## Tradeoffs               — what is given up
## Risks                   — including if the recommendation is followed
## Expected outcome
## What approval is required — precisely what you need them to say yes to
```

```bash
python3 scripts/company.py escalate subject="..." recommendation="..." risks="..."
```

## Rules
- **Recommend.** An escalation without a recommendation is abdication.
- **Never dump raw research.** Synthesize.
- One page. If it needs more, link the artifact.
- Say plainly what happens if they do nothing.
- **Never ask for a credential, token or password.** Tell them where it goes; they put it there.
