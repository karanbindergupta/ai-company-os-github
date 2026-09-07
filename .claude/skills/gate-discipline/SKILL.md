---
name: gate-discipline
description: How quality gates work and how to assess one honestly. Load before passing or failing any gate. Defines the evidence required, who may override what, and why passing a gate you know is unmet is the most damaging available action.
---

# Gate discipline

A gate is a promise that specific evidence exists. Passing one without that evidence corrupts
every decision downstream, and nobody finds out until much later.

## Assessing a gate
```bash
cat .ai-company/sop/gates.json     # the criteria - use these, not your judgement of "good enough"
python3 scripts/company.py gate <gate_id> pass|fail by=<role> note="..."
```

Read the criteria. Check each one against **evidence on disk**. A criterion you cannot verify is
not met.

## Failing a gate is normal and correct
The gate exists to catch incomplete work. Failing one is the system working. What is not
acceptable is passing a gate because:
- the run is taking a long time
- the founder seems impatient
- "it is probably fine"
- the missing evidence "will be produced later"

## Authority
- Each gate has an owner who assesses it.
- **`gate_security` carries the CISO's veto — not overridable by the CTO or CEO.** Only the founder
  may accept a security risk, and the acceptance is recorded against their name.
- **`gate_release` requires founder authorization.** The engine refuses it without a
  `founder_approval` value. Do not work around this.

## The phase engine enforces the rest
`phase-complete` refuses when required artifacts are missing, the gate is not passed, or tasks are
open. **If it refuses, it is right and you are wrong.** Do not edit state files to get past it -
that is falsifying the record.

## When a gate fails
Say specifically which criterion failed and what evidence is missing. Create remediation tasks.
Re-assess only after the evidence exists.
