---
description: Add a feature through the full company workflow
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Feature: **$ARGUMENTS**

A feature is a small mission, not a shortcut past the process:
1. `product-lead` — is this justified by evidence? What does it displace? Write the spec and
   acceptance criteria. **Rejecting it is a valid outcome.**
2. `architect` — how does it fit the existing architecture?
3. `designer` — flows including error and empty states.
4. `engineer` — implement with tests.
5. `qa-lead` — independent verification.
6. `security-lead` — if it touches auth, data or third parties.
7. `auditor` — if it materially changes the product.

Track it: `python3 scripts/company.py task-add title="..." owner=... criteria="..."`
