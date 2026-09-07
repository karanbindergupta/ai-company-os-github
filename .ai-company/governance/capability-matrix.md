---
document: capability-matrix
version: 1.0.0
source: generated from the company database by scripts/matrices.py
---
# CAPABILITY MATRIX

All **111 roles**. A role is fully operational only when Playbook, Tools, KPIs,
Reviewer and Escalation are populated. Verify any authority claim with:
`python3 scripts/companydb.py can <role> <action> <domain>`

| Agent | Dept | Lvl | Owns (decision domains) | Veto | Tools | Playbook | KPIs | Reviewer | Escalates |
|---|---|---|---|---|---|---|---|---|---|
| `accessibility-designer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `brand-designer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `brand-strategist-creative` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `content-designer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `creative-auditor` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `design-system-architect` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `interaction-designer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `motion-specialist` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `positioning-writer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `ui-designer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `ux-designer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `ux-researcher` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `visual-designer` | creative | L3 | — | — | `design_family` | `design` | token adherence, AA failures (0), missing states | creative-director | L2 |
| `backend-lead` | engineering | L2 | routine_implementation | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L3 |
| `database-architect` | engineering | L2 | data_migration | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L3 |
| `frontend-lead` | engineering | L2 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L3 |
| `principal-architect` | engineering | L2 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L3 |
| `ai-ml-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L2 |
| `api-specialist` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | backend-lead | L2 |
| `backend-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | backend-lead | L2 |
| `cloud-architect` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L2 |
| `data-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | database-architect | L2 |
| `devops-engineer` | engineering | L3 | production_deploy | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L2 |
| `frontend-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | frontend-lead | L2 |
| `infrastructure-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cloud-architect | L2 |
| `integration-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | backend-lead | L2 |
| `mobile-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | frontend-lead | L2 |
| `performance-engineer` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L2 |
| `solution-architect` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | principal-architect | L2 |
| `sre` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | cto | L2 |
| `systems-architect` | engineering | L3 | — | — | `engineer_family` | `engineering` | defect escape, rework, coverage | principal-architect | L2 |
| `ceo` | executive | L1 | — | — | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | founder | L4 |
| `cfo` | executive | L1 | pricing, major_financial_commitment, business_model | **pricing, major_financial_commitment, business_model** | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `ciso` | executive | L1 | security_architecture | **technical_architecture, security_architecture, release_readiness, data_migration, production_deploy** | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `cmo` | executive | L1 | marketing_strategy, public_communication | — | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `coo` | executive | L1 | — | — | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `cpo` | executive | L1 | product_roadmap, product_scope | **product_roadmap, product_scope** | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `creative-director` | executive | L1 | brand_direction | **brand_direction** | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `cro-research` | executive | L1 | research_acceptance | — | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `cro-risk` | executive | L1 | risk_acceptance | **market_entry, research_acceptance, risk_acceptance** | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `cso` | executive | L1 | market_entry | — | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `cto` | executive | L1 | technical_architecture, engineering_standards | **technical_architecture, engineering_standards, data_migration** | `researcher_family` | `research` | decision quality, dissent surfaced, escalation precision | ceo | L4 |
| `acquisition-specialist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `analytics-specialist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `content-strategist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `copywriter` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `cro-specialist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `customer-success-strategist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `growth-strategist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `marketing-strategist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `seo-specialist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `social-strategist` | growth | L3 | — | — | `researcher_family` | `product` | pre-registered thresholds, CAC estimate vs actual | cmo | L2 |
| `agent-performance-auditor` | operations | L3 | — | — | `engineer_family` | `engineering` | cycle time, blocked age, status accuracy | coo | L2 |
| `cost-optimizer` | operations | L3 | — | — | `engineer_family` | `engineering` | cycle time, blocked age, status accuracy | cfo | L2 |
| `delivery-manager` | operations | L3 | — | — | `engineer_family` | `engineering` | cycle time, blocked age, status accuracy | coo | L2 |
| `documentation-specialist` | operations | L3 | — | — | `engineer_family` | `engineering` | cycle time, blocked age, status accuracy | coo | L2 |
| `knowledge-manager` | operations | L3 | — | — | `engineer_family` | `engineering` | cycle time, blocked age, status accuracy | coo | L2 |
| `project-manager` | operations | L3 | — | — | `engineer_family` | `engineering` | cycle time, blocked age, status accuracy | coo | L2 |
| `technical-writer` | operations | L3 | — | — | `engineer_family` | `engineering` | cycle time, blocked age, status accuracy | coo | L2 |
| `chief-people-officer` | people | L1 | hiring_role | **hiring_role** | `researcher_family` | `research` | roles activated vs added, authority overlaps | ceo | L4 |
| `onboarding-specialist` | people | L3 | — | — | `researcher_family` | `research` | roles activated vs added, authority overlaps | chief-people-officer | L2 |
| `org-designer` | people | L3 | — | — | `researcher_family` | `research` | roles activated vs added, authority overlaps | chief-people-officer | L2 |
| `role-author` | people | L3 | — | — | `researcher_family` | `research` | roles activated vs added, authority overlaps | chief-people-officer | L2 |
| `role-researcher` | people | L3 | — | — | `researcher_family` | `research` | roles activated vs added, authority overlaps | chief-people-officer | L2 |
| `product-manager` | product | L2 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L3 |
| `acceptance-criteria-specialist` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `business-analyst` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `feature-specialist` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `product-auditor` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `product-discovery-specialist` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `product-owner` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `product-strategist` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `requirements-engineer` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `roadmap-strategist` | product | L3 | — | — | `finance_family` | `product` | requirement traceability, reject ratio, criteria testability | cpo | L2 |
| `qa-lead` | quality | L2 | routine_bugfix | **release_readiness** | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | cto | L3 |
| `release-manager` | quality | L2 | release_readiness | **release_readiness, production_deploy** | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | coo | L3 |
| `accessibility-tester` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | qa-lead | L2 |
| `architecture-auditor` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | cro-risk | L2 |
| `code-reviewer` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | qa-lead | L2 |
| `e2e-tester` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | qa-lead | L2 |
| `performance-tester` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | qa-lead | L2 |
| `qa-engineer` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | qa-lead | L2 |
| `regression-tester` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | qa-lead | L2 |
| `test-automation-engineer` | quality | L3 | — | — | `qa_family` | `engineering` | pre-release defect find rate, regression escapes | qa-lead | L2 |
| `appsec-engineer` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `compliance-specialist` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `dependency-auditor` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `privacy-specialist` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `red-team` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `security-architect` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `security-reviewer` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `threat-modeler` | security | L3 | — | — | `security_family` | `security` | criticals at release (0), MTTR, fixes verified | ciso | L2 |
| `brand-strategist-research` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `business-model-strategist` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `competitor-intelligence` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `customer-researcher` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `evidence-verifier` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `feasibility-analyst` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `features-strategist` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `financial-strategist` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `industry-researcher` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `innovation-strategist` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `market-researcher` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `opportunity-analyst` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `pricing-strategist` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `problem-solver` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `research-auditor` | strategy-research | L3 | — | **research_acceptance** | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-risk | L2 |
| `research-director` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `research-synthesizer` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `rnd-specialist` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |
| `trend-analyst` | strategy-research | L3 | — | — | `researcher_family` | `research` | sourced-claim %, audit pass rate, fabrications (0) | cro-research | L2 |

## Coverage

- Roles with a decision domain they own: **15**
- Roles holding a veto: **10**
- Roles with a review obligation: **19**
- Every role has: a playbook, a tool family, KPIs, a reviewer and an escalation level.

Roles without an owned domain are specialists acting inside their pack's authority; they
escalate to their lead rather than deciding. That is intended, not a gap.
