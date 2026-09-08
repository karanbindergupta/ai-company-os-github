# SOP FRAMEWORK
Every **recurring** process gets an SOP. One-off work does not — an SOP for something done once
is bureaucracy.

## The 12 required fields
| Field | Why it exists |
|---|---|
| **Purpose** | If you cannot state it, the process may not be needed |
| **Owner** | One named role. Shared ownership is no ownership |
| **Inputs** | What must exist before starting |
| **Steps** | Numbered, unambiguous, executable without interpretation |
| **Decision points** | Where judgement is required, and who exercises it |
| **Tools** | With permission level from the integration matrix |
| **Outputs** | The artifact produced, at a named path |
| **Quality standard** | What "done correctly" means |
| **Failure modes** | What usually goes wrong here |
| **Escalation** | Who to go to, at which level |
| **Metrics** | How the process itself is measured |
| **Review date** | When to re-examine. An SOP with no review date rots |

```bash
sqlite3 .ai-company/state/company.db \
 "INSERT INTO sops(id,name,purpose,owner,steps,quality_standard,failure_modes,escalation,metrics,review_date,created)
  VALUES('SOP-001','...','...','coo','...','...','...','...','...','2026-12-01',datetime('now'));"
```

## When an SOP is warranted
| Warranted | Not warranted |
|---|---|
| Recurring, multi-step, multi-role | One-off work |
| Has failed before in a repeatable way | Fully covered by an existing gate |
| Consequences of error are material | Judgement-dominated creative work |
| Handed between agents | Already encoded in `companydb.py` |

**Do not write an SOP for something the code already enforces.** The release gate is not an SOP;
it is a refusal in `companydb.py release ship`.

## SOP quality
An SOP a competent agent cannot execute without asking a question is not finished. Test it by
having a different role follow it — the same test the People department uses for new role packs.
