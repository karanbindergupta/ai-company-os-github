#!/usr/bin/env python3
"""companydb.py - the AI Company's operating mechanism.

Authority, vetoes, separation of duties, decisions, dependencies, memory and
recovery are enforced HERE, in code, so they cannot be talked around by a model
under pressure. Markdown states the rules; this file makes them real.

  python3 scripts/companydb.py help
"""
import sqlite3, sys, json, pathlib, datetime, hashlib, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / ".ai-company/state/company.db"
SCHEMA = ROOT / ".ai-company/state/schema.sql"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def die(m): print(f"REFUSED: {m}", file=sys.stderr); sys.exit(1)
def ok(m): print(m)

def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; c.execute("PRAGMA foreign_keys=ON")
    return c

def log(c, action, actor=None, etype=None, entity=None, detail=None):
    c.execute("INSERT INTO audit_log(ts,actor,action,entity_type,entity,detail) VALUES(?,?,?,?,?,?)",
              (now(), actor, action, etype, entity, detail))

def kv(argv):
    out = {}
    for a in argv:
        if "=" in a: k, v = a.split("=", 1); out[k] = v
    return out

def need(d, *keys):
    miss = [k for k in keys if not d.get(k)]
    if miss: die(f"missing required: {', '.join(miss)}")

# --------------------------------------------------------------- bootstrap
AUTH_LEVEL = {"founder": 0, "executive": 1, "lead": 2, "specialist": 3}

DECISION_RIGHTS = [
 # domain, owner, reviewers, veto_holders, founder_required, escalation_level
 ("technical_architecture","cto","principal-architect,security-architect","ciso,cto",0,3),
 ("product_roadmap","cpo","ceo,cso","cpo",0,3),
 ("product_scope","cpo","product-manager,cto","cpo",0,3),
 ("pricing","cfo","cpo,ceo,pricing-strategist","cfo",1,4),
 ("marketing_strategy","cmo","cpo,cfo","",0,3),
 ("brand_direction","creative-director","cmo,ceo","creative-director",0,3),
 ("security_architecture","ciso","cto,security-architect","ciso",0,3),
 ("release_readiness","release-manager","qa-lead,ciso,cpo","ciso,qa-lead,release-manager",1,4),
 ("major_financial_commitment","cfo","ceo","cfo",1,4),
 ("market_entry","cso","cfo,cmo,ceo","cro-risk",1,4),
 ("business_model","cfo","cso,cpo,ceo","cfo",1,4),
 ("hiring_role","chief-people-officer","coo","chief-people-officer",0,2),
 ("research_acceptance","cro-research","research-auditor","research-auditor,cro-risk",0,2),
 ("risk_acceptance","cro-risk","ceo,ciso","cro-risk",1,4),
 ("engineering_standards","cto","backend-lead,frontend-lead","cto",0,2),
 ("data_migration","database-architect","cto","cto,ciso",1,4),
 ("production_deploy","devops-engineer","release-manager,ciso","ciso,release-manager",1,4),
 ("public_communication","cmo","ceo,creative-director","",1,4),
 ("routine_implementation","backend-lead","code-reviewer","",0,1),
 ("routine_bugfix","qa-lead","code-reviewer","",0,1),
]

TOOL_PERMS = [  # least privilege: role-pattern, tool, grant
 ("researcher_roles","WebSearch,WebFetch,exa,tavily","allow"),
 ("engineer_roles","Bash,Edit,Write,Read,Grep,Glob","allow"),
 ("qa_roles","Bash,Read,Grep,Glob,browser","allow"),
 ("security_roles","Bash,Read,Grep,Glob,claude-security,npm-audit","allow"),
 ("design_roles","Read,Write,Edit,adobe,cloudinary,v0,miro","allow"),
 ("finance_roles","Read,Write,Edit,WebSearch,WebFetch","allow"),
 ("release_roles","Bash,Read,git","confirm"),
 ("all_roles","supabase-execute-sql,supabase-apply-migration,deploy,publish,purchase","confirm"),
]

def cmd_init(argv):
    if DB.exists() and "--force" not in argv:
        die("database already exists. Pass --force only if you intend to rebuild it.")
    c = db(); c.executescript(SCHEMA.read_text())
    reg = json.loads((ROOT/".ai-company/org/roles.json").read_text())["roles"]
    depts = sorted({r["department"] for r in reg})
    for d in depts:
        c.execute("INSERT OR REPLACE INTO departments(id,name,charter) VALUES(?,?,?)",
                  (d, d.replace("-", " ").title(), f".ai-company/departments/{d}.md"))
    for r in reg:
        lvl = AUTH_LEVEL.get(r["seniority"], 3)
        if r["slug"] in ("backend-lead","frontend-lead","qa-lead","principal-architect",
                         "database-architect","product-manager","release-manager"): lvl = 2
        c.execute("""INSERT OR REPLACE INTO agents(id,department,title,reports_to,seniority,
                     authority_level,artifact,pack_path,status) VALUES(?,?,?,?,?,?,?,?,'active')""",
                  (r["slug"], r["department"], r["title"], r["reports_to"], r["seniority"],
                   lvl, r["artifact"], r["path"]))
    known = {r["slug"] for r in reg}
    for dom, own, rev, veto, fr, esc in DECISION_RIGHTS:
        if own not in known: continue
        rev = ",".join(x for x in rev.split(",") if x in known)
        veto = ",".join(x for x in veto.split(",") if x in known)
        c.execute("""INSERT OR REPLACE INTO decision_rights
                     (domain,owner,reviewers,veto_holders,founder_required,escalation_level)
                     VALUES(?,?,?,?,?,?)""", (dom, own, rev, veto, fr, esc))
    c.execute("INSERT OR REPLACE INTO schema_version VALUES(1,?)", (now(),))
    log(c, "db_init", detail=f"{len(reg)} agents, {len(depts)} departments")
    c.commit()
    ok(f"company database initialized\n  agents: {len(reg)}  departments: {len(depts)}  "
       f"decision domains: {c.execute('SELECT COUNT(*) FROM decision_rights').fetchone()[0]}")

# --------------------------------------------------------------- authority
def cmd_authority(argv):
    """Who owns / reviews / can veto a decision domain, and does the founder decide?"""
    c = db()
    if not argv:
        ok(f"{'DOMAIN':<30}{'OWNER':<24}{'VETO':<28}FOUNDER")
        for r in c.execute("SELECT * FROM decision_rights ORDER BY domain"):
            ok(f"{r['domain']:<30}{r['owner']:<24}{(r['veto_holders'] or '-'):<28}"
               f"{'YES' if r['founder_required'] else 'no'}")
        return
    dom = argv[0]
    r = c.execute("SELECT * FROM decision_rights WHERE domain=?", (dom,)).fetchone()
    if not r: die(f"unknown domain '{dom}'. Run `authority` with no arguments to list them.")
    ok(f"DOMAIN            {r['domain']}\nOWNER             {r['owner']}")
    ok(f"REVIEWERS         {r['reviewers'] or '(none)'}")
    ok(f"VETO HOLDERS      {r['veto_holders'] or '(none)'}")
    ok(f"FOUNDER APPROVAL  {'REQUIRED' if r['founder_required'] else 'not required'}")
    ok(f"ESCALATES TO      level {r['escalation_level']}")

def cmd_can(argv):
    """can <role> <action> <domain>  - authority check before acting."""
    if len(argv) < 3: die("usage: can <role> <decide|approve|review|veto> <domain>")
    role, action, dom = argv[0], argv[1], argv[2]
    c = db()
    if not c.execute("SELECT 1 FROM agents WHERE id=?", (role,)).fetchone():
        die(f"'{role}' is not a registered agent")
    r = c.execute("SELECT * FROM decision_rights WHERE domain=?", (dom,)).fetchone()
    if not r: die(f"unknown domain '{dom}'")
    rev = [x for x in r["reviewers"].split(",") if x]
    veto = [x for x in r["veto_holders"].split(",") if x]
    verdict, why = False, ""
    if action == "decide":
        verdict = (role == r["owner"])
        why = f"owner is {r['owner']}"
        if verdict and r["founder_required"]:
            why = "owner, BUT founder approval is required before this takes effect"
    elif action == "approve": verdict, why = role in rev or role == r["owner"], f"approvers: {r['reviewers'] or 'none'}"
    elif action == "review":  verdict, why = role in rev, f"reviewers: {r['reviewers'] or 'none'}"
    elif action == "veto":    verdict, why = role in veto, f"veto holders: {r['veto_holders'] or 'none'}"
    else: die("action must be decide, approve, review or veto")
    ok(f"{'ALLOWED' if verdict else 'DENIED'}  {role} may {'' if verdict else 'NOT '}{action} '{dom}'\n  {why}")
    sys.exit(0 if verdict else 2)

def cmd_veto(argv):
    """veto raise|lift|list - domain-limited blocking authority with mandatory justification."""
    if not argv: die("usage: veto raise|lift|list ...")
    sub = argv[0]; d = kv(argv[1:]); c = db()
    if sub == "list":
        rows = c.execute("SELECT * FROM vetoes WHERE status='active' ORDER BY created").fetchall()
        if not rows: ok("(no active vetoes)"); return
        for r in rows:
            ok(f"[{r['severity'].upper():<8}] {r['id']}  {r['role']} blocks {r['target_type']}:{r['target']}")
            ok(f"           reason: {r['reason']}\n           lift when: {r['lift_conditions']}")
        return
    if sub == "raise":
        need(d, "role", "domain", "target", "reason", "evidence", "severity", "remediation", "lift_conditions")
        r = c.execute("SELECT veto_holders FROM decision_rights WHERE domain=?", (d["domain"],)).fetchone()
        if not r: die(f"unknown domain '{d['domain']}'")
        holders = [x for x in r["veto_holders"].split(",") if x]
        if d["role"] not in holders:
            die(f"'{d['role']}' holds no veto over '{d['domain']}'. Veto holders: {', '.join(holders) or 'none'}.\n"
                "         Arbitrary vetoes are not permitted - escalate instead.")
        vid = "VETO-" + hashlib.sha1(f"{d['target']}{now()}".encode()).hexdigest()[:6].upper()
        c.execute("""INSERT INTO vetoes(id,target_type,target,role,domain,reason,evidence,severity,
                     remediation,lift_conditions,status,created)
                     VALUES(?,?,?,?,?,?,?,?,?,?,'active',?)""",
                  (vid, d.get("target_type","release"), d["target"], d["role"], d["domain"],
                   d["reason"], d["evidence"], d["severity"], d["remediation"], d["lift_conditions"], now()))
        log(c, "veto_raised", d["role"], "veto", vid, d["reason"]); c.commit()
        ok(f"{vid} RAISED by {d['role']} over {d['target_type'] if d.get('target_type') else 'release'}:{d['target']}")
        ok(f"  severity: {d['severity']}\n  remediation: {d['remediation']}\n  lifts when: {d['lift_conditions']}")
        return
    if sub == "lift":
        need(d, "id", "role", "note")
        v = c.execute("SELECT * FROM vetoes WHERE id=?", (d["id"],)).fetchone()
        if not v: die(f"no veto '{d['id']}'")
        if v["role"] != d["role"]:
            die(f"only {v['role']} (who raised it) may lift {d['id']}. "
                "A veto cannot be lifted by the party it blocks.")
        c.execute("UPDATE vetoes SET status='lifted', lifted=? WHERE id=?", (now(), d["id"]))
        log(c, "veto_lifted", d["role"], "veto", d["id"], d["note"]); c.commit()
        ok(f"{d['id']} lifted by {d['role']}: {d['note']}")

# --------------------------------------------------------------- decisions
def cmd_decision(argv):
    if not argv: die("usage: decision new|approve|decide|dissent|show|list ...")
    sub = argv[0]; d = kv(argv[1:]); c = db()
    if sub == "list":
        for r in c.execute("SELECT * FROM decisions ORDER BY date DESC"):
            ok(f"[{r['status']:<12}] {r['id']}  {r['title'][:52]:<52} owner={r['owner']}")
        return
    if sub == "new":
        need(d, "title", "owner", "domain")
        rr = c.execute("SELECT * FROM decision_rights WHERE domain=?", (d["domain"],)).fetchone()
        if not rr: die(f"unknown domain '{d['domain']}'")
        if d["owner"] != rr["owner"]:
            die(f"'{d['owner']}' does not own '{d['domain']}'. Owner is '{rr['owner']}'.")
        n = c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0] + 1
        did = f"DEC-{n:03d}"
        c.execute("""INSERT INTO decisions(id,date,domain,title,problem,context,options,args_for,
                     args_against,risks,rejected,owner,confidence,status)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'proposed')""",
                  (did, now()[:10], d["domain"], d["title"], d.get("problem",""), d.get("context",""),
                   d.get("options",""), d.get("args_for",""), d.get("args_against",""),
                   d.get("risks",""), d.get("rejected",""), d["owner"], d.get("confidence","MEDIUM")))
        for ev in [x for x in d.get("evidence","").split(",") if x]:
            c.execute("INSERT OR IGNORE INTO decision_evidence VALUES(?,?)", (did, ev))
        log(c, "decision_new", d["owner"], "decision", did, d["title"]); c.commit()
        ok(f"{did} proposed by {d['owner']} in domain '{d['domain']}'")
        ok(f"  required reviewers: {rr['reviewers'] or 'none'}")
        if rr["founder_required"]: ok("  FOUNDER APPROVAL REQUIRED before this can be decided")
        return
    if sub == "dissent":
        need(d, "id", "role", "position", "argument")
        c.execute("INSERT INTO dissent(decision,role,position,argument,created) VALUES(?,?,?,?,?)",
                  (d["id"], d["role"], d["position"], d["argument"], now()))
        log(c, "dissent", d["role"], "decision", d["id"]); c.commit()
        ok(f"dissent recorded on {d['id']} by {d['role']} - preserved verbatim, never averaged away")
        return
    if sub == "approve":
        need(d, "id", "role")
        dec = c.execute("SELECT * FROM decisions WHERE id=?", (d["id"],)).fetchone()
        if not dec: die(f"no decision '{d['id']}'")
        rr = c.execute("SELECT * FROM decision_rights WHERE domain=?", (dec["domain"],)).fetchone()
        allowed = [x for x in rr["reviewers"].split(",") if x] + [rr["owner"]]
        if d["role"] not in allowed:
            die(f"'{d['role']}' is not a reviewer for '{dec['domain']}'. Reviewers: {rr['reviewers']}")
        ap = [x for x in (dec["approvers"] or "").split(",") if x]
        if d["role"] not in ap: ap.append(d["role"])
        c.execute("UPDATE decisions SET approvers=?,status='under_review' WHERE id=?", (",".join(ap), d["id"]))
        log(c, "decision_approve", d["role"], "decision", d["id"]); c.commit()
        ok(f"{d['id']} approved by {d['role']}  ({len(ap)}/{len([x for x in rr['reviewers'].split(',') if x])} reviewers)")
        return
    if sub == "decide":
        need(d, "id", "role", "decision")
        dec = c.execute("SELECT * FROM decisions WHERE id=?", (d["id"],)).fetchone()
        if not dec: die(f"no decision '{d['id']}'")
        rr = c.execute("SELECT * FROM decision_rights WHERE domain=?", (dec["domain"],)).fetchone()
        if d["role"] != rr["owner"]: die(f"only '{rr['owner']}' may decide '{dec['domain']}'")
        v = c.execute("SELECT * FROM vetoes WHERE target=? AND status='active'", (d["id"],)).fetchone()
        if v: die(f"BLOCKED by {v['id']} ({v['role']}, {v['severity']}): {v['reason']}\n"
                  f"         lifts when: {v['lift_conditions']}")
        need_rev = [x for x in rr["reviewers"].split(",") if x]
        have = [x for x in (dec["approvers"] or "").split(",") if x]
        missing = [x for x in need_rev if x not in have]
        if missing: die(f"missing required review from: {', '.join(missing)}")
        if rr["founder_required"] and not d.get("founder_approval"):
            die(f"'{dec['domain']}' requires founder approval. Re-run with founder_approval=<what they approved>.")
        c.execute("UPDATE decisions SET decision=?,status='decided',outcome=?,review_date=? WHERE id=?",
                  (d["decision"], d.get("outcome",""), d.get("review_date",""), d["id"]))
        log(c, "decision_decided", d["role"], "decision", d["id"], d["decision"]); c.commit()
        ok(f"{d['id']} DECIDED by {d['role']}")
        n = c.execute("SELECT COUNT(*) FROM dissent WHERE decision=?", (d["id"],)).fetchone()[0]
        if n: ok(f"  {n} dissenting opinion(s) preserved on the record")
        return
    if sub == "show":
        need(d, "id")
        r = c.execute("SELECT * FROM decisions WHERE id=?", (d["id"],)).fetchone()
        if not r: die("not found")
        for k in r.keys():
            if r[k]: ok(f"{k:<18} {r[k]}")
        for x in c.execute("SELECT * FROM dissent WHERE decision=?", (d["id"],)):
            ok(f"DISSENT ({x['role']}) {x['position']}: {x['argument']}")
        for e in c.execute("SELECT research FROM decision_evidence WHERE decision=?", (d["id"],)):
            ok(f"EVIDENCE           {e['research']}")

# --------------------------------------------------------------- tasks
def cmd_task(argv):
    if not argv: die("usage: task add|update|list|ready|graph ...")
    sub = argv[0]; d = kv(argv[1:]); c = db()
    if sub == "add":
        need(d, "title", "owner")
        for r in (d["owner"], d.get("reviewer")):
            if r and not c.execute("SELECT 1 FROM agents WHERE id=?", (r,)).fetchone():
                die(f"'{r}' is not a registered agent")
        if d.get("reviewer") == d["owner"]:
            die("separation of duties: an agent may not review its own work")
        n = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        tid = d.get("id") or f"T{n+1:04d}"
        while c.execute("SELECT 1 FROM tasks WHERE id=?", (tid,)).fetchone():
            n += 1; tid = f"T{n+1:04d}"
        c.execute("""INSERT INTO tasks(id,parent,kind,project,title,owner,reviewer,department,
                     objective,acceptance,priority,risk,phase,parallel_group,created,updated)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (tid, d.get("parent"), d.get("kind","task"), d.get("project"), d["title"],
                   d["owner"], d.get("reviewer"), d.get("department"), d.get("objective",""),
                   d.get("acceptance",""), int(d.get("priority",3)), d.get("risk","low"),
                   d.get("phase"), d.get("parallel_group"), now(), now()))
        for dep in [x for x in d.get("deps","").split(",") if x]:
            if not c.execute("SELECT 1 FROM tasks WHERE id=?", (dep,)).fetchone():
                die(f"dependency '{dep}' does not exist - create it first")
            c.execute("INSERT INTO task_deps VALUES(?,?)", (tid, dep))
        log(c, "task_add", d["owner"], "task", tid, d["title"]); c.commit()
        ok(f"{tid}  {d['title']}  -> {d['owner']}" + (f"  (reviewer: {d['reviewer']})" if d.get("reviewer") else ""))
        return
    if sub == "update":
        need(d, "id", "status")
        t = c.execute("SELECT * FROM tasks WHERE id=?", (d["id"],)).fetchone()
        if not t: die(f"no task '{d['id']}'")
        if d["status"] == "done":
            ev = d.get("evidence") or t["evidence"]
            if not ev: die("cannot mark done without evidence=<path>. No fake completion.")
            if t["acceptance"] and not d.get("acceptance_verified"):
                die("this task has acceptance criteria. Pass acceptance_verified=<how they were verified>.")
            if t["reviewer"] and not d.get("reviewed_by"):
                die(f"independent review required from '{t['reviewer']}'. Pass reviewed_by={t['reviewer']}.")
            if d.get("reviewed_by") and d["reviewed_by"] == t["owner"]:
                die("separation of duties: the owner cannot be the reviewer")
        att = t["attempts"] + (1 if d["status"] == "failed" else 0)
        c.execute("UPDATE tasks SET status=?,evidence=COALESCE(?,evidence),blocked_on=?,attempts=?,updated=? WHERE id=?",
                  (d["status"], d.get("evidence"), d.get("blocked_on"), att, now(), d["id"]))
        c.execute("INSERT INTO agent_performance(role,task,outcome,rework,escalated,recorded) VALUES(?,?,?,?,?,?)",
                  (t["owner"], d["id"], d["status"], 1 if d["status"]=="failed" else 0, 0, now()))
        log(c, "task_update", t["owner"], "task", d["id"], d["status"]); c.commit()
        ok(f"{d['id']} -> {d['status']}")
        if att >= 2 and d["status"] == "failed":
            ok("  ANTI-LOOP: 2+ failures. Do not retry unchanged - dispatch problem-solver or escalate.")
        return
    if sub == "list":
        q = "SELECT * FROM tasks"; p = []
        if d.get("status"): q += " WHERE status=?"; p.append(d["status"])
        for t in c.execute(q + " ORDER BY priority, id", p):
            deps = [r["depends_on"] for r in c.execute("SELECT depends_on FROM task_deps WHERE task=?", (t["id"],))]
            ok(f"[{t['status']:<11}] {t['id']:<7}{t['title'][:44]:<44} {t['owner'][:20]:<20}"
               + (f" deps={','.join(deps)}" if deps else ""))
        return
    if sub == "ready":
        done = {r["id"] for r in c.execute("SELECT id FROM tasks WHERE status IN ('done','cancelled','accepted_risk')")}
        groups = {}
        for t in c.execute("SELECT * FROM tasks WHERE status='todo'"):
            deps = {r["depends_on"] for r in c.execute("SELECT depends_on FROM task_deps WHERE task=?", (t["id"],))}
            if deps - done: continue
            groups.setdefault(t["parallel_group"] or "_ungrouped", []).append(t)
        if not groups: ok("(nothing ready)"); return
        ok("READY - dispatch each group in ONE message so they run concurrently:\n")
        for g, ts in groups.items():
            ok(f"  group '{g}' ({len(ts)} parallel):")
            for t in ts: ok(f"    {t['id']:<7}{t['title'][:46]:<46} -> {t['owner']}")
        return
    if sub == "graph":
        ok("TASK DEPENDENCY GRAPH")
        for t in c.execute("SELECT * FROM tasks ORDER BY id"):
            deps = [r["depends_on"] for r in c.execute("SELECT depends_on FROM task_deps WHERE task=?", (t['id'],))]
            ok(f"  {t['id']} [{t['status']}] {t['title'][:40]}" + (f"  <- {', '.join(deps)}" if deps else "  (root)"))

def cmd_handoff(argv):
    d = kv(argv)
    need(d, "from_role", "to_role", "work_done", "next_action")
    c = db()
    c.execute("""INSERT INTO handoffs(task,from_role,to_role,context,work_done,evidence,artifacts,
                 decisions,open_questions,risks,next_action,acceptance,created)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (d.get("task"), d["from_role"], d["to_role"], d.get("context",""), d["work_done"],
               d.get("evidence",""), d.get("artifacts",""), d.get("decisions",""),
               d.get("open_questions",""), d.get("risks",""), d["next_action"], d.get("acceptance",""), now()))
    log(c, "handoff", d["from_role"], "task", d.get("task")); c.commit()
    ok(f"handoff recorded: {d['from_role']} -> {d['to_role']}\n  next: {d['next_action']}")

# --------------------------------------------------------------- registers
def _simple_add(c, table, cols, d, prefix):
    n = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] + 1
    rid = d.get("id") or f"{prefix}-{n:03d}"
    vals = [rid] + [d.get(k, "") for k in cols] + [now()]
    c.execute(f"INSERT INTO {table}(id,{','.join(cols)},created) VALUES({','.join('?'*(len(cols)+2))})", vals)
    return rid

def cmd_risk(argv):
    d = kv(argv[1:] if argv and argv[0] in ("add","list") else argv); c = db()
    if argv and argv[0] == "list":
        for r in c.execute("SELECT * FROM risks WHERE status='open' ORDER BY severity DESC"):
            ok(f"[{r['severity']:<8}] {r['id']}  {r['description'][:50]:<50} owner={r['owner']}")
        return
    need(d, "description", "owner", "probability", "impact", "severity")
    if not c.execute("SELECT 1 FROM agents WHERE id=?", (d["owner"],)).fetchone():
        die(f"'{d['owner']}' is not a registered agent - every risk needs a real owner")
    rid = _simple_add(c, "risks", ["description","category","probability","impact","severity",
                                   "owner","evidence","mitigation","contingency"], d, "RISK")
    log(c, "risk_add", d["owner"], "risk", rid); c.commit(); ok(f"{rid} logged ({d['severity']}) owner={d['owner']}")

def cmd_experiment(argv):
    d = kv(argv[1:] if argv and argv[0] in ("add","result","list") else argv); c = db()
    if argv and argv[0] == "list":
        for r in c.execute("SELECT * FROM experiments ORDER BY created DESC"):
            ok(f"[{r['status']:<10}] {r['id']}  {r['hypothesis'][:48]:<48} metric={r['metric']}")
        return
    if argv and argv[0] == "result":
        need(d, "id", "result", "learning")
        c.execute("UPDATE experiments SET status='complete',result=?,learning=? WHERE id=?",
                  (d["result"], d["learning"], d["id"]))
        log(c, "experiment_result", entity=d["id"]); c.commit()
        ok(f"{d['id']} complete. Learning recorded - failed experiments are company knowledge too.")
        return
    need(d, "hypothesis", "metric")
    rid = _simple_add(c, "experiments", ["hypothesis","metric","threshold","owner"], d, "EXP")
    log(c, "experiment_add", entity=rid); c.commit(); ok(f"{rid} designed. Threshold set BEFORE running: {d.get('threshold','(none)')}")

def cmd_incident(argv):
    d = kv(argv[1:] if argv and argv[0] in ("open","resolve","list") else argv); c = db()
    if argv and argv[0] == "list":
        for r in c.execute("SELECT * FROM incidents ORDER BY created DESC"):
            ok(f"[{r['status']:<10}] {r['id']}  {r['title'][:50]}  sev={r['severity']}")
        return
    if argv and argv[0] == "resolve":
        need(d, "id", "postmortem", "preventive_action")
        c.execute("UPDATE incidents SET status='resolved',postmortem=?,preventive_action=?,resolved=? WHERE id=?",
                  (d["postmortem"], d["preventive_action"], now(), d["id"]))
        log(c, "incident_resolved", entity=d["id"]); c.commit()
        ok(f"{d['id']} resolved. Postmortem is now institutional memory.")
        return
    need(d, "title", "severity")
    rid = _simple_add(c, "incidents", ["title","severity","owner","detection","diagnosis"], d, "INC")
    log(c, "incident_open", entity=rid); c.commit(); ok(f"{rid} opened ({d['severity']})")

def cmd_release(argv):
    if not argv: die("usage: release new|check|approve|ship ...")
    sub = argv[0]; d = kv(argv[1:]); c = db()
    GATES = ["product_ready","engineering_ready","qa_passed","security_passed",
             "performance_ok","docs_ready","rollback_ready"]
    if sub == "new":
        need(d, "version")
        rid = f"REL-{d['version']}"
        c.execute("INSERT INTO releases(id,version,status,created) VALUES(?,?,'preparing',?)",
                  (rid, d["version"], now()))
        log(c, "release_new", entity=rid); c.commit(); ok(f"{rid} created")
        return
    if sub == "check":
        need(d, "id")
        r = c.execute("SELECT * FROM releases WHERE id=?", (d["id"],)).fetchone()
        if not r: die("not found")
        ok(f"RELEASE {r['id']} [{r['status']}]")
        for g in GATES: ok(f"  [{'x' if r[g] else ' '}] {g}")
        v = c.execute("SELECT * FROM vetoes WHERE target=? AND status='active'", (d["id"],)).fetchall()
        for x in v: ok(f"  VETO {x['id']} by {x['role']} ({x['severity']}): {x['reason']}")
        ok(f"  founder approval: {r['founder_approval'] or 'NOT GIVEN'}")
        return
    if sub == "approve":
        need(d, "id", "gate", "role")
        if d["gate"] not in GATES: die(f"gate must be one of: {', '.join(GATES)}")
        c.execute(f"UPDATE releases SET {d['gate']}=1 WHERE id=?", (d["id"],))
        log(c, "release_gate", d["role"], "release", d["id"], d["gate"]); c.commit()
        ok(f"{d['id']}: {d['gate']} approved by {d['role']}")
        return
    if sub == "ship":
        need(d, "id", "role")
        r = c.execute("SELECT * FROM releases WHERE id=?", (d["id"],)).fetchone()
        if not r: die("not found")
        missing = [g for g in GATES if not r[g]]
        if missing: die(f"cannot ship - gates not met: {', '.join(missing)}")
        v = c.execute("SELECT * FROM vetoes WHERE target=? AND status='active'", (d["id"],)).fetchone()
        if v: die(f"BLOCKED by {v['id']} ({v['role']}, {v['severity']}): {v['reason']}\n"
                  f"         lifts when: {v['lift_conditions']}")
        if not d.get("founder_approval"):
            die("release requires founder authorization. Re-run with founder_approval=<what they approved>.")
        c.execute("UPDATE releases SET status='released',released=?,founder_approval=? WHERE id=?",
                  (now(), d["founder_approval"], d["id"]))
        log(c, "release_ship", d["role"], "release", d["id"]); c.commit()
        ok(f"{d['id']} RELEASED (founder: {d['founder_approval']})")

def cmd_escalate(argv):
    d = kv(argv); need(d, "level", "subject", "raised_by"); c = db()
    lvl = int(d["level"])
    n = c.execute("SELECT COUNT(*) FROM escalations").fetchone()[0] + 1
    eid = f"ESC-{n:03d}"
    if lvl == 4 and not d.get("recommendation"):
        die("a founder escalation without a recommendation is abdication. Provide recommendation=...")
    c.execute("""INSERT INTO escalations(id,level,subject,raised_by,recommendation,evidence,risks,created)
                 VALUES(?,?,?,?,?,?,?,?)""",
              (eid, lvl, d["subject"], d["raised_by"], d.get("recommendation",""),
               d.get("evidence",""), d.get("risks",""), now()))
    log(c, "escalation", d["raised_by"], "escalation", eid, d["subject"]); c.commit()
    names = {0:"agent self-resolve",1:"peer specialist",2:"department lead",3:"executive",4:"FOUNDER"}
    ok(f"{eid} escalated to level {lvl} ({names[lvl]}): {d['subject']}")

def cmd_memory(argv):
    if not argv: die("usage: memory put|get|list ...")
    sub = argv[0]; d = kv(argv[1:]); c = db()
    if sub == "put":
        need(d, "tier", "topic", "content")
        if d["tier"] == "permanent" and d.get("actor") not in ("ceo","founder","chief-people-officer"):
            die("permanent memory may only be written by the CEO, the founder, or the Chief People Officer. "
                "Pass actor=<role>.")
        mid = d.get("id") or "MEM-" + hashlib.sha1(f"{d['topic']}".encode()).hexdigest()[:8]
        prev = c.execute("SELECT version FROM memory WHERE id=?", (mid,)).fetchone()
        ver = (prev["version"] + 1) if prev else 1
        c.execute("""INSERT OR REPLACE INTO memory(id,tier,topic,content,owner,source,created,updated,expires,review_after,version)
                     VALUES(?,?,?,?,?,?,COALESCE((SELECT created FROM memory WHERE id=?),?),?,?,?,?)""",
                  (mid, d["tier"], d["topic"], d["content"], d.get("owner"), d.get("source"),
                   mid, now(), now(), d.get("expires"), d.get("review_after"), ver))
        log(c, "memory_put", d.get("actor"), "memory", mid, f"v{ver} {d['tier']}"); c.commit()
        ok(f"{mid} stored in {d['tier']} memory (v{ver})")
        return
    if sub == "list":
        q = "SELECT * FROM memory" + (" WHERE tier=?" if d.get("tier") else "")
        for r in c.execute(q + " ORDER BY tier,topic", ([d["tier"]] if d.get("tier") else [])):
            ok(f"[{r['tier']:<10}] {r['id']}  v{r['version']}  {r['topic'][:44]:<44} {r['content'][:40]}")
        return
    if sub == "get":
        need(d, "topic")
        for r in c.execute("SELECT * FROM memory WHERE topic LIKE ?", (f"%{d['topic']}%",)):
            ok(f"{r['id']} [{r['tier']} v{r['version']}] {r['topic']}\n  {r['content']}")

def cmd_link(argv):
    """Knowledge graph edge: link src_type=customer src=C1 relation=has_problem dst_type=problem dst=P1"""
    d = kv(argv); need(d, "src_type", "src", "relation", "dst_type", "dst"); c = db()
    c.execute("INSERT OR REPLACE INTO knowledge_edges VALUES(?,?,?,?,?)",
              (d["src_type"], d["src"], d["relation"], d["dst_type"], d["dst"]))
    log(c, "link", entity=f"{d['src']}->{d['dst']}"); c.commit()
    ok(f"{d['src_type']}:{d['src']} --{d['relation']}--> {d['dst_type']}:{d['dst']}")

def cmd_trace(argv):
    """Follow the knowledge graph from a node - customer -> problem -> requirement -> ... -> decision."""
    if not argv: die("usage: trace <node-id> [depth]")
    start = argv[0]; depth = int(argv[1]) if len(argv) > 1 else 5; c = db()
    seen = set()
    def walk(n, d, pre):
        if d <= 0 or n in seen: return
        seen.add(n)
        for e in c.execute("SELECT * FROM knowledge_edges WHERE src=?", (n,)):
            ok(f"{pre}--{e['relation']}--> {e['dst_type']}:{e['dst']}")
            walk(e["dst"], d - 1, pre + "  ")
    ok(f"TRACE from {start}"); walk(start, depth, "  ")
    if not seen - {start}: ok("  (no outgoing edges)")

# --------------------------------------------------------------- oversight
def cmd_dashboard(argv):
    c = db()
    def one(q, p=()): 
        r = c.execute(q, p).fetchone(); return r[0] if r else 0
    ok("=" * 62); ok("  COMPANY STATUS"); ok("=" * 62)
    ok(f"\nORGANIZATION   {one('SELECT COUNT(*) FROM agents')} agents across "
       f"{one('SELECT COUNT(*) FROM departments')} departments")
    ok(f"               {one('SELECT COUNT(*) FROM decision_rights')} decision domains defined")
    ok(f"\nTASKS")
    for r in c.execute("SELECT status, COUNT(*) n FROM tasks GROUP BY status ORDER BY n DESC"):
        ok(f"  {r['status']:<14}{r['n']}")
    if not one("SELECT COUNT(*) FROM tasks"): ok("  (none)")
    bl = c.execute("SELECT * FROM tasks WHERE status IN ('blocked','failed')").fetchall()
    if bl:
        ok("\nBLOCKED / FAILED")
        for t in bl: ok(f"  {t['id']} {t['title'][:44]:<44} {t['blocked_on'] or ''}")
    ok(f"\nDECISIONS      {one('SELECT COUNT(*) FROM decisions')} total, "
       f"{one(chr(39).join(['SELECT COUNT(*) FROM decisions WHERE status=','decided','']))} decided, "
       f"{one('SELECT COUNT(*) FROM dissent')} dissenting opinions preserved")
    va = c.execute("SELECT * FROM vetoes WHERE status='active'").fetchall()
    ok(f"\nVETOES         {len(va)} active")
    for v in va: ok(f"  {v['id']} {v['role']} blocks {v['target']} ({v['severity']}): {v['reason'][:44]}")
    ok(f"\nRISKS          {one(chr(39).join(['SELECT COUNT(*) FROM risks WHERE status=','open','']))} open")
    for r in c.execute("SELECT * FROM risks WHERE status='open' ORDER BY severity DESC LIMIT 5"):
        ok(f"  [{r['severity']:<8}] {r['description'][:48]}")
    ok(f"\nQUALITY        {one(chr(39).join(['SELECT COUNT(*) FROM bugs WHERE status=','open','']))} open bugs")
    ok(f"EXPERIMENTS    {one('SELECT COUNT(*) FROM experiments')} "
       f"({one(chr(39).join(['SELECT COUNT(*) FROM experiments WHERE status=','complete','']))} complete)")
    ok(f"INCIDENTS      {one(chr(39).join(['SELECT COUNT(*) FROM incidents WHERE status=','open','']))} open")
    ok(f"RESEARCH       {one('SELECT COUNT(*) FROM research')} studies, "
       f"{one('SELECT COUNT(*) FROM evidence')} evidence records")
    esc = c.execute("SELECT * FROM escalations WHERE status='open' AND level=4").fetchall()
    ok(f"\nAWAITING FOUNDER  {len(esc)}")
    for e in esc: ok(f"  {e['id']} {e['subject']}\n      recommends: {e['recommendation'][:60]}")
    ok(f"\nAUDIT LOG      {one('SELECT COUNT(*) FROM audit_log')} recorded events")
    ok("=" * 62)

def cmd_recover(argv):
    """State recovery after an interruption - what completed, what is pending, what to do next."""
    c = db()
    ok("STATE RECOVERY\n")
    ok("COMPLETED")
    for t in c.execute("SELECT * FROM tasks WHERE status='done' ORDER BY updated DESC LIMIT 8"):
        ok(f"  {t['id']} {t['title'][:50]}")
    if not c.execute("SELECT 1 FROM tasks WHERE status='done'").fetchone(): ok("  (none)")
    ok("\nIN PROGRESS - resume these first")
    for t in c.execute("SELECT * FROM tasks WHERE status='in_progress'"):
        ok(f"  {t['id']} {t['title'][:44]:<44} owner={t['owner']}")
    ok("\nBLOCKED")
    for t in c.execute("SELECT * FROM tasks WHERE status='blocked'"):
        ok(f"  {t['id']} {t['title'][:40]:<40} blocked_on={t['blocked_on']}")
    ok("\nFAILED - read incidents before retrying; never repeat a failed approach")
    for t in c.execute("SELECT * FROM tasks WHERE status='failed'"):
        ok(f"  {t['id']} {t['title'][:40]:<40} attempts={t['attempts']}")
    ok("\nPENDING (ready to dispatch)"); cmd_task(["ready"])
    ok("\nACTIVE VETOES"); cmd_veto(["list"])
    ok("\nLAST 5 EVENTS")
    for r in c.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 5"):
        ok(f"  {r['ts']}  {r['action']:<20}{r['entity'] or ''}")

def cmd_verify(argv):
    """Integrity check of the company itself."""
    c = db(); errs = []
    for t in c.execute("SELECT * FROM tasks"):
        if t["status"] == "done" and not t["evidence"]: errs.append(f"{t['id']}: done without evidence")
        if t["reviewer"] and t["reviewer"] == t["owner"]: errs.append(f"{t['id']}: reviewer == owner")
        if not c.execute("SELECT 1 FROM agents WHERE id=?", (t["owner"],)).fetchone():
            errs.append(f"{t['id']}: owner '{t['owner']}' not a registered agent")
    colour = {}
    def visit(n, st):
        if colour.get(n) == 2: return
        if colour.get(n) == 1: errs.append("dependency cycle: " + " -> ".join(st + [n])); return
        colour[n] = 1
        for r in c.execute("SELECT depends_on FROM task_deps WHERE task=?", (n,)): visit(r["depends_on"], st + [n])
        colour[n] = 2
    for t in c.execute("SELECT id FROM tasks"): visit(t["id"], [])
    for r in c.execute("SELECT * FROM decision_rights"):
        for who in [r["owner"]] + [x for x in (r["reviewers"] + "," + r["veto_holders"]).split(",") if x]:
            if not c.execute("SELECT 1 FROM agents WHERE id=?", (who,)).fetchone():
                errs.append(f"decision_rights[{r['domain']}]: '{who}' not a registered agent")
    for d_ in c.execute("SELECT * FROM decisions WHERE status='decided'"):
        rr = c.execute("SELECT * FROM decision_rights WHERE domain=?", (d_["domain"],)).fetchone()
        if rr:
            missing = [x for x in rr["reviewers"].split(",") if x and x not in (d_["approvers"] or "")]
            if missing: errs.append(f"{d_['id']}: decided without review from {', '.join(missing)}")
    if errs:
        ok(f"VERIFY FAILED - {len(errs)} issue(s)"); [ok("  " + e) for e in errs]; sys.exit(1)
    n = lambda t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    ok(f"VERIFY PASSED  agents={n('agents')} domains={n('decision_rights')} tasks={n('tasks')} "
       f"decisions={n('decisions')} risks={n('risks')} vetoes={n('vetoes')}")

def cmd_help(argv):
    print(__doc__)
    print("""Commands
  init [--force]                          build the database from the role registry
  authority [domain]                      decision-rights matrix
  can <role> <decide|approve|review|veto> <domain>     authority check (exit 0 allowed / 2 denied)
  veto raise|lift|list                    domain-limited blocking authority
  decision new|approve|decide|dissent|show|list
  task add|update|list|ready|graph
  handoff from_role= to_role= work_done= next_action= [evidence= risks= ...]
  risk add|list      experiment add|result|list      incident open|resolve|list
  release new|check|approve|ship          memory put|get|list
  link / trace                            knowledge graph
  escalate level= subject= raised_by= [recommendation=]
  dashboard                               founder view
  recover                                 state recovery after interruption
  verify                                  integrity check
""")

CMDS = {"init":cmd_init,"authority":cmd_authority,"can":cmd_can,"veto":cmd_veto,
        "decision":cmd_decision,"task":cmd_task,"handoff":cmd_handoff,"risk":cmd_risk,
        "experiment":cmd_experiment,"incident":cmd_incident,"release":cmd_release,
        "escalate":cmd_escalate,"memory":cmd_memory,"link":cmd_link,"trace":cmd_trace,
        "dashboard":cmd_dashboard,"recover":cmd_recover,"verify":cmd_verify,"help":cmd_help}
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS: cmd_help([]); sys.exit(0 if len(sys.argv) < 2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
