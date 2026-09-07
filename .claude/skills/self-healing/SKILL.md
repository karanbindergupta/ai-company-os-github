---
name: self-healing
description: How to handle failure - agent failure, task failure, and findings. Load when a task fails, an agent loops, or an audit produces findings. Covers classification, intelligent retry, and the prohibition on repeating a failed approach.
---

# Self-healing

A finding that is only reported is a finding that will still be there at launch.

## Findings become tasks, never observations
```bash
python3 scripts/company.py task-add title="Fix: <finding>" owner=<role> phase=remediate \
  criteria="<what must be true>; verified by <how>"
```
Every finding gets severity, affected area, owner, dependencies and acceptance criteria. Then:
**fix → test → independent review → retest.**

Closed means fixed and verified, or formally accepted as a recorded risk with an owner.

## When an agent fails
1. **Detect** — the task engine counts attempts.
2. **Classify** — missing input? bad specification? genuine technical blocker? wrong owner?
3. **Preserve** — write partial work with `status: partial` and `blocked_on`. Never discard it.
4. **Record**:
   ```bash
   python3 scripts/company.py incident what="..." task=<id> tried="..." next="..."
   ```
5. **Change strategy** — different approach, decomposition, or owner.
6. **Escalate at two failures** — dispatch `problem-solver`.

## The rule that matters
**Never run the same failed action twice.** Governance rule 11. Read `.ai-company/incidents/`
before retrying anything. Looping burns tokens and produces nothing - it is the single most
common failure mode of autonomous systems.

## Failure classes
| Class | Response |
|---|---|
| Missing input | Find the upstream owner; do not guess the input |
| Bad specification | Return to the specifier — do not implement a guess |
| Technical blocker | `problem-solver`; consider a different approach |
| Wrong owner | Reassign via the COO |
| Genuinely impossible | Say so. That is a valid, valuable outcome |

"This cannot be done as specified" is a legitimate resolution. Say it early.
