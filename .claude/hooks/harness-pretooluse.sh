#!/bin/sh
# Harness PreToolUse governance.
#
# Records every tool request in the execution ledger and enforces the permission
# policy held in company.db (`permission_rules`, deny-biased, last-match-wins).
#
# COMPOSITION: this runs ALONGSIDE ECC GateGuard, which also occupies PreToolUse.
# Claude Code runs every registered hook for an event; either may block. This hook
# does not replace, disable or reorder GateGuard.
#
# FAILURE POSTURE, stated deliberately:
#   * A real policy DENY or APPROVAL-REQUIRED blocks the call (exit 2). Fails CLOSED.
#   * A harness malfunction (missing python3, missing db, parse error) exits 0.
#     Fails OPEN, so a broken ledger cannot brick the founder's session. This is a
#     considered trade-off: availability of the human's own tooling outranks
#     enforcement completeness. It is a known bypass, recorded in
#     .ai-company/harness/SECURITY.md rather than hidden.
#
# Role comes from HARNESS_ROLE (default: orchestrator). HARNESS_EXECUTION, when set,
# correlates the tool call to a live execution row.

INPUT=$(cat)

# Extract the tool name WITHOUT depending on the harness, so the failure posture can
# be graduated even when the harness itself is unreachable. Falls back to a grep if
# python3 is missing entirely.
TOOL=$(printf '%s' "$INPUT" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("tool_name", ""))
except Exception:
    print("")
' 2>/dev/null) || TOOL=""
if [ -z "$TOOL" ]; then
    TOOL=$(printf '%s' "$INPUT" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi

# GRADUATED FAILURE POSTURE, applied to EVERY bail-out path.
#
# The first version of this hook exited 0 on four separate guards - unreachable
# project dir, missing harness, missing python3, unparseable payload. Each was an
# independent fail-open hole: break any one of them and every tool call proceeds
# ungoverned. A test proved it: with CLAUDE_PROJECT_DIR pointed at a nonexistent
# path, `rm -rf /` was permitted.
#
# Now a degraded harness falls back to READ-ONLY. Read-only tools pass so the
# founder's session stays usable; anything with a side effect is refused.
harness_unavailable() {
    case "$TOOL" in
        Read|Grep|Glob|NotebookRead|TodoWrite|WebFetch|WebSearch|"")
            exit 0
            ;;
        *)
            printf 'HARNESS UNAVAILABLE (%s) - failing closed for %s\n' "$1" "$TOOL" >&2
            printf 'The permission engine could not be consulted, so this call is refused.\n' >&2
            printf 'Read-only tools still work. Diagnose:  python3 scripts/harness.py verify\n' >&2
            exit 2
            ;;
    esac
}

[ -n "$CLAUDE_PROJECT_DIR" ] && cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || harness_unavailable "project dir unreachable"
[ -f scripts/harness.py ] || harness_unavailable "harness.py missing"
command -v python3 >/dev/null 2>&1 || harness_unavailable "python3 missing"
[ -z "$TOOL" ] && exit 0

# The policy-relevant argument. For Bash this is the command string, which harness.py
# re-parses with shlex before matching: a path pattern that ignores the shell is
# decorative (see Roo-Code issue #4732).
ARG=$(printf '%s' "$INPUT" | python3 -c '
import sys, json
try:
    i = json.load(sys.stdin).get("tool_input", {}) or {}
    print(i.get("command") or i.get("file_path") or i.get("path") or i.get("url") or "")
except Exception:
    print("")
' 2>/dev/null)

ROLE="${HARNESS_ROLE:-orchestrator}"

# SPAWN AUTO-REGISTRATION.
# The harness cannot spawn (`claude` is not on PATH), so it cannot open the ledger
# entry at dispatch time. But this hook runs BEFORE the spawn, so registration happens
# whether or not the calling agent cooperates. This closes the last convention-dependent
# gap: an agent can no longer spawn work the ledger does not know about.
if [ "$TOOL" = "Task" ]; then
    SPAWN=$(printf '%s' "$INPUT" | python3 -c '
import sys, json
try:
    i = json.load(sys.stdin).get("tool_input", {}) or {}
    print((i.get("subagent_type") or "general-purpose").replace("\n", " "))
    print((i.get("description") or "").replace("\n", " "))
except Exception:
    print("general-purpose"); print("")
' 2>/dev/null)
    SUBTYPE=$(printf '%s' "$SPAWN" | sed -n 1p)
    SUBDESC=$(printf '%s' "$SPAWN" | sed -n 2p)
    NEWEX=$(python3 scripts/harness.py autoregister \
              subagent_type="$SUBTYPE" description="$SUBDESC" parent_role="$ROLE" \
              ${HARNESS_EXECUTION:+parent_execution="$HARNESS_EXECUTION"} 2>/dev/null | tail -1)
    case "$NEWEX" in
        EX-*) printf 'harness: spawn registered as %s\n' "$NEWEX" >&2 ;;
    esac
fi

if [ -n "$HARNESS_EXECUTION" ]; then
    OUT=$(python3 scripts/harness.py permit role="$ROLE" tool="$TOOL" arg="$ARG" execution="$HARNESS_EXECUTION" 2>&1)
else
    OUT=$(python3 scripts/harness.py permit role="$ROLE" tool="$TOOL" arg="$ARG" 2>&1)
fi
RC=$?

case "$RC" in
    0)
        exit 0
        ;;
    2)
        printf 'HARNESS DENY\n%s\n' "$OUT" >&2
        exit 2
        ;;
    3)
        printf 'HARNESS: APPROVAL REQUIRED\n%s\nThis is a founder decision. Ask; do not proceed.\n' "$OUT" >&2
        exit 2
        ;;
    *)
        # HARNESS MALFUNCTION - GRADUATED FAILURE POSTURE.
        #
        # The old behaviour failed open for every tool, which was the one hole a
        # determined attacker would aim at: break the harness, then act freely.
        #
        # Now a broken harness degrades to READ-ONLY rather than to wide-open.
        # Read-only tools still pass, so the founder's session stays usable and a
        # corrupt ledger cannot brick the machine. Everything capable of a side
        # effect is REFUSED until the harness is healthy again.
        case "$TOOL" in
            Read|Grep|Glob|NotebookRead|TodoWrite|WebFetch|WebSearch)
                exit 0
                ;;
            *)
                printf 'HARNESS UNAVAILABLE - failing closed for %s\n' "$TOOL" >&2
                printf 'The permission engine could not be consulted, so this call is refused.\n' >&2
                printf 'Read-only tools still work. Diagnose with:\n  python3 scripts/harness.py verify\n' >&2
                exit 2
                ;;
        esac
        ;;
esac
