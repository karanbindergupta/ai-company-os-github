---
description: Define the product: requirements, MVP boundary, acceptance criteria
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

Scope: **$ARGUMENTS**

```bash
python3 scripts/company.py phase-start product_spec
```

Dispatch `product-lead` across its role packs. Required outputs:
- `.ai-company/product/requirements.md` — every requirement traced to a validated problem
- `.ai-company/product/mvp.md` — the MVP boundary, explicit
- `.ai-company/product/features.md` — **including a non-empty rejected-features list**
- `.ai-company/product/nfr.md` — quantified, with measurement methods
- `.ai-company/product/acceptance-criteria.md` — binary and testable

```bash
python3 scripts/company.py gate gate_product_spec pass|fail by=cpo
```
The gate fails if the reject list is empty, any NFR is unquantified, or any acceptance criterion
requires interpretation.
