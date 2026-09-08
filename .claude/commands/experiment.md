---
description: Design, run or record the result of an experiment
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---
Experiment: **$ARGUMENTS**

Set the success threshold **before** running — a threshold chosen afterwards is a rationalization.
```bash
python3 scripts/companydb.py experiment add hypothesis="..." metric="..." threshold="..." owner=<role>
python3 scripts/companydb.py experiment result id=EXP-001 result="..." learning="..."
python3 scripts/companydb.py experiment list
```
**Record failed experiments.** A failure that is written down is company knowledge; one that is
not is a failure the company will repeat. Link the learning to any decision it informed:
`companydb.py link src_type=experiment src=EXP-001 relation=informed dst_type=decision dst=DEC-00X`
