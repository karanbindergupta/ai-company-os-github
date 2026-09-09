# Observability
`harness.py dash` answers **"what is the company doing right now"** without reading raw logs.
`dash json=1` for machine consumption.

Reports: live executions with status/profile/agent/retries · success and blocked rates ·
tool-call and denial rates · sha256-verified evidence count · event count · exceeded budgets ·
outstanding leases · `GLOBAL_PAUSE` banner.

**Event log:** append-only, 28-term `CHECK`-constrained vocabulary, unique `(execution, seq)`,
`in_context` / `evicted_by_seq` so compaction flags rather than deletes. History is never rewritten.

**Metrics** (`harness_eval.py`): success rate · blocked rate · denial rate · evidence integrity ·
completions-without-evidence (must be 0) · recovery availability.
