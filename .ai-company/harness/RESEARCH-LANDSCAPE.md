---
artifact: harness-research-landscape
role: cro-research
name: Amara Diallo
phase: research (Phase 2 — founder directive: execution harness selection)
mission: EXECUTION HARNESS beneath the existing master orchestrator
status: complete
confidence: MEDIUM-HIGH on the native baseline (primary vendor docs, retrieved today) · MEDIUM on external candidates (registry metadata is FACT; behavioural claims are INFERENCE) · LOW on anything marked UNKNOWN
retrieved: 2026-09-09
governance_note: |
  Rule 3 (independent review) NOT yet satisfied for this artifact. It must be
  reviewed by an owner-independent reviewer (suggest `principal-architect` or
  `cto`, NOT the author) before it informs a gate.
provider_provenance: |
  USED   — Tavily CLI 0.1.8 (`tvly search`), keyless tier, WORKED (not exhausted)
  USED   — WebFetch against code.claude.com (primary vendor documentation)
  USED   — Bash + curl/node against pypi.org/pypi/*/json, registry.npmjs.org,
           api.github.com (public registry APIs — primary metadata)
  NOT USED — WebSearch (Tavily + direct primary fetch was sufficient)
  NOT USED — Exa (declared unavailable for this task by the directive)
  NOT USED — Brave (DEAD — HTTP 422 SUBSCRIPTION_TOKEN_INVALID, BLOCKER 3). No
           Brave result is cited anywhere in this document.
  LIMITATION — the `claude` binary is NOT on PATH in this execution sandbox
           (`which claude` → not found). Every Claude Code capability below is
           established from vendor documentation, NOT from local execution.
           Nothing here has been empirically exercised on this machine.
---

# EXECUTION HARNESS — RESEARCH LANDSCAPE

**The question:** what layer sits *underneath* `company.py` (SOP state machine) and
`companydb.py` (54 tables: authority, task graph, decisions, memory, recovery) and *above* the
raw Claude Code agent runtime — turning a decomposed, owned, criteria-bearing task into a
reliably executed, evidenced unit of work?

**The answer, stated up front:** almost everything the founder listed is a layer *above* the
company orchestrator, not below it, and is therefore disqualified by constraint 1. The layer the
company actually lacks is thin. Claude Code already ships most of it.

---

## 0. HOW CLAIMS ARE LABELLED

`FACT` = retrieved from a primary source with URL + date · `INFERENCE` = my reasoning over facts ·
`HYPOTHESIS` = plausible, untested · `ASSUMPTION` = taken on trust, unverified · `UNKNOWN` = could
not establish.

---

# 1. THE BASELINE — WHAT CLAUDE CODE AND THE AGENT SDK GIVE US FOR FREE

This is the most important section. The directive says: *if native capabilities plus a thin
internal harness beat an external framework, choose that.* Here is what "native" actually means as
of today.

**Runtime under test:** `@anthropic-ai/claude-code` **v2.1.266**, published **2026-09-08**,
**zero npm dependencies**. `FACT` — registry.npmjs.org/@anthropic-ai/claude-code, retrieved
2026-09-09. A zero-dependency, daily-released runtime is itself an argument against bolting a
57-dependency framework onto it.

## 1.1 Execution primitives

| Capability | What it gives the harness | Evidence |
|---|---|---|
| **Subagents (Agent tool)** | Isolated context window per worker; result returned to caller; parent never sees intermediate tool calls | `FACT` — https://code.claude.com/docs/en/sub-agents (2026-09-09) |
| **Concurrency limit** | **20 concurrent subagents by default**, tunable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`; error `Concurrent subagent limit reached` when exceeded | `FACT` — sub-agents (2026-09-09) |
| **Nesting depth** | **3 layers deep by default**, tunable via `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`; at the limit the `Agent` tool is withheld and the subagent does the work itself | `FACT` — sub-agents (2026-09-09) |
| **Per-agent tool restriction** | `tools:` allowlist, `disallowedTools:` denylist, `Agent(worker, researcher)` spawn restriction, `mcp__github` server-level denial | `FACT` — sub-agents (2026-09-09) |
| **Per-agent permission mode** | `permissionMode: default\|acceptEdits\|auto\|dontAsk\|bypassPermissions\|plan` in frontmatter | `FACT` — sub-agents (2026-09-09) |
| **Per-agent turn cap** | `maxTurns` — caps agentic turns, and the subagent **can be resumed if it hits the limit** | `FACT` — sub-agents + tools-reference (2026-09-09) |
| **Per-agent model + effort** | `model: sonnet\|opus\|haiku\|inherit`, `effort: low..max`; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` pins all | `FACT` — sub-agents (2026-09-09) |
| **Per-agent persistent memory** | `memory: user\|project\|local` | `FACT` — sub-agents (2026-09-09) |
| **Background execution** | `background: true` in frontmatter; `Bash(run_in_background: true)`; `/tasks` lists and stops them | `FACT` — sub-agents + tools-reference (2026-09-09) |
| **Prompt-injection defence** | Claude Code **scans subagent output before the parent reads it**, escaping text that imitates harness tags and prepending `[harness: subagent output matched...]` | `FACT` — sub-agents (2026-09-09) |

### The finding that matters most for D-1

**`--agents <json>` is a CLI flag, and `agents` is an Agent SDK option.** Subagent scope is
documented as, in priority order: managed settings → **`--agents` CLI flag (current session)** →
`.claude/agents/` (project) → `~/.claude/agents/` (user) → plugin `agents/`.
`FACT` — https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/headless
("Custom agents → `--agents <json>`"), both retrieved 2026-09-09.

`INFERENCE (HIGH confidence)`: **this dissolves the tension D-1 was created to manage.** D-1 exists
because 121 role packs written as `.claude/agents/*.md` would permanently consume orchestrator
context. A harness that *projects the two-to-five role packs relevant to a task into `--agents`
JSON at dispatch time* gets full role fidelity at **zero standing context cost**, and does not add
a single file to `.claude/agents/`. This is a native mechanism the company has never used and is
the highest-value single finding in this research.

`ASSUMPTION` — that a role pack's 40–80 lines survive projection into a subagent system prompt
without losing behavioural fidelity. **Untested. Must be piloted before it is relied on.**

## 1.2 Control and enforcement primitives — hooks

Claude Code documents **31 hook events**. `FACT` — https://code.claude.com/docs/en/hooks
(2026-09-09). The ones that are load-bearing for this company's governance:

| Hook | Can block? | Why this company cares |
|---|---|---|
| `PreToolUse` | **YES** (exit 2, or `permissionDecision: "deny"`) | Authority enforcement at the point of action — call `companydb.py can <role> decide <domain>` and deny on exit 2 |
| `PreToolUse` `updatedInput` | rewrite | Can *modify tool input before execution* — e.g. force an artifact path |
| `PostToolUse` / `PostToolUseFailure` | no (stderr shown to Claude) | Evidence capture: every Write/Edit recorded to SQLite as an artifact |
| `PostToolBatch` | **YES** (stops the agentic loop) | A whole parallel batch can be halted on a gate failure |
| `SubagentStart` / `SubagentStop` | Stop: **YES** | Where "did this agent write its artifact?" gets checked — the fix for prose-instead-of-artifact |
| `Stop` / `StopFailure` | Stop: **YES** | Refuse to end the turn until the artifact exists |
| `TaskCreated` / `TaskCompleted` | **YES** (`rollback: true`) | Refuse a completion with no evidence — the native mirror of the company's no-fake-completion rule |
| `TeammateIdle` | **YES** | Keep an agent working instead of going idle |
| `SessionStart` | no, but injects `additionalContext` | Auto-inject `company.py resume` output into every session — makes rule "read CURRENT_STATE.md first" structural instead of hoped-for |
| `PreCompact` / `PostCompact` | no | Detect context loss events |
| `WorktreeCreate` / `WorktreeRemove` | Create: **YES** | Replace git worktree logic entirely (e.g. for non-git VCS) |
| `ConfigChange` | **YES** (except `policy_settings`) | Detect tampering with settings mid-session — relevant to rule 14 |
| `PermissionRequest` / `PermissionDenied` | no | Audit trail of every escalation |

Hook handler types: **`command`, `http`, `mcp_tool`, `prompt`, `agent`**. `FACT` — hooks
(2026-09-09). `command` hooks receive the full event as JSON on stdin (`session_id`, `cwd`,
`permission_mode`, `tool_name`, `tool_input`, `tool_use_id`, `agent_id`, `agent_type`) and support
`async`/`asyncRewake`, `timeout` (default 600s), and an `if:` permission-rule filter such as
`"Bash(git *)"`.

`INFERENCE (HIGH confidence)`: **a `command` hook is a Python 3.9 stdlib script reading JSON from
stdin and writing JSON to stdout.** That is exactly the shape of every script already in
`scripts/`. The company's entire governance layer can be wired into the agent loop with zero new
dependencies and zero new runtime.

## 1.3 Durability primitives

| Capability | Reality | Evidence |
|---|---|---|
| `--resume <session_id>` / `--continue` | Works in `-p` non-interactive mode and in the Agent SDK. Session IDs are **findable by ID across any project on the machine** (v2.1.223+) | `FACT` — headless (2026-09-09) |
| Checkpointing (`/rewind`) | Snapshots for the **100 most recent checkpoints** per session; survives resume; retention swept after ~30 days (`cleanupPeriodDays`) | `FACT` — https://code.claude.com/docs/en/checkpointing (2026-09-09) |
| **Checkpointing limits** | **Does NOT track files modified by bash commands.** **Does NOT restore subagent edits** (except a foreground forked skill). Does not track external changes. Skips symlinks/hard links. Explicitly "not a replacement for version control" | `FACT` — checkpointing (2026-09-09) |
| SIGTERM behaviour | Exit code **143**; runs `SessionEnd` hooks; kills the Bash process tree; **on resume, Claude Code continues the turn SIGTERM left unfinished** | `FACT` — headless (2026-09-09) |
| API retry | Built in. `system/api_retry` events carry `attempt`, `max_retries`, `retry_delay_ms`, `error_status`, and an `error` category (`rate_limit`, `overloaded`, `server_error`, …) | `FACT` — headless (2026-09-09) |
| Bash timeouts | Default 2 min (`BASH_DEFAULT_TIMEOUT_MS`), ceiling 10 min (`BASH_MAX_TIMEOUT_MS`); auto-background on overrun | `FACT` — tools-reference (2026-09-09) |
| Background wait ceiling | `claude -p` stays open until a background subagent/workflow completes, capped at **10 minutes idle** (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`, `0` = no cap) | `FACT` — headless (2026-09-09) |

`INFERENCE (HIGH)`: **checkpointing is not a durability mechanism for this company** and must not
be sold as one. Its two documented exclusions — bash-command file changes and subagent edits — are
precisely how this company's agents write artifacts. Git plus `company.py`'s
write-to-disk-on-every-transition is the real durability story, and it already exists.

## 1.4 Isolation primitives

- `claude --worktree <name>` / `-w`: isolated worktree under `.claude/worktrees/<name>/` on branch
  `worktree-<name>`. `FACT` — https://code.claude.com/docs/en/worktrees (2026-09-09).
- `isolation: worktree` in subagent frontmatter makes isolation **permanent for that role**.
  `FACT` — worktrees (2026-09-09).
- **Enforcement is real, not advisory.** Inside a worktree Claude Code blocks: edits targeting the
  main checkout; Bash/PowerShell/Monitor commands whose cwd resolves into the main checkout; git
  redirects via `git -C`, `--git-dir`, `GIT_DIR`, `GIT_WORK_TREE`, or a `cd`; and commands whose
  shape it cannot verify. The last check **cannot be turned off**. `FACT` — worktrees (2026-09-09).
- `.worktreeinclude` copies gitignored files (e.g. `.env`) into every new worktree. `FACT`.
- Automatic sweep removes agent/background worktrees older than `cleanupPeriodDays`, but **leaves
  any worktree that still holds work** (changed/untracked files, unpushed commits). `FACT`.
- **Trap:** `${CLAUDE_PROJECT_DIR}` in hook commands **stays at the session's launch root** and
  does not follow the worktree; hooks must read `cwd` from the input JSON instead. `FACT` —
  worktrees (2026-09-09). *This session is itself running in `.claude/worktrees/review-project-architecture-87dcc7/`, so this is not academic.*

## 1.5 Programmatic entry points

`claude -p` (non-interactive) with:
`--output-format text|json|stream-json` · `--json-schema <schema>` (structured output lands in
`structured_output`) · `--resume <id>` / `--continue` · `--allowedTools` / `--disallowedTools` ·
`--permission-mode auto|dontAsk|acceptEdits|plan` · `--permission-prompts none` (v2.1.259+, for
unattended runs) · `--agents <json>` · `--settings <file-or-json>` · `--mcp-config` ·
`--append-system-prompt(-file)` · `--bare` (skips discovery of hooks/skills/agents/plugins/MCP —
*"the recommended mode for scripted and SDK calls, and will become the default for `-p`"*) ·
`--forward-subagent-text`. Exit 0 on success, non-zero on failure. `--output-format json` returns
`total_cost_usd` and a per-model cost breakdown. `FACT` — https://code.claude.com/docs/en/headless
and /cli-reference (2026-09-09).

## 1.6 The Claude Agent SDK

- Two packages: **`@anthropic-ai/claude-agent-sdk` v0.3.266** (npm, modified 2026-09-08) and
  **`claude-agent-sdk` v0.2.152** (PyPI, uploaded 2026-09-02). `FACT` — registry.npmjs.org and
  pypi.org, retrieved 2026-09-09.
- Feature parity with Claude Code: built-in tools, hooks, subagents, MCP, permissions, sessions
  (resume/fork), skills/commands/memory loaded from `.claude/`, plugins. There is a documented
  *Migration guide: migrate from the Claude Code SDK packages to the Agent SDK* — confirming the
  rename. `FACT` — https://code.claude.com/docs/en/agent-sdk/overview (2026-09-09).
- **"To drive the same agent loop from another language, run the CLI as a subprocess with the `-p`
  flag and `--output-format json`."** `FACT` — agent-sdk/overview (2026-09-09).

### 🔴 The Python Agent SDK is incompatible with this project's stated runtime

**`claude-agent-sdk` requires Python `>=3.10`.** The project runs **Python 3.9.6** (verified
locally this session: `python3 --version` → `Python 3.9.6`). Its hard dependencies are
`anyio>=4.0.0`, `jsonschema>=4.20.0`, `mcp>=1.23.0,<3.0.0`, `sniffio>=1.0.0`. `FACT` —
pypi.org/pypi/claude-agent-sdk/json, retrieved 2026-09-09.

`INFERENCE (HIGH)`: adopting the **Python** Agent SDK means a second Python runtime **and**
breaking the stdlib-only rule. The documented alternative — *run the CLI as a subprocess with `-p`
and `--output-format json`* — needs only `subprocess` and `json`, both stdlib, and works on 3.9.
**That is the harness's execution primitive.**

## 1.7 Native capabilities that look attractive and are traps

**Agent teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) give a shared task list with
dependencies, file-locked task claiming, per-agent mailboxes at
`~/.claude/teams/{team}/inboxes/{agent}.json`, and a task list at `~/.claude/tasks/{team}/`.
`FACT` — https://code.claude.com/docs/en/agent-teams (2026-09-09).

**Disqualify as the company's task store — three independent reasons:**
1. `INFERENCE (HIGH)` — **it is a second task graph with dependency resolution, stored outside
   `company.db`. That is a direct D-2 violation.** Two sources of truth silently diverge.
2. `FACT` — the docs' own Limitations section: *"Agent teams are experimental and disabled by
   default"*; *"`/resume` and `/rewind` do not restore in-process teammates"*; *"teammates
   sometimes fail to mark tasks as completed, which blocks dependent tasks"*.
3. `FACT` — *"In non-interactive mode with the `-p` flag, including Agent SDK sessions, Claude
   doesn't spawn teammates."* A headless harness cannot use them at all.

**Verdict:** teams' *hooks* (`TaskCreated`, `TaskCompleted`, `TeammateIdle`) are worth adopting.
Teams' *state* is not.

**Task tools availability caveat.** The tools reference states the Task tools are *"NOT available
by default on: Opus 4.8, Sonnet 5, Fable 5, Mythos 5+"*, opt-in via
`CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. `FACT` — tools-reference (2026-09-09). Whether **Opus 5** (the
model running this session) is in or out of that set is **UNKNOWN** — it is not named in the list.
A harness must not depend on `TaskCreate`/`TaskUpdate` being present.

**Dynamic Workflows / the `Workflow` tool.** Claude Code can write and run task-specific
JavaScript "harnesses" that spawn and coordinate subagents, with named patterns
(classify-and-act, fan-out-and-synthesize, adversarial verification, generate-and-filter,
tournament, loop-until-done); workflows save to `~/.claude/workflows` or ship inside skills;
interrupted sessions *"pick up where they left off."* `FACT` —
https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code (published
~2026-06-02, retrieved 2026-09-09) and tools-reference (2026-09-09).

`INFERENCE (MEDIUM)`: **Anthropic's own answer to "what harness should sit under an orchestrator"
is a thin, task-specific, locally-written script — not an external framework.** The named patterns
map almost one-to-one onto SOP phases the company already runs (fan-out-and-synthesize = the six
research roles; adversarial verification = `adversarial`; tournament = `debate`). That the
JavaScript runtime is not Python is a real friction and the reason I do not recommend `Workflow`
as the harness itself — but it is strong convergent evidence for the *shape* of the recommendation.

---

# 2. CANDIDATE TABLE

`ORCH?` = does it want to be the top-level orchestrator (constraint 1)? · `Deps` = hard runtime
dependencies from the package registry, retrieved 2026-09-09 · all versions/dates `FACT` from
pypi.org / registry.npmjs.org / api.github.com on 2026-09-09.

| Candidate | Version · last release | Layer it actually occupies | ORCH? | Deps | Server needed? | Maturity / maintenance | Claude Code fit | **Disqualified?** |
|---|---|---|---|---|---|---|---|---|
| **Claude Code native + thin internal module** | CC v2.1.266 · 2026-09-08 | Agent runtime + enforcement hooks | **No** | **0** | No | Production; released daily | Native | **NO — SURVIVES** |
| **Claude Agent SDK (CLI subprocess, `-p`)** | CLI, stdlib `subprocess` | Programmatic invocation | No | **0** | No | Production | Native | **NO — SURVIVES** |
| **Claude Agent SDK (Python package)** | 0.2.152 · 2026-09-02 | Programmatic invocation | No | 4 | No | Production | Native | **YES — requires Python ≥3.10; project is 3.9.6** |
| **Claude Agent SDK (TypeScript)** | 0.3.266 · 2026-09-08 | Programmatic invocation | No | — | No | Production | Native | Not disqualified, but adds a second language for zero unique capability |
| **git worktree (native `--worktree`)** | git 2.50.1 (local) | Filesystem isolation | No | **0** | No | Production; enforcement is in-runtime | Native | **NO — SURVIVES** |
| **OpenTelemetry SDK** | opentelemetry-sdk 1.44.0 · 2026-07-16 | Observability | No | 3 | Collector optional | Production, CNCF | Neutral | **NO — SURVIVES (narrow, optional)** |
| **DBOS Transact (Python)** | dbos 2.31.1 · 2026-09-08 · 1.5k★ | Durable execution *library* | No | 6 | **Postgres** (SQLite support claimed, unverified) | Active, small | Would wrap the subprocess, not the agent | **NO — survives on constraints, fails on value (§3.4)** |
| **Temporal** | temporalio 1.32.0 · 2026-08-24 · 22.9k★ | Durable execution *platform* | Borderline — it owns the workflow | 5 | **YES — dedicated server + Cassandra/MySQL/Postgres** | Very mature, very active | Wraps the process | **YES — server requirement violates "local-only, no-server"** |
| **Restate** | restate-sdk 1.0.5 · 2026-09-02 · 4.4k★ | Durable execution platform | Borderline | **0** | **YES — `restate-server` binary** | Active, younger | Wraps the process | **YES — server requirement** |
| **Inngest** | inngest (py) 0.5.19 · 2026-06-23 · 5.8k★ | *"The leading workflow orchestration platform"* (self-description) | **YES** | 4 | **YES — dev server / cloud** | Active | Above, not below | **YES — orchestrator + server** |
| **Prefect** | 3.8.5 · 2026-09-03 · 23.8k★ | *"Workflow orchestration framework"* (self-description) | **YES** | **57** | Server/API for most value | Very mature | Above, not below | **YES — orchestrator; 57 hard deps** |
| **Dagster** | 1.13.21 · 2026-09-03 · 16.1k★ | *"An orchestration platform"* (self-description) | **YES** | **32** | Daemon + webserver | Very mature | Above, not below | **YES — orchestrator; data-asset model is the wrong domain** |
| **LangGraph** | 1.2.11 · 2026-08-11 · 41.3k★ | Stateful agent graph runtime | **YES** — it owns the graph and the state | 6 | No (SQLite checkpointer exists) | Very active | **Replaces the agent runtime** | **YES — orchestrator AND violates constraint 4** |
| **AutoGen** | autogen-agentchat 0.7.5 · **2025-09-30**; repo pushed **2026-04-15** · 60.9k★ | Multi-agent conversation framework | **YES** | 1 | No | **~11 months since PyPI release, ~5 months since repo push** | Replaces runtime | **YES — orchestrator + maintenance risk** |
| **AG2 (AutoGen fork)** | 1.0.4 · 2026-09-07 · 4.9k★ | *"The Open-Source AgentOS"* | **YES** | 5 | No | Active | Replaces runtime | **YES — orchestrator** |
| **CrewAI** | 1.15.20 · 2026-09-04 · 58.3k★ | *"orchestrating role-playing, autonomous AI agents"* | **YES — and it duplicates the org model itself** | **31** | No | Very active | Replaces runtime | **YES — this is a competing AI-company abstraction** |
| **OpenAI Swarm** | repo pushed 2026-04-15 · 22.0k★ · *"Educational framework"* (own description) | Multi-agent orchestration | **YES** | — | No | Superseded by Agents SDK | Wrong vendor runtime | **YES — orchestrator + explicitly educational** |
| **OpenAI Agents SDK** | openai-agents 0.22.1 · 2026-09-08 · 29.3k★ | Multi-agent workflow framework | **YES** | 7 | No | Active | **Wrong agent runtime entirely** | **YES — orchestrator + violates constraint 4** |
| **E2B** | e2b 2.48.0 · 2026-09-09 · 13.7k★ | Cloud sandbox | No | 12 | **YES — cloud, API key** | Active | Sits beside | **YES — needs a credential + network; no code to sandbox yet** |
| **Daytona** | daytona-sdk 0.211.2 (**deprecated alias**) · 71.8k★ · repo pushed 2026-07-24 | Cloud sandbox | No | 24 | **YES — cloud** | Active but the SDK alias is deprecated | Sits beside | **YES — same as E2B** |
| **microsandbox** | superradcompany/microsandbox · 8.1k★ · pushed 2026-09-09 | Local microVM sandbox | No | — | Local daemon | Active | Sits beside | **YES for now — no application code exists to sandbox (§2 CURRENT_STATE)** |
| **Langfuse** | py 4.15.1 · 2026-08-28 · 34.4k★ | LLM observability platform | No | 9 | **YES — self-host or cloud** | Very active | Sits beside | **YES — server + a product to instrument does not exist** |
| **Braintrust** | 0.37.0 · 2026-09-03 | Eval/observability platform | No | 10 | **YES — SaaS** | Active | Sits beside | **YES — duplicates `intelligence.py` evals; SaaS** |
| **W&B Weave** | 0.53.8 · 2026-09-03 · 1.1k★ | Tracing/eval toolkit | No | **16** | **YES — W&B account** | Active | Sits beside | **YES — SaaS + credential** |
| **Container Use (Dagger)** | dagger/container-use · 4.0k★ · pushed 2026-09-07 | Container + worktree isolation for coding agents | No | — | **Docker** | Active | Overlaps native worktrees | **YES — Docker is blocked (Homebrew ABSENT, CLAUDE.md §10)** |
| **Conductor** | — | macOS GUI for parallel Claude Code worktrees | No | — | No | `UNKNOWN` — not verified this session | GUI, not a harness | **YES — a UI, not a programmable layer** |

## 2.1 The single constraint that eliminates most of the field at once

**Every one of the 18 Python packages checked requires Python ≥ 3.10.** temporalio, prefect,
dagster, langgraph, autogen-agentchat, ag2, crewai, openai-agents, restate-sdk, inngest, dbos, e2b,
daytona-sdk, langfuse, braintrust, weave, opentelemetry-sdk, claude-agent-sdk — **all of them.**
`FACT` — `requires_python` field from pypi.org/pypi/*/json, retrieved 2026-09-09.

`INFERENCE (HIGH)`: this is not a coincidence, it is the floor of the modern Python ecosystem.
Adopting *any* Python framework here means standing up a second interpreter. `uv 0.12.10` is
installed (CLAUDE.md §9), so this is **surmountable, not fatal** — and I will not overstate it as a
blocker. But it converts "add a library" into "add a runtime, a lockfile, a virtualenv and a CI
step," and it must be priced that way.

---

# 3. THE CANDIDATES THAT SURVIVE, ASSESSED IN DEPTH

## 3.1 A thin internal harness — `scripts/harness.py` — **RECOMMENDED**

**Layer:** between `company.py task ready` and `claude -p`. It does not decide *what* to do
(orchestrator) or *who* does it (`workforce.py`) or *whether it is allowed* (`companydb.py`). It
decides **how a decided, assigned, authorised task actually gets executed, retried, timed out,
evidenced and recorded.**

**What it would be, concretely:** ~300–500 lines of Python 3.9 stdlib (`subprocess`, `json`,
`sqlite3`, `os`, `signal`, `time`). For each ready task it would:
1. read the task + owner + acceptance criteria from `company.db` (existing tables, no new store);
2. project the owner's role pack — and the *independent reviewer's* — into `--agents` JSON;
3. spawn `claude -p --bare --output-format json --json-schema <artifact-contract> --agents <json>
   --permission-mode dontAsk --permission-prompts none --allowedTools <per-role>`;
4. capture `session_id`, `total_cost_usd`, `structured_output`, exit code;
5. on failure, classify from the `error` category already emitted in `system/api_retry`
   (`rate_limit` → back off; `overloaded` → back off; `invalid_request` → do **not** retry, that is
   rule 11's "changed approach or escalate");
6. **resume rather than restart** via `--resume <session_id>` — the documented behaviour that a
   SIGTERM-interrupted turn continues on resume;
7. verify the artifact exists on disk, then call `companydb.py task update ... evidence=<path>`,
   which already refuses `done` without it.

**Why it is the right size.** Every guarantee the founder asked about is already provided by
something the company owns or Claude Code ships:

| Guarantee | Already provided by | Gap the harness fills |
|---|---|---|
| Checkpoint | `company.py` writes every transition to disk immediately (its own docstring); git | Nothing — it exists |
| Resume | `company.py resume`, `companydb.py recover`, `claude --resume <id>` | Wiring the two together |
| Retry | Claude Code's built-in API retry with typed error categories | Task-level attempt counting — **already in `company.py`, which warns at two attempts** |
| Timeout | `BASH_MAX_TIMEOUT_MS`, `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`, `maxTurns` | Setting them per role |
| Failure recovery | `companydb.py incident`, `.ai-company/incidents/` | Auto-opening the incident instead of hoping an agent does |
| Idempotency | Artifact-on-disk + evidence-required `done` | Deterministic artifact paths |

**Cost:** zero dependencies, zero new runtime, one file, reviewable by one person.
**Risk:** `HYPOTHESIS` — a hand-rolled harness accretes into a second orchestrator. Mitigation:
give it a written prohibition — *the harness may not decide what work exists, who does it, or
whether a gate passes.* Put that in the module docstring where the next session will read it.

## 3.2 Claude Code hooks as the enforcement substrate — **RECOMMENDED, adopt with §3.1**

`INFERENCE (HIGH)`: this is where the company's biggest live wound gets closed.
**RISK-011** records that in the last session *"the subagent dispatch tool was disabled for the
whole session; the orchestrator produced every artifact by adopting role packs sequentially,"* so
governance rule 3 is DEGRADED for that run — and it was only caught because a diligent agent wrote
it down. A `SubagentStop` or `Stop` hook that exits 2 when `companydb.py` shows a task marked
complete with `owner == reviewer`, or with no artifact on disk, makes that failure **structurally
impossible rather than honestly reported.** That is a strictly stronger property, and it is
available today for the price of a shell script.

Four hooks I would install first, in this order:
1. `SessionStart` → inject `company.py resume` output as `additionalContext`. Makes rule "read
   CURRENT_STATE.md first" automatic.
2. `PreToolUse` on `Bash`/`Write`/`Edit` → `companydb.py can <role> ...`, deny on exit 2. Moves
   authority enforcement from "the agent chose to check" to "the runtime checked."
3. `SubagentStop` → refuse to finish without the artifact path the task demanded.
4. `PostToolUse` on `Write|Edit` → append to the evidence table in `company.db`.

**Caution — `ConfigChange` and rule 14.** Hooks are configuration. `CLAUDE.md` §11 forbids
modifying governance controls without founder approval. `INFERENCE`: installing governance hooks is
itself a governance change and **requires founder approval**, even though it strengthens the rules.
A `ConfigChange` hook that blocks unapproved edits to `.claude/settings.json` should ship in the
same change.

## 3.3 Native git worktrees — **RECOMMENDED, adopt as-is, build nothing**

Already referenced by the ORCHESTRATION-MANUAL (*"Use `EnterWorktree` when parallel streams touch
the same files"*) and already in use by this very session. The enforcement — blocked cross-checkout
edits, blocked git redirects, an un-disableable command-shape check — is stronger than anything a
harness could implement in Python, and it costs nothing. **The only work needed is the documented
`${CLAUDE_PROJECT_DIR}` trap: every hook script must read `cwd` from the hook's input JSON, not the
env var.** That is a one-line convention, and getting it wrong would silently run governance checks
against the wrong checkout.

## 3.4 DBOS Transact — the strongest external durable-execution case, and why I still decline it

DBOS is the only durable-execution candidate that is genuinely a *library* rather than a platform:
*"a library that runs directly inside your existing application code"* and *"requiring no
infrastructure except Postgres."* `FACT` — dbos.dev and github.com/dbos-inc/dbos-transact-py,
retrieved 2026-09-09. `dbos` v2.31.1, released 2026-09-08, 6 hard dependencies, 1,565 stars.

Two problems, one soft and one fatal.

**Soft:** the SQLite claim. A DBOS maintainer states on Hacker News that *"DBOS Python recently
added SQLite support."* That is a forum comment, not documentation. `LOW confidence` — **I did not
verify SQLite support against DBOS's own docs, and it should not be relied on without that check.**
The GitHub README still says *"requiring no infrastructure except Postgres."*

**Fatal — and it applies to Temporal and Restate equally.** `INFERENCE (HIGH confidence)`: durable
execution engines deliver exactly-once semantics by **deterministic replay** — re-executing a
workflow function from a log and expecting identical decisions, with non-deterministic effects
quarantined into recorded steps. **An LLM turn is non-deterministic and its side effects are files
on disk.** Wrapping `claude -p` in a `@Workflow` therefore checkpoints only the *shape* of the
call, not the reasoning; on replay the model may take a different path, and the artifacts it wrote
before the crash are already committed. The company would pay for a replay guarantee it cannot
use.

The durable unit here is not a Python function. It is **(a) the Claude Code session, whose
durability Anthropic already implements via transcripts and `--resume`, and (b) the artifact on
disk, whose durability git already implements.** Both are stronger for this workload than a replay
log, and both already exist. `HYPOTHESIS`: if the company ever runs a genuinely long-lived,
multi-day, multi-service process with real external side effects (payments, deploys, third-party
API mutations), this conclusion inverts. It does not have one, and per §2 of CURRENT_STATE it has
no application code at all.

**Temporal and Restate** additionally require a server process — `temporal server start-dev` is a
single binary with no external dependencies for *development*, but production persistence is
Cassandra/MySQL/PostgreSQL (`FACT` — docs.temporal.io self-hosted guide, retrieved 2026-09-09), and
Restate is *"a single self-contained binary"* you must run (`FACT` — docs.restate.dev, 2026-09-09).
For a **single-founder, local-only, no-server** project, a background daemon that must be running
for the company to work is a new class of failure — and it fails *silently*, which is the worst
kind for a system whose entire value proposition is refusing to fake completion.

## 3.5 OpenTelemetry — **CONDITIONALLY VIABLE, defer**

The only observability candidate that is a *specification with a vendor-neutral SDK* rather than a
platform requiring an account. `opentelemetry-sdk` 1.44.0, 2026-07-16, 3 hard deps, CNCF-governed.
`FACT` — pypi.org, 2026-09-09.

**Defer, for two reasons.** First, `--output-format json` already returns `total_cost_usd` and a
per-model cost breakdown per invocation (`FACT` — headless), and `company.db` already has 54
tables to put it in — the marginal information from OTel spans is small. Second, Python ≥3.10.
`UNKNOWN` — whether Claude Code natively exports OpenTelemetry telemetry (a monitoring page exists
in the docs; **I did not retrieve it this session**). If it does, the correct integration is
configuration, not a dependency. **Verify before deciding.**

---

# 4. RECOMMENDATION — BUILD THIN INTERNAL

**Recommendation: build a thin internal harness. Adopt no external framework.**
**Confidence: HIGH on rejecting the external frameworks. MEDIUM-HIGH on the internal design.**

The load-bearing reasoning, in order of strength:

1. **Most candidates are the wrong layer, not merely the wrong choice.** Prefect, Dagster,
   Inngest, LangGraph, CrewAI, AutoGen/AG2, OpenAI Agents SDK and Swarm all describe *themselves*
   as orchestration frameworks in their own package metadata. The directive says penalize anything
   that tries to become a second company orchestrator. These do not "try" — it is their purpose.
   CrewAI is the sharpest case: it is *"a framework for orchestrating role-playing, autonomous AI
   agents,"* which is a competing implementation of the thing this repository *is*. Adopting it
   would mean maintaining two org models.
2. **The agent-framework candidates also fail constraint 4.** LangGraph, CrewAI, AG2 and the
   OpenAI Agents SDK own the agent loop. Claude Code would become a tool they call, or be
   displaced. The company would lose hooks, permission rules, worktree enforcement, subagent output
   scanning and `--resume` — every native capability catalogued in §1.
3. **Durable execution is real engineering solving a problem this project does not have.** §3.4.
   Temporal and Restate need a server; DBOS needs Postgres (SQLite unverified); and all three buy
   deterministic replay, which does not apply to a non-deterministic model turn writing files.
4. **The dependency and runtime cost is concrete, not ideological.** Every Python candidate needs
   ≥3.10 against the project's 3.9.6. Prefect brings 57 hard dependencies; CrewAI 31; Dagster 32.
   Claude Code itself ships with **zero**. A 121-employee governance system whose credibility rests
   on `verify` passing should not acquire a 57-package transitive surface to gain retry logic it
   already has.
5. **The gap is genuinely small.** Walk the guarantees: checkpoint (exists), resume (exists,
   twice over), retry (exists in the runtime *and* in `company.py`'s attempt counter), timeout
   (exists as documented env vars), failure recovery (`companydb.py incident` exists),
   isolation (native worktrees, enforced in-runtime). What is missing is **the wiring**, plus one
   genuinely new capability: **runtime-projected role packs via `--agents`.**
6. **Anthropic's own harness guidance points the same way** — task-specific scripts written locally,
   not an adopted framework (§1.7).

## What I would build, in order

| # | Deliverable | Why first |
|---|---|---|
| 1 | `scripts/harness.py` — stdlib-only dispatcher: task → `--agents` projection → `claude -p --bare --output-format json --json-schema` → evidence → `task update` | The whole recommendation stands or falls on whether role packs survive `--agents` projection |
| 2 | **A pilot on one real task before anything else is built.** Dispatch one existing role pack via `--agents` and compare the artifact against the same role pack adopted in-session | This is the ASSUMPTION in §1.1. Do not build layer 3 on an unpiloted layer 1 |
| 3 | `SessionStart` hook injecting `company.py resume` | Cheapest, highest-compliance-value, cannot break anything |
| 4 | `SubagentStop` / `Stop` hook enforcing artifact-on-disk and owner ≠ reviewer | Closes RISK-011 structurally |
| 5 | `PreToolUse` hook calling `companydb.py can` | Authority moves from prose into the runtime |
| 6 | Adopt native worktrees as-is; document the `${CLAUDE_PROJECT_DIR}` vs `cwd` rule | Zero build cost, one silent-failure trap to avoid |

**Founder approval is required before step 3.** Hooks are governance configuration (rule 14).

## What would change my mind — stated in advance, so it can be checked

| Evidence | Would change the recommendation to |
|---|---|
| The `--agents` projection pilot (#2) shows role-pack fidelity collapses — agents behave generically | Reconsider `.claude/agents/` for a small elite subset, i.e. revisit **D-1**, with founder approval |
| The company acquires a long-lived process with real external side effects — payments, production deploys, third-party mutations spanning days | **DBOS** becomes worth its weight; re-verify the SQLite claim first |
| `scripts/harness.py` passes ~800 lines, or starts deciding *which* tasks exist or *whether* a gate passes | Stop. It has become a second orchestrator. Delete and re-scope |
| The founder moves to a server, or the project stops being local-only | Re-open **Temporal** — it is by far the most mature (22.9k stars, 2026-09-09 activity) |
| Claude Code turns out to export OpenTelemetry natively | Adopt OTel by **configuration**, no dependency |
| Agent teams leave experimental **and** gain a documented external task store | Re-open teams — but never as the task graph while **D-2** stands |
| Python is upgraded to ≥3.10 project-wide | Re-open the **Python Agent SDK** — it becomes a legitimate alternative to subprocess invocation |

---

# 5. WHAT I COULD NOT ESTABLISH

| # | Item | Status | Why it matters |
|---|---|---|---|
| 1 | **Nothing here was executed.** `which claude` → not found in this sandbox. Every Claude Code behaviour is documented, not observed | `UNKNOWN` | The whole recommendation rests on vendor docs. **The §4 pilot is not optional** |
| 2 | Whether a 40–80 line role pack retains behavioural fidelity when projected through `--agents` | `ASSUMPTION` | The core mechanism of the recommendation |
| 3 | Whether **Opus 5** has the Task tools by default (the docs name Opus 4.8, Sonnet 5, Fable 5, Mythos 5+ — not Opus 5) | `UNKNOWN` | A harness must not depend on `TaskCreate`/`TaskUpdate` |
| 4 | Whether **DBOS Python genuinely supports SQLite** — the claim is a maintainer's forum comment; the README still says Postgres | `LOW confidence` | Load-bearing for the only external candidate that nearly survived |
| 5 | Whether **Claude Code natively exports OpenTelemetry** — a monitoring doc page exists; not retrieved | `UNKNOWN` | Decides adopt-by-config vs adopt-by-dependency |
| 6 | Installed **Claude Code version on this machine** | `UNKNOWN` | Many capabilities above carry minimum versions (`--permission-prompts` needs v2.1.259+, `--agents` unversioned in docs). npm latest is v2.1.266 — the local install may lag |
| 7 | **Conductor** — not verified at all | `UNKNOWN` | Judged out-of-scope as a GUI, on the description alone. Low materiality |
| 8 | Real token/cost delta between subprocess-per-task and in-session subagents | `UNKNOWN` | Affects whether the harness should prefer `-p` or the in-session `Agent` tool. The teams doc warns separate instances cost *"significantly more tokens"* |
| 9 | Whether ECC's **GateGuard** hook conflicts with new `PreToolUse` hooks | `UNKNOWN` | CLAUDE.md §10 records GateGuard intercepting Bash calls. Two `PreToolUse` chains could interact badly. **Check before installing hook #5** |
| 10 | Prefect/Dagster/Temporal server footprint measured rather than reasoned about | `INFERENCE only` | I rejected them on layer and dependency count, which I consider sufficient; I did not benchmark them |

**INSUFFICIENT EVIDENCE is recorded above wherever it applies rather than papered over. Items 1, 2
and 4 are the ones that could actually overturn a conclusion in this document.**
