# AI COMPANY OS — ARCHITECTURE

## The problem this design solves

Claude Code loads **every** `.claude/agents/*.md` description into the parent context. An
organization with 107 agent files would consume the orchestrator's context before it read the
mission. Most "AI company" designs either stay small to avoid this, or grow large and degrade.

**This design separates the executable surface from the organizational surface.**

| | Executable subagents | Role packs |
|---|---|---|
| Where | `.claude/agents/` | `.ai-company/org/roles/` |
| Count | 18 | 107 |
| Context cost | Loaded into the orchestrator always | Loaded on demand, by the agent that needs it |
| What they are | Vessels with isolated context and scoped tools | Job specifications |

An agent becomes a specialist by reading a role pack. The `researcher` subagent is a market
researcher, a competitor analyst, or a feasibility analyst depending on which pack it loads.

**Consequence:** adding a specialist costs one markdown file and zero orchestrator context.
Adding a subagent costs context permanently — which is why the Chief People Officer may create
role packs freely but needs founder approval for a new subagent.

## What was borrowed, and from where

| Source | Idea taken | How it appears here |
|---|---|---|
| **MetaGPT** (`Code = SOP(Team)`) | Agents exchange structured artifacts, not conversation; phases encoded as an SOP | `.ai-company/sop/phases.json`, the artifact contract in `CLAUDE.md` §3 |
| **Claude Code subagents** | Isolated context, fan-out/fan-in, return conclusions not transcripts | The 18 vessels; `parallel-dispatch` skill; worktree isolation for engineering |
| **LangGraph checkpointing** | Persist state at every step boundary, not at the end | `scripts/company.py` writes atomically at every transition; `resume` |
| **CrewAI** | Role-based team simulation | The 107-role registry with explicit authority boundaries |

Nothing was copied. The ideas were extracted and rebuilt for this environment's constraints.

## The five layers

```
FOUNDER
   |  /company-start "industry" "idea"
   v
COMMANDS (.claude/commands/, 23)          founder-facing verbs
   |
   v
ORCHESTRATOR (.claude/agents/orchestrator.md)
   |  reads state -> decomposes -> dispatches parallel groups -> enforces gates
   v
SUBAGENTS (.claude/agents/, 18)           isolated context, scoped tools
   |  each adopts a role pack
   v
ROLE PACKS (.ai-company/org/roles/, 107)  the actual organization
   |  each writes its artifact
   v
STATE (.ai-company/, scripts/company.py)  durable, resumable, enforced
```

## Why the state engine is code, not prose

Governance written only in prompts is advisory — a model under pressure will rationalize past it.
These rules are enforced in `scripts/company.py` and cannot be talked around:

| Rule | Enforcement |
|---|---|
| No fake completion | `phase-complete` refuses when required artifacts are absent from disk |
| No unearned gate | `phase-complete` refuses when the phase's gate is not `passed` |
| No evidence-free done | `task-update status=done` refuses without an `evidence` path |
| No dependency cycles | `validate` performs colour-marking cycle detection |
| No invented roles | `validate` rejects any task owner not in the registry |
| No unauthorized release | `gate_release` refuses without a `founder_approval` value |
| No silent ID reuse | Task ids are monotonic; self- and unknown dependencies rejected at creation |

## Resumability

A run survives session limits because state is written **at every transition**, atomically
(temp file then rename, so a killed process never leaves a torn state file).

```bash
python3 scripts/company.py resume
```
reports the next incomplete phase, its owner, its exit criteria, and which artifacts already
exist. A `SessionStart` hook surfaces this automatically so an interrupted mission is never
silently restarted.

## Parallelism

`ready` groups tasks that share no unresolved dependency. The orchestrator dispatches a whole
group **in one message**, which is what makes them run concurrently — dispatching across separate
messages silently serializes them, and is the most common way parallelism is lost.

Genuinely parallel: the six research roles; executive positions in a debate; architecture and
design; QA and security; the four audits.

Only apparently parallel: backend and frontend before the API contract is agreed.

## Relationship to the ECC plugin

ECC (already installed) supplies 286 **domain** skills and 68 coding agents. This system supplies
the **organization**: hierarchy, authority, gates, state and orchestration. The nine skills in
`.claude/skills/` are deliberately organizational only — they do not duplicate ECC's domain
coverage. When a role needs domain expertise, it should reach for ECC's skills.
