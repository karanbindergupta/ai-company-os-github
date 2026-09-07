---
description: Show company status, or run the orchestrator on the current mission
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Run the state engine first, then act on what it says.

```bash
python3 scripts/company.py status
```

Then:
- **If no run exists** — tell the founder to start one with `/company-start`, and show them the
  format. Do not invent a mission.
- **If a run is active** — report status concisely: phase, gates, blocked and failed tasks, and
  anything awaiting founder decision. Then ask whether to continue, or continue directly if
  `$ARGUMENTS` says so.
- **If work is awaiting the founder** — present those decision packages first. They are blocking.

Keep the report short. The founder wants to know where things stand and what needs them, not a
transcript of everything that happened.
