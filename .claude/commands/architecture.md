---
description: Design the architecture and choose the stack
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS**

```bash
python3 scripts/company.py phase-start architecture
```

Dispatch `architect` (principal, then systems/database/API as needed) and `security-lead` as
`security-architect` — the security review happens **before** the design is accepted, not after.

Outputs: `.ai-company/architecture/architecture.md`, `decisions/` (ADRs), `data-model.md`,
`api-spec.md`, and `.ai-company/security/architecture.md`.

```bash
python3 scripts/company.py gate gate_architecture pass|fail by=cto
```
The gate fails if a stack choice has no requirement behind it, if ADRs are missing, or if the
design is more complex than the requirements justify. **Over-engineering fails this gate.**
