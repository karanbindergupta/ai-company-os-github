# Security model
**Deny-biased, last-match-wins.** Nothing is permitted unless a later rule allows it.
Effects: `ALLOW` · `ALLOW_WITH_AUDIT` · `ALLOW_READ_ONLY` · `REQUIRE_APPROVAL` · `DENY`.

**Bash is matched on the shlex-parsed argv, not the raw string.** Roo-Code issue #4732 shows a mode
restricted to `\.(md|yaml|json)$` editing PowerShell anyway: a path pattern that ignores the shell is
decorative. Verified blocked here: `cat .env`, `echo x && cat .env`, `(cat .env)`, `F=.env; cat $F`.

**Founder-only:** granting approvals, setting `GLOBAL_PAUSE`. Red-team A4 confirms an agent
attempting either exits 2.

## KNOWN BYPASSES — stated, not hidden
1. **The hook fails OPEN on harness malfunction.** If `python3` is missing, the DB is unreadable, or
   the hook errors, the tool call proceeds. Deliberate: a broken ledger must not brick the founder's
   session. Availability of human tooling outranks enforcement completeness. **Accepted risk.**
2. **The harness cannot spawn.** `claude` is not on PATH, so an execution row is created by the
   caller. An agent cannot bypass *permissions*, but it can fail to *register an execution at all*.
   Tool calls are still recorded; execution attribution is not guaranteed. **Open.**
3. **A rule authored too broadly is a live hazard.** Proven: `*rm*` matched "pe**rm**it" and blocked
   legitimate work. Fixed to token matching. The failure mode was safe (blocked, not silently allowed).
4. **`ALLOW_WITH_AUDIT` records but does not stop.** By design; it is not a containment control.
