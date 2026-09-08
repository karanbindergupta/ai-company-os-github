# CURRENT STATE — read this second

**Snapshot date: 2026-09-08** · Generated at the end of the knowledge-preservation session.
Read [`CLAUDE.md`](CLAUDE.md) first. This file tells you *where we are* and *what to do next*.

---

## 30-SECOND SUMMARY

The **company is built and validated. The product is not started.** 119 employees exist with
enforced authority, cognitive profiles and behavioural contracts. One mission is live —
**medical tourism** — and it is **stopped at a founder decision**. Two things block progress:
the founder must pick a market position (ESC-002), and the GitHub repo must be created before
anything can be pushed.

---

## 1. WHAT IS BUILT AND WORKING

| | Status |
|---|---|
| 119 employees, 11 departments | ✅ COMPLETE |
| Every employee named, hierarchy verified | ✅ 0 orphans, 0 shadows, 0 SPOFs, 0 circular reporting |
| Authority enforced in code (`companydb.py can`) | ✅ WORKING |
| Separation of duties (owner ≠ reviewer, DB CHECK) | ✅ ENFORCED |
| 23-phase SOP, 13 gates, refuses to skip | ✅ WORKING |
| 119 cognitive profiles + behavioural contracts | ✅ COMPLETE |
| Drill engine + automated rubrics | ✅ WORKING (11 drills, 22 runs) |
| Capability probing, provider provenance | ✅ WORKING |
| CI pipeline (9 gates) | ⚠️ Executes **locally** only. Never run remotely |
| Full employee/hierarchy/drill documentation | ✅ Generated from DB by `scripts/gen_memory.py` |

**Validation suites — last run all passing:**
`readiness_audit.py` (43) · `behavior_tests.py` (35) · `cognitive_validation.py` (23) ·
`capability_validation.py` (14) · `staffing_audit.py` · `audit_org.py`

---

## 2. WHAT IS NOT BUILT

- **No product. No application code. No frontend, backend, database schema or deployment.**
- The medical tourism mission has not chosen a direction.
- 110 of 119 agents have **never been drilled** — their behaviour is UNTESTED.
- No agent has completed real, outcome-validated work. **Zero agents at maturity L5.**
- CI has never run on GitHub Actions. `trusted_as_gate = 0`.
- **Three staffing gaps remain open** and are reported every run by `staffing_audit.py`:
  `security-analyst` (CISO has no analyst for monitoring / vulnerability management) ·
  `sales-lead` (Sales is a single specialist with no lead) ·
  `executive-operations` (CEO has no ops support). These were judged **not yet worth hiring** —
  no mission has generated the work. Revisit when one does, per rule D-11 (reuse before hire).

---

## 3. ACTIVE MISSION — `run_73df81997a` — MEDICAL TOURISM

| | |
|---|---|
| Industry | Medical tourism |
| Idea | **NONE.** Founder supplied an industry and explicitly no idea |
| Constraints | Solo founder · pre-revenue · open on direction |
| SOP phase | `intake` — **0/23 phases formally completed** |
| Status | **BLOCKED on founder decision ESC-002** |

**Note on phase state:** discovery-level research was performed and written to disk, but the SOP
phase counter was never advanced past `intake` because the mission hit a founder decision first.
That is correct behaviour, not a bug. Do not mark phases complete retroactively.

### What the company found

1. **Medical tourism is a market for lemons.** Quality is unobservable at purchase; the failure
   surface (complication, revision, poor outcome) appears **18–36 months later**, so the price
   signal never propagates back. Bad providers are not punished by the market.
2. **The obvious entry — a facilitator or marketplace — is structurally misaligned.** Facilitators
   are paid per booking, so their incentive is volume, not outcome. Building the obvious thing
   means building the broken thing.
3. **The uncontested position is supply-side orchestration for mid-tier hospitals** — the
   hospitals with real capability and no international patient funnel.

### ESC-002 — OPEN, awaiting the founder

> **Company recommendation:** *Supply-side orchestration for mid-tier hospitals as the first move;
> it is validatable by a solo founder and is a route into the buy-side model.*

Options put to the founder:

| | Position | Company's view |
|---|---|---|
| A | Patient marketplace / facilitator | Structurally misaligned — RISK-003 |
| **B** | **Supply-side orchestration for mid-tier hospitals** | **RECOMMENDED** |
| C | Buy-side patient agent (paid by the patient) | Blocked on UNKNOWN: will patients pay? |
| D | Outcome registry / quality data layer | Slow, but attacks the actual root cause |

**Also needed from the founder:** target geography (corridor), and whether they have any personal
healthcare or hospital contacts — that changes which option is realistic for a solo founder.

### Open risks on this mission
| ID | Sev | Description |
|---|---|---|
| RISK-003 | HIGH | Facilitator/marketplace entry is structurally misaligned |
| RISK-004 | HIGH | Patient-safety and regulatory exposure as a facilitator — **NOT RESEARCHED** |

**Artifacts:** `.ai-company/mission/charter.md` · `.ai-company/mission/intake.md` ·
`.ai-company/research/industry.md` · `.ai-company/research/sources/index.md` ·
`.ai-company/decisions/founder/medical-tourism-position.md`

---

## 4. PREVIOUS MISSION — `run_63de3f6ebc` — REVOKED

Diaspora airline ticketing platform for Europe. **The founder revoked it** after the company found
the idea was already shipping: **BharatFare, launched December 2025**, same corridor, WhatsApp-first,
same neighbourhood expansion plan (RISK-002). The company also found the founder's premise was
wrong in a more interesting way — agent reliance is **structural (hidden net fares)**, not a UX
problem (RISK-001, ESC-001). The only genuinely uncontested axis found was **baggage-adjusted total
landed cost**.

**Lessons:** `.ai-company/knowledge/lessons-learned/diaspora-airline-revoked.md`
**This produced governance rule D-9: run the competitive scan before scoping anything.**

---

## 5. BLOCKERS — things a new session cannot fix alone

### 🔴 BLOCKER 1 — GitHub repo does not exist
The remote is configured (`https://github.com/karanbindergupta/ai-company.git`) but **nothing has
ever been pushed. 29+ local commits exist only on this machine.**

`create_repository` via the GitHub MCP returns **403** — the PAT is scoped to *"only select
repositories"* and lacks Administration permission.

**Founder must, manually:**
1. Create an **empty private** repo named `ai-company` at https://github.com/new
   (no README, no .gitignore, no licence)
2. Add that repo to the PAT's repository list — GitHub → Settings → Developer settings →
   Fine-grained tokens → the token → *Repository access*
3. Then:
```bash
cd ~/code/ai-company && git push -u origin main
```

Once pushed, GitHub Actions runs `ci.yml` and CI can finally be observed remotely.
**Until an actual remote run is seen, never claim CI passed.**

### 🟡 BLOCKER 2 — ESC-002 unanswered
The medical tourism mission cannot proceed without a position. See §3.

### 🟡 BLOCKER 3 — Brave API key invalid
`BRAVE_API_KEY` is set but a live query returns HTTP 422 `SUBSCRIPTION_TOKEN_INVALID`. Tools load;
the capability does not work. Founder should verify it at brave.com/search/api — likely not
activated, wrong plan, or copied with whitespace. **Research is unaffected** (Exa + Tavily +
native are GREEN).

### 🟡 BLOCKER 4 — OAuth-gated MCP servers
`exa` (plugin variant), Notion, Linear, Slack, Figma, Asana, Atlassian and the rest of the
product-management pack are **unauthorized**. They need authorization from the founder via
claude.ai connector settings or `/mcp` in an interactive terminal. The **direct Exa MCP endpoint
is GREEN and unaffected** — research does not depend on these.

---

## 6. WHAT TO DO NEXT

**If the founder answered ESC-002:**
```bash
python3 scripts/company.py resume
```
Record the decision, then dispatch the `orchestrator` agent. It owns decomposition, department
selection, parallel dispatch, gates and phase transitions from there.

**If the founder has not answered:** do not guess a position. Do not start building. Present
ESC-002 as a decision package and wait.

**If the founder wants to push to GitHub:** walk them through BLOCKER 1. Do not attempt
`create_repository` again — it is a token-scope problem, not a retry problem.

**If the founder wants more confidence in the organization:** the honest gap is that 110 of 119
agents are untested. Run drills:
```bash
python3 scripts/behavior.py drill <drill-id> <agent-slug>
```

---

## 7. HOUSEKEEPING FOR THE NEXT SESSION

**Uncommitted at the time of writing** (commit these):
`CLAUDE.md` (rewritten) · `CURRENT_STATE.md` (new) · `scripts/gen_memory.py` (new) ·
`.ai-company/org/AI-EMPLOYEE-DIRECTORY.md` · `.ai-company/org/HIERARCHY.md` ·
`.ai-company/behavior/DRILL-CATALOGUE.md`

**After changing any agent, role pack or profile, regenerate — do not hand-edit:**
```bash
python3 scripts/sync_registry.py && python3 scripts/gen_memory.py && python3 scripts/matrices.py
```

**Before any commit:**
```bash
bash scripts/secret_scan.sh
```

---

## 8. THE HONEST POSITION

State this plainly rather than overselling it:

> The organization is **built, internally consistent, and enforced in code** — authority,
> separation of duties, gates, provenance and rubrics all execute and all refuse when they should.
> Its behaviour is **evidenced for 9 agents and unproven for the other 110**. It has never
> completed real outcome-validated work, and its CI has never run remotely. Everything claimed
> here is verifiable by running the scripts in §9 of `CLAUDE.md`.

**Configuration completeness is not capability. Do not let this session, or any future one,
report the company as proven.**
