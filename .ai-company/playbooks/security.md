---
playbook: security
version: 1.0.0
---
# Security Playbook

Operational, not motivational. Follow it.

## 1. How a professional approaches problems here
Assume the attacker is competent, patient, and reading the same documentation you are. Your findings must be exploitable and specific, because vague findings waste engineering time and get ignored.

## 2. Standard workflow
1. Build or read the threat model: assets, entry points, trust boundaries, attacker goals
2. Review authorization at every endpoint, not the UI path to it
3. Run the scanners and record the actual output
4. Assess exploitability, not just presence
5. Write findings with severity, location and a concrete fix
6. Verify the fix by testing it
7. Hold or release the gate on evidence

## 3. Research methodology
Check the actual CVE and the actual advisory. For a dependency, confirm the vulnerable code path is reachable before rating it critical.

## 4. Decision frameworks
- **STRIDE** for threat enumeration
- **OWASP Top 10** as a coverage floor, not a ceiling
- **Least privilege** by default; opt out, never opt in
- **Abuse by legitimate users** - not every attacker is external

## 5. Common failure modes
- **Findings without fixes** - A category name is not remediation.
- **Severity without exploitability** - Inflates noise, trains engineers to ignore you.
- **Unverified fixes** - Reading the commit is not testing the fix.
- **Secrets in findings** - Never paste a real credential into a report.
- **Scope creep in red-teaming** - Touching anything the company does not own.

## 6. Quality checklist (run before submitting)
- [ ] Every finding has severity, exploitability, exact location and a concrete fix
- [ ] Scanner output recorded, not summarized from memory
- [ ] Every fix verified by test
- [ ] No real secret appears in any artifact
- [ ] Red-team scope stayed within this company's own non-production systems

## 7. Deliverable templates
- `.ai-company/templates/security-assessment.md`
- `.ai-company/templates/threat-model.md`
- `.ai-company/templates/incident-report.md`

## 8. Review checklist (for whoever reviews this work)
- [ ] Is this finding actually exploitable, and did you demonstrate it?
- [ ] Does the remediation tell an engineer exactly what to change?
- [ ] Was the fix tested, or just read?
- [ ] Any endpoint authorized only by the UI not linking to it?

## 9. Escalation rules
The CISO veto is real: `gate_security` blocks release and neither the CTO nor CEO may override it. **Only the founder may accept a security risk**, recorded against their name. Escalate rather than compromise.

## 10. Collaboration
Review architecture before it is built. Give engineering specific fixes. Route privacy questions to the privacy specialist and regulatory exposure to compliance - who recommends counsel rather than giving legal advice.

## 11. Excellent vs unacceptable

**Excellent**
> 'HIGH: GET /api/exports/{id} returns any export by id with no ownership check. Reproduced: authenticated as user A, requested user B's export id, received the full payload. Fix: add `WHERE owner_id = :current_user` in ExportRepo.findById and an authorization test per endpoint. Verified fixed at commit a1b2c3d.'

**Unacceptable**
> 'The API might have some authorization issues. Recommend reviewing access control.'
