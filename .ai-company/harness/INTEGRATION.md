# Integration with the Company OS
```
COMPANY OS         company.py (SOP/phases/gates) · companydb.py (authority/vetoes/decisions)
MASTER ORCHESTRATOR decomposition, dispatch
────────────────────────────────────────────────────────────
EXECUTION HARNESS  harness.py + PreToolUse hook    ← records, permissions, refuses
────────────────────────────────────────────────────────────
CLAUDE CODE        Task tool, subagents, worktrees ← performs the work
```
**The harness never decides.** Authority stays in `companydb.py`; ask it "may X do Y?" and it answers.
The harness only refuses to let an answer go unrecorded.

**Task state:** `company.db` is authoritative. `tasks.json` is a `_DERIVED` read-only projection,
re-emitted on every write. `tasks-check` proves they have not diverged and exits 2 if they have.

**Reused, not rebuilt:** agents/roles registry · decision_rights · vetoes · escalations · risks ·
agent_performance · memory · knowledge graph · the 23-phase SOP · the 13 gates · CI.

**Deliberately unchanged:** `company.py`, `companydb.py`, the orchestrator, role packs, cognitive
profiles, the CISO veto, founder-required domains, GateGuard, D-1 (19 agent files), D-2 (one database).
