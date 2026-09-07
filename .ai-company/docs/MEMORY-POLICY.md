# MEMORY POLICY
| Tier | Holds | Who may write | Expiry |
|---|---|---|---|
| `permanent` | Constitution, fundamental strategy, architecture principles | **CEO, founder, CPO-People only** (enforced) | never |
| `longterm` | Competitors, customers, market, historical decisions, experiments | Department leads | reviewed on volatility schedule |
| `working` | Current project, sprint, active tasks, live research | Any agent | ends with the project |
| `ephemeral` | Agent reasoning | Any agent | **not persisted** |
`memory put tier=permanent` refuses unless `actor=` is ceo, founder or chief-people-officer.
Every write increments a **version**; history is auditable via `audit_log`.
Contradictions are resolved by the owning role or flagged in `knowledge/contradictions.md` —
never left silently disagreeing. Do not store everything: ephemeral reasoning is noise.
