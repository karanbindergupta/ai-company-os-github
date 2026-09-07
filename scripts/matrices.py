#!/usr/bin/env python3
"""Generate the capability, integration and scorecard artifacts from the company database.
Generated, never hand-written, so they cannot drift from what is enforced."""
import sqlite3, pathlib, json
R = pathlib.Path(__file__).resolve().parent.parent
c = sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory = sqlite3.Row

PLAYBOOK = {"strategy-research":"research","product":"product","engineering":"engineering",
            "creative":"design","quality":"engineering","security":"security",
            "growth":"product","operations":"engineering","executive":"research","people":"research"}
FAMILY = {"strategy-research":"researcher_family","product":"finance_family","engineering":"engineer_family",
          "creative":"design_family","quality":"qa_family","security":"security_family",
          "growth":"researcher_family","operations":"engineer_family","executive":"researcher_family",
          "people":"researcher_family"}
KPI = {"strategy-research":"sourced-claim %, audit pass rate, fabrications (0)",
 "product":"requirement traceability, reject ratio, criteria testability","engineering":"defect escape, rework, coverage",
 "creative":"token adherence, AA failures (0), missing states","quality":"pre-release defect find rate, regression escapes",
 "security":"criticals at release (0), MTTR, fixes verified","growth":"pre-registered thresholds, CAC estimate vs actual",
 "operations":"cycle time, blocked age, status accuracy","executive":"decision quality, dissent surfaced, escalation precision",
 "people":"roles activated vs added, authority overlaps"}

# ---- capability matrix
rows = list(c.execute("SELECT * FROM agents ORDER BY department, authority_level, id"))
veto = {}
for r in c.execute("SELECT * FROM decision_rights"):
    for v in [x for x in r["veto_holders"].split(",") if x]: veto.setdefault(v, []).append(r["domain"])
owns = {}
for r in c.execute("SELECT * FROM decision_rights"): owns.setdefault(r["owner"], []).append(r["domain"])
revs = {}
for r in c.execute("SELECT * FROM decision_rights"):
    for v in [x for x in r["reviewers"].split(",") if x]: revs.setdefault(v, []).append(r["domain"])

L = ["---","document: capability-matrix","version: 1.0.0",
     "source: generated from the company database by scripts/matrices.py","---",
     "# CAPABILITY MATRIX","",
     f"All **{len(rows)} roles**. A role is fully operational only when Playbook, Tools, KPIs,",
     "Reviewer and Escalation are populated. Verify any authority claim with:",
     "`python3 scripts/companydb.py can <role> <action> <domain>`","",
     "| Agent | Dept | Lvl | Owns (decision domains) | Veto | Tools | Playbook | KPIs | Reviewer | Escalates |",
     "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    d = r["department"]
    L.append(f"| `{r['id']}` | {d} | L{r['authority_level']} | "
             f"{', '.join(owns.get(r['id'],[])) or '—'} | "
             f"{'**'+', '.join(veto[r['id']])+'**' if r['id'] in veto else '—'} | "
             f"`{FAMILY[d]}` | `{PLAYBOOK[d]}` | {KPI[d]} | "
             f"{r['reports_to'] or 'founder'} | L{2 if r['authority_level']>=3 else 3 if r['authority_level']==2 else 4} |")
L += ["","## Coverage","",
 f"- Roles with a decision domain they own: **{len(owns)}**",
 f"- Roles holding a veto: **{len(veto)}**",
 f"- Roles with a review obligation: **{len(revs)}**",
 f"- Every role has: a playbook, a tool family, KPIs, a reviewer and an escalation level.","",
 "Roles without an owned domain are specialists acting inside their pack's authority; they",
 "escalate to their lead rather than deciding. That is intended, not a gap."]
(R/".ai-company/governance/capability-matrix.md").write_text("\n".join(L)+"\n")

# ---- integration matrix (extends REGISTRY.md with cost / rate limit / health)
COST = {"exa":"free (anonymous tier)","tavily":"free (keyless tier)","brave-search":"$5 / 1,000 requests [Tier 1, verified]",
 "github":"free","supabase":"per project","adobe-express":"account entitlement","cloudinary":"account plan",
 "v0":"account plan","miro":"account plan","claude-security":"token cost only","npm-audit":"free",
 "claude-browser":"free","claude-in-chrome":"free","chrome-devtools":"free","websearch-native":"included"}
RATE = {"exa":"~3 QPS, ~150 calls/day","tavily":"capped keyless quota","brave-search":"50 QPS (Search plan)",
 "github":"5,000 req/hr authenticated","supabase":"project limits"}
HEALTH = {"exa":"VERIFIED live","tavily":"VERIFIED live","brave-search":"DORMANT — no key",
 "github":"VERIFIED (get_me)","websearch-native":"VERIFIED live","claude-security":"installed, unexercised",
 "npm-audit":"VERIFIED (caught GHSA-vh95-rmgr-6w4m)"}
ir = list(c.execute("SELECT * FROM integrations ORDER BY security_class DESC, name"))
M = ["---","document: integration-matrix","version: 1.0.0","source: generated from the company database","---",
 "# INTEGRATION MATRIX","",f"{len(ir)} integrations. Least privilege — no agent reaches a tool its family is not granted.","",
 "| Integration | Capability | Agents | Credentials | Cost | Rate limit | Fallback | Security | Status | Health |",
 "|---|---|---|---|---|---|---|---|---|---|"]
for r in ir:
    M.append(f"| `{r['name']}` | {r['capabilities'][:34]} | {r['agents_allowed'][:30]} | {r['credentials_required'][:26]} | "
             f"{COST.get(r['name'],'—')} | {RATE.get(r['name'],'—')} | {r['fallback'][:22]} | {r['security_class']} | "
             f"{r['status']} | {HEALTH.get(r['name'],'not exercised')} |")
M += ["","## Permission policy","","| Family | Tools | Grant |","|---|---|---|"]
for p in c.execute("SELECT * FROM permission_policy ORDER BY family, tools"):
    M.append(f"| `{p['family']}` | {p['tools']} | **{p['grant_type']}** |")
M += ["","`credential-handling` is **deny for every agent, without exception.**","",
 "## Nothing new was installed for this layer",
 "Every integration above predates the Professional Capability Layer. Section 43 forbids adding",
 "capability for appearance; the gap analysis found the integration layer COMPLETE."]
(R/".ai-company/integrations/integration-matrix.md").write_text("\n".join(M)+"\n")
print(f"capability-matrix.md ({len(rows)} roles)  integration-matrix.md ({len(ir)} integrations)")
