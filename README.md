# AI Company OS

An autonomous multi-agent organization for Claude Code. The founder supplies an industry and a
rough idea; the company performs the research, strategy, product definition, financial analysis,
competitive intelligence, creative direction, architecture, engineering, QA, security and auditing
required to turn it into a real product.

```
/company-start Industry: <industry>. Idea: <one line>.
```

## What is here

| | |
|---|---|
| **107 roles** | 10 departments, each a full job specification in `.ai-company/org/roles/` |
| **18 subagents** | `.claude/agents/` — isolated context, scoped tools; they adopt role packs |
| **23 commands** | `.claude/commands/` — founder-facing, wired to the state engine |
| **9 skills** | `.claude/skills/` — organizational discipline (evidence, gates, parallelism, failure) |
| **23 phases** | `.ai-company/sop/phases.json` — the SOP every mission follows |
| **13 gates** | `.ai-company/sop/gates.json` — enforced in code, not prose |

## Governance is executable, not advisory

```bash
python3 scripts/company.py validate     # graph, roles, phases, gates
python3 scripts/audit_org.py            # structural audit of the organization itself
python3 scripts/company.py resume       # where to continue after any interruption
```

A phase cannot complete with missing artifacts, an unpassed gate, or open tasks. A task cannot be
marked done without evidence on disk. A release cannot pass without recorded founder
authorization. These are refusals in `scripts/company.py`, not requests in a prompt.

## Resumability

State is written atomically at every transition, so a run survives session limits and crashes.
`/company-resume` continues exactly where it stopped; completed phases are never redone.

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — the operating constitution every agent inherits
- [`.ai-company/docs/FOUNDER-GUIDE.md`](.ai-company/docs/FOUNDER-GUIDE.md) — how to use it
- [`.ai-company/docs/ARCHITECTURE.md`](.ai-company/docs/ARCHITECTURE.md) — how and why it is built this way
- [`.ai-company/org/ORG-CHART.md`](.ai-company/org/ORG-CHART.md) — the full organization
- [`.ai-company/audits/organization.md`](.ai-company/audits/organization.md) — the dry run and its 32 fixed defects
- [`.ai-company/tooling/`](.ai-company/tooling/) — the environment audit this was built on

## Known limits

- **GitHub Actions/CI cannot be inspected** from this environment; the company will not claim CI status.
- **No Homebrew**, so `gitleaks`/`trivy`/Docker are unavailable. Dependency scanning is `npm audit`
  plus the `claude-security` plugin.
- The dry run verified structure and enforcement. **No phase has yet been executed by a live
  fan-out of subagents** — the first real mission is the true test.
