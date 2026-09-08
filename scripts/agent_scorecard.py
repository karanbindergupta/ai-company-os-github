#!/usr/bin/env python3
"""Agent performance scoring. Quality-weighted - speed is deliberately not a metric."""
import sqlite3, pathlib, sys
R = pathlib.Path(__file__).resolve().parent.parent
c = sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory = sqlite3.Row
rows = list(c.execute("""SELECT role, COUNT(*) n,
    SUM(CASE WHEN outcome='done' THEN 1 ELSE 0 END) done,
    SUM(CASE WHEN outcome='failed' THEN 1 ELSE 0 END) failed,
    SUM(rework) rework, SUM(review_failed) revfail, SUM(escalated) esc
    FROM agent_performance GROUP BY role ORDER BY n DESC"""))
if not rows:
    print("No agent performance records yet.")
    print("Populated automatically by `companydb.py task update`. Scoring needs real missions.")
    sys.exit(0)
print(f"{'ROLE':<28}{'TASKS':>6}{'DONE':>6}{'FAIL':>6}{'REWORK':>8}{'REVFAIL':>9}{'SCORE':>7}")
for r in rows:
    n = r["n"] or 1
    # completion earns, rework and review failure cost more than failure alone -
    # an agent that finishes fast and creates rework must score worse than a slow correct one
    score = round(max(0, min(5, 5*(r["done"]/n) - 1.5*(r["rework"]/n) - 2.0*(r["revfail"]/n))), 2)
    print(f"{r['role'][:27]:<28}{r['n']:>6}{r['done']:>6}{r['failed']:>6}{r['rework']:>8}{r['revfail']:>9}{score:>7}")
print("\nSpeed is not scored. Rework and review failure are weighted above raw completion.")
