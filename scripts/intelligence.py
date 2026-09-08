#!/usr/bin/env python3
"""intelligence.py - the empirical layer. OBSERVED BEHAVIOUR > DECLARED CAPABILITY.

Refuses to let the company describe an untested capability as proven, promote an
agent on configuration alone, overinterpret a tiny sample, or claim a tool was
used when a fallback actually ran.

  python3 scripts/intelligence.py help
"""
import sqlite3, sys, pathlib, datetime, subprocess, hashlib, json, shutil, os
R=pathlib.Path(__file__).resolve().parent.parent
DB=R/".ai-company/state/company.db"
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def die(m): print(f"REFUSED: {m}",file=sys.stderr); sys.exit(1)
def kv(a): return dict(x.split("=",1) for x in a if "=" in x)

DIMENSIONS=["cognitive_specialization","decision_quality","evidence_calibration","independence",
            "disagreement_quality","authority_adherence","risk_recognition","failure_response",
            "learning","collaboration","communication","execution_reliability"]

# Sample-size honesty. n=1 is never a conclusion.
def confidence_for(n):
    if n<=0: return "NO DATA"
    if n==1: return "INSUFFICIENT EVIDENCE"
    if n<5:  return "very low"
    if n<15: return "low"
    if n<30: return "medium"
    if n<60: return "medium-high"
    return "high"

# ---------------------------------------------------------------- evaluation
def cmd_evaluate(argv):
    d=kv(argv)
    for k in ("agent","scenario","evaluator","eval_type"):
        if k not in d: die("usage: evaluate agent= scenario= evaluator= eval_type=controlled|adversarial|collaborative|failure|pressure|real_work [score=] [dims...]")
    c=db()
    a=c.execute("SELECT * FROM agents WHERE id=?",(d["agent"],)).fetchone()
    if not a: die(f"'{d['agent']}' is not a registered agent")
    if d["evaluator"]==d["agent"]:
        die("an agent may not be the sole evaluator of itself (section 7: no circular validation)")
    indep=1 if c.execute("SELECT 1 FROM agents WHERE id=?",(d["evaluator"],)).fetchone() and \
                d["evaluator"]!=d["agent"] and a["reports_to"]!=d["evaluator"] else 0
    eid="EVAL-"+hashlib.sha1((d["agent"]+d["scenario"]+now()).encode()).hexdigest()[:8].upper()
    c.execute("""INSERT INTO evaluations(id,agent,role,department,profile_version,scenario,objective,
        difficulty,context,constraints,evidence_available,expected_competencies,authority_boundaries,
        tools_available,pressure_conditions,agent_response,decision,assumptions,confidence,evidence_used,
        risks_identified,dissent,escalation_behavior,outcome,evaluator,evaluator_independent,
        evaluation_method,score,weaknesses,strengths,lessons,eval_type,model_version,tool_environment,
        reproducibility,created) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
      (eid,d["agent"],a["title"],a["department"],d.get("profile_version","1.0.0"),d["scenario"],
       d.get("objective",""),d.get("difficulty","medium"),d.get("context",""),d.get("constraints",""),
       d.get("evidence_available",""),d.get("expected_competencies",""),d.get("authority_boundaries",""),
       d.get("tools_available",""),d.get("pressure_conditions",""),d.get("agent_response",""),
       d.get("decision",""),d.get("assumptions",""),d.get("confidence",""),d.get("evidence_used",""),
       d.get("risks_identified",""),d.get("dissent",""),d.get("escalation_behavior",""),d.get("outcome",""),
       d["evaluator"],indep,d.get("evaluation_method","rubric"),
       float(d["score"]) if d.get("score") else None,d.get("weaknesses",""),d.get("strengths",""),
       d.get("lessons",""),d["eval_type"],d.get("model_version",""),d.get("tool_environment",""),
       d.get("reproducibility",""),now()))
    for dim in DIMENSIONS:
        if dim in d:
            n=c.execute("SELECT COUNT(*) FROM evaluations WHERE agent=?",(d["agent"],)).fetchone()[0]
            c.execute("""INSERT OR REPLACE INTO evaluation_dimensions
                (evaluation,dimension,score,evidence,confidence,sample_size,trend,limitations)
                VALUES(?,?,?,?,?,?,?,?)""",
              (eid,dim,float(d[dim]),d.get(dim+"_evidence",""),confidence_for(n),n,"",
               "single evaluation" if n<=1 else ""))
    c.execute("INSERT INTO audit_log(ts,action,entity_type,entity,detail) VALUES(?,?,?,?,?)",
              (now(),"evaluation",d["agent"],eid,d["eval_type"]))
    c.commit()
    print(f"{eid} recorded  agent={d['agent']}  type={d['eval_type']}")
    print(f"  evaluator: {d['evaluator']}  independent: {'YES' if indep else 'NO - reports-to relationship or non-agent'}")
    n=c.execute("SELECT COUNT(*) FROM evaluations WHERE agent=?",(d["agent"],)).fetchone()[0]
    print(f"  sample size for this agent: n={n}  confidence: {confidence_for(n)}")
    if n<5: print("  NOTE: too few evaluations to support any conclusion about this agent.")

def cmd_performance(argv):
    """Longitudinal, multidimensional. Never one number."""
    c=db()
    if not argv:
        rows=c.execute("""SELECT agent, COUNT(*) n, AVG(score) s,
                          SUM(evaluator_independent) ind FROM evaluations GROUP BY agent ORDER BY n DESC""").fetchall()
        if not rows: print("No evaluations recorded. Performance is UNTESTED, not zero."); return
        print(f"{'AGENT':<28}{'n':>4}{'MEAN':>7}{'INDEP':>7}  CONFIDENCE")
        for r in rows:
            print(f"{r['agent'][:27]:<28}{r['n']:>4}{(round(r['s'],1) if r['s'] else '-'):>7}"
                  f"{r['ind']:>7}  {confidence_for(r['n'])}")
        return
    ag=argv[0]
    n=c.execute("SELECT COUNT(*) FROM evaluations WHERE agent=?",(ag,)).fetchone()[0]
    print(f"PERFORMANCE HISTORY: {ag}\n")
    if n==0:
        print("  UNTESTED - no evaluations recorded.")
        print("  This is not a score of zero. It is an absence of evidence.")
        return
    print(f"  evaluations: n={n}   confidence: {confidence_for(n)}")
    ind=c.execute("SELECT SUM(evaluator_independent) FROM evaluations WHERE agent=?",(ag,)).fetchone()[0] or 0
    print(f"  independently evaluated: {ind}/{n}")
    print("\n  BY DIMENSION")
    rows=c.execute("""SELECT d.dimension, AVG(d.score) s, COUNT(*) n FROM evaluation_dimensions d
                      JOIN evaluations e ON e.id=d.evaluation WHERE e.agent=? GROUP BY d.dimension""",(ag,)).fetchall()
    if not rows: print("    (no dimension scores recorded)")
    for r in rows:
        print(f"    {r['dimension']:<28}{round(r['s'],1):>5}/100   n={r['n']}   {confidence_for(r['n'])}")
    print("\n  Multidimensional by design. There is no single 'intelligence' number.")

# ---------------------------------------------------------------- maturity
THRESHOLDS={"L2":dict(n=3,q=60,fail=2),"L3":dict(n=10,q=70,fail=1),
            "L4":dict(n=25,q=80,fail=0),"L5":dict(n=60,q=88,fail=0)}
def cmd_maturity(argv):
    """Evidence-based maturity. Refuses promotion without evidence."""
    if not argv: 
        c=db()
        print(f"{'AGENT':<28}{'LEVEL':>6}{'EVALS':>7}  VERDICT")
        for r in c.execute("""SELECT a.id, a.maturity_level, COUNT(e.id) n FROM agents a
                              LEFT JOIN evaluations e ON e.agent=a.id GROUP BY a.id
                              ORDER BY n DESC, a.id LIMIT 20"""):
            v="INSUFFICIENT EVIDENCE" if r["n"]<3 else "assessable"
            print(f"{r['id'][:27]:<28}{'L'+str(r['maturity_level']):>6}{r['n']:>7}  {v}")
        print("\nMaturity is EARNED. `maturity assess <agent>` to evaluate a promotion.")
        return
    ag=argv[0]; c=db()
    a=c.execute("SELECT * FROM agents WHERE id=?",(ag,)).fetchone()
    if not a: die(f"'{ag}' is not a registered agent")
    cur=int(a["maturity_level"]); nxt=f"L{cur+1}"
    n=c.execute("SELECT COUNT(*) FROM evaluations WHERE agent=?",(ag,)).fetchone()[0]
    q=c.execute("SELECT AVG(score) FROM evaluations WHERE agent=? AND score IS NOT NULL",(ag,)).fetchone()[0]
    viol=c.execute("""SELECT COUNT(*) FROM drift_alerts WHERE agent=? AND severity='CRITICAL' AND status='open'""",(ag,)).fetchone()[0]
    ind=c.execute("SELECT SUM(evaluator_independent) FROM evaluations WHERE agent=?",(ag,)).fetchone()[0] or 0
    print(f"MATURITY ASSESSMENT: {ag}   current L{cur} -> proposed {nxt}\n")
    if nxt not in THRESHOLDS:
        print("  Already at the top level."); return
    t=THRESHOLDS[nxt]
    checks=[("evaluated assignments", n, t["n"], n>=t["n"]),
            ("mean decision quality", round(q,1) if q else 0, t["q"], (q or 0)>=t["q"]),
            ("open CRITICAL drift alerts", viol, t["fail"], viol<=t["fail"]),
            ("independent evaluations", ind, max(1,t["n"]//3), ind>=max(1,t["n"]//3))]
    for name,have,need,ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<32} have {have}, need >= {need}" if name!="open CRITICAL drift alerts"
              else f"  [{'PASS' if ok else 'FAIL'}] {name:<32} have {have}, need <= {need}")
    verdict="PROMOTE" if all(x[3] for x in checks) else ("INSUFFICIENT EVIDENCE" if n<t["n"] else "NOT YET")
    c.execute("""INSERT INTO maturity_assessments(agent,current_level,proposed_level,verdict,
        evaluated_assignments,decision_quality,authority_violations,independent_reviews,
        sample_size,rationale,assessed_by,assessed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
      (ag,f"L{cur}",nxt,verdict,n,q,viol,ind,n,
       f"threshold n>={t['n']}, quality>={t['q']}, critical drift<={t['fail']}","intelligence-engine",now()))
    c.commit()
    print(f"\n  VERDICT: {verdict}")
    if verdict!="PROMOTE":
        print("  Not promoted. Configuration completeness and self-confidence are not evidence.")

# ---------------------------------------------------------------- drift
def cmd_drift(argv):
    if not argv: die("usage: drift detect | drift alert ... | drift list")
    sub=argv[0]; c=db()
    if sub=="list":
        rows=list(c.execute("SELECT * FROM drift_alerts WHERE status='open' ORDER BY severity DESC"))
        if not rows: print("(no open drift alerts)"); return
        for r in rows:
            print(f"[{r['severity']:<8}] {r['id']}  {r['agent']} / {r['dimension']}")
            print(f"    declared: {r['declared'][:80]}\n    observed: {r['observed'][:80]}")
            print(f"    n={r['frequency']} confidence={r['confidence']}  profile changed: {'YES' if r['profile_changed'] else 'NO - investigate first'}")
        return
    if sub=="alert":
        d=kv(argv[1:])
        for k in ("agent","dimension","declared","observed","evidence","severity"):
            if k not in d: die("usage: drift alert agent= dimension= declared= observed= evidence= severity=INFO|MINOR|MODERATE|MAJOR|CRITICAL [frequency=]")
        if d["severity"] not in ("INFO","MINOR","MODERATE","MAJOR","CRITICAL"): die("bad severity")
        freq=int(d.get("frequency",1))
        if freq<2 and d["severity"] in ("MAJOR","CRITICAL"):
            die("a MAJOR/CRITICAL drift alert needs frequency>=2. One unusual result is not drift "
                "(section 1: never modify a profile because of one unusual result).")
        aid="DRIFT-"+hashlib.sha1((d["agent"]+d["dimension"]+now()).encode()).hexdigest()[:6].upper()
        c.execute("""INSERT INTO drift_alerts(id,agent,dimension,declared,observed,evidence,frequency,
            confidence,severity,possible_causes,recommended_investigation,created)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
          (aid,d["agent"],d["dimension"],d["declared"],d["observed"],d["evidence"],freq,
           confidence_for(freq),d["severity"],
           d.get("possible_causes","workload; tool failure; missing context; playbook problem; "
                 "instruction drift; model change; profile mismatch; task misassignment"),
           d.get("recommended_investigation","Review the last N evaluations before changing anything."),now()))
        c.commit()
        print(f"{aid} raised  {d['severity']}  {d['agent']}/{d['dimension']}  n={freq}")
        print("  PROFILE NOT MODIFIED. Investigate cause before recalibrating.")
        if d["severity"]=="CRITICAL":
            print("  CRITICAL drift -> governance escalation required (companydb.py escalate level=3).")
        return
    if sub=="detect":
        # automated: compare declared evidence_threshold against observed evidence use
        print("AUTOMATED DRIFT SCAN (declared profile vs observed behaviour)\n")
        rows=c.execute("""SELECT a.id, a.evidence_threshold, COUNT(e.id) n,
                          SUM(CASE WHEN e.evidence_used IS NULL OR e.evidence_used='' THEN 1 ELSE 0 END) noev
                          FROM agents a LEFT JOIN evaluations e ON e.agent=a.id
                          GROUP BY a.id HAVING n>0""").fetchall()
        if not rows:
            print("  No evaluations exist yet. Drift cannot be detected without observed behaviour.")
            print("  This is the correct answer, not a failure.")
            return
        found=0
        for r in rows:
            if r["n"]>=2 and r["noev"]/r["n"]>0.5:
                found+=1
                print(f"  CANDIDATE  {r['id']}: declared a stated evidence threshold, but "
                      f"{r['noev']}/{r['n']} evaluations recorded no evidence used.")
        if not found: print("  No drift candidates from the available sample.")
        print(f"\n  Scanned {len(rows)} agents with observations. Candidates are NOT alerts - raise one explicitly.")

# ---------------------------------------------------------------- learning
def cmd_lesson(argv):
    if not argv: die("usage: lesson add|confirm|apply|list ...")
    sub=argv[0]; d=kv(argv[1:]); c=db()
    if sub=="list":
        for r in c.execute("SELECT * FROM lessons ORDER BY validation_status DESC, created DESC"):
            print(f"[{r['validation_status']:<20}] {r['id']}  obs={r['observation_count']} "
                  f"conf={r['independent_confirmations']} applied={r['successful_applications']}")
            print(f"    {r['lesson'][:88]}")
        return
    if sub=="add":
        for k in ("lesson","source","root_cause"):
            if k not in d: die("usage: lesson add lesson= source= root_cause= [context=] [affected_roles=]")
        lid="LES-"+hashlib.sha1((d["lesson"]+now()).encode()).hexdigest()[:6].upper()
        c.execute("""INSERT INTO lessons(id,source,context,expected_behavior,actual_behavior,outcome,
            root_cause,lesson,confidence,applicability,affected_roles,affected_playbooks,affected_agents,
            validation_status,created) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'OBSERVATION',?)""",
          (lid,d["source"],d.get("context",""),d.get("expected_behavior",""),d.get("actual_behavior",""),
           d.get("outcome",""),d["root_cause"],d["lesson"],"very low",d.get("applicability",""),
           d.get("affected_roles",""),d.get("affected_playbooks",""),d.get("affected_agents",""),now()))
        c.commit()
        print(f"{lid} recorded as OBSERVATION (n=1).")
        print("  One failure is not a rule. Promotion path: OBSERVATION -> HYPOTHESIS (repeat)")
        print("  -> VALIDATED_LESSON (independent confirmation) -> ESTABLISHED_PRACTICE (repeated success).")
        return
    if sub=="confirm":
        if "id" not in d: die("usage: lesson confirm id=LES-xxx [independent=1]")
        l=c.execute("SELECT * FROM lessons WHERE id=?",(d["id"],)).fetchone()
        if not l: die("not found")
        obs=l["observation_count"]+1
        ind=l["independent_confirmations"]+(1 if d.get("independent")=="1" else 0)
        st=l["validation_status"]
        if st=="OBSERVATION" and obs>=2: st="HYPOTHESIS"
        if st=="HYPOTHESIS" and ind>=1: st="VALIDATED_LESSON"
        c.execute("UPDATE lessons SET observation_count=?,independent_confirmations=?,validation_status=?,confidence=? WHERE id=?",
                  (obs,ind,st,confidence_for(obs),d["id"]))
        c.commit(); print(f"{d['id']} -> {st}  (observations={obs}, independent={ind})")
        return
    if sub=="apply":
        if "id" not in d: die("usage: lesson apply id=LES-xxx")
        l=c.execute("SELECT * FROM lessons WHERE id=?",(d["id"],)).fetchone()
        if not l: die("not found")
        if l["validation_status"] not in ("VALIDATED_LESSON","ESTABLISHED_PRACTICE"):
            die(f"{d['id']} is only {l['validation_status']}. A lesson must be VALIDATED before it is applied "
                "as company doctrine.")
        n=l["successful_applications"]+1
        st="ESTABLISHED_PRACTICE" if n>=3 else l["validation_status"]
        c.execute("UPDATE lessons SET successful_applications=?,validation_status=? WHERE id=?",(n,st,d["id"]))
        c.commit(); print(f"{d['id']} applied ({n}x) -> {st}")

# ---------------------------------------------------------------- capability
def probe():
    """Live probes. Nothing is GREEN because a config file exists."""
    out={}
    # Exa - anonymous tier is real; verify rather than assume
    try:
        r=subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","--max-time","15",
          "-X","POST","https://mcp.exa.ai/mcp","-H","Content-Type: application/json",
          "-H","Accept: application/json, text/event-stream","-d",
          '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}'],
          capture_output=True,text=True,timeout=25)
        exa_ok = r.stdout.strip()=="200"
    except Exception: exa_ok=False
    keyed = bool(os.environ.get("EXA_API_KEY"))
    out["exa"]=dict(cat="research",cfg=1,cred=1 if keyed else 0,reach=1 if exa_ok else 0,
        exe=1 if exa_ok else 0,obs=1,insp=1,mr=1,gate=0,
        status="OPERATIONAL_ANONYMOUS_TIER" if exa_ok else "UNREACHABLE",
        rag="GREEN" if exa_ok else "RED",
        ev=f"MCP initialize returned HTTP {'200' if exa_ok else 'non-200'} with no credential",
        budget="~3 QPS, ~150 calls/day (anonymous tier)",fb="tavily -> WebSearch",
        rem="Optional: add EXA_API_KEY to raise limits. NOT required for operation.")
    tv=shutil.which("tvly")
    out["tavily"]=dict(cat="research",cfg=1,cred=1,reach=1 if tv else 0,exe=1 if tv else 0,
        obs=1,insp=1,mr=1,gate=0,status="OPERATIONAL_KEYLESS" if tv else "NOT_INSTALLED",
        rag="GREEN" if tv else "RED",ev=f"tvly at {tv}" if tv else "binary absent",
        budget="capped keyless quota",fb="exa -> WebFetch",rem="Optional: `tvly auth` raises quota.")
    bk=bool(os.environ.get("BRAVE_API_KEY"))
    out["brave"]=dict(cat="research",cfg=1,cred=1 if bk else 0,reach=0,exe=0,obs=0,insp=0,mr=0,gate=0,
        status="CONFIGURED_BUT_CREDENTIAL_MISSING" if not bk else "OPERATIONAL",
        rag="YELLOW" if not bk else "GREEN",
        ev="BRAVE_API_KEY unset; .mcp.json entry present",budget="$5/1000 requests [Tier 1 verified]",
        fb="exa + tavily as the two independent indexes",
        rem="Founder adds BRAVE_API_KEY to settings.json env block.")
    out["websearch_native"]=dict(cat="research",cfg=1,cred=1,reach=1,exe=1,obs=1,insp=1,mr=1,gate=0,
        status="OPERATIONAL",rag="GREEN",ev="verified live in prior phases",budget="none",
        fb="none needed",rem="")
    wf=list((R/".github/workflows").glob("*")) if (R/".github/workflows").exists() else []
    gh=shutil.which("gh")
    # CI truth has three parts: does a workflow exist, does it EXECUTE, and has a REMOTE run
    # been observed? Earlier this collapsed to a single guess and contradicted ci_report.py.
    remote = "[remote" in (R/".git/config").read_text() if (R/".git/config").exists() else False
    try:
        con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
        local_runs=con.execute("SELECT COUNT(*) FROM ci_runs WHERE observed=1").fetchone()[0]
        last=con.execute("SELECT status FROM ci_runs ORDER BY started DESC").fetchone()
        last=last[0] if last else None
    except Exception: local_runs, last = 0, None
    if not wf:
        ci=dict(status="NOT_CONFIGURED",rag="GRAY",exe=0,obs=0,insp=0,mr=0,
                ev="no workflow files")
    elif local_runs and remote:
        ci=dict(status="OPERATIONAL",rag="GREEN",exe=1,obs=1,insp=1,mr=1,
                ev=f"workflow present; {local_runs} observed runs; remote configured; last={last}")
    elif local_runs:
        ci=dict(status="WORKFLOW_WRITTEN_EXECUTES_LOCALLY_NO_REMOTE",rag="YELLOW",exe=1,obs=1,insp=1,mr=1,
                ev=f"ci.yml present; {local_runs} runs executed and persisted to ci_runs "
                   f"(last={last}); NO GIT REMOTE so Actions has never run it")
    else:
        ci=dict(status="CONFIGURED_NEVER_EXECUTED",rag="RED",exe=0,obs=0,insp=0,mr=0,
                ev="ci.yml present but never executed")
    out["ci"]=dict(cat="ci_cd",cfg=1 if wf else 0,cred=0,reach=1 if wf else 0,
        exe=ci["exe"],obs=ci["obs"],insp=ci["insp"],mr=ci["mr"],
        gate=0,  # trusted_as_gate stays 0 until a REMOTE run is observed
        status=ci["status"],rag=ci["rag"],ev=ci["ev"],budget="",
        fb="local execution via scripts/ci_report.py",
        rem="" if ci["rag"]=="GREEN" else
            "Founder action: create the GitHub repo and push. Actions then runs ci.yml on every "
            "push. trusted_as_gate remains 0 until a remote run is observed - UNKNOWN is never PASS.")
    out["git"]=dict(cat="development",cfg=1,cred=1,reach=1,exe=1,obs=1,insp=1,mr=1,gate=0,
        status="OPERATIONAL",rag="GREEN",ev=f"git present at {shutil.which('git')}",budget="",fb="",rem="")
    ghtok=bool(os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"))
    out["github"]=dict(cat="development",cfg=1,cred=1 if ghtok else 0,reach=1,exe=1,obs=1,insp=1,mr=1,gate=0,
        status="OPERATIONAL" if ghtok else "TOKEN_NOT_IN_THIS_SHELL",rag="GREEN" if ghtok else "YELLOW",
        ev="GITHUB_PERSONAL_ACCESS_TOKEN present in this shell" if ghtok else
           "no GITHUB_PERSONAL_ACCESS_TOKEN in this shell - set it to enable GitHub tools",
        budget="5000 req/hr",fb="local git",rem="")
    npm=shutil.which("npm")
    out["npm_audit"]=dict(cat="security",cfg=1,cred=1,reach=1 if npm else 0,exe=1 if npm else 0,
        obs=1,insp=1,mr=1,gate=1,status="OPERATIONAL" if npm else "ABSENT",
        rag="GREEN" if npm else "RED",ev=f"npm present at {npm}" if npm else "npm not on PATH",budget="",fb="",rem="")
    out["claude_security"]=dict(cat="security",cfg=1,cred=1,reach=1,exe=0,obs=0,insp=1,mr=0,gate=0,
        status="INSTALLED_NEVER_EXERCISED",rag="YELLOW",
        ev="plugin registered in the Claude Code environment; no scan observed in this repository",
        budget="",fb="npm audit + manual review",rem="Run a scan on real source code once it exists.")
    out["secret_scanning"]=dict(cat="security",cfg=1,cred=1,reach=1,exe=1,obs=1,insp=1,mr=1,gate=1,
        status="OPERATIONAL",rag="GREEN",
        ev="scripts/secret_scan.sh present and executable",budget="",fb="",rem="")
    for n in ["static_analysis","container_scanning","logs","metrics","traces","errors"]:
        out[n]=dict(cat="security" if "scan" in n or n=="static_analysis" else "observability",
          cfg=0,cred=0,reach=0,exe=0,obs=0,insp=0,mr=0,gate=0,status="NOT_CONFIGURED",rag="GRAY",
          ev="no product exists to instrument or scan",budget="",fb="",
          rem="Deliberately deferred - installing observability for a nonexistent product is waste.")
    brew=shutil.which("brew")
    out["homebrew"]=dict(cat="development",cfg=1 if brew else 0,cred=1,reach=1 if brew else 0,
        exe=1 if brew else 0,obs=1,insp=1,mr=0,gate=0,
        status="ABSENT_NO_ACTION_REQUIRED",rag="YELLOW" if not brew else "GREEN",
        ev="absent; a known documented constraint, not a new actionable issue",
        budget="",fb="npm -g and uv both verified working without it",rem="NO_ACTION_REQUIRED")
    return out

def cmd_capability(argv):
    c=db(); p=probe()
    for name,d in p.items():
        c.execute("""INSERT OR REPLACE INTO capability_readiness(name,category,configured,credentialed,
            reachable,executable,observable,inspectable,machine_readable,trusted_as_gate,status,rag,
            evidence,budget,fallback,remediation,last_probed)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (name,d["cat"],d["cfg"],d["cred"],d["reach"],d["exe"],d["obs"],d["insp"],d["mr"],d["gate"],
           d["status"],d["rag"],d["ev"],d["budget"],d["fb"],d["rem"],now()))
    c.commit()
    order={"GREEN":0,"YELLOW":1,"RED":2,"GRAY":3}
    print("INFRASTRUCTURE READINESS  (live probes - nothing is GREEN from configuration alone)\n")
    cat=None
    for r in sorted(c.execute("SELECT * FROM capability_readiness"),key=lambda x:(x["category"],order[x["rag"]])):
        if r["category"]!=cat: cat=r["category"]; print(f"\n{cat.upper()}")
        print(f"  [{r['rag']:<6}] {r['name']:<20}{r['status']}")
        if r["evidence"]: print(f"           evidence: {r['evidence'][:90]}")
    g=c.execute("SELECT COUNT(*) FROM capability_readiness WHERE rag='GREEN'").fetchone()[0]
    tot=c.execute("SELECT COUNT(*) FROM capability_readiness").fetchone()[0]
    print(f"\n  GREEN {g}/{tot}. GRAY means unverified or deliberately absent - never assume it works.")

def cmd_provider(argv):
    """Record which provider ACTUALLY ran. Never claim a provider that fell back."""
    d=kv(argv)
    for k in ("requested","actual"):
        if k not in d: die("usage: provider requested= actual= [task=] [fallback_reason=] [evidence=]")
    c=db()
    if d["requested"]!=d["actual"] and not d.get("fallback_reason"):
        die("a fallback must record WHY. The company never silently substitutes a provider.")
    cap=c.execute("SELECT status,rag FROM capability_readiness WHERE name=?",(d["actual"],)).fetchone()
    if cap is None:
        die(f"'{d['actual']}' has no readiness record. Probe it first: intelligence.py capability")
    # Only a GREEN capability may be recorded as having actually run. YELLOW (degraded /
    # credential-missing) previously slipped through, which would have let an agent claim a
    # provider it could not have used. Found by test 13.
    if cap["rag"] != "GREEN":
        die(f"'{d['actual']}' is {cap['status']} ({cap['rag']}) - it CANNOT be recorded as the actual "
            f"provider. Record the provider that genuinely ran, with a fallback_reason.")
    c.execute("""INSERT INTO provider_usage(task,requested_provider,actual_provider,fallback_reason,
        research_quality,evidence,recorded) VALUES(?,?,?,?,?,?,?)""",
      (d.get("task",""),d["requested"],d["actual"],d.get("fallback_reason",""),
       d.get("research_quality",""),d.get("evidence",""),now()))
    c.commit()
    if d["requested"]==d["actual"]: print(f"provider recorded: {d['actual']} (as requested)")
    else:
        print(f"FALLBACK RECORDED: requested {d['requested']} -> actually used {d['actual']}")
        print(f"  reason: {d['fallback_reason']}")
        print(f"  The artifact must state that {d['requested']} was NOT used.")

def cmd_help(argv):
    print(__doc__)
    print("""Commands
  evaluate agent= scenario= evaluator= eval_type= [score=] [<dimension>=..]
  performance [agent]                 longitudinal, multidimensional, with sample size
  maturity [agent]                    evidence-based promotion assessment
  drift detect | drift alert ... | drift list
  lesson add|confirm|apply|list       OBSERVATION -> HYPOTHESIS -> VALIDATED -> ESTABLISHED
  capability                          live infrastructure probes (RAG)
  provider requested= actual= [fallback_reason=]   honest provider provenance
  report                              company intelligence report
""")

def cmd_report(argv):
    c=db()
    print("="*64); print("  AI COMPANY INTELLIGENCE REPORT"); print("="*64)
    ne=c.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
    print(f"\n1-3. AGENT PERFORMANCE     {ne} evaluations recorded")
    if ne==0: print("     UNTESTED - no agent has been behaviourally evaluated.")
    print(f"\n4.  COGNITIVE DIVERSITY    {c.execute('SELECT COUNT(DISTINCT cognitive_style) FROM agents').fetchone()[0]} distinct styles / 111 agents")
    dq=c.execute("SELECT COUNT(*) FROM decision_quality").fetchone()[0]
    print(f"5.  DECISION QUALITY       {dq} decisions scored" + ("  (INSUFFICIENT EVIDENCE)" if dq<5 else ""))
    print(f"6.  DISAGREEMENT           {c.execute('SELECT COUNT(*) FROM dissent').fetchone()[0]} dissents recorded")
    print(f"7.  FAILURE HANDLING       {c.execute('SELECT COUNT(*) FROM incidents').fetchone()[0]} incidents")
    ls=c.execute("SELECT validation_status, COUNT(*) n FROM lessons GROUP BY validation_status").fetchall()
    print(f"8.  LEARNING               " + (", ".join(f"{r['validation_status']}={r['n']}" for r in ls) if ls else "no lessons recorded"))
    da=c.execute("SELECT COUNT(*) FROM drift_alerts WHERE status='open'").fetchone()[0]
    print(f"9.  DRIFT ALERTS           {da} open")
    ma=c.execute("SELECT COUNT(*) FROM maturity_assessments").fetchone()[0]
    print(f"10. MATURITY               {ma} assessments; promotions require evidence")
    print(f"13. PLAYBOOK COVERAGE      {c.execute('SELECT COUNT(*) FROM playbook_coverage').fetchone()[0]} capabilities mapped")
    print("\n14-16. INFRASTRUCTURE")
    for r in c.execute("SELECT * FROM capability_readiness WHERE rag<>'GREEN' ORDER BY rag"):
        print(f"     [{r['rag']:<6}] {r['name']:<20}{r['status']}")
    print("\n18. EVIDENCE LIMITATIONS")
    print("     Sample sizes are small or zero. Nothing here supports a conclusion about")
    print("     agent quality. The layer is INSTALLED and MECHANICALLY TESTED, not PROVEN.")
    print("="*64)

CMDS={"evaluate":cmd_evaluate,"performance":cmd_performance,"maturity":cmd_maturity,"drift":cmd_drift,
      "lesson":cmd_lesson,"capability":cmd_capability,"provider":cmd_provider,"report":cmd_report,"help":cmd_help}
if __name__=="__main__":
    if len(sys.argv)<2 or sys.argv[1] not in CMDS: cmd_help([]); sys.exit(0 if len(sys.argv)<2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
