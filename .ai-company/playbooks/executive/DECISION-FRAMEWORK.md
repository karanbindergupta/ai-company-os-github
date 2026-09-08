# EXECUTIVE DECISION FRAMEWORK
The 17-step procedure for a major decision. **No major decision disappears into conversation.**

| # | Step | Mechanism |
|---|---|---|
| 1 | Define the decision as a question | Write it before analysing |
| 2 | Identify the responsible executive | `companydb.py authority <domain>` |
| 3 | Identify affected departments | Determines the review council |
| 4 | Gather evidence | Research Director; Level 3–4 for major decisions |
| 5 | Identify assumptions | Label each `ASSUMPTION`, never blur with `FACT` |
| 6 | Generate alternatives | Minimum two genuine options |
| 7 | Request independent executive analysis | Dispatch `executive` agents **in parallel, unseen by each other** |
| 8 | Identify disagreement | Where do positions actually diverge? |
| 9 | Debate | Factual disputes → research. Assumption disputes → compare assumptions |
| 10 | Identify risks | `companydb.py risk add` with a named owner |
| 11 | Determine reversibility | Easy / Moderate / Difficult / Irreversible |
| 12 | Determine required authority | Founder-required domain? Active veto? |
| 13 | Make the decision | `decision decide` — refuses if reviewers missing or vetoed |
| 14 | Record it | Options, rejected, risks, confidence, dissent |
| 15 | Assign execution | Task with owner, criteria and independent reviewer |
| 16 | Define the review trigger | The condition that reopens this |
| 17 | Measure the outcome | Predicted vs actual, into lessons-learned |

```bash
python3 scripts/companydb.py authority <domain>
python3 scripts/companydb.py decision new domain=.. owner=.. title=".." options=".." rejected=".."
python3 scripts/companydb.py decision dissent id=DEC-0xx role=.. position=".." argument="<verbatim>"
python3 scripts/companydb.py decision approve id=DEC-0xx role=<each required reviewer>
python3 scripts/companydb.py decision decide id=DEC-0xx role=<owner> decision=".." [founder_approval=".."]
```

## Reversibility governs speed
| Class | Posture |
|---|---|
| Easy | Decide fast, learn from it |
| Moderate | Normal process |
| Difficult | Full council, adversarial review |
| **Irreversible** | **Founder decision by construction** — constitution §XIX prefers reversible under uncertainty |

## The absence-of-dissent check
If nobody dissented on a genuinely hard question, the question was not examined. Ask each
executive: *"what would have to be true for you to be wrong?"* A council that cannot answer that
has rubber-stamped, not decided.
