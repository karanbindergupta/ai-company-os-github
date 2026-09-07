---
description: Produce the Master Brief
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

```bash
python3 scripts/company.py phase-start brief
```

The `ceo` assembles `.ai-company/briefs/MASTER-BRIEF.md` from work already done. **Do not
re-research** — synthesize the artifacts that exist. Every section cites its source artifact.

Required sections: Executive Summary · Problem Definition · Customer Definition · Jobs To Be Done ·
Market Analysis · Competitive Analysis · Differentiation · Business Model · Revenue Model ·
Pricing · Unit Economics · Go-To-Market · Brand Strategy · Product Strategy · Feature Architecture ·
Functional Requirements · Non-Functional Requirements · UX Strategy · UI Strategy · Design System ·
Information Architecture · Technical Architecture · Database Architecture · API Architecture ·
Infrastructure · Security · Privacy · Compliance · Analytics · Testing · Performance ·
Accessibility · Roadmap · Risks · Assumptions · Acceptance Criteria · Launch Strategy ·
Post-Launch Strategy

Then dispatch **CTO, CPO, CISO, CFO and Creative Director** in parallel to review it. Each returns
approve or reject-with-reason.

```bash
python3 scripts/company.py gate gate_brief pass|fail by=ceo
```
**No section may be left as TODO.** A section with nothing behind it means the work was not done.
