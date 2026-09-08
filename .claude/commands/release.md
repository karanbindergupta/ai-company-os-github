---
description: Verify every gate and prepare the release
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

```bash
python3 scripts/company.py phase-start deliver
python3 scripts/company.py status
```

`release-manager` verifies **every** gate is green **with evidence on disk**. Not a promise that a
gate will pass — evidence.

Checklist: `.ai-company/qa/release-checklist.md`. Rollback plan required and tested.

```bash
python3 scripts/company.py escalate subject="Release authorization" recommendation="..." risks="..."
```

**The founder authorizes every release. Always.** Then, and only then:
```bash
python3 scripts/company.py gate gate_release pass by=release-manager founder_approval="<what they approved>"
```
The engine refuses this gate without the founder approval field. That is deliberate.
