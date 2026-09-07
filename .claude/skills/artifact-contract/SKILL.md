---
name: artifact-contract
description: How agents communicate in this company - through files, never conversation. Load before producing any departmental artifact. Defines the required frontmatter, status values, and what a caller receives back.
---

# The artifact contract

Agents in this company communicate by **writing files**. Your caller sees a short summary; the
work must be on disk or it did not happen. This is what makes work parallelizable, auditable and
survivable across session limits.

## Every artifact carries frontmatter
```yaml
---
artifact: market-analysis
role: market-researcher
phase: research
status: complete | partial | blocked
confidence: high | medium | low
depends_on: [industry-analysis]
blocked_on: ""          # required when status is blocked or partial
updated: 2026-09-07
---
```

## Status means something
- `complete` — the role's stated output exists and meets its quality standards
- `partial` — real work was done but something is missing; `blocked_on` says what
- `blocked` — could not proceed; `blocked_on` names the blocker

**Never mark `complete` to look finished.** The phase engine and the auditors check.

## Structure for the reader
Each artifact begins with a **Summary** (5 lines maximum) that a downstream agent can read without
the rest. Then findings, then evidence. Downstream agents read your summary, not your whole file -
front-load the conclusion.

## What you return to your caller
At most ~15 lines:
1. What you produced and its path
2. Your top conclusions
3. What is unresolved or blocked
4. What you recommend happens next

**Do not paste the artifact into your response.** That defeats context isolation, which is the
entire reason you run in a separate window.

## Never write outside your lane
Write only to the paths your role pack names. Two roles writing the same file is a defect - if you
need something in another department's artifact, ask the orchestrator to dispatch that role.
