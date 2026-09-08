# FUTURE INTEGRATIONS

A map, not a shopping list. **Nothing here is installed.** Each entry is gated by
`TOOLING-POLICY.md`'s seven gates at the moment it is actually needed.

---

## Core — the AI Company will almost certainly need these

| Capability | Recommended | When | Notes |
|---|---|---|---|
| GitHub | `github@claude-plugins-official` | **Now** | Already a P0 blocker — see `SETUP-BLOCKERS.md` §1 |
| Homebrew | Homebrew installer | **Now** | Meta-blocker; unlocks most other tooling |
| Work tracking | `linear` **or** `asana` (already present, unauthorized) | At org formation | Pick **one**. Linear suits engineering-led orgs |
| Company memory | `notion` (already present, unauthorized) | At org formation | Complements, does not replace, `.ai-company/` |
| Comms | `slack` (already present, unauthorized) | When >1 human is involved | Not needed while the founder works solo |
| Design handoff | `figma` (already present, unauthorized) | When design→engineering handoff begins | Adobe/v0/Miro cover creation already |
| Secret scanning in CI | `gitleaks` via Homebrew | First real repo | `claude-security` covers in-session review |
| Containers | Docker Desktop | First service with a real runtime | Also unlocks reproducible test environments |

## Product-dependent — only once the industry and product are chosen

| If the product needs… | Evaluate | Do not install before |
|---|---|---|
| Payments | `stripe` plugin, or Airwallex for multi-currency | A pricing model exists |
| Database beyond Supabase | `neon`, `cockroachdb`, `clickhouse`, or a Cloud SQL plugin | A schema exists |
| Deployment | `vercel`, `cloudflare`, `aws-core`, or `azure` | A deployable artifact exists |
| Auth | `auth0` plugin, or Supabase Auth (already reachable) | User accounts are specified |
| Email | Resend/Postmark, or `ecc:mailtrap-email-integration` | Transactional email is designed |
| Maps/geo | `amazon-location-service` | Location is a product requirement |
| Search/scraping | `brightdata-plugin`, `youdotcom-agent-skills` | Native `WebSearch` proves insufficient |
| API security | `42crunch-api-security-testing` | A public API spec exists |
| Mobile | Full Xcode + the iOS Simulator MCP already present | Mobile is on the roadmap |
| CMS/content | `ckeditor`, `contentful`-class plugins | Content modelling is done |

## Scale-stage — after the product has real users

- **Observability:** `sentry` + `sentry-cli` — error tracking is the first thing to add once
  real traffic exists. Currently nothing is instrumented because nothing is deployed.
- **Product analytics:** `amplitude` or `pendo` (both present, unauthorized).
- **Customer support:** `intercom` (present, unauthorized).
- **Meeting capture:** `fireflies` (present, unauthorized).
- **Competitive intel:** `similarweb` (present, unauthorized).
- **Supply-chain security:** `syft` + `grype`, or Endor Labs once the dependency tree is large
  enough that `npm audit` stops being sufficient.
- **DAST:** `stackhawk-hawkscan` once a staging environment exists.
- **CI/CD:** `buildkite`, or GitHub Actions via the GitHub plugin.
- **Cap table / finance:** `carta-cap-table`, `airwallex-agentos` — only if the company raises.

## Optional — nice to have, easy to justify away

- `gitkraken` — richer git context. Overlaps the GitHub plugin (Gate 2).
- `canva` — overlaps Adobe Express and Cloudinary (Gate 2).
- `browser-use` — a fourth browser stack. **Refused by policy.**
- `code-modernization`, `aws-transform` — only relevant to legacy migration, which a greenfield
  company does not have.
- `claude-code-setup`, `claude-md-management` — meta-tooling; the AI Company OS will supply its own.
- `agent-sdk-dev` — only if the company builds *on* the Claude Agent SDK as a product.

## Standing review rhythm

Re-run this audit when any of these happen:

1. The founder names the industry and product → re-check the FUTURE lane in `SKILL-INVENTORY.md`
   for a matching vertical skill before installing anything new.
2. A tech stack is chosen → install only that stack's toolchain.
3. The first deployment target is chosen → install only that provider's tooling.
4. The connector set changes at the claude.ai account level → refresh `MCP-INVENTORY.md`, since
   host-injected servers cannot be pinned from disk.
