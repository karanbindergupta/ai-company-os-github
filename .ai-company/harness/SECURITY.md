# Security model
**Deny-biased, last-match-wins.** Nothing is permitted unless a later rule allows it.
Effects: `ALLOW` · `ALLOW_WITH_AUDIT` · `ALLOW_READ_ONLY` · `REQUIRE_APPROVAL` · `DENY`.

**Bash is matched on the shlex-parsed argv, not the raw string.** Roo-Code issue #4732 shows a mode
restricted to `\.(md|yaml|json)$` editing PowerShell anyway: a path pattern that ignores the shell is
decorative. Verified blocked here: `cat .env`, `echo x && cat .env`, `(cat .env)`, `F=.env; cat $F`.

**Founder-only:** granting approvals, setting `GLOBAL_PAUSE`. Red-team A4 confirms an agent
attempting either exits 2.

## KNOWN BYPASSES — stated, not hidden

### CLOSED 2026-09-09 — the fail-open hole
The hook previously exited 0 on **four separate guards** — unreachable project dir, missing
`harness.py`, missing `python3`, unparseable payload. Each was an independent fail-open path.
**A test proved the impact: with `CLAUDE_PROJECT_DIR` pointed at a nonexistent path, an arbitrary
destructive shell command was permitted.**

**Now a degraded harness falls back to READ-ONLY.** Read-only tools still pass so the session stays
usable; `Bash`, `Write`, `Edit` and `Task` are **refused**. Verified against all four guards.

**Residual:** a read-only tool still passes when the harness is down. Deliberate floor — the
alternative is a corrupt ledger bricking the machine.

### CONTAINMENT — seatbelt, not Docker
Docker is absent and cannot be installed (no Homebrew). macOS **seatbelt** is present and fits
better: no daemon, no images, no root, and it confines the process rather than a VM.
`harness.py sandbox` confines a command to one workspace on Apple's `bsd.sb` base, writes
restricted to the workspace, **network denied unless granted**. Every run recorded in `sandbox_runs`.

**Limit:** seatbelt confines filesystem and network. It is not a VM boundary and does not defend
against a kernel exploit. That needs a container, and that needs Docker.
2. **The harness cannot spawn.** `claude` is not on PATH, so an execution row is created by the
   caller. An agent cannot bypass *permissions*, but it can fail to *register an execution at all*.
   Tool calls are still recorded; execution attribution is not guaranteed. **Open.**
3. **A rule authored too broadly is a live hazard.** Proven: `*rm*` matched "pe**rm**it" and blocked
   legitimate work. Fixed to token matching. The failure mode was safe (blocked, not silently allowed).
4. **`ALLOW_WITH_AUDIT` records but does not stop.** By design; it is not a containment control.
