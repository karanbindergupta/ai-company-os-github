# DYNAMIC TEAM FORMATION
Teams are assembled **to the problem** and dissolved when it is solved. A standing team for
everything is the same failure as activating every agent for every task.

## Procedure
1. Understand the objective
2. Identify required capabilities — the disciplines, not the individuals
3. Identify risk level
4. Select specialists by capability match, cognitive fit and available load
5. Select **reviewers independent of each member**
6. Attach executive oversight where risk warrants it
7. Create the team; assign responsibilities
8. Execute
9. **Dissolve when complete**

```bash
python3 scripts/workforce.py team form objective=".." capabilities=growth,product,finance risk=high
python3 scripts/workforce.py team list
python3 scripts/workforce.py team dissolve id=TEAM-XXXXXX
```

## Cross-department composition (spec §8)
| Situation | Team |
|---|---|
| **New product launch** | Executive · Product · Growth · Marketing · Creative · Operations · Engineering · QA · Security · Finance |
| **Major hiring / capability decision** | People · Operations · Finance · the relevant executive |
| **Growth campaign** | Growth · Marketing · Creative · Product · Finance · Analytics |
| **Major operational change** | Operations · CTO · Security · Finance · the relevant executive |
| **Security incident** | CISO (lead) · CTO · CEO · CRO-Risk (+ CMO only if disclosure is in scope) |

## Sizing
Add a capability only if its absence would change the outcome. **Every added member costs context,
coordination and tokens.** A five-role team that decides beats a twelve-role team that converges.

## Dissolution
Dissolve as soon as the objective completes. A team that persists past its purpose starts
generating work to justify itself — and holds agents unavailable for real work.
