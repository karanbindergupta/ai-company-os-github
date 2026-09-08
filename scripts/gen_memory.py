#!/usr/bin/env python3
"""Generate the complete AI-employee directory from the company database.
Generated, never hand-written, so it cannot drift from the source of truth."""
import sqlite3, pathlib, collections, json
R=pathlib.Path(__file__).resolve().parent.parent
c=sqlite3.connect(R/".ai-company/state/company.db"); c.row_factory=sqlite3.Row
rows=list(c.execute("SELECT * FROM agents WHERE status='active' ORDER BY department,authority_level,id"))
byid={r["id"]:r for r in rows}
reports=collections.defaultdict(list)
for a in rows:
    if a["reports_to"]: reports[a["reports_to"]].append(a["id"])
owns=collections.defaultdict(list); revs=collections.defaultdict(list); vet=collections.defaultdict(list)
DR={}
for r in c.execute("SELECT * FROM decision_rights"):
    DR[r["domain"]]=r; owns[r["owner"]].append(r["domain"])
    for x in [y for y in r["reviewers"].split(",") if y]: revs[x].append(r["domain"])
    for x in [y for y in r["veto_holders"].split(",") if y]: vet[x].append(r["domain"])
BC={r["agent"]:r for r in c.execute("SELECT * FROM behavioral_contracts")}
DRILLS=collections.defaultdict(list)
for d in c.execute("SELECT * FROM drills"): DRILLS[d["role"]].append(d["id"])
RUNS=collections.defaultdict(list)
for d in c.execute("SELECT * FROM drill_runs WHERE verdict<>'INCONCLUSIVE'"):
    RUNS[d["agent"]].append(f"{d['drill']}={d['verdict']}({d['score']})")
PB={"executive":"playbooks/executive/","strategy-research":"playbooks/research.md",
"product":"playbooks/product.md","creative":"playbooks/design.md",
"engineering":"playbooks/engineering.md + playbooks/engineering/","quality":"playbooks/engineering.md",
"security":"playbooks/security.md","growth":"playbooks/growth/","operations":"playbooks/operations/",
"people":"playbooks/people/","commercial":"playbooks/sales/"}
TOOLS={"strategy-research":"WebSearch, WebFetch, exa, tavily (researcher_family)",
"engineering":"Bash, Read, Write, Edit, Grep, Glob, github (engineer_family)",
"quality":"Bash, Read, Grep, Glob, claude-browser, chrome-devtools (qa_family)",
"security":"Bash, Read, Grep, Glob, claude-security, npm-audit (security_family)",
"creative":"Read, Write, Edit, adobe-express, cloudinary, v0, miro (design_family)",
"executive":"Read, Write, Edit, WebSearch, WebFetch","product":"Read, Write, Edit, WebSearch, WebFetch",
"growth":"Read, Write, Edit, WebSearch, WebFetch","operations":"Read, Write, Edit, Grep, Glob, Bash",
"people":"Read, Write, Edit, WebSearch, WebFetch","commercial":"Read, Write, Edit, WebSearch, WebFetch"}
DEPTN={"executive":"Executive Council","strategy-research":"Strategy & Research","product":"Product",
"creative":"Creative & Brand","engineering":"Engineering","quality":"Quality","security":"Security",
"growth":"Growth & Marketing","operations":"Operations","people":"People (HR)","commercial":"Commercial"}
order=["executive","strategy-research","product","creative","engineering","quality","security",
       "growth","operations","people","commercial"]
by=collections.defaultdict(list)
for r in rows: by[r["department"]].append(r)

L=["---","document: ai-employee-directory","version: 1.0.0","generated_by: scripts/gen_memory.py",
   "source_of_truth: .ai-company/state/company.db","---","",
   "# AI EMPLOYEE DIRECTORY — all 119",""
   ,"**Generated from the database.** Do not hand-edit; run `python3 scripts/gen_memory.py`.",
   "Full behavioural spec for each person is in their **role pack** (path given per entry).","",
   "## Index","","| Dept | Count | Head |","|---|---|---|"]
for d in order:
    head=[a for a in by[d] if a["authority_level"]<=1] or by[d][:1]
    L.append(f"| {DEPTN[d]} | {len(by[d])} | {head[0]['name']} |")
L+=["",f"**Total: {len(rows)} employees across {len(by)} departments.**","","---",""]
for d in order:
    L+=[f"# {DEPTN[d]} ({len(by[d])})",""]
    for a in sorted(by[d], key=lambda x:(x["authority_level"],x["id"])):
        boss = byid[a["reports_to"]]["name"] if a["reports_to"] in byid else "FOUNDER (Karan)"
        subs = [byid[s]["name"] for s in reports.get(a["id"],[])]
        bc = BC.get(a["id"])
        L+=[f"## {a['name']} — {a['title']}","",
        f"| Field | Value |","|---|---|",
        f"| **Role slug** (canonical for all commands) | `{a['id']}` |",
        f"| Department | {DEPTN[d]} |",
        f"| Seniority / authority level | {a['seniority']} / L{a['authority_level']} |",
        f"| **Reports to** | {boss} |",
        f"| **Direct reports** | {', '.join(subs) if subs else 'none — individual contributor'} |",
        f"| **Owns decisions** | {', '.join(owns.get(a['id'],[])) or 'none — works within role-pack authority'} |",
        f"| **Reviews decisions** | {', '.join(revs.get(a['id'],[])) or 'none'} |",
        f"| **VETO over** | {'**'+', '.join(vet[a['id']])+'**' if a['id'] in vet else 'none'} |",
        f"| Backs up | {byid[a['backup_for']]['name'] if a['backup_for'] in byid else '—'} |",
        f"| Primary artifact | `{a['artifact']}` |",
        f"| Role pack (full spec) | `{a['pack_path']}` |",
        f"| Playbook | `{PB.get(d,'—')}` |",
        f"| Tools | {TOOLS.get(d,'—')} |",
        f"| Maturity | **L{a['maturity_level']}** ({'DEFINED' if str(a['maturity_level'])=='1' else 'CONFIGURED' if str(a['maturity_level'])=='2' else 'RELIABLE' if str(a['maturity_level'])=='3' else 'ADVANCED' if str(a['maturity_level'])=='4' else 'PROVEN'}) |",
        f"| Drills available | {', '.join(DRILLS.get(a['id'],[])) or 'none authored yet'} |",
        f"| Drills run | {', '.join(RUNS.get(a['id'],[])) or '**UNTESTED**'} |","",
        f"**Cognitive style** — {a['cognitive_style'] or 'UNKNOWN'}","",
        f"**Strengths** — {a['cog_strengths'] or 'UNKNOWN'}","",
        f"**Blind spots** — {a['blind_spots'] or 'UNKNOWN'}","",
        f"**Instincts (what they look for unprompted)** — {a['instincts'] or 'UNKNOWN'}","",
        f"**Decision philosophy** — {a['decision_philosophy'] or 'UNKNOWN'}","",
        f"**Risk profile** — `{a['risk_profile'] or 'UNKNOWN'}`","",
        f"**Evidence threshold** — {a['evidence_threshold'] or 'UNKNOWN'}","",
        f"**Debate style (how they disagree)** — {a['debate_style'] or 'UNKNOWN'}","",
        f"**Under pressure** — {a['pressure_behavior'] or 'UNKNOWN'}","",
        f"**On failure / when wrong** — {a['failure_behavior'] or 'UNKNOWN'}","",
        f"**Counterbalanced by** — {a['counterbalanced_by'] or 'UNKNOWN'}",""]
        if bc:
            L+=[f"**Escalation** — {bc['escalation_behaviors']}","",
                f"**Prohibited** — {bc['prohibited_behaviors']}","",
                f"**When information is missing** — {bc['evidence_behaviors']}","",
                f"**Quality bar** — {bc['quality_behaviors']}",""]
        L.append("---\n")
(R/".ai-company/org/AI-EMPLOYEE-DIRECTORY.md").write_text("\n".join(L)+"\n")
print(f"AI-EMPLOYEE-DIRECTORY.md: {len(rows)} employees, {len(L)} lines")

# Hierarchy tree
H=["---","document: hierarchy","generated_by: scripts/gen_memory.py","---","",
   "# COMPLETE ORGANIZATIONAL HIERARCHY","",
   "Role slugs are canonical for every command. Names are for humans.","","```"]
H.append("FOUNDER (Karan) — final authority on everything reserved to the founder")
def tree(node,ind):
    for s in sorted(reports.get(node,[])):
        a=byid[s]
        mark=""
        if s in vet: mark=f"  [VETO: {', '.join(vet[s])}]"
        elif s in owns: mark=f"  [owns: {', '.join(owns[s][:2])}]"
        H.append(f"{ind}└── {a['name']:<26} {a['id']:<30}{mark}")
        tree(s,ind+"    ")
H.append("  └── Nadia Okonkwo             ceo")
tree("ceo","      ")
H+=["```","","## Relationship rules","",
 "| Relationship | Rule |","|---|---|",
 "| Reports to | Exactly one manager per agent. Zero circular reporting (verified by `staffing_audit.py`) |",
 "| Delegates work | Only downward, to direct reports. The orchestrator may route across the tree |",
 "| Reviews work | The reviewer is NEVER the owner. Enforced by DB CHECK `owner <> reviewer` |",
 "| Approves | Only the named reviewers for that decision domain |",
 "| Escalates | L0 self → L1 peer → L2 lead → L3 executive → L4 FOUNDER |",
 "| Final report | Reaches the founder as a decision package, never raw research |",
 "| Peers | Agents at the same authority level in the same department |",
 "| No subordinates | Any agent with `Direct reports: none` in the directory |",
 "| Requires approval before acting | Any agent acting in a founder-required domain (9 of 29) |","",
 "## Authority levels","",
 "| Level | Who | Meaning |","|---|---|---|",
 "| **L0** | Founder (Karan) | Final authority. Cannot be overridden by any agent |",
 "| L1 | Executive Council (13) | Domain authority; CEO resolves inter-executive conflict |",
 "| L2 | Leads / architects | Departmental execution and standards |",
 "| L3 | Specialists | Their craft, within their role pack |","",
 "## Vetoes — who can block what","","| Holder | Domains |","|---|---|"]
for k in sorted(vet): H.append(f"| {byid[k]['name']} (`{k}`) | {', '.join(vet[k])} |")
H+=["","**The CISO veto on `gate_security` is not overridable by the CTO or CEO.** Only the founder may",
    "accept a security risk, and that acceptance is recorded against their name.","",
    "## Founder-required decision domains (9)","",
    "| Domain | Owner |","|---|---|"]
for dom,r in sorted(DR.items()):
    if r["founder_required"]: H.append(f"| `{dom}` | {byid[r['owner']]['name'] if r['owner'] in byid else r['owner']} |")
(R/".ai-company/org/HIERARCHY.md").write_text("\n".join(H)+"\n")
print(f"HIERARCHY.md written")

# Drills
D=["---","document: drill-catalogue","generated_by: scripts/gen_memory.py","---","",
   "# DRILL & TRAINING CATALOGUE","",
   "Drills test **behaviour**, scored by **automated rubric in `scripts/behavior.py`** — code reading",
   "text, not a model grading itself. Rubrics are sentence-scoped and negation-aware.","",
   f"**{c.execute('SELECT COUNT(*) FROM drills').fetchone()[0]} drills authored · "
   f"{c.execute(chr(39).join(['SELECT COUNT(*) FROM drill_runs WHERE verdict<>','INCONCLUSIVE',''])).fetchone()[0]} runs recorded**",""]
for d in c.execute("SELECT * FROM drills ORDER BY category,id"):
    runs=[f"{r['agent']}: {r['verdict']} ({r['score']})" for r in
          c.execute("SELECT * FROM drill_runs WHERE drill=? AND verdict<>'INCONCLUSIVE'",(d["id"],))]
    D+=[f"## {d['id']} — {d['behavioral_target']}","",
        f"| | |","|---|---|",
        f"| **Purpose** | {d['behavioral_target']} |",
        f"| **Category / trigger** | {d['category']} — run on hire, on drift alert, or on profile change |",
        f"| **Agent** | `{d['role']}` |",
        f"| **Difficulty / pressure** | {d['difficulty']} / {d['pressure_level']} |",
        f"| **Inputs (scenario)** | {d['scenario']} |",
        f"| **Context** | {d['context']} |",
        f"| **Expected behaviour** | {d['expected_behaviors']} |",
        f"| **Anti-patterns (failure conditions)** | {d['anti_patterns']} |",
        f"| **Rubric** | {d['rubric']} |",
        f"| **Pass criteria** | {d['pass_criteria']} |",
        f"| **Fail criteria** | {d['fail_criteria']} |",
        f"| **Procedure** | `behavior.py drill run drill={d['id']} agent={d['role']} response_file=<path> evaluator=<other role>` |",
        f"| **Review** | Evaluator must not be the agent. Failures generate coaching via `behavior.py coach` |",
        f"| **Results** | {'; '.join(runs) if runs else '**NOT YET RUN**'} |","","---",""]
(R/".ai-company/behavior/DRILL-CATALOGUE.md").write_text("\n".join(D)+"\n")
print("DRILL-CATALOGUE.md written")
