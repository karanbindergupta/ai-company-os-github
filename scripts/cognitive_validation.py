#!/usr/bin/env python3
"""Cognitive architecture validation - the section 44 checklist."""
import sqlite3, pathlib, subprocess, sys, collections
R=pathlib.Path(__file__).resolve().parent.parent
c=sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory=sqlite3.Row
res=[]
def t(n,ok,d=""): res.append((n,ok,d))
def one(q): return c.execute(q).fetchone()[0]
FIELDS=["cognitive_style","cog_strengths","blind_spots","instincts","decision_philosophy",
        "risk_profile","evidence_threshold","debate_style","pressure_behavior",
        "failure_behavior","counterbalanced_by","maturity_level"]
tot=one("SELECT COUNT(*) FROM agents")
full=one("SELECT COUNT(*) FROM agents WHERE " + " AND ".join(f"{f} IS NOT NULL AND {f}<>''" for f in FIELDS))
t("every agent has a cognitive profile", full==tot, f"{full}/{tot}")
ex=one("SELECT COUNT(*) FROM agents WHERE department='executive'")
exd=len({r["cognitive_style"] for r in c.execute("SELECT cognitive_style FROM agents WHERE department='executive'")})
t("every executive has a DISTINCTIVE cognitive model", exd==ex, f"{exd} distinct styles across {ex} executives")
t("every specialist has domain-specific instincts",
  one("SELECT COUNT(DISTINCT instincts) FROM agents")>=10,
  f"{one('SELECT COUNT(DISTINCT instincts) FROM agents')} distinct instinct sets")
t("blind spots documented", one("SELECT COUNT(*) FROM agents WHERE blind_spots<>''")==tot)
t("risk profiles exist and differ",
  one("SELECT COUNT(DISTINCT risk_profile) FROM agents")>=8,
  f"{one('SELECT COUNT(DISTINCT risk_profile) FROM agents')} distinct risk profiles")
t("evidence thresholds exist", one("SELECT COUNT(DISTINCT evidence_threshold) FROM agents")>=8)
t("confidence calibration exists",
  {"confidence"} <= {r[1] for r in c.execute("PRAGMA table_info(decisions)")})
t("debate styles exist and differ", one("SELECT COUNT(DISTINCT debate_style) FROM agents")>=10)
t("failure behaviour exists", one("SELECT COUNT(*) FROM agents WHERE failure_behavior<>''")==tot)
t("pressure behaviour exists", one("SELECT COUNT(*) FROM agents WHERE pressure_behavior<>''")==tot)
t("learning behaviour exists",
  (R/".ai-company/knowledge/lessons-learned").exists() and
  one("SELECT COUNT(*) FROM sqlite_master WHERE name='agent_performance'")==1)
def can(role,act,dom):
    return subprocess.run(["python3","scripts/companydb.py","can",role,act,dom],
                          capture_output=True,cwd=R).returncode
t("PERSONALITY DOES NOT OVERRIDE AUTHORITY",
  can("creative-director","decide","pricing")==2 and can("growth-strategist","veto","security_architecture")==2,
  "creative-director denied pricing; growth denied security veto")
t("agents can disagree constructively (dissent preserved)",
  one("SELECT COUNT(*) FROM sqlite_master WHERE name='dissent'")==1)
t("agents defer to legitimate expertise (counterbalances named)",
  one("SELECT COUNT(*) FROM agents WHERE counterbalanced_by<>''")==tot)
t("major decisions use independent analysis + ANTI-ANCHORING",
  one("SELECT COUNT(*) FROM sqlite_master WHERE name='cognitive_panels'")==1
  and "ANTI-ANCHORING" in (R/"scripts/cognition.py").read_text())
t("red-team behaviour exists",
  (R/".ai-company/org/roles/security/red-team.md").exists()
  and (R/".claude/skills/adversarial-review/SKILL.md").exists())
t("executive synthesis exists (CEO rules, does not vote)",
  "synthesize" in (R/"scripts/cognition.py").read_text()
  and (R/".ai-company/playbooks/executive/DECISION-FRAMEWORK.md").exists())
t("personality drift controls exist",
  one("SELECT COUNT(*) FROM sqlite_master WHERE name='drift_observations'")==1)
t("agent performance feeds improvement",
  one("SELECT COUNT(*) FROM sqlite_master WHERE name='agent_performance'")==1
  and (R/"scripts/agent_scorecard.py").exists())
t("decision QUALITY scored, not outcome",
  one("SELECT COUNT(*) FROM sqlite_master WHERE name='decision_quality'")==1)
t("maturity levels assigned, not self-claimed",
  one("SELECT COUNT(*) FROM agents WHERE maturity_level='5'")==0,
  "zero agents at L5 - it must be earned")
t("no personality theatre",
  not any(w in (R/"scripts/cognition.py").read_text().lower()
          for w in ["biography","backstory","roleplay as","pretend to be"]))
t("NO DUPLICATE cognitive systems",
  not (R/".ai-company/cognition/profiles").exists()
  and one("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE '%profile%'")==0,
  "profiles live in the agents table only")
fails=sum(1 for _,ok,_ in res if not ok)
for n,ok,d in res: print(f"  [{'PASS' if ok else 'FAIL'}] {n}" + (f"  ({d})" if d else ""))
print(f"\n{'='*62}\nCOGNITIVE VALIDATION: {len(res)-fails}/{len(res)} passed" + ("" if not fails else f"  {fails} FAILED"))
sys.exit(1 if fails else 0)
