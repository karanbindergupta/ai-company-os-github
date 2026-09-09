---
artifact: defect
component: scripts/companydb.py
severity: medium
found: 2026-09-08
found_during: PROJECT ATLAS run_a2d1d5010d
status: open
---
# Defect — `risk add` generates colliding IDs after any deletion

## Symptom
`python3 scripts/companydb.py risk add ...` fails with
`sqlite3.IntegrityError: UNIQUE constraint failed: risks.id`

## Cause
The ID is derived from `COUNT(*)` rather than the maximum existing ID. After RISK-003 and RISK-004
were deleted (founder revocation of a mission), `COUNT(*)+1` resolved to an ID that already existed.

## Impact
Any risk deletion permanently breaks `risk add` until IDs are assigned manually. The same pattern
appears in `cmd_escalate` (`SELECT COUNT(*) FROM escalations`) and so escalations are affected too —
**ESC-002 and ESC-003 were deleted in the same operation, so the next `escalate` call will collide.**

## Fix
Derive the next ID from the maximum existing numeric suffix, not the row count. Applies to at least
`risks` and `escalations`; audit every other `COUNT(*)+1` ID generator in the file.

## Workaround used
Direct `INSERT` with an explicit next-free ID, plus a matching `audit_log` row so the ledger stays
complete.
