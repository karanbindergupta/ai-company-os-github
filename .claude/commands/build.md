---
description: Plan and execute parallel engineering
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS**

```bash
python3 scripts/company.py phase-start plan
```

1. `ops-lead` builds the task graph — owner, criteria, dependencies, parallel groups.
2. ```bash
   python3 scripts/company.py validate && python3 scripts/company.py ready
   ```
3. `gate_plan` passes only when the graph is acyclic and every task is fully specified.
4. `phase-start build`, then **dispatch each parallel group in a single message** so they run
   concurrently. Use `EnterWorktree` for isolation when workstreams touch the same files.
5. Every change gets an **independent** review before integration — never self-review.

Backend and frontend parallelize **only after the API contract is agreed**. Dispatching them
before that produces work that has to be redone.
