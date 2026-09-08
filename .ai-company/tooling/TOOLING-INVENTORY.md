# TOOLING INVENTORY

**Audit date:** 2026-09-07
**Host:** macOS (Darwin 25.3.0), shell `zsh`
**Claude Code surface:** Claude Desktop app — "Code" tab. The `claude` CLI is **not** on PATH.
**Model:** Opus 5 (`claude-opus-5`)
**AI Company home:** `<REPO_ROOT>` (git-initialised during this preflight)

> This file lists what the environment **actually has**, verified by execution — not what it
> could have. Anything unverified is marked as such.

---

## 1. Claude Code native capabilities

| Capability | Status | Evidence |
|---|---|---|
| Filesystem read/write/edit/glob/grep | Available | Used throughout this audit |
| Bash execution | Available | Used throughout |
| Web search (`WebSearch`) | **Verified** | Live query returned Sept-2026-current results |
| Web fetch (`WebFetch`) | Available | Loaded; URL→markdown+extract |
| Subagents (`Agent` tool) | Available | 80+ agent types registered (see §4) |
| Deterministic multi-agent workflows (`Workflow`) | Available | `enableWorkflows: true` in settings |
| Parallel tool execution | **Verified** | Independent Bash/MCP calls batched in one turn, repeatedly |
| Skills | Available | 286 ECC + Anthropic + product-management skills |
| Slash commands | Available | 94 ECC commands |
| Hooks | Available & active | ECC registers 7 event types (see MCP-INVENTORY / PLUGIN-INVENTORY) |
| Artifacts (published HTML pages) | Available | `Artifact` tool with DB/assets/comments actions |
| Scheduled work (`CronCreate`, `scheduled-tasks` MCP) | Available | Not exercised |
| Remote routines (`RemoteTrigger`) | **Verified reachable** | `GET /v1/code/triggers` → HTTP 200, `{"data":[]}` |
| Session management (`ccd_session_mgmt`) | Available | list/search/message other sessions |
| Persistent project state | **Verified** | `~/code/ai-company` created + `git init` |

## 2. System toolchain

### Present

| Tool | Version | Path |
|---|---|---|
| git | 2.50.1 (Apple Git-155) | `/usr/bin/git` |
| node | v24.18.0 | `/usr/local/bin/node` |
| npm | 11.16.0 | `/usr/local/bin/npm` (prefix `~/.npm-global`, on PATH, **no sudo needed**) |
| npx | — | `/usr/local/bin/npx` |
| python3 | 3.9.6 (system) | `/usr/bin/python3` |
| pip3 | 21.2.4 | CommandLineTools framework |
| curl | — | `/usr/bin/curl` |
| jq | — | `/usr/bin/jq` |
| ripgrep (`rg`) | 14.1.1 | on PATH |
| make | — | `/usr/bin/make` |
| sqlite3 | 3.51.0 | `/usr/bin/sqlite3` |
| swift | 6.3.3 | `/usr/bin/swift` |
| Xcode CLT | `/Library/Developer/CommandLineTools` | **Command Line Tools only — no full Xcode** |

### Absent

`gh` · `brew` · `pnpm` · `yarn` · `bun` · `deno` · `uv`/`uvx` · `docker` · `docker compose` ·
`cmake` · `go` · `rustc`/`cargo` · **Java runtime** (the `java` shim exists but no JRE is installed) ·
`mvn` · `gradle` · `psql` · `mysql` · `redis-cli` · `aws` · `gcloud` · `az` · `vercel` ·
`wrangler` · `supabase` · `flyctl` · `netlify` · `terraform` · `kubectl` ·
`semgrep` · `gitleaks` · `trivy` · `trufflehog` · `syft` · `grype` · `playwright`

**The absence of Homebrew is the single biggest toolchain constraint.** Most macOS CLI security
and cloud tooling is distributed via Homebrew. Without it (and without sudo), the only credential-free
install channels available are `npm -g` (works, writes to `~/.npm-global`) and `pip3 --user`
(works, but writes to `~/Library/Python/3.9/bin`, which is **not on PATH**).

## 3. Global npm packages

- `@vudovn/ag-kit@2026.8.31` — pre-existing, not installed by this preflight, purpose not
  established. Flagged for founder review in `SETUP-BLOCKERS.md`.

## 4. Agent roster available to the orchestrator

Claude Code exposes ~80 registered subagent types today. Generic: `general-purpose`, `Explore`,
`Plan`, `claude`. Domain specialists (from ECC): architecture, code review per language
(TS/JS, Python, Go, Rust, Java, Kotlin, Swift, C++, C#, F#, PHP, Dart/Flutter, React, Vue, Django,
FastAPI), build-error resolvers per stack, security-reviewer, database-reviewer,
performance-optimizer, tdd-guide, e2e-runner, planner, code-architect, code-explorer,
marketing-agent, seo-specialist, a11y-architect, mle-reviewer, rag-pipeline-reviewer,
silent-failure-hunter, agent-evaluator, and the GAN generator/evaluator/planner trio.

**This roster already covers most of the engineering, QA, security and design "employees" the
AI Company OS was going to need.** The next phase should compose these, not re-create them.

## 5. Verification log

| Scenario | Test performed | Result |
|---|---|---|
| A — Research | `WebSearch` for 2026 Claude Code marketplace/security tooling | **PASS** — returned current, dated sources |
| B — GitHub | Full §4 capability sweep against a live repository (see below) | **PASS** — 9 of 10 points; Actions unavailable |
| C — Browser | `navigate` → `https://example.com` → `get_page_text` | **PASS** — page title and body text returned |
| D — Engineering | `npm install --package-lock-only` on a throwaway fixture | **PASS** — lockfile resolved |
| E — Security | `npm audit` on a fixture pinned to `minimist@0.0.8` | **PASS** — correctly reported 1 critical (GHSA-vh95-rmgr-6w4m prototype pollution) |
| F — Parallel work | Multiple independent Bash + MCP calls issued in single turns | **PASS** — used continuously during this audit |
| G — Persistent state | `mkdir ~/code/ai-company` + `git init` + this document tree | **PASS** |

Test fixtures were created in the session scratchpad, never in a project directory.


## 6. Scenario B — GitHub capability sweep (re-run after remediation)

Initially **FAILED**: no GitHub tool of any kind was reachable. After installing the plugin,
repairing the plugin cache and configuring a PAT, re-run 2026-09-07 against
`anthropics/claude-plugins-official` (read-only, public):

| §4 requirement | Result |
|---|---|
| 1. Detect existing integration | **PASS** — `plugin:github:github`, 46 tools |
| 2. Verify authentication | **PASS** — `get_me` → `<GITHUB_USER>` (account id redacted) |
| 3. Verify repository access | **PASS** — `get_file_contents` returned README.md |
| 4. Verify read permissions | **PASS** — file content retrieved at a pinned SHA |
| 5. Issues accessible | **PASS** — `list_issues` returned live issues, `totalCount: 1142` |
| 6. Pull requests accessible | **PASS** — `list_pull_requests` returned open PRs with head refs |
| 7. Branches inspectable | **PASS** — `list_branches` returned branches with SHAs and protection flags |
| 8. Commits inspectable | **PASS** — `list_commits` returned SHAs and URLs |
| 9. Repository metadata | **PASS** — full name and description returned |
| 10. GitHub Actions inspectable | **NOT AVAILABLE** — the plugin exposes no workflow/run tool among its 46 |

**Two documented limitations:**

- **No Actions/CI inspection.** There is no `list_workflow_runs` equivalent. If the AI Company OS
  needs CI visibility, that is a genuine gap — closing it means either the `gh` CLI (blocked on
  Homebrew) or a separate integration. Do not assume CI can be read today.
- **Repository search fails.** `search_repositories` with `user:<GITHUB_USER>` returns
  `Validation Failed`. Expected: the account currently has **0 repositories**, and fine-grained
  PATs are restricted on the search API. `list_*` tools work normally. Re-test once a repo exists.

### Write capability — deliberately not tested

Branch creation, commits, PR and issue creation were **not exercised**. The token grants them, but
testing would mean creating real objects on the founder's account, which the brief's "do not modify
the actual product unnecessarily" instruction rules out. Write access is configured and unverified;
first real use will confirm it.
