# PLUGIN INVENTORY

**Audit date:** 2026-09-07
**Config:** `~/.claude/settings.json` (backed up to `settings.json.pre-preflight-20260907-135027.bak`)

## Marketplaces registered

| Marketplace | Source | Trust |
|---|---|---|
| `claude-plugins-official` | `github:anthropics/claude-plugins-official` | **Anthropic-managed.** 291 plugins. Highest trust. |
| `ecc` | `git:github.com/affaan-m/everything-claude-code` | Third-party, community. Very large surface. |
| `ui-ux-pro-max-skill` | `git:github.com/nextlevelbuilder/ui-ux-pro-max-skill` | Third-party. Marketplace registered; plugin **disabled**. |

## Plugins

### `ecc@ecc` — v2.2.1 — ENABLED (pre-existing)

Installed 2026-09-01, commit `ca185ef`. Path: `~/.claude/plugins/cache/ecc/ecc/2.2.1`.

| Surface | Count |
|---|---|
| Agents | 68 |
| Commands | 94 |
| Skills | 286 |
| Hook scripts | 51 |

Registers hooks on **7 event types**: `PreToolUse` (8 matcher groups), `PostToolUse`,
`PostToolUseFailure`, `PreCompact`, `SessionStart`, `Stop` (7 groups), `SessionEnd`.
Named hooks include `stop:check-console-log`, `stop:cost-tracker`, `stop:format-typecheck`,
`stop:evaluate-session`, `stop:desktop-notify`, `session:end:marker`, and a `PreToolUse`
Bash gate ("GateGuard") that **intercepted and blocked the first Bash call of this session**
until facts were restated.

**Assessment: KEEP, with two caveats.**

- *Value:* It supplies most of the specialist agent roster and the orchestration skills
  (`orch-*`, `gan-*`, `multi-*`, `team-agent-orchestration`) that the AI Company OS would
  otherwise have to build. This is the single largest asset in the environment.
- *Caveat 1 — surface area.* 286 skills and 51 hooks is a very large amount of third-party
  code executing on `PreToolUse`. It writes `~/.claude/bash-commands.log` (1.5 MB) and
  `~/.claude/cost-tracker.log` (1.5 MB), i.e. **every Bash command is logged to disk**.
  That is useful telemetry and also a data-retention consideration.
- *Caveat 2 — GateGuard friction.* The Bash fact-forcing gate will interrupt autonomous agents.
  Before the OS runs unattended, decide deliberately: keep it (safer, slower) or scope it via
  `GATEGUARD_BASH_ROUTINE_DISABLED=1` / `ECC_DISABLED_HOOKS`. **Do not disable it blindly.**

### `ui-ux-pro-max@ui-ux-pro-max-skill` — v2.13.0 — INSTALLED BUT DISABLED

Present in `~/.claude/plugins/cache/` and in `installed_plugins.json`, but **absent from
`enabledPlugins`** in the live `settings.json`. It *was* enabled in `settings.json.bak`
(2026-09-02), so the founder appears to have disabled it deliberately on or after 2026-09-05.

**Assessment: LEAVE AS IS.** Not re-enabled by this preflight — reversing a deliberate founder
decision without a reason would violate the "never delete/alter working configuration without a
documented reason" principle. Design capability is already covered by Adobe Express, Cloudinary,
v0, Miro, the `design` skill and the `artifact-design` skill. If the founder wants it back:

```bash
claude plugin enable ui-ux-pro-max@ui-ux-pro-max-skill
```

### `claude-security@claude-plugins-official` — v0.10.2.3 — **INSTALLED BY THIS PREFLIGHT**

Author: Anthropic (`support@anthropic.com`). Source: local path inside the already-cloned
official marketplace.

Why it was chosen, and why it was the only install:

- It closes the **only genuinely uncovered required capability** — static vulnerability analysis.
  Nothing else in the environment did SAST.
- It runs **entirely inside the Claude Code session**. No MCP server, no network credentials,
  no API key, no external account. Nothing to authorize.
- Its sole hook is `UserPromptExpansion` matching `^claude-security:claude-security$` and it
  **prints a banner** — the manifest explicitly states it "never returns a permission decision".
  Zero interception of tool calls.
- Ships 7 agents (`scan-inventory`, `scan-researcher`, `scan-verifier`, `patch-generator`,
  `patch-verifier`, `explore`, `claude-security`), 1 skill, 1 workflow (`scan.js`).
  Findings are adversarially verified before being reported — which matches the "adversarial
  agents" requirement of the future OS.

**Verification status:** installed and registered in `settings.json`. **Its agents and the
`/claude-security` command load on the next Claude Code session start** — plugin registration is
read at startup, so it could not be exercised within this session. First run should be a scan of
a real repository once one exists.

## Plugins evaluated and NOT installed

| Plugin | Why not |
|---|---|
| `playwright` (official, Microsoft) | **Duplicate.** Three browser stacks are already active. Adding a fourth violates the anti-duplication rule. |
| `semgrep` (third-party) | Overlaps `claude-security` for this stage, and is a third-party git-subdir MCP. Revisit only if `claude-security` proves insufficient on a real codebase. |
| `supabase`, `vercel`, `sentry`, `stripe`, `cloudinary` (official) | Supabase and Cloudinary MCPs are **already present** as connectors. Vercel/Sentry/Stripe are speculative — there is no product and no deployment target yet. |
| `aikido`, `42crunch`, `endor-labs`, `stackhawk` | All require paid accounts and external credentials. Not justified pre-product. |

### `github@claude-plugins-official` — **ENABLED BY THIS PREFLIGHT (awaiting token)**

Author: GitHub. Enabled at the founder's explicit instruction. Because the `claude` CLI is not on
PATH in the desktop app, it was enabled by editing `~/.claude/settings.json` directly
(backup: `settings.json.pre-github-*.bak`).

It is **not an OAuth plugin**. It registers GitHub's remote MCP server:

| | |
|---|---|
| Transport | `http` |
| Endpoint | `https://api.githubcopilot.com/mcp/` |
| Auth | `Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}` |
| Token present? | **No** — verified unset in the environment |

**Verification status: enabled but NOT functional.** The server will fail to authenticate until
`GITHUB_PERSONAL_ACCESS_TOKEN` is exported. Token handling is a founder action — see
`SETUP-BLOCKERS.md` §1. Scope the PAT narrowly: it grants an autonomous system write access to
repositories.
