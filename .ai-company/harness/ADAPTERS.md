---
artifact: harness-extensibility
status: complete
retrieved: 2026-09-09
---
# Extensibility — adapter boundaries (directive §28)

Interfaces, not implementations. Nothing here adds a dependency. The point is that a future
integration does not require rewriting the harness.

| Boundary | Contract today | Swap target |
|---|---|---|
| **Agent runtime** | `PreToolUse:Task` → `autoregister` → execution row | direct spawn if `claude` reaches PATH; Agent SDK |
| **Model runtime** | `routing_outcomes.model` column, unused | per-model scoring in `route` |
| **Tool runtime** | `permit(role, tool, arg)` → ALLOW/DENY/APPROVAL | MCP servers; any tool with a name and args |
| **Workspace runtime** | `workspaces` table + git worktree | container/VM sandbox (E2B, Daytona) |
| **Persistence** | SQLite via `db()` / `_flush_db()` | Postgres — replace two functions |
| **Workflow backend** | `executions` + `events` + `checkpoints` | Temporal/Restate **only if** a server becomes justified |
| **Observability** | `events` table + `dash json=1` | OpenTelemetry exporter reading `events` |
| **Memory backend** | `context_bundles` + `lessons_h` | vector store behind `cmd_context` |
| **Approval backend** | `approvals` table, founder-only | Slack/email approval that writes the same row |

**Rule for any future adapter:** it plugs in *below* the harness or *beside* it. Anything that wants
to own decomposition, authority or task state is an orchestrator, and this company already has one.
