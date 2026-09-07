# PROCESS OPTIMIZATION

> **UNDERSTAND → SIMPLIFY → STANDARDIZE → AUTOMATE**
>
> **Never automate a broken process.** You get the same failures, faster and less visibly.

## 1. Understand
Map what actually happens, not what the SOP claims. Where does work wait? Who touches it? Where
does it go backwards?

## 2. Simplify — before anything else
Look for: unnecessary steps · duplicated work · **bottlenecks** · manual work that exists only
because nobody removed it · unnecessary dependencies · single points of failure.

Ask of each step: **"what breaks if we delete this?"** If the answer is "nothing", delete it.
Most process improvement is deletion, not addition.

## 3. Standardize
Only once simplified. Write the SOP. Make the good path the easy path.

## 4. Automate
Only what is understood, simplified and standardized. Automate the **mechanical**, never the
**judgemental** — automating a decision that requires judgement produces confident wrong answers
at scale.

| Automate | Never automate |
|---|---|
| Validation, checks, state transitions | Decisions requiring domain judgement |
| Dependency and cycle detection | Gate assessment on ambiguous evidence |
| Report generation | Risk acceptance |
| Secret scanning | Anything founder-required |

## Bottleneck analysis
A bottleneck is where work **queues**, not where it is hardest. Common ones here:
- **One over-relied-upon reviewer** — the most frequent; fix with `workforce.py health`
- A gate with no clear owner
- A capability with no backup (a genuine SPOF)
- An agent looping on a failed approach — should have hit the anti-loop rule at two attempts

Removing a bottleneck usually moves it. Re-measure after every change.
