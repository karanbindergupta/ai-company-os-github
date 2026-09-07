---
description: Executive review and the founder decision package
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

```bash
python3 scripts/company.py phase-start exec_review
python3 scripts/company.py status
```

Executives sign off in parallel. Then the `ceo` prepares
`.ai-company/decisions/founder/release-package.md`:

**Decision · Recommendation · Why · Evidence · Alternatives · Tradeoffs · Risks · Expected
outcome · What approval is required**

Present the recommendation. **Never dump raw research on the founder.**
```bash
python3 scripts/company.py gate gate_exec pass by=ceo
```
