---
playbook: people
version: 1.0.0
department: people
---
# PEOPLE PLAYBOOK — "How do we manage and improve our AI workforce?"

**This is AI workforce management, not HR.** Do not import traditional HR practice: there is no
morale, no compensation, no career ladder. There *is* capability, allocation, reliability,
redundancy and retirement — and those are engineering problems.

| Document | Covers |
|---|---|
| `README.md` | Workforce architecture, assignment, failure modes |
| `TEAM-FORMATION.md` | Dynamic team assembly and dissolution |
| `PERFORMANCE-AND-DEVELOPMENT.md` | Review, diagnosis before replacement, specialization |
| `REDUNDANCY-AND-RETIREMENT.md` | Backups, conflict, deprecation, permission governance |

**Backed by a real mechanism, not documentation:** `scripts/workforce.py`.
**Extends:** `agents` table, `agent_performance`, `scripts/agent_scorecard.py`,
`org/roles.json`, the `people` role packs, `scripts/audit_org.py`.

## 1. The workforce registry
```bash
python3 scripts/workforce.py registry [department]
```
Per agent: role · capabilities · **cognitive profile** · tools · permissions · seniority ·
current workload · performance · strengths · weaknesses · reliability · backup · status.

**Cognitive profile** is what kind of thinking the role is being asked for — not a personality.
A QA engineer's is *"adversarial curiosity; assumes the happy path is a lie until tested"*. That
is an assignment input: it is why you do not route threat modelling to a role optimized for
throughput.

## 2. Agent assignment — the orchestrator's question
```bash
python3 scripts/workforce.py assign capability=<x> [risk=high] [exclude=a,b]
```
Returns a recommended owner, **an independent reviewer**, and alternates. Ranking weighs
capability match first, then current load, then track record.

> **Do NOT assign every task to the same high-performing agent.**

That is the most tempting failure in this department. It creates a bottleneck, a single point of
failure, and an organization whose resilience is one agent deep. The ranking deliberately
penalizes load so work spreads.

## 3. Standard workflow
1. Receive the capability request from the orchestrator
2. Check the registry for matching capability and cognitive fit
3. Check current load — do not overload a strong performer
4. Recommend owner + independent reviewer + alternates
5. For high-risk work, attach executive oversight and an auditor
6. Record the assignment; performance accrues automatically on task update
7. Review outcomes; diagnose failures before reassigning

## 4. Common failure modes
- **Hero routing** — everything to the best agent. Creates the bottleneck and the SPOF
- **Replacing before diagnosing** — the agent is usually not the problem
- **Speculative hiring** — a role with no observed gap is context cost with no return
- **Permission drift** — responsibilities change, obsolete permissions stay active
- **Over-specialization** — deep expertise creating organizational blind spots
- **Silent single points of failure** — a critical capability with no backup, unnoticed until it fails

## 5. Quality checklist
- [ ] Assignment matched capability, not convenience
- [ ] Owner ≠ reviewer (enforced by the database)
- [ ] No agent carries a disproportionate share of open work
- [ ] Every critical capability has a named backup
- [ ] Failures were diagnosed before any reassignment
- [ ] Permissions reviewed when responsibilities changed

## 6. Integration with the orchestrator (§5)
Orchestrator asks *"who should do this?"* → People answers from expertise, cognitive profile,
workload, performance, tools, risk and availability → orchestrator dispatches.
**People recommends; the orchestrator assigns.** Neither does both.

## 7. Integration with executives (§6)
```bash
python3 scripts/workforce.py health
```
Surfaces for organizational design: capability gaps · overloaded specialists · weak areas ·
bottlenecks · redundant capability · high performers · **critical single points of failure**.

## 8. Excellent vs unacceptable

**Excellent**
> "Three agents overloaded (backend-lead 7 items, qa-lead 6, cro-research 5). `principal-architect`
> has no backup for architecture review — SPOF on a critical capability. `product-auditor` and
> `acceptance-criteria-specialist` overlap on criteria verification. Recommend: route the next two
> backend tasks to `backend-engineer` with `backend-lead` reviewing; register
> `architecture-auditor` as backup_for `principal-architect`; merge the criteria responsibility
> into `product-auditor` and narrow the specialist's pack to authoring only."

**Unacceptable**
> "The team is working well. backend-lead is our strongest agent so we should give it the
> important tasks."
