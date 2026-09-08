#!/usr/bin/env python3
"""Sync roles.json from the role packs. Packs are the source of truth for role metadata;
the registry is an index. They drifted once (reports_to), so this makes the sync explicit."""
import json, pathlib, re, sys
R=pathlib.Path(__file__).resolve().parent.parent
idx=R/".ai-company/org/roles.json"
d=json.loads(idx.read_text()); by={r["slug"]:r for r in d["roles"]}
changed=[]
for p in (R/".ai-company/org/roles").rglob("*.md"):
    fm=p.read_text().split("---")[1]
    slug=p.stem
    if slug not in by: continue
    for field in ("reports_to","department","seniority","name","title"):
        m=re.search(rf"^{field}:\s*(.+)$", fm, re.M)
        if m:
            v=m.group(1).strip()
            if by[slug].get(field)!=v:
                changed.append(f"{slug}.{field}: {by[slug].get(field)} -> {v}")
                by[slug][field]=v
    by[slug]["path"]=str(p.relative_to(R))
d["roles"]=sorted(by.values(), key=lambda r:(r["department"],r["slug"])); d["count"]=len(d["roles"])
idx.write_text(json.dumps(d,indent=2))
print(f"registry synced from {len(list((R/'.ai-company/org/roles').rglob('*.md')))} packs; {len(changed)} field(s) updated")
for ch in changed[:12]: print("  "+ch)
