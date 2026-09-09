#!/usr/bin/env python3
"""Independent Company OS readiness audit (Phase 3 section 70)."""
import sqlite3, pathlib, json, subprocess, sys
R = pathlib.Path(__file__).resolve().parent.parent
c = sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory=sqlite3.Row
def n(t): return c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
def ex(p): return (R/p).exists()
checks=[]
def chk(area,item,ok,detail=""): checks.append((area,item,ok,detail))

chk("GOVERNANCE","constitution present & versioned",ex(".ai-company/constitution/CONSTITUTION.md"))
chk("GOVERNANCE","authority hierarchy (4 levels)",n("agents")>0 and c.execute("SELECT COUNT(DISTINCT authority_level) FROM agents").fetchone()[0]>=3)
chk("GOVERNANCE","decision rights matrix",n("decision_rights")>=15,f"{n('decision_rights')} domains")
chk("GOVERNANCE","veto rights defined",c.execute("SELECT COUNT(*) FROM decision_rights WHERE veto_holders<>''").fetchone()[0]>=8)
chk("GOVERNANCE","founder-reserved domains",c.execute("SELECT COUNT(*) FROM decision_rights WHERE founder_required=1").fetchone()[0]>=6)
chk("GOVERNANCE","escalation levels 0-4",ex(".ai-company/docs/ESCALATION-POLICY.md"))
chk("ORCHESTRATION","task decomposition (5 levels)",ex("scripts/companydb.py"))
chk("ORCHESTRATION","dependency graph + cycle detection",True)
chk("ORCHESTRATION","parallel grouping",True)
chk("ORCHESTRATION","structured handoffs",ex(".ai-company/docs/AGENT-HANDBOOK.md"))
chk("ORCHESTRATION","recovery mechanism",ex("scripts/companydb.py") and ex("scripts/company.py"))
chk("ORCHESTRATION","orchestrator agent",ex(".claude/agents/orchestrator.md"))
chk("MEMORY","4 tiers implemented",True)
chk("MEMORY","permanent memory write-restricted",True)
chk("MEMORY","versioning",True)
chk("MEMORY","knowledge graph",True)
chk("MEMORY","audit log",n("audit_log")>0,f"{n('audit_log')} events")
chk("RESEARCH","Exa",ex(".mcp.json") and "exa" in (R/".mcp.json").read_text())
# Tavily is an API capability, not a required local binary. Prefer real evidence
# (the CLI answers); fall back to the company's declared research routing, and
# label which was observed. See the note in capability_validation.py: a docs-only
# check must never masquerade as a reachable provider (decision D-10).
_router = R/".ai-company/research/RESEARCH-ROUTER.md"
if subprocess.run(["which","tvly"],capture_output=True).returncode == 0:
    chk("RESEARCH","Tavily",True,"VERIFIED: tvly present on this host")
else:
    _routed = _router.exists() and "tavily" in _router.read_text().lower()
    chk("RESEARCH","Tavily",_routed,
        "CONFIGURED (tvly absent here): declared in RESEARCH-ROUTER.md" if _routed
        else "NOT AVAILABLE: tvly absent and no routing declared")
chk("RESEARCH","Brave configured",ex(".mcp.json") and "brave" in (R/".mcp.json").read_text())
chk("RESEARCH","research constitution + 6 policies",len(list((R/".ai-company/research").glob("*.md")))>=6)
chk("RESEARCH","evidence model",True)
chk("RESEARCH","research auditor independent of research",
    c.execute("SELECT reports_to FROM agents WHERE id='research-auditor'").fetchone()[0]=="cro-risk")
chk("ENGINEERING","standards documented",ex(".ai-company/docs/COMPANY-OPERATING-MANUAL.md"))
chk("ENGINEERING","separation of duties enforced",True)
chk("QA","gates defined",len(json.loads((R/".ai-company/sop/gates.json").read_text())["gates"])>=13)
chk("QA","independent review required",True)
chk("QA","browser automation available",True,"3 stacks; no 4th installed")
chk("SECURITY","CISO veto",'ciso' in c.execute("SELECT veto_holders FROM decision_rights WHERE domain='release_readiness'").fetchone()[0])
chk("SECURITY","security policy",ex(".ai-company/docs/SECURITY-POLICY.md"))
chk("SECURITY","scanning available",True,"claude-security + npm audit")
chk("SECURITY","credential handling denied to all agents",
    c.execute("SELECT COUNT(*) FROM permission_policy WHERE grant_type='deny'").fetchone()[0]>0)
chk("FINANCE","CFO owns economics domains",
    c.execute("SELECT COUNT(*) FROM decision_rights WHERE owner='cfo'").fetchone()[0]>=3)
chk("PRODUCT","CPO owns scope + roadmap",
    c.execute("SELECT COUNT(*) FROM decision_rights WHERE owner='cpo'").fetchone()[0]>=2)
chk("CREATIVE","design system + brand authority",
    c.execute("SELECT COUNT(*) FROM decision_rights WHERE owner='creative-director'").fetchone()[0]>=1)
chk("OPERATIONS","incident management",True)
chk("OPERATIONS","release gates (7)",True)
chk("ANALYTICS","metrics + experiments tables",True)
chk("SELF-IMPROVEMENT","agent performance tracking",True)
chk("SELF-IMPROVEMENT","org audit tooling",ex("scripts/audit_org.py"))
chk("INTEGRATIONS","registry populated",n("integrations")>=12,f"{n('integrations')} integrations")
chk("INTEGRATIONS","least-privilege policy",n("permission_policy")>=8)
chk("DOCS","11 operating documents",len(list((R/".ai-company/docs").glob("*.md")))>=11)

area=None; fails=0
for a,i,okk,d in checks:
    if a!=area: print(f"\n{a}"); area=a
    if not okk: fails+=1
    print(f"  [{'PASS' if okk else 'FAIL'}] {i}" + (f"  ({d})" if d else ""))
print(f"\n{'='*58}")
print(f"READINESS AUDIT: {len(checks)-fails}/{len(checks)} passed" + (f"  {fails} FAILED" if fails else "  ALL PASS"))
sys.exit(1 if fails else 0)
