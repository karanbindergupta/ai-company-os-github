"""Emit a role pack. Shared by the department batch generators."""
import os, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
REG = ROOT / ".ai-company/org/roles"

DEFAULT_TOOLS = "Read, Write, Edit, Grep, Glob"
RESEARCH_TOOLS = "Read, Write, Edit, Grep, Glob, WebSearch, WebFetch"
ENG_TOOLS = "Read, Write, Edit, Grep, Glob, Bash"

_registry = []

def role(slug, title, dept, reports_to, mission, responsibilities, authority,
         inputs, outputs, activate, never, collab, quality, escalate,
         tools=DEFAULT_TOOLS, seniority="specialist", on_failure=None):
    """outputs: list of (artifact_name, path). Everything else: str or list[str]."""
    def bullets(x):
        return "\n".join(f"- {i}" for i in x) if isinstance(x, list) else f"- {x}"
    out_rows = "\n".join(f"| {n} | `{p}` |" for n, p in outputs)
    fail = on_failure or (
        "Write what you learned to your artifact with `status: partial` and an explicit "
        "`blocked_on` field naming what you need. Never emit an empty or invented artifact. "
        "Do not retry the same approach twice — change strategy or escalate to your lead.")
    body = f"""---
role: {slug}
title: {title}
department: {dept}
reports_to: {reports_to}
seniority: {seniority}
primary_artifact: {outputs[0][1]}
---

# {title}

> Load with: `Read .ai-company/org/roles/{dept}/{slug}.md and act strictly as this role.`
> You are a member of one organization. `CLAUDE.md` governs you.

## Mission
{mission}

## Responsibilities
{bullets(responsibilities)}

## Authority
{authority}

## Inputs
{bullets(inputs)}

## Outputs — write these files; do not answer in prose
| Artifact | Path |
|---|---|
{out_rows}

## Tools
`{tools}`

## Activate when
{bullets(activate)}

## Do NOT activate when
{bullets(never)}

## Collaboration
{bullets(collab)}

## Quality standards
{bullets(quality)}

## Escalation
{escalate}

## On failure
{fail}
"""
    d = REG / dept
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.md").write_text(body)
    _registry.append({"slug": slug, "title": title, "department": dept,
                      "reports_to": reports_to, "seniority": seniority,
                      "artifact": outputs[0][1],
                      "path": f".ai-company/org/roles/{dept}/{slug}.md"})

def flush():
    idx = REG.parent / "roles.json"
    existing = json.loads(idx.read_text())["roles"] if idx.exists() else []
    by = {r["slug"]: r for r in existing}
    for r in _registry:
        by[r["slug"]] = r
    allr = sorted(by.values(), key=lambda r: (r["department"], r["slug"]))
    idx.write_text(json.dumps({"version": 1, "count": len(allr), "roles": allr}, indent=2))
    print(f"wrote {len(_registry)} roles; registry now {len(allr)}")
