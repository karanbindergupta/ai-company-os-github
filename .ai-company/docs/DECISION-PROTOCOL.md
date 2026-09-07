# DECISION PROTOCOL
Every significant decision is a database row, not a paragraph.
```bash
companydb.py decision new domain=<d> owner=<role> title=".." problem=".." options=".." rejected=".."
companydb.py decision dissent id=DEC-001 role=<r> position="Oppose" argument="<verbatim>"
companydb.py decision approve id=DEC-001 role=<reviewer>      # each required reviewer
companydb.py decision decide  id=DEC-001 role=<owner> decision=".." [founder_approval=".."]
```
**Rules enforced in code:** only the domain owner may propose or decide; every required reviewer
must approve first; an active veto blocks the decision entirely; founder-required domains refuse
without `founder_approval`. Dissent is stored verbatim and reported at decision time — the system
counts it and says so. Rejected alternatives are mandatory: they stop the company relitigating.
A decision is reopened only with **new evidence**, recorded as a new decision superseding the old.
