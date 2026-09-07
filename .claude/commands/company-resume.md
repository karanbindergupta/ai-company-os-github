---
description: Resume an interrupted run exactly where it stopped
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

A run survives session limits, crashes and restarts. Recover it:

```bash
python3 scripts/company.py resume
python3 scripts/company.py validate
python3 scripts/company.py task-list status=in_progress
python3 scripts/company.py task-list status=blocked
```

`resume` is authoritative. It reports the next incomplete phase, its owner, exit criteria, and
which artifacts already exist on disk.

**Rules for resuming:**
- Never restart a completed phase. Completed phases are listed in `run.json`.
- Finish unfinished tasks in the current phase before starting the next.
- Re-read the artifacts that already exist rather than regenerating them.
- Read `.ai-company/incidents/` before retrying anything that previously failed — do not repeat a
  recorded failed approach.

Then dispatch the `orchestrator` to continue.
