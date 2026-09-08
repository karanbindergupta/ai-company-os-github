#!/bin/sh
# Pre-commit secret scan. Exits non-zero on a real credential.
# Matches only credential-LENGTH strings, so prose about token formats does not false-positive.
cd "$(git rev-parse --show-toplevel)" || exit 1
PAT='github_pat_[A-Za-z0-9_]{30,}|ghp_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|xox[baprs]-[A-Za-z0-9-]{20,}'
HITS=$(git grep -nIE "$PAT" -- . ':!scripts/secret_scan.sh' 2>/dev/null)
if [ -n "$HITS" ]; then
  echo "SECRETS DETECTED - commit blocked:"; echo "$HITS" | cut -c1-100; exit 1
fi
echo "secret scan: clean"
