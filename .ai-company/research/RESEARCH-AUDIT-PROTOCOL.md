# RESEARCH AUDIT PROTOCOL

Before research becomes company knowledge, the Research Auditor checks it.

> **For Level 3 and 4 research, the auditor must not be the agent that produced the conclusion.**
> Self-audit is not audit.

## The checklist

| # | Check | Fails when |
|---|---|---|
| 1 | **Source validity** | A cited URL does not resolve, or does not say what is claimed |
| 2 | **Source authority** | A Tier 3 anecdote is carrying a Tier 1 conclusion |
| 3 | **Source freshness** | A HIGH-volatility claim is older than 30 days at decision time |
| 4 | **Citation accuracy** | The source is real but does not support the specific claim |
| 5 | **Primary-source usage** | A secondary summary was used where the primary was available |
| 6 | **Unsupported claims** | A statement carries no evidence record and no label |
| 7 | **Hallucination** | A statistic, citation, URL or figure cannot be traced to a source |
| 8 | **Circular sourcing** | "Three sources" are three republications of one press release |
| 9 | **Conflicting evidence** | A contradiction was found and quietly resolved in one direction |
| 10 | **Weak assumptions** | An assumption is load-bearing but unlabelled |
| 11 | **Stale information** | Superseded facts presented as current |
| 12 | **Confidence inflation** | A conclusion is more confident than its weakest input |

**Check 7 is terminating.** A fabricated citation invalidates the artifact — reject it and re-run
the research. Do not repair it in place.

## Verifying, not skimming

Spot-check by actually retrieving cited URLs and confirming they say what is claimed. An audit
that only reads the report cannot catch checks 1, 4 or 7 — the three that matter most.

## Conflict resolution

When sources disagree, **never silently pick the convenient number.** Record:

```markdown
## EVIDENCE CONFLICT: <the question>

**SOURCE A** — [S12], TIER 1, 2026-08-01 — claims: <value>
**SOURCE B** — [S19], TIER 2, 2026-05-14 — claims: <value>

**WHY THEY DIFFER**
<different definitions? different periods? different geography? one is stale? one is marketing?>

**MOST DEFENSIBLE CONCLUSION**
<which, and why — or "unresolved", which is a legitimate outcome>

**CONFIDENCE** — LOW / MEDIUM / HIGH
```

Significant contradictions are investigated, not averaged. Two conflicting numbers do not have a
meaningful midpoint.

## Audit verdicts

| Verdict | Meaning |
|---|---|
| **PASS** | Becomes company knowledge |
| **PASS WITH CAVEATS** | Usable; named claims downgraded in confidence |
| **FAIL — REMEDIATE** | Specific gaps must be filled and re-audited |
| **FAIL — REJECT** | Fabrication or fundamental unsoundness; re-run from scratch |

Write to `.ai-company/audits/research-<topic>.md`. Every verdict names the specific checks that
failed and the specific claims affected. **"Looks fine" is not an audit.**
