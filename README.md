# AI Company OS

An autonomous multi-agent organization for Claude Code, plus the execution control plane beneath
it. The founder supplies an industry and a rough idea; the company performs the research, strategy,
product definition, financial analysis, competitive intelligence, creative direction, architecture,
engineering, QA, security and auditing required to turn it into a real product.

```
/company-start Industry: <industry>. Idea: <one line>.
```

**This repository is not a product. It is the company that builds products.** It contains no
application code — only the organization, its mechanisms, its memory, and the stdlib-Python tooling
that enforces its rules.

---

## Repository identity

| | |
|---|---|
| **Canonical local path** | `/Users/karan/code/ai-company` (branch work in `.claude/worktrees/`) |
| **Canonical for** | **both** the Company OS and the Execution Harness |
| **Public snapshot** | [`karanbindergupta/ai-company-os-github`](https://github.com/karanbindergupta/ai-company-os-github) — a *portable subset*, mission material removed |
| **`karanbindergupta/ai-company`** | **Does not exist.** The configured `origin` points at a repository GitHub returns 404 for |

The public snapshot and this repository have **unrelated git histories** (no common ancestor: 42
commits here from root `69cf0fd`, 5 there from root `d1fd3ab`). The snapshot is not an ancestor,
a fork, or a branch of this repository — it is a curated export. See §Publication below.

---

## Two systems, one repository

The **Company OS** governs. The **Execution Harness** executes.

```
FOUNDER -> EXECUTIVE COUNCIL -> COMPANY OS (authority, gates, vetoes)
                             -> MASTER ORCHESTRATOR (decomposition, dispatch)
  ------------------------------------------------------------------
  EXECUTION HARNESS   scripts/harness.py + PreToolUse hook
  ------------------------------------------------------------------
                             -> CLAUDE CODE / Task / subagents
                             -> tools, files, git, APIs
```

**Company OS decides** WHO, WHAT, WHY, authority, priority, dependencies, approvals, vetoes.
**The harness decides** HOW execution is controlled: permissions, evidence, checkpoints, retries,
recovery, execution state, verification, refusal, observability. **It never makes a decision the
Company OS owns.** There is one orchestrator, one authority engine and one task truth.

---

## What is here

| | |
|---|---|
| **121 role packs** | 11 departments, each a full job specification in `.ai-company/org/roles/` |
| **19 subagents** | `.claude/agents/` — isolated context, scoped tools; they adopt role packs |
| **28 commands** | `.claude/commands/` — founder-facing, wired to the state engine |
| **9 skills** | `.claude/skills/` — organizational discipline (evidence, gates, parallelism, failure) |
| **23 phases** | `.ai-company/sop/phases.json` — the SOP every mission follows |
| **13 gates** | `.ai-company/sop/gates.json` — enforced in code, not prose |
| **29 decision domains** | authority, reviewers, veto holders, founder-required flags |
| **121 cognitive profiles** | 23 fields each, including the load-bearing blind-spot field |
| **121 behavioural contracts** | the profile translated into observable behaviour |
| **24 mechanisms** | `scripts/` — stdlib Python 3.9, no third-party dependencies |
| **15 harness documents** | `.ai-company/harness/` — architecture through operations |

---

## Repository structure

```
CLAUDE.md            master operating document, inherited by every agent
CURRENT_STATE.md     where we are and the exact next step
README.md            this file
LICENSE              MIT
.github/workflows/   CI: 21 steps including a clean-install gate
.claude/             agents (19) · commands (28) · skills (9) · hooks · settings
.ai-company/
  org/               121 role packs, generated directory, hierarchy, roles.json
  constitution/      CONSTITUTION.md
  governance/        authority matrix, capability matrix, model routing
  cognition/         profile schema, personality and interaction matrices
  behavior/          drills, contracts, coaching, drill catalogue
  harness/           15 documents: architecture, security, operations, evaluation
  playbooks/         29 professional playbooks
  sop/               phases.json (23) · gates.json (13)
  state/             schema.sql · seed.sql · archive/   (company.db is NOT tracked)
  docs/              12 operating manuals
  research/ decisions/ risks/ knowledge/ incidents/ audits/ templates/
scripts/             24 mechanisms
```

---

## Installation

A clean checkout has **no database**. Reconstruct it from source:

```bash
python3 scripts/bootstrap.py
python3 scripts/companydb.py verify && python3 scripts/harness.py verify
```

`bootstrap.py` is the single canonical install path, in four steps:

1. `companydb.py init` — base schema (`schema.sql`) + 121 roles from the role packs
2. `seed.sql` — cognitive profiles, behavioural contracts, permission policy, decision rights,
   drills, benchmark scenarios, integrations
3. `harness.py migrate` — execution-harness schema, migrations v2+
4. `harness.py tasks-project` — emit the derived `tasks.json` projection

It is idempotent and safe to re-run. A clean install yields exactly:

```
agents=121  domains=29  cognitive=121  contracts=121
permission_rules=22  benchmarks=7  tables=81
executions=0  drill_runs=0  ci_runs=0     <- runtime evidence is ZERO, by design
```

Requires Python 3.9+ and sqlite3. **No third-party packages.**

---

## Source vs runtime

The repository must be reconstructable from source. Runtime state is never canonical.

| Tracked (source) | Ignored (runtime) |
|---|---|
| `state/schema.sql` — 53 base tables | `state/company.db` |
| `state/seed.sql` — non-reproducible configuration | `state/run.json`, `state/tasks.json` |
| `state/archive/` — frozen historical snapshots | `state/backup/` |
| migrations inside `scripts/harness.py` | `logs/*.jsonl` |

**`company.db` is runtime state and is reconstructable from source.** `tasks.json` is a *derived*
read-only projection; the database is the single authority. `harness.py tasks-check` proves they
have not diverged, and both `company.py` and `companydb.py` delegate every task write to
`harness.py` so a second write path cannot reappear.

---

## Testing

```bash
python3 scripts/readiness_audit.py        # 43 checks
python3 scripts/cognitive_validation.py   # 23 checks
python3 scripts/capability_validation.py  # 14 checks
python3 scripts/behavior_tests.py         # 35 checks
python3 scripts/audit_org.py              # structural audit of the organization
python3 scripts/harness_eval.py           # 45 checks incl. 12-class self-red-team
python3 scripts/harness_bench.py          # 15 representative scenarios
```

**On a fresh install `behavior_tests` scores 19/35, and that is correct.** Sixteen assertions
require accumulated operational evidence — drill runs, coaching, measurable improvement, live
provider probes. A newly bootstrapped company has earned none of it. Those sixteen are
**NOT YET PROVEN**, not failures, and must never be made green by seeding fabricated history.

`behavior_tests.py --clean-install` asserts that exact shape and fails **in both directions**: any
other check failing is a regression, and any of the sixteen *passing* means evidence was
manufactured. Both are hard errors. This is what CI enforces.

---

## Security model

Permissions are **deny-biased and last-match-wins**, evaluated by `harness.py` and enforced at
`PreToolUse` (composing with, not replacing, ECC GateGuard).

- **Bash is matched on the parsed command.** The resolver splits on shell operators before `shlex`,
  because a path pattern that ignores the shell is decorative (Roo-Code #4732).
- **Security denies are hard.** A `DENY` marked `hard` cannot be lifted by any later rule. Without
  this, appending one innocuous token that matched a later ALLOW defeated the credential and
  private-key rules outright — reproduced, then closed in migration v14.
- **Graduated failure.** A degraded harness falls back to **read-only**, not wide-open. The healthy
  policy is never narrower than the degraded fallback.
- **The MCP surface is governed, not blanket-denied.** Read-only GitHub lookups are allowed; writes
  require founder approval; repository deletion is a hard deny; everything else — Supabase
  included — remains denied by default.
- **Credentials are never handled.** `credential-handling` is `deny` for all agents; the founder
  places secrets personally.

```bash
python3 scripts/harness.py permit role=<role> tool=<tool> arg=<arg>   # 0 allow · 2 deny · 3 approval
sh scripts/secret_scan.sh
```

---

## Development workflow

```bash
python3 scripts/company.py resume        # active mission, next phase — run before continuing
python3 scripts/companydb.py dashboard   # company status
python3 scripts/companydb.py verify      # integrity
python3 scripts/harness.py status        # execution ledger
```

After any structural change, regenerate the derived documents and re-run the suites:

```bash
python3 scripts/sync_registry.py && python3 scripts/gen_memory.py && python3 scripts/matrices.py
```

`matrices.py` output is deterministic — byte-identical across runs and across a clean install.

**Never create a new `.claude/agents/` file to add a specialist; add a role pack** (decision D-1).

---

## Current maturity

**L3 — adversarially tested.** Not L4 (empirically validated) and not L5 (production-proven).

| Proven | Not proven |
|---|---|
| Clean install reproducible from source | No real mission has run under the harness |
| 43/43 · 23/23 · 14/14 · 35/35 on an established runtime | 110 of 121 agents have never been drilled |
| 45/45 harness eval, 15/15 benchmark | No agent holds outcome-validated maturity evidence |
| Permission bypasses found by test, then closed | CI has never executed on GitHub |
| Deterministic matrices, idempotent migrations | Every test is a self-test |

---

## Known limitations

- **CI has never run remotely.** The workflow passes in a simulated clean runner locally; no
  observed GitHub Actions result exists. The company will not claim CI status it has not seen.
- **No Homebrew**, so `gitleaks`, `trivy`, `semgrep` and Docker are unavailable. Dependency
  scanning is `npm audit` plus the `claude-security` plugin.
- **Sandboxing is macOS seatbelt**, not a container. It confines filesystem and network; it is not
  a VM boundary and does not defend against a kernel exploit.
- **The harness cannot spawn.** `claude` is not on PATH here, so spawns are captured by the hook at
  `PreToolUse:Task` rather than initiated by the harness.
- **Competitor harnesses were never executed.** `harness_bench.py` records every competitor as
  `NOT EXECUTED` with the specific blocking reason. No competitor score is estimated or invented.
- **No production validation.** Maturity is L3.

---

## Publication

This repository contains mission material — competitive intelligence, founder testimony about
named third parties, and business strategy. The public snapshot deliberately **excludes** that
category (see its `COMPANY_OS_MANIFEST.md`). Decision **D-12** stands: this repository defaults to
**private**, and what becomes public is a founder decision, taken per-file, not a mirror of this
tree.

Nothing here has been pushed to GitHub.

---

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — the operating constitution every agent inherits
- [`CURRENT_STATE.md`](CURRENT_STATE.md) — where we are and the exact next step
- [`.ai-company/harness/ARCHITECTURE.md`](.ai-company/harness/ARCHITECTURE.md) — the harness
- [`.ai-company/harness/SECURITY.md`](.ai-company/harness/SECURITY.md) — threat model and known bypasses
- [`.ai-company/docs/FOUNDER-GUIDE.md`](.ai-company/docs/FOUNDER-GUIDE.md) — how to use it
- [`.ai-company/org/AI-EMPLOYEE-DIRECTORY.md`](.ai-company/org/AI-EMPLOYEE-DIRECTORY.md) — all 121 employees

## License

MIT — see [`LICENSE`](LICENSE).
