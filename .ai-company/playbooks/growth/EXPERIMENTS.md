# GROWTH EXPERIMENT FRAMEWORK

```
HYPOTHESIS → TARGET USER → BASELINE → CHANGE → EXPECTED EFFECT → METRIC
→ EXPERIMENT → RESULT → INTERPRETATION → DECISION → LEARNING
```

**Never call an experiment successful merely because a metric moved.**

## Before running — all of these, or do not run
- [ ] Hypothesis stated as a falsifiable prediction
- [ ] Target user segment defined
- [ ] **Baseline measured**, not estimated
- [ ] **Success threshold pre-registered** — the number that means "ship it"
- [ ] Minimum sample and duration decided in advance
- [ ] Confounds identified (seasonality, concurrent launches, channel mix shifts)
- [ ] Cost of running it

## Evaluating a result — six checks
| Check | Failure it catches |
|---|---|
| Statistical confidence | Noise read as signal |
| **Sample quality** | Wrong population — early adopters are not the market |
| Duration | Novelty effect; a lift that decays by week three |
| **Confounding variables** | A concurrent campaign did the work |
| Implementation errors | The variant never rendered for half the arm |
| **Segment differences** | Aggregate hides one segment improving, another collapsing |

## Interpretation honesty
- A result within noise is **inconclusive**, not "slightly positive"
- Moving the target after seeing data invalidates the experiment
- A negative result is a real result — record it; it stops the company retrying this
- If the metric moved but the mechanism is unclear, say so

```bash
python3 scripts/companydb.py experiment add hypothesis=".." metric=".." threshold=".." owner=<role>
python3 scripts/companydb.py experiment result id=EXP-0xx result=".." learning=".."
```
Template: `.ai-company/templates/experiment.md`

> **"We launched it" is not "we validated it."**
