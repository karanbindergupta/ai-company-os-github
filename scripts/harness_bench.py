#!/usr/bin/env python3
"""harness_bench.py - the 15 representative scenarios from directive section 26.

Runs OUR harness against each. Every competitor column is NOT EXECUTED, with the
specific blocking reason recorded. No competitor result is estimated or invented.
"""
import subprocess, sqlite3, pathlib, sys, time

R = pathlib.Path(__file__).resolve().parent.parent
DB = R / ".ai-company/state/company.db"
HP = [sys.executable, str(R / "scripts/harness.py")]

def h(*a):
    return subprocess.run(HP + list(a), cwd=str(R), capture_output=True, text=True, timeout=60)
def q(sql, *p):
    c = sqlite3.connect(str(DB)); r = c.execute(sql, p).fetchall(); c.close(); return r
def ex_new(agent="backend-lead", obj="bench"):
    o = h("submit", f"agent={agent}", f"objective={obj}", "kind=bench").stdout
    return o.split()[0] if o else None

RESULTS = []
def scenario(n, name, fn):
    try:
        ok, note = fn()
    except Exception as e:
        ok, note = False, f"exception: {e}"
    RESULTS.append((n, name, ok, note))
    print(f"  {n:>2}. {'PASS' if ok else 'FAIL'}  {name:<34} {note}")

def s1():
    # STANDARD profile requires a passing PEER_REVIEW before completion. The first
    # draft of this scenario omitted it and the harness correctly refused - the
    # scenario was wrong, not the harness.
    e = ex_new(obj="simple coding task"); h("start", f"execution={e}")
    h("evidence", f"execution={e}", "kind=artifact", "path=scripts/harness.py")
    h("review", f"execution={e}", "mode=PEER_REVIEW", "reviewer=qa-lead", "verdict=ACCEPT")
    r = h("complete", f"execution={e}", "reviewer=qa-lead")
    return "SUCCEEDED" in r.stdout, "evidence + peer review gated completion"

def s2():
    e = ex_new(obj="multi-file feature"); h("start", f"execution={e}")
    for st in ("design", "implement", "test"):
        h("step", f"execution={e}", f"step={st}", "ok=1")
    last = q("SELECT last_successful_step FROM executions WHERE id=?", e)[0][0]
    return last == "test", f"step tracking -> {last}"

def s3():
    e = ex_new(obj="debugging"); h("start", f"execution={e}")
    h("fail", f"execution={e}", "class=CODE", "detail=null deref")
    r = h("recover", f"execution={e}")
    return "REQUIRES_RECONCILIATION" in r.stdout, "failure classified for diagnosis"

def s4():
    e = ex_new(obj="failed-test recovery"); h("start", f"execution={e}")
    h("event", "type=TestFailed", f"execution={e}", "actor=qa-lead")
    h("fail", f"execution={e}", "class=CODE", "detail=assert failed")
    r = h("resume", f"execution={e}")
    return "RUNNING" in r.stdout, "bounded retry, resumed"

def s5():
    es = [ex_new(agent=a, obj=f"parallel {a}") for a in ("backend-lead", "qa-lead", "devops-engineer")]
    for e in es: h("start", f"execution={e}")
    return len(set(es)) == 3 and all(es), "3 distinct executions, no id collision"

def s6():
    e = ex_new(obj="long-running"); h("start", f"execution={e}")
    h("schedule", f"execution={e}", "minutes=-1", "reason=overnight feed")
    return e in h("due").stdout, "parked and surfaced when due"

def s7():
    e = ex_new(obj="crash recovery"); h("start", f"execution={e}")
    h("checkpoint", f"execution={e}", "state=mid", "next_action=resume here")
    h("lease", f"execution={e}", "holder=backend-lead", "ttl_s=1"); time.sleep(2); h("reap")
    st = q("SELECT status FROM executions WHERE id=?", e)[0][0]
    r = h("recover", f"execution={e}")
    return st == "BLOCKED" and "resume here" in r.stdout, "crash detected, restart point known"

def s8():
    return h("permit", "role=backend-lead", "tool=Bash",
             "arg=git push origin main").returncode == 3, "permission-sensitive -> APPROVAL"

def s9():
    return h("permit", "role=backend-lead", "tool=Bash",
             "arg=cat " + "." + "env").returncode == 2, "security-sensitive -> DENY"

def s10():
    r = h("route", "task_kind=kind-with-no-history-at-all")
    return r.returncode == 2 and "INSUFFICIENT EVIDENCE" in r.stdout, "refuses to guess a route"

def s11():
    e = ex_new(obj="multi-agent"); h("start", f"execution={e}")
    h("review", f"execution={e}", "mode=PEER_REVIEW", "reviewer=qa-lead", "verdict=ACCEPT")
    return q("SELECT COUNT(*) FROM reviews WHERE execution=?", e)[0][0] == 1, "independent review recorded"

def s12():
    e = ex_new(obj="ambiguous task"); h("start", f"execution={e}")
    return h("complete", f"execution={e}").returncode == 2, "refuses completion without evidence"

def s13():
    e = ex_new(obj="conflicting agents")
    h("workspace", "register=ws-bench-a", "path=/tmp/ws-bench", f"execution={e}")
    e2 = ex_new(agent="qa-lead", obj="conflicting agents 2")
    r2 = h("workspace", "register=ws-bench-b", "path=/tmp/ws-bench", f"execution={e2}")
    return r2.returncode == 2, "second agent refused the held workspace"

def s14():
    con = sqlite3.connect(str(DB))
    con.execute("INSERT INTO executions(id,agent,status,created) "
                "VALUES('EX-BENCHTAMPER','ceo','SUCCEEDED',datetime('now'))")
    con.commit(); con.close()
    bad = h("verify").returncode != 0
    con = sqlite3.connect(str(DB)); con.execute("DELETE FROM executions WHERE id='EX-BENCHTAMPER'")
    con.commit(); con.close()
    return bad, "state corruption detected by verify"

def s15():
    e = ex_new(obj="human approval workflow"); h("start", f"execution={e}")
    h("profile", f"execution={e}", "set=CRITICAL")
    for _ in range(3):
        h("evidence", f"execution={e}", "kind=artifact", "path=scripts/harness.py")
    return h("complete", f"execution={e}", "reviewer=qa-lead").returncode == 2, \
           "CRITICAL blocks pending reviews + founder approval"

COMPETITORS = {
    "OpenHands": "requires a Docker runtime; Docker absent, Homebrew absent (documented constraint)",
    "Cline":     "VS Code extension; no VS Code CLI present, no headless entry point",
    "Roo Code":  "VS Code extension; same constraint as Cline",
    "SWE-agent": "requires Python >=3.11; runtime here is 3.9.6",
    "Letta":     "requires Python >=3.10; runtime here is 3.9.6",
    "Goose":     "builds from Rust source; cargo absent",
    "OpenCode":  "not installed; would additionally require model credentials",
}

if __name__ == "__main__":
    print("=" * 76)
    print("  HARNESS BENCHMARK - 15 representative scenarios (directive section 26)")
    print("=" * 76)
    for i, (name, fn) in enumerate([
        ("simple coding task", s1), ("multi-file feature", s2), ("debugging", s3),
        ("failed-test recovery", s4), ("parallel tasks", s5), ("long-running task", s6),
        ("crash recovery", s7), ("permission-sensitive task", s8),
        ("security-sensitive task", s9), ("research task (routing)", s10),
        ("multi-agent task", s11), ("ambiguous task", s12),
        ("conflicting-agent task", s13), ("state corruption task", s14),
        ("human approval workflow", s15)], 1):
        scenario(i, name, fn)

    p = sum(1 for _, _, ok, _ in RESULTS if ok)
    print("\n" + "=" * 76)
    print(f"  OUR HARNESS: {p}/{len(RESULTS)} scenarios passed")
    print("=" * 76)
    print("\n  COMPETITOR EXECUTION - all NOT EXECUTED. Reasons, not excuses:")
    for k, v in COMPETITORS.items():
        print(f"    {k:<11} NOT EXECUTED - {v}")
    print("\n  No competitor score is estimated, inferred or invented.")
    print("  Architecture-only comparison: .ai-company/harness/BENCHMARK-MATRIX.md")
    sys.exit(0 if p == len(RESULTS) else 1)
