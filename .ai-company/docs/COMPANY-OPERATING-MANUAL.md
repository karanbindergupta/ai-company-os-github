---
document: company-operating-manual
version: 1.0.0
---
# COMPANY OPERATING MANUAL

## What this company is
An organization of **111 roles across 10 departments**, run by **19 executable subagents** that
adopt role packs, coordinated by an orchestrator, governed by a constitution, and held to account
by mechanisms that are **enforced in code rather than requested in prose**.

## The two engines

| Engine | Owns |
|---|---|
| `scripts/company.py` | The SOP phase machine — 23 phases, 13 gates, run state, resumability |
| `scripts/companydb.py` | Authority, vetoes, decisions, tasks, memory, risk, releases, recovery |

Both refuse illegal transitions. That refusal *is* the governance.

## A day in the company
```
founder: /company-start Industry: X. Idea: Y.
   -> orchestrator reads state, selects departments, decomposes work
   -> parallel groups dispatched in ONE message (concurrent)
   -> each agent adopts a role pack, writes an artifact, records evidence
   -> reviewers verify independently; gates assessed on evidence
   -> conflicts go to the CEO; dissent recorded verbatim
   -> founder sees only decision packages and approvals
```

## Enforcement — what the system refuses
| Attempt | Result |
|---|---|
| Complete a phase with a missing artifact | Refused |
| Mark a task done with no evidence | Refused |
| Mark done without verifying acceptance criteria | Refused |
| Mark done without independent review | Refused |
| Review your own work | Refused (DB constraint + runtime check) |
| Decide a domain you do not own | Refused |
| Decide while a veto is active | Refused |
| Decide without required reviewers | Refused |
| Veto a domain you hold no veto over | Refused |
| Lift someone else's veto | Refused |
| Ship with an unmet gate or no founder approval | Refused |
| Escalate to the founder with no recommendation | Refused |
| Create a dependency cycle | Caught by `verify` |
| Assign work to an unregistered agent | Refused |

## Daily commands
```bash
python3 scripts/companydb.py dashboard     # founder view
python3 scripts/companydb.py recover       # after any interruption
python3 scripts/companydb.py verify        # integrity
python3 scripts/company.py resume          # next phase in the SOP
python3 scripts/audit_org.py               # organizational drift
```

## Limitations, stated honestly
- **CI/GitHub Actions cannot be inspected** from this environment. The company never claims CI status.
- **No Homebrew** — Gitleaks/Trivy/Semgrep unavailable; coverage is `claude-security` + `npm audit`.
- **Brave is dormant** pending a key; Exa and Tavily provide the two independent indexes.
- **Exa keyless is ~150 calls/day** — a Level 3 fan-out can exhaust it. Route via Tavily or add a key.
- Multi-model routing is **organizationally** supported (roles/tasks are model-agnostic) but only
  Claude executes here today. No fake abstraction was built for models that cannot run.
