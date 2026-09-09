#!/usr/bin/env python3
"""bootstrap.py - rebuild the Company OS + Execution Harness from repository source.

A clean checkout has no company.db. This reconstructs it, in order:

  1. companydb.py init   -> base schema (schema.sql) + 121 agents from the role packs
  2. seed.sql            -> non-reproducible configuration: cognitive profiles,
                            behavioural contracts, permission policy, decision
                            rights, drills, integrations
  3. harness.py migrate  -> execution-harness schema, migrations v2+

Why step 2 exists: `companydb.py init` inserts only nine agent fields, and roles.json
carries none of the cognitive architecture. Without seed.sql the cognitive profiles -
which CLAUDE.md section 7 calls the load-bearing field - cannot be reconstructed at all.

Idempotent. Safe to re-run. Refuses to overwrite an existing database unless --force.
"""
import subprocess, sqlite3, pathlib, sys

R = pathlib.Path(__file__).resolve().parent.parent
DB = R / ".ai-company/state/company.db"
SEED = R / ".ai-company/state/seed.sql"


def run(*a):
    r = subprocess.run([sys.executable] + list(a), cwd=str(R), capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    force = "--force" in sys.argv
    if DB.exists() and not force:
        print(f"database already exists: {DB}")
        print("  Re-running is safe but will not re-seed. Use --force to rebuild from source.")
        print("  Applying any pending harness migrations instead...")
        rc, out = run("scripts/harness.py", "migrate")
        if out:
            print("  " + out.splitlines()[-1])
        return 0

    print("=" * 66)
    print("  BOOTSTRAP - Company OS + Execution Harness from source")
    print("=" * 66)

    print("\n[1/4] companydb.py init  (base schema + roles)")
    rc, out = run("scripts/companydb.py", "init", *(["--force"] if force else []))
    if rc != 0:
        print("  FAILED:\n" + out)
        return 1
    for ln in out.splitlines()[:3]:
        print("      " + ln)

    print("\n[2/4] seed.sql  (cognitive profiles, contracts, policy, rights, drills)")
    if not SEED.exists():
        print(f"  FAILED: {SEED} is missing. The cognitive architecture cannot be rebuilt "
              f"without it; no other tracked source contains it.")
        return 1
    con = sqlite3.connect(str(DB))
    try:
        con.executescript(SEED.read_text())
        con.commit()
    except Exception as e:
        print(f"  FAILED applying seed: {e}")
        return 1
    n_cog = con.execute("SELECT COUNT(*) FROM agents WHERE cognitive_style IS NOT NULL "
                        "AND cognitive_style<>''").fetchone()[0]
    n_con = con.execute("SELECT COUNT(*) FROM behavioral_contracts").fetchone()[0]
    n_pol = con.execute("SELECT COUNT(*) FROM permission_policy").fetchone()[0]
    con.close()
    print(f"      cognitive profiles: {n_cog}   behavioural contracts: {n_con}   "
          f"permission policy: {n_pol}")

    print("\n[3/4] harness.py migrate  (execution harness schema)")
    rc, out = run("scripts/harness.py", "migrate")
    if rc != 0:
        print("  FAILED:\n" + out)
        return 1
    if out:
        print("      " + out.splitlines()[-1])

    # tasks.json is a DERIVED read-only projection of the authoritative task table.
    # A clean checkout has no projection, so `harness.py tasks-check` refused on a
    # fresh install and CI failed for a file the install itself should produce.
    # Emit it here so a bootstrapped tree is immediately coherent.
    print("\n[4/4] tasks-project  (emit derived tasks.json projection)")
    rc, out = run("scripts/harness.py", "tasks-project")
    if rc != 0:
        print("  FAILED:\n" + out)
        return 1
    if out:
        print("      " + out.splitlines()[-1])

    con = sqlite3.connect(str(DB))
    tables = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
    agents = con.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    rules = con.execute("SELECT COUNT(*) FROM permission_rules").fetchone()[0]
    con.close()
    print("\n" + "=" * 66)
    print(f"  READY   tables={tables}  agents={agents}  permission_rules={rules}")
    print("  Verify:  python3 scripts/companydb.py verify && python3 scripts/harness.py verify")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
