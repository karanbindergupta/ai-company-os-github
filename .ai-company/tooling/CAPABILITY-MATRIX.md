# CAPABILITY MATRIX

**Audit date:** 2026-09-07
Legend — **A**vailable · **M**issing · **D**uplicate · **R**equired now · Action taken

| # | Capability | Available | Missing | Duplicate | Required now | Action |
|---|---|---|---|---|---|---|
| 1 | Local git | ✅ git 2.50.1 | — | — | ✅ | None — present |
| 2 | Git **identity** (`user.name` / `user.email`) | ❌ | ✅ no `~/.gitconfig` | — | ✅ | **BLOCKER** — founder must set (P0) |
| 3 | GitHub repo/PR/issue access | ❌ | ✅ no MCP, no `gh`, no SSH | — | ✅ | **BLOCKER** — founder OAuth (P0) |
| 4 | Web research | ✅ `WebSearch` + `WebFetch` | — | — | ✅ | **Verified.** No search MCP installed — native is sufficient |
| 5 | Browser automation / QA | ✅ `Claude_Browser` | — | ⚠️ 3 stacks | ✅ | **Verified.** Playwright deliberately NOT added |
| 6 | Browser perf profiling | ✅ chrome-devtools MCP | — | — | ➖ | None |
| 7 | Filesystem access | ✅ native | — | — | ✅ | No filesystem MCP added — native suffices |
| 8 | Persistent company state | ✅ now | was ✅ | — | ✅ | **Created `~/code/ai-company` + `git init`** |
| 9 | Subagents / specialist "employees" | ✅ ~80 types | — | — | ✅ | None — roster already rich |
| 10 | Parallel execution | ✅ parallel tool calls + `Workflow` | — | — | ✅ | **Verified** in this session |
| 11 | Deterministic multi-agent workflows | ✅ `Workflow`, `enableWorkflows:true` | — | — | ✅ | None |
| 12 | Sequential workflows / handoffs | ✅ ECC `orch-*`, `pipeline()` | — | — | ✅ | None |
| 13 | Adversarial / review agents | ✅ GAN harness, santa-loop, `claude-security` | — | — | ✅ | Strengthened by install #21 |
| 14 | Scheduling / autonomous cadence | ✅ `scheduled-tasks`, `CronCreate`, `RemoteTrigger` | — | — | ✅ | **RemoteTrigger verified** (HTTP 200) |
| 15 | Skills system | ✅ ~320 skills | — | ⚠️ several lanes | ✅ | Documented; merges deferred to next phase |
| 16 | Hooks | ✅ ECC, 7 event types | — | — | ✅ | Untouched. GateGuard flagged |
| 17 | Dependency vuln scanning (Node) | ✅ `npm audit` | — | — | ✅ | **Verified** — caught GHSA-vh95-rmgr-6w4m |
| 18 | Dependency vuln scanning (other langs) | ❌ | ✅ no `uv`/`trivy`/`grype` | — | ➖ | Deferred — no non-Node project exists |
| 19 | Static analysis / SAST | ❌ → ✅ | was ✅ | — | ✅ | **Installed `claude-security` (P0)** |
| 20 | Secret detection | ⚠️ partial | ✅ no `gitleaks`/`trufflehog` | — | ✅ | `claude-security` + `ecc:security-scan` cover it; binaries blocked by no-Homebrew |
| 21 | Supply-chain / SBOM | ❌ | ✅ no `syft` | — | ➖ | Deferred (P2) |
| 22 | Database access | ✅ Supabase MCP + `sqlite3` | ⚠️ no `psql` | — | ➖ | None — no schema exists to inspect |
| 23 | Design / creative | ✅ Adobe, Cloudinary, v0, Miro, `design` skill, Artifacts | — | ⚠️ rich | ✅ | None — deliberately no new design MCP |
| 24 | Diagramming | ✅ Miro + native mermaid in Artifacts | — | — | ✅ | None |
| 25 | Document output (docx/pptx/xlsx/pdf) | ✅ `anthropic-skills:*` | — | — | ✅ | None |
| 26 | Node toolchain | ✅ node 24.18 / npm 11.16 | — | — | ✅ | None |
| 27 | Alt package managers (pnpm/yarn/bun) | ❌ | ✅ | — | ➖ | Install on demand via `npm -g` |
| 28 | Python toolchain | ⚠️ 3.9.6 system only | ✅ no `uv`, user-bin off PATH | — | ➖ | P1 — see blockers |
| 29 | Containers | ❌ | ✅ no Docker | — | ➖ | P1 — founder install |
| 30 | Cloud CLIs (aws/gcloud/az/vercel/wrangler) | ❌ | ✅ all | — | ❌ | P3 now — no deployment target |
| 31 | Observability (Sentry/analytics) | ❌ | ✅ | — | ❌ | P2 — documented in FUTURE-INTEGRATIONS |
| 32 | PM/comms tools (Linear, Notion, Slack, Figma…) | ⚠️ present but unauthorized | ✅ 14 servers | — | ➖ | **Founder OAuth** — see blockers |
| 33 | Java / Go / Rust / C++ toolchains | ❌ (`swift` ✅) | ✅ | — | ❌ | P3 — install per chosen stack |
| 34 | iOS build | ⚠️ simulator MCP present | ✅ full Xcode absent | — | ❌ | P3 unless mobile is chosen |
| 35 | Homebrew | ❌ | ✅ | — | ⚠️ | **Meta-blocker** — gates rows 20, 21, 22, 29, 30, 33 |

## Summary counts

- **Available and verified by execution:** 7 (research, browser, parallel, persistence, npm audit, npm toolchain, remote-trigger reachability)
- **Available, not exercised:** 18
- **Installed by this preflight:** 1 (`claude-security`)
- **Blocked on founder authorization:** 3 (GitHub, git identity, 14 PM connectors)
- **Deliberately skipped:** 9 (see `TOOLING-POLICY.md`)
