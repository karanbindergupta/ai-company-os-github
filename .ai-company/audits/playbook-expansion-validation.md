---
artifact: playbook-expansion-validation
version: 1.0.0
date: 2026-09-07
---
# PLAYBOOK EXPANSION — VALIDATION

Four first-class departments installed: **Executive, Growth, Operations, People.**
Audit ran first; the six existing playbooks were extended, never rebuilt.

## Defects found by testing — all fixed

**1. `backup_for` written inverted (critical).** Set so the CISO backed up the security-reviewer
rather than the reverse. `workforce.py health` caught it immediately, reporting 9 critical roles
as single points of failure while simultaneously listing them as backups. Corrected: 16
relationships now point backup → critical role. SPOFs: **zero**.

**2. `capability=finance` matched nothing.** Finance roles live under `executive` and
`strategy-research`, not a `finance` department. The orchestrator's vocabulary is not the
department list. Fixed with a capability alias map (finance, marketing, legal, analytics, risk,
architecture, research, qa, design, strategy, release).

**3. Team formation ranked by load alone**, selecting alphabetically-first low-load agents —
`accessibility-designer` for "creative", `acceptance-criteria-specialist` for "product". Fixed to
rank relevance first, load second, with leads outranking juniors on equal match. Now returns
`growth-strategist, product-manager, cfo, analytics-specialist`.

## The four §9 simulations

### Executive — strategic decision with conflicting opinions
`DEC-001` EU market entry. CFO dissented (uncosted GDPR work, unsourced CAC); CISO dissented
(data residency absent from architecture). Both preserved verbatim.
- Decision **refused** while required reviewers (cfo, cmo, ceo) were missing
- After reviews, **refused again** — `market_entry` is founder-required
- Decided only with founder approval, and the ruling changed under dissent pressure:
  *"Enter EU Q4, gated on GDPR + data-residency work"* rather than the original Q3 proposal
- **2 dissenting opinions reported at decision time**

### Growth — strong traffic, poor conversion and retention
Team assembled from the *relevant* disciplines: growth-strategist, analytics-specialist,
product-manager, cro-research — each with an independent reviewer.

### Operations — execution becoming chaotic
An induced dependency cycle was caught: `dependency cycle: CA -> CB -> CA`.
Health surfaced the real bottleneck honestly: **`code-reviewer` at 6 items, `backend-lead` at 5** —
the classic single-over-relied-upon-reviewer bottleneck named in the operations playbook.

### People — overload, duplication, missing backup
Removing `architecture-auditor`'s backup registration was detected immediately:
*"principal-architect — no agent is registered as backup_for=principal-architect"*.
Reassignment away from the overloaded `backend-lead` returned `ai-ml-engineer` (load 0) rather
than routing more work to the strongest agent.

## Honest limitation
These simulations exercised **mechanisms** — authority, dissent, cycle detection, load balancing,
team assembly. They did not run live subagents producing real departmental work. The machinery is
proven; the quality of executive judgement, growth analysis and operational reporting under real
load remains unproven until a real mission runs.
