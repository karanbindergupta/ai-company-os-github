---
playbook: operations
version: 1.0.0
department: operations
---
# OPERATIONS PLAYBOOK — "How do we execute reliably?"

Operations converts strategy into reliable execution. Its product is **predictability**.

| Document | Covers |
|---|---|
| `README.md` | Operating system, health, resource allocation, failure modes |
| `SOP-FRAMEWORK.md` | The 12-field standard for any recurring process |
| `PROCESS-OPTIMIZATION.md` | Understand → simplify → standardize → automate |
| `LAUNCH-OPERATIONS.md` | Pre-launch through post-launch review |
| `RESILIENCE.md` | Fallbacks, recovery and vendor operations |

**Extends:** `docs/ORCHESTRATION-MANUAL.md`, `sop/phases.json`, `integrations/integration-matrix.md`,
`companydb.py task/recover`, `workforce.py health`.

## 1. How an operations professional approaches problems
Assume the plan is optimistic and the status report is generous. Your job is to find where work
actually stops — which is rarely where people say it does. **Surface bad news early**; a blocker
raised on day two is a scheduling question, on day twenty it is a crisis.

## 2. What operations owns
Workflows · SOPs · processes · resource coordination · execution coordination · bottleneck
removal · operational reliability · vendor coordination · internal tooling · documentation ·
launch operations · incident operations.

## 3. Standard workflow
1. Model the dependency graph before scheduling anything
2. Validate it — a cycle is a blocking defect
3. Identify what is genuinely parallel vs only apparently parallel
4. Assign owners **and independent reviewers**
5. Dispatch parallel groups in one message
6. Monitor: blocked, failed, stale, overloaded
7. Remove bottlenecks; reassign rather than letting work rot
8. Verify integration **by tests**, not by a clean merge
9. Review: what slipped, and why?

```bash
python3 scripts/companydb.py task graph      # dependencies
python3 scripts/companydb.py verify          # cycles, orphans, evidence-free 'done'
python3 scripts/companydb.py task ready      # dispatchable now, grouped
python3 scripts/workforce.py health          # overload and single points of failure
```

## 4. Operational health — what to watch
| Signal | Meaning | Action |
|---|---|---|
| Throughput | Tasks completed per phase | Falling → find the bottleneck |
| Cycle time | Start to done | Rising → work is too large or blocked |
| **Blocked age** | How long blocked | >1 phase → escalate, do not wait |
| Failure rate | Tasks hitting `failed` | Clustered → a systemic problem, not agent fault |
| **Rework** | Work redone after review | The most expensive signal; usually bad specification |
| Utilization | Load per agent | `workforce.py health` |
| Bottlenecks | Where work queues | Often a single over-relied-upon reviewer |

## 5. Resource allocation
Continuously determine: who is overloaded · who is idle · what is blocked · what can parallelize ·
what needs specialist expertise · where capability is missing.
```bash
python3 scripts/workforce.py health
python3 scripts/workforce.py assign capability=<x>
```
Coordinate with the orchestrator — **operations recommends the allocation, the orchestrator
dispatches.** A capability gap goes to the People department, not to a heroic reassignment.

## 6. Common failure modes
- **Optimistic status** — reporting intent instead of evidence
- **Late blocker disclosure** — the single most damaging operational habit
- **False parallelism** — dispatching backend and frontend before the API contract exists
- **Hero allocation** — routing everything to the best agent, creating a bottleneck and a SPOF
- **Automating a broken process** — now it fails faster and less visibly
- **Merge-as-integration** — a clean merge is not a verified integration

## 7. Quality checklist
- [ ] Every task has owner, criteria, dependencies, and a reviewer who is not the owner
- [ ] Dependency graph acyclic (`verify` passes)
- [ ] Parallel groups share no unresolved dependency
- [ ] Every blocked task has a named blocker and an owner
- [ ] Status reflects evidence, not optimism
- [ ] No agent is a single point of failure for a critical capability

## 8. Excellent vs unacceptable

**Excellent**
> "Phase `build` is 3 days late. Root cause: T0031 blocked 4 days on an unagreed API contract —
> backend and frontend were dispatched in parallel before the contract existed, which the plan
> gate should have caught. Contract agreed today; both streams resume. Preventive action: `verify`
> now fails a parallel group containing both a producer and consumer of an unagreed contract."

**Unacceptable**
> "Build is progressing well, a few tasks are taking longer than expected but we should catch up."
