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

[ -n "$CLAUDE_PROJECT_DIR" ] && cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
[ -f scripts/harness.py ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

INPUT=$(cat)

TOOL=$(printf '%s' "$INPUT" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("tool_name", ""))
except Exception:
    print("")
' 2>/dev/null) || exit 0

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
        # Harness malfunction. Fail open by design; see FAILURE POSTURE above.
        exit 0
        ;;
esac
