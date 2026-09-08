---
description: Identify a capability gap and hire a role for it
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Gap: **$ARGUMENTS**

```bash
python3 scripts/company.py task-list status=failed
cat .ai-company/audits/organization.md 2>/dev/null
```

Dispatch `hr-lead`:
1. **Chief People Officer** — is the gap real, and not already covered? Prefer revising an
   existing role over adding one.
2. **Role Researcher** — research the actual profession, with sources.
3. **Role Author** — write the pack via `scripts/_rolegen.py`, register it in `roles.json`.
4. **Onboarding Specialist** — test it against a real task.

```bash
python3 scripts/company.py validate
```
**Never create a new `.claude/agents/` subagent** — that needs founder approval because it costs
orchestrator context permanently. Role packs are free; subagents are not.
