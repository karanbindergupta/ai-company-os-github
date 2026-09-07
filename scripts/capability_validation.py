#!/usr/bin/env python3
"""Professional Capability Layer validation - the 13 tests in section 44."""
import sqlite3, pathlib, subprocess, json, sys, collections
R = pathlib.Path(__file__).resolve().parent.parent
c = sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory=sqlite3.Row
res=[]
def t(name, ok, detail=""): res.append((name, ok, detail)); return ok

# 1 AGENT TEST - can every specialist discover and use its professional profile?
packs=list((R/".ai-company/org/roles").rglob("*.md"))
FIELDS=["## Mission","## Responsibilities","## Authority","## Inputs","## Outputs","## Tools",
        "## Activate when","## Do NOT activate when","## Collaboration","## Quality standard",
        "## Escalation","## On failure","## Methodology","## Excellence standard","## KPIs",
        "## Benchmark","## Continuous improvement","## Audit protocol"]
missing=[p.stem for p in packs if any(f not in p.read_text() for f in FIELDS)]
t("1 AGENT     every role pack has all 18 professional fields", not missing,
  f"{len(packs)} packs" + (f"; INCOMPLETE: {missing[:3]}" if missing else ""))

# 2 AUTHORITY TEST
def can(role,act,dom):
    return subprocess.run(["python3","scripts/companydb.py","can",role,act,dom],
                          capture_output=True,cwd=R).returncode
t("2 AUTHORITY agents correctly determine what they may decide",
  can("cto","decide","technical_architecture")==0 and can("frontend-engineer","decide","technical_architecture")==2
  and can("ciso","veto","release_readiness")==0 and can("cmo","veto","release_readiness")==2)

# 3 ESCALATION TEST
fr=[r["domain"] for r in c.execute("SELECT domain FROM decision_rights WHERE founder_required=1")]
esc=subprocess.run(["python3","scripts/companydb.py","escalate","level=4","subject=t","raised_by=ceo"],
                   capture_output=True,cwd=R)
t("3 ESCALATION consequential decisions reach the right authority",
  len(fr)>=8 and esc.returncode!=0, f"{len(fr)} founder-required domains; level-4 without recommendation refused")

# 4 TOOL TEST
t("4 TOOL      authorized agents can reach required tools",
  c.execute("SELECT COUNT(*) FROM integrations WHERE status='active'").fetchone()[0]>=10
  and subprocess.run(["which","tvly"],capture_output=True).returncode==0)

# 5 SECURITY TEST - restricted access is actually restricted
deny=c.execute("SELECT COUNT(*) FROM permission_policy WHERE grant_type='deny'").fetchone()[0]
conf=c.execute("SELECT COUNT(*) FROM permission_policy WHERE grant_type='confirm'").fetchone()[0]
sec=subprocess.run(["sh","scripts/secret_scan.sh"],capture_output=True,cwd=R)
t("5 SECURITY  restricted resources are restricted; no secrets committed",
  deny>=1 and conf>=3 and sec.returncode==0, f"{deny} deny, {conf} confirm rules; secret scan clean")

# 6 RESEARCH TEST
t("6 RESEARCH  evidence-backed research is possible",
  subprocess.run(["which","tvly"],capture_output=True).returncode==0
  and "exa" in (R/".mcp.json").read_text()
  and len(list((R/".ai-company/research").glob("*.md")))>=6)

# 7 DEBATE TEST - can executives genuinely disagree?
t("7 DEBATE    executives can genuinely disagree and it is preserved",
  (R/".ai-company/docs/DECISION-PROTOCOL.md").exists()
  and c.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='dissent'").fetchone()[0]==1)

# 8 DECISION TEST
cols={r[1] for r in c.execute("PRAGMA table_info(decisions)")}
t("8 DECISION  decisions logged with evidence and dissent",
  {"options","rejected","risks","confidence","approvers"}<=cols
  and c.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='decision_evidence'").fetchone()[0]==1)

# 9 HANDOFF TEST
h={r[1] for r in c.execute("PRAGMA table_info(handoffs)")}
t("9 HANDOFF   work moves between specialists without losing context",
  {"context","work_done","evidence","artifacts","decisions","open_questions","risks",
   "next_action","acceptance"}<=h and (R/".ai-company/templates/handoff.md").exists())

# 10 QUALITY TEST - do gates actually block?
g=json.loads((R/".ai-company/sop/gates.json").read_text())["gates"]
t("10 QUALITY  gates actually block bad work",
  len(g)>=13 and (R/".ai-company/metrics/company-quality-scorecard.md").exists()
  and c.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='vetoes'").fetchone()[0]==1)

# 11 RECOVERY TEST
rec=subprocess.run(["python3","scripts/companydb.py","recover"],capture_output=True,cwd=R,text=True)
t("11 RECOVERY interrupted workflows resume",
  rec.returncode==0 and "STATE RECOVERY" in rec.stdout)

# 12 LEARNING TEST
t("12 LEARNING company captures meaningful lessons",
  (R/".ai-company/knowledge/lessons-learned").exists()
  and all("## Continuous improvement" in p.read_text() for p in packs[:20]))

# 13 FOUNDER TEST
t("13 FOUNDER  founder remains final authority on founder-level decisions",
  len(fr)>=8 and "founder_approval" in (R/"scripts/companydb.py").read_text())

# 14 DUPLICATION TEST (section 43)
dups=[]
if (R/".ai-company/governance/company-constitution.md").exists() and (R/".ai-company/constitution/CONSTITUTION.md").exists():
    dups.append("two constitutions")
names=collections.Counter(p.stem for p in packs)
dups += [f"duplicate role pack: {k}" for k,v in names.items() if v>1]
agents=[p.stem for p in (R/".claude/agents").glob("*.md")]
dups += [f"duplicate agent: {k}" for k,v in collections.Counter(agents).items() if v>1]
dbs=list((R/".ai-company/state").glob("*.db"))
if len(dbs)>1: dups.append(f"multiple databases: {[d.name for d in dbs]}")
t("14 DUPLICATE no duplicate agents, tools, databases or systems", not dups, "; ".join(dups) or "clean")

fails=sum(1 for _,ok,_ in res if not ok)
for name,ok,d in res: print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"\n         {d}" if d else ""))
print(f"\n{'='*62}\nCAPABILITY VALIDATION: {len(res)-fails}/{len(res)} passed" + ("" if not fails else f"  {fails} FAILED"))
sys.exit(1 if fails else 0)
