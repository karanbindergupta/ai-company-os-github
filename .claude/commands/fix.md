---
description: Run remediation on open findings, then retest
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS** (omit for all open findings)

```bash
python3 scripts/company.py phase-start remediate
python3 scripts/company.py task-list status=todo phase=remediate
python3 scripts/company.py ready
```

For each finding: fix → independent review → retest. Not "fix and declare done".

A finding is closed only when it is **fixed and verified**, or formally **accepted as a risk** with
an owner and founder sign-off where required.

```bash
python3 scripts/company.py phase-start retest
python3 scripts/company.py gate gate_qa pass|fail by=qa-lead
```
Retest must check for **new** regressions introduced by the fixes, not just the original findings.
