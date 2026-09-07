# SKILL INVENTORY

**Audit date:** 2026-09-07

Skills come from four sources. **No skill was created, merged, replaced or removed during this
preflight** — building the AI Company skill library is the next phase's job. This is a
classification only.

| Source | Count | Notes |
|---|---|---|
| `ecc@ecc` plugin | 286 | The bulk of the library |
| Anthropic first-party (`anthropic-skills:*`) | 12 | docx/pptx/xlsx/pdf, memory, scheduling, skill-creator |
| `product-management:*` | 8 | Brainstorm, PRD, roadmap, sprint, metrics, competitive brief, research synthesis, stakeholder update |
| Host built-ins | ~15 | `design`, `dataviz`, `artifact-design`, `artifact-capabilities`, `artifact-diagramming`, `code-review`, `security-review`, `loop`, `schedule`, `workflow-authoring`, `claude-api`, `run`, `init`, `update-config`, `simplify` |
| `~/.claude/skills/learned` | 0 files | Empty directory — the ECC continuous-learning system has recorded nothing yet |

---

## KEEP — directly load-bearing for the AI Company OS

**Orchestration & multi-agent** — the highest-value cluster; the next phase should build *on* these:
`ecc:orch-pipeline`, `ecc:orch-add-feature`, `ecc:orch-build-mvp`, `ecc:orch-change-feature`,
`ecc:orch-fix-defect`, `ecc:orch-refine-code`, `ecc:orch-review`, `ecc:team-agent-orchestration`,
`ecc:team-builder`, `ecc:dev-team`, `ecc:plan-orchestrate`, `ecc:parallel-execution-optimizer`,
`ecc:council`, `ecc:council-multi-model`, `ecc:multi-workflow`, `ecc:agentic-os`,
`ecc:autonomous-agent-harness`, `ecc:autonomous-loops`, `ecc:continuous-agent-loop`,
`workflow-authoring` (host).

**Adversarial / quality gates** — maps to the "review agents, adversarial agents, auditors" requirement:
`ecc:gan-style-harness`, `ecc:gan-build`, `ecc:gan-design`, `ecc:santa-method`, `ecc:santa-loop`,
`ecc:verification-loop`, `ecc:delivery-gate`, `ecc:gateguard`, `ecc:agent-self-evaluation`,
`ecc:agent-eval`, `ecc:eval-harness`, `code-review` (host), `security-review` (host).

**Research & strategy:** `ecc:deep-research`, `ecc:market-research`, `ecc:research-ops`,
`ecc:competitive-platform-analysis`, `ecc:competitive-report-structure`, `ecc:search-first`,
`ecc:iterative-retrieval`, `product-management:*` (all 8).

**Product & design:** `design` (host), `artifact-design`, `artifact-capabilities`,
`artifact-diagramming`, `dataviz`, `ecc:design-system`, `ecc:frontend-design-direction`,
`ecc:brand-discovery`, `ecc:brand-voice`, `ecc:taste`, `ecc:accessibility`, `ecc:frontend-a11y`.

**Engineering:** language/framework `*-patterns`, `*-testing`, `*-review` families;
`ecc:tdd-workflow`, `ecc:e2e-testing`, `ecc:browser-qa`, `ecc:api-design`, `ecc:contract-first`,
`ecc:hexagonal-architecture`, `ecc:architecture-decision-records`, `ecc:git-workflow`.

**Security & audit:** `ecc:security-review`, `ecc:security-bounty-hunter`, `ecc:production-audit`,
`ecc:agent-architecture-audit`, `ecc:safety-guard`, `ecc:skill-comply`, plus the newly installed
`claude-security` plugin skill.

**State & memory** — needed for "company memory": `ecc:unified-memory`, `ecc:knowledge-ops`,
`ecc:living-docs-governance`, `ecc:recursive-decision-ledger`, `ecc:strategic-compact`,
`ecc:context-budget`, `ecc:save-session`, `ecc:resume-session`,
`anthropic-skills:consolidate-memory`, `anthropic-skills:import-memory`.

**Business/GTM:** `ecc:marketing-campaign`, `ecc:content-engine`, `ecc:seo`, `ecc:growth-log`,
`ecc:investor-materials`, `ecc:investor-outreach`, `ecc:lead-intelligence`, `ecc:social-publisher`.

**Cost control** — matters a great deal for an autonomous org: `ecc:cost-tracking`,
`ecc:ecc-tools-cost-audit`, `ecc:token-budget-advisor`, `ecc:model-route`,
`ecc:cost-aware-llm-pipeline`.

## MERGE — overlapping; the next phase should pick one per lane

| Lane | Overlapping skills | Recommendation |
|---|---|---|
| Planning | `ecc:plan`, `ecc:plan-prd`, `ecc:prp-plan`, `ecc:prp-prd`, `ecc:blueprint`, `product-management:write-spec` | Choose **one** PRD path and one plan path. `prp-*` and the non-prp variants are near-duplicates. |
| Learning | `ecc:learn`, `ecc:learn-eval`, `ecc:continuous-learning`, `ecc:continuous-learning-v2` | Keep `learn-eval` + `continuous-learning-v2`; retire the v1s. |
| PR creation | `ecc:pr`, `ecc:prp-pr` | Identical descriptions. Keep one. |
| Code review | `ecc:code-review`, `ecc:review-pr`, `ecc:orch-review`, host `code-review` | Host `code-review` + `orch-review` for gates; drop the rest. |
| Loops | `ecc:loop-start`, `ecc:loop-status`, `ecc:autonomous-loops`, `ecc:continuous-agent-loop`, `ecc:dynamic-workflow-mode`, host `loop` | Converge on one loop primitive. |

## REPLACE — none

No skill was found to be outdated or inferior enough to warrant replacement at this stage.

## REMOVE — none

**Nothing was removed and nothing is recommended for removal.** No unsafe or broken skill was
identified. The 286-skill ECC library is large but inert until invoked; the cost of carrying it is
catalogue noise, not risk.

## FUTURE — irrelevant now, keep in mind

Large domain verticals that only matter once the founder names an industry:
healthcare (`ecc:healthcare-*`, `ecc:hipaa-compliance`), networking (`ecc:homelab-*`,
`ecc:network-*`, `ecc:cisco-ios-patterns`), crypto/DeFi (`ecc:defi-amm-security`,
`ecc:evm-token-decimals`, `ecc:prediction-market-*`, `ecc:agent-payment-x402`),
logistics/supply chain (`ecc:carrier-relationship-management`, `ecc:customs-trade-compliance`,
`ecc:inventory-demand-planning`, `ecc:returns-reverse-logistics`),
scientific (`ecc:scientific-*`, `ecc:boltz`-adjacent), video/media (`ecc:remotion-video-creation`,
`ecc:manim-video`, `ecc:tasteforge-video`, `ecc:videodb`).

**This is a genuine advantage:** whichever industry the founder names, there is a decent chance a
relevant vertical skill already exists. Re-check this list at industry-selection time.
