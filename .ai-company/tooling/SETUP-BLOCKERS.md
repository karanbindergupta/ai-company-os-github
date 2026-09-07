# SETUP BLOCKERS

Actions that **genuinely require the founder**. Everything else in this preflight was completed
autonomously. No secrets, tokens or credentials were requested, printed, stored or committed.

---

## P0 — blocks the AI Company OS from functioning

### 1. ~~GitHub is not connected~~ — RESOLVED 2026-09-07

**Verified working.** `get_me` returns `karanbindergupta` (id 322836099, company `@chikmark`),
and 46 GitHub tools are live in-session.

Getting there took three fixes, recorded because the same failure will recur on any future
plugin install in this environment:

1. **The plugin is not OAuth.** It registers GitHub's remote MCP server
   (`https://api.githubcopilot.com/mcp/`) with `Authorization: Bearer
   ${GITHUB_PERSONAL_ACCESS_TOKEN}`. A fine-grained PAT is required.
2. **Enabling in `settings.json` does not install a plugin.** `installed_plugins.json` recorded
   `github` and `claude-security` as installed, but the app never copied their files into
   `~/.claude/plugins/cache/claude-plugins-official/<plugin>/<version>/`. The `.mcp.json` that
   defines the server was simply absent from disk. Fixed by copying from the marketplace clone
   (`plugins/` and `external_plugins/`) into the exact `installPath` each entry names.
   **The `claude` CLI is not on PATH in the desktop app**, so `claude plugin install` is
   unavailable here — this manual path is the working procedure.
3. **`~/.zshrc` is the wrong file.** zsh reads it only for interactive shells; the desktop app,
   launched from the Dock, never sources it. The token must go in the `env` block of
   `~/.claude/settings.json`.

### 1a. ~~Rotate the access token~~ — RESOLVED 2026-09-07

A token was pasted into a chat session and had to be treated as compromised. It has been
**revoked and replaced**. Evidence: the old token returned `token expired` from the GitHub MCP
endpoint; the replacement authenticates as `karanbindergupta` via `get_me`. `~/.zshrc` no longer
contains a token, and the credential now lives in exactly one place —
`~/.claude/settings.json` → `env.GITHUB_PERSONAL_ACCESS_TOKEN`.

**Operational notes for future credential work in this environment:**

- **`~/.zshrc` does not work.** zsh reads it only for interactive shells; the Dock-launched
  desktop app never sources it. Credentials must go in the `env` block of
  `~/.claude/settings.json`.
- **Paste, never hand-select.** One rotation attempt failed because the value was
  hand-selected in TextEdit and the `github_pat_` prefix was left behind — GitHub rejected it
  with `Authorization header is badly formatted`. The reliable procedure is to have the agent
  clear the field to `""` first, then click between the quotes and paste with ⌘V.
- **Prefix matching is not identity.** All of an account's fine-grained PATs share a leading
  segment (here `github_pat_11CM7B`), so a matching prefix does not mean a token was reused.
  Verify by authenticating, not by comparing prefixes.
- **Token still lives in plaintext on disk**, as `settings.json` requires. Mitigate with a short
  expiry and repository-scoped permissions rather than by hiding the file.

**Standing rule for the AI Company OS: no credential is ever pasted into a chat session, and no
agent ever asks for one.** A secret's only route is browser → clipboard → editor → file.

### 2. ~~Git has no identity~~ — RESOLVED 2026-09-07

Was: no `~/.gitconfig` existed, and `git commit` failed with `Author identity unknown`.

The founder ran the fix during the preflight session. `~/.gitconfig` now sets
`user.name = Karan` / `user.email = kewalsingh99990@gmail.com`, and the preflight
documentation was committed as `69cf0fd`.

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
