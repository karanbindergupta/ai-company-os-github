# MCP INVENTORY

**Audit date:** 2026-09-07

## Key finding: there is no local MCP configuration

`~/.claude.json` has **no** `mcpServers` block, and every project entry in it has `mcpServers: []`.
There is no `.mcp.json` anywhere in scope. `mcp-registry list_connectors` returns `{"connectors": []}`.

Every MCP server below is injected by the **Claude Desktop host** (account-level connectors and
built-in tooling) or by an **enabled plugin** — not by a file on this machine. Consequences:

- These servers **cannot be audited or version-pinned from disk**. Their trust derives from the
  Anthropic host and the founder's claude.ai connector settings.
- Adding or removing them is done in **claude.ai connector settings / the desktop app**, not by
  editing config here.
- A future `.mcp.json` in a project directory would be *additive* to this set.

---

## Active servers

| Server | Surfaced as | Purpose | Permissions / reach | Keep? |
|---|---|---|---|---|
| **Miro** | `03b88433-…` | Boards, docs, diagrams, tables, canvas SVG, comments, spaces | Read + **write** to the founder's Miro team; can create/share/move boards | Keep — strategy & design artefacts |
| **Cloudinary** | `1fc9efd4-…` | Asset DAM: upload, transform, tag, **generate images**, delete | Read + **write + delete** on the founder's media library | Keep — marketing/brand asset store |
| **Supabase** | `46fbe9d3-…` | Postgres: list tables, `execute_sql`, `apply_migration`, branches, edge functions, advisors, logs | **Highest-risk server present.** Can execute arbitrary SQL and deploy functions against real projects | Keep, but see risk note |
| **Adobe Express** | `a4014958-…` | Design authoring, image editing (~40 ops), fonts, video, PDF/InDesign, stock licensing | Read + write to Adobe cloud storage; `asset_license_and_download_stock` can consume entitlements | Keep — creative org |
| **v0 (Vercel)** | `ac198052-…` | UI generation chats, previews | Creates v0 chats on the founder's account | Keep — UI prototyping |
| **mcp-registry** | `mcp-registry` | Discover/suggest connectors | Read-only catalogue | Keep |
| **Claude Browser** | `Claude_Browser` | In-app browser: navigate, a11y tree, console, network, screenshots, viewport emulation | Full web browsing from the app's own browser | Keep — **primary browser/QA surface** |
| **Claude in Chrome** | `claude-in-chrome` | Drives the founder's **real Chrome with live logins** | Very high blast radius — acts as the signed-in user | Keep, use sparingly |
| **chrome-devtools** | `plugin_ecc_chrome-devtools` | Performance traces, Lighthouse, heap snapshots, network/console | Third browser stack, via the ECC plugin | Keep for perf work only |
| **iOS Simulator** | `Claude_Code_iOS_Simulator` | Boot/drive/screenshot iOS simulators, build | Local simulators only. **Blocked: only Xcode CLT installed, no full Xcode** | Keep, currently non-functional for builds |
| **terminal** | `terminal` | Read-only view of the user's terminal panel | Read-only | Keep |
| **visualize** | `visualize` | Inline SVG/HTML widgets in chat | Render-only | Keep |
| **ccd_session / ccd_directory / ccd_session_mgmt** | host | Session metadata, chapters, directory changes, cross-session messaging | Local session control | Keep — **orchestration substrate** |
| **scheduled-tasks** | `scheduled-tasks` | Create/list/update/delete scheduled tasks | Schedules future autonomous runs | Keep — **required for autonomous cadence** |

## Servers requiring authorization (unusable until the founder authorizes)

From the `product-management` plugin — **14 servers, all unauthenticated:**

`amplitude` · `amplitude-eu` · `asana` · `atlassian` · `clickup` · `figma` · `fireflies` ·
`intercom` · `linear` · `monday` · `notion` · `pendo` · `similarweb` · `slack`

`~/.claude/mcp-needs-auth-cache.json` records failed auth probes for 12 of these dating to
2026-08-31. **This session is non-interactive and cannot run the OAuth flow.** See
`SETUP-BLOCKERS.md`.

## Absent, and deliberately so

**No GitHub MCP server is present.** Verified three ways: tool search for `+github` returns no
GitHub tool; `mcp-registry search_mcp_registry(["github","repository","pull request","git"])`
returns `{"results": []}`; no GitHub tool appears in the session's deferred-tool manifest.
See `SETUP-BLOCKERS.md` §1.

## Security review of the MCP surface

1. **Supabase is the sharpest edge.** `execute_sql`, `apply_migration`, `deploy_edge_function`
   and `pause_project` are production-capable. Before the AI Company OS runs autonomously,
   constrain it: development branches only, and a permission rule requiring confirmation on
   `apply_migration` / `execute_sql` / `deploy_edge_function`.
2. **`claude-in-chrome` acts as the logged-in founder.** Any page it visits can attempt prompt
   injection against a browser holding live sessions. Prefer `Claude_Browser` (isolated) for
   all research and QA; reserve real Chrome for tasks that genuinely need existing logins.
3. **Three browser stacks are active.** This is pre-existing, not something this preflight added.
   No fourth (e.g. Playwright) should be installed — see `TOOLING-POLICY.md`.
4. **Cloudinary and Miro both hold delete/write authority** over founder-owned content. Treat any
   destructive call from an autonomous agent as requiring confirmation.
5. **Host-injected servers cannot be pinned.** Accept this, and re-run this audit whenever the
   connector set changes.
