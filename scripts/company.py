#!/usr/bin/env python3
"""company.py - durable state engine for the AI Company OS.

Every phase and task transition is written to disk immediately, so a run survives
session limits, crashes and restarts. `resume` reports exactly where to continue.

Usage:  python3 scripts/company.py <command> [args]
Run    `python3 scripts/company.py help`  for the full command list.
"""
import json, sys, os, pathlib, datetime, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / ".ai-company/state"
SOP = ROOT / ".ai-company/sop"
RUN = STATE / "run.json"
TASKS = STATE / "tasks.json"
GATES = STATE / "gates.json"
LOG = ROOT / ".ai-company/logs/events.jsonl"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def jload(p, d=None):
    if p.exists():
        try: return json.loads(p.read_text())
        except json.JSONDecodeError: return d
    return d
def jdump(p, o):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(o, indent=2)); tmp.replace(p)   # atomic: never a torn state file
def event(kind, **kw):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f: f.write(json.dumps({"ts": now(), "event": kind, **kw}) + "\n")
def phases(): return jload(SOP/"phases.json", {"phases": []})["phases"]
def gatedefs(): return jload(SOP/"gates.json", {"gates": {}})["gates"]
def die(m): print(f"ERROR: {m}", file=sys.stderr); sys.exit(1)

# ---------------------------------------------------------------- run lifecycle
def cmd_init(argv):
    if len(argv) < 2: die("usage: init <industry> <idea> [constraints]")
    industry, idea = argv[0], argv[1]
    constraints = argv[2] if len(argv) > 2 else ""
    if RUN.exists() and jload(RUN, {}).get("status") == "active":
        die("a run is already active. Use `status`, `resume`, or `archive` first.")
    rid = "run_" + hashlib.sha1(f"{industry}{idea}{now()}".encode()).hexdigest()[:10]
    jdump(RUN, {"run_id": rid, "created": now(), "updated": now(), "status": "active",
                "industry": industry, "idea": idea, "constraints": constraints,
                "current_phase": "intake", "completed_phases": [],
                "gates": {g: {"status": "pending"} for g in gatedefs()},
                "escalations": [], "notes": []})
    jdump(TASKS, {"version": 1, "tasks": []})
    event("run_init", run_id=rid, industry=industry)
    print(f"run initialized: {rid}\nindustry: {industry}\nidea: {idea}\nphase: intake")

def _run():
    r = jload(RUN)
    if not r: die("no run. `init <industry> <idea>` first.")
    return r
def _save(r): r["updated"] = now(); jdump(RUN, r)

def cmd_status(_):
    r = _run(); ts = jload(TASKS, {"tasks": []})["tasks"]
    ph = {p["id"]: p for p in phases()}
    cur = ph.get(r["current_phase"], {})
    by = {}
    for t in ts: by[t["status"]] = by.get(t["status"], 0) + 1
    print(f"RUN         {r['run_id']}  [{r['status']}]")
    print(f"INDUSTRY    {r['industry']}")
    print(f"IDEA        {r['idea'][:80]}")
    if r.get("constraints"): print(f"CONSTRAINTS {r['constraints'][:80]}")
    print(f"\nPHASE       {r['current_phase']}  ({cur.get('name','?')})  owner={cur.get('owner','?')}")
    print(f"COMPLETED   {len(r['completed_phases'])}/{len(phases())}  {', '.join(r['completed_phases']) or '-'}")
    print(f"\nTASKS       " + ("  ".join(f"{k}={v}" for k, v in sorted(by.items())) if by else "none"))
    blocked = [t for t in ts if t["status"] == "blocked"]
    failed  = [t for t in ts if t["status"] == "failed"]
    if blocked:
        print("\nBLOCKED");  [print(f"  {t['id']:22} {t['title'][:50]}  <- {t.get('blocked_on','?')}") for t in blocked]
    if failed:
        print("\nFAILED");   [print(f"  {t['id']:22} {t['title'][:50]}  ({t.get('attempts',0)} attempts)") for t in failed]
    print("\nGATES")
    for g, st in r["gates"].items():
        mark = {"passed":"PASS","failed":"FAIL","pending":"....","blocked":"BLOCK"}.get(st["status"], "?")
        extra = f"  {st.get('note','')}" if st.get("note") else ""
        print(f"  [{mark}] {g}{extra}")
    if r["escalations"]:
        print("\nAWAITING FOUNDER")
        for e in r["escalations"]:
            if e.get("status") == "open": print(f"  - {e['subject']}")

def cmd_resume(_):
    """The recovery entry point: says exactly what to do next."""
    r = _run(); ph = phases(); done = set(r["completed_phases"])
    ts = jload(TASKS, {"tasks": []})["tasks"]
    print(f"RESUMING {r['run_id']}\n  industry: {r['industry']}\n  idea: {r['idea'][:70]}\n")
    stuck = [t for t in ts if t["status"] in ("in_progress", "blocked", "failed")]
    if stuck:
        print("Unfinished tasks in the current phase - finish these first:")
        for t in stuck:
            print(f"  [{t['status']:11}] {t['id']:20} {t['title'][:46]}  owner={t['owner']}")
        print()
    nxt = None
    for p in ph:
        if p["id"] in done: continue
        missing = [d for d in p["depends_on"] if d not in done]
        if missing:
            print(f"Phase '{p['id']}' waits on: {', '.join(missing)}"); continue
        nxt = p; break
    if not nxt:
        print("All phases complete."); return
    print(f"NEXT PHASE   {nxt['id']} - {nxt['name']}")
    print(f"OWNER        {nxt['owner']}  (role pack: .ai-company/org/roles/*/{nxt['owner']}.md)")
    print(f"GATE         {nxt['gate']}")
    print("EXIT CRITERIA")
    for c in nxt["exit_criteria"]: print(f"  - {c}")
    print("ARTIFACTS TO PRODUCE")
    for a in nxt["artifacts"]:
        exists = (ROOT / a).exists()
        print(f"  [{'x' if exists else ' '}] {a}")

# ---------------------------------------------------------------- phases
def cmd_phase_start(argv):
    if not argv: die("usage: phase-start <phase_id>")
    pid = argv[0]; r = _run(); ph = {p["id"]: p for p in phases()}
    if pid not in ph: die(f"unknown phase '{pid}'")
    missing = [d for d in ph[pid]["depends_on"] if d not in r["completed_phases"]]
    if missing: die(f"phase '{pid}' depends on incomplete: {', '.join(missing)}")
    r["current_phase"] = pid; _save(r); event("phase_start", phase=pid)
    print(f"phase started: {pid} ({ph[pid]['name']}), owner {ph[pid]['owner']}")

def cmd_phase_complete(argv):
    if not argv: die("usage: phase-complete <phase_id>")
    pid = argv[0]; r = _run(); ph = {p["id"]: p for p in phases()}
    if pid not in ph: die(f"unknown phase '{pid}'")
    p = ph[pid]
    missing = [a for a in p["artifacts"] if not (ROOT/a).exists()]
    if missing:
        die("cannot complete - required artifacts missing:\n  " + "\n  ".join(missing) +
            "\nNo fake completion: write the artifacts, or mark the phase blocked.")
    g = p["gate"]
    if g != "gate_none" and r["gates"].get(g, {}).get("status") != "passed":
        die(f"cannot complete - gate '{g}' is '{r['gates'].get(g,{}).get('status')}', not passed.")
    open_t = [t for t in jload(TASKS,{"tasks":[]})["tasks"]
              if t.get("phase") == pid and t["status"] not in ("done","cancelled","accepted_risk")]
    if open_t: die(f"cannot complete - {len(open_t)} open task(s): " + ", ".join(t['id'] for t in open_t))
    if pid not in r["completed_phases"]: r["completed_phases"].append(pid)
    _save(r); event("phase_complete", phase=pid)
    print(f"phase complete: {pid}"); cmd_resume([])

# ---------------------------------------------------------------- tasks
def cmd_task_add(argv):
    kw = dict(a.split("=", 1) for a in argv if "=" in a)
    for req in ("title", "owner"):
        if req not in kw: die(f"usage: task-add title=... owner=... [phase=] [deps=a,b] [criteria=...] [parallel_group=]")
    d = jload(TASKS, {"version":1,"tasks":[]}); r = _run()
    # Monotonic ids. Never derive from len(): deleting a task would reuse a number and
    # silently rewire another task's dependencies. Found by the 2026-09-07 dry run.
    seq = d.get("next_id", 0)
    for t in d["tasks"]:
        if t["id"].startswith("T") and t["id"][1:].isdigit(): seq = max(seq, int(t["id"][1:]))
    tid = kw.get("id") or f"T{seq+1:03d}"
    if any(t["id"] == tid for t in d["tasks"]): die(f"task id '{tid}' already exists")
    d["next_id"] = max(seq + 1, d.get("next_id", 0))
    t = {"id": tid, "title": kw["title"], "owner": kw["owner"],
         "phase": kw.get("phase", r["current_phase"]),
         "status": "todo", "deps": [x for x in kw.get("deps","").split(",") if x],
         "criteria": [c for c in kw.get("criteria","").split(";") if c],
         "parallel_group": kw.get("parallel_group",""), "evidence": [],
         "attempts": 0, "created": now()}
    if tid in t["deps"]: die(f"task '{tid}' cannot depend on itself")
    unknown = [x for x in t["deps"] if x not in {y["id"] for y in d["tasks"]}]
    if unknown: die(f"unknown dependencies: {', '.join(unknown)} - add them before this task")
    d["tasks"].append(t); jdump(TASKS, d); event("task_add", task=tid, owner=t["owner"])
    print(f"added {tid}: {t['title']} -> {t['owner']}")

def cmd_task_update(argv):
    if not argv: die("usage: task-update <id> status=... [evidence=path] [blocked_on=...] [note=...]")
    tid = argv[0]; kw = dict(a.split("=",1) for a in argv[1:] if "=" in a)
    d = jload(TASKS, {"tasks":[]}); t = next((x for x in d["tasks"] if x["id"]==tid), None)
    if not t: die(f"no task '{tid}'")
    new = kw.get("status", t["status"])
    valid = ("todo","in_progress","blocked","failed","review","done","cancelled","accepted_risk")
    if new not in valid: die(f"status must be one of: {', '.join(valid)}")
    if new == "done":
        ev = [e for e in (t["evidence"] + [kw["evidence"]] if kw.get("evidence") else t["evidence"])]
        if not ev:
            die("cannot mark done without evidence. Pass evidence=<path>. "
                "Governance rule 15: never declare success without evidence.")
    if new == "failed": t["attempts"] = t.get("attempts",0) + 1
    if kw.get("evidence"): t["evidence"].append(kw["evidence"])
    for k in ("blocked_on","note"):
        if kw.get(k): t[k] = kw[k]
    t["status"] = new; t["updated"] = now()
    jdump(TASKS, d); event("task_update", task=tid, status=new)
    print(f"{tid} -> {new}")
    if t.get("attempts",0) >= 2 and new == "failed":
        print("  NOTE: 2+ failures. Governance rule 11: do not retry unchanged. "
              "Dispatch problem-solver or escalate to the COO.")

def cmd_task_list(argv):
    d = jload(TASKS, {"tasks":[]})["tasks"]
    filt = dict(a.split("=",1) for a in argv if "=" in a)
    for t in d:
        if any(t.get(k) != v for k, v in filt.items()): continue
        dep = f" deps={','.join(t['deps'])}" if t["deps"] else ""
        pg = f" grp={t['parallel_group']}" if t.get("parallel_group") else ""
        print(f"[{t['status']:11}] {t['id']:6} {t['title'][:44]:44} {t['owner'][:22]:22}{dep}{pg}")
    if not d: print("(no tasks)")

def cmd_ready(_):
    """Tasks whose dependencies are met - these may run in parallel."""
    d = jload(TASKS, {"tasks":[]})["tasks"]
    done = {t["id"] for t in d if t["status"] in ("done","accepted_risk","cancelled")}
    ready = [t for t in d if t["status"]=="todo" and all(x in done for x in t["deps"])]
    if not ready: print("(nothing ready)"); return
    groups = {}
    for t in ready: groups.setdefault(t.get("parallel_group") or "_ungrouped", []).append(t)
    print("READY TO DISPATCH - tasks within a group have no unresolved dependency and run in parallel:\n")
    for g, items in groups.items():
        print(f"  group '{g}' ({len(items)} parallel):")
        for t in items: print(f"    {t['id']:6} {t['title'][:50]:50} -> {t['owner']}")

def cmd_validate(_):
    """Structural integrity of the task graph and registry."""
    d = jload(TASKS, {"tasks":[]})["tasks"]; ids = {t["id"] for t in d}; errs = []
    for t in d:
        for dep in t["deps"]:
            if dep not in ids: errs.append(f"{t['id']}: dependency '{dep}' does not exist")
        if t["status"] == "in_progress" and not t["owner"]: errs.append(f"{t['id']}: in_progress with no owner")
        if t["status"] == "done" and not t["evidence"]: errs.append(f"{t['id']}: done with no evidence")
    # cycle detection
    colour = {}
    def visit(n, stack):
        if colour.get(n) == 2: return
        if colour.get(n) == 1: errs.append("dependency cycle: " + " -> ".join(stack + [n])); return
        colour[n] = 1
        for m in next((x["deps"] for x in d if x["id"] == n), []): visit(m, stack + [n])
        colour[n] = 2
    for t in d: visit(t["id"], [])
    reg = jload(ROOT/".ai-company/org/roles.json", {"roles":[]})["roles"]
    slugs = {r["slug"] for r in reg}
    for t in d:
        if t["owner"] and t["owner"] not in slugs:
            errs.append(f"{t['id']}: owner '{t['owner']}' is not a registered role")
    for r in reg:
        if not (ROOT/r["path"]).exists(): errs.append(f"role '{r['slug']}': pack missing at {r['path']}")
    for p in phases():
        if p["owner"] not in slugs: errs.append(f"phase '{p['id']}': owner '{p['owner']}' is not a registered role")
        if p["gate"] != "gate_none" and p["gate"] not in gatedefs(): errs.append(f"phase '{p['id']}': unknown gate '{p['gate']}'")
        for dep in p["depends_on"]:
            if dep not in {x["id"] for x in phases()}: errs.append(f"phase '{p['id']}': unknown dependency '{dep}'")
    if errs:
        print("VALIDATION FAILED"); [print("  " + e) for e in errs]; sys.exit(1)
    print(f"VALIDATION PASSED  ({len(d)} tasks, {len(reg)} roles, {len(phases())} phases, {len(gatedefs())} gates)")

# ---------------------------------------------------------------- gates
def cmd_gate(argv):
    if len(argv) < 2: die("usage: gate <gate_id> pass|fail|pending [note=...]")
    gid, verdict = argv[0], argv[1]
    kw = dict(a.split("=",1) for a in argv[2:] if "=" in a)
    r = _run(); gd = gatedefs()
    if gid not in gd: die(f"unknown gate '{gid}'. Known: {', '.join(gd)}")
    if verdict not in ("pass","fail","pending"): die("verdict must be pass, fail or pending")
    if verdict == "pass" and gd[gid].get("founder_required") and not kw.get("founder_approval"):
        die(f"gate '{gid}' requires founder authorization. "
            "Re-run with founder_approval=<what the founder actually approved>.")
    r["gates"][gid] = {"status": {"pass":"passed","fail":"failed","pending":"pending"}[verdict],
                       "by": kw.get("by",""), "note": kw.get("note",""), "at": now()}
    if kw.get("founder_approval"): r["gates"][gid]["founder_approval"] = kw["founder_approval"]
    _save(r); event("gate", gate=gid, verdict=verdict)
    print(f"{gid} -> {r['gates'][gid]['status']}")
    print("  criteria:"); [print(f"    - {c}") for c in gd[gid]["criteria"]]

def cmd_escalate(argv):
    kw = dict(a.split("=",1) for a in argv if "=" in a)
    if "subject" not in kw: die("usage: escalate subject=... [recommendation=] [why=] [risks=]")
    r = _run()
    r["escalations"].append({"at": now(), "status":"open", **kw})
    _save(r); event("escalation", subject=kw["subject"])
    print(f"ESCALATED TO FOUNDER: {kw['subject']}")
    print("  Present as a decision package: recommendation, why, evidence, alternatives,")
    print("  tradeoffs, risks, expected outcome, and what approval is required.")

def cmd_incident(argv):
    kw = dict(a.split("=",1) for a in argv if "=" in a)
    if "what" not in kw: die("usage: incident what=... [task=] [tried=] [next=]")
    p = ROOT/".ai-company/incidents"/f"{now().replace(':','-')}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"# Incident {now()}\n\n**What failed:** {kw['what']}\n\n"
                 f"**Task:** {kw.get('task','-')}\n\n**What was tried:** {kw.get('tried','-')}\n\n"
                 f"**Do not repeat:** the approach above failed. Change strategy.\n\n"
                 f"**Next approach:** {kw.get('next','-')}\n")
    event("incident", **kw); print(f"incident recorded: {p.relative_to(ROOT)}")

def cmd_help(_):
    print(__doc__)
    print("""Commands
  init <industry> <idea> [constraints]   start a run
  status                                 full run state
  resume                                 where to continue (use after any interruption)
  phase-start <id>                       begin a phase (checks dependencies)
  phase-complete <id>                    finish a phase (checks artifacts, gate, open tasks)
  task-add title=.. owner=.. [phase=] [deps=a,b] [criteria=a;b] [parallel_group=]
  task-update <id> status=.. [evidence=path] [blocked_on=] [note=]
  task-list [status=..] [owner=..]       list tasks
  ready                                  tasks dispatchable now, grouped for parallel execution
  validate                               check graph, roles, phases and gates for integrity
  gate <id> pass|fail|pending [by=] [note=] [founder_approval=]
  escalate subject=.. [recommendation=] [why=] [risks=]
  incident what=.. [task=] [tried=] [next=]
""")

CMDS = {"init":cmd_init,"status":cmd_status,"resume":cmd_resume,"phase-start":cmd_phase_start,
        "phase-complete":cmd_phase_complete,"task-add":cmd_task_add,"task-update":cmd_task_update,
        "task-list":cmd_task_list,"ready":cmd_ready,"validate":cmd_validate,"gate":cmd_gate,
        "escalate":cmd_escalate,"incident":cmd_incident,"help":cmd_help}
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS: cmd_help([]); sys.exit(0 if len(sys.argv)<2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
