---
name: decision-record
description: How to record a decision so the company never relitigates it. Load when making any material decision, ruling a debate, or writing an ADR. The rejected alternatives are the most valuable part.
---

# Decision records

Undocumented decisions get remade, differently, by whoever comes next. The rejected options matter
more than the chosen one.

## Format
```markdown
---
decision: <slug>
date: 2026-09-07
decided_by: <role>
status: decided | superseded | revisited
---
# Decision: <question>

## Context          — what forced a decision now
## Options considered
### Option A — <name>
Pros / Cons / Evidence
### Option B ...

## Decision         — what was chosen
## Rationale        — why, against the evidence
## Rejected         — each option, and the specific reason it lost
## Dissent          — who disagreed, and their argument, verbatim
## Consequences     — what this commits us to, including the bad parts
## Revisit when     — the condition that should reopen this
```

## Rules
- **At least two real options.** One option and a justification is not a decision.
- **Record dissent verbatim.** Never smooth it away. The dissenting view is often right later.
- **Name what would change your mind.** A decision with no falsification condition is a belief.
- **State the consequences you dislike.** A decision record listing only benefits is advocacy.

## Where
- Executive and business decisions → `.ai-company/decisions/`
- Architecture decisions → `.ai-company/architecture/decisions/`
