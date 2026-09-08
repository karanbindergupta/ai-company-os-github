---
description: Run the QA phase
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS**

```bash
python3 scripts/company.py phase-start qa
```

Dispatch `qa-lead` for strategy, then `tester` role packs **in parallel** — functional, e2e,
regression, performance, accessibility. They are independent.

Use the Claude Browser stack for e2e. **Do not install Playwright.**

```bash
python3 scripts/company.py gate gate_qa pass|fail by=qa-lead
```
Every result records what was run and what was observed. The gate does not pass with open critical
or high defects, whatever the schedule says.
