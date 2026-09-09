---
artifact: harness-operating-principles
status: canonical
---
# The harness's operating principles

Not a character. Not a personality. A **policy stance**, expressed in code and refusals.
Every line below is enforced somewhere in `scripts/harness.py`, and the enforcement is named.

| Principle | Where it is real |
|---|---|
| **EVIDENCE BEFORE CLAIM** | `complete` refuses without sha256-verified evidence; a nonexistent path is refused outright |
| **SAFETY BEFORE SPEED** | Deny-biased permissions: anything not explicitly allowed is denied |
| **AUTHORITY BEFORE AUTONOMY** | `approve` is founder-only; `control` is founder-only; agents cannot self-authorise |
| **VERIFICATION BEFORE COMPLETION** | Profile gates: `CRITICAL` needs 3 evidence items, 4 review modes and founder approval |
| **RECOVERY BEFORE RETRY** | `recover` classifies retry-safety before `resume` is permitted |
| **CLARITY BEFORE ACTION** | Every refusal names the rule and the remedy, never just "denied" |
| **MINIMUM NECESSARY PRIVILEGE** | Rules are per-role, last-match-wins; the CEO has a *stricter* push rule than a developer |
| **STOP WHEN UNCERTAIN** | Unconfirmed side effects block resume rather than risk a double-apply |
| **LEARN FROM FAILURE** | `lesson` promotes only on repetition: OBSERVATION → CANDIDATE → REPEATED → VALIDATED |
| **NEVER HIDE FAILURE** | The event log is append-only; compaction flags `in_context=0`, it never deletes |
| **NEVER FABRICATE EVIDENCE** | Claim-only evidence is stored `verified=0` and **cannot** complete an execution |
| **NEVER SELF-AUTHORISE** | Red-team A4: an agent granting itself approval exits 2 |
| **NEVER CONFUSE ACTIVITY WITH PROGRESS** | Completion requires evidence and review, not tool calls |
| **NEVER OPTIMIZE COST OVER CORRECTNESS** | Routing score weights success 0.60, cost 0.05 |
| **NEVER OPTIMIZE AUTONOMY OVER CONTROL** | `GLOBAL_PAUSE` halts everything and only the founder lifts it |
