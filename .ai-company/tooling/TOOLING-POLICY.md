# TOOLING POLICY

Rules governing what may be added to this environment. Binding on every future agent in the
AI Company OS.

## The mental model

```
AGENTS       = employees          SKILLS = expertise
MCPs         = equipment          TOOLS  = infrastructure
ORCHESTRATOR = management         .ai-company/ = company memory & state
```

External tools supply **capabilities**. They must never be used to duplicate the **organisation** —
the OS itself provides the organisational intelligence. An "AI employee" plugin is always the wrong
answer; a piece of equipment an employee lacks may be the right one.

## The seven gates

Before installing any MCP server, plugin, or CLI tool, all seven must pass:

1. **Native first.** Does Claude Code already do this? Filesystem, search, subagents, parallelism,
   scheduling, git and artifacts are all native. If native covers it, stop.
2. **No duplicate.** Does an installed capability already cover it? Three browser stacks are already
   present — a fourth is refused regardless of quality.
3. **Real need, now.** Is there a project that needs it *today*? Speculative installs for a product
   that does not exist yet are refused. "We might need Stripe" is not a reason.
4. **Reputable and maintained.** Prefer Anthropic-authored, then official vendor plugins from
   `claude-plugins-official`, then well-maintained third parties. **Star count is not evidence.**
5. **Least privilege.** What can it read, write, delete, execute? Can it reach the network or the
   filesystem? Anything with delete or production-write authority needs an explicit decision.
6. **Credential honesty.** If it needs an API key, OAuth, an account or billing, it is a **founder
   action** — it is documented in `SETUP-BLOCKERS.md`, never worked around, never bypassed.
7. **Verifiable.** If it cannot be tested after installation, it is not installed.

## Priority classes

| Class | Meaning | Rule |
|---|---|---|
| **P0** | Essential; the OS cannot function without it | Install autonomously **if** safe and credential-free; otherwise escalate as a blocker |
| **P1** | Highly valuable | Install only with a written justification recorded here |
| **P2** | Optional | Document in `FUTURE-INTEGRATIONS.md`. Do not install |
| **P3** | Irrelevant to this environment | Do not install. Do not document beyond a line |

## Hard prohibitions

- No second GitHub integration.
- No fourth browser stack.
- No filesystem MCP — native tools are sufficient.
- No additional web-search MCP — `WebSearch`/`WebFetch` are sufficient and verified.
- No "AI employee"/agent-framework plugins.
- No installing a tool because it appeared in a tutorial or a listicle.
- **No secret, API key or token is ever printed, echoed, logged or committed.** `.ai-company/` is
  for state and documentation, never for credentials.
- No destructive security testing against any system without written authorization.
- Never bypass an authentication prompt. Escalate instead.

## Change procedure

1. Name the missing capability and the concrete task that is blocked by its absence.
2. Run the seven gates in writing.
3. Compare at least two candidate implementations.
4. Choose the **smallest reliable** option.
5. Back up `~/.claude/settings.json` before editing it.
6. Install.
7. **Verify by execution** and record the evidence.
8. Update `CAPABILITY-MATRIX.md`, `MCP-INVENTORY.md` or `PLUGIN-INVENTORY.md`, and note the
   justification here.

## Removal procedure

Never remove working configuration without a documented reason. Disabling is preferred to deleting.
Record what was removed, why, and how to restore it. Where the founder appears to have made a
deliberate configuration choice (see `ui-ux-pro-max` in `PLUGIN-INVENTORY.md`), do not reverse it —
surface it.

## Decisions taken during the 2026-09-07 preflight

**Installed (1):** `claude-security@claude-plugins-official` — Anthropic-authored, in-session,
zero credentials, single display-only hook. Closed the only uncovered required capability (SAST).

**Refused (9), with reasons:**

| Refused | Gate failed |
|---|---|
| `playwright` plugin | Gate 2 — three browser stacks already active |
| A second web-search MCP | Gate 1 — `WebSearch`/`WebFetch` verified sufficient |
| A filesystem MCP | Gate 1 — native tools sufficient |
| `semgrep` plugin | Gates 2 + 4 — overlaps `claude-security`; third-party |
| `supabase` / `cloudinary` plugins | Gate 2 — already present as connectors |
| `vercel`, `sentry`, `stripe` plugins | Gate 3 — no product, no deployment target |
| `aikido`, `42crunch`, `endor-labs`, `stackhawk` | Gates 3 + 6 — paid accounts, external credentials |
| Downloaded release binaries (`gh`, `gitleaks`, `trivy`) | Policy — no fetching and executing binaries from the network without explicit founder approval |
| Re-enabling `ui-ux-pro-max` | Removal procedure — reversing an apparently deliberate founder decision |

**Not done, deliberately:** no shell profile was modified, no git identity was set, no OAuth was
attempted, no product code was written, and no part of the AI Company OS was built.
