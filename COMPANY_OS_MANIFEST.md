# COMPANY OS MANIFEST

**Snapshot date:** 2026-09-08 · **Source:** a live AI Company OS deployment, packaged for reuse.
This manifest is the honest account of what is in the repository, what was removed, what actually
runs, and what does not.

---

## INCLUDED — Company OS subsystems

| Subsystem | Location | Contents |
|---|---|---|
| Constitution & governance | `.ai-company/constitution/`, `governance/` | Constitution v1.1.0, authority matrix, capability matrix, benchmarking, model routing |
| Organization | `.ai-company/org/` | 119 role packs, employee directory, hierarchy, org chart, roster, staffing matrix, `roles.json` |
| Executive council | `.ai-company/org/roles/executive/` + `.claude/agents/` | CEO, COO, CTO, CFO, CPO, CMO, CSO, CRO-Research, CRO-Risk, CISO, Creative Director, Managing Director, Chief People Officer |
| Departments | `.ai-company/org/roles/<dept>/` | Executive 14 · Strategy & Research 19 · Engineering 21 · Creative 13 · Product 10 · Quality 10 · Growth 10 · Security 8 · Operations 7 · People 5 · Commercial 2 |
| Authority & permissions | `companydb.py` + `decision_rights`, `permission_policy` | 29 decision rights, 10 permission policies, vetoes, founder-required domains, separation of duties |
| Cognition architecture | `.ai-company/cognition/`, `agents` table | Profile schema, executive personality matrix, specialist matrix, interaction matrix, 119 profiles |
| Personality / behavioural contracts | `behavioral_contracts` table, `.ai-company/behavior/contracts/` | 119 contracts: communication, debate, pressure, failure, quality bar, unacceptable output, escalation |
| Intelligence layer | `scripts/intelligence.py`, `.ai-company/intelligence/` | Evaluations, maturity model L1–L5, capability probing, provider provenance, drift |
| Research infrastructure | `.ai-company/research/` | Research constitution, evidence standard, source hierarchy, freshness policy, router, audit protocol |
| Knowledge & memory | `.ai-company/knowledge/`, `memory/`, `docs/MEMORY-POLICY.md` | Working / long-term / permanent memory structure, lessons |
| Decision systems | `.ai-company/decisions/`, `docs/DECISION-PROTOCOL.md` | Decision records, escalation policy, decision packages |
| Database | `.ai-company/state/company.db`, `schema.sql` | **53 tables**, full DDL, reusable data only |
| SOP & orchestration | `.ai-company/sop/`, `scripts/company.py`, `.claude/agents/orchestrator.md` | 23 phases, 13 gates, task graph, resumability |
| Playbooks | `.ai-company/playbooks/` | 29 files: executive, growth, operations, people, sales, research, product, engineering, design, finance, security |
| Workforce mechanism | `scripts/workforce.py` | Assignment, org health, team formation, SPOF detection, retirement |
| Behavioural conditioning | `scripts/behavior.py`, `.ai-company/behavior/` | 11 drills, automated rubrics, coaching, regression detection, drill catalogue |
| Validation infrastructure | `scripts/*_validation.py`, `*_audit.py`, `behavior_tests.py` | 115 automated checks across 4 suites plus 2 audits |
| CI | `.github/workflows/ci.yml`, `scripts/ci_report.py` | 9 gates, machine-readable JSON output |
| Security | `.ai-company/docs/SECURITY-POLICY.md`, `scripts/secret_scan.sh` | Credential prohibition, red-team boundaries, secret scanning |
| Integrations | `.ai-company/integrations/`, `integrations` table | 15 integrations, registry, matrix — **names and env-var names only** |
| Templates | `.ai-company/templates/` | 28 deliverable templates |
| Documentation | `CLAUDE.md`, `README.md`, `.ai-company/docs/` | Master operating document + 12 operating manuals |
| Claude Code surface | `.claude/` | 19 subagents, 28 commands, 9 skills, session hook, project settings |
| Config templates | `.env.example`, `.ai-company/org/FOUNDER.example.md`, `.mcp.json` | Placeholders only |

---

## EXCLUDED — and why

### Active project / mission work
| Removed | Reason |
|---|---|
| `.ai-company/mission/charter.md`, `intake.md` | Live mission charter for a specific industry |
| `.ai-company/decisions/founder/*.md` | Founder decisions about a specific market position |
| `.ai-company/research/industry.md`, `competitors.md`, `customers.md`, `sources/index.md` | Market research for a specific mission |
| `.ai-company/knowledge/lessons-learned/*.md` | A lesson tied to a named competitor and market |
| `.ai-company/product/assumptions.md`, `discovery.md` | Product discovery for a specific product idea |
| `CURRENT_STATE.md` | Mission status of the source deployment |
| `.ai-company/state/run.json`, `tasks.json`, `archive/` | Live run state and prior mission archives |
| `.ai-company/logs/events.jsonl` | Runtime event log of the source deployment |
| **`.claude/worktrees/`** | **A separate git worktree containing a second, more advanced branch of active product work** — see WARNINGS |

Directory structure is preserved (`.gitkeep`) so a new mission has somewhere to write.

### Runtime and environment state
`capability_readiness` (17 rows — contained a machine-local filesystem path) · `audit_log` (79) ·
`ci_runs` (9) · `provider_usage` (7, mission-linked) · `escalations` (2, mission) ·
`risks` (4, mission) · `environment_changes` (1) · `ci-results.json` · `*.db-wal` / `*.db-shm`.

### Personal identity — redacted, not just excluded
| Where | What | Replacement |
|---|---|---|
| `.ai-company/tooling/SETUP-BLOCKERS.md` | Founder's personal email address | `you@example.com` |
| `.ai-company/tooling/TOOLING-INVENTORY.md` | Absolute home-directory path | `<REPO_ROOT>` |
| `TOOLING-INVENTORY.md`, `SETUP-BLOCKERS.md`, `CAPABILITY-MATRIX.md`, `CLAUDE.md` | GitHub username, account id, company handle | `<GITHUB_USER>`, redacted |
| `scripts/intelligence.py` | Hard-coded evidence strings asserting this machine's verified state | Live-probe results |

### Git history
Not carried over. The source history interleaves OS construction with mission commits. This
snapshot begins with a single clean initial commit.

---

## IMPLEMENTED — verified to execute

- Authority enforcement (`companydb.py can`) — exit 0 allowed / 2 denied
- Separation of duties — DB CHECK constraint `owner <> COALESCE(reviewer,'~')`
- SOP phase machine — refuses on missing artifacts, unpassed gate, or open tasks
- Task lifecycle with evidence, acceptance verification and independent review
- Escalation ladder L0→L4; level 4 refuses without a recommendation
- Workforce assignment, org health, team formation, SPOF detection
- Cognitive profiles, panels with anti-anchoring, blind-spot gap detection
- Drill engine with automated, sentence-scoped, negation-aware rubrics
- Coaching and behavioural regression detection
- Capability probing with live checks; provider provenance guard
- Maturity model — refuses to promote without evidence
- Registry sync, memory generation, matrices, agent scorecards
- Secret scanning
- Local CI — 9 gates, machine-readable output
- 115 automated validation checks

## PARTIALLY IMPLEMENTED

| Feature | State |
|---|---|
| **CI as a trusted gate** | Workflow executes locally and persists results. `trusted_as_gate = 0` — never observed on GitHub Actions |
| **Behavioural evidence** | 11 drills, 22 runs, but only **9 of 119 agents** have been drilled |
| **Maturity levels** | Model works and refuses unearned promotion; **zero agents at L5** because no real work has been validated |
| **Evaluations** | 2 recorded, 4 dimensions defined; `confidence_for(n)` correctly returns INSUFFICIENT EVIDENCE at n=1 |
| **`claude-security` SAST** | Available but never exercised — nothing to scan until a product exists |
| **Cognitive panels** | `cognition.py panel` implemented; `cognitive_panels` table ships empty |

## CONCEPTUAL — specified, not implemented

| Item | Where specified | Reality |
|---|---|---|
| Observability (logs, metrics, traces, errors) | `capability_readiness` categories | `NOT_CONFIGURED` / GRAY — deliberately deferred; no product to instrument |
| Static analysis & container scanning | same | `NOT_CONFIGURED` — deliberately deferred |
| `demonstrations`, `development_plans`, `knowledge_edges`, `team_formations`, `behavioral_baselines`, `drift_observations`, `profile_changes`, `sops`, `experiments`, `metrics`, `bugs`, `releases`, `incidents`, `memory` tables | Schema | Tables exist with working interfaces; **no rows** — these fill during real operation |
| Three staffing roles | `staffing_audit.py` | `security-analyst`, `sales-lead`, `executive-operations` — flagged, deliberately unfilled |
| Product/engineering/QA/design output directories | `.ai-company/*` | Structure only. This OS has never shipped a product |

---

## VALIDATION — results from this snapshot

Run inside the snapshot on 2026-09-08, Python 3.9.6, macOS.

| Suite | Result |
|---|---|
| `readiness_audit.py` | **43/43 PASS** |
| `cognitive_validation.py` | **23/23 PASS** |
| `capability_validation.py` | **14/14 PASS** |
| `audit_org.py` | **0 findings** |
| `staffing_audit.py` | **0 orphans · 0 shadow agents · 0 circular reporting**; 3 known gaps reported |
| `workforce.py health` | **0 single points of failure** — every critical role has a named backup |
| `secret_scan.sh` | **clean** |
| `sqlite3 PRAGMA integrity_check` | **ok** |
| `behavior_tests.py` (as shipped) | **24/35** — 11 fail because `capability_readiness` and `ci_runs` ship empty |
| `behavior_tests.py` (after bootstrap) | **34/35** — verified in a scratch copy after `intelligence.py capability` + `ci_report.py` |

**The one permanent failure:** test 33, *"unavailable provider triggers fallback"*, requires a
real research call that falls back from one provider to another. It cannot pass until the company
does actual research. This is correct behaviour, not a defect — the test refuses to pass on
configuration alone.

**No result above was fabricated.** Re-run any of them.

---

## EXTERNAL DEPENDENCIES — configure after cloning

| Dependency | Required? | Notes |
|---|---|---|
| Python 3.9+ | **Yes** | Standard library only. No packages to install |
| git | **Yes** | |
| Claude Code | **Yes**, to run agents | The scripts run standalone; the organization needs Claude Code |
| `npm` | No | Dependency auditing only |
| `uv` | No | For the Tavily CLI |
| Exa MCP | No | Anonymous tier needs no credential |
| Tavily | No | Keyless tier |
| Brave Search | No | Needs `BRAVE_API_KEY` |
| GitHub MCP | No | Needs a fine-grained PAT; *Administration* permission to create repos |
| Supabase | No | Only if the company builds an application |

## ENVIRONMENT VARIABLES — names only

`EXA_API_KEY` · `TAVILY_API_KEY` · `BRAVE_API_KEY` · `GITHUB_PERSONAL_ACCESS_TOKEN` ·
`MODEL_API_KEY` · `ANTHROPIC_API_KEY` · `COMPANY_DATABASE_URL` · `SUPABASE_URL` ·
`SUPABASE_SERVICE_ROLE_KEY`

All optional. See `.env.example`. **No values appear anywhere in this repository.**

---

## KNOWN LIMITATIONS

1. **110 of 119 agents are behaviourally untested.** Treat their conduct as unproven.
2. **No agent has completed real outcome-validated work.** Zero at maturity L5.
3. **All drill evidence is synthetic** — responses scored by rubric, not live subagent runs.
4. **CI has never run remotely.** Do not report CI status until you observe a real run.
5. **`capability_readiness` and `ci_runs` ship empty.** Bootstrap before relying on either.
6. **`.ai-company/tooling/` describes the source machine**, not yours. Historical reference only.
7. **`.ai-company/audits/organization.md`** contains one descriptive clause naming the throwaway
   test scenario used to validate the org. Left in as validation provenance; it is not product work.
8. **Python 3.9 baseline.** Type-hint syntax is 3.9-compatible; do not assume 3.10+ features.
9. **`schema.sql` was regenerated** from the live database during packaging. The committed copy in
   the source repository was stale (27 of 53 tables) because later layers create tables in Python.
10. **This OS has never shipped a product.** Everything is validated against itself.
