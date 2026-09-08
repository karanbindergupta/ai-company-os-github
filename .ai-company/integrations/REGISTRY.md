---
document: integration-registry
version: 1.0.0
source: generated from the company database
---
# INTEGRATION REGISTRY

15 integrations. **No agent may reach a tool its role family is not granted.**

| Integration | Purpose | Credentials | Agents allowed | Class | Status |
|---|---|---|---|---|---|
| `github` | Source control, PRs, issues, code review | GITHUB_PERSONAL_ACCESS_TOKEN (set) | engineer,release-manager,code-reviewer,ops-l | restricted | active |
| `adobe-express` | Design authoring, image editing, fonts, video | account connector | designer,creative-lead,visual-designer | internal | active |
| `brave-search` | Independent web index for cross-verification | BRAVE_API_KEY (NOT SET) | research-director,evidence-verifier | internal | dormant |
| `chrome-devtools` | Performance tracing, Lighthouse, heap snapshots | none | performance-engineer,performance-tester | internal | active |
| `claude-browser` | Isolated browser for QA and research | none | qa-lead,e2e-tester,designer,researcher | internal | active |
| `claude-security` | Deep vulnerability scanning, adversarially verified | none | security-lead,appsec-engineer,ciso | internal | active |
| `cloudinary` | Asset management and image generation | account connector | designer,visual-designer,creative-lead | internal | active |
| `exa` | Deep semantic research and high-signal source discovery | none - anonymous tier (~150 calls/day) | research-director,researcher,evidence-verifi | internal | active |
| `miro` | Boards, diagrams, strategy artifacts | account connector | cso,creative-lead,product-lead | internal | active |
| `npm-audit` | Node dependency vulnerability scanning | none | dependency-auditor,security-lead | internal | active |
| `tavily` | Search, extraction, crawling, multi-page research | none - keyless tier | research-director,researcher,evidence-verifi | internal | active |
| `v0` | UI generation and preview | account connector | designer,frontend-lead | internal | active |
| `websearch-native` | Guaranteed research floor | none | all | internal | active |
| `supabase` | Postgres, migrations, edge functions | account connector | database-architect,data-engineer,backend-lea | SENSITIVE - production capable | active |
| `claude-in-chrome` | Real Chrome with the founder's live logins | founder's browser session | (none by default) | SENSITIVE - high blast radius | restricted |

## Sensitive - confirmation required

| Integration | Why |
|---|---|
| `supabase` | `execute_sql`, `apply_migration`, `deploy_edge_function` are production-capable |
| `claude-in-chrome` | Acts as the signed-in founder; a hostile page reaches live sessions |
| `github` (write) | Pushes commits, PRs and issues on the founder's account |
| `cloudinary` (delete) | Destructive on founder-owned media |

## Tool permission policy - least privilege

| Role family | Tools | Grant |
|---|---|---|
| `researcher_family` | WebSearch,WebFetch,exa,tavily,brave-search | **allow** |
| `engineer_family` | Bash,Read,Write,Edit,Grep,Glob,github | **allow** |
| `qa_family` | Bash,Read,Grep,Glob,claude-browser,chrome-devtools | **allow** |
| `security_family` | Bash,Read,Grep,Glob,claude-security,npm-audit | **allow** |
| `design_family` | Read,Write,Edit,adobe-express,cloudinary,v0,miro | **allow** |
| `finance_family` | Read,Write,Edit,WebSearch,WebFetch | **allow** |
| `release_family` | Bash,Read,github | **confirm** |
| `ALL` | supabase:execute_sql,supabase:apply_migration,supabase:deploy_edge_function | **confirm** |
| `ALL` | claude-in-chrome,production-deploy,publish,purchase,send | **confirm** |
| `ALL` | credential-handling | **deny** |

`deny` on `credential-handling` is absolute: **no agent ever handles a secret.**

## Deliberately not installed

| Rejected | Reason |
|---|---|
| Perplexity | Founder instruction; the three-engine stack covers the need |
| Playwright | Three browser stacks already exist |
| Firecrawl / Nimble | Overlap Tavily's crawl and extract |
| npm `tavily-cli` | Third-party publisher, not Tavily - impostor risk |
| Semgrep, Gitleaks, Trivy | Blocked on Homebrew; `claude-security` + `npm audit` cover the stack |
