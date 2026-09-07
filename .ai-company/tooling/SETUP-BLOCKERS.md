# SETUP BLOCKERS

Actions that **genuinely require the founder**. Everything else in this preflight was completed
autonomously. No secrets, tokens or credentials were requested, printed, stored or committed.

---

## P0 — blocks the AI Company OS from functioning

### 1. GitHub is not connected to this Claude Code session

**You told me GitHub was already connected via connectors. I verified that carefully, and in this
local desktop session it is not reachable.** Three independent checks:

| Check | Result |
|---|---|
| Tool search for `+github` across all deferred tools | No GitHub tool in the manifest |
| `mcp-registry search_mcp_registry(["github","repository","pull request","git"])` | `{"results": []}` |
| `mcp-registry list_connectors()` | `{"connectors": []}` |
| `command -v gh` | not found |
| `~/.ssh` | does not exist |
| `~/.gitconfig` | does not exist |

For comparison, your other connectors **do** surface here as MCP servers (Miro, Cloudinary,
Supabase, Adobe Express, v0). A GitHub connector would appear the same way. It does not.

**The most likely explanation:** the GitHub connection you made is at the **claude.ai account
level for Claude Code on the web / cloud sessions** (the repo picker and routines), which is a
different integration from a desktop MCP connector. It genuinely exists — it just is not exposed
to this local session's tools. (`RemoteTrigger` reached `/v1/code/triggers` with HTTP 200, so your
account auth is healthy; there are simply no routines and no local GitHub tool.)

**Fix — enable the official GitHub plugin.** The marketplace is already registered locally:

```bash
claude plugin install github@claude-plugins-official
```

Run it in an **interactive** terminal (`claude`) and complete the OAuth prompt — this session is
non-interactive and cannot run an OAuth flow. Then confirm with `/mcp`.

Do not add a second GitHub integration; this one covers repos, branches, commits, PRs, issues,
code review and Actions.

### 2. Git has no identity — commits will fail

There is no `~/.gitconfig` at all. **Verified during this preflight:** `git commit` in the new
`~/code/ai-company` repo failed with `Author identity unknown`. The preflight documentation is
staged but **cannot be committed** until this is set.

You asked me to verify the GitHub connection rather than set this, so **I did not set it.**
When you're ready, substituting the name you want on commits:

```bash
git config --global user.name "Karan" && git config --global user.email "kewalsingh99990@gmail.com"
```

### 3. No SSH keys

`~/.ssh` does not exist. Not required if you use the GitHub plugin over HTTPS/OAuth, but `git push`
over SSH will fail. Only act on this if you want SSH remotes.

---

## P1 — materially improves the environment

### 4. Homebrew is absent — this is the meta-blocker

Without Homebrew (and without sudo available to me) most macOS developer tooling cannot be
installed. It currently gates: `gh` as a CLI, `gitleaks`, `trivy`, `grype`, `syft`, `trufflehog`,
`psql`, Docker, Go, Rust, cloud CLIs, and full language toolchains.

Installing it requires your password, so **I cannot run it**:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Two workable channels do exist without it, and I confirmed both: `npm install -g` (writes to
`~/.npm-global`, already on PATH, no sudo) and `pip3 install --user`.

### 5. Fourteen product/comms connectors are unauthenticated

`amplitude` · `amplitude-eu` · `asana` · `atlassian` · `clickup` · `figma` · `fireflies` ·
`intercom` · `linear` · `monday` · `notion` · `pendo` · `similarweb` · `slack`

`~/.claude/mcp-needs-auth-cache.json` shows failed auth probes for 12 of these dating to
2026-08-31. Authorize only the ones you will actually use — each is a standing data-access grant.
For an AI Company OS the highest-value ones are **Linear or Asana** (work tracking),
**Notion** (company memory), **Slack** (comms) and **Figma** (design handoff).

Authorize via your claude.ai connector settings, or `/mcp` in an interactive session.

### 6. Python is the old system 3.9.6, and user-installed CLIs are off PATH

`pip3 install --user` puts binaries in `~/Library/Python/3.9/bin`, which is **not on your PATH**,
so anything installed that way is invisible. If you want Python tooling to work, either add that
directory to PATH in `~/.zshrc`, or install `uv` (needs Homebrew or its own installer script).

I did not modify your shell profile.

---

## P2 — worth knowing, no action needed yet

### 7. Unidentified global npm package

`@vudovn/ag-kit@2026.8.31` is installed globally. It predates this preflight and I could not
establish its purpose. Worth a look — an unknown global package with an unfamiliar scope is the
kind of thing to be deliberate about.

### 8. Full Xcode is not installed

Only Command Line Tools are present. The iOS Simulator MCP is available but **cannot build an
iOS app**. Only relevant if the company ships mobile.

### 9. Supabase MCP has production-level authority

`execute_sql`, `apply_migration`, `deploy_edge_function` and `pause_project` are all reachable.
Before any autonomous agent runs, decide whether to gate these behind confirmation. This is the
single largest blast-radius item in the environment.

### 10. ECC's GateGuard hook will interrupt autonomous runs

It blocked the first Bash call of this session pending a restatement of facts. Good for supervised
work; it will stall unattended agents. Decide deliberately before the OS runs unsupervised —
scoping is via `GATEGUARD_BASH_ROUTINE_DISABLED=1` or `ECC_DISABLED_HOOKS`. Do not disable blindly.

### 11. Every Bash command is logged to disk

ECC writes `~/.claude/bash-commands.log` and `~/.claude/cost-tracker.log` (~1.5 MB each). Useful
telemetry; also a data-retention decision you should make knowingly.
