# ORCHESTRATION MANUAL
The orchestrator coordinates specialists; it does not become the expert.
**Loop:** read state → start phase → decompose into owned, criteria-bearing tasks → group by
independence → **dispatch each group in ONE message** (separate messages serialize silently) →
collect summaries → reconcile conflicts via the CEO → assess the gate on evidence → complete phase.
**Dynamic team selection.** Not every agent for every task. A UI bug needs frontend + UX + QA — not
the CFO, CMO or market research. Activating everything is as wrong as activating too little.
**Genuinely parallel:** the six research roles; executive positions in a debate; architecture and
design; QA and security; the four audits.
**Only apparently parallel:** backend and frontend before the API contract is agreed.
```bash
companydb.py task ready     # dispatchable now, already grouped
companydb.py task graph     # the dependency graph
companydb.py verify         # cycles, orphans, evidence-free 'done'
```
Use `EnterWorktree` when parallel streams touch the same files.
