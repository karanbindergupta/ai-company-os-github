# Evaluation and maturity
`python3 scripts/harness_eval.py` — failure injection, self-red-team, metrics. Exit 1 on any failure.

**Maturity levels:** L0 conceptual · L1 implemented · L2 tested · L3 adversarially tested ·
L4 empirically validated (real workload evidence) · L5 production-proven.

**Nothing here is above L3.** L4 requires evidence from real missions, not self-tests. The harness
does not grade itself into maturity — the same rule the Company OS applies to its agents.

## Red-team attacks executed (all currently blocked)
A1 forged/claim-only evidence · A2 self-review · A3 security review by non-security role ·
A4 self-authorisation and self-lifting an emergency pause · A5 credential read via plain, pipeline,
subshell and shell-variable indirection · A6 unknown-tool fail-open · A7 unregistered owner and
owner==reviewer · A8 fabricated evidence path on task completion · A9 unrecorded provider claim ·
A10 CRITICAL profile completion without required reviews · A11 direct DB insert of a SUCCEEDED
execution · A12 hand-edited task projection.
