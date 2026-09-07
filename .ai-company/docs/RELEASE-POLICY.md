# RELEASE POLICY
Seven gates, all required: product_ready, engineering_ready, qa_passed, security_passed,
performance_ok, docs_ready, rollback_ready.
```bash
companydb.py release new version=1.0.0
companydb.py release approve id=REL-1.0.0 gate=qa_passed role=qa-lead
companydb.py release check id=REL-1.0.0
companydb.py release ship id=REL-1.0.0 role=release-manager founder_approval="<what they approved>"
```
`ship` refuses on any unmet gate, any active veto, or missing founder approval.
The **Release Manager can stop any release but cannot authorize one** — that is the founder's.
High-risk releases (auth, data, payments, migrations) additionally require executive review.
