# LAUNCH OPERATIONS

```
PRE-LAUNCH → READINESS CHECK → DEPLOYMENT → MONITORING → VALIDATION → INCIDENT RESPONSE → POST-LAUNCH REVIEW
```

## Pre-launch
Confirm every gate has **evidence on disk**, not a promise. Rollback plan written **and tested** —
an untested rollback is a hope. Metrics defined **before** launch. Owner on point for the window.

## Readiness check
```bash
python3 scripts/companydb.py release check id=REL-x.y.z
python3 scripts/companydb.py veto list
```
Seven gates: product · engineering · QA · security · performance · docs · rollback.
`release ship` refuses on any unmet gate, any active veto, or missing founder approval.

## Deployment
**Founder-authorized, always** (`production_deploy` is founder-required). Reversible by design.
One person deploying, one watching. Never deploy into an unmonitored window.

## Monitoring and validation
Watch the metrics defined pre-launch, not metrics chosen afterwards to look good. Validate the
**user-visible** outcome, not just that the deploy succeeded. A green deploy with a broken signup
flow is a failed launch.

## Incident response
If it goes wrong: **contain first, diagnose second.** Roll back rather than fixing forward under
pressure. Open an incident — do not handle it informally.

## Post-launch review
Predicted vs actual. What did we get wrong? What did the gates miss? Which assumption failed?
Write to `.ai-company/knowledge/lessons-learned/`. **A launch review that finds nothing has not
been done honestly** — something always differs from the plan.
