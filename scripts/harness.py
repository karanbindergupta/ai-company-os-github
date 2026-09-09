#!/usr/bin/env python3
"""harness.py - the execution layer beneath the orchestrator.

The Company OS decides WHO / WHAT / WHY / AUTHORITY. This decides HOW execution is
recorded, permissioned, checkpointed, verified and recovered. It never makes a
decision the OS owns; it refuses to let one go unrecorded.

Design constraints, all load-bearing:
  * stdlib only, Python 3.9 compatible          (CLAUDE.md 9)
  * one database - .ai-company/state/company.db (D-2, no parallel stores)
  * never a second orchestrator                 (founder directive PHASE 3)
  * `claude` is NOT on PATH in this environment, so the harness does NOT spawn.
    Spawning stays with Claude Code's native Task tool. The harness wraps it.
  * migrations are versioned and idempotent     (founder directive PHASE 7)
"""
import sqlite3, json, sys, os, pathlib, datetime, hashlib, subprocess

R  = pathlib.Path(__file__).resolve().parent.parent
DB = R / ".ai-company/state/company.db"

def now(): return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
def die(m): print(f"REFUSED: {m}", file=sys.stderr); sys.exit(2)
def ok(m):  print(m)

# --------------------------------------------------------------- migrations
# Append-only. Never edit a shipped migration; add a new one.
MIGRATIONS = [
 (2, "harness execution ledger", """
 CREATE TABLE IF NOT EXISTS executions(
   id TEXT PRIMARY KEY, task TEXT, agent TEXT, parent TEXT, kind TEXT,
   status TEXT NOT NULL DEFAULT 'QUEUED', phase TEXT, objective TEXT,
   worktree TEXT, branch TEXT, base_commit TEXT,
   retries INTEGER DEFAULT 0, retry_budget INTEGER DEFAULT 2,
   timeout_s INTEGER, tokens INTEGER, cost_usd REAL,
   started TEXT, finished TEXT, created TEXT NOT NULL,
   CHECK(status IN ('QUEUED','RUNNING','WAITING','BLOCKED','REVIEW','FAILED',
                    'RECOVERING','SUCCEEDED','CANCELLED','ROLLED_BACK')));
 CREATE TABLE IF NOT EXISTS execution_events(
   id INTEGER PRIMARY KEY AUTOINCREMENT, execution TEXT NOT NULL, ts TEXT NOT NULL,
   kind TEXT NOT NULL, detail TEXT, FOREIGN KEY(execution) REFERENCES executions(id));
 CREATE TABLE IF NOT EXISTS tool_calls(
   id INTEGER PRIMARY KEY AUTOINCREMENT, execution TEXT, ts TEXT NOT NULL,
   agent TEXT, tool TEXT NOT NULL, authorized INTEGER NOT NULL DEFAULT 1,
   decision TEXT, target TEXT, outcome TEXT);
 CREATE TABLE IF NOT EXISTS checkpoints(
   id INTEGER PRIMARY KEY AUTOINCREMENT, execution TEXT NOT NULL, ts TEXT NOT NULL,
   seq INTEGER NOT NULL, state TEXT, files TEXT, git_state TEXT,
   tests TEXT, open_issues TEXT, next_action TEXT,
   FOREIGN KEY(execution) REFERENCES executions(id));
 CREATE TABLE IF NOT EXISTS execution_evidence(
   id INTEGER PRIMARY KEY AUTOINCREMENT, execution TEXT NOT NULL, ts TEXT NOT NULL,
   kind TEXT NOT NULL, path TEXT, sha256 TEXT, lines INTEGER, claim TEXT, verified INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS execution_failures(
   id INTEGER PRIMARY KEY AUTOINCREMENT, execution TEXT NOT NULL, ts TEXT NOT NULL,
   class TEXT NOT NULL, detail TEXT, recovery TEXT, escalated INTEGER DEFAULT 0,
   CHECK(class IN ('TRANSIENT','TOOL','CONTEXT','CODE','DEPENDENCY','PERMISSION',
                   'SECURITY','LOGIC','AGENT','SYSTEM','HUMAN_REQUIRED')));
 CREATE TABLE IF NOT EXISTS id_sequences(
   name TEXT PRIMARY KEY, next INTEGER NOT NULL);
 CREATE INDEX IF NOT EXISTS ix_exec_status ON executions(status);
 CREATE INDEX IF NOT EXISTS ix_ev_exec     ON execution_events(execution);
 CREATE INDEX IF NOT EXISTS ix_tc_exec     ON tool_calls(execution);
 """),

 (3, "task state single source of truth", """
 CREATE TABLE IF NOT EXISTS task_store_audit(
   id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, action TEXT NOT NULL,
   task TEXT, detail TEXT);
 CREATE TABLE IF NOT EXISTS quarantined_tasks(
   id TEXT PRIMARY KEY, payload TEXT NOT NULL, reason TEXT NOT NULL, ts TEXT NOT NULL);
 """),

 (4, "event log, permissions, leases, idempotency", """
 CREATE TABLE IF NOT EXISTS events(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   execution TEXT, seq INTEGER NOT NULL, ts TEXT NOT NULL,
   type TEXT NOT NULL, actor TEXT, payload TEXT, correlation TEXT,
   in_context INTEGER NOT NULL DEFAULT 1, evicted_by_seq INTEGER,
   CHECK(type IN (
     'ExecutionCreated','ExecutionStarted','ExecutionResumed','ExecutionBlocked',
     'ExecutionCompleted','ExecutionTerminated','ExecutionStale',
     'ToolRequested','ToolAllowed','ToolDenied','ToolApprovalRequired',
     'CheckpointCreated','AgentMessage','ArtifactCreated',
     'TestStarted','TestPassed','TestFailed',
     'FailureDetected','RecoveryStarted','RecoveryCompleted',
     'ReviewRequested','ReviewCompleted',
     'ApprovalRequested','ApprovalGranted','ApprovalDenied',
     'Heartbeat','BudgetExceeded','DoomLoopDetected')));
 CREATE UNIQUE INDEX IF NOT EXISTS ux_events_exec_seq ON events(execution,seq);
 CREATE INDEX IF NOT EXISTS ix_events_type ON events(type);

 CREATE TABLE IF NOT EXISTS permission_rules(
   id INTEGER PRIMARY KEY AUTOINCREMENT, ordinal INTEGER NOT NULL,
   role TEXT NOT NULL DEFAULT '*', tool TEXT NOT NULL DEFAULT '*',
   arg_match TEXT, effect TEXT NOT NULL, reason TEXT, created TEXT NOT NULL,
   CHECK(effect IN ('ALLOW','DENY','REQUIRE_APPROVAL','ALLOW_WITH_AUDIT','ALLOW_READ_ONLY')));
 CREATE INDEX IF NOT EXISTS ix_rules_ord ON permission_rules(ordinal);

 CREATE TABLE IF NOT EXISTS leases(
   execution TEXT PRIMARY KEY, holder TEXT NOT NULL, acquired TEXT NOT NULL,
   renewed TEXT NOT NULL, ttl_s INTEGER NOT NULL DEFAULT 900);

 CREATE TABLE IF NOT EXISTS op_keys(
   key TEXT PRIMARY KEY, execution TEXT, op TEXT NOT NULL,
   result TEXT, applied INTEGER NOT NULL DEFAULT 0, ts TEXT NOT NULL);
 """),

 (5, "approvals and emergency control", """
 CREATE TABLE IF NOT EXISTS approvals(
   id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL, granted_by TEXT NOT NULL,
   reason TEXT, granted TEXT NOT NULL, expires TEXT, uses_left INTEGER,
   revoked INTEGER NOT NULL DEFAULT 0);
 CREATE INDEX IF NOT EXISTS ix_appr_scope ON approvals(scope);
 CREATE TABLE IF NOT EXISTS control_flags(
   name TEXT PRIMARY KEY, value TEXT NOT NULL, set_by TEXT NOT NULL, ts TEXT NOT NULL, reason TEXT);
 """),
]

def db():
    c = sqlite3.connect(str(DB)); c.execute("PRAGMA foreign_keys=ON"); return c

def migrate(verbose=True):
    c = db()
    c.execute("CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY, applied TEXT)")
    have = {r[0] for r in c.execute("SELECT version FROM schema_version")}
    applied = []
    for ver, name, sql in MIGRATIONS:
        if ver in have: continue
        c.executescript(sql)
        c.execute("INSERT INTO schema_version(version,applied) VALUES(?,?)", (ver, now()))
        applied.append(f"{ver} {name}")
    c.commit()
    if verbose:
        cur = max({r[0] for r in c.execute('SELECT version FROM schema_version')})
        print(f"schema at version {cur}" + (f"; applied: {', '.join(applied)}" if applied else "; nothing to apply"))
    return applied

def next_id(c, name, fmt):
    """Collision-safe allocator. Fixes the RISK-NNN collision observed under parallel agents."""
    c.execute("INSERT OR IGNORE INTO id_sequences(name,next) VALUES(?,1)", (name,))
    n = c.execute("SELECT next FROM id_sequences WHERE name=?", (name,)).fetchone()[0]
    c.execute("UPDATE id_sequences SET next=? WHERE name=?", (n+1, name))
    return fmt % n

def kv(argv):
    d = {}
    for a in argv:
        if "=" in a: k, v = a.split("=", 1); d[k] = v
    return d
def need(d, *ks):
    miss = [k for k in ks if not d.get(k)]
    if miss: die("missing required: " + ", ".join(miss))

def event(c, ex, kind, detail=""):
    c.execute("INSERT INTO execution_events(execution,ts,kind,detail) VALUES(?,?,?,?)", (ex, now(), kind, detail))

# ------------------------------------------------------------------ adapter
def cmd_submit(argv):
    d = kv(argv); need(d, "agent", "objective")
    c = db(); migrate(verbose=False)
    ex = next_id(c, "execution", "EX-%04d")
    c.execute("""INSERT INTO executions(id,task,agent,parent,kind,status,phase,objective,
                 retry_budget,timeout_s,created) VALUES(?,?,?,?,?,'QUEUED',?,?,?,?,?)""",
              (ex, d.get("task"), d["agent"], d.get("parent"), d.get("kind", "work"),
               d.get("phase"), d["objective"], int(d.get("retry_budget", 2)),
               int(d["timeout_s"]) if d.get("timeout_s") else None, now()))
    event(c, ex, "submitted", d["objective"][:200]); c.commit()
    ok(f"{ex} QUEUED  agent={d['agent']}")
    return ex

def _set(ex, status, **extra):
    c = db()
    row = c.execute("SELECT status FROM executions WHERE id=?", (ex,)).fetchone()
    if not row: die(f"unknown execution {ex}")
    sets = ["status=?"]; vals = [status]
    for k, v in extra.items():
        if v is not None: sets.append(f"{k}=?"); vals.append(v)
    vals.append(ex)
    c.execute(f"UPDATE executions SET {','.join(sets)} WHERE id=?", vals)
    event(c, ex, "status", f"{row[0]} -> {status}"); c.commit()
    ok(f"{ex} {row[0]} -> {status}")

def cmd_start(argv):
    d = kv(argv); need(d, "execution"); _set(d["execution"], "RUNNING", started=now(),
        worktree=d.get("worktree"), branch=d.get("branch"), base_commit=d.get("base_commit"))

def cmd_checkpoint(argv):
    d = kv(argv); need(d, "execution")
    c = db(); ex = d["execution"]
    if not c.execute("SELECT 1 FROM executions WHERE id=?", (ex,)).fetchone(): die(f"unknown execution {ex}")
    seq = (c.execute("SELECT COALESCE(MAX(seq),0) FROM checkpoints WHERE execution=?", (ex,)).fetchone()[0]) + 1
    git = ""
    try: git = subprocess.run(["git","rev-parse","HEAD"],cwd=str(R),capture_output=True,text=True,timeout=10).stdout.strip()
    except Exception: pass
    c.execute("""INSERT INTO checkpoints(execution,ts,seq,state,files,git_state,tests,open_issues,next_action)
                 VALUES(?,?,?,?,?,?,?,?,?)""",
              (ex, now(), seq, d.get("state"), d.get("files"), git,
               d.get("tests"), d.get("open_issues"), d.get("next_action")))
    event(c, ex, "checkpoint", f"seq={seq}"); c.commit()
    ok(f"{ex} checkpoint {seq} saved  git={git[:8]}")

def cmd_evidence(argv):
    """Register evidence. A file claim is VERIFIED against the filesystem, not trusted."""
    d = kv(argv); need(d, "execution", "kind")
    c = db(); ex = d["execution"]
    if not c.execute("SELECT 1 FROM executions WHERE id=?", (ex,)).fetchone(): die(f"unknown execution {ex}")
    sha = None; lines = None; verified = 0
    p = d.get("path")
    if p:
        fp = (R / p) if not os.path.isabs(p) else pathlib.Path(p)
        if not fp.exists():
            die(f"evidence path does not exist: {p}. Evidence is not a claim; it is a file.")
        b = fp.read_bytes(); sha = hashlib.sha256(b).hexdigest(); lines = b.count(b"\n"); verified = 1
    c.execute("""INSERT INTO execution_evidence(execution,ts,kind,path,sha256,lines,claim,verified)
                 VALUES(?,?,?,?,?,?,?,?)""", (ex, now(), d["kind"], p, sha, lines, d.get("claim"), verified))
    event(c, ex, "evidence", f"{d['kind']} {p or ''}"); c.commit()
    ok(f"{ex} evidence recorded  kind={d['kind']}" + (f"  sha={sha[:12]} lines={lines} VERIFIED" if verified else "  (claim only, UNVERIFIED)"))

def cmd_fail(argv):
    d = kv(argv); need(d, "execution", "class", "detail")
    c = db(); ex = d["execution"]
    r = c.execute("SELECT retries,retry_budget FROM executions WHERE id=?", (ex,)).fetchone()
    if not r: die(f"unknown execution {ex}")
    retries, budget = r
    c.execute("""INSERT INTO execution_failures(execution,ts,class,detail,recovery,escalated)
                 VALUES(?,?,?,?,?,?)""", (ex, now(), d["class"], d["detail"], d.get("recovery"),
                 1 if d["class"] == "HUMAN_REQUIRED" else 0))
    if d["class"] in ("SECURITY", "HUMAN_REQUIRED") or retries >= budget:
        c.execute("UPDATE executions SET status='BLOCKED' WHERE id=?", (ex,))
        event(c, ex, "blocked", f"class={d['class']} retries={retries}/{budget}"); c.commit()
        ok(f"{ex} BLOCKED  class={d['class']}  retries={retries}/{budget}\n"
           f"  Retry budget exhausted or class is non-retryable. Escalate; do not retry unchanged (rule 11).")
    else:
        c.execute("UPDATE executions SET status='RECOVERING', retries=retries+1 WHERE id=?", (ex,))
        event(c, ex, "failure", f"class={d['class']} retry {retries+1}/{budget}"); c.commit()
        ok(f"{ex} RECOVERING  retry {retries+1}/{budget}  class={d['class']}\n"
           f"  Rule 11: change the approach. Do not repeat the failed action unchanged.")

def cmd_complete(argv):
    """Completion REFUSES without verified evidence. This is the point of the whole file."""
    d = kv(argv); need(d, "execution")
    c = db(); ex = d["execution"]
    row = c.execute("SELECT status,agent FROM executions WHERE id=?", (ex,)).fetchone()
    if not row: die(f"unknown execution {ex}")
    ev = c.execute("SELECT COUNT(*) FROM execution_evidence WHERE execution=? AND verified=1", (ex,)).fetchone()[0]
    if ev == 0:
        die(f"{ex} has NO VERIFIED EVIDENCE. Completion requires evidence on disk "
            f"(harness.py evidence execution={ex} kind=artifact path=...). "
            f"Rule 15: never declare success without evidence.")
    rev = d.get("reviewer")
    if rev and rev == row[1]:
        die(f"reviewer must not be the owner ({row[1]}). Rule 3: no agent reviews its own work.")
    c.execute("UPDATE executions SET status=?, finished=?, tokens=?, cost_usd=? WHERE id=?",
              ("REVIEW" if d.get("needs_review") == "1" else "SUCCEEDED", now(),
               int(d["tokens"]) if d.get("tokens") else None,
               float(d["cost_usd"]) if d.get("cost_usd") else None, ex))
    event(c, ex, "complete", f"evidence={ev} reviewer={rev or 'none'}"); c.commit()
    ok(f"{ex} {'REVIEW' if d.get('needs_review')=='1' else 'SUCCEEDED'}  verified_evidence={ev}")

def cmd_tool(argv):
    """Record an actual tool call. Feeds the honesty check."""
    d = kv(argv); need(d, "tool")
    c = db(); migrate(verbose=False)
    c.execute("""INSERT INTO tool_calls(execution,ts,agent,tool,authorized,decision,target,outcome)
                 VALUES(?,?,?,?,?,?,?,?)""",
              (d.get("execution"), now(), d.get("agent"), d["tool"],
               int(d.get("authorized", 1)), d.get("decision"), d.get("target"), d.get("outcome")))
    c.commit(); ok(f"tool_call recorded: {d['tool']}")

def cmd_honesty(argv):
    """Refute or confirm a provider/tool claim against the ledger. Rule: never claim a tool ran."""
    d = kv(argv); need(d, "tool")
    c = db()
    q = "SELECT COUNT(*) FROM tool_calls WHERE tool=?"; p = [d["tool"]]
    if d.get("execution"): q += " AND execution=?"; p.append(d["execution"])
    n = c.execute(q, p).fetchone()[0]
    if n == 0:
        print(f"REFUTED  '{d['tool']}' has NO recorded call" + (f" in {d['execution']}" if d.get('execution') else "") +
              ".\n  A claim that it ran is unsupported by the ledger (rule: never claim a tool ran that did not).")
        sys.exit(2)
    ok(f"CONFIRMED  '{d['tool']}' recorded {n} time(s)" + (f" in {d['execution']}" if d.get("execution") else ""))

def cmd_status(argv):
    d = kv(argv); c = db()
    if d.get("execution"):
        ex = d["execution"]
        r = c.execute("SELECT * FROM executions WHERE id=?", (ex,)).fetchone()
        if not r: die(f"unknown execution {ex}")
        cols = [x[1] for x in c.execute("PRAGMA table_info(executions)")]
        print("=" * 62)
        for k, v in zip(cols, r):
            if v not in (None, ""): print(f"  {k:14} {v}")
        for lbl, tbl in (("EVENTS","execution_events"),("TOOL CALLS","tool_calls"),
                         ("CHECKPOINTS","checkpoints"),("EVIDENCE","execution_evidence"),
                         ("FAILURES","execution_failures")):
            n = c.execute(f"SELECT COUNT(*) FROM {tbl} WHERE execution=?", (ex,)).fetchone()[0]
            print(f"  {lbl:14} {n}")
        print("=" * 62); return
    rows = c.execute("SELECT status,COUNT(*) FROM executions GROUP BY status").fetchall()
    tot = c.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
    print(f"EXECUTIONS  {tot} total")
    for s, n in rows: print(f"  {s:12} {n}")
    live = c.execute("""SELECT id,agent,status,substr(objective,1,46) FROM executions
                        WHERE status IN ('QUEUED','RUNNING','RECOVERING','BLOCKED','REVIEW')
                        ORDER BY created""").fetchall()
    if live:
        print("\nOPEN")
        for i, a, s, o in live: print(f"  {i}  {s:11} {a:24} {o}")

def cmd_verify(argv):
    """Integrity check for the harness ledger itself."""
    c = db(); problems = []
    orph = c.execute("""SELECT COUNT(*) FROM execution_events e
                        WHERE NOT EXISTS(SELECT 1 FROM executions x WHERE x.id=e.execution)""").fetchone()[0]
    if orph: problems.append(f"{orph} orphaned execution_events")
    noev = c.execute("""SELECT COUNT(*) FROM executions WHERE status='SUCCEEDED'
                        AND id NOT IN (SELECT execution FROM execution_evidence WHERE verified=1)""").fetchone()[0]
    if noev: problems.append(f"{noev} SUCCEEDED executions with NO verified evidence (rule 15 violation)")
    stuck = c.execute("SELECT COUNT(*) FROM executions WHERE status='RUNNING' AND started IS NULL").fetchone()[0]
    if stuck: problems.append(f"{stuck} RUNNING executions never started")
    ver = c.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
    if problems:
        print("HARNESS VERIFY FAILED"); [print("  -", p) for p in problems]; sys.exit(2)
    ok(f"HARNESS VERIFY PASSED  schema=v{ver}  "
       f"executions={c.execute('SELECT COUNT(*) FROM executions').fetchone()[0]}  "
       f"tool_calls={c.execute('SELECT COUNT(*) FROM tool_calls').fetchone()[0]}  "
       f"evidence={c.execute('SELECT COUNT(*) FROM execution_evidence').fetchone()[0]}")


# ------------------------------------------------ PHASE 2: one task authority
TASKS_JSON = R / ".ai-company/state/tasks.json"
_STATUSES = ('todo','in_progress','blocked','failed','review','done','cancelled','accepted_risk')

def _project_json(c):
    """Emit tasks.json as a DERIVED, read-only projection of the DB. Never a second truth."""
    rows = c.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    cols = [x[1] for x in c.execute("PRAGMA table_info(tasks)")]
    out = []
    for r in rows:
        t = dict(zip(cols, r))
        deps = [x[0] for x in c.execute("SELECT depends_on FROM task_deps WHERE task=?", (t["id"],))]
        out.append({"id": t["id"], "title": t["title"], "owner": t["owner"],
                    "reviewer": t.get("reviewer"), "phase": t.get("phase"),
                    "status": t["status"], "deps": deps,
                    "criteria": [x for x in (t.get("acceptance") or "").split(";") if x],
                    "parallel_group": t.get("parallel_group") or "",
                    "evidence": [x for x in (t.get("evidence") or "").split(",") if x],
                    "attempts": t.get("attempts", 0), "created": t.get("created"),
                    "updated": t.get("updated"), "blocked_on": t.get("blocked_on")})
    seq = 0
    for t in out:
        if t["id"].startswith("T") and t["id"][1:].isdigit(): seq = max(seq, int(t["id"][1:]))
    TASKS_JSON.write_text(json.dumps({
        "_DERIVED": True,
        "_SOURCE": "company.db table `tasks` - THE authority",
        "_WARNING": "Read-only projection. Edits here are OVERWRITTEN and are NOT authoritative. "
                    "Write via: harness.py task-add / task-update, or companydb.py task.",
        "_generated": now(), "version": 1, "next_id": seq, "tasks": out}, indent=2))
    return len(out)

def cmd_tasks_import(argv):
    """One-time, idempotent import of the legacy JSON store into the DB. Conflicts are QUARANTINED, never dropped."""
    d = kv(argv); c = db(); migrate(verbose=False)
    src = pathlib.Path(d.get("from") or (R / ".ai-company/state/backup"))
    if src.is_dir():
        cands = sorted(src.glob("tasks.json.pre-v2-*"))
        if not cands: die(f"no legacy snapshot found in {src}")
        src = cands[-1]
    legacy = json.loads(src.read_text())
    if legacy.get("_DERIVED"): ok(f"{src.name} is already a derived projection; nothing to import"); return
    agents = {r[0] for r in c.execute("SELECT id FROM agents")}
    imported = skipped = quarantined = 0
    for t in legacy.get("tasks", []):
        if c.execute("SELECT 1 FROM tasks WHERE id=?", (t["id"],)).fetchone(): skipped += 1; continue
        if t["owner"] not in agents:
            c.execute("INSERT OR REPLACE INTO quarantined_tasks(id,payload,reason,ts) VALUES(?,?,?,?)",
                      (t["id"], json.dumps(t), f"owner '{t['owner']}' is not a registered agent", now()))
            c.execute("INSERT INTO task_store_audit(ts,action,task,detail) VALUES(?,?,?,?)",
                      (now(), "quarantine", t["id"], f"unregistered owner {t['owner']}"))
            quarantined += 1; continue
        if t.get("status") not in _STATUSES:
            c.execute("INSERT OR REPLACE INTO quarantined_tasks(id,payload,reason,ts) VALUES(?,?,?,?)",
                      (t["id"], json.dumps(t), f"invalid status '{t.get('status')}'", now()))
            quarantined += 1; continue
        c.execute("""INSERT INTO tasks(id,kind,title,owner,phase,status,acceptance,parallel_group,
                     attempts,evidence,blocked_on,created,updated)
                     VALUES(?,'task',?,?,?,?,?,?,?,?,?,?,?)""",
                  (t["id"], t["title"], t["owner"], t.get("phase"), t.get("status", "todo"),
                   ";".join(t.get("criteria", [])), t.get("parallel_group", ""),
                   t.get("attempts", 0), ",".join(t.get("evidence", [])), t.get("blocked_on"),
                   t.get("created", now()), t.get("updated", t.get("created", now()))))
        imported += 1
    for t in legacy.get("tasks", []):
        for dep in t.get("deps", []):
            if c.execute("SELECT 1 FROM tasks WHERE id=?", (t["id"],)).fetchone() and \
               c.execute("SELECT 1 FROM tasks WHERE id=?", (dep,)).fetchone():
                c.execute("INSERT OR IGNORE INTO task_deps(task,depends_on) VALUES(?,?)", (t["id"], dep))
    c.execute("INSERT INTO task_store_audit(ts,action,task,detail) VALUES(?,?,?,?)",
              (now(), "import", None, f"imported={imported} skipped={skipped} quarantined={quarantined}"))
    c.commit()
    n = _project_json(c); c.commit()
    ok(f"imported={imported} already_present={skipped} QUARANTINED={quarantined}\n"
       f"tasks.json re-emitted as a DERIVED projection of {n} DB rows")
    if quarantined:
        ok("  Quarantined tasks are preserved in `quarantined_tasks`, NOT deleted:")
        for r in c.execute("SELECT id,reason FROM quarantined_tasks"): ok(f"    {r[0]}  {r[1]}")

def cmd_task_add(argv):
    """Authoritative task creation. DB first, JSON re-projected."""
    d = kv(argv); need(d, "title", "owner")
    c = db(); migrate(verbose=False)
    if not c.execute("SELECT 1 FROM agents WHERE id=?", (d["owner"],)).fetchone():
        die(f"'{d['owner']}' is not a registered agent. Register the role or use an existing one.")
    if d.get("reviewer"):
        if not c.execute("SELECT 1 FROM agents WHERE id=?", (d["reviewer"],)).fetchone():
            die(f"reviewer '{d['reviewer']}' is not a registered agent")
        if d["reviewer"] == d["owner"]: die("separation of duties: an agent may not review its own work")
    tid = d.get("id") or next_id(c, "task", "T%03d")
    while c.execute("SELECT 1 FROM tasks WHERE id=?", (tid,)).fetchone():
        tid = next_id(c, "task", "T%03d")
    c.execute("""INSERT INTO tasks(id,kind,title,owner,reviewer,phase,status,acceptance,
                 parallel_group,risk,created,updated) VALUES(?,'task',?,?,?,?, 'todo',?,?,?,?,?)""",
              (tid, d["title"], d["owner"], d.get("reviewer"), d.get("phase"),
               d.get("criteria", ""), d.get("parallel_group", ""), d.get("risk", "low"), now(), now()))
    for dep in [x for x in d.get("deps", "").split(",") if x]:
        if dep == tid: die("a task cannot depend on itself")
        if not c.execute("SELECT 1 FROM tasks WHERE id=?", (dep,)).fetchone():
            die(f"unknown dependency '{dep}' - add it first")
        c.execute("INSERT OR IGNORE INTO task_deps(task,depends_on) VALUES(?,?)", (tid, dep))
    c.execute("INSERT INTO task_store_audit(ts,action,task,detail) VALUES(?,?,?,?)",
              (now(), "add", tid, d["title"][:120]))
    c.commit(); _project_json(c); c.commit()
    ok(f"{tid} created  owner={d['owner']}" + (f" reviewer={d['reviewer']}" if d.get('reviewer') else ""))

def cmd_task_update(argv):
    d = kv(argv); need(d, "id", "status")
    c = db()
    row = c.execute("SELECT owner,reviewer,evidence,acceptance,attempts FROM tasks WHERE id=?", (d["id"],)).fetchone()
    if not row: die(f"no task '{d['id']}'")
    owner, reviewer, evid, accept, att = row
    if d["status"] not in _STATUSES: die("status must be one of: " + ", ".join(_STATUSES))
    if d["status"] == "done":
        ev = d.get("evidence") or evid
        if not ev: die("cannot mark done without evidence=<path>. Rule 15: never declare success without evidence.")
        for pth in [x.strip() for x in ev.split(",") if x.strip()]:
            fp = (R / pth) if not os.path.isabs(pth) else pathlib.Path(pth)
            if not fp.exists(): die(f"evidence path does not exist: {pth}. Evidence is a file, not a claim.")
        if accept and not d.get("acceptance_verified"):
            die("this task has acceptance criteria. Pass acceptance_verified=<how they were verified>.")
        if reviewer and not d.get("reviewed_by"):
            die(f"independent review required from '{reviewer}'. Pass reviewed_by={reviewer}.")
        if d.get("reviewed_by") and d["reviewed_by"] == owner:
            die("separation of duties: the owner cannot be the reviewer")
    att = att + (1 if d["status"] == "failed" else 0)
    c.execute("UPDATE tasks SET status=?,evidence=COALESCE(?,evidence),blocked_on=?,attempts=?,updated=? WHERE id=?",
              (d["status"], d.get("evidence"), d.get("blocked_on"), att, now(), d["id"]))
    c.execute("INSERT INTO agent_performance(role,task,outcome,rework,escalated,recorded) VALUES(?,?,?,?,?,?)",
              (owner, d["id"], d["status"], 1 if d["status"] == "failed" else 0, 0, now()))
    c.execute("INSERT INTO task_store_audit(ts,action,task,detail) VALUES(?,?,?,?)",
              (now(), "update", d["id"], d["status"]))
    c.commit(); _project_json(c); c.commit()
    ok(f"{d['id']} -> {d['status']}")
    if att >= 2 and d["status"] == "failed":
        ok("  ANTI-LOOP (rule 11): 2+ failures. Do not retry unchanged - dispatch problem-solver or escalate.")

def cmd_tasks_check(argv):
    """Prove the two stores cannot diverge. Non-zero exit if they have."""
    c = db()
    if not TASKS_JSON.exists(): die("tasks.json missing - run `harness.py tasks-project`")
    j = json.loads(TASKS_JSON.read_text())
    problems = []
    if not j.get("_DERIVED"):
        problems.append("tasks.json is NOT marked _DERIVED - it may be being used as a second source of truth")
    dbrows = {r[0]: r[1] for r in c.execute("SELECT id,status FROM tasks")}
    jrows  = {t["id"]: t["status"] for t in j.get("tasks", [])}
    only_db = set(dbrows) - set(jrows); only_js = set(jrows) - set(dbrows)
    if only_db: problems.append(f"in DB but not projection: {sorted(only_db)}")
    if only_js: problems.append(f"in projection but not DB (EDITED BY HAND?): {sorted(only_js)}")
    drift = [k for k in set(dbrows) & set(jrows) if dbrows[k] != jrows[k]]
    if drift: problems.append(f"status drift on {drift}")
    if problems:
        print("TASK STORE DIVERGENCE DETECTED"); [print("  -", p) for p in problems]
        print("  Re-project with: python3 scripts/harness.py tasks-project"); sys.exit(2)
    q = c.execute("SELECT COUNT(*) FROM quarantined_tasks").fetchone()[0]
    ok(f"TASK STORE COHERENT  db={len(dbrows)} projection={len(jrows)} quarantined={q}  single authority = company.db")

def cmd_tasks_project(argv):
    c = db(); n = _project_json(c); c.commit(); ok(f"tasks.json re-projected from DB: {n} tasks")


# ---------------------------------------- MECHANISM 1: step-flush write barrier
def _flush_db():
    """WAL + one COMMITTED transaction per event. Durability is a property of the loop,
    not of an agent remembering to call checkpoint. (SWE-agent/OpenHands pattern.)"""
    c = sqlite3.connect(str(DB), isolation_level=None, timeout=30)
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=FULL")
    return c

def emit(execution, etype, actor=None, payload=None, correlation=None):
    """Append one event and COMMIT immediately. Also renews the lease - liveness is
    proven by work done, not by elapsed wall-clock. Never overwrites history."""
    c = _flush_db()
    try:
        c.execute("BEGIN IMMEDIATE")
        seq = c.execute("SELECT COALESCE(MAX(seq),0)+1 FROM events WHERE execution IS ?",
                        (execution,)).fetchone()[0]
        c.execute("""INSERT INTO events(execution,seq,ts,type,actor,payload,correlation)
                     VALUES(?,?,?,?,?,?,?)""",
                  (execution, seq, now(), etype, actor,
                   json.dumps(payload) if payload is not None else None, correlation))
        if execution:
            c.execute("UPDATE leases SET renewed=? WHERE execution=?", (now(), execution))
        c.execute("COMMIT")
        return seq
    except Exception:
        try: c.execute("ROLLBACK")
        except Exception: pass
        raise
    finally: c.close()

def cmd_event(argv):
    d = kv(argv); need(d, "type")
    seq = emit(d.get("execution"), d["type"], d.get("actor"),
               json.loads(d["payload"]) if d.get("payload") else None, d.get("correlation"))
    ok(f"event #{seq} {d['type']}" + (f" on {d['execution']}" if d.get("execution") else ""))

def cmd_events(argv):
    d = kv(argv); c = db()
    q = "SELECT seq,ts,type,actor,payload FROM events WHERE 1=1"; p = []
    if d.get("execution"): q += " AND execution=?"; p.append(d["execution"])
    if d.get("type"): q += " AND type=?"; p.append(d["type"])
    q += " ORDER BY id DESC LIMIT ?"; p.append(int(d.get("limit", 30)))
    rows = list(c.execute(q, p))
    for seq, ts, t, a, pay in reversed(rows):
        print(f"  #{seq:<4} {ts[11:19]}  {t:22} {a or '':22} {(pay or '')[:44]}")
    if not rows: print("  (no events)")

# ------------------------- MECHANISM 3: deny-biased, last-match-wins permissions
def _resolve(c, role, tool, arg):
    """Last matching rule wins; default DENY for anything not explicitly allowed.
    bash is matched on the PARSED command, because Roo #4732 proves a regex that
    ignores the shell is decorative."""
    import fnmatch, shlex
    tokens = []
    if arg and tool.lower() in ("bash", "shell", "run"):
        try: tokens = shlex.split(arg)
        except ValueError: tokens = arg.split()
    decision, reason = "DENY", "no rule matched (deny-biased default)"
    for r in c.execute("SELECT ordinal,role,tool,arg_match,effect,reason FROM permission_rules ORDER BY ordinal"):
        _, rrole, rtool, rarg, eff, rsn = r
        if rrole != "*" and rrole != role: continue
        if rtool != "*" and rtool.lower() != tool.lower(): continue
        if rarg:
            hay = [arg or ""] + tokens
            if not any(fnmatch.fnmatch(h, rarg) for h in hay): continue
        decision, reason = eff, rsn or f"rule #{r[0]}"
    return decision, reason

def cmd_permit(argv):
    """Authorization check. Exit 0 allow, 2 deny, 3 approval required. Deny-biased."""
    d = kv(argv); need(d, "role", "tool")
    c = db(); migrate(verbose=False)
    pause = c.execute("SELECT value FROM control_flags WHERE name='GLOBAL_PAUSE'").fetchone()
    if pause and pause[0] == "on":
        emit(d.get("execution"), "ExecutionBlocked", d["role"], {"tool": d["tool"], "reason": "GLOBAL_PAUSE"})
        print("DENY  GLOBAL_PAUSE is active. Founder must lift it: harness.py control set=GLOBAL_PAUSE value=off by=founder")
        sys.exit(2)
    dec, why = _resolve(c, d["role"], d["tool"], d.get("arg"))
    ex = d.get("execution")
    if dec == "REQUIRE_APPROVAL":
        scope = f"{d['tool']}:{(d.get('arg') or '')[:80]}"
        aid = _live_approval(c, scope) or _live_approval(c, d["tool"])
        if aid:
            c.execute("UPDATE approvals SET uses_left=CASE WHEN uses_left IS NULL THEN NULL ELSE uses_left-1 END WHERE id=?", (aid,))
            c.commit()
            emit(ex, "ApprovalGranted", d["role"], {"tool": d["tool"], "approval": aid})
            dec, why = "ALLOW_WITH_AUDIT", f"founder approval #{aid} consumed"
    c.execute("""INSERT INTO tool_calls(execution,ts,agent,tool,authorized,decision,target,outcome)
                 VALUES(?,?,?,?,?,?,?,?)""",
              (ex, now(), d["role"], d["tool"], 1 if dec.startswith("ALLOW") else 0, dec,
               (d.get("arg") or "")[:200], why)); c.commit()
    emit(ex, "ToolRequested", d["role"], {"tool": d["tool"], "arg": (d.get("arg") or "")[:200]})
    if dec.startswith("ALLOW"):
        emit(ex, "ToolAllowed", d["role"], {"tool": d["tool"], "effect": dec}); ok(f"ALLOW ({dec})  {why}"); sys.exit(0)
    if dec == "REQUIRE_APPROVAL":
        emit(ex, "ToolApprovalRequired", d["role"], {"tool": d["tool"]}); print(f"APPROVAL REQUIRED  {why}"); sys.exit(3)
    emit(ex, "ToolDenied", d["role"], {"tool": d["tool"], "reason": why})
    print(f"DENY  role={d['role']} tool={d['tool']}\n  {why}"); sys.exit(2)

def cmd_rule(argv):
    d = kv(argv)
    if d.get("list") or not d.get("effect"):
        c = db()
        print(f"  {'ORD':<5}{'ROLE':<22}{'TOOL':<14}{'ARG':<26}{'EFFECT':<18}REASON")
        for r in c.execute("SELECT ordinal,role,tool,COALESCE(arg_match,''),effect,COALESCE(reason,'') FROM permission_rules ORDER BY ordinal"):
            print(f"  {r[0]:<5}{r[1]:<22}{r[2]:<14}{r[3][:24]:<26}{r[4]:<18}{r[5][:30]}")
        return
    need(d, "effect")
    c = db(); migrate(verbose=False)
    o = int(d["ordinal"]) if d.get("ordinal") else (c.execute("SELECT COALESCE(MAX(ordinal),0)+10 FROM permission_rules").fetchone()[0])
    c.execute("""INSERT INTO permission_rules(ordinal,role,tool,arg_match,effect,reason,created)
                 VALUES(?,?,?,?,?,?,?)""",
              (o, d.get("role", "*"), d.get("tool", "*"), d.get("arg_match"), d["effect"], d.get("reason"), now()))
    c.commit(); ok(f"rule #{o}: {d.get('role','*')} / {d.get('tool','*')} -> {d['effect']}")

# ------------------------------- MECHANISM 4: leases renewed by work, reap stale
def cmd_lease(argv):
    d = kv(argv); need(d, "execution", "holder")
    c = db(); migrate(verbose=False)
    c.execute("""INSERT INTO leases(execution,holder,acquired,renewed,ttl_s) VALUES(?,?,?,?,?)
                 ON CONFLICT(execution) DO UPDATE SET holder=excluded.holder, renewed=excluded.renewed""",
              (d["execution"], d["holder"], now(), now(), int(d.get("ttl_s", 900))))
    c.commit(); emit(d["execution"], "Heartbeat", d["holder"], {"ttl_s": int(d.get("ttl_s", 900))})
    ok(f"lease held on {d['execution']} by {d['holder']} ttl={d.get('ttl_s',900)}s")

def cmd_reap(argv):
    """Distinguish DEAD from SLOW by last EVENT, not by elapsed wall-clock."""
    import datetime as _dt
    c = db(); n = 0
    for ex, holder, renewed, ttl in c.execute("SELECT execution,holder,renewed,ttl_s FROM leases"):
        st = c.execute("SELECT status FROM executions WHERE id=?", (ex,)).fetchone()
        if not st or st[0] not in ("RUNNING", "RECOVERING"): continue
        try: age = (_dt.datetime.now(_dt.timezone.utc) - _dt.datetime.fromisoformat(renewed)).total_seconds()
        except Exception: continue
        if age > ttl:
            c.execute("UPDATE executions SET status='BLOCKED' WHERE id=?", (ex,)); c.commit()
            emit(ex, "ExecutionStale", holder, {"idle_s": int(age), "ttl_s": ttl})
            print(f"  STALE {ex} holder={holder} idle={int(age)}s > ttl={ttl}s -> BLOCKED"); n += 1
    ok(f"reap complete: {n} stale execution(s) blocked" if n else "reap complete: no stale executions")

# ----------------------------- MECHANISM 5: op-keys, journal-then-apply idempotency
def cmd_opkey(argv):
    """Claim an operation key BEFORE a side effect. Second claim returns the memoised
    result and exits 4, so a resumed execution never double-applies."""
    d = kv(argv); need(d, "key", "op")
    c = db(); migrate(verbose=False)
    row = c.execute("SELECT applied,result FROM op_keys WHERE key=?", (d["key"],)).fetchone()
    if row:
        print(f"ALREADY APPLIED  key={d['key']}  result={row[1] or ''}\n"
              f"  Do NOT re-apply. This is the memoised result of a prior attempt.")
        sys.exit(4)
    c.execute("INSERT INTO op_keys(key,execution,op,result,applied,ts) VALUES(?,?,?,?,0,?)",
              (d["key"], d.get("execution"), d["op"], None, now())); c.commit()
    ok(f"claimed {d['key']} - proceed, then: harness.py opkey-done key={d['key']} result=...")

def cmd_opkey_done(argv):
    d = kv(argv); need(d, "key")
    c = db(); c.execute("UPDATE op_keys SET applied=1,result=? WHERE key=?", (d.get("result"), d["key"]))
    c.commit(); ok(f"{d['key']} marked applied")


# ------------------------------------- APPROVALS: make REQUIRE_APPROVAL satisfiable
def _live_approval(c, scope):
    import datetime as _dt
    for aid, exp, uses in c.execute(
        "SELECT id,expires,uses_left FROM approvals WHERE scope=? AND revoked=0 ORDER BY id DESC", (scope,)):
        if exp:
            try:
                if _dt.datetime.now(_dt.timezone.utc) > _dt.datetime.fromisoformat(exp): continue
            except Exception: pass
        if uses is not None and uses <= 0: continue
        return aid
    return None

def cmd_approve(argv):
    """Founder grants a scoped, time-boxed, use-limited approval. Only the founder may."""
    d = kv(argv); need(d, "scope", "by")
    if d["by"] != "founder": die("only the founder may grant an approval (CLAUDE.md 2). No agent self-authorises.")
    import datetime as _dt
    c = db(); migrate(verbose=False)
    mins = int(d.get("minutes", 30))
    exp = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(minutes=mins)).replace(microsecond=0).isoformat()
    c.execute("""INSERT INTO approvals(scope,granted_by,reason,granted,expires,uses_left)
                 VALUES(?,?,?,?,?,?)""",
              (d["scope"], d["by"], d.get("reason"), now(), exp,
               int(d["uses"]) if d.get("uses") else 1)); c.commit()
    emit(d.get("execution"), "ApprovalGranted", "founder",
         {"scope": d["scope"], "expires": exp, "uses": d.get("uses", 1)})
    ok(f"APPROVED scope='{d['scope']}' by founder, expires {exp}, uses={d.get('uses',1)}")

def cmd_revoke(argv):
    d = kv(argv); need(d, "scope")
    c = db(); n = c.execute("UPDATE approvals SET revoked=1 WHERE scope=? AND revoked=0", (d["scope"],)).rowcount
    c.commit(); emit(None, "ApprovalDenied", "founder", {"scope": d["scope"], "revoked": n})
    ok(f"revoked {n} approval(s) for '{d['scope']}'")

def cmd_control(argv):
    """Founder emergency control. PAUSE halts every permit decision at DENY."""
    d = kv(argv)
    c = db(); migrate(verbose=False)
    if not d.get("set"):
        rows = list(c.execute("SELECT name,value,set_by,ts,COALESCE(reason,'') FROM control_flags"))
        if not rows: ok("no control flags set - system NORMAL"); return
        for n_, v, b, t_, r in rows: print(f"  {n_:<16} {v:<10} by={b:<10} {t_}  {r}")
        return
    need(d, "set", "value", "by")
    if d["by"] != "founder": die("emergency controls are founder-only")
    c.execute("""INSERT INTO control_flags(name,value,set_by,ts,reason) VALUES(?,?,?,?,?)
                 ON CONFLICT(name) DO UPDATE SET value=excluded.value,set_by=excluded.set_by,
                 ts=excluded.ts,reason=excluded.reason""",
              (d["set"], d["value"], d["by"], now(), d.get("reason"))); c.commit()
    emit(None, "ExecutionBlocked" if d["value"] == "on" else "ExecutionResumed", "founder",
         {"flag": d["set"], "value": d["value"]})
    ok(f"CONTROL {d['set']}={d['value']} set by founder. {d.get('reason','')}")

HELP = """harness.py - execution layer beneath the orchestrator

  migrate                                     apply pending schema migrations (idempotent)
  submit agent= objective= [task= phase= parent= retry_budget= timeout_s=]
  start execution= [worktree= branch= base_commit=]
  checkpoint execution= [state= files= tests= open_issues= next_action=]
  evidence execution= kind= [path= claim=]     path is VERIFIED on disk, not trusted
  complete execution= [reviewer= needs_review=1 tokens= cost_usd=]
  fail execution= class= detail= [recovery=]   class: TRANSIENT TOOL CONTEXT CODE DEPENDENCY
                                               PERMISSION SECURITY LOGIC AGENT SYSTEM HUMAN_REQUIRED
  tool tool= [execution= agent= authorized= target= outcome=]
  honesty tool= [execution=]                   refutes an unsupported "I used X" claim
  status [execution=]                          ledger view
  verify                                       integrity check
  tasks-import [from=]                         one-time legacy JSON -> DB, conflicts QUARANTINED
  task-add title= owner= [reviewer= deps= criteria= phase= risk=]   DB is authority
  task-update id= status= [evidence= reviewed_by= acceptance_verified=]
  tasks-check                                  prove DB and projection cannot diverge
  tasks-project                                re-emit tasks.json from the DB
  event type= [execution= actor= payload= correlation=]   append-only, commits immediately
  events [execution= type= limit=]             read the event stream
  permit role= tool= [arg= execution=]         exit 0 ALLOW / 2 DENY / 3 APPROVAL. deny-biased
  rule effect= [role= tool= arg_match= ordinal= reason=] | rule list=1
  lease execution= holder= [ttl_s=]            heartbeat, renewed by every event
  reap                                         BLOCK executions whose lease expired
  opkey key= op= [execution=]                  claim before a side effect; exit 4 if already applied
  opkey-done key= [result=]
  approve scope= by=founder [minutes= uses= reason=]   satisfies a REQUIRE_APPROVAL
  revoke scope=                                revoke outstanding approvals
  control [set= value= by=founder reason=]     GLOBAL_PAUSE etc. Founder-only

The harness records and enforces. It never decides. Authority stays in companydb.py."""

CMDS = {"migrate": lambda a: migrate(), "submit": cmd_submit, "start": cmd_start,
        "checkpoint": cmd_checkpoint, "evidence": cmd_evidence, "complete": cmd_complete,
        "fail": cmd_fail, "tool": cmd_tool, "honesty": cmd_honesty, "status": cmd_status,
        "verify": cmd_verify, "tasks-import": cmd_tasks_import, "task-add": cmd_task_add,
        "task-update": cmd_task_update, "tasks-check": cmd_tasks_check,
        "tasks-project": cmd_tasks_project, "event": cmd_event, "events": cmd_events,
        "permit": cmd_permit, "rule": cmd_rule, "lease": cmd_lease, "reap": cmd_reap,
        "opkey": cmd_opkey, "opkey-done": cmd_opkey_done, "approve": cmd_approve,
        "revoke": cmd_revoke, "control": cmd_control, "help": lambda a: print(HELP)}

if __name__ == "__main__":
    if not DB.exists(): die(f"company database not found at {DB}")
    if len(sys.argv) < 2: print(HELP); sys.exit(0)
    cmd = sys.argv[1]
    if cmd not in CMDS: print(HELP); die(f"unknown command '{cmd}'")
    CMDS[cmd](sys.argv[2:])
