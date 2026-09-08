#!/usr/bin/env python3
"""Workforce staffing audit: LONE_EXECUTIVE / ORPHAN_AGENT / SHADOW_AGENT detection."""
import sqlite3, pathlib, json, collections, sys
R=pathlib.Path(__file__).resolve().parent.parent
c=sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory=sqlite3.Row
agents={r["id"]:r for r in c.execute("SELECT * FROM agents WHERE status='active'")}
reports=collections.defaultdict(list)
for a in agents.values():
    if a["reports_to"]: reports[a["reports_to"]].append(a["id"])
owns=collections.defaultdict(list)
for r in c.execute("SELECT * FROM decision_rights"): owns[r["owner"]].append(r["domain"])
contracts={r[0] for r in c.execute("SELECT agent FROM behavioral_contracts")}

EXECS=[a for a in agents.values() if a["seniority"]=="executive"]
print("="*70); print("  EXECUTIVE STAFFING AUDIT"); print("="*70)
lone=[]
for e in sorted(EXECS,key=lambda x:x["id"]):
    direct=reports.get(e["id"],[])
    # indirect: anyone reporting to a direct report
    indirect=sum(len(reports.get(d,[])) for d in direct)
    total=len(direct)+indirect
    flag="" 
    if total==0: flag="  <-- LONE_EXECUTIVE_CAPABILITY_GAP"; lone.append(e["id"])
    elif total<2: flag="  <-- thin"
    print(f"\n{e['name']} ({e['id']})")
    print(f"  direct reports : {len(direct)}   total workforce: {total}{flag}")
    print(f"  owns domains   : {', '.join(owns.get(e['id'],[])) or 'NONE'}")
    if direct: print(f"  team           : {', '.join(direct[:8])}{' ...' if len(direct)>8 else ''}")

print("\n"+"="*70); print("  PATHOLOGY SCAN"); print("="*70)
orphans=[a["id"] for a in agents.values()
         if not a["reports_to"] or (a["reports_to"] not in agents and a["reports_to"]!="founder")]
print(f"\nORPHAN_AGENT (no valid reporting line): {len(orphans)}")
for o in orphans: print(f"  {o} -> reports_to='{agents[o]['reports_to']}'")

shadow=[a["id"] for a in agents.values()
        if not a["pack_path"] or not (R/a["pack_path"]).exists()
        or a["id"] not in contracts or not a["cognitive_style"]]
print(f"\nSHADOW_AGENT (exists but not routable): {len(shadow)}")
for s in shadow[:10]:
    a=agents[s]; why=[]
    if not (R/a["pack_path"]).exists() if a["pack_path"] else True: why.append("no pack")
    if s not in contracts: why.append("no contract")
    if not a["cognitive_style"]: why.append("no cognitive profile")
    print(f"  {s}: {', '.join(why)}")

# circular reporting
cyc=[]
for a in agents:
    seen=set(); cur=a
    while cur and cur in agents and cur not in seen:
        seen.add(cur); cur=agents[cur]["reports_to"]
    if cur in seen: cyc.append(a)
print(f"\nCIRCULAR REPORTING: {len(cyc)}" + (f" -> {cyc[:5]}" if cyc else " (none)"))

# capability gaps the user named + likely thin spots
print("\n"+"="*70); print("  NAMED / SUSPECTED GAPS"); print("="*70)
for cap,desc in [("data-analyst","Data analysis under CTO (founder explicitly named this)"),
                 ("financial-analyst","CFO has no analyst to build models"),
                 ("security-analyst","CISO has no analyst for monitoring/vuln management"),
                 ("business-operations-specialist","MD has no execution analyst"),
                 ("sales-lead","Sales is a single specialist with no lead"),
                 ("executive-operations","CEO has no ops support")]:
    ex = "EXISTS" if cap in agents else "MISSING"
    print(f"  {cap:<32}{ex:<9}{desc}")
print(f"\nTOTAL AGENTS: {len(agents)}   EXECUTIVES: {len(EXECS)}")
sys.exit(0)
