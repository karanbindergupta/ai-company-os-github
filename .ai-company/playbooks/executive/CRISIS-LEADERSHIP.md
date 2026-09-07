# CRISIS LEADERSHIP
Command is **assembled dynamically to the incident**, not convened wholesale. A security breach
does not need the CMO in the first hour; a public data exposure does.

## Command roles
| Executive | Command |
|---|---|
| CEO | Strategic command; the single decision-maker |
| COO | Operational coordination |
| CTO | Technical command |
| **CISO** | **Security command — has the veto, including against the CEO** |
| CFO | Financial impact |
| CPO | Customer and product impact |
| CMO | Communications and market impact (**founder approves all external comms**) |
| CRO-Risk | Enterprise risk and containment scope |

## Assembly by incident type
| Incident | Command |
|---|---|
| Security breach | CISO (lead) · CTO · CEO · CRO-Risk. CMO only once disclosure is in scope |
| Outage | CTO (lead) · COO · SRE · CPO |
| Data loss | CTO · CISO · CRO-Risk · CEO · **founder immediately** |
| Financial | CFO (lead) · CEO · **founder** |
| Reputational | CMO · CEO · CRO-Risk · **founder owns all external statements** |

## Procedure
`DETECT → CLASSIFY → ASSIGN → DIAGNOSE → CONTAIN → FIX → TEST → REVIEW → DEPLOY → VERIFY → POSTMORTEM → LESSON`
```bash
python3 scripts/companydb.py incident open title=".." severity=critical owner=<lead> detection=".."
python3 scripts/companydb.py incident resolve id=INC-0xx postmortem=".." preventive_action=".."
```
`resolve` refuses without both a postmortem and a concrete preventive action.

## Crisis rules
1. **Contain before fixing.** Stop the bleeding first.
2. **One decision-maker.** The CEO or the named lead — not a committee, mid-incident.
3. **The CISO's veto still applies.** Speed never silently overrides security (constitution §XIX).
4. **Escalate to the founder immediately** for: data loss, external disclosure, legal exposure,
   financial impact, anything irreversible.
5. **Postmortems are blameless and produce exactly one concrete preventive action.**
6. Never communicate externally without founder approval — `public_communication` is founder-required.
