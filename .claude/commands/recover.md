---
description: Recover company state after an interruption or crash
allowed-tools: Bash, Read, Grep, Glob, Task
---
```bash
python3 scripts/companydb.py recover
python3 scripts/companydb.py verify
python3 scripts/company.py resume
```
**Never restart a completed phase.** Finish in-progress tasks first. Read
`.ai-company/incidents/` before retrying anything that failed — governance rule 11 forbids
repeating a failed approach. The database is authoritative over anyone's recollection.
