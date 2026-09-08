#!/usr/bin/env python3
"""Machine-readable CI result emitter. Runs every gate and reports honestly.
UNKNOWN is never PASS. SKIPPED is never PASS."""
import subprocess, json, sys, pathlib, datetime, os
R=pathlib.Path(__file__).resolve().parent.parent
GATES=[("compile","python3 -m compileall -q scripts/"),
 ("secret_scan","sh scripts/secret_scan.sh"),
 ("company_verify","python3 scripts/companydb.py verify"),
 ("sop_validate","python3 scripts/company.py validate"),
 ("org_audit","python3 scripts/audit_org.py"),
 ("capability_validation","python3 scripts/capability_validation.py"),
 ("cognitive_validation","python3 scripts/cognitive_validation.py"),
 ("readiness_audit","python3 scripts/readiness_audit.py"),
 ("behavior_tests","python3 scripts/behavior_tests.py")]
jobs=[]; start=datetime.datetime.now(datetime.timezone.utc)
for name,cmd in GATES:
    t0=datetime.datetime.now()
    try:
        p=subprocess.run(cmd,shell=True,cwd=R,capture_output=True,text=True,timeout=180)
        st="PASS" if p.returncode==0 else "FAIL"
        tail=(p.stdout or p.stderr or "").strip().splitlines()[-1:] or [""]
    except subprocess.TimeoutExpired:
        st="UNKNOWN"; tail=["timeout"]
    except Exception as e:
        st="UNKNOWN"; tail=[str(e)[:120]]
    jobs.append(dict(job=name,status=st,detail=tail[0][:160],
                     duration_s=round((datetime.datetime.now()-t0).total_seconds(),2)))
overall = "PASS" if all(j["status"]=="PASS" for j in jobs) else \
          ("FAIL" if any(j["status"]=="FAIL" for j in jobs) else "UNKNOWN")
sha=subprocess.run(["git","rev-parse","HEAD"],cwd=R,capture_output=True,text=True).stdout.strip()[:12]
br=subprocess.run(["git","rev-parse","--abbrev-ref","HEAD"],cwd=R,capture_output=True,text=True).stdout.strip()
out=dict(schema="ai-company-ci/1", status=overall, commit=sha, branch=br,
         workflow="ci.yml", trigger=os.environ.get("GITHUB_EVENT_NAME","local"),
         started=start.isoformat(timespec="seconds"),
         duration_s=round((datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),2),
         jobs=jobs,
         failure_reason=next((f"{j['job']}: {j['detail']}" for j in jobs if j["status"]!="PASS"),None))
# Persist the run so the orchestrator can inspect CI without re-running it.
# observed=1 only because this process actually executed the jobs and saw the results.
try:
    import sqlite3
    db=R/".ai-company/state/company.db"
    if db.exists():
        con=sqlite3.connect(db)
        rid="CI-"+start.strftime("%Y%m%dT%H%M%S")
        con.execute("""INSERT OR REPLACE INTO ci_runs(id,commit_sha,branch,workflow,trigger,status,
            started,finished,duration_s,jobs_json,failure_reason,artifacts,observed)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1)""",
          (rid,sha,br,"ci.yml",out["trigger"],overall,out["started"],
           datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           out["duration_s"],json.dumps(jobs),out["failure_reason"],"ci-results.json"))
        con.commit(); con.close()
        out["run_id"]=rid
except Exception as e:
    out["persist_error"]=str(e)[:120]

print(json.dumps(out,indent=2))
sys.exit(0 if overall=="PASS" else 1)
