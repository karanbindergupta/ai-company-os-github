# SECURITY POLICY
**The CISO holds a release veto that neither the CTO nor the CEO may override.** Only the founder
may accept a security risk, and the acceptance is recorded against their name.
Coverage: authentication, authorization at every endpoint, data exposure, secrets, dependencies,
injection, XSS/SSRF/IDOR/CSRF, API security, privacy, configuration, third parties, abuse by
legitimate users. Tools: `claude-security`, `npm audit`. Gitleaks/Trivy/Semgrep blocked on Homebrew.
**Company OS security:** no secret is ever printed, logged or committed. `credential-handling` is
`deny` for every agent — an agent that needs a credential says where it goes and stops.
`.gitignore` excludes `.env*`. Sensitive tools (`supabase` writes, `claude-in-chrome`, deploys,
publishing, purchases) require confirmation.
**Red-teaming:** defensive only, this company's own product only, non-production only, never DoS,
never third-party systems, never real user data.
