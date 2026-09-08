#!/usr/bin/env python3
"""Structural audit of the organization itself. Run after any org change."""
import json,re,pathlib,collections,sys
root=pathlib.Path(__file__).resolve().parent.parent
agents={p.stem for p in (root/".claude/agents").glob("*.md")}
reg=json.load(open(root/".ai-company/org/roles.json"))["roles"]
roles={r["slug"] for r in reg}
phases=json.load(open(root/".ai-company/sop/phases.json"))["phases"]
gates=json.load(open(root/".ai-company/sop/gates.json"))["gates"]
issues=[]

# every path any role pack declares in its Outputs table
declared=set()
for r in reg:
    for m in re.findall(r"\|\s*[^|]+\|\s*`([^`]+)`\s*\|", (root/r["path"]).read_text()):
        declared.add(m.rstrip("/"))

for p in (root/".claude/commands").glob("*.md"):
    t=p.read_text()
    for m in set(re.findall(r'[Dd]ispatch(?:es)?\s+`([a-z][a-z0-9-]+)`', t)):
        if m not in agents and m not in roles:
            issues.append(f"[broken-ref] {p.name}: dispatches '{m}' - neither an agent nor a role")
for r in reg:
    if r["reports_to"] not in roles and r["reports_to"]!="founder":
        issues.append(f"[org] '{r['slug']}' reports to unregistered '{r['reports_to']}'")
g=collections.defaultdict(list)
for ph in phases:
    if ph["gate"]!="gate_none": g[ph["gate"]].append(ph["id"])
for k,v in g.items():
    if len(v)>1: issues.append(f"[gate-reuse] '{k}' shared by phases {v}")
for k in gates:
    if k not in g: issues.append(f"[unused-gate] '{k}' is defined but no phase uses it")
titles=collections.Counter(r["title"] for r in reg)
for t,c in titles.items():
    if c>1: issues.append(f"[duplicate] role title '{t}' appears {c} times")
for ph in phases:
    for a in ph["artifacts"]:
        if a.rstrip("/") not in declared:
            issues.append(f"[orphan-artifact] phase '{ph['id']}' requires {a} - no role declares it")
    if ph["owner"] not in roles: issues.append(f"[phase] '{ph['id']}' owner '{ph['owner']}' unregistered")
for a in agents:
    if not (root/".claude/agents"/f"{a}.md").read_text().startswith("---"):
        issues.append(f"[agent] '{a}' missing frontmatter")
print(f"ORGANIZATION AUDIT - {len(issues)} finding(s)")
for i in issues: print("  "+i)
sys.exit(1 if issues else 0)
