---
description: Open, drive or resolve an incident
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---
Incident: **$ARGUMENTS**

Detection → triage → severity → owner → diagnosis → containment → fix → verification → recovery →
postmortem → preventive action.
```bash
python3 scripts/companydb.py incident open title="..." severity=critical owner=<role> detection="..."
python3 scripts/companydb.py incident resolve id=INC-001 postmortem="..." preventive_action="..."
```
**A postmortem is blameless and produces a concrete preventive action** — otherwise it is a story,
not a fix. `resolve` refuses without both. Record the lesson in `.ai-company/knowledge/lessons.md`.
