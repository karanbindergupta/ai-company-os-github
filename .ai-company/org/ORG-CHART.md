# ORG CHART

**107 roles across 10 departments.**

Roles are *role packs* in `.ai-company/org/roles/`, adopted by the executable subagents in
`.claude/agents/`. Regenerate with `scripts/audit_org.py` after any change.

## Executive Council (11)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Chief Executive Officer](roles/executive/ceo.md) | `founder` | `.ai-company/mission/charter.md` |
| [Chief Financial Officer](roles/executive/cfo.md) | `ceo` | `.ai-company/finance/model.md` |
| [Chief Information Security Officer](roles/executive/ciso.md) | `ceo` | `.ai-company/security/posture.md` |
| [Chief Marketing Officer](roles/executive/cmo.md) | `ceo` | `.ai-company/marketing/gtm.md` |
| [Chief Operating Officer](roles/executive/coo.md) | `ceo` | `.ai-company/state/operations.md` |
| [Chief Product Officer](roles/executive/cpo.md) | `ceo` | `.ai-company/product/strategy.md` |
| [Creative Director](roles/executive/creative-director.md) | `ceo` | `.ai-company/design/creative-direction.md` |
| [Chief Research Officer](roles/executive/cro-research.md) | `ceo` | `.ai-company/research/synthesis.md` |
| [Chief Risk Officer](roles/executive/cro-risk.md) | `ceo` | `.ai-company/risks/register.md` |
| [Chief Strategy Officer](roles/executive/cso.md) | `ceo` | `.ai-company/decisions/strategy.md` |
| [Chief Technology Officer](roles/executive/cto.md) | `ceo` | `.ai-company/architecture/cto-position.md` |

## Strategy & Research (15)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Brand Strategy Lead](roles/strategy-research/brand-strategist-research.md) | `cro-research` | `.ai-company/design/brand-strategy.md` |
| [Business Model Strategist](roles/strategy-research/business-model-strategist.md) | `cro-research` | `.ai-company/decisions/business-model.md` |
| [Competitive Intelligence Analyst](roles/strategy-research/competitor-intelligence.md) | `cro-research` | `.ai-company/research/competitors.md` |
| [Customer Researcher](roles/strategy-research/customer-researcher.md) | `cro-research` | `.ai-company/research/customers.md` |
| [Feasibility Analyst](roles/strategy-research/feasibility-analyst.md) | `cro-research` | `.ai-company/research/feasibility.md` |
| [Features Strategist](roles/strategy-research/features-strategist.md) | `cro-research` | `.ai-company/product/features.md` |
| [Financial Strategist](roles/strategy-research/financial-strategist.md) | `cro-research` | `.ai-company/finance/projections.md` |
| [Industry Researcher](roles/strategy-research/industry-researcher.md) | `cro-research` | `.ai-company/research/industry.md` |
| [Innovation Strategist](roles/strategy-research/innovation-strategist.md) | `cro-research` | `.ai-company/research/innovation.md` |
| [Market Researcher](roles/strategy-research/market-researcher.md) | `cro-research` | `.ai-company/research/market.md` |
| [Opportunity Analyst](roles/strategy-research/opportunity-analyst.md) | `cro-research` | `.ai-company/research/opportunities.md` |
| [Pricing Strategist](roles/strategy-research/pricing-strategist.md) | `cro-research` | `.ai-company/finance/pricing.md` |
| [Problem Solver](roles/strategy-research/problem-solver.md) | `cro-research` | `.ai-company/incidents/` |
| [R&D Specialist](roles/strategy-research/rnd-specialist.md) | `cro-research` | `.ai-company/research/rnd/` |
| [Trend Analyst](roles/strategy-research/trend-analyst.md) | `cro-research` | `.ai-company/research/trends.md` |

## Product (10)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Acceptance Criteria Specialist](roles/product/acceptance-criteria-specialist.md) | `cpo` | `.ai-company/product/acceptance-criteria.md` |
| [Business Analyst](roles/product/business-analyst.md) | `cpo` | `.ai-company/product/analysis.md` |
| [Feature Specialist](roles/product/feature-specialist.md) | `cpo` | `.ai-company/product/features/` |
| [Product Auditor](roles/product/product-auditor.md) | `cpo` | `.ai-company/audits/product.md` |
| [Product Discovery Specialist](roles/product/product-discovery-specialist.md) | `cpo` | `.ai-company/product/discovery.md` |
| [Product Manager](roles/product/product-manager.md) | `cpo` | `.ai-company/product/requirements.md` |
| [Product Owner](roles/product/product-owner.md) | `cpo` | `.ai-company/product/acceptance.md` |
| [Product Strategist](roles/product/product-strategist.md) | `cpo` | `.ai-company/product/product-strategy.md` |
| [Requirements Engineer](roles/product/requirements-engineer.md) | `cpo` | `.ai-company/product/functional-requirements.md` |
| [Roadmap Strategist](roles/product/roadmap-strategist.md) | `cpo` | `.ai-company/roadmap/roadmap.md` |

## Creative & Brand (13)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Accessibility Designer](roles/creative/accessibility-designer.md) | `creative-director` | `.ai-company/design/accessibility.md` |
| [Brand Designer](roles/creative/brand-designer.md) | `creative-director` | `.ai-company/design/brand-identity.md` |
| [Brand Application Lead](roles/creative/brand-strategist-creative.md) | `creative-director` | `.ai-company/design/brand-application.md` |
| [Content Designer](roles/creative/content-designer.md) | `creative-director` | `.ai-company/design/content.md` |
| [Creative Auditor](roles/creative/creative-auditor.md) | `creative-director` | `.ai-company/audits/creative.md` |
| [Design System Architect](roles/creative/design-system-architect.md) | `creative-director` | `.ai-company/design/design-system.md` |
| [Interaction Designer](roles/creative/interaction-designer.md) | `creative-director` | `.ai-company/design/interaction.md` |
| [Motion Specialist](roles/creative/motion-specialist.md) | `creative-director` | `.ai-company/design/motion.md` |
| [Positioning Writer](roles/creative/positioning-writer.md) | `creative-director` | `.ai-company/design/positioning-copy.md` |
| [UI Designer](roles/creative/ui-designer.md) | `creative-director` | `.ai-company/design/ui/` |
| [UX Designer](roles/creative/ux-designer.md) | `creative-director` | `.ai-company/design/ux/` |
| [UX Researcher](roles/creative/ux-researcher.md) | `creative-director` | `.ai-company/design/ux-research.md` |
| [Visual Designer](roles/creative/visual-designer.md) | `creative-director` | `.ai-company/artifacts/visual/` |

## Engineering (18)

| Role | Reports to | Primary artifact |
|---|---|---|
| [AI/ML Engineer](roles/engineering/ai-ml-engineer.md) | `cto` | `.ai-company/architecture/ml-design.md` |
| [API Specialist](roles/engineering/api-specialist.md) | `backend-lead` | `.ai-company/architecture/api-spec.md` |
| [Backend Engineer](roles/engineering/backend-engineer.md) | `backend-lead` | `(source files in the product repository)` |
| [Backend Lead](roles/engineering/backend-lead.md) | `cto` | `.ai-company/engineering/backend-plan.md` |
| [Cloud Architect](roles/engineering/cloud-architect.md) | `cto` | `.ai-company/architecture/infrastructure.md` |
| [Data Engineer](roles/engineering/data-engineer.md) | `database-architect` | `(source files)` |
| [Database Architect](roles/engineering/database-architect.md) | `cto` | `.ai-company/architecture/data-model.md` |
| [DevOps Engineer](roles/engineering/devops-engineer.md) | `cto` | `(source files)` |
| [Frontend Engineer](roles/engineering/frontend-engineer.md) | `frontend-lead` | `(source files in the product repository)` |
| [Frontend Lead](roles/engineering/frontend-lead.md) | `cto` | `.ai-company/engineering/frontend-plan.md` |
| [Infrastructure Engineer](roles/engineering/infrastructure-engineer.md) | `cloud-architect` | `(source files)` |
| [Integration Engineer](roles/engineering/integration-engineer.md) | `backend-lead` | `.ai-company/architecture/integrations.md` |
| [Mobile Engineer](roles/engineering/mobile-engineer.md) | `frontend-lead` | `(source files)` |
| [Performance Engineer](roles/engineering/performance-engineer.md) | `cto` | `.ai-company/qa/performance.md` |
| [Principal Architect](roles/engineering/principal-architect.md) | `cto` | `.ai-company/architecture/architecture.md` |
| [Solution Architect](roles/engineering/solution-architect.md) | `principal-architect` | `.ai-company/architecture/solutions/` |
| [Site Reliability Engineer](roles/engineering/sre.md) | `cto` | `.ai-company/engineering/reliability.md` |
| [Systems Architect](roles/engineering/systems-architect.md) | `principal-architect` | `.ai-company/architecture/systems.md` |

## Quality (10)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Accessibility Tester](roles/quality/accessibility-tester.md) | `qa-lead` | `.ai-company/qa/accessibility.md` |
| [Architecture Auditor](roles/quality/architecture-auditor.md) | `cro-risk` | `.ai-company/audits/architecture.md` |
| [Code Reviewer](roles/quality/code-reviewer.md) | `qa-lead` | `.ai-company/qa/reviews/` |
| [End-to-End Tester](roles/quality/e2e-tester.md) | `qa-lead` | `.ai-company/qa/e2e.md` |
| [Performance Tester](roles/quality/performance-tester.md) | `qa-lead` | `.ai-company/qa/performance-tests.md` |
| [QA Engineer](roles/quality/qa-engineer.md) | `qa-lead` | `.ai-company/qa/results/` |
| [QA Lead](roles/quality/qa-lead.md) | `cto` | `.ai-company/qa/strategy.md` |
| [Regression Tester](roles/quality/regression-tester.md) | `qa-lead` | `.ai-company/qa/regression.md` |
| [Release Manager](roles/quality/release-manager.md) | `coo` | `.ai-company/qa/release-checklist.md` |
| [Test Automation Engineer](roles/quality/test-automation-engineer.md) | `qa-lead` | `(test files)` |

## Security (8)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Application Security Engineer](roles/security/appsec-engineer.md) | `ciso` | `.ai-company/security/appsec.md` |
| [Compliance Specialist](roles/security/compliance-specialist.md) | `ciso` | `.ai-company/security/compliance.md` |
| [Dependency Auditor](roles/security/dependency-auditor.md) | `ciso` | `.ai-company/security/dependencies.md` |
| [Privacy Specialist](roles/security/privacy-specialist.md) | `ciso` | `.ai-company/security/privacy.md` |
| [Defensive Red Team](roles/security/red-team.md) | `ciso` | `.ai-company/security/red-team.md` |
| [Security Architect](roles/security/security-architect.md) | `ciso` | `.ai-company/security/architecture.md` |
| [Security Reviewer](roles/security/security-reviewer.md) | `ciso` | `.ai-company/security/review.md` |
| [Threat Modeler](roles/security/threat-modeler.md) | `ciso` | `.ai-company/security/threat-model.md` |

## Growth & Marketing (10)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Acquisition Specialist](roles/growth/acquisition-specialist.md) | `cmo` | `.ai-company/marketing/acquisition.md` |
| [Analytics Specialist](roles/growth/analytics-specialist.md) | `cmo` | `.ai-company/marketing/analytics.md` |
| [Content Strategist](roles/growth/content-strategist.md) | `cmo` | `.ai-company/marketing/content-strategy.md` |
| [Copywriter](roles/growth/copywriter.md) | `cmo` | `.ai-company/marketing/copy/` |
| [Conversion Optimization Specialist](roles/growth/cro-specialist.md) | `cmo` | `.ai-company/marketing/conversion.md` |
| [Customer Success Strategist](roles/growth/customer-success-strategist.md) | `cmo` | `.ai-company/marketing/customer-success.md` |
| [Growth Strategist](roles/growth/growth-strategist.md) | `cmo` | `.ai-company/marketing/growth.md` |
| [Marketing Strategist](roles/growth/marketing-strategist.md) | `cmo` | `.ai-company/marketing/strategy.md` |
| [SEO Specialist](roles/growth/seo-specialist.md) | `cmo` | `.ai-company/marketing/seo.md` |
| [Social Strategy Specialist](roles/growth/social-strategist.md) | `cmo` | `.ai-company/marketing/social.md` |

## Operations (7)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Agent Performance Auditor](roles/operations/agent-performance-auditor.md) | `coo` | `.ai-company/audits/organization.md` |
| [Cost Optimizer](roles/operations/cost-optimizer.md) | `cfo` | `.ai-company/state/cost-report.md` |
| [Delivery Manager](roles/operations/delivery-manager.md) | `coo` | `.ai-company/engineering/integration.md` |
| [Documentation Specialist](roles/operations/documentation-specialist.md) | `coo` | `.ai-company/docs/INDEX.md` |
| [Knowledge Manager](roles/operations/knowledge-manager.md) | `coo` | `.ai-company/knowledge/` |
| [Project Manager](roles/operations/project-manager.md) | `coo` | `.ai-company/state/project-plan.md` |
| [Technical Writer](roles/operations/technical-writer.md) | `coo` | `.ai-company/docs/` |

## People (HR) (5)

| Role | Reports to | Primary artifact |
|---|---|---|
| [Chief People Officer](roles/people/chief-people-officer.md) | `ceo` | `.ai-company/org/hiring/decisions.md` |
| [Onboarding Specialist](roles/people/onboarding-specialist.md) | `chief-people-officer` | `.ai-company/org/hiring/onboarding.md` |
| [Organization Designer](roles/people/org-designer.md) | `chief-people-officer` | `.ai-company/org/org-design.md` |
| [Role Author](roles/people/role-author.md) | `chief-people-officer` | `.ai-company/org/roles/<department>/<slug>.md` |
| [Role Researcher](roles/people/role-researcher.md) | `chief-people-officer` | `.ai-company/org/hiring/research/` |

## Authority notes

- The **CEO** resolves executive conflict but cannot override the CISO on security.
- The **CISO** holds a release veto. Only the **founder** may accept a security risk.
- The **Release Manager** can stop any release but cannot authorize one.
- **Auditors report to the Chief Risk Officer**, not to the department they audit. The
  Architecture Auditor reports to the CRO, not the CTO, so the audit is genuinely independent.
- The **Chief People Officer** may add role packs; creating a new executable subagent needs
  founder approval, because each one permanently costs orchestrator context.
