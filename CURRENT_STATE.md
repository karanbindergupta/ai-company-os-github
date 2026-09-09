# CURRENT STATE — read this second

**Snapshot: 2026-09-09** · end of the repository-canonicalization session.
Read [`CLAUDE.md`](CLAUDE.md) first. This file says *where we are* and *what to do next*.

---

## 1. WHERE WE ARE

Repository canonicalization is **complete locally**. Nothing has been pushed.

This working tree is the **single canonical source** for both the Company OS and the Execution
Harness. Five AI-Company copies existed on this machine; four are superseded (§5). The repository
now reconstructs itself from source, and runtime state is no longer canonical.

**The one thing left is a founder decision about publication (§7).**

---

## 2. ARCHITECTURE

```
FOUNDER (L0) -> EXECUTIVE COUNCIL (13) -> COMPANY OS -> MASTER ORCHESTRATOR
                                       -> EXECUTION HARNESS -> Claude Code / Task / tools
```

| | |
|---|---|
| Agents | **121** across 11 departments (was 119; Atlas added 2 strategy-research roles) |
| Cognitive profiles | 121/121 · behavioural contracts 121/121 |
| Decision domains | 29 · 11 founder-required |
| SOP | 23 phases · 13 gates |
| Harness schema | **v16** · one orchestrator · one authority engine · one task truth |
| Database | 81 tables at runtime; 53 declared in `schema.sql`; the rest from migrations |
| Language | Python 3.9, **stdlib only** |

---

## 3. TEST STATE

**Established runtime** (this working tree):

| Suite | Result |
|---|---|
| `readiness_audit` | **43/43** |
| `cognitive_validation` | **23/23** |
| `capability_validation` | **14/14** |
| `behavior_tests` | **35/35** |
| `audit_org` | **0 findings** |
| `harness_eval` (incl. self-red-team) | **45/45** |
| `harness_bench` | **15/15** |
| `companydb verify` · `harness verify` · `tasks-check` · `secret_scan` | PASS |

**Clean install from source** (verified in an isolated tree, four times):

```
agents=121  domains=29  cognitive=121  contracts=121
permission_rules=22  benchmarks=7  tables=81
executions=0  drill_runs=0  ci_runs=0
readiness 43/43 · cognitive 23/23 · capability 14/14 · audit 0 · eval 45/45 · bench 15/15
behavior_tests --clean-install: 19/35  BASELINE OK
```

**19/35 is correct, not a defect.** Sixteen checks require accumulated operational evidence
(drills, coaching, measured improvement, live provider probes). A fresh company has earned none.
`--clean-install` asserts that exact shape and fails **both** if something else breaks *and* if any
of the sixteen passes — the latter meaning evidence was fabricated. Proven in both directions by
injecting fake drill rows: the gate caught it.

---

## 4. WHAT CHANGED THIS SESSION

**Four permission defects, all found by test and closed:**

1. **Token-append bypass (critical).** `cat ~/.ssh/id_rsa; echo company.db` resolved to **ALLOW** —
   a later ALLOW matching any appended token lifted the private-key deny. Closed with *hard denies*
   (migration v14). Reproduced before the fix and guarded by `HD-PERM-003/004`.
2. **Shell-operator blindness.** `shlex` does not split on `;`/`&&`/`|`, so the filename token kept
   its trailing punctuation and an anchored pattern missed it. The resolver now splits on operators
   first (`HD-PERM-005`).
3. **Over-broad credential pattern.** It matched any string containing the substring, including
   `os.environ` in ordinary Python — it blocked the very migration that repairs it. Narrowed to
   filename patterns (v15), false positives guarded by `HD-PERM-006`.
4. **Ungoverned MCP surface.** Every `mcp__*` tool fell to the deny-biased default, so the whole
   surface was blocked wholesale — the weakest posture, since a blanket deny drives work outside
   the harness. Now governed (v16): read-only GitHub allowed, writes require founder approval,
   repository deletion is a hard deny, Supabase still denied by default.

**Reconciled from the public snapshot** (its PR #1 — work we did not have, found by it actually
running CI remotely):

- Provider checks no longer require `which tvly`, which would fail on any CI runner. Rather than
  swap a real check for a docs check (which weakens evidence, D-10), the check now prefers the real
  binary and **labels** which grade it saw: `VERIFIED` vs `CONFIGURED`.
- `ci_report.py --pre-behavior` generates genuine CI evidence before behavioural tests run.
- `LICENSE` (MIT), `FOUNDER.example.md`, and 6 `.gitkeep` files — without those the SOP writes
  `charter.md`, `pricing.md`, `positioning.md` and `discovery.md` into directories that do not
  exist on a clean clone.
- **Rejected:** the snapshot tracks `company.db`. That is the anti-pattern we removed.

**Schema correction.** Six tables previously excluded as "dead" are restored. That call was wrong:
`benchmarks` held **7 rows of authored configuration** a clean install was silently losing (now in
`seed.sql`), and omitting the rest left fresh installs at 47 tables against 54 for existing ones —
the exact drift `schema.sql` exists to prevent. `environment_changes` is declared but **never
seeded**: it holds a runtime observation, and seeding it would fabricate measurement.

**Second task write path closed.** `companydb.py task add` still wrote the tasks table directly,
leaving the projection stale — proven by test (`DIVERGENCE DETECTED`). An earlier remediation fixed
this in `company.py` and missed this one. Both now delegate to `harness.py`.

**Runtime/source separation.** `company.db`, `run.json`, `tasks.json`, `backup/`, WAL sidecars and
`logs/events.jsonl` untracked (index-only; **every file preserved on disk**), with ignore rules and
rationale. `schema.sql`, `seed.sql` and `archive/` are deliberately *not* ignored.

---

## 5. THE FIVE LOCAL COPIES

| Path | Verdict |
|---|---|
| **this worktree** (`~/code/ai-company`, branch `claude/review-project-architecture-87dcc7`) | **CANONICAL** — only copy with the harness, seed, bootstrap and fixes |
| `~/Desktop/airline` | Working copy of the public repo @ `3a4c1bf`, incl. merged PR #1. **Reconciled from, not deleted** |
| `~/code/ai-company-os-github` | Older clone of the same remote (1 commit). Superseded by the above |
| `~/code/ai-company-os` | Non-git duplicate of `main`. No unique content |
| `~/AI-Company` | **A different project** — an NDC/airline application (`src/ndc_adapter.py`, `pool_service.py`). Not an AI Company OS copy; left untouched |

**Nothing was deleted.** No candidate repository was modified.

---

## 6. GIT STATE

| | |
|---|---|
| Branch | `claude/review-project-architecture-87dcc7` |
| Base | `main` @ `2e1ff24` |
| Commits | 42 total; 12 ahead of `main` |
| Configured `origin` | `karanbindergupta/ai-company.git` — **404, does not exist** |
| Public repo | `karanbindergupta/ai-company-os-github` — public, MIT, 25 stars, 6 forks, `main` @ `3a4c1bf` |
| Shared history | **None.** No common ancestor |
| Pushed | **No. Nothing has ever been pushed from this repository.** |

---

## 7. NEXT STEP — FOUNDER DECISION REQUIRED

Local work is finished. Publication is blocked on a decision only the founder can make, because
**the canonical public destination is public and already has 25 stars and 6 forks**, and this tree
contains material the public snapshot deliberately excluded:

`.ai-company/knowledge/lessons-learned/atlas-compacted.md` names a real company
(**MyFlighty / S.C.A. Corporate Group SRL, Civitanova Marche**), records **founder testimony**
("the founder, who knows one of their founders, confirmed it"), states unverified allegations about
that company's commercial practices, and lays out the founder's own competitive wedge.

Publishing it would be **effectively irreversible** — public, forked, indexed.

**Options:**

| | Option | Effect |
|---|---|---|
| **A** | Publish the OS only — a curated export like the existing snapshot, mission material excluded | Safe, matches the snapshot's own stated policy and D-12 |
| **B** | Push this tree to a **new branch** on `ai-company-os-github` | Non-destructive to `main` and to forks, **but still public** — the content question stands |
| **C** | Create a **private** repository and push everything there | Preserves D-12; nothing sensitive becomes public |
| **D** | Replace `main` on the public repo | **Destructive.** Unrelated history, breaks 6 forks. Requires explicit founder authorization |

**Recommended: C for the full canonical tree, plus A for the public artefact.**

Also fix, whichever is chosen: the configured `origin` points at a repository that does not exist.

---

## 8. KNOWN LIMITATIONS

- **CI has never run on GitHub.** It passes in a locally simulated clean runner (no provider CLIs
  on PATH); no observed Actions result exists. Do not claim CI status.
- **No real mission has run under the harness.** Every test is a self-test. Maturity **L3**.
- **111 of 121 agents have never been drilled.**
- Sandboxing is macOS seatbelt, not a container.
- Brave API key returns 422; Homebrew absent (blocks gitleaks/trivy/semgrep/Docker).

---

## 9. TO RESUME

```bash
python3 scripts/company.py resume        # active mission, next phase
python3 scripts/companydb.py verify      # integrity
python3 scripts/harness.py verify        # ledger
python3 scripts/harness.py status        # executions
```

An Atlas mission run (`run_a2d1d5010d`) is still open in the state engine with `T023` failed. The
Atlas working set was deleted by founder instruction; what survives is
`.ai-company/knowledge/lessons-learned/atlas-compacted.md`. Do not reconstruct the deleted
artifacts — if Atlas restarts, start from that file and re-verify.
