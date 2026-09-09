# Failure and recovery
**11 classes** → **3 retry-safety verdicts**:

| Safety | Classes | Behaviour |
|---|---|---|
| `SAFE_TO_RETRY` | TRANSIENT, DEPENDENCY, TOOL, CONTEXT | bounded retry within budget |
| `REQUIRES_RECONCILIATION` | SYSTEM, AGENT, LOGIC, CODE | reconcile side effects, then resume |
| `MUST_NOT_RETRY` | SECURITY, PERMISSION, HUMAN_REQUIRED | **escalate; resume refuses** |

**The load-bearing rule.** An operation *claimed* via `opkey` but never confirmed via `opkey-done`
may or may not have taken effect. `resume` **refuses** until it is reconciled. Recovery never guesses.

**Bounded retry (rule 11).** `retry_budget` defaults to 2. On exhaustion the execution goes
`BLOCKED` with: *"change the approach; do not repeat the failed action unchanged."*
