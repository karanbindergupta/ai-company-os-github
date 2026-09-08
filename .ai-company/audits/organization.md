---
artifact: organization-audit
role: agent-performance-auditor
phase: audit
status: complete
confidence: high
updated: 2026-09-07
---
# Organization Audit — dry run 2026-09-07

## Summary
The organization was run against a test mission (local food marketplace / home chefs) and audited
structurally. **32 defects found, 32 fixed, 0 remaining.** The defects were real: three of them
would have silently corrupted a live run.

## Method
1. Probed the enforcement paths directly (can the governance be talked around?)
2. Walked the phase machine on a real mission with real sourced research
3. Ran a structural audit of references, ownership, gates and the org graph

## Enforcement probes — all held
| # | Probe | Result |
|---|---|---|
| 1 | Complete a phase with a missing artifact | **Refused** |
| 2 | Start a phase whose dependency is incomplete | **Refused** |
| 3 | Mark a task done with no evidence | **Refused** |
| 4 | Assign a task to an unregistered role | **Caught by validate** |
| 5 | Pass the release gate without founder approval | **Refused** |
| 6 | Create a dependency cycle | **Caught by validate** |
| 7 | Fail the same task twice | **Anti-loop warning fired** |
| 8 | Group independent tasks for parallel dispatch | **Correct grouping** |
| 9 | Resume after simulated interruption | **State intact, correct next phase** |

## Defects found and fixed

### Critical — would have corrupted a live run
1. **Task ids reused after deletion.** Ids derived from `len(tasks)+1`. Deleting a task caused the
   next id to collide, silently rewiring another task's dependencies — observed producing a task
   that depended on itself. *Fixed:* ids are monotonic; self- and unknown dependencies are now
   rejected at creation.
2. **`gate_qa` shared by the `qa` and `retest` phases.** A pass during QA would have satisfied the
   retest phase, meaning remediation could ship unverified. *Fixed:* added `gate_retest` with its
   own criteria, including "no NEW defects introduced by the remediation".
3. **15 role packs reported to `chief-research-officer`**, which is not a registered slug (the slug
   is `cro-research`). Escalation from a third of the research organization pointed at nothing.
   *Fixed.*

### Structural
4. **No role owned the architecture audit.** The audit phase required
   `.ai-company/audits/architecture.md` and nobody produced it. *Fixed by hiring:* an
   **Architecture Auditor** was researched, specified and registered — reporting to the **Chief
   Risk Officer, not the CTO**, so it can genuinely audit the CTO's architecture. This exercised
   the HR hiring path end to end.
5. **Eight phase artifacts had no owning role.** *Fixed:* assigned to CEO, CTO, COO, QA Lead and
   Red Team.
6. **Duplicate role title "Brand Strategist"** across two departments. *Fixed:* renamed to Brand
   Strategy Lead (strategy) and Brand Application Lead (creative).
7. **A dangling task dependency** survived a deletion. Caught by `validate` — working as intended,
   recorded here as evidence the check earns its place.

## Organizational qualities checked
| Check | Result |
|---|---|
| Conflicting responsibilities | None — every role has one reporting line and distinct authority |
| Duplicate roles | One found and resolved |
| Circular delegation | None — reporting graph is acyclic |
| Unnecessary parallelism | None — parallel groups verified genuinely independent |
| Missing quality gates | One found (retest) and added |
| Broken commands | None — all 23 dispatch existing agents or roles |
| Agents asking the founder unnecessary questions | Escalation boundary defined in `CLAUDE.md` §6 and the `founder-escalation` skill |
| Context overload | Addressed structurally: 18 subagents, not 107 |

## Standing recommendation
Run `python3 scripts/audit_org.py` after **any** change to roles, phases, gates or commands. It
exits non-zero on any finding and is the cheapest defence against organizational drift.

## What the dry run could not test
Full multi-agent execution under real load — the enforcement layer and structure were verified,
but no phase has yet been executed by a fan-out of live subagents. **First real mission is the
true test.** Expect prompt-quality defects that a structural audit cannot see.
