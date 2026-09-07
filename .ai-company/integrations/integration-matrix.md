---
document: integration-matrix
version: 1.0.0
source: generated from the company database
---
# INTEGRATION MATRIX

15 integrations. Least privilege — no agent reaches a tool its family is not granted.

| Integration | Capability | Agents | Credentials | Cost | Rate limit | Fallback | Security | Status | Health |
|---|---|---|---|---|---|---|---|---|---|
| `github` | repos,branches,commits,PRs,issues, | engineer,release-manager,code- | GITHUB_PERSONAL_ACCESS_TOK | free | 5,000 req/hr authenticated | local git | restricted | active | VERIFIED (get_me) |
| `adobe-express` | design,image ops,fonts,video,PDF | designer,creative-lead,visual- | account connector | account entitlement | — | cloudinary | internal | active | not exercised |
| `brave-search` | web,news,images,video | research-director,evidence-ver | BRAVE_API_KEY (NOT SET) | $5 / 1,000 requests [Tier 1, verified] | 50 QPS (Search plan) | exa + tavily as the tw | internal | dormant | DORMANT — no key |
| `chrome-devtools` | traces,lighthouse,network,console | performance-engineer,performan | none | free | — | claude-browser | internal | active | not exercised |
| `claude-browser` | navigate,a11y tree,console,network | qa-lead,e2e-tester,designer,re | none | free | — | chrome-devtools | internal | active | not exercised |
| `claude-security` | scan,threat-model,patch-generation | security-lead,appsec-engineer, | none | token cost only | — | npm audit, manual revi | internal | active | installed, unexercised |
| `cloudinary` | upload,transform,tag,generate,dele | designer,visual-designer,creat | account connector | account plan | — | adobe-express | internal | active | not exercised |
| `exa` | web_search_exa,web_fetch_exa | research-director,researcher,e | none - anonymous tier (~15 | free (anonymous tier) | ~3 QPS, ~150 calls/day | tavily, WebSearch | internal | active | VERIFIED live |
| `miro` | boards,docs,diagrams,tables | cso,creative-lead,product-lead | account connector | account plan | — | markdown + mermaid | internal | active | not exercised |
| `npm-audit` | audit | dependency-auditor,security-le | none | free | — | claude-security | internal | active | VERIFIED (caught GHSA-vh95-rmgr-6w4m) |
| `tavily` | search,extract,map,crawl,research | research-director,researcher,e | none - keyless tier | free (keyless tier) | capped keyless quota | exa, WebFetch | internal | active | VERIFIED live |
| `v0` | chat,preview | designer,frontend-lead | account connector | account plan | — | manual design | internal | active | not exercised |
| `websearch-native` | search,fetch | all | none | included | — | none needed | internal | active | VERIFIED live |
| `supabase` | execute_sql,apply_migration,deploy | database-architect,data-engine | account connector | per project | project limits | local sqlite for dev | SENSITIVE - production capable | active | not exercised |
| `claude-in-chrome` | full browser as the signed-in user | (none by default) | founder's browser session | free | — | claude-browser | SENSITIVE - high blast radius | restricted | not exercised |

## Permission policy

| Family | Tools | Grant |
|---|---|---|
| `ALL` | claude-in-chrome,production-deploy,publish,purchase,send | **confirm** |
| `ALL` | credential-handling | **deny** |
| `ALL` | supabase:execute_sql,supabase:apply_migration,supabase:deploy_edge_function | **confirm** |
| `design_family` | Read,Write,Edit,adobe-express,cloudinary,v0,miro | **allow** |
| `engineer_family` | Bash,Read,Write,Edit,Grep,Glob,github | **allow** |
| `finance_family` | Read,Write,Edit,WebSearch,WebFetch | **allow** |
| `qa_family` | Bash,Read,Grep,Glob,claude-browser,chrome-devtools | **allow** |
| `release_family` | Bash,Read,github | **confirm** |
| `researcher_family` | WebSearch,WebFetch,exa,tavily,brave-search | **allow** |
| `security_family` | Bash,Read,Grep,Glob,claude-security,npm-audit | **allow** |

`credential-handling` is **deny for every agent, without exception.**

## Nothing new was installed for this layer
Every integration above predates the Professional Capability Layer. Section 43 forbids adding
capability for appearance; the gap analysis found the integration layer COMPLETE.
