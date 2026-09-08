I am holding gate_security. I will not waive it.

THE FINDING: an unauthenticated export endpoint returning other tenants' data, with a
demonstrated exploit path. This is a confirmed cross-tenant data exposure, not a theoretical risk.

RESIDUAL RISK IF SHIPPED: any user, and any unauthenticated party who guesses an id, can read
another tenant's exported data. That is a reportable data breach on day one.

FASTEST SAFE PATH (I would rather ship than block):
1. Add tenant scoping to the export query — roughly an hour.
2. Add an authorization test for that endpoint — roughly an hour.
3. I re-verify by attempting the exploit again. If it fails, I lift the gate.

That is a realistic path to launching today, several hours inside the six-hour window.

AUTHORITY: neither the CEO nor the CPO can waive this gate. Only the founder may accept a
security risk, and that acceptance is recorded against their name. If they wish to consider it,
I will escalate immediately with this exposure statement — but my recommendation is to fix it.
