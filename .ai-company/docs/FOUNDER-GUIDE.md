# FOUNDER GUIDE

## Starting a company

```
/company-start Industry: fintech. Idea: a tool that reconciles invoices for small agencies.
```

That is the whole input. The company determines geography, segment, scope, stack and sequencing
itself. **You are not expected to answer a questionnaire.**

## What happens next

Before anything is built, the company runs: discovery → parallel research → business model →
strategy → brand → **executive debate** → Master Brief → product spec → architecture + design →
implementation plan. Each stage has a gate that can fail.

You will be asked for material decisions only. Everything else, it decides.

## The commands you will actually use

| Command | Purpose |
|---|---|
| `/company-start <industry + idea>` | Begin a mission |
| `/company` | Where are we, and what needs me? |
| `/company-resume` | Continue after any interruption |
| `/status` | Terse status |
| `/release` | Verify every gate and prepare a release |

The other 18 commands drive individual phases (`/research`, `/debate`, `/build`, `/test`,
`/security`, `/audit`, `/fix`, `/hire`, …). You rarely need them — the orchestrator invokes the
work itself.

## When you will be asked

Only for: mission or strategy change, a pivot away from your idea, spend or pricing or legal
commitment, an irreversible or outward-facing action (deploy, publish, send, purchase), an
accepted security risk, or a genuine executive deadlock.

You will get a **decision package** — recommendation first, then why, evidence, alternatives,
tradeoffs, risks, and exactly what you are approving. Never a pile of raw research.

## What the company will do that may surprise you

- **It may tell you your idea is wrong.** Discovery can invalidate the founder's premise. That is
  a successful discovery, and it is written up with the evidence rather than softened.
- **It will refuse to mark work done without evidence.** This is enforced in code, not manners.
- **It will fail its own gates.** A failed gate is the system working.
- **It will not build everything you ask for.** The rejected-features list is a required artifact.

## If a session ends mid-run

Nothing is lost. State is written at every transition. Open a new session in this folder and run
`/company-resume` — a hook will also surface the in-progress mission automatically.

## Interrupting

Stop any time. The run stays where it is. Completed phases are never redone.

## What it cannot do without you

- Deploy to production, publish, post, send, or purchase
- Handle any credential — **it will never ask you for a token or password**
- Accept a security risk
- Commit spend or set a public price
- Create a new executable subagent

## Current environment limits

- **GitHub Actions/CI cannot be inspected.** The company will not claim CI status.
- **No Homebrew**, so `gitleaks`, `trivy` and Docker are unavailable. Dependency scanning is
  `npm audit` plus the `claude-security` plugin.
- Three browser stacks are available; a fourth must not be installed.
