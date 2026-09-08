# REDUNDANCY, CONFLICT AND RETIREMENT

## Capability redundancy
**No critical capability should depend on one agent where a backup is practical.**
```bash
python3 scripts/workforce.py health     # lists SPOFs and existing backups
```
16 critical roles currently carry a named backup — CISO ← security-reviewer, principal-architect ←
architecture-auditor, CRO-Research ← research-auditor, CEO ← COO, and so on.

Backups are usually the **auditor or reviewer** for that role, which is deliberate: they already
understand the domain and are already independent of the primary's output.

A backup that has never done the work is nominal, not real. Rotate genuine work through it.

## Agent conflict management
When two agents repeatedly disagree, diagnose the cause rather than forcing agreement:

| Cause | Resolution |
|---|---|
| Different objectives | Realign both role packs against the mission charter |
| Different evidence | Commission research; it is a factual dispute |
| Different assumptions | Surface both; name what would falsify each |
| Different risk tolerance | CRO-Risk frames it; the founder owns risk appetite |
| Cognitive bias | Expected — it is why independent review exists |
| **Authority confusion** | `companydb.py authority <domain>`; the org designer fixes the overlap |

> **Do not force artificial consensus** — constitution §XVIII. Repeated conflict between the same
> two roles is an organizational design defect, not a personality problem.

## Agent retirement
Deprecate when: capability is duplicated · performance is consistently poor **after diagnosis** ·
the role is no longer required · technology changed · organizational design changed.

```bash
python3 scripts/workforce.py retire role=<id> reason=".." successor=<id>
```

**The command refuses** unless: the successor is a registered agent (verifies replacement
capability), the role owns no open tasks (responsibilities transferred), and the role owns no
decision domain (reassigned first).

Then, manually: preserve useful knowledge into `knowledge/lessons-learned/`, update any role
listing it as `backup_for`, and **review its tool permissions with security**.

## Permission governance
**When agent responsibilities change, review tools, permissions and data access.**
Obsolete permissions must never stay active indefinitely — that is how a least-privilege model
silently becomes an over-privileged one.

Trigger a permission review on: role retirement · authority change · a new tool grant · any
security incident involving that role. Coordinate with the CISO; the People department may
recommend a permission change but **security owns the grant**.
