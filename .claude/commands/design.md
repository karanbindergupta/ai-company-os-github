---
description: Design the experience and the design system
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS**

```bash
python3 scripts/company.py phase-start design
```

`creative-lead` sets direction and owns the design system. Then dispatch `designer` agents in
parallel for UX research, flows, UI, interaction, content and accessibility.

```bash
python3 scripts/company.py gate gate_design pass|fail by=creative-director
```
The gate fails if error/empty/loading states are missing, if any value bypasses the design tokens,
or if WCAG 2.2 AA is not met.
