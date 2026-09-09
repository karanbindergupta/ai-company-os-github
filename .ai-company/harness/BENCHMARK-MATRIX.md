---
title: Coding-Agent Harness Benchmark Matrix — mechanisms, not dependencies
artifact_type: research
status: complete
owner: cro-research (Amara Diallo) — vessel
mission: harness V2 upgrade — execution control plane
created: 2026-09-09
refresh_after: 2026-12-09
supersedes: none
relates_to:
  - .ai-company/harness/ARCHITECTURE.md
  - .ai-company/harness/PHASE-0-ARCHITECTURE-MAP.md
  - .ai-company/harness/RESEARCH-LANDSCAPE.md
provider_provenance:
  exa: NOT USED — unavailable this session
  brave: NOT USED — token invalid (DEAD), never cited
  tavily: USED — primary discovery + extraction; keyless cap did not exhaust
  websearch_webfetch: primary
constraints_assumed:
  - Python 3.9.6, stdlib only
  - ONE SQLite DB (.ai-company/state/company.db) — D-2
  - No new .claude/agents/ files — D-1
evidence_labels: FACT | INFERENCE | HYPOTHESIS | ASSUMPTION | UNKNOWN
---

# Benchmark Matrix

**Write discipline note:** this file is appended to after each project is studied. If it ends
mid-matrix, everything above the cut is still valid and citable.

## The six questions

1. Crash recovery — what is persisted, at what moment, where is the write barrier?
2. Idempotency — how is double-applying a side effect on resume prevented?
3. Stale detection — heartbeats, leases, TTLs; dead vs slow worker.
4. Event log — append-only design, vocabulary, correlation IDs, no history overwrite.
5. Context assembly — what goes in, what is summarised, how provenance is kept.
6. Tool permission enforcement — enforced vs requested; where interception happens.

## Study order

1. OpenHands · 2. Cline · 3. Letta · 4. Roo Code · 5. SWE-agent · 6. Goose · then others.

---

<!-- APPEND FINDINGS BELOW THIS LINE -->

# 1. OpenHands (All Hands AI) — `software-agent-sdk`

**Sources (retrieved 2026-09-09, via Tavily `tvly search`/`tvly extract`; Exa unavailable, Brave DEAD):**
- https://docs.openhands.dev/sdk/arch/conversation
- https://docs.openhands.dev/sdk/arch/events
- https://docs.openhands.dev/sdk/guides/convo-persistence
- https://docs.openhands.dev/sdk/arch/security · https://docs.openhands.dev/sdk/guides/security
- https://docs.openhands.dev/sdk/api-reference/openhands.sdk.conversation
- https://raw.githubusercontent.com/OpenHands/software-agent-sdk/main/openhands-sdk/openhands/sdk/conversation/stuck_detector.py (source read directly)

## The six questions

**1. Crash recovery — FACT.** Persistence is a **two-path split**: `base_state.json` holds
metadata/config/status/stats and is rewritten on each modification; the `events/` directory holds
**one JSON file per event**, named `event-00000-<id>.json` — sequential index plus event id
(convo-persistence). The arXiv SDK paper states the same: *"Metadata fields serialize to a single
`base_state.json` file on each modification, while EventStore persists events as individual JSON
files"* (arxiv.org, retrieved 2026-09-09). **The write barrier is the individual event file**: an
append never rewrites history, so a crash can at worst lose the last event, never corrupt the log.
A fork of the SDK architecture doc describes JSONL event storage with **corruption tolerance —
"skips corrupted lines in events.jsonl"** and graceful handling of a missing/malformed state file
(github.com/enyst/OpenHands-Tab, `docs/agent-sdk-architecture.md`). `INFERENCE`: the file-per-event
layout is the newer design and the JSONL description is either an earlier or a fork variant — treat
the *tolerance principle* as the transferable claim, not the exact file format.
**Resume contract — FACT:** re-construct `Conversation` with the *same* `conversation_id` and
`persistence_dir` and it continues from saved state; the docs warn **"tools must match persisted on
restore"** (api-reference). That is a **compatibility check on resume**, which we do not have.

**2. Idempotency — UNKNOWN/partial.** No documented operation-ID or journal-then-apply mechanism was
found. What exists: events carry an `id`, and `ActionEvent`s carry `llm_response_id` grouping
parallel tool calls (arch/events). `INFERENCE`: replay safety comes from the fact that a resumed
conversation replays the *log into the LLM context*, not the *side effects* — tool calls are not
re-executed, their recorded `ObservationEvent` is reused. **That is the real idempotency mechanism
and it is the one we should copy**: the observation is the memoised result of the action.

**3. Stale detection — FACT, but it is stuck-detection not liveness.** `StuckDetector` reads the
last **20 events** (`MAX_EVENTS_TO_SCAN_FOR_STUCK_DETECTION = 20`), truncated to events *after the
last user message*, and matches five patterns with per-pattern thresholds
(`StuckDetectionThresholds`: `action_observation`, `action_error`, `monologue`,
`alternating_pattern`): repeating action→observation cycles, repeating action→error cycles, agent
monologue (repeated messages with no user input), alternating action/observation patterns, and
context-window errors. It records `_last_nudged_error_event_id` so the same error is not nudged
twice (source read 2026-09-09). **Note the deliberate design choice: windowed, not full-history,
"to avoid materializing large file-backed event logs."** `UNKNOWN`: heartbeat/lease-based dead-worker
detection in the agent-server was not established.

**4. Event log — FACT.** Append-only, immutable, typed. Vocabulary is small and closed:
`MessageEvent`, `ActionEvent`, `ObservationEvent`, `UserRejectObservation`, `AgentErrorEvent`,
`SystemPromptEvent`, `CondensationSummaryEvent`, `Condensation`, `CondensationRequest`,
`ConversationStateUpdateEvent`, `PauseEvent`. Every event has **id, timestamp, source**. Two
correlation keys: `llm_response_id` (groups parallel tool calls from one model response) and the
sequential event index. The doc gives an explicit provenance rule: **"Do not infer event origin from
the LLM role... rely on `Event.source`"** (arch/events). State updates take **two paths**:
state-only updates (status, counters) that do *not* append an event, and event-based updates that do
(arch/conversation). Services (visualisation, stuck detection, condenser) are **read-only observers
on the log and never mutate state** — the stated design principle.

**5. Context assembly — FACT.** Only events subclassing `LLMConvertibleEvent` become messages. A
**condenser** compresses history and emits a `CondensationSummaryEvent` describing *which events were
forgotten*, with an optional summary — so **the fact of forgetting is itself an event in the log**.
Provenance survives compaction because the summary event references the dropped range. `active_branch(limit=N)`
implies the log supports branching (`INFERENCE` from the stuck-detector source).

**6. Tool permission enforcement — FACT.** A `SecurityAnalyzerBase` with a `security_risk()` contract
sits **between the model's ActionEvent and tool execution**: *"every agent action passes through the
analyzer before execution"* (guides/security). Four levels — LOW (read-only), MEDIUM (modifies user
data), HIGH (dangerous: deletion, system commands, privilege escalation), UNKNOWN. Policy:
HIGH requires confirmation, MEDIUM/LOW pass, UNKNOWN confirms by default (`confirm_unknown=True`).
A rejection is not silent — it is recorded as a `UserRejectObservation` **event**, and
`ConversationState` carries `blocked_actions: dict[str, str]` and `blocked_messages: dict[str, str]`
(api-reference). `LLMSecurityAnalyzer` asks the model to self-declare risk; pluggable third-party
analyzers exist (`GraySwanAnalyzer` with thresholds, via the agent-server API). `ASSUMPTION`: a
model-declared risk level is advisory, not adversarially robust.

## WHAT IT DOES BETTER THAN US
1. A real append-only event log with a **closed, typed vocabulary** and source provenance. We have an
   `execution_events` table and no vocabulary.
2. **Crash-safe write barrier**: one file per event, plus corruption tolerance on read. We checkpoint
   on demand; we do not durably journal each step.
3. **Rejection is a first-class recorded event**, not an absence. Our refusals exit non-zero and
   leave no queryable trace of *what was blocked*.
4. **Compaction that logs its own forgetting** (`CondensationSummaryEvent`). We have no provenance
   for summarised context.
5. **Stuck detection as an explicit, thresholded, windowed algorithm.** Ours is capability #24, MISSING.
6. **Resume-time compatibility check** ("tools must match persisted on restore").

## WHAT WE DO BETTER THAN IT
1. **Completion that refuses on a nonexistent evidence path** with sha256 verification. OpenHands has
   no evidence gate; a conversation ends when the agent says it is finished.
2. **owner ≠ reviewer enforced in schema.** No independent-review concept exists in the SDK.
3. **11-class failure taxonomy with a bounded retry budget.** OpenHands has `AgentErrorEvent` and
   stuck-detection nudges — a loop-breaker, not a classifier.
4. **Tool-honesty refutation exiting 2.** Nothing comparable: the SDK trusts the model's own
   `security_risk` self-declaration, which is the opposite posture.
5. **DB CHECK-constrained state machine + one governed store.** OpenHands state is JSON files.

## MECHANISM WORTH LEARNING (stdlib Python + SQLite)
**(a) Observation memoisation as the idempotency primitive.** Table
`execution_events(execution_id, seq, kind, source, payload_json, correlation_id, ts)` with
`UNIQUE(execution_id, seq)`. Before performing a side-effecting operation, compute
`op_key = sha256(execution_id || tool || canonical_json(args))`; `INSERT OR IGNORE` into
`tool_calls(op_key UNIQUE, ...)`. If the insert affected 0 rows **and** a completed observation row
exists, return the stored observation instead of re-executing. That is journal-then-apply plus
memoisation in ~20 lines, and it is exactly what makes a resumed run safe.
**(b) Closed event vocabulary with a CHECK constraint:**
`CHECK(kind IN ('message','action','observation','rejection','error','system_prompt','condensation','state_update','pause','heartbeat'))`
— the same trick already used for execution status. A vocabulary enforced by the database cannot
drift the way a convention does.
**(c) Windowed stuck detector.** `SELECT kind, sha256(payload) FROM execution_events WHERE
execution_id=? ORDER BY seq DESC LIMIT 20`, drop everything up to the last `message/user`, then test
four thresholds: N identical (action,observation) hash pairs; N identical (action,error) pairs; N
consecutive agent messages with no intervening user/tool event; alternating ABAB over N cycles.
Persist `last_nudged_event_id` so one stuck streak produces one incident, not one per tick.
**(d) `condensation` event recording what was dropped** — `payload_json` = `{"forgot_seq_range":[a,b],
"summary_sha256":...}`. Compaction stops being lossy-and-silent.

## NOT APPROPRIATE FOR US
- **The agent-server / RemoteConversation split** (HTTP + WebSocket to a container). Requires a
  server; disqualified by the same constraint that killed Temporal/Restate in the prior pass.
- **`LLMSecurityAnalyzer` self-declared risk.** We already enforce authority in `companydb.py`
  against a matrix; asking the model to grade its own action is weaker than what we have and would
  regress our tool-honesty posture.
- **Pydantic-based event typing.** Third-party dep; SQLite CHECK constraints + `json` give us the
  enforcement half without the dependency.
- **File-per-event on disk.** We have D-2 (one DB). SQLite rows are our event files.

## VERDICT: **ADAPT** — the strongest single source in this study. Take (a), (b), (c), (d).

---

# 2. Cline — checkpointing

**Sources (retrieved 2026-09-09, Tavily):**
- https://docs.cline.bot/core-workflows/checkpoints (official)
- https://github.com/cline/cline/discussions/13447 (feature request naming the exact code path, Aug 21 2026)
- https://github.com/cline/cline/issues/4388 (reported failure mode of the mechanism)

## The six questions (Cline answers 1 and 2 well; the rest are largely out of scope for it)

**1. Crash recovery — FACT.** Cline maintains a **shadow Git repository separate from the project's
real Git history**, held in the editor's global storage. *"After each tool use (file edits,
commands, etc.), Cline commits the current state of your files to this shadow repo. Your main Git
repository stays untouched"* (docs). Properties claimed explicitly: checkpoints capture **untracked
files too**; they **persist across editor sessions**; each checkpoint is a complete file state, so
three sequential edits give three independently restorable points.
**The write barrier is a git commit object in a side repo** — content-addressed, immutable, cheap
because git deduplicates blobs.

**FACT — the granularity changed, and the reason is the interesting part.** As of 4.1.x the snapshot
is taken **once per user run**, in a `beforeModel` hook gated on `iteration === 1`
(`sdk/packages/core/src/hooks/checkpoint-hooks.ts`), stored as a **stash-style commit under
`refs/cline/checkpoints/...`**; mid-run there are zero snapshots (discussion #13447, Aug 2026). The
same post states why per-tool-call was coarsened: *"hangs/timeouts on large repos, storage bloat,
cross-task clobbering, firing local git hooks."* `INFERENCE`: the official docs page still describes
the classic per-tool-use behaviour and is stale relative to the beta — **do not cite the docs as
evidence of current granularity.**

**FACT — a documented failure mode of this mechanism.** Issue #4388 reports that Cline *"corrupts
Git repositories by temporarily renaming `.git` folders to `.git_disabled` and failing to restore
them when processes are interrupted, cancelled, or crash"*, breaking submodules and leaving orphaned
`.git_disabled` directories. **This is the clearest warning in the whole study: a checkpoint
mechanism that mutates the workspace in order to take its snapshot is not crash-safe.**

**2. Idempotency — the restore triad is the mechanism.** Restore is offered along **two independent
axes**, files and conversation:

| Option | Files | Conversation |
|---|---|---|
| Restore Files | reverted | kept |
| Restore Task Only | untouched | truncated after this point |
| Restore Files & Task | reverted | truncated |

`INFERENCE`: this is the key conceptual move — **workspace state and reasoning state are separately
restorable**, because the failure modes differ (bad code with good reasoning vs. good code with
poisoned reasoning). We currently have neither axis.

**3/4/5/6 — Stale detection `UNKNOWN`. Event log `UNKNOWN` beyond task message history. Context
assembly not established. Tool permission enforcement is a human-in-the-loop UI prompt
(`ASSUMPTION` from product behaviour, not read in source).** Cline is a single-user editor
extension; it has no worker-liveness problem to solve.

## WHAT IT DOES BETTER THAN US
1. **A checkpoint that actually restores.** Ours records git HEAD and state; it has **no restore
   path at all**. A checkpoint you cannot roll back to is a log entry.
2. **Snapshots capture untracked files**, which a `git HEAD` reference does not.
3. **Two-axis restore** (workspace vs. conversation) — a distinction we have not modelled.
4. **Content-addressed dedup for free** by using git as the store.

## WHAT WE DO BETTER THAN IT
1. **Our checkpoint does not mutate the workspace to take itself** — the `.git_disabled` defect
   class (#4388) is impossible for us.
2. **Evidence verification and completion refusal.** Cline's checkpoint is an undo button, not a gate.
3. **Owner ≠ reviewer, failure taxonomy, bounded retry** — all absent; Cline's recovery model is
   "the human clicks restore".
4. **Governed single store.** Cline's shadow repos live in editor global storage and have
   demonstrated **cross-task clobbering** (#13447).

## MECHANISM WORTH LEARNING (stdlib Python + SQLite)
**Shadow-worktree checkpoint using git plumbing, NEVER touching the project's `.git`.**
Python 3.9 `subprocess` against the git binary (git 2.50.1 present):
```
env = {**os.environ,
       "GIT_DIR": ".ai-company/state/checkpoints.git",   # separate repo, never the project's
       "GIT_WORK_TREE": <workspace root>,
       "GIT_INDEX_FILE": <tempfile in scratch>}          # never touches the real index
git --git-dir=... init --bare                            # once, idempotent
git add -A ; tree=$(git write-tree)
commit=$(git commit-tree $tree [-p $parent] -m "<exec_id>:<seq>")
git update-ref refs/harness/<execution_id> $commit
```
Record `(execution_id, seq, commit_sha, tree_sha, ts)` in the existing `checkpoints` table. Restore
= `git read-tree <tree> && git checkout-index -a -f`. Because `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_INDEX_FILE` are supplied per invocation, **the project's `.git` is never renamed, never locked,
and never fires a hook** — the #4388 defect class is structurally excluded. Add
`-c core.hooksPath=/dev/null -c gc.auto=0` to be certain.
**Granularity policy learned from their regression:** checkpoint at **task boundaries and before any
declared-destructive operation**, not after every tool call. Cline paid for per-tool-call
granularity in hangs and storage bloat, then removed it.
**Two-axis restore in our terms:** `restore_workspace` (git tree) and `restore_ledger` (mark
`execution_events` with `seq > N` as `superseded_by_checkpoint` — never DELETE, so history stays
append-only, which Cline's "delete messages after this point" does not).

## NOT APPROPRIATE FOR US
- Per-tool-call snapshotting — their own regression is the evidence.
- Checkpoints in an opaque per-editor global-storage location. Ours belong beside the DB.
- Deleting history on restore. Rule 15 and our audit posture require append-only; we mark
  superseded, we do not truncate.

## VERDICT: **ADAPT** — the git-plumbing checkpoint is the highest-value single mechanism for the gap
"we checkpoint but cannot restore". Reject the granularity, take the storage design.

---

# 3. Letta (ex-MemGPT) — durable agent state and memory hierarchy

**Sources (retrieved 2026-09-09, Tavily):**
- https://docs.letta.com/guides/agents/memory · https://docs.letta.com/guides/core-concepts/memory/archival-memory
- https://docs.letta.com/v1-sdk/messages/compaction (exact defaults)
- https://docs.letta.com/v1-sdk/concepts/agent-file · https://github.com/letta-ai/agent-file
- https://www.letta.com/blog/guide-to-context-engineering
- https://deepwiki.com/letta-ai/agent-file/4.2-memory-systems (`INFERENCE`-grade: third-party wiki, used only where it agrees with the official docs)

## The six questions

**1. Crash recovery — FACT, and this is Letta's whole thesis.** *"In Letta, all state, includes
memories, user messages, reasoning, tool calls, are all persisted in a database, so they are never
lost, even once evicted from the context window"* (docs.letta.com/guides/agents/memory). **There is
no in-process agent object that can die and take state with it** — the agent *is* rows in a
database, and a step reads state in and writes state out. This is the single most direct
architectural answer to our observed failure "3 agents died mid-write and their artifacts survived
by luck."
`ASSUMPTION` (not verified in source): the write barrier is the transaction boundary at the end of
each agent step.

**2. Idempotency — `UNKNOWN`.** No operation-ID / journal-then-apply mechanism was established from
the docs. Do not attribute one to Letta.

**3. Stale detection — `UNKNOWN`.** Not established. Letta is a server; liveness is presumably an
HTTP concern.

**4. Event log — FACT, with the mechanism we most need.** The `.af` (Agent File) schema lists
*"Message history — complete chat history with an **`in_context` field indicating if a message is in
the current context window**"* (github.com/letta-ai/agent-file). **Eviction from context is a
boolean flag on a retained row, not a deletion.** History is never destroyed; only its visibility
changes. That is exactly the "append-only ledger + windowed view" design we need, expressed in one
column.

**5. Context assembly — FACT, and precisely specified.** Four tiers with different residency rules
(official docs, corroborated by the deepwiki table):

| Tier | Location | Residency | Access |
|---|---|---|---|
| Core memory / memory blocks | system prompt / agent state | **always in context** | agent edits via tools |
| Message buffer | agent state | windowed, `in_context` flag | recency |
| Recall memory | external database | not in context | explicit search |
| Archival memory | external database | **cannot be pinned to context**; "must be queried on-demand via tools" | semantic search |

**Memory blocks are attachable, detachable, and shareable across agents** ("shared blocks") — the
official docs say so explicitly. `INFERENCE`: a shared block is a governed, versioned, multi-reader
context fragment — the natural implementation of "all agents on this mission see the same corrected
premise," which is exactly what our `SendMessage`-disabled failure needed and did not have.
**Compaction — FACT with numbers:** default mode `sliding_window`, `sliding_window_percentage=0.3`
(summarise oldest ~30%, keep ~70%, *"increases the summarized portion in ~10% steps if needed to fit
the token budget"*), summary clipped at 50,000 characters, summariser runs as a **separate, cheaper
model call** (`claude-haiku-4-5` / `gpt-5-mini` / `gemini-2.5-flash` defaults), with modes
`sliding_window` / `all` / others. A reported defect (github.com/letta-ai/letta/issues/3279) shows
the sharp edge: a global context cap applied to the *summariser* made compaction fail exactly when
it was needed — **the recovery path must not share the budget that overflowed.**

**6. Tool permission enforcement — PARTIAL, and the interesting part is "tool rules".** The `.af`
schema includes *"Tool rules — definitions of how tools should be sequenced or constrained"*
(github.com/letta-ai/agent-file). `INFERENCE`: this is a declarative constraint graph over tool
ordering (e.g. "tool X must be followed by tool Y", "terminal tools"), enforced by the runtime
rather than requested in a prompt. `UNKNOWN`: the exact rule vocabulary — I did not read the
implementation, and will not state it.

## WHAT IT DOES BETTER THAN US
1. **State lives in the database, not the process.** We persist *decisions* in a DB and let
   *execution* live in an ephemeral process. Letta inverts this, which is why it survives crashes.
2. **`in_context` as a flag rather than truncation** — history preserved, visibility windowed.
3. **A named, tiered memory hierarchy with explicit residency rules.** We have "artifacts on disk"
   and no residency model at all.
4. **Compaction is configurable, measured, and uses a cheaper separate model.** Ours is the host's,
   invisible to the OS, and leaves no record.
5. **Shared memory blocks** — one edit visible to many agents. Our correction-injection failure
   (RISK-011 run) is precisely this missing primitive.
6. **`.af` — a portable serialization of an entire agent's state**, including tools and message
   traces.

## WHAT WE DO BETTER THAN IT
1. **Evidence-verified completion.** Letta agents remember; they are not required to *prove* anything.
   Nothing in Letta refuses a completion for a nonexistent evidence path.
2. **Independent review enforced in schema.** Absent.
3. **Authority/veto model.** Letta has tool rules (sequencing), not *authority* (who may decide what).
4. **Failure taxonomy + bounded retry.** Absent.
5. **We are stdlib-only and serverless.** Letta requires a server and (typically) Postgres +
   embeddings for archival search — the same disqualifier that removed Temporal/Restate in the prior pass.

## MECHANISM WORTH LEARNING (stdlib Python + SQLite)
**(a) `in_context` flag instead of truncation.** Add to `execution_events`:
`in_context INTEGER NOT NULL DEFAULT 1` and `evicted_by_seq INTEGER NULL`. Compaction sets
`in_context=0` and stamps `evicted_by_seq` with the seq of the `condensation` event that replaced
them. **No row is ever deleted.** Context assembly becomes
`SELECT ... WHERE execution_id=? AND in_context=1 ORDER BY seq`. Provenance for a summary is then a
single join, and an auditor can always reconstruct what the agent *stopped* seeing and when.
**(b) Shared memory blocks as a governed table.**
`memory_blocks(block_id PK, label, content, char_limit, version, updated_by, updated_at)` plus
`block_attachments(block_id, execution_id, PRIMARY KEY(block_id, execution_id))`. An orchestrator
correction becomes: `UPDATE memory_blocks SET content=?, version=version+1` — and every attached
execution reads the new value at its next step. This is the stdlib answer to "SendMessage is
disabled": **do not push corrections to running agents; have agents pull a shared block each step.**
Enforce `length(content) <= char_limit` with a CHECK constraint so a block cannot silently blow the
context budget.
**(c) Tiered residency, enforced by query rather than convention.** `residency` column on
`memory_blocks` with `CHECK(residency IN ('core','recall','archival'))`; `core` rows are always
assembled, `recall`/`archival` require an explicit tool call that is itself recorded as an event.
Archival search without embeddings: **SQLite FTS5 is in the stdlib `sqlite3` module's bundled
library on macOS** — `HYPOTHESIS`, must be verified with
`sqlite3.connect(':memory:').execute("CREATE VIRTUAL TABLE t USING fts5(x)")` before relying on it.
Fall back to `LIKE`/token overlap if FTS5 is absent.
**(d) Compaction that cannot be starved.** Letta's issue #3279 is the lesson: give the summarisation
path its own budget, separate from the budget that was exhausted.

## NOT APPROPRIATE FOR US
- **The server + Postgres + embedding-model deployment.** Disqualified on constraints, consistent
  with the prior pass.
- **Letting the agent self-edit its own core memory unsupervised.** Our governance requires that
  changes to premises be attributable and reviewable; a self-rewriting persona block is an
  unaudited mutation of the thing we most need to keep honest.
- **`.af` as a format to adopt.** It serialises LLM configuration we do not own (the host runs the
  model). The *idea* — a complete portable state snapshot — is worth taking; the schema is not.

## VERDICT: **ADAPT** — take (a) `in_context`, (b) shared memory blocks. **DEFER** (c) archival/FTS5
until an execution actually overflows. **REJECT** the server, the embeddings, and `.af`.

---

# 4. Roo Code — task chaining, mode/permission configuration, worktree isolation

**Sources (retrieved 2026-09-09, Tavily):**
- https://roocodeinc.github.io/Roo-Code/features/custom-modes (official)
- https://roocodeinc.github.io/Roo-Code/features/boomerang-tasks (official)
- https://github.com/RooCodeInc/Roo-Code/issues/4732 (reported permission leak)
- https://github.com/RooCodeInc/Roo-Code/issues/10646 (worktree = open feature request)

## The six questions

**1. Crash recovery — `UNKNOWN`.** Not established from the docs read. Do not attribute a
persistence design to Roo Code.

**2. Idempotency — `UNKNOWN`.** Not established.

**3. Stale detection — `UNKNOWN`.**

**4. Event log — `UNKNOWN`** beyond per-task conversation history.

**5. Context assembly — FACT, and this is Roo's contribution.** "Boomerang tasks": the Orchestrator
mode calls `new_task` with a `mode` parameter; **the parent task pauses**, the subtask runs in *its
own isolated context and conversation history*, and on completion the subtask calls
`attempt_completion` — **the parent resumes receiving ONLY the `result` summary**, not the subtask's
history (official docs). The docs state the constraint bluntly: *"Information must be explicitly
passed"* — down via the initial instructions, up via the `result` parameter. **The handoff is a
narrow, declared, single-string interface, and everything else is discarded by construction.**
Also FACT: *"By default, user approval is needed for creating and completing each subtask"* — i.e.
**delegation itself is a permissioned act**, not a free one.

**6. Tool permission enforcement — FACT, and it is *declarative and static*.** A mode declares
`groups`, drawn from `read` / `edit` / `browser` / `command` / `mcp`. The `edit` group can be
narrowed with a regex over file paths:
```yaml
groups:
  - read
  - - edit
    - fileRegex: \.(js|ts)$
      description: JS/TS files only
```
Modes are defined globally or per-project in a **`.roomodes` file in the project root**
(rundatarun.io writeup, corroborated by the official custom-modes page). Stated limitations, quoted:
*"No runtime permission changes. Static file patterns only."*
**FACT — and this is the load-bearing caution:** issue #4732 reports Architect mode *"just started
editing PowerShell scripts despite not having permission to do so"* while restricted to
`fileRegex \.(md|yaml|json|toml|.+ignore|roomodes)$`. `INFERENCE`: either the pattern was not
applied on every write path, or an alternate tool (e.g. a shell command) bypassed the `edit` group.
**Either way the lesson is the same and it is the most important lesson in this section: a
path-pattern permission that does not also cover the `command`/shell path is not a permission, it
is a suggestion.** Our GateGuard-style `PreToolUse` interception is the right *shape*; the regex is
the wrong *sole* control.

**Worktree isolation — FACT, negative:** git-worktree management in Roo Code is an **open feature
request (#10646)**, not a shipped feature. Do not cite Roo as prior art for worktree isolation.
(Separately, third-party writeups claim Claude Code subagents support an `isolation: worktree`
frontmatter key — `UNVERIFIED` here, secondary sources only; the prior `RESEARCH-LANDSCAPE.md` pass
owns Claude Code natives and should be the authority, not this note.)

## WHAT IT DOES BETTER THAN US
1. **The handoff contract is narrow and enforced by construction**: a subtask returns one summary
   string; the parent cannot accidentally inherit the child's reasoning. Our `handoffs` table has
   **0 rows** and no contract at all.
2. **Delegation is an approvable act.** Spawning is itself gated. Our spawn is entirely outside
   governance (Phase-0 defect 2.4).
3. **Per-mode declarative tool + file-scope config in a checked-in project file** (`.roomodes`).
   Our role packs describe authority in prose; nothing reads them at execution time.

## WHAT WE DO BETTER THAN IT
1. **Authority is enforced against a matrix in code** (`companydb.py`), and it is *role*-scoped and
   *domain*-scoped, not merely path-scoped. A veto is a real object.
2. **Evidence-verified, refusing completion.** Roo's `attempt_completion` is the agent asserting it
   is done — exactly the "declare success without evidence" pattern rule 15 forbids.
3. **Owner ≠ reviewer.** Roo's subtask reviews itself by writing its own `result`.
4. **Failure taxonomy and bounded retry.** Absent.
5. **We have a persistent ledger.** Roo's task state is not documented as durable.

## MECHANISM WORTH LEARNING (stdlib Python + SQLite)
**(a) A declared handoff contract, recorded as a row.** Populate the empty `handoffs` table on every
delegation:
`handoffs(handoff_id PK, from_execution, to_execution, contract_json, result_summary, result_sha256,
status CHECK(status IN ('open','returned','abandoned')), created_at, returned_at)`.
`contract_json` is written **before** the child runs and names exactly what must come back
(`{"required_keys":["artifact_path","claim_labels","blocked_on"]}`). On return, `harness.py handoff
return` validates the child's summary against `required_keys` and **refuses** if a key is missing —
the same refusal semantics we already apply to evidence, applied to delegation. This turns "the
parent receives only a summary" from a convention into a checked contract, which is strictly
stronger than Roo.
**(b) Machine-readable per-role tool scope, derived from the role packs.** Table
`tool_permissions(role_slug, tool, mode CHECK(mode IN ('allow','deny','confirm')), path_regex NULL,
source)` — generated by `sync_registry.py` from the packs (D-14: packs are source of truth), then
**consulted by the hook at PreToolUse**, not by the agent. The table currently has 0 rows; this is
what fills it.
**(c) Cover the shell path or do not claim enforcement.** Learned from #4732: any `path_regex` rule
must be evaluated for `Write`/`Edit` **and** for `Bash` command strings, or an agent restricted to
`*.md` writes a `.ps1` through `cat > file`. Concretely: if the tool is `Bash`, extract candidate
write targets (`>`, `>>`, `tee`, `sed -i`, `cp`, `mv`, `install`) and apply the same regex; if the
command cannot be parsed with confidence, **`confirm` rather than `allow`** — fail closed.

## NOT APPROPRIATE FOR US
- **Regex-over-file-paths as the primary permission model.** Our unit of authority is a *decision
  domain* and a *role*, not a file glob. Path scoping is a useful secondary control only.
- **Per-subtask human approval by default.** With 119 roles and parallel dispatch this converts the
  founder into a task queue, which §2 of `CLAUDE.md` explicitly forbids.
- **A separate `.roomodes`-style config file.** D-2 and D-14: role packs are the source of truth and
  the DB is the single store; a third configuration surface would drift, exactly as `roles.json`
  once drifted from the packs.

## VERDICT: **ADAPT (a) and (c) — strongly.** (a) fills a table that has never had a row and closes
the RISK-011 self-review gap at the delegation boundary. (c) is a security correction we should make
before installing any hook, not after. **REJECT** the regex-first permission model and the
per-subtask approval default.

---

# 5. SWE-agent — agent-computer interface and trajectory recording

**Sources (retrieved 2026-09-09, Tavily):**
- https://github.com/SWE-agent/SWE-agent/blob/main/docs/background/aci.md (official)
- https://github.com/SWE-agent/SWE-agent/blob/main/docs/usage/trajectories.md (official)
- https://swe-agent.com/latest/usage/cli (official)
- https://arxiv.org/html/2405.15793v3 and the NeurIPS 2024 camera-ready PDF (the paper)
- https://dev.to/truongpx396/swe-agent-deep-dive-build-your-own-guide-ade (secondary; used for the
  flake8 ruleset, which the official docs do not enumerate — labelled `INFERENCE` accordingly)

## The six questions

**1. Crash recovery — FACT, and it is the cleanest write barrier in this whole study.** The agent
loop is:
```
while not step_output.done:
    step_output = self.step()
    self.save_trajectory()      # <- .traj written after EVERY step
```
(paraphrased loop published in the dev.to deep-dive; consistent with the official trajectories doc,
which states the `.traj` file *"contains the (thought, action, observation) turns"*). **The
trajectory is flushed to disk after every single step**, so the maximum loss window is one step.
Corroborating official CLI surface: `sweagent remove-unfinished` exists precisely because
half-finished trajectories are an expected on-disk state — **the design assumes crashes.**

**2. Idempotency — FACT, and it is the strongest in the study: `sweagent run-replay`.** *"Replay a
trajectory file or a demo file. This means that you take all actions from the trajectory and execute
them again in the environment"* (official CLI docs). Replay is **explicit and opt-in**, and it is a
*debugging/demonstration* tool, not an automatic resume. `INFERENCE`: SWE-agent's real safety
property is that the trajectory is a **complete, ordered, replayable action log** — the same
property that makes an event-sourced system recoverable. `UNKNOWN`: whether replay guards against
double-applying side effects; the environment is a fresh container per run, which sidesteps the
question rather than answering it. **Do not claim SWE-agent solved idempotency; it made it
unnecessary by starting from a clean environment.** That is itself a lesson.

**3. Stale detection — `UNKNOWN`.** Not established.

**4. Event log — FACT.** One `.traj` JSON per episode holding *"history, model output, observations,
costs"* (dev.to; the paper says the per-episode artifacts are *"the trajectory... and the final
patch generation"*). Vocabulary is a strict repeating triple: **(thought, action, observation)**.
`traj-to-demo` converts a trajectory into an editable demonstration, and demonstrations are fed back
into future runs as few-shot context — **the log is not only for auditors, it is reusable training
context**. That is a use of our ledger we had not considered.

**5. Context assembly — FACT, and this is the paper's central claim.** The Agent-Computer Interface
is designed for the *model's* limits, not the human's:
- a **purpose-built file viewer showing 100 lines per turn** with scroll and in-file search, rather
  than `cat` (official aci.md: *"we found that this file viewer works best when displaying just 100
  lines in each turn"*);
- line-targeted `edit` rather than free-form rewriting;
- search results summarised rather than dumped.
The dev.to synthesis states the measured effect: a windowed viewer + line-targeted edit +
syntax-checked autosave *"roughly doubles SWE-Bench score versus raw bash"* — `INFERENCE`, secondary
source, magnitude not independently verified, but directionally consistent with the paper's ablations.
**The claim to take seriously: the interface, not the model, was the binding constraint.**

**6. Tool permission enforcement — FACT, expressed as a *guardrail on the tool itself*.** *"We add a
linter that runs when an edit command is issued, and **do not let the edit command go through if the
code isn't syntactically correct**"* (official aci.md). The paper adds the exact semantics: if the
linter produces output, *"the edit is reverted"*, and the agent is shown the error plus **what the
edit would have looked like** if applied. The ruleset is deliberately narrow — `flake8 --isolated
--select=` F821/F822 (undefined names), F831 (duplicate args), E111/E112/E113 (indentation), E999
(syntax error), E902 (IO/tokenization) — *"not general-purpose linting... a hand-picked 'did your
edit produce broken Python' checklist"* (`INFERENCE`, dev.to, ruleset not in official docs).
**This is validate-then-apply implemented inside the tool, which is the correct interception point:
the agent cannot route around it, because there is no other edit path.**

## WHAT IT DOES BETTER THAN US
1. **Write-after-every-step durability.** We checkpoint when an agent remembers to. SWE-agent writes
   unconditionally in the loop. Our 3-agents-died-mid-write failure is exactly what this prevents.
2. **A replay command that exists and is documented.** Our capability #30 (reproducibility) is MISSING.
3. **Validate-then-apply inside the tool**, with the rejected edit *shown back* to the agent — a
   refusal that teaches. Our refusals exit non-zero and say why, but do not return the counterfactual.
4. **An interface deliberately budgeted for the model** (100 lines/turn). We have no context budget
   at all; an agent reads whatever it wants until the session dies.
5. **The log doubles as reusable demonstration context** (`traj-to-demo`).

## WHAT WE DO BETTER THAN IT
1. **Evidence verification with sha256 against the filesystem**, and completion that refuses. A
   SWE-agent episode ends when the agent submits; nothing checks that the claimed artifact exists.
2. **Independent review (owner ≠ reviewer).** SWE-agent has no reviewer concept — evaluation is
   external and post-hoc (SWE-bench).
3. **11-class failure taxonomy with bounded retry.** SWE-agent has a retry-the-edit loop, not a
   classifier, and no cross-run budget.
4. **Authority and veto.** Entirely absent; SWE-agent is one agent, one issue.
5. **Governed single store.** Trajectories are loose files under `trajectories/`.

## MECHANISM WORTH LEARNING (stdlib Python + SQLite)
**(a) Unconditional step-flush — the write barrier we are missing.** Wrap every harness-observed
step in:
```python
con.execute("BEGIN IMMEDIATE")
con.execute("INSERT INTO execution_events(execution_id,seq,kind,source,payload_json,ts) VALUES (?,?,?,?,?,?)", ...)
con.execute("UPDATE executions SET last_seq=?, heartbeat_at=? WHERE execution_id=?", ...)
con.commit()          # <- the barrier; nothing else is the barrier
```
with `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=FULL` set once at open. **WAL + a committed
transaction per step gives us SWE-agent's guarantee with a stronger integrity story than a JSON file
rewrite**, because a torn write cannot corrupt earlier events. Note: WAL creates `-wal`/`-shm`
sidecar files next to `company.db` — they must be added to `.gitignore`, and the DB should be
checkpointed (`PRAGMA wal_checkpoint(TRUNCATE)`) before committing the DB to git, since the DB is
tracked (§9). This is a real operational consequence and must be decided explicitly, not assumed.
**(b) Validate-then-apply, returning the counterfactual.** Generalise our evidence check into a
`harness.py apply --dry-run` shape: compute the proposed post-state, run the declared validator
(for us: `python3 -m py_compile`, `secret_scan.sh`, front-matter presence, claim-label presence),
and if it fails, **write a `rejection` event containing both the reason and the rejected payload**,
then exit non-zero. The agent gets told what it *would* have done. Cheap, stdlib, and it converts
our refusals from a wall into a correction signal.
**(c) A `replay` command that re-derives state from the event log**, not from the environment:
`harness.py replay <execution_id>` prints the ordered (action, observation) pairs and re-verifies
every recorded evidence sha256 against the current filesystem, reporting drift. That is a *safe*
replay — it re-checks rather than re-executes, so it can never double-apply a side effect.
**(d) A declared context budget per execution.** `executions.context_budget_events INTEGER` and a
100-line-equivalent convention for artifact reads; when exceeded, emit a `condensation` event
(mechanism from OpenHands §1(d)) rather than silently continuing until the session dies.

## NOT APPROPRIATE FOR US
- **flake8 as the validator.** Third-party dependency; `py_compile`/`ast.parse` from the stdlib gives
  us E999-equivalent for Python, and our artifacts are mostly Markdown, where the meaningful
  validator is front-matter + claim labels, not syntax.
- **Fresh-container-per-run as the idempotency strategy.** Docker is blocked (no Homebrew, §10), and
  our side effects are governed artifacts in a git repo that must persist across runs. We must solve
  idempotency properly (OpenHands §1(a) memoisation) rather than avoid it.
- **`run-replay`'s re-execute semantics.** Re-executing recorded actions against a live repo is
  precisely the double-apply hazard. Take the read-only variant in (c).

## VERDICT: **ADAPT (a) and (b) — (a) is the single highest-value change in the entire study.**
ADAPT (c) in read-only form. DEFER (d). REJECT flake8 and re-executing replay.

---

# 6. Goose (Block) — session persistence, extension model, permission modes

**Sources (retrieved 2026-09-09, Tavily):**
- https://goose-docs.ai/docs/guides/goose-cli-commands (session storage + CLI flags)
- https://block.github.io/goose/docs/guides/goose-permissions (official permission modes)
- https://block.github.io/goose/docs/guides/tool-permissions (per-tool permission levels)
- https://github.com/aaif-goose/goose/issues/10252 (third-party fork issue; used only as a
  *reported user experience*, labelled `INFERENCE`, not as design evidence)

## The six questions

**1. Crash recovery — FACT, and it is the most directly relevant precedent in this entire study.**
*"Starting with version 1.10.0, goose uses a SQLite database (`sessions.db`) instead of individual
`.jsonl` files. Your existing sessions are automatically imported to the database. Legacy `.jsonl`
files remain on disk but are no longer managed by goose"* (official CLI docs).
**A mature, widely-used coding harness migrated FROM append-only JSONL TO SQLite for session
storage.** That is external corroboration that the architecture we are already committed to (D-2:
one SQLite store) is the endpoint other harnesses converge on, not a constraint we are suffering
under. It also shows the migration cost: the legacy files were imported once and then abandoned —
**exactly the shape of the `tasks.json` → `companydb.tasks` unification that Phase 0 flagged as
defect 2.1 and left unfixed.**
Resume is a first-class CLI surface: `goose session -r` / `--name <name>` / `--path <PATH>`.
`INFERENCE`: named, addressable sessions are what make resume usable — an execution you cannot name
is an execution you cannot resume.
**Cautionary data point (`INFERENCE`, single report on a fork):** issue #10252 describes a 14 MB
session JSON surviving on disk but being *"rendered inaccessible after a goose update"*, and
proposes a `memory.merge(path)` API to re-import an orphaned session. **A durable file that the
current version can no longer read is not durable.** Whatever we build must keep a versioned,
forward-compatible read path — which our `schema_version` migration table already provides, and
which we should not let rot.

**2. Idempotency — `UNKNOWN`.** Not established. Do not attribute one.

**3. Stale detection — `UNKNOWN`.** Not established.

**4. Event log — `INFERENCE`.** Sessions are message histories in `sessions.db`; the pre-1.10 format
was `.jsonl`, i.e. append-only-by-line. The internal event vocabulary was not read and is `UNKNOWN`.

**5. Context assembly — FACT (partial).** Two persistent-context surfaces: a `.goosehints` file
(project-level standing instructions) and a Memory extension (MCP server) for retrieved memories.
The proposed resume API in #10252 takes `messages: number` — *"number of recent messages to load
(default: 20)"* — `INFERENCE`: resume loads a bounded recent window, not the whole history, which is
the same windowing instinct as OpenHands' 20-event stuck window and SWE-agent's 100-line viewer.
**Three independent harnesses converge on "assemble a bounded recent window, not everything."**

**6. Tool permission enforcement — FACT, and the mode taxonomy is worth stealing verbatim.** Four
modes, switchable mid-session with `/mode`: **`auto` (autonomous)**, **`approve` (manual)**,
**`smart_approve`**, **`chat` (no extensions, no commands — planning only)**. Under manual and smart
modes, *"goose will only ask for permission for tools that it deems are 'write' tools, e.g. any
'text editor write', 'text editor edit', 'bash - rm, cp, mv' commands"*, and the docs are refreshingly
honest about the limit: *"Read/write approval makes best effort attempt at classifying read or write
tools"* (official permissions guide). Beneath the modes there is **per-tool, per-extension permission
configuration** (tool-permissions guide) — so the mode is a default and the per-tool rule is an
override.
**Two design lessons.** (i) A **`chat`/plan mode that structurally cannot execute** is a stronger
control than asking an agent to be careful — it is the same instinct as our `harness.py` deliberately
not being able to spawn. (ii) The vendor states plainly that write-classification is *best effort*;
**a classifier-based permission is advisory. Ours must be declarative (a table), with the classifier
only able to escalate to `confirm`, never to downgrade to `allow`.**

## WHAT IT DOES BETTER THAN US
1. **Named, addressable, resumable sessions with a CLI surface.** We have execution IDs and no resume.
2. **They actually completed the JSONL→SQLite consolidation** we have on our backlog as defect 2.1.
3. **A four-mode permission ladder including a genuinely non-executing mode**, switchable mid-run.
4. **Per-tool permission granularity layered under a coarse mode.**

## WHAT WE DO BETTER THAN IT
1. **Permissions are tied to a governed authority matrix and a role**, not to a user's UI toggle. A
   Goose mode is a user preference; our authority is an organizational fact with a veto holder.
2. **Evidence-verified completion and refusal on a nonexistent path.** Goose has no completion gate.
3. **Owner ≠ reviewer in schema.** Absent.
4. **Failure taxonomy + bounded retry.** Absent.
5. **Tool-honesty refutation.** Goose records tool calls; it does not refute a false claim of use.

## MECHANISM WORTH LEARNING (stdlib Python + SQLite)
**(a) A permission-mode ladder, stored and enforced, not toggled.**
`executions.permission_mode TEXT NOT NULL DEFAULT 'approve' CHECK(permission_mode IN
('chat','approve','smart_approve','auto'))`. The `PreToolUse` hook reads the row for the current
execution and resolves in this precedence order, which must be **deny-biased**:
```
1. explicit DENY in tool_permissions        -> block (exit 2)
2. founder-required domain touched          -> block, emit escalation row
3. explicit ALLOW in tool_permissions       -> allow
4. mode == 'chat' and tool is not read-only -> block
5. write-classifier says write              -> confirm
6. otherwise                                -> allow
```
Rule 1 before rule 3 and the classifier only able to produce `confirm` are the whole design: **a
best-effort classifier can add friction but can never grant permission.**
**(b) Named executions and a real `resume`.** `executions.name TEXT UNIQUE` plus
`harness.py resume <name|id>` which (i) reloads the last `checkpoint`, (ii) replays the last N
`in_context=1` events as a briefing block, (iii) re-verifies recorded evidence hashes, and (iv)
emits a `resumed` event with the prior `last_seq` so the ledger shows the seam. N bounded (20 is the
number three separate harnesses chose independently).
**(c) Finish the JSONL→DB consolidation, using Goose's migration shape.** Import `tasks.json` into
`companydb.tasks` once, write a `schema_version` bump, leave the JSON on disk **read-only and
marked superseded** rather than deleting it, and make `company.py task-add` write to the DB. Goose's
own users show the failure mode to avoid: an orphaned legacy file the new version cannot read.
**This is Phase-0 defect 2.1 and it is a governance-adjacent change — recommend, do not assume.**

## NOT APPROPRIATE FOR US
- **The extension/MCP configuration model as a permission boundary.** Our MCP surface is configured
  in `.mcp.json` at the project level and includes production-capable servers (Supabase, §16);
  per-session extension toggling is a weaker control than the deny-list we already have.
- **Mid-session mode switching by the agent.** A running agent must not be able to widen its own
  permissions; mode changes belong to the orchestrator or the founder (rule 14).
- **`.goosehints`-style free-text standing instructions as the persistence mechanism.** We have
  `CLAUDE.md` and role packs; a third prose surface would drift (D-14).

## VERDICT: **ADAPT (a) and (b).** (c) is the right fix but is **ESCALATE, not adopt** — it changes
the orchestrator's write path and touches D-2 governance.

---

# 7. OpenCode — declarative tool permissions, and the honest state of liveness detection

Studied out of the stated order because it turned out to hold **the single best primary source on
question 6** (enforced permissions) and **the clearest evidence on question 3** (stale detection).

**Sources (retrieved 2026-09-09, Tavily):**
- https://opencode.ai/docs/permissions (official — the load-bearing source)
- https://opencode.ai/docs/agents (official)
- https://github.com/anomalyco/opencode/issues/13841 (precise diagnosis of a missing watchdog)
- https://github.com/anomalyco/opencode/issues/11865 (subagent hangs forever — no timeout/retry)

## Question 6 — tool permission enforcement. FACT, quoted from the official docs.

Permissions are **keyed by tool name**, each set to `"allow"` (run without approval), `"ask"`
(prompt), or `"deny"` (block). The full key set:
`read` (matches the file path) · `edit` (covers edit/write/patch) · `glob` · `grep` ·
**`bash` — "matches parsed commands like `git status --porcelain`"** · **`task` — "launching
subagents (matches the subagent type)"** · `skill` · `lsp` · `question` · `webfetch` (matches URL) ·
`websearch` (matches query) · **`external_directory` — "triggered when a tool touches paths outside
the project working directory"** · **`doom_loop` — "triggered when the same tool call repeats 3
times with identical input."**

Rule resolution, quoted: *"Rules are evaluated by pattern match, with the **last matching rule
winning**. A common pattern is to put the catch-all `"*"` rule first, and more specific rules
after it."* Wildcards are simple: `*` = zero or more characters, `?` = exactly one.
Defaults: most permissions `allow`; **`doom_loop` and `external_directory` default to `ask`**;
`read` is `allow` **"but `.env` files are denied by default."**
Auto mode (`--auto`) auto-approves anything not explicitly denied — and the docs are explicit that
**"Explicit `deny` rules are still enforced. Auto mode only changes requests that would otherwise
ask for approval."** `deny` is unconditional and outranks the mode.
`ask` offers three outcomes — `once`, `always`, `reject` — where `always` whitelists a
**tool-suggested pattern**, e.g. bash approvals *"typically whitelist a safe command prefix like
`git status*`"*, scoped to the current session only.
Per-agent overrides live in agent frontmatter, and the community idiom is deny-by-default:
`"*": deny` then allow specific tools (reddit r/opencodeCLI — `INFERENCE`, community source, cited
only as an idiom, not as design).

**Four things here are better than anything else found in this study:**
1. **`bash` permissions match the *parsed command*, not the raw string.** This is the direct answer
   to Roo Code's #4732 leak (§4): if you do not parse the shell command, your file-scope permission
   is decorative.
2. **`task` is a permission.** Delegation is a governed tool call, matched by subagent type. Our
   Phase-0 defect 2.4 is exactly "spawn is outside governance"; OpenCode shows the fix is one row.
3. **`external_directory` as a first-class guard** — a single rule that catches every path-taking
   tool escaping the workspace, instead of N per-tool path rules.
4. **`doom_loop` as a *permission* rather than a heuristic**: an identical tool call repeated 3 times
   raises a configurable event you can set to `ask` or `deny`. Compare OpenHands' 20-event pattern
   matcher (§1) — OpenCode's is cruder but trivially implementable and needs no LLM.

## Question 3 — stale detection. The honest finding is a NEGATIVE one, and it matters.

`FACT` — issue #13841 diagnoses precisely: *"The `LLM.stream()` call at `llm.ts:211` passes only the
session's `AbortSignal` — there is no `streamIdleTimeout` or chunk-activity watchdog. Individual
tools each have their own `abortAfter()` timeouts (bash: 2min, webfetch: 30–120s, websearch: 25s via
`abort.ts`), but the LLM stream itself has none... The heartbeat code in `server.ts:520-532` is for
SSE connections to the TUI WebView, not for LLM API streams."*
`FACT` — issue #11865: *"a subagent gets stuck and the session hangs forever because apparently
there is not timeout/retry."*

**Synthesis across all seven projects: none of them has a real lease/heartbeat model for detecting a
dead agent.** OpenHands has stuck-*pattern* detection (not liveness). OpenCode has per-tool
timeouts and a heartbeat that measures **the wrong thing** — UI connectivity, not agent progress.
Cline, Roo, SWE-agent and Goose: `UNKNOWN` / absent.
`INFERENCE`, and it is the most useful conclusion in this document: **liveness is the least-solved
problem in the field, so we should not expect to copy it — we have to design it.** The good news is
that it is also the cheapest thing to build against SQLite, and our observed failure (3 of 4 agents
killed by a session rate limit, detected by a notification rather than by the OS) is exactly the
failure a lease would have caught.

## WHAT IT DOES BETTER THAN US
1. **A declarative, pattern-matched, deny-biased permission table covering every tool including
   `task` (spawn) and shell command *parsing*.** Our `tool_permissions` table has **0 rows**.
2. **A cheap, deterministic loop detector** (`doom_loop`, 3 identical calls) that needs no model.
3. **A workspace-escape guard** as one rule rather than many.
4. **`deny` that survives auto mode** — a mode cannot widen an explicit prohibition.

## WHAT WE DO BETTER THAN IT
1. **Our permissions would be tied to a role and an authority matrix with a veto holder**, not to a
   config file a user edits. OpenCode's model is expressive but has no notion of *who is entitled*.
2. **Evidence-verified completion, refusal on nonexistent paths, owner ≠ reviewer, failure taxonomy,
   tool-honesty refutation** — none of which exist in OpenCode.
3. **We already know our liveness gap and have named it** (capabilities #22–#24). OpenCode's is a
   live bug report.

## MECHANISM WORTH LEARNING (stdlib Python + SQLite)
**(a) The permission table, fail-closed, with last-match-wins.**
```sql
CREATE TABLE IF NOT EXISTS tool_permissions (
  rule_id     INTEGER PRIMARY KEY,          -- ordinal = precedence; higher wins
  scope       TEXT NOT NULL,                -- '*' | role_slug | execution_id
  tool        TEXT NOT NULL,                -- 'read','edit','bash','task','webfetch',...
  pattern     TEXT NOT NULL DEFAULT '*',    -- fnmatch pattern over the tool's matched input
  action      TEXT NOT NULL CHECK(action IN ('allow','ask','deny')),
  source      TEXT NOT NULL,                -- role pack path / founder decision id
  created_at  TEXT NOT NULL
);
```
Resolution in `harness.py permit --tool X --input S --role R`: select rules where
`scope IN ('*', :role, :execution)` and `fnmatch.fnmatch(S, pattern)` (stdlib `fnmatch`), order by
`rule_id`, **take the last match**; if none matched, return `deny` — **we invert OpenCode's
permissive default, because our constitution is deny-biased and a permissive default is how a
governance control becomes decorative.** Exit code 0 allow / 1 ask / 2 deny, so a `PreToolUse` hook
can consume it directly with no parsing.
**(b) Matched-input extraction per tool, including the shell.** `read`/`edit` → the path;
`webfetch` → the URL; `task` → the subagent/role slug; `bash` → **the parsed command**. For bash,
`shlex.split()` (stdlib) each `;`/`&&`/`|`-separated segment, take `argv[0]` plus its first
argument, and match on that normalised string (`"git status"`, `"rm -rf"`). If `shlex` raises or the
segment contains redirection into an unexpected path, **return `ask`, never `allow`** — fail closed
on ambiguity. This single rule is what makes the permission real rather than advisory (Roo #4732).
**(c) `doom_loop` in four lines of SQL.**
```sql
SELECT COUNT(*) FROM (
  SELECT payload_sha256 FROM tool_calls
  WHERE execution_id=? ORDER BY seq DESC LIMIT 3)
GROUP BY payload_sha256 HAVING COUNT(*)=3;
```
Non-empty result ⇒ the same tool call with identical input three times ⇒ emit a `doom_loop` event
and apply the configured action. `payload_sha256 = sha256(tool + '\x00' + canonical_json(args))`.
Bounded, deterministic, no model, and it directly serves rule 11 (*do not repeat a failed action
unchanged*) — **we have that rule in prose and no code that detects the violation.**
**(d) `external_directory` guard.** One rule: `os.path.realpath(target)` must be under
`os.path.realpath(workspace_root)` — `realpath` first, so symlink escapes are caught — else `ask`.
Cheap, and it protects the worktree boundary we already rely on.
**(e) Leases, since nobody has them to copy (see Question 3).** Add to `executions`:
`heartbeat_at TEXT`, `lease_expires_at TEXT`, `lease_owner TEXT`, `wall_clock_budget_s INTEGER`.
Every event write bumps `heartbeat_at` in the same transaction (free — the barrier is already there
per SWE-agent §5(a)). `harness.py reap` marks any execution `RUNNING` with
`lease_expires_at < now()` as `STALE` (a new CHECK-constrained state), writes a `lease_expired`
event, and files a failure of class `INFRA/TIMEOUT` against the bounded retry budget. **A dead
worker is distinguished from a slow one by whether it has written an event, not by wall-clock age
alone** — a long-running agent that is still emitting events keeps renewing its lease; a killed one
does not. That is the distinction OpenCode's SSE heartbeat gets wrong, and it costs us nothing
because our lease is renewed by the work itself.

## NOT APPROPRIATE FOR US
- **OpenCode's permissive defaults** (`most permissions default to allow`). Invert them.
- **`ask` as a frequent outcome.** With parallel dispatch and a founder who is explicitly *not a
  task queue*, `ask` must be rare and reserved for founder-required domains; everything else should
  resolve to `allow` or `deny` from the matrix without a human in the loop.
- **A JSON config file as the permission source of truth.** D-2/D-14: role packs generate the table;
  the table is what the hook reads.

## VERDICT: **ADAPT — (a), (b), (c), (d), (e).** This section supplies the concrete design for the
two capabilities the founder named as missing: enforced tool governance and stale detection.

---

# 8. CROSS-CUTTING MATRIX

Blank cells are `UNKNOWN` — not established from primary sources this session, and deliberately not
guessed.

| | Crash recovery | Idempotency | Stale detection | Event log | Context assembly | Tool enforcement |
|---|---|---|---|---|---|---|
| **OpenHands** | file-per-event + `base_state.json`; corruption-tolerant read | observation reuse on replay (`INFERENCE`) | stuck-pattern, 20-event window, 5 patterns | **closed typed vocabulary, `source`, `llm_response_id`** | condenser + `CondensationSummaryEvent` records what was forgotten | analyzer between action and execution; 4 risk levels; rejection recorded as event |
| **Cline** | **shadow git repo, commit per snapshot**; captures untracked files | two-axis restore (files / conversation) | — | — | — | human approval in UI |
| **Letta** | **all state in the database; agent is rows, not a process** | — | — | messages retained with **`in_context` flag** | 4 tiers; sliding-window compaction 0.3, 50k char cap, separate cheap model | tool rules (sequencing) `INFERENCE` |
| **Roo Code** | — | — | — | — | **subtask returns only a `result` summary; isolated child context** | mode `groups` + `fileRegex`; **leaked (#4732)**; "no runtime permission changes" |
| **SWE-agent** | **`save_trajectory()` after every step** | `run-replay` re-executes; clean container sidesteps the problem | — | `.traj`: (thought, action, observation) + costs; `traj-to-demo` | **100-line viewer, line-targeted edit** | **linter inside the edit tool; invalid edit reverted and shown back** |
| **Goose** | **migrated JSONL → SQLite `sessions.db` (v1.10.0)**; named sessions, `-r` resume | — | — | messages in `sessions.db` | `.goosehints` + memory extension; resume loads ~20 recent | 4 modes (auto/approve/smart/chat) + per-tool levels; write-classifier is *"best effort"* |
| **OpenCode** | — | — | **per-tool timeouts only; heartbeat measures the UI, not the agent (#13841); subagents hang forever (#11865)** | — | — | **allow/ask/deny per tool, pattern-matched on parsed input, last-match-wins; `task`, `external_directory`, `doom_loop` are permissions; `deny` survives auto mode** |

**Not studied — budget exhausted, honestly declared:** Mastra, DeepAgents, PydanticAI. `UNKNOWN`.
No claim is made about them anywhere in this document.

## Three convergences worth more than any single feature
1. **Everyone windows.** OpenHands scans 20 events, Goose resumes ~20 messages, SWE-agent shows 100
   lines. Independent teams landed on bounded assembly. We currently assemble without a budget.
2. **Everyone's durable unit is a step, not a task.** SWE-agent flushes per step; OpenHands writes
   per event; Letta puts state in the DB. **The write barrier is always *inside* the loop.** Ours is
   outside it — `checkpoint` is a command an agent may or may not call.
3. **Nobody has solved liveness.** See §7, question 3. This is a gap in the field, not a gap in our
   research. We must design it; the design is cheap.

---

# 9. TOP 8 MECHANISMS TO ADAPT — prioritised

Ranked for a system that **already has** evidence verification, refusal semantics, owner ≠ reviewer,
an 11-class failure taxonomy and a CHECK-constrained state machine, and **lacks** crash recovery,
heartbeats, an event log, and enforced tool governance.

### 1. Step-flush write barrier — WAL + one committed transaction per event
*From SWE-agent (`save_trajectory()` after every step); corroborated by OpenHands and Letta.*
Open the DB once with `PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000`.
Every harness-observed step executes `BEGIN IMMEDIATE`, inserts one `execution_events` row, bumps
`executions.last_seq` and `executions.heartbeat_at`, and commits — **the commit is the barrier and
nothing else is**. Maximum loss on a killed process is one step, and a torn write cannot corrupt
earlier events because SQLite's WAL is append-structured. Two consequences must be handled
explicitly, not discovered later: WAL creates `company.db-wal`/`-shm` sidecars which must be
gitignored, and because `company.db` is tracked in git (§9), any commit path must first run
`PRAGMA wal_checkpoint(TRUNCATE)` so the committed file is complete. This is the single highest-value
change in the study: it converts "artifacts survived by luck" into a guarantee.

### 2. Append-only event log with a closed vocabulary and an `in_context` flag
*From OpenHands (typed vocabulary, `source`, correlation IDs) + Letta (`in_context`).*
`execution_events(execution_id, seq, kind, source, actor_role, payload_json, payload_sha256,
correlation_id, in_context INTEGER DEFAULT 1, evicted_by_seq, ts)` with `UNIQUE(execution_id, seq)`
and `CHECK(kind IN ('message','action','observation','rejection','error','checkpoint','condensation',
'state_update','handoff','heartbeat','lease_expired','doom_loop','resumed'))`. Two update paths, as
OpenHands does: cheap counters update `executions` without an event; anything semantic appends.
**Nothing is ever deleted** — compaction sets `in_context=0` and stamps `evicted_by_seq` on the
`condensation` event that replaced the range, so an auditor can always reconstruct what an agent
stopped seeing and when. `seq` allocation goes through the existing `id_sequences` table, which
already fixed the observed RISK-007/008/009 collision. This is the substrate the next six mechanisms
all sit on; build it second and only once.

### 3. Deny-biased `tool_permissions` table, resolved by the harness, enforced by a `PreToolUse` hook
*From OpenCode (the design) + Roo Code #4732 (the failure mode that shapes it).*
Rows are `(rule_id, scope, tool, pattern, action CHECK(action IN ('allow','ask','deny')), source)`;
resolution selects rules matching `scope IN ('*', role_slug, execution_id)` and
`fnmatch.fnmatch(matched_input, pattern)`, orders by `rule_id`, and **takes the last match — with no
match meaning `deny`**, inverting OpenCode's permissive default because our constitution is
deny-biased. Matched input is per-tool: path for `read`/`edit`, URL for `webfetch`, **role slug for
`task` (so delegation is finally a governed act, closing Phase-0 defect 2.4)**, and for `bash` the
**parsed** command — `shlex.split()` each `;`/`&&`/`|` segment, normalise to `argv[0] + ' ' +
argv[1]`, and on any parse ambiguity or unexpected redirection return `ask`, never `allow`. Rows are
generated from the role packs by `sync_registry.py` (D-14), never hand-written. `harness.py permit`
exits 0/1/2 so a hook consumes it with no parsing. **Installing the blocking hook is a governance
change under rule 14 and requires founder authorisation — build and test the resolver first, ship
the hook only on approval.**

### 4. Leases renewed by work, and a `reap` command
*Designed, not copied — §7 establishes that no studied project has this.*
Add `heartbeat_at`, `lease_expires_at`, `lease_owner`, `wall_clock_budget_s` to `executions`. Because
mechanism 1 already writes a transaction per step, renewing the lease is free: the same statement
sets `heartbeat_at=now()` and `lease_expires_at=now()+ttl`. `harness.py reap` transitions any
`RUNNING` execution whose `lease_expires_at` has passed into a new CHECK-constrained `STALE` state,
appends a `lease_expired` event, and files an `INFRA`/`TIMEOUT` failure against the existing bounded
retry budget so a dead agent consumes an attempt rather than silently vanishing. **A slow agent is
distinguished from a dead one by whether it is still emitting events, not by elapsed time** — which
is exactly what OpenCode's SSE heartbeat fails to measure (#13841). This is what would have caught
the three agents killed by the session rate limit.

### 5. Operation keys and observation memoisation — idempotent resume
*From OpenHands (the observation is the memoised result of the action).*
Before any side-effecting operation, compute `op_key = sha256(execution_id + '\x00' + tool + '\x00' +
json.dumps(args, sort_keys=True, separators=(',',':')))` and `INSERT OR IGNORE INTO tool_calls(op_key
UNIQUE, execution_id, seq, tool, args_json, status, result_json)`. If the insert changes 0 rows and
the existing row has `status='completed'`, **return the stored result instead of re-executing**; if
it has `status='started'`, the operation died mid-flight and must be classified, not blindly retried.
This is journal-then-apply plus memoisation, it is roughly twenty lines of stdlib, and it is the
difference between a resume that is safe and a resume that double-applies. Deliberately do **not**
copy SWE-agent's `run-replay` re-execution semantics against a live repo.

### 6. Git-plumbing shadow checkpoint that can actually restore
*From Cline (shadow repo), with its own #4388 defect designed out.*
Keep a bare repo at `.ai-company/state/checkpoints.git`. Snapshot by invoking git with
`GIT_DIR`, `GIT_WORK_TREE` and a scratch `GIT_INDEX_FILE` in the environment, plus
`-c core.hooksPath=/dev/null -c gc.auto=0`: `git add -A`, `git write-tree`, `git commit-tree` with
the previous checkpoint as parent, `git update-ref refs/harness/<execution_id>`. Store
`(execution_id, seq, commit_sha, tree_sha)` in the existing `checkpoints` table. Restore is
`git read-tree <tree> && git checkout-index -a -f`. **Because every invocation supplies its own
GIT_DIR/WORK_TREE/INDEX, the project's `.git` is never renamed, never locked and never fires a hook —
the exact defect class Cline shipped (#4388) is structurally impossible.** Checkpoint at task
boundaries and before declared-destructive operations, *not* per tool call: Cline paid for that
granularity in hangs and storage bloat and then removed it. Pair with a ledger-side restore that
marks superseded events rather than deleting them.

### 7. `doom_loop` + windowed stuck detection — rule 11 finally enforced in code
*From OpenCode (`doom_loop`, 3 identical calls) + OpenHands (5-pattern, 20-event window).*
Cheapest first: after each `tool_calls` insert, check whether the last three rows for this execution
share a `payload_sha256`; if so append a `doom_loop` event and apply the configured action. Then the
richer version over `execution_events`: take the last 20 rows, drop everything up to the last
`message` from the orchestrator, and test four thresholds — N identical (action, observation) hash
pairs, N identical (action, error) pairs, N consecutive agent messages with no intervening
tool/observation event, and an ABAB alternation over N cycles. Persist `last_nudged_event_id` so one
stuck streak produces one incident rather than one per tick. **Governance rule 11 says "do not repeat
a failed action unchanged"; today nothing detects the violation. This is the detector.**

### 8. Handoff contracts and shared memory blocks — governed delegation and correction propagation
*From Roo Code (the narrow summary-only handoff) + Letta (shared, attachable memory blocks).*
Two tables. First, populate the `handoffs` table that has never had a row:
`(handoff_id, from_execution, to_execution, contract_json, result_summary, result_sha256, status
CHECK(status IN ('open','returned','abandoned')))`, where `contract_json` is written **before** the
child starts and names the required return keys; `harness.py handoff return` validates the child's
summary against them and **refuses** if one is missing — applying our existing refusal semantics to
delegation, which is strictly stronger than Roo, where a subtask writes its own `attempt_completion`
unchecked. Second, `memory_blocks(block_id, label, content, char_limit, version, updated_by,
updated_at)` with `block_attachments(block_id, execution_id)` and a
`CHECK(length(content) <= char_limit)`. An orchestrator correction becomes a single versioned UPDATE
that every attached execution reads at its next step. **This is the stdlib answer to the observed
`SendMessage`-disabled failure: stop trying to push corrections into running agents; have agents pull
a shared block each step.**

---

# 10. WHAT WE ALREADY DO BETTER THAN ALL SEVEN — do not trade any of it away
1. **Completion that refuses on a nonexistent evidence path, sha256-verified.** No project studied
   has an evidence gate. Every one of them ends a task when the agent says it is finished.
2. **owner ≠ reviewer enforced in schema.** No project studied has an independent-review concept.
3. **11-class failure taxonomy with bounded retry.** The field has retry loops and stuck nudges, not
   classifiers with budgets.
4. **Tool-honesty refutation exiting 2.** OpenHands moves in the opposite direction, asking the model
   to self-declare its own action's risk; Goose calls its write-classifier *"best effort"*.
5. **Authority, domains and a non-overridable veto.** Every permission model found is a *user
   preference*, not an organizational entitlement.

# 11. REJECT — explicitly, with reasons
- **Servers and second orchestrators** — OpenHands agent-server, Letta's server + Postgres +
  embeddings. Same disqualifier as the prior pass; nothing here changes it.
- **Model-self-declared risk as a permission** (OpenHands `LLMSecurityAnalyzer`). Weaker than the
  authority matrix we already enforce, and it would regress our tool-honesty posture.
- **Regex-over-file-paths as the primary permission model** (Roo). Secondary control only — and
  #4732 shows it leaks without command parsing.
- **Per-tool-call checkpointing** (Cline classic). Their own regression is the evidence.
- **Re-executing replay** (SWE-agent `run-replay`) against a live repo. Take the read-only variant.
- **Deleting history on restore** (Cline "Restore Task Only"). We mark superseded; we never truncate.
- **Permissive defaults** (OpenCode). Invert them.
- **Mid-session self-widening of permissions** (Goose `/mode`). Rule 14.
- **A third configuration surface** (`.roomodes`, `opencode.json`, `.goosehints`). D-2 and D-14.
- **Third-party dependencies** — Pydantic, flake8, embeddings. `py_compile`/`ast`, `fnmatch`,
  `shlex`, `hashlib`, `sqlite3` cover every mechanism above.

# 12. THE ONE THING THE BEST HARNESSES DO THAT WE DO NOT
**They put the durability barrier inside the execution loop.** SWE-agent flushes the trajectory after
every step; OpenHands writes an immutable event file per event; Letta keeps the agent in the database
so there is no in-process state to lose; Goose moved sessions into SQLite. In all four the system
persists **because of how it runs**, not because an agent remembered to record something. Our
`harness.py checkpoint` is a command an agent may call, and in the one real mission we have run,
**several agents had no Bash tool and therefore never called it at all**. We have the better
*semantics* — evidence, refusal, independent review — attached to a loop that does not durably
record. Mechanism 1 fixes that, and mechanisms 2, 4, 5 and 7 all become nearly free once it exists.

---

# 13. LIMITATIONS OF THIS RESEARCH — stated, not hidden
- **Provider provenance: Tavily (`tvly search` / `tvly extract`) for discovery and extraction, with
  the official documentation site or repository read directly for every load-bearing claim. Exa was
  NOT used (unavailable this session). Brave was NOT used (token invalid — DEAD) and is cited
  nowhere.** The keyless Tavily cap did not exhaust during this pass.
- **Source code was read directly for exactly one project** (OpenHands `stuck_detector.py`).
  Everything else rests on official documentation, official issue trackers, or clearly-labelled
  secondary sources. Where a mechanism is attributed from a secondary source it carries `INFERENCE`
  and the reason.
- **Idempotency and stale detection are the weakest-evidenced questions**, because most projects do
  not document them. Where nothing was established the cell says `UNKNOWN`; mechanisms 4 and 5 are
  therefore **our design informed by their absence**, not a copy of proven prior art, and should be
  treated as `HYPOTHESIS` until tested.
- **One claim was verified by direct local measurement rather than citation:** SQLite FTS5 is
  available in this environment — `sqlite3.connect(':memory:').execute("CREATE VIRTUAL TABLE t USING
  fts5(x)")` succeeded on sqlite 3.51.0, Python 3.9.6, 2026-09-09. `FACT`.
- **Not studied for budget reasons:** Mastra, DeepAgents, PydanticAI. No claims are made about them.
- **This artifact has not been independently reviewed.** Rule 3 requires a reviewer who is not the
  author before any of these mechanisms is treated as an approved design. **Mechanism 3 (the blocking
  hook) additionally requires founder authorisation under rule 14, and mechanism "finish the
  `tasks.json` → DB consolidation" (§6c) is an escalation, not an adoption.**
