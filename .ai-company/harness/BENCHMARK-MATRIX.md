---
title: Coding-Agent Harness Benchmark Matrix — mechanisms, not dependencies
artifact_type: research
status: in_progress
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
  tavily: status recorded inline per query
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
