---
document: authority-matrix
version: 1.0.0
source: generated from decision_rights in .ai-company/state/company.db
---
# AUTHORITY MATRIX

Generated from the database, so it cannot drift from what is enforced.
Verify any row with `python3 scripts/companydb.py can <role> <action> <domain>`.

| Domain | Owner | Required review | Veto | Founder | Escalates to |
|---|---|---|---|---|---|
| `business_model` | **cfo** | cso,cpo,ceo | **cfo** | **YES** | L4 |
| `data_migration` | **database-architect** | cto | **cto,ciso** | **YES** | L4 |
| `major_financial_commitment` | **cfo** | ceo | **cfo** | **YES** | L4 |
| `market_entry` | **cso** | cfo,cmo,ceo | **cro-risk** | **YES** | L4 |
| `pricing` | **cfo** | cpo,ceo,pricing-strategist | **cfo** | **YES** | L4 |
| `production_deploy` | **devops-engineer** | release-manager,ciso | **ciso,release-manager** | **YES** | L4 |
| `public_communication` | **cmo** | ceo,creative-director | — | **YES** | L4 |
| `release_readiness` | **release-manager** | qa-lead,ciso,cpo | **ciso,qa-lead,release-manager** | **YES** | L4 |
| `risk_acceptance` | **cro-risk** | ceo,ciso | **cro-risk** | **YES** | L4 |
| `brand_direction` | **creative-director** | cmo,ceo | **creative-director** | no | L3 |
| `engineering_standards` | **cto** | backend-lead,frontend-lead | **cto** | no | L2 |
| `hiring_role` | **chief-people-officer** | coo | **chief-people-officer** | no | L2 |
| `marketing_strategy` | **cmo** | cpo,cfo | — | no | L3 |
| `product_roadmap` | **cpo** | ceo,cso | **cpo** | no | L3 |
| `product_scope` | **cpo** | product-manager,cto | **cpo** | no | L3 |
| `research_acceptance` | **cro-research** | research-auditor | **research-auditor,cro-risk** | no | L2 |
| `routine_bugfix` | **qa-lead** | code-reviewer | — | no | L1 |
| `routine_implementation` | **backend-lead** | code-reviewer | — | no | L1 |
| `security_architecture` | **ciso** | cto,security-architect | **ciso** | no | L3 |
| `technical_architecture` | **cto** | principal-architect,security-architect | **ciso,cto** | no | L3 |

## How this is enforced

- `decision new` refuses an owner who does not own the domain.
- `decision decide` refuses while any required reviewer is missing.
- `decision decide` refuses while an active veto targets the decision.
- `decision decide` refuses a founder-required domain without `founder_approval=`.
- `veto raise` refuses a role that holds no veto over that domain.
- `veto lift` refuses anyone except the role that raised it.
- `release ship` refuses on any unmet gate, any active veto, or missing founder approval.

## Escalation levels

| Level | Resolver |
|---|---|
| 0 | The agent itself |
| 1 | A peer specialist |
| 2 | Department lead |
| 3 | Executive |
| 4 | **Founder** |

A level-4 escalation without a recommendation is refused by the system.
