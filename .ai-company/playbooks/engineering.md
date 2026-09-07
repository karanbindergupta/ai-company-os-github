---
playbook: engineering
version: 1.0.0
---
# Engineering Playbook

Operational, not motivational. Follow it.

## 1. How a professional approaches problems here
Write code an unfamiliar engineer can safely change in six months. That constraint - not cleverness - is what makes a codebase survive. Contracts before code is what makes parallel work possible at all.

## 2. Standard workflow
1. Confirm you have acceptance criteria, a solution design and an agreed API contract. If not, stop and request them
2. Write the failing test first, or alongside
3. Implement the smallest thing that satisfies the criteria
4. Handle the error path explicitly - validate at the boundary
5. Run the checks: tests, lint, types, build
6. Request independent review; never self-approve
7. Record evidence with the task update

## 3. Research methodology
Read the official documentation, not a blog summarizing it. For anything version-dependent, verify against the actual installed version rather than memory.

## 4. Decision frameworks
- **ADR** for any significant choice: context, options, decision, consequences, revisit trigger
- **Build vs buy** - what does this cost to maintain, not just to write?
- **Simplest sufficient design** - over-engineering is a defect the architecture auditor will flag
- **Reversibility** - prefer a change you can undo

## 5. Common failure modes
- **Silent error swallowing** - A bare catch that logs nothing. A defect, always.
- **Unilateral contract change** - Breaks the parallel workstream depending on it.
- **Untested completion** - 'Implemented' without verifying it runs.
- **Hard-coded design values** - A colour or spacing literal instead of a token.
- **Missing async states** - No loading, empty or error state in a view.

## 6. Quality checklist (run before submitting)
- [ ] Tests written and passing, covering the unhappy path
- [ ] Every input validated at the boundary
- [ ] No secret in code, committed config or logs
- [ ] Design tokens used - no literal colours or spacing
- [ ] Loading, empty and error states implemented
- [ ] An independent reviewer approved it

## 7. Deliverable templates
- `.ai-company/templates/technical-specification.md`
- `.ai-company/templates/architecture-decision-record.md`
- `.ai-company/templates/engineering-plan.md`

## 8. Review checklist (for whoever reviews this work)
- [ ] Does the test actually assert behaviour, or just that nothing threw?
- [ ] What happens when this external call times out?
- [ ] Is any error path unhandled or silently swallowed?
- [ ] Would a new engineer understand why this was built this way?

## 9. Escalation rules
L2 to your lead when the task cannot be completed as specified. L3 to the CTO when requirements conflict with the architecture. Never invent behaviour to unblock yourself.

## 10. Collaboration
Agree contracts with the consuming side before building. Route security findings to appsec. Give QA testability - ask for seams rather than letting them test around bad design.

## 11. Excellent vs unacceptable

**Excellent**
> 'Added POST /exports with a 30s timeout, retry-with-backoff, and a 413 on oversized requests. Tests cover success, timeout, malformed body and concurrent submission. Reviewed by code-reviewer; ADR-011 records why we stream rather than buffer.'

**Unacceptable**
> 'Implemented the export endpoint. Should work.'
