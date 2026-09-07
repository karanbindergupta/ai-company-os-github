#!/usr/bin/env python3
"""workforce.py - the People department's operating mechanism.

Answers the question the orchestrator actually asks: "who should do this?"
Also surfaces what executives need for organizational design: overload,
single points of failure, duplicated capability and capability gaps.

  python3 scripts/workforce.py help
"""
import sqlite3, sys, pathlib, datetime, collections, hashlib
R = pathlib.Path(__file__).resolve().parent.parent
DB = R/".ai-company/state/company.db"
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def die(m): print(f"REFUSED: {m}", file=sys.stderr); sys.exit(1)


# Capability vocabulary. The orchestrator asks for "finance" or "marketing"; those are not
# department names here (finance sits under executive + strategy-research). Found by testing.
ALIAS = {
 "finance":["cfo","financial-strategist","pricing-strategist","business-model-strategist"],
 "marketing":["cmo","marketing-strategist","content-strategist","copywriter"],
 "legal":["compliance-specialist","privacy-specialist"],
 "analytics":["analytics-specialist","cro-specialist"],
 "risk":["cro-risk","threat-modeler"],
 "architecture":["principal-architect","systems-architect","solution-architect"],
 "research":["cro-research","research-director","market-researcher","customer-researcher"],
 "qa":["qa-lead","qa-engineer","e2e-tester"],
 "design":["creative-director","ux-designer","ui-designer","design-system-architect"],
 "strategy":["cso","opportunity-analyst","innovation-strategist"],
 "release":["release-manager","devops-engineer"],
}
def _alias_hits(cap):
    return ALIAS.get(cap, [])

def _load(c):
    """Live workload and performance per agent."""
    wl=collections.Counter(r["owner"] for r in c.execute(
        "SELECT owner FROM tasks WHERE status IN ('todo','in_progress','review','blocked')"))
    rv=collections.Counter(r["reviewer"] for r in c.execute(
        "SELECT reviewer FROM tasks WHERE reviewer IS NOT NULL AND status NOT IN ('done','cancelled')"))
    perf={}
    for r in c.execute("""SELECT role, COUNT(*) n, SUM(CASE WHEN outcome='done' THEN 1 ELSE 0 END) done,
                          SUM(rework) rw, SUM(review_failed) rf FROM agent_performance GROUP BY role"""):
        n=r["n"] or 1
        perf[r["role"]]=round(max(0,min(5,5*(r["done"]/n)-1.5*(r["rw"]/n)-2.0*(r["rf"]/n))),2)
    return wl, rv, perf

def cmd_registry(argv):
    c=db(); wl,rv,perf=_load(c)
    dept = argv[0] if argv else None
    q="SELECT * FROM agents" + (" WHERE department=?" if dept else "") + " ORDER BY department, authority_level, id"
    rows=list(c.execute(q, ([dept] if dept else [])))
    if not rows: die(f"no agents{' in ' + dept if dept else ''}")
    print(f"{'AGENT':<30}{'DEPT':<19}{'LVL':>4}{'LOAD':>6}{'REVIEWS':>8}{'SCORE':>7}  STATUS")
    for r in rows:
        s=perf.get(r["id"])
        print(f"{r['id'][:29]:<30}{r['department'][:18]:<19}{'L'+str(r['authority_level']):>4}"
              f"{wl.get(r['id'],0):>6}{rv.get(r['id'],0):>8}{(s if s is not None else '-'):>7}  {r['status']}")
    print(f"\n{len(rows)} agents. Load = open owned tasks. Score is quality-weighted; speed is not counted.")

def cmd_assign(argv):
    """assign capability=<domain-ish> [risk=high] [exclude=a,b] - recommend an owner AND an independent reviewer."""
    kw=dict(a.split("=",1) for a in argv if "=" in a)
    if "capability" not in kw: die("usage: assign capability=<department|role|keyword> [risk=low|high] [exclude=a,b]")
    cap=kw["capability"].lower(); risk=kw.get("risk","low")
    excl={x for x in kw.get("exclude","").split(",") if x}
    c=db(); wl,rv,perf=_load(c)
    rows=[r for r in c.execute("SELECT * FROM agents WHERE status='active'") if r["id"] not in excl]
    hits=_alias_hits(cap)
    def match(r):
        s=0
        if r["id"] in hits: s+=10 - hits.index(r["id"])   # alias order = preference
        if cap==r["department"]: s+=6
        if cap in r["id"]: s+=8
        if cap in (r["title"] or "").lower(): s+=5
        if cap in (r["cognitive_profile"] or "").lower(): s+=2
        return s
    cands=[(match(r),r) for r in rows]
    cands=[(s,r) for s,r in cands if s>0]
    if not cands: die(f"no agent matches '{cap}'. Check `registry` or the role registry.")
    def rank(t):
        s,r=t
        load=wl.get(r["id"],0)+rv.get(r["id"],0)
        score=perf.get(r["id"],3.0)
        # capability first, then spread the work, then track record.
        # deliberately NOT "always the best agent" - that creates a single point of failure.
        return -(s*3) + load*2 - score
    cands.sort(key=rank)
    top=cands[0][1]
    print(f"RECOMMENDED OWNER   {top['id']}  ({top['title']})")
    print(f"  department        {top['department']}   authority L{top['authority_level']}")
    print(f"  current load      {wl.get(top['id'],0)} owned, {rv.get(top['id'],0)} reviewing")
    print(f"  track record      {perf.get(top['id'],'no history yet')}")
    print(f"  cognitive profile {top['cognitive_profile']}")
    # independent reviewer - never the owner, prefer a named backup or the auditor line
    rb=c.execute("SELECT id FROM agents WHERE backup_for=?", (top["id"],)).fetchone()
    rev=None
    if rb: rev=rb["id"]
    elif top["backup_for"]: rev=top["backup_for"]
    else:
        peers=[r for s,r in cands if r["id"]!=top["id"]]
        rev=peers[0]["id"] if peers else (top["reports_to"] or "coo")
    if rev==top["id"]: rev=top["reports_to"] or "coo"
    print(f"\nINDEPENDENT REVIEWER {rev}")
    print("  (owner != reviewer is enforced by the database, not by convention)")
    alts=[r["id"] for s,r in cands[1:4]]
    if alts: print(f"\nALTERNATES          {', '.join(alts)}")
    if risk=="high":
        print("\nHIGH RISK - also route to: an executive owner for the domain, plus an independent auditor.")
        print("  Check `companydb.py authority <domain>` for who must review and who may veto.")

def cmd_health(argv):
    """Organizational health: overload, single points of failure, duplication, idle capability."""
    c=db(); wl,rv,perf=_load(c)
    rows=list(c.execute("SELECT * FROM agents WHERE status='active'"))
    print("ORGANIZATIONAL HEALTH\n")
    over=[(a,wl.get(a,0)+rv.get(a,0)) for a in {r["id"] for r in rows} if wl.get(a,0)+rv.get(a,0)>=4]
    print("OVERLOADED (>=4 open items)")
    if over:
        for a,n in sorted(over,key=lambda x:-x[1]): print(f"  {a:<30}{n} items")
    else: print("  none")
    crit=["ciso","cto","cpo","cfo","ceo","principal-architect","qa-lead","cro-research",
          "creative-director","release-manager","coo","cro-risk"]
    have={r["id"]:r["backup_for"] for r in rows}
    back={r["backup_for"] for r in rows if r["backup_for"]}
    print("\nSINGLE POINTS OF FAILURE (critical role with no named backup)")
    spof=[a for a in crit if a in have and a not in back]
    if spof:
        for a in spof: print(f"  {a}  - no agent is registered as backup_for={a}")
    else: print("  none - every critical role has a named backup")
    print("\nCAPABILITY REDUNDANCY (critical roles and their backups)")
    for r in sorted(rows,key=lambda x:x["id"]):
        if r["backup_for"]: print(f"  {r['backup_for']:<26} <- backed by {r['id']}")
    dept=collections.Counter(r["department"] for r in rows)
    print("\nDEPARTMENT SIZE")
    for d,n in dept.most_common(): print(f"  {d:<22}{n}")
    idle=[r["id"] for r in rows if wl.get(r["id"],0)+rv.get(r["id"],0)==0]
    print(f"\nIDLE CAPABILITY  {len(idle)} agents with no open work")
    print("  (idle is normal - roles activate per mission. Only a concern if a needed role stays idle)")
    weak=[(a,s) for a,s in perf.items() if s<3.0]
    print("\nUNDERPERFORMING (score < 3.0)")
    if weak:
        for a,s in sorted(weak,key=lambda x:x[1]):
            print(f"  {a:<30}{s}  -> diagnose before replacing: capability, tools, knowledge,")
            print( "                                instructions, assignment, review, model, or workload?")
    else: print("  none recorded")

def cmd_team(argv):
    """team form objective=.. capabilities=a,b,c [risk=high] | team list | team dissolve id=.."""
    if not argv: die("usage: team form|list|dissolve ...")
    sub=argv[0]; kw=dict(a.split("=",1) for a in argv[1:] if "=" in a); c=db()
    if sub=="list":
        for r in c.execute("SELECT * FROM team_formations ORDER BY created DESC"):
            print(f"[{r['status']:<9}] {r['id']}  {r['objective'][:44]:<44} members={r['members'][:40]}")
        return
    if sub=="dissolve":
        if "id" not in kw: die("usage: team dissolve id=TEAM-xxx")
        c.execute("UPDATE team_formations SET status='dissolved',dissolved=? WHERE id=?",(now(),kw["id"]))
        c.commit(); print(f"{kw['id']} dissolved. Temporary teams do not persist past their objective.")
        return
    if sub=="form":
        for k in ("objective","capabilities"): 
            if k not in kw: die("usage: team form objective=.. capabilities=research,product,security [risk=high]")
        caps=[x.strip() for x in kw["capabilities"].split(",") if x.strip()]
        members,reviewers=[],[]
        wl,rv,perf=_load(c)
        for cap in caps:
            cl=cap.lower(); hits=_alias_hits(cl)
            def rel(r):
                s=0
                if r["id"] in hits: s+=10-hits.index(r["id"])
                if cl==r["department"]: s+=6
                if cl in r["id"]: s+=8
                if cl in (r["title"] or "").lower(): s+=5
                # a lead outranks a junior specialist when both match equally
                if r["authority_level"]<=2: s+=2
                return s
            rows=[r for r in c.execute("SELECT * FROM agents WHERE status='active'") if rel(r)>0]
            if not rows: print(f"  WARNING: no agent matches capability '{cap}'"); continue
            rows.sort(key=lambda r: (-rel(r), wl.get(r["id"],0)+rv.get(r["id"],0)))
            m=rows[0]; members.append(m["id"])
            rb=c.execute("SELECT id FROM agents WHERE backup_for=?",(m["id"],)).fetchone()
            reviewers.append(rb["id"] if rb else (m["reports_to"] or "coo"))
        execu = "ceo" if kw.get("risk")=="high" else ""
        tid="TEAM-"+hashlib.sha1((kw["objective"]+now()).encode()).hexdigest()[:6].upper()
        c.execute("""INSERT INTO team_formations(id,objective,capabilities,members,reviewers,executive,risk,created)
                     VALUES(?,?,?,?,?,?,?,?)""",
                  (tid,kw["objective"],",".join(caps),",".join(members),",".join(reviewers),
                   execu,kw.get("risk","low"),now()))
        c.commit()
        print(f"{tid} formed for: {kw['objective']}")
        print(f"  members    {', '.join(members)}")
        print(f"  reviewers  {', '.join(reviewers)}   (independent of their member)")
        if execu: print(f"  executive  {execu}  (high risk - executive oversight attached)")
        print("\nDissolve when the objective completes: workforce.py team dissolve id="+tid)

def cmd_retire(argv):
    """retire role=<id> reason=.. successor=<id> - checklist before deprecating an agent."""
    kw=dict(a.split("=",1) for a in argv if "=" in a)
    for k in ("role","reason","successor"):
        if k not in kw: die("usage: retire role=<id> reason=.. successor=<id>")
    c=db()
    r=c.execute("SELECT * FROM agents WHERE id=?",(kw["role"],)).fetchone()
    if not r: die(f"'{kw['role']}' is not a registered agent")
    if not c.execute("SELECT 1 FROM agents WHERE id=?",(kw["successor"],)).fetchone():
        die(f"successor '{kw['successor']}' is not a registered agent - verify replacement capability first")
    open_t=c.execute("SELECT COUNT(*) FROM tasks WHERE owner=? AND status NOT IN ('done','cancelled')",
                     (kw["role"],)).fetchone()[0]
    if open_t: die(f"'{kw['role']}' still owns {open_t} open task(s). Transfer responsibilities first.")
    deps=[x["id"] for x in c.execute("SELECT id FROM agents WHERE backup_for=?",(kw["role"],))]
    dom=[x["domain"] for x in c.execute("SELECT domain FROM decision_rights WHERE owner=?",(kw["role"],))]
    if dom: die(f"'{kw['role']}' owns decision domain(s): {', '.join(dom)}. Reassign before retiring.")
    c.execute("UPDATE agents SET status='retired' WHERE id=?",(kw["role"],))
    c.execute("INSERT INTO audit_log(ts,action,entity_type,entity,detail) VALUES(?,?,?,?,?)",
              (now(),"agent_retired","agent",kw["role"],f"reason={kw['reason']}; successor={kw['successor']}"))
    c.commit()
    print(f"{kw['role']} retired.  successor: {kw['successor']}")
    print("  Preserve knowledge: move its lessons to .ai-company/knowledge/lessons-learned/")
    if deps: print(f"  WARNING: {', '.join(deps)} listed it as backup_for - update those.")
    print("  Review its tool permissions with security: obsolete permissions must not stay active.")

def cmd_help(argv):
    print(__doc__)
    print("""Commands
  registry [department]                     workforce registry: load, reviews, score
  assign capability=<x> [risk=high] [exclude=a,b]   recommend owner + independent reviewer
  health                                    overload, SPOFs, redundancy, idle, underperformance
  team form objective=.. capabilities=a,b,c [risk=high]
  team list | team dissolve id=TEAM-xxx
  retire role=<id> reason=.. successor=<id> guarded deprecation checklist
""")
CMDS={"registry":cmd_registry,"assign":cmd_assign,"health":cmd_health,"team":cmd_team,
      "retire":cmd_retire,"help":cmd_help}
if __name__=="__main__":
    if len(sys.argv)<2 or sys.argv[1] not in CMDS: cmd_help([]); sys.exit(0 if len(sys.argv)<2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
