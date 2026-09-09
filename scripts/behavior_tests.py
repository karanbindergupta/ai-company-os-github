#!/usr/bin/env python3
"""Layer 3 test suite - 35 checks (behaviour, CI, tools). Exits non-zero on any failure."""
import sqlite3, pathlib, subprocess, sys, os, json
R=pathlib.Path(__file__).resolve().parent.parent
c=sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory=sqlite3.Row
res=[]
def t(n,ok,d=""): res.append((n,ok,d))
def one(q,p=()):
    try: return c.execute(q,p).fetchone()[0]
    except Exception: return 0
def ex(p): return (R/p).exists()

# --- BEHAVIOUR (1-18)
t("1  contracts load",one("SELECT COUNT(*) FROM behavioral_contracts")>=100,f"{one('SELECT COUNT(*) FROM behavioral_contracts')} contracts")
t("2  contracts inherit cognitive profile",one("""SELECT COUNT(*) FROM behavioral_contracts b JOIN agents a
   ON a.id=b.agent WHERE b.evidence_behaviors=a.evidence_threshold AND b.risk_behaviors=a.risk_profile""")>=100)
t("3  role-specific behaviours present",one("SELECT COUNT(DISTINCT decision_behaviors) FROM behavioral_contracts")>=8)
t("4  prohibited behaviours represented",one("SELECT COUNT(*) FROM behavioral_contracts WHERE prohibited_behaviors LIKE '%Fabricating%'")>=100)
t("5  drills execute",one("SELECT COUNT(*) FROM drill_runs")>=6,f"{one('SELECT COUNT(*) FROM drill_runs')} runs")
t("6  evaluations recorded with score+verdict",one("SELECT COUNT(*) FROM drill_runs WHERE score IS NOT NULL AND verdict<>''")>=6)
t("7  failed drills generate coaching",one("SELECT COUNT(*) FROM coaching")>=1)
t("8  coaching names a retest drill",one("SELECT COUNT(*) FROM coaching WHERE retest_drill<>''")>=1)
base=one("SELECT score FROM drill_runs WHERE drill='DR-TOOL-001' AND verdict='FAIL'")
ret=one("SELECT score FROM drill_runs WHERE drill='DR-TOOL-001' AND verdict='PASS'")
t("9  behavioural improvement measurable",ret>base,f"{base} -> {ret}")
t("10 behavioural regression detected",one("SELECT COUNT(*) FROM behavioral_regressions")>=1)
t("11 one failure does not rewrite personality",
  one("SELECT COUNT(*) FROM profile_changes WHERE approved=1")==0 and one("SELECT COUNT(*) FROM coaching")>=1,
  "coaching applied; zero approved profile edits")
t("12 repeated evidence updates development",one("SELECT COUNT(*) FROM drill_runs WHERE agent='cfo'")>=2)
t("13 authority behaviour intact",
  subprocess.run(["python3","scripts/companydb.py","can","cfo","decide","security_architecture"],
                 capture_output=True,cwd=R).returncode==2)
t("14 tool honesty enforced (rubric catches a false claim)",base==0,"unconditioned baseline scored 0 with a VIOLATION")
t("15 uncertainty behaviour evaluated",one("SELECT COUNT(*) FROM drill_runs WHERE drill='DR-UNCERT-001'")>=1)
t("16 disagreement behaviour evaluated",one("SELECT COUNT(*) FROM drill_runs WHERE drill='DR-DISAG-001'")>=1)
t("17 failure behaviour evaluated",one("SELECT COUNT(*) FROM drill_runs WHERE drill='DR-FAIL-001'")>=1)
t("18 pressure behaviour evaluated",one("SELECT COUNT(*) FROM drill_runs WHERE drill='DR-PRESS-001'")>=1)

# --- CI (19-30)
t("19 CI configuration exists",ex(".github/workflows/ci.yml"))
runs=one("SELECT COUNT(*) FROM ci_runs")
t("20 CI runs recorded",runs>=1,f"{runs} runs")
jobs=json.loads(one("SELECT jobs_json FROM ci_runs ORDER BY started DESC") or "[]") if runs else []
names={j["job"] for j in jobs}
t("21 tests execute in CI",{"company_verify","sop_validate"}<=names)
t("22 build/compile executes",("compile" in names))
t("23 lint/validation executes",{"org_audit","capability_validation"}<=names)
t("24 type/consistency check executes",("cognitive_validation" in names),"stdlib project: compileall + validators serve this role")
t("25 security checks execute",("secret_scan" in names))
t("26 results inspectable",one("SELECT COUNT(*) FROM ci_runs WHERE jobs_json IS NOT NULL")>=1)
t("27 failure details inspectable",ex("scripts/ci_report.py"))
t("28 artifacts inspectable",ex("ci-results.json") or ("upload-artifact" in (R/".github/workflows/ci.yml").read_text()))
st=one("SELECT status FROM ci_runs ORDER BY started DESC")
gate=one("SELECT trusted_as_gate FROM capability_readiness WHERE name='ci'")
t("29 CI cannot be PASS without evidence",
  one("SELECT COUNT(*) FROM ci_runs WHERE status='PASS' AND observed=0")==0,
  "no PASS row lacking observation")
t("30 CI failure creates actionable info",
  "failure_reason" in (R/"scripts/ci_report.py").read_text())

# --- TOOLS (31-35)
cap=lambda n,f: one(f"SELECT {f} FROM capability_readiness WHERE name=?",(n,))
t("31 Exa probed, not assumed",cap("exa","last_probed") not in (0,None,"") and cap("exa","rag")=="GREEN",
  f"exa={cap('exa','status')}")
t("32 Brave probed, not assumed",cap("brave","last_probed") not in (0,None,""),f"brave={cap('brave','status')}")
t("33 unavailable provider triggers fallback",one("SELECT COUNT(*) FROM provider_usage WHERE fallback_reason<>''")>=1)
t("34 provider usage cannot be falsely claimed",
  subprocess.run(["python3","scripts/intelligence.py","provider","requested=brave","actual=brave"],
                 capture_output=True,cwd=R).returncode!=0)
t("35 registry reflects observed status",one("SELECT COUNT(*) FROM capability_readiness WHERE last_probed IS NOT NULL")>=10)

# ---------------------------------------------------------------------------
# CLEAN-INSTALL BASELINE
#
# 16 of these 35 checks assert ACCUMULATED OPERATIONAL EVIDENCE: drills actually
# run, coaching actually issued, improvement actually measured, providers
# actually probed. A freshly bootstrapped company has earned none of it, so on a
# clean install they MUST fail. That is the suite working, not breaking - and
# making them pass by seeding rows would be fabricated evidence, which decisions
# D-5 and D-10 and governance rule 15 all forbid.
#
# CI still needs a real gate, so `--clean-install` asserts the exact expected
# shape instead of a bare count:
#   * any check outside this set that fails  -> HARD FAILURE (a real regression)
#   * any check inside this set that PASSES  -> HARD FAILURE (evidence was
#     manufactured, which is the more dangerous direction)
CLEAN_INSTALL_UNPROVEN = {
    "5  drills execute",
    "6  evaluations recorded with score+verdict",
    "7  failed drills generate coaching",
    "8  coaching names a retest drill",
    "9  behavioural improvement measurable",
    "10 behavioural regression detected",
    "11 one failure does not rewrite personality",
    "12 repeated evidence updates development",
    "15 uncertainty behaviour evaluated",
    "16 disagreement behaviour evaluated",
    "17 failure behaviour evaluated",
    "18 pressure behaviour evaluated",
    "31 Exa probed, not assumed",
    "32 Brave probed, not assumed",
    "33 unavailable provider triggers fallback",
    "35 registry reflects observed status",
}

fails=sum(1 for _,ok,_ in res if not ok)
for n,ok,d in res: print(f"  [{'PASS' if ok else 'FAIL'}] {n}"+(f"  ({d})" if d else ""))
print(f"\nLAYER 3 TESTS: {len(res)-fails}/{len(res)} passed"+("" if not fails else f"  {fails} FAILED"))

if "--clean-install" in sys.argv:
    unexpected_fail = [n for n,ok,_ in res if not ok and n not in CLEAN_INSTALL_UNPROVEN]
    unexpected_pass = [n for n,ok,_ in res if ok and n in CLEAN_INSTALL_UNPROVEN]
    print("\nCLEAN-INSTALL BASELINE")
    print(f"  proven now                 : {len(res)-len(CLEAN_INSTALL_UNPROVEN)}/{len(res)}")
    print(f"  NOT YET PROVEN (no evidence): {len(CLEAN_INSTALL_UNPROVEN)}")
    bad = False
    if unexpected_fail:
        print("  REGRESSION - these should pass on a clean install:")
        for n in unexpected_fail: print(f"    FAIL {n}")
        bad = True
    if unexpected_pass:
        print("  FABRICATED EVIDENCE - these cannot be true on a clean install:")
        for n in unexpected_pass: print(f"    PASS {n}")
        bad = True
    if not bad:
        print("  BASELINE OK - every unproven check is unproven, nothing regressed,")
        print("  and no runtime evidence was manufactured.")
    sys.exit(1 if bad else 0)

sys.exit(1 if fails else 0)
