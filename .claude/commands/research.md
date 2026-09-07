---
description: Run the parallel research phase
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS** (omit to run the full sweep)

```bash
python3 scripts/company.py phase-start research
```

**Dispatch these as `researcher` agents in a single message so they run concurrently** — they are
independent of each other:

| Role pack | Artifact |
|---|---|
| `industry-researcher` | `.ai-company/research/industry.md` |
| `market-researcher` | `.ai-company/research/market.md` |
| `customer-researcher` | `.ai-company/research/customers.md` |
| `competitor-intelligence` | `.ai-company/research/competitors.md` |
| `trend-analyst` | `.ai-company/research/trends.md` |
| `feasibility-analyst` | `.ai-company/research/feasibility.md` |

Then dispatch `cro-research` to synthesize and hold the gate:
```bash
python3 scripts/company.py gate gate_research pass|fail by=cro-research note="..."
```

The gate fails on any unsourced material claim or fabricated statistic. **Failing this gate is
correct behaviour when the evidence is not there.**
