---
artifact: harness-architecture
role: principal-architect
phase: harness-design
status: complete
confidence: HIGH
retrieved: 2026-09-09
---
# The execution harness — decision, architecture, position

## DECISION: build thin internal. No external framework adopted.

### Phase 3 — decision matrix (condensed; full landscape in `RESEARCH-LANDSCAPE.md`)

| Candidate | Layer | Second orchestrator? | Deps | Verdict |
|---|---|---|---|---|
| **Claude Code native + hooks + `scripts/harness.py`** | execution | **No** | **0** | **SELECTED** |
| Prefect · Dagster · Inngest | orchestration | **Yes — self-described** | heavy | Disqualified (directive PHASE 3) |
| LangGraph · CrewAI · AutoGen/AG2 · OpenAI Agents SDK · Swarm | agent loop | **Yes** — they own the loop | heavy | Disqualified: would replace Claude Code |
| Temporal · Restate · DBOS | durable execution | partly | **server required** | Disqualified: no server, and see below |
| E2B · Daytona · Container Use | sandbox | No | credentials / Docker | Disqualified: Docker blocked (no Homebrew), no credentials |
| Langfuse · Braintrust · Weave | observability | No | credentials | Deferred — no product to observe yet |
| OpenTelemetry | observability | No | moderate | **Deferred**, viable later |

**Two measured facts that decided it:**
1. **Every one of 18 Python candidates requires Python ≥3.10.** The project is **3.9.6**. Including
   Anthropic's own `claude-agent-sdk`. Adding a library here means adding a *runtime*.
2. **Durable-execution engines buy deterministic replay. An LLM turn is not deterministic**, and its
   side effects are files already on disk. **The guarantee cannot be used.** The durable units in
   this system — the Claude Code session and the git artifact — are already durable.

### The constraint that shaped the design
**`claude` is NOT on PATH in this environment** (verified: `which claude` → not found; PATH contains
plugin bins only; this is the desktop app's agent mode, not a standalone CLI).

**Therefore the harness does NOT spawn.** The research proposed `harness.py` invoking `claude -p`;
that is **not implementable here** and was rejected on measurement rather than taste.

> **Spawning stays with Claude Code's native `Task` tool. The harness wraps, records, permissions,
> checkpoints and verifies it. It is a ledger and an enforcement layer, not a runtime.**

That is also the *safer* architecture: it cannot become a second orchestrator, because it cannot
start anything.

---
## Phase 4 — position in the stack
```
FOUNDER                    authority, founder-required domains
EXECUTIVE COUNCIL          decisions within domain, vetoes
COMPANY OS                 company.py (SOP/phases/gates) · companydb.py (authority/decisions)
MASTER ORCHESTRATOR        decomposition, dependency graph, dispatch
─────────────────────────────────────────────────────────────────────────
EXECUTION HARNESS          scripts/harness.py + Claude Code hooks   ← THIS LAYER
  ledger · permissioning · checkpointing · failure classification ·
  bounded retry · tool-honesty · evidence verification · completion refusal
─────────────────────────────────────────────────────────────────────────
CLAUDE CODE / AGENTS       Task tool, subagents, worktrees
TOOLS / MCP                bash, git, browser, Tavily, GitHub
EVIDENCE                   files on disk, sha256-verified into execution_evidence
COMPANY STATE              company.db - ONE database (D-2)
```

**The harness never decides.** Authority stays in `companydb.py`. Ask it "may X do Y?" — it answers.
The harness only refuses to let an answer go unrecorded.

---
## What was implemented
`scripts/harness.py` — 303 lines, stdlib only, Python 3.9 compatible.

| Command | Enforces |
|---|---|
| `migrate` | Versioned, **idempotent** migrations via `schema_version`. Re-runnable |
| `submit / start` | Execution lifecycle, 10 states, **DB CHECK constraint** on status |
| `checkpoint` | Captures state + **real git HEAD**, monotonic seq |
| `evidence` | **A path is verified against the filesystem and sha256'd.** A nonexistent path is REFUSED |
| `complete` | **REFUSES without verified evidence** (rule 15). **REFUSES self-review** (rule 3) |
| `fail` | 11-class taxonomy, **bounded retry budget**, SECURITY/HUMAN_REQUIRED block immediately (rule 11) |
| `tool` / `honesty` | Records actual tool calls; **refutes an unsupported "I used X" claim** with exit 2 |
| `status` / `verify` | Ledger view; integrity check incl. "SUCCEEDED without evidence" detection |

### New tables (7) — additive only, nothing altered
`executions · execution_events · tool_calls · checkpoints · execution_evidence ·
execution_failures · id_sequences`

`id_sequences` fixes an **observed** defect: two agents concurrently allocated `RISK-007/008/009`
because `COUNT(*)+1` is not safe under parallelism.

---
## Deliberately NOT changed
- `company.py`, `companydb.py`, the orchestrator, role packs, cognitive profiles, gates, the CISO
  veto, founder-required domains
- **No `.claude/agents/` file created** (D-1 intact — still 19)
- **No second database** (D-2 intact — one file, 54 → 61 tables, all additive)
- **No hooks installed yet.** Installing blocking `PreToolUse` hooks is a governance change under
  **rule 14** and needs founder authorisation. ECC's GateGuard already occupies `PreToolUse` with 8
  hooks; project hooks compose alongside plugin hooks, so there is no collision — but the decision
  is the founder's, not mine. **See `INTEGRATION.md` for the proposed hook and its exact blocking
  semantics.**

---
## Known gaps — stated, not hidden
1. **Hooks not installed** → tool governance is *recordable* but not yet *preventive*. Rule 14.
2. **The two-task-store divergence (D-2 violation) is NOT fixed.** `tasks.json` holds 22 tasks;
   `companydb.tasks` holds 0. Unifying them changes the orchestrator's write path and is a
   governance-adjacent change. **Recommended as the next work, escalated not assumed.**
3. **No spawn integration** — agents must call `harness.py` themselves, and several agents this run
   had no Bash tool. Until hooks exist, adoption is by convention, which is weak.
4. **OpenTelemetry deferred.**
5. **Not independently reviewed** — RISK-011 applies to this artifact too.
