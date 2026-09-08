---
document: playbook-index
version: 2.0.0
---
# COMPANY PLAYBOOK INDEX

Playbooks are **operating systems for their department**, not descriptions of responsibility.
Every specialist loads its department's playbook alongside its role pack.

## The 20 departments

| # | Department | Playbook | Covers |
|---|---|---|---|
| 1 | **Executive** | [`executive/`](executive/) | Strategy, governance, decisions, capital, conflict, crisis leadership |
| 2 | **Strategy** | [`research.md`](research.md) + [`executive/`](executive/) | Market, competition, positioning, strategic planning |
| 3 | **Research** | [`research.md`](research.md) | Methodology, evidence, sourcing, synthesis |
| 4 | **Product** | [`product.md`](product.md) | Discovery, requirements, prioritization, validation |
| 5 | **Design** | [`design.md`](design.md) | UX, UI, design systems, accessibility |
| 6 | **Creative** | [`design.md`](design.md) + [`../design/creative-standards/`](../design/creative-standards/) | Brand, visual identity, direction, campaigns |
| 7 | **Engineering** | [`engineering.md`](engineering.md) + [`engineering/`](engineering/) | Craft + the CTO organization, rights matrix and routing |
| 8 | **Security** | [`security.md`](security.md) | Threat modelling, secure development, security testing |
| 9 | **QA** | [`engineering.md`](engineering.md) + [`../docs/QUALITY-GATES.md`](../docs/QUALITY-GATES.md) | Testing, validation, regression, gates |
| 10 | **Finance** | [`finance.md`](finance.md) | Economics, budgeting, forecasting, pricing |
| 11 | **Growth** | [`growth/`](growth/) | Acquisition, activation, retention, monetization, experimentation |
| 12 | **Marketing** | [`growth/`](growth/) + [`../design/creative-standards/`](../design/creative-standards/) | Positioning, messaging, campaigns, content |
| 13 | **Operations** | [`operations/`](operations/) | Processes, SOPs, execution, resources, resilience |
| 14 | **People** | [`people/`](people/) | AI workforce management, capability, performance, staffing |
| 15 | **Analytics** | [`growth/EXPERIMENTS.md`](growth/EXPERIMENTS.md) | Measurement, instrumentation, metrics |
| 16 | **Risk** | [`executive/CONFLICT-RESOLUTION.md`](executive/CONFLICT-RESOLUTION.md) + [`../templates/risk-assessment.md`](../templates/risk-assessment.md) | Identification, assessment, mitigation |
| 17 | **Release** | [`operations/LAUNCH-OPERATIONS.md`](operations/LAUNCH-OPERATIONS.md) + [`../docs/RELEASE-POLICY.md`](../docs/RELEASE-POLICY.md) | Launch readiness, deployment, verification |
| 19 | **Managing Director** | [`executive/md/`](executive/md/) | Execution integration, commercial coordination |
| 20 | **Sales** | [`sales/`](sales/) | Prospecting, discovery, qualification, honest conversion |
| 18 | **Incident** | [`executive/CRISIS-LEADERSHIP.md`](executive/CRISIS-LEADERSHIP.md) + [`operations/RESILIENCE.md`](operations/RESILIENCE.md) | Detection, response, recovery, postmortems |

**Where a cell names two documents**, the discipline is genuinely shared — Marketing draws
strategy from Growth and craft from Creative Standards. A separate playbook was **not** created
for those, because duplicating guidance means two sources of truth that drift.

## The four operating questions
| Department | Question it answers |
|---|---|
| Executive | **How do we lead?** |
| Growth | **How do we grow sustainably?** |
| Operations | **How do we execute reliably?** |
| People | **How do we manage and improve our AI workforce?** |

## Mechanisms behind the playbooks
Playbooks describe; these enforce.
```bash
python3 scripts/companydb.py    # authority, vetoes, decisions, tasks, releases, recovery
python3 scripts/workforce.py    # who should do this; org health; team formation; retirement
python3 scripts/company.py      # SOP phases and gates
python3 scripts/agent_scorecard.py   # quality-weighted performance
python3 scripts/audit_org.py    # organizational drift
```

## Cross-department operating rule
These departments do not operate independently. Team composition for common situations is in
[`people/TEAM-FORMATION.md`](people/TEAM-FORMATION.md), and is assembled by
`workforce.py team form`, not chosen by habit.
