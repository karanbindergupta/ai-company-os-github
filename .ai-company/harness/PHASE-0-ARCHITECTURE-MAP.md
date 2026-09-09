---
artifact: harness-architecture-map
role: principal-architect
phase: harness-discovery
mission: HARNESS LAYER
status: complete
confidence: HIGH
retrieved: 2026-09-09
note: Read-only discovery. Nothing was modified.
---
# Phase 0 — architecture map, and Phase 1 — capability classification

**The evidence base is unusually strong: this session BROKE the harness layer repeatedly while
running a real mission.** Every gap below is backed by an observed failure in `run_a2d1d5010d`, not
by a checklist. That is the difference between an audit and a guess.

---
# THE FINDING, IN ONE SENTENCE
> **The Company OS has excellent governance *schema* and almost no execution *wiring*. The tables
> exist. Nothing writes to them when real agents do real work.**

The harness is not a missing framework. It is **missing plumbing between the orchestrator's
decisions and the agents' actual execution.**

---
# 1. WHAT EXISTS (verified, read-only)

| Layer | Mechanism | State |
|---|---|---|
| Governance | `companydb.py` — 54 tables: authority, vetoes, decision_rights, escalations, risks | **Works.** Live-tested this session |
| SOP / phases | `company.py` — 23 phases, 13 gates, refuses to skip | **Works** |
| Task graph | `company.py task-add/update/list` → **`.ai-company/state/tasks.json`** | Works, but see §2.1 |
| Agent spawn | **Claude Code `Task` tool only.** No script spawns agents — `grep subprocess scripts/*.py` returns only validation suites calling `companydb.py` | **ENTIRELY OUTSIDE THE OS** |
| Evidence | Markdown artifacts on disk + `audit_log` (157 rows) | Partial — see §2.2 |
| Git isolation | `git worktree` — this session runs in one | Works, but unmanaged |
| Hooks | **`session-start.sh` only** | No PreToolUse / PostToolUse / Stop hooks |
| Migrations | `schema_version` table (=1); `schema.sql` uses `CREATE TABLE IF NOT EXISTS` ×27, bare `CREATE TABLE` ×0 | **Already idempotent.** The founder's CI concern does not reproduce here |

---
# 2. THE FOUR STRUCTURAL DEFECTS

## 2.1 — TWO TASK STORES, ALREADY DIVERGED. Violates D-2.
```
.ai-company/state/tasks.json   →  22 tasks   (company.py writes here)
companydb.tasks table          →   0 rows    (companydb.py writes here)
```
**D-2 states: "Single SQLite database, no parallel stores — two sources of truth silently diverge."**
They have diverged. `companydb.py task` and `company.py task-add` are two task systems that do not
know about each other. Every separation-of-duties guarantee in `companydb.py task update`
(evidence required, owner ≠ reviewer, independent review) **is bypassed entirely** because the
orchestrator writes to the JSON store instead.

**This is the single most serious finding in Phase 0.**

## 2.2 — BIDIRECTIONAL FILE/DB DRIFT. Evidence is not linked to anything.
```
incidents:   4 files on disk  →  0 DB rows
decisions:  11 files on disk  →  0 DB rows
risks:       0 files on disk  → 20 DB rows
evidence table:                  0 rows      ← in an evidence-driven company
```
Drift runs **both ways**. The `evidence` table being empty while the mission produced ~40 sourced
artifacts is the clearest statement of the gap: **evidence exists as prose, not as queryable state.**

## 2.3 — NO EXECUTION LEDGER. The OS cannot see its own work.
```
tasks 0 · task_deps 0 · handoffs 0 · tool_permissions 0 · agent_performance 0 · incidents 0
```
This session dispatched **~10 agents** consuming **>1M subagent tokens**. The Company DB records
**none of it**: no execution rows, no tool calls, no cost, no duration, no outcome. `agent_scorecard.py`
has nothing to score. Maturity can never be earned because no execution is ever recorded.

## 2.4 — SPAWN IS OUTSIDE GOVERNANCE.
Agent dispatch happens through the Claude Code `Task` tool, which the Company OS cannot observe,
authorise, checkpoint, resume, or stop. **Authority is enforced at the database and ignored at the
point of execution.**

---
# 3. PHASE 1 — THE 35 CAPABILITIES, CLASSIFIED
Each verdict is followed by the **observed evidence** where this session produced it.

| # | Capability | Verdict | Evidence from this run |
|---|---|---|---|
| 1 | Agent lifecycle management | **MISSING** | No lifecycle record exists anywhere |
| 2 | Agent spawning | **INADEQUATE** | `Task` tool works but is invisible to the OS |
| 3 | Parallel execution | **PARTIALLY** | 4 executives ran in parallel — but **3 died on a session rate limit** with no backpressure or queueing |
| 4 | Context isolation | **IMPLEMENTED** | Subagents have isolated context by construction |
| 5 | Context compaction | **IMPLEMENTED** (host) | Provided by Claude Code, not by the OS |
| 6 | Context persistence | **PARTIALLY** | Artifacts persist; agent context does not |
| 7 | Checkpointing | **MISSING** | 3 agents died mid-write; artifacts survived only because they wrote before summarising. **Luck, not design** |
| 8 | Resume / recovery | **MISSING** | No agent has ever been resumed. `SendMessage` is disabled in this session |
| 9 | Tool permission enforcement | **MISSING** | `tool_permissions` table: **0 rows**. `permission_policy` unused |
| 10 | Sandbox / isolation | **PARTIALLY** | Bash sandbox + GateGuard hook |
| 11 | Git worktree isolation | **PARTIALLY** | In use, unmanaged, unrecorded |
| 12 | Branch management | **MISSING** | No branch/worktree registry |
| 13 | Task state management | **DUPLICATED** | §2.1 — two stores, diverged |
| 14 | Retry policies | **MISSING** | No retry budget. `tasks.attempts` column exists, unused |
| 15 | Failure classification | **MISSING** | No taxonomy in code |
| 16 | Automatic remediation loops | **MISSING** | Remediation tasks T015–T022 were written but never executed |
| 17 | Test enforcement | **PARTIALLY** | CI has 10 gates; no per-task enforcement |
| 18 | Evidence collection | **INADEQUATE** | `evidence` table 0 rows; evidence is prose |
| 19 | Artifact collection | **PARTIALLY** | Files land on disk, unregistered |
| 20 | Execution tracing | **MISSING** | No trace exists |
| 21 | Cost / token monitoring | **MISSING** | >1M subagent tokens spent, **zero recorded** |
| 22 | Timeout management | **MISSING** | One agent ran 19 minutes with no budget |
| 23 | Dead-agent detection | **MISSING** | Detected by notification, not by the OS |
| 24 | Stuck-task detection | **MISSING** | — |
| 25 | Agent handoffs | **MISSING** | `handoffs` table: **0 rows** despite a documented handoff protocol |
| 26 | Human approval gates | **PARTIALLY** | Gates exist in SOP; not enforced at execution |
| 27 | Veto enforcement | **IMPLEMENTED** | Verified live: CTO denied veto on `security_architecture` |
| 28 | Security controls | **PARTIALLY** | `secret_scan.sh`, GateGuard, deny-list — not execution-bound |
| 29 | Audit logs | **PARTIALLY** | 157 rows, but only of `companydb.py` calls, not agent work |
| 30 | Reproducibility | **MISSING** | No execution can be replayed |
| 31 | Multi-agent coordination | **INADEQUATE** | **`SendMessage` disabled** — a correction could not be injected into 4 running agents |
| 32 | Independent verification | **INADEQUATE** | **RISK-011: rule 3 DEGRADED all run.** The orchestrator could not dispatch (nested `Task` disabled), so owner = reviewer |
| 33 | Completion verification | **PARTIALLY** | Enforced in `companydb.py task update` — **which nothing calls** |
| 34 | Rollback | **MISSING** | — |
| 35 | Release integration | **PARTIALLY** | `releases` table + gates exist, unexercised |

```
IMPLEMENTED  3   ·  PARTIALLY 11  ·  INADEQUATE 5  ·  DUPLICATED 1  ·  MISSING 15
```

---
# 4. THE FAILURES THAT PROVE IT — observed, not theorised
1. **Nested dispatch is disabled.** The orchestrator subagent could not spawn anyone; it ran 6 phases
   as a single vessel. **Rule 3 (independent review) was degraded for the entire mission (RISK-011).**
   Flat dispatch from the top level works; one level down it does not.
2. **`SendMessage` disabled.** A material correction (the withdrawn SATpro inference) could not reach
   four agents already running. They worked from stale premises by design, not by accident.
3. **Rate limits killed 3 of 4 agents mid-write.** No backpressure, no queue, no checkpoint. Their
   artifacts survived by luck.
4. **Agents had no Bash**, so `company.py task-update` was never called — several said so explicitly:
   *"no task ID was given and no Bash."* Task state was never recorded.
5. **RISK-ID collisions.** Two agents allocated `RISK-007/008/009` concurrently. `COUNT(*)+1` is not
   a safe ID allocator under parallelism.
6. **Tavily's keyless cap exhausted mid-audit**, unnoticed until the agent reported it.

**Every one of these is a harness defect, not a model defect.**

---
# 5. WHAT MUST NOT CHANGE
`company.py` remains the SOP authority · `companydb.py` remains the governance authority ·
the orchestrator agent remains the decomposition authority · **D-1** (no new `.claude/agents/`) ·
**D-2** (one database) · stdlib-only · the CISO veto · founder-required domains.

**The harness executes decisions. It never makes them.**
