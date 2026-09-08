# OPERATIONAL RESILIENCE

**No critical operation depends on one fragile step without a recovery strategy.**

## Every critical process needs
| Requirement | Test |
|---|---|
| **Fallback** | What runs if the primary fails? |
| **Recovery procedure** | Written, and actually executed at least once |
| **Owner** | One named role |
| **Escalation** | Who, at which level |
| **Backup capability** | A second agent who can do this — `workforce.py health` |

## Known fallbacks in this company
| Primary | Fallback | Status |
|---|---|---|
| Exa (research) | Tavily, then native WebSearch | Verified |
| Tavily (extraction) | Exa, then WebFetch | Verified |
| Brave (independent index) | Exa + Tavily as the two independent checks | Dormant — documented |
| GitHub | Local git | Available |
| Supabase | Local sqlite for development | Available |
| Any agent | Named backup role | 16 critical roles covered |
| Interrupted session | `companydb.py recover` | Verified from a cold process |

## Vendor and tool operations
Tracked in `integrations/integration-matrix.md`: vendor · purpose · cost · owner · dependency ·
permissions · security class · fallback · rate limit · status · health.

**Avoid tool sprawl.** Constitution and tooling policy both require the seven gates before adding
anything. Every tool is a dependency, a permission surface and a thing that can fail.

Review triggers: a tool fails · cost changes materially · a credential expires · a cheaper or
safer equivalent appears · **the tool has not been used in a full mission cycle** — unused tools
are removed, not kept "just in case".

## Recovery drill
Periodically verify recovery actually works rather than assuming:
```bash
python3 scripts/companydb.py recover
python3 scripts/company.py resume
python3 scripts/companydb.py verify
```
This was validated in Phase 3 from a process with no conversation memory. **Re-run it after any
change to the state engine** — a recovery path that is never exercised is a recovery path that
does not work.
