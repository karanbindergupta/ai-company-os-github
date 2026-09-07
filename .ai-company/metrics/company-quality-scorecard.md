---
document: company-quality-scorecard
version: 1.0.0
---
# COMPANY QUALITY SCORECARD

Scored per major project. **Passing technical tests is the floor, not the goal.**

Scale: **1** unacceptable · **2** below bar · **3** professional · **4** excellent · **5** exceptional.
**Any dimension at 1 or 2 blocks release** regardless of the average — a strong average hiding a
failing dimension is exactly what this scorecard exists to catch.

| # | Dimension | What "professional" (3) means | Scored by |
|---|---|---|---|
| 1 | Strategic quality | Differentiation stated and defensible, or absence stated honestly | cso |
| 2 | Customer value | Every feature traces to validated customer evidence | cpo |
| 3 | Product quality | Requirements met; reject list real; no scope drift | product-auditor |
| 4 | UX quality | Flows complete incl. error/empty/loading; task reachable in fewest sensible steps | ux-designer |
| 5 | Visual quality | Reads as one designed thing; every value from tokens | creative-auditor |
| 6 | Technical quality | Tested, reviewed, ADRs written, simplest sufficient design | architecture-auditor |
| 7 | Security | No unresolved critical/high; threat model current; fixes verified | ciso |
| 8 | Performance | Measured against budget, not asserted | performance-engineer |
| 9 | Accessibility | WCAG 2.2 AA verified by test, keyboard-complete | accessibility-tester |
| 10 | Financial viability | Unit economics close, or non-viability stated plainly | cfo |
| 11 | Operational readiness | Runbooks, rollback tested, alerts actionable | sre |
| 12 | Market readiness | Positioning evidenced; GTM has metrics defined pre-launch | cmo |
| 13 | Maintainability | An unfamiliar engineer can change it safely in six months | cto |

## Scoring rules
- Score against **evidence on disk**, not impression.
- The scorer must be **independent of the work** — no self-scoring.
- A dimension with no evidence scores **1**, not "not assessed".
- Record the score, the evidence path, and the single thing that would raise it one point.

## Template
```markdown
| # | Dimension | Score | Evidence | To raise one point |
|---|---|---|---|---|
| 7 | Security | 4 | .ai-company/security/posture.md | Automate the authz test suite in CI |
```

## Aggregate
Mean is reported but never used alone. Report: **mean, lowest dimension, and every dimension ≤2.**
The lowest score is the honest summary of the project.
