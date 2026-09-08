---
playbook: engineering-organization
version: 1.0.0
---
# ENGINEERING ORGANIZATION — under the CTO

**Extends** `playbooks/engineering.md` (the craft playbook). This document is the **organization**:
who reports to whom, who may do what, and how work routes.

## Why there is no Engineering Lead
The spec offered one. **We declined to create it.** `backend-lead` (Desmond Achterberg) and
`frontend-lead` (Mateo Escobar) already report to the CTO, `principal-architect` (Sasha Malenkov)
owns structure, and the COO owns sequencing. An Engineering Lead between them would be a layer
with no decision it could make that those four cannot — the spec's own warning: *"Do not create a
fake management role merely for hierarchy."*

Revisit if a real coordination failure appears in `audits/organization.md`.

## The organization
```
Priya Raghunathan (CTO) — final technical authority
├── Sasha Malenkov      Principal Architect ── Beatrix Coyle, Hugo Nakamura
├── Desmond Achterberg  Backend Lead ── Lyra Kowalczyk, Roland Adeyemi, Fionn Ó Braonáin
├── Mateo Escobar       Frontend Lead ── Suki Tanabe, Halima Yusuf
├── Vera Stanislav      Database Architect ── Annika Thorvaldsen (Supabase), Cormac Blaise
├── Salvador Reyes      Cloud Architect ── Petra Novakova
├── Rafferty Osei-Bonsu Full-Stack (cross-layer features)
├── Tanvi Sridhar       AI/ML
├── Anika Brennholt     DevOps — owns the CI foundation
├── Kenji Morrow        Performance
└── Julian Ostrowski    SRE
```

## Rights matrix — integrated with the existing authority system
| Role | Code | Review | Merge | Deploy | Prod data | Architecture |
|---|---|---|---|---|---|---|
| Frontend / Backend / Full-stack / API / AI | yes | yes | after independent review | no | no | propose |
| **Supabase (Annika)** | yes | yes | after review | no | **controlled — CTO + CISO** | propose |
| **DevOps (Anika)** | yes | yes | yes | **founder-gated** | no | propose |
| Leads | assign | approve | yes | no | no | recommend |
| **CTO (Priya)** | yes | yes | yes | founder-gated | approve | **final technical authority** |

**The CTO does not override:** CISO on security · QA on release · CFO on financial ·
Risk · Product on requirements · Creative on brand · the founder on anything reserved.

## Routing
| Work | Goes to |
|---|---|
| UI / component / accessibility | Suki (frontend-engineer) |
| Business logic, services, jobs | Lyra (backend-engineer) |
| Schema, RLS, policies, migrations | **Annika (supabase-engineer)** |
| End-to-end feature across layers | Rafferty (fullstack-engineer) |
| Third-party API, webhooks, retries | Roland / Fionn |
| CI, environments, deploys | Anika (devops-engineer) |
| Model routing, prompts, evals | Tanvi (ai-ml-engineer) |
| Architecture dispute | Sasha, then Priya |
| Security-sensitive technical issue | engineer + Rune (CISO) |

## Workflow — no gate is skipped for urgency
```
REQUIREMENT → TECHNICAL ANALYSIS → DESIGN → ARCHITECTURE REVIEW → BREAKDOWN → IMPLEMENT
→ LOCAL VALIDATION → CODE REVIEW → TESTS → CI → SECURITY → QA → PERFORMANCE (if required)
→ PRODUCT ACCEPTANCE → RELEASE APPROVAL → DEPLOY → OBSERVE → VERIFY → DOCUMENT → LEARN
```
Emergencies use the incident authority path — not a shortcut through the gates.

## Database / Supabase change workflow
```
REQUIREMENT → DATA MODEL IMPACT → MIGRATION PLAN → SAFETY REVIEW → DEV MIGRATION → TEST
→ REVIEW → CI → SECURITY → STAGING → VALIDATION → PRODUCTION APPROVAL → MIGRATE
→ VERIFY → BACKUP/RECOVERY CONFIRMATION
```
**Non-negotiable:** every table with user data has RLS enabled and a policy tested from an
unauthorized session. Service-role credentials never reach frontend code or any committed file.
Destructive production operations require CTO + CISO and are founder-gated (`data_migration`).

## Separation of duties — no circular validation
Engineering builds. **QA validates independently. CISO validates security independently.**
Release validates readiness. Product validates requirements. None of these is engineering's to
self-certify. **No engineer may claim "CI passed" without observed CI evidence.**
