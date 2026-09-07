---
document: ai-company-empirical-readiness-report
version: 1.0.0
date: 2026-09-07
---
# AI COMPANY EMPIRICAL READINESS REPORT

> **OBSERVED BEHAVIOUR > DECLARED CAPABILITY.** Nothing below is inflated. Where evidence is
> absent, the entry says so.

## Two corrections to the specification's premises

The spec asserted two states that **live probes contradict**. Implementing them as written would
have created exactly the dishonesty this layer exists to prevent.

| Spec said | Verified reality | Action |
|---|---|---|
| §18 "Exa … no usable key/credential, availability = UNAVAILABLE" | **Exa returns HTTP 200 on the anonymous tier and works.** `EXA_API_KEY` is unset but not required | Recorded `OPERATIONAL_ANONYMOUS_TIER` / **GREEN** |
| §20 "CI exists but is uninspectable" | **No CI exists at all** — 0 workflow files, no `gh`, no Actions tool among 46 GitHub MCP tools | Recorded `NOT_CONFIGURED` / **GRAY**, not `UNOBSERVABLE` |

**Brave** is the capability that is actually configured-without-a-credential (YELLOW).

## A. Implemented
11 new tables in the **existing** company database (no parallel store). `scripts/intelligence.py`:
evaluations with 12 behavioural dimensions · longitudinal performance · evidence-based maturity ·
drift alerts · 4-stage lesson validation · live capability probes · provider provenance ·
intelligence report. 7 versioned benchmarks. 7 capabilities mapped for playbook coverage.

## B. Tested mechanically — 20/20 after one fix
Refusals verified: self-evaluation · promotion without evidence · MAJOR drift on n=1 ·
applying an unvalidated lesson · silent provider substitution · **claiming a non-GREEN provider
actually ran**.

**Defect found by test 13 and fixed:** the provider guard blocked RED/GRAY but not YELLOW, so an
agent could have claimed Brave ran when Brave has no key. Now only a **GREEN** capability may be
recorded as the actual provider. Retested in all four directions.

## C. Tested behaviourally — barely
| Exercise | Result |
|---|---|
| Live research through Tavily (keyless) | **PASS** — retrieved concrete, dated CAC benchmarks |
| Evaluation of that retrieval | **72/100**, n=1, **INSUFFICIENT EVIDENCE** |

The evaluation's own finding: the retrieval used **Tier 2/3 aggregators only**, did not reach a
primary source, and was not triangulated — the circular-sourcing pattern the research
constitution warns about. Availability was satisfied; the evidence standard was not.

## D. Untested
Every executive cognitive model. All 111 agents' actual reasoning. Panel behaviour with live
subagents. Whether the CFO genuinely challenges economics. Whether the CEO synthesizes rather
than dominates. `claude-security` has never run a scan.

## E. Maturity evidence
**n=2 evaluations across 111 agents.** All maturity verdicts return `INSUFFICIENT EVIDENCE`.
No agent has been promoted. No agent is at L5.

## F. Drift status
1 MAJOR alert raised on a synthetic fixture (n=2). **No profile was modified** — investigation
precedes recalibration. Automated scan found no candidates: correct, since there is almost no
observed behaviour to compare against.

## G. Learning
1 VALIDATED_LESSON (promoted through OBSERVATION → HYPOTHESIS → VALIDATED via independent
confirmation), 1 OBSERVATION. Applying an unvalidated lesson is refused.

## H. Playbook coverage
7 capabilities mapped. 3 flagged **MEDIUM duplication risk / keep_shared_monitor**: marketing,
analytics, QA — QA in particular has a distinct adversarial method that may warrant its own
playbook once real usage shows whether sharing causes ambiguity.

## I–K. Infrastructure — 7 GREEN of 17
| Capability | Status |
|---|---|
| exa · tavily · websearch · git · github · npm_audit · secret_scanning | **GREEN** — probed |
| brave | YELLOW — `CONFIGURED_BUT_CREDENTIAL_MISSING` |
| claude_security | YELLOW — `INSTALLED_NEVER_EXERCISED` |
| homebrew | YELLOW — `ABSENT_NO_ACTION_REQUIRED` (per §21) |
| ci | **GRAY — `NOT_CONFIGURED`, `trusted_as_gate=0`** |
| logs · metrics · traces · errors · static_analysis · container_scanning | GRAY — deliberately deferred, no product to instrument |

## L. Remaining weaknesses — honest
1. **n=2.** Nothing here supports a conclusion about any agent's quality.
2. **Self-evaluation problem.** One model authored the agents, the scenarios *and* the scores.
   `evaluator_independent=1` is structurally true (different role) but not epistemically
   independent. **Genuine independence needs live subagents or the founder.**
3. **Drift detection is largely inert** without observed behaviour to compare against.
4. **Benchmarks are unleaked but also unvalidated** — nobody has confirmed they discriminate
   between good and bad reasoning.
5. **CI cannot become a quality gate** without both workflows and `gh`, and `gh` needs Homebrew.

## M. Recommended next action
**Run a real mission.** The layer is installed and mechanically sound; it is now the *measuring
instrument*, and it has nothing to measure. Every remaining gap closes only with real work.
