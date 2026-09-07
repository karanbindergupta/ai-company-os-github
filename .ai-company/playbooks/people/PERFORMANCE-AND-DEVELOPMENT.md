# AGENT PERFORMANCE AND DEVELOPMENT

## Review dimensions
quality · correctness · reliability · decision quality · **calibration** (was stated confidence
justified?) · rework · collaboration · efficiency · **useful** escalations · missed risks ·
business outcomes.

```bash
python3 scripts/agent_scorecard.py
```
Scoring is quality-weighted: rework costs 1.5×, review failure 2.0×, against completion.
**Speed is not a metric.** An agent that finishes fast and creates rework scores worse than a
slower correct one — that is deliberate and matches spec §27.

Performance is judged on **outcomes and evidence**, never on volume of output.

## Diagnose before replacing
When an agent repeatedly fails, the agent is usually not the cause. Work through these in order:

| # | Cause | Signal | Fix |
|---|---|---|---|
| 1 | **Poor instructions** | Failures cluster on one task type | Revise the role pack |
| 2 | **Bad task assignment** | Wrong capability for the work | Fix routing, not the agent |
| 3 | **Insufficient tools** | Blocked on access | Check the integration matrix |
| 4 | **Insufficient knowledge** | Repeats known-solved mistakes | Point at the playbook and lessons |
| 5 | **Inadequate review** | Defects reach QA | Strengthen the reviewer, not the author |
| 6 | **Excessive workload** | Quality drops as load rises | `workforce.py health` |
| 7 | **Wrong cognitive profile** | Consistently misjudges this work class | Reassign the work class |
| 8 | **Unsuitable model** | Reasoning-depth failures | See `governance/MODEL-ROUTING.md` |
| 9 | **Insufficient capability** | Everything above ruled out | *Only now* consider replacement |

> **Do not immediately replace the agent. Diagnose first.**
> In this organization, most "agent failure" is specification failure wearing a costume.

## Specialization — and its danger
Agents strengthen in a domain through repeated work, accumulated knowledge, specialized playbooks
and lessons learned. That is desirable.

**But over-specialization creates organizational blind spots.** If only one role ever touches
security, the company sees security only through that lens. Counter it by keeping backup
capability real (not nominal), rotating reviewers, and having auditors report to a *different*
line than the work they audit — which is why `research-auditor` reports to CRO-Risk, not CRO-Research.
