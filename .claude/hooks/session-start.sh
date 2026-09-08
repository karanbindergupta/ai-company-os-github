#!/bin/sh
# Surfaces run state at session start so an interrupted mission is never silently restarted.
# Read-only and fast. If anything is wrong, exit quietly rather than blocking the session.
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
[ -f .ai-company/state/run.json ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
STATUS=$(python3 scripts/company.py resume 2>/dev/null) || exit 0
[ -n "$STATUS" ] || exit 0
printf 'AI COMPANY - a mission is in progress. Do not restart it; continue from here.\n\n%s\n\nRun /company-resume to continue, or /company for full status.\n' "$STATUS"
