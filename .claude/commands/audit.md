---
description: Run the independent audits and the adversarial review
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

```bash
python3 scripts/company.py phase-start audit
```

Dispatch `auditor` **in parallel** for: product audit, creative audit, architecture audit, and
organization audit. Then run the adversarial pass.

**Auditors must be independent of the work they audit.** Never let a role audit its own output.

Every finding becomes a remediation task with severity and an owner — an audit that produces a
list of concerns has failed.

```bash
python3 scripts/company.py gate gate_audit pass|fail by=cro-risk
```
