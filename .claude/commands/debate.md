---
description: Convene the executive debate on an open question
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Question: **$ARGUMENTS**

```bash
python3 scripts/company.py phase-start debate
```

1. **Dispatch each relevant executive in parallel** as `executive` agents — CFO, CTO, CPO, CMO,
   CISO, CSO, CRO, Creative Director. Each writes an independent position paper to
   `.ai-company/decisions/positions/<slug>.md` with assumptions, evidence, alternatives, risks,
   tradeoffs, expected outcome, and what would change their mind.

   Do not let them see each other's positions first. Independent views, then reconciliation.

2. **Dispatch `ceo`** to rule. The ruling records the dissent verbatim and names which argument
   lost and why.

```bash
python3 scripts/company.py gate gate_debate pass by=ceo
```

**A debate where everyone agreed was not a debate.** If positions converged suspiciously, send it
back and ask each executive what would have to be true for them to be wrong.
