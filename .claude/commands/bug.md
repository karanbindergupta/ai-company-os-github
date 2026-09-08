---
description: Fix a defect properly
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Defect: **$ARGUMENTS**

1. **Reproduce it first.** A bug you cannot reproduce is not understood.
2. Write a **failing regression test** that captures it.
3. Find the root cause, not the symptom.
4. Fix it. The test goes green.
5. Independent review.
6. Regression pass — check the fix broke nothing else.

```bash
python3 scripts/company.py task-add title="Bug: $ARGUMENTS" owner=<role> criteria="regression test written and passing; root cause documented"
```
Record the root cause in `.ai-company/knowledge/lessons.md` if it reveals a systemic problem.
