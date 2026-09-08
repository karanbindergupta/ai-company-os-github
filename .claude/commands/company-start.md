---
description: Start a new company mission from an industry and a rough idea
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Founder input: **$ARGUMENTS**

## 1. Parse the input
Extract `industry`, `idea`, and any `constraints`. If the founder gave only a sentence, that is
enough — the company's job is to work out the rest. **Do not interrogate them with a questionnaire.**

If genuinely ambiguous (e.g. no industry at all), ask **one** clarifying question, not a list.

## 2. Initialize the run
```bash
python3 scripts/company.py init "<industry>" "<idea>" "<constraints>"
python3 scripts/company.py validate
```

## 3. Hand off to the orchestrator
Dispatch the `orchestrator` agent with the mission. It owns the run from here: decomposition,
department selection, parallel dispatch, gates, and phase transitions.

Tell the founder plainly:
- what the mission is, as the company understood it
- which phases will run before anything is built
- that they will be asked only for material decisions
- that `/company` shows status and `/company-resume` recovers an interrupted run
