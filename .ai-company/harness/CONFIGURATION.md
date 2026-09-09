# Configuration
**Hook:** `.claude/settings.json` → `hooks.PreToolUse` → `.claude/hooks/harness-pretooluse.sh`.
Composes with ECC GateGuard; both run, neither disables the other.

**Environment:** `HARNESS_ROLE` (default `orchestrator`) · `HARNESS_EXECUTION` (correlates calls).

**Policy** lives in `permission_rules` (DB), not in a config file — one authority, auditable, and
changes are timestamped. `harness.py rule list=1` to read it.

**Profiles** in the `profiles` table. **Budgets** at 5 scopes: execution, task, project, department, company.

**Deactivation:** remove the `PreToolUse` entry from `.claude/settings.json`. The ledger keeps working;
only enforcement stops.
