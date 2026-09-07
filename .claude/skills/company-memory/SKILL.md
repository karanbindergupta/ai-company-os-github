---
name: company-memory
description: How organizational memory works and why it must be written down. Load at phase boundaries, after decisions, and after failures. Runs get interrupted by session limits - anything unwritten is genuinely lost.
---

# Company memory

This company runs across sessions. A session limit can end mid-phase. Everything not on disk at
that moment is gone permanently - there is no recollection to fall back on.

## What must be persisted
| Kind | Where |
|---|---|
| Mission and charter | `.ai-company/mission/` |
| Validated facts, with sources | `.ai-company/research/` |
| Assumptions, marked as assumptions | `.ai-company/product/assumptions.md` |
| Decisions **and rejected alternatives** | `.ai-company/decisions/` |
| Architecture decisions | `.ai-company/architecture/decisions/` |
| Risks, owners, acceptances | `.ai-company/risks/register.md` |
| Failures and what was tried | `.ai-company/incidents/` |
| Lessons learned | `.ai-company/knowledge/lessons.md` |
| Unresolved questions | `.ai-company/knowledge/open-questions.md` |
| Run state | `.ai-company/state/run.json` (written automatically at every transition) |

## Rejected alternatives are the highest-value memory
They are what stops the company spending three phases relitigating a settled question. Always
record what was considered and why it lost.

## Index, do not duplicate
Departments own their artifacts. `.ai-company/knowledge/INDEX.md` points at them. Copying content
creates two sources of truth that silently diverge.

## Give agents what they need, not everything
Never load the whole memory into an agent. Its role pack names its inputs - pass those. Context is
the scarcest resource in this organization.

## On resume
```bash
python3 scripts/company.py resume
```
Read existing artifacts rather than regenerating them. Read `.ai-company/incidents/` before
retrying anything. Never restart a completed phase.
