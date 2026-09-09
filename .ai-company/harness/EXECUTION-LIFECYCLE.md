# Execution lifecycle
```
QUEUED ──start──> RUNNING ──complete──> REVIEW ──> SUCCEEDED
                    │  ├── checkpoint (seq++, captures git HEAD)
                    │  ├── fail(class) ──> RECOVERING ──resume──> RUNNING
                    │  │                       └─(budget spent)─> BLOCKED
                    │  ├── fail(SECURITY|HUMAN_REQUIRED) ─────────> BLOCKED
                    │  └── lease expiry ──reap──> BLOCKED (ExecutionStale)
                    └── GLOBAL_PAUSE ──> every tool call DENIED
```
10 states, enforced by a DB `CHECK` constraint — an invalid status cannot be written even by raw SQL.

**Durability.** Every `emit()` opens `BEGIN IMMEDIATE`, writes one event, and `COMMIT`s. WAL +
`synchronous=FULL`. Durability is a property of the loop, not of an agent remembering to checkpoint.

**Completion bar is set by profile:**
| Profile | Evidence | Reviews | Founder approval |
|---|---|---|---|
| LIGHT | 1 | — | no |
| STANDARD | 1 | PEER_REVIEW | no |
| HIGH_ASSURANCE | 2 | PEER + SECURITY | no |
| CRITICAL | 3 | PEER + ADVERSARIAL + SECURITY + FINAL | **yes** |
