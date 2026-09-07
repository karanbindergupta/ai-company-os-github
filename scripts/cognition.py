#!/usr/bin/env python3
"""cognition.py - the cognitive architecture as a mechanism.

Personality here is an operational capability, not theatre. This tool assembles
cognitive panels with anti-anchoring enforced, surfaces the blind spots a panel
carries, detects personality drift, and scores decision QUALITY (not outcome).

  python3 scripts/cognition.py help
"""
import sqlite3, sys, pathlib, datetime, hashlib, collections
R=pathlib.Path(__file__).resolve().parent.parent
DB=R/".ai-company/state/company.db"
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def die(m): print(f"REFUSED: {m}",file=sys.stderr); sys.exit(1)

def cmd_profile(argv):
    if not argv: die("usage: profile <role>")
    c=db(); r=c.execute("SELECT * FROM agents WHERE id=?",(argv[0],)).fetchone()
    if not r: die(f"'{argv[0]}' is not a registered agent")
    F=[("ROLE",r["title"]),("DEPARTMENT",r["department"]),("MATURITY","L"+str(r["maturity_level"])),
       ("COGNITIVE STYLE",r["cognitive_style"]),("STRENGTHS",r["cog_strengths"]),
       ("BLIND SPOTS",r["blind_spots"]),("INSTINCTS - what it looks for",r["instincts"]),
       ("DECISION PHILOSOPHY",r["decision_philosophy"]),("RISK PROFILE",r["risk_profile"]),
       ("EVIDENCE THRESHOLD",r["evidence_threshold"]),("DEBATE STYLE",r["debate_style"]),
       ("UNDER PRESSURE",r["pressure_behavior"]),("ON FAILURE",r["failure_behavior"]),
       ("COUNTERBALANCED BY",r["counterbalanced_by"])]
    import textwrap
    for k,v in F:
        if not v: continue
        print(f"\n{k}")
        for line in textwrap.wrap(str(v),92): print(f"  {line}")
    print("\nGOVERNANCE OVERRIDE: this profile shapes HOW this role thinks. It never overrides the")
    print("constitution, founder authority, the authority matrix, security controls or evidence rules.")

def cmd_panel(argv):
    """panel form question=".." roles=a,b,c  - assemble a cognitive panel with anti-anchoring."""
    if not argv: die("usage: panel form|status|synthesize ...")
    sub=argv[0]; kw=dict(a.split("=",1) for a in argv[1:] if "=" in a); c=db()
    if sub=="form":
        if "question" not in kw or "roles" not in kw: die('usage: panel form question=".." roles=ceo,cfo,cto')
        roles=[x.strip() for x in kw["roles"].split(",") if x.strip()]
        bad=[x for x in roles if not c.execute("SELECT 1 FROM agents WHERE id=?",(x,)).fetchone()]
        if bad: die(f"unregistered: {', '.join(bad)}")
        if len(roles)<3: die("a panel needs at least 3 independent perspectives to be worth assembling")
        pid="PANEL-"+hashlib.sha1((kw["question"]+now()).encode()).hexdigest()[:6].upper()
        c.execute("""INSERT INTO cognitive_panels(id,decision,question,members,independent_until,status,created)
                     VALUES(?,?,?,?,?,'independent',?)""",
                  (pid,kw.get("decision"),kw["question"],",".join(roles),"all positions filed",now()))
        c.commit()
        print(f"{pid} formed: {kw['question']}\n")
        print("ANTI-ANCHORING IS IN FORCE.")
        print("  Dispatch all members IN ONE MESSAGE. Each writes independently to")
        print("  .ai-company/decisions/positions/<role>.md WITHOUT seeing another member's position.")
        print("  Exposing one position first contaminates the rest - that is the failure this prevents.\n")
        print("PANEL AND THE LENS EACH BRINGS")
        for x in roles:
            r=c.execute("SELECT * FROM agents WHERE id=?",(x,)).fetchone()
            print(f"\n  {x} ({r['title']})")
            print(f"    challenges : {(r['debate_style'] or '')[:88]}")
            print(f"    looks for  : {(r['instincts'] or '')[:88]}")
            print(f"    BLIND SPOT : {(r['blind_spots'] or '')[:88]}")
        print("\nCOVERAGE CHECK")
        cover={"economic":"cfo","technical":"cto","customer":"cpo","security":"ciso",
               "evidence":"cro-research","downside":"cro-risk","market":"cmo",
               "positioning":"cso","brand":"creative-director","execution":"coo"}
        missing=[k for k,v in cover.items() if v not in roles]
        if missing: print(f"  NOT REPRESENTED: {', '.join(missing)} - deliberate, or an oversight?")
        else: print("  full executive coverage")
        return
    if sub=="status":
        for r in c.execute("SELECT * FROM cognitive_panels ORDER BY created DESC"):
            print(f"[{r['status']:<12}] {r['id']}  {r['question'][:50]}\n    members: {r['members']}")
        return
    if sub=="synthesize":
        if "id" not in kw: die("usage: panel synthesize id=PANEL-x consensus=.. disagreements=.. uncertainties=.. missing_evidence=..")
        c.execute("""UPDATE cognitive_panels SET status='synthesized', consensus=?, disagreements=?,
                     uncertainties=?, missing_evidence=? WHERE id=?""",
                  (kw.get("consensus",""),kw.get("disagreements",""),kw.get("uncertainties",""),
                   kw.get("missing_evidence",""),kw["id"]))
        c.commit()
        print(f"{kw['id']} synthesized.")
        print("  The CEO now rules on the DISAGREEMENTS - not on a vote count.")
        print("  Record dissent verbatim: companydb.py decision dissent ...")

def cmd_blindspots(argv):
    """Which blind spots does a set of roles carry collectively, and who is missing to cover them?"""
    if not argv: die('usage: blindspots <role,role,role>')
    roles=[x.strip() for x in argv[0].split(",") if x.strip()]; c=db()
    print("COLLECTIVE BLIND SPOTS OF THIS GROUP\n")
    counter=set()
    for x in roles:
        r=c.execute("SELECT * FROM agents WHERE id=?",(x,)).fetchone()
        if not r: print(f"  {x}: not registered"); continue
        print(f"  {x}\n    {r['blind_spots']}")
        for cb in (r["counterbalanced_by"] or "").split("·"):
            n=cb.strip().split(" ")[0]
            if n: counter.add(n)
    absent=sorted(counter-set(roles))
    print(f"\nCOUNTERBALANCES NOT IN THIS GROUP: {', '.join(absent) if absent else 'none - well balanced'}")
    if absent:
        print("  Each of these exists to catch a blind spot the current group shares.")
        print("  Add them, or record explicitly why their lens is not needed here.")

def cmd_drift(argv):
    """drift record|list - personality drift detection and recalibration."""
    if not argv or argv[0]=="list":
        c=db()
        rows=list(c.execute("SELECT * FROM drift_observations WHERE status='open' ORDER BY recorded DESC"))
        if not rows: print("(no open drift observations)"); return
        for r in rows:
            print(f"[{r['severity']:<8}] {r['role']:<26}{r['pattern']}\n    evidence: {r['evidence']}\n    fix: {r['recalibration']}")
        return
    kw=dict(a.split("=",1) for a in argv[1:] if "=" in a)
    for k in ("role","pattern","evidence"):
        if k not in kw: die('usage: drift record role=.. pattern=.. evidence=.. [severity=] [recalibration=]')
    PATTERNS=["excessive confidence","excessive conservatism","excessive verbosity",
              "unnecessary disagreement","excessive risk-taking","analysis paralysis",
              "personality overriding role","refusal to defer to expertise"]
    if kw["pattern"] not in PATTERNS:
        die("pattern must be one of: " + "; ".join(PATTERNS))
    c=db()
    c.execute("""INSERT INTO drift_observations(role,pattern,evidence,severity,recalibration,recorded)
                 VALUES(?,?,?,?,?,?)""",
              (kw["role"],kw["pattern"],kw["evidence"],kw.get("severity","medium"),
               kw.get("recalibration",""),now()))
    c.commit()
    print(f"drift recorded: {kw['role']} - {kw['pattern']}")
    print("  Detect -> document -> review -> recalibrate. Recalibration edits the role's cognitive")
    print("  profile fields, and is reviewed by the Chief People Officer before taking effect.")

def cmd_score(argv):
    """score decision=DEC-001 <12 dimensions 1-5> - scores REASONING, never outcome."""
    kw=dict(a.split("=",1) for a in argv if "=" in a)
    if "decision" not in kw: die("usage: score decision=DEC-001 evidence_quality=4 reasoning_quality=4 ...")
    D=["evidence_quality","reasoning_quality","assumption_quality","downside_awareness",
       "upside_analysis","reversibility_assessed","strategic_alignment","customer_impact",
       "financial_impact","technical_impact","security_impact","confidence_calibration"]
    c=db()
    if not c.execute("SELECT 1 FROM decisions WHERE id=?",(kw["decision"],)).fetchone():
        die(f"no decision '{kw['decision']}'")
    vals=[]
    for d in D:
        v=kw.get(d)
        if v is None: die(f"missing dimension '{d}'. All 12 are required - a partial score is not a score.")
        if not v.isdigit() or not 1<=int(v)<=5: die(f"{d} must be 1-5")
        vals.append(int(v))
    c.execute(f"""INSERT OR REPLACE INTO decision_quality(decision,{','.join(D)},scored_by,scored_at,note)
                  VALUES({','.join('?'*(len(D)+4))})""",
              [kw["decision"]]+vals+[kw.get("scored_by",""),now(),kw.get("note","")])
    c.commit()
    mean=round(sum(vals)/len(vals),2); low=min(vals); worst=D[vals.index(low)]
    print(f"{kw['decision']} decision-quality score: {mean}/5")
    print(f"  weakest dimension: {worst} = {low}")
    print("\n  This scores the QUALITY OF REASONING AT THE TIME OF DECIDING.")
    print("  A well-reasoned decision can still fail; a lucky one is still badly made.")
    print("  Never score a decision by whether it happened to succeed.")

def cmd_matrix(argv):
    """Regenerate the personality interaction matrix from the database."""
    c=db()
    T=[("ceo","cfo","Strategic ambition vs capital efficiency"),
       ("ceo","cto","Speed vs technical sustainability"),
       ("ceo","cro-risk","Opportunity vs material downside"),
       ("cpo","cto","Customer value vs implementation complexity"),
       ("cpo","creative-director","Usability and conversion vs brand experience"),
       ("cmo","cpo","Market demand vs product capability"),
       ("cmo","cfo","Acquisition investment vs economic return"),
       ("ciso","cto","Security vs engineering velocity"),
       ("ciso","cpo","Control vs usability"),
       ("cso","cro-research","Strategic hypothesis vs evidence quality"),
       ("cso","coo","Strategic ambition vs executability"),
       ("cfo","cso","Near-term economics vs long-term positioning"),
       ("coo","cpo","Throughput vs scope integrity"),
       ("cro-research","ceo","Evidence sufficiency vs decision timing"),
       ("creative-director","cmo","Creative quality vs market comprehension")]
    L=["---","document: personality-interaction-matrix","version: 1.0.0",
       "source: generated from agent cognitive profiles in the company database","---",
       "# PERSONALITY INTERACTION MATRIX","",
       "**These tensions are intentional.** Each pair optimizes for something genuinely different.",
       "The company's intelligence comes from the interlock, not from agreement.","",
       "| A | B | Productive tension |","|---|---|---|"]
    for a,b,t in T: L.append(f"| `{a}` | `{b}` | {t} |")
    L+=["","## How each executive challenges","","| Role | Challenges | Characteristic blind spot |","|---|---|---|"]
    for r in c.execute("SELECT * FROM agents WHERE department='executive' ORDER BY id"):
        d=(r["debate_style"] or "").split(".")[0]
        b=(r["blind_spots"] or "").split(".")[0]
        L.append(f"| `{r['id']}` | {d} | {b} |")
    L+=["","## Complementary, not conflicting","",
        "Agents disagree when their professional models genuinely differ, and **agree quickly when",
        "the evidence is overwhelming**. Manufactured disagreement is drift (`cognition.py drift`),",
        "and so is manufactured agreement.","",
        "## Governance override","",
        "Personality never overrides the constitution, founder authority, the authority matrix,",
        "security controls, evidence requirements or safety. **Governance wins, always.**",
        "An aggressive CEO cannot authorize outside its authority. A creative agent cannot waive",
        "accessibility. A growth agent cannot bypass security. A skeptical researcher cannot",
        "endlessly delay an obviously reversible decision."]
    (R/".ai-company/cognition/personality-interaction-matrix.md").write_text("\n".join(L)+"\n")
    print(f"personality-interaction-matrix.md regenerated ({len(T)} documented tensions)")

def cmd_help(argv):
    print(__doc__)
    print("""Commands
  profile <role>                       full cognitive profile
  panel form question=".." roles=a,b,c assemble a panel; enforces anti-anchoring
  panel status | panel synthesize id=..
  blindspots <role,role,role>          collective blind spots + missing counterbalances
  drift record role=.. pattern=.. evidence=.. [severity=] [recalibration=]
  drift list
  score decision=DEC-001 <12 dimensions 1-5>   scores REASONING, not outcome
  matrix                               regenerate the interaction matrix
""")
CMDS={"profile":cmd_profile,"panel":cmd_panel,"blindspots":cmd_blindspots,"drift":cmd_drift,
      "score":cmd_score,"matrix":cmd_matrix,"help":cmd_help}
if __name__=="__main__":
    if len(sys.argv)<2 or sys.argv[1] not in CMDS: cmd_help([]); sys.exit(0 if len(sys.argv)<2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
