---
description: Run the security review
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS**

```bash
python3 scripts/company.py phase-start security
```

Dispatch `security-lead` across: threat model, appsec review, dependency audit, privacy
assessment, compliance check, and the defensive red-team pass.

```bash
npm audit 2>/dev/null || echo "no Node dependency manifest"
```
Use the `claude-security` plugin for deep scanning.

```bash
python3 scripts/company.py gate gate_security pass|fail by=ciso
```
**The CISO's veto is not overridable.** No release with an unresolved critical or high finding.
Only the founder may accept a security risk, and that acceptance is recorded against their name.

Red-teaming is defensive, against this product only, non-production only, never DoS.
