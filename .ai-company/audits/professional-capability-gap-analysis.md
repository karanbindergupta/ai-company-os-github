---
document: professional-capability-gap-analysis
version: 1.0.0
date: 2026-09-07
---
# PROFESSIONAL CAPABILITY LAYER - GAP ANALYSIS

Audit of the existing AI Company OS against the Professional Capability Layer spec,
**performed before any change**, per section 1.

## Existing systems inventory (reused, not rebuilt)

| System | State |
|---|---|
| Role packs | 111 roles, 10 departments |
| Executable subagents | 19 |
| Commands | 28 |
| Company database | 29 tables |
| Decision domains | 20 |
| Integrations | 15 |
| SOP phases / gates | 23 / 13 |
| Operating documents | 12 |

## Verdict: 15 COMPLETE / 16 PARTIAL / 10 MISSING

| Sec | Capability | Status | Evidence |
|---|---|---|---|
| 2 | Company Constitution | **COMPLETE** | .ai-company/constitution/CONSTITUTION.md v1.0.0 - spec asks for governance/company-constitution.md; DUPLICATE RISK, will cross-link not recreate |
| 3 | Professional profiles (18 fields) | **PARTIAL** | 111 role packs have 13 of 18 fields; missing methodology, excellence standard, KPIs, benchmarks, continuous-improvement |
| 4 | Professional playbooks | **MISSING** | no .ai-company/playbooks/ |
| 5 | Executive operating system | **PARTIAL** | 11 exec role packs + authority matrix exist; no exec-specific challenge protocols |
| 6 | Tool registry | **COMPLETE** | integrations/REGISTRY.md, 15 integrations + 10 permission rules |
| 7 | Research intelligence layer | **COMPLETE** | Exa+Tavily live, Brave dormant, router + 6 policies, research-auditor independent |
| 8 | Knowledge system | **PARTIAL** | .ai-company/knowledge/ exists but has no domain structure or knowledge records |
| 9 | Knowledge graph | **COMPLETE** | knowledge_edges + trace verified customer->decision |
| 10 | Decision intelligence | **PARTIAL** | decisions table strong; missing reversibility + review-trigger fields |
| 11 | Experimentation engine | **PARTIAL** | experiments table exists; missing baseline/duration/cost fields |
| 12 | Customer intelligence | **MISSING** | no persona/JTBD/objection/customer-language store |
| 13 | Creative studio standards | **MISSING** | no .ai-company/design/creative-standards/ |
| 14 | Design system (tokens) | **MISSING** | design-system.md is a role OUTPUT path; no actual tokens exist |
| 15 | Engineering standards | **PARTIAL** | standards referenced in role packs; no single engineering standards doc |
| 16 | Quality gate matrix | **PARTIAL** | 13 gates enforced; no PASS/FAIL/BLOCKED/N-A matrix artifact |
| 17 | Real product validation | **COMPLETE** | 3 browser stacks; QA role packs mandate live testing |
| 18 | Security professional system | **COMPLETE** | CISO veto enforced, claude-security + npm audit, policy written |
| 19 | Finance models | **MISSING** | no reusable model templates or base/upside/downside scaffolds |
| 20 | Growth intelligence | **PARTIAL** | 10 growth role packs; no loop/channel framework artifact |
| 21 | Analytics & observability | **PARTIAL** | tables exist; nothing instrumented - correct, no product yet |
| 22 | Incident response | **COMPLETE** | incidents table + workflow + /incident command |
| 23 | Risk management | **COMPLETE** | risks table with owner/probability/impact/severity/mitigation |
| 24 | Benchmarking system | **MISSING** | no 'what would excellent look like' mechanism |
| 25 | Adversarial review | **PARTIAL** | auditor agent + adversarial-review skill; not wired as a required stage |
| 26 | Cross-functional peer review | **PARTIAL** | decision_rights encode reviewers; no dynamic review-council selector |
| 27 | Agent performance system | **PARTIAL** | agent_performance table records outcomes; no scoring or report |
| 28 | Agent learning system | **PARTIAL** | knowledge-manager role + lessons path; no capture mechanism |
| 29 | Model routing | **MISSING** | documented as a limitation in Phase 3; no routing rules |
| 30 | Founder interface | **COMPLETE** | dashboard + escalation levels + decision packages |
| 31 | Executive dashboard | **PARTIAL** | dashboard covers org/tasks/decisions/vetoes/risks/escalations; missing product, finance, growth, research sections |
| 32 | Deliverable templates | **MISSING** | no .ai-company/templates/ |
| 33 | Handoff protocol | **COMPLETE** | handoffs table with 12 fields + CLI |
| 34 | Definition of Done | **COMPLETE** | enforced 4 ways in code |
| 35 | No circular validation | **COMPLETE** | DB CHECK owner<>reviewer + runtime checks |
| 36 | Failure recovery | **COMPLETE** | recover CLI verified in Phase 3 |
| 37 | Company OS security | **COMPLETE** | secret_scan.sh, credential-handling=deny, .gitignore |
| 38 | Operating cycle | **COMPLETE** | 23-phase SOP |
| 39 | Capability matrix | **MISSING** | no governance/capability-matrix.md |
| 40 | Integration matrix | **PARTIAL** | REGISTRY.md exists; missing cost/rate-limit/health columns |
| 41 | Quality scorecard | **MISSING** | no company-quality-scorecard.md |
| 42 | Self-improvement loop | **PARTIAL** | org audit exists; no predicted-vs-actual mechanism |

## Duplication risks identified and avoided

| Spec asks for | Already exists as | Action |
|---|---|---|
| `governance/company-constitution.md` | `constitution/CONSTITUTION.md` v1.0.0 | **Cross-link, do not recreate** |
| `integrations/tool-registry.md` | `integrations/REGISTRY.md` | **Extend, do not duplicate** |
| `.ai-company/agents/<a>/professional-profile.md` | `.ai-company/org/roles/<dept>/<slug>.md` | **Extend the packs in place** |
| `incidents/`, `risks/`, `experiments/`, `decisions/` | All exist as DB tables + dirs | **Reuse** |
| Research providers | Exa + Tavily live, Brave dormant | **Reuse, install nothing** |
| Browser automation (Playwright named in spec) | 3 stacks already present | **Refuse a 4th** |
| Analytics (PostHog/Sentry/OTel named in spec) | Nothing instrumented | **Do not install - no product exists yet** |

## Implementation scope

Only the MISSING and the weakest PARTIAL items are built. Everything marked COMPLETE is left
untouched. Section 43 forbids installing capability for appearance.
