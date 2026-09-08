# AI Company OS

A **119-employee simulated organization** for Claude Code, with authority, separation of duties,
quality gates and behavioural rules **enforced in Python and SQLite rather than described in
prose**. You give it an industry and a rough idea; it does the research, strategy, product,
design, engineering, QA, security and audit work required to turn that into a real product.

**It is not a product. It is the company that builds products.** This repository contains no
application code.

> **The one rule that shapes everything else:** *observed behaviour beats declared capability.*
> Nothing here is GREEN because a config file exists. Maturity is earned, providers are probed,
> and `INSUFFICIENT EVIDENCE` is a complete answer.

---

## 1. What you get

| | |
|---|---|
| **119 role packs** | Every employee: authority, decision rights, artifacts, escalation, prohibitions |
| **19 executable subagents** | The officers Claude Code can actually dispatch |
| **11 departments** | Executive · Strategy & Research · Product · Creative · Engineering · Quality · Security · Growth · Operations · People · Commercial |
| **119 cognitive profiles** | Thinking style, instincts, **blind spots**, risk profile, evidence threshold, debate style, pressure and failure behaviour |
| **119 behavioural contracts** | The profile translated into observable, testable behaviour |
| **23-phase SOP + 13 gates** | A phase machine that *refuses* to advance on missing evidence |
| **53-table SQLite database** | One store. Authority, decisions, tasks, drills, evaluations, provenance |
| **20 mechanisms** | Python (stdlib only) — the enforcement layer, not documentation |
| **11 drills + automated rubrics** | Code scoring text. A model does not grade itself |
| **29 playbooks · 28 templates** | How each profession actually works |

## 2. Architecture

```
FOUNDER (L0, final authority)
   │  objective
   ▼
CEO ──► mission charter, department selection
   │
ORCHESTRATOR ──► task graph: owner + acceptance criteria + dependencies
   │
WORKFORCE ──► workforce.py assign  →  owner + INDEPENDENT reviewer (DB-enforced: owner ≠ reviewer)
   │
AGENTS ──► adopt a role pack, write an ARTIFACT to disk, record evidence
   │
GATES ──► assessed on evidence; phase-complete refuses without it
   │
FOUNDER ◄── decision packages only, never raw research
```

**Two kinds of agent.** Claude Code loads every subagent description into the parent context, so
only 19 exist. The other 100 specialists are **role packs** — a lead adopts one by reading
`.ai-company/org/roles/<department>/<role>.md`. This is how 119 specialists fit without collapsing
the orchestrator's context. *Never add a specialist by creating a new `.claude/agents/` file.*

**Artifacts, not conversation.** Agents communicate by writing files. This is what makes work
parallelizable, auditable and resumable.

### Executive structure
CEO, and reporting to them: COO · CTO · CFO · CPO · CMO · Chief Strategy · Chief Research ·
Chief Risk · CISO · Creative Director · Managing Director · Chief People Officer. Every one carries
a documented **blind spot** and a named counterbalance. **The CISO's release veto cannot be
overridden by the CTO or the CEO** — only the founder may accept a security risk.

Full detail: [`.ai-company/org/AI-EMPLOYEE-DIRECTORY.md`](.ai-company/org/AI-EMPLOYEE-DIRECTORY.md) ·
[`HIERARCHY.md`](.ai-company/org/HIERARCHY.md)

### Cognition and personality
Personality changes *what an agent notices, questions and challenges* — never whether it tells the
truth or respects authority. **Governance always wins over personality**, and there is a test for
it. No fake biographies, no roleplay.

### Intelligence and research
Evidence standard, source hierarchy, freshness policy, a provider router, and **provider
provenance**: the system records which provider was actually used and refuses to claim one ran
when it did not. Only a GREEN capability may be recorded as an actual provider.

### Memory
Organizational memory lives in the database plus `.ai-company/knowledge/`, `decisions/`,
`incidents/` and `research/sources/`. Run state in `.ai-company/state/` makes any mission
resumable after an interruption.

---

## 3. Requirements

- **Python 3.9+** — standard library only. **No third-party packages, no build step.**
- **git**
- **Claude Code** (desktop app, CLI, or IDE extension) to run the agents
- Optional: `npm` (dependency auditing), `uv` (Tavily CLI)

## 4. Install and run

```bash
git clone <your-fork> ai-company && cd ai-company
cp .env.example .env                          # fill in only what you have; none are required
cp .ai-company/org/FOUNDER.example.md .ai-company/org/FOUNDER.md
```

Bootstrap the two observed-state tables (they ship **empty on purpose**):

```bash
python3 scripts/intelligence.py capability    # live-probe every provider
python3 scripts/ci_report.py                  # run the 9 local gates, persist results
```

Then start a mission:

```bash
python3 scripts/company.py init "<industry>" "<your rough idea>" "<constraints>"
python3 scripts/company.py status
```

Inside Claude Code, `/company-start`, `/company` and `/company-resume` drive the same machine.

## 5. Validate the system

```bash
python3 scripts/readiness_audit.py        # 43 checks
python3 scripts/cognitive_validation.py   # 23 checks
python3 scripts/capability_validation.py  # 14 checks
python3 scripts/behavior_tests.py         # 35 checks  (run the bootstrap above first)
python3 scripts/audit_org.py              # organizational pathologies
python3 scripts/staffing_audit.py         # orphans, shadows, lone executives, SPOFs
bash    scripts/secret_scan.sh            # credential scan
```

Check authority is real:

```bash
python3 scripts/companydb.py can creative-director decide pricing   # exit 2 — denied
python3 scripts/companydb.py can cfo decide pricing                 # exit 0 — allowed
```

## 6. Extend it

- **Add a specialist** → write a role pack in `.ai-company/org/roles/<dept>/`, then
  `python3 scripts/sync_registry.py && python3 scripts/gen_memory.py`. Role packs are the source
  of truth; `roles.json` is a generated index.
- **Add a department** → update `departments`, then `matrices.py`.
- **Add a drill** → define it in `.ai-company/behavior/drills/` with a rubric; `behavior.py`
  scores it automatically.
- **Never hand-edit** `AI-EMPLOYEE-DIRECTORY.md`, `HIERARCHY.md` or `DRILL-CATALOGUE.md` —
  they are generated from the database by `gen_memory.py`.

## 7. Security

- **No agent may handle a credential.** `credential-handling` is `deny` for all 119, without
  exception. Agents tell you where a key goes; you put it there.
- `secret_scan.sh` blocks commits containing credential-length strings.
- Red-teaming is defensive only: this company's own product, non-production, never DoS, never
  third-party systems, never real user data.
- Destructive and outward-facing actions require explicit human confirmation — see §16 of
  [`CLAUDE.md`](CLAUDE.md).

## 8. Known limitations — read before trusting this

- **110 of the 119 agents have never been drilled.** Their behaviour is UNTESTED.
- **No agent has completed real, outcome-validated work.** Zero agents at maturity L5.
- **CI has never been observed running remotely.** `trusted_as_gate = 0`.
- All drill evidence is **synthetic** — responses scored by rubric, not live subagent runs.
- `behavior_tests.py` test 33 fails until the company performs real research that triggers a
  provider fallback. This is expected on a fresh clone.
- Three staffing gaps are deliberately open: `security-analyst`, `sales-lead`,
  `executive-operations`. Nothing has generated the work yet.
- The environment audit under `.ai-company/tooling/` describes **the machine this was built on**,
  not yours. Re-probe.

**Configuration completeness is not capability.** The system is built to say so, and so is this
README.

## 9. Implemented vs conceptual

See [`COMPANY_OS_MANIFEST.md`](COMPANY_OS_MANIFEST.md) for the full breakdown of what actually
runs, what is partial, and what exists only as specification.

## 10. Start here

[`CLAUDE.md`](CLAUDE.md) is the master operating document. Every agent inherits it. Read it before
changing anything.
