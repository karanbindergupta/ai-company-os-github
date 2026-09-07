# EXECUTIVE COUNCIL SESSIONS
Five session types. **Never merge them** — a strategic review that drifts into execution triage
accomplishes neither.

## 1. Strategic Review
Mission · current objective · progress against success criteria · opportunities · threats ·
financial position · product status · customer signals · growth · technology · security ·
operational health · major risks.
```bash
python3 scripts/companydb.py dashboard
python3 scripts/workforce.py health
```
Output: a written position on whether the mission still holds.

## 2. Decision Session
**Only decisions requiring executive attention.** Anything a department lead can decide is
returned to them — appearing here is itself a finding.
Run the 17-step framework. Nothing leaves undecided or with an explicit next step and a date.

## 3. Debate Session
**Only issues with genuine disagreement.** Each executive files independently first
(`decisions/positions/<role>.md`), *then* they meet. Meeting first produces anchoring, not debate.
The CEO rules and names which argument lost and why.

## 4. Execution Review
What is blocked? What is late? What needs resources?
```bash
python3 scripts/companydb.py task list status=blocked
python3 scripts/companydb.py task list status=failed
python3 scripts/workforce.py health
```
The COO owns this. Escalate scope, never absorb it silently.

## 5. Learning Review
What did the company learn? Which prediction was wrong? Which process failed?
Write to `.ai-company/knowledge/lessons-learned/`. **A lesson becomes doctrine only after review** —
one observation is not a rule.

## Cadence
Strategic per mission or when evidence shifts · Decision on demand · Debate only on real
disagreement · Execution at each phase boundary · Learning at phase completion and after incidents.
