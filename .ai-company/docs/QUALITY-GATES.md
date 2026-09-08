# QUALITY GATES
13 gates in `.ai-company/sop/gates.json`, enforced by `company.py phase-complete`.
**Risk-scaled** — the orchestrator selects gates by risk, not ceremony:
| Change | Gates |
|---|---|
| Typo / copy | Review only |
| UI bug fix | Review + QA regression |
| New feature | Product, design, architecture, QA, security, performance, acceptance |
| Auth / data / payments | All gates + threat model + red team + founder approval |
**Definition of done:** acceptance criteria verified, evidence on disk, independent review passed.
All three checked in code. `gate_security` carries the CISO veto — not overridable by CTO or CEO.
`gate_release` refuses without recorded founder authorization.
