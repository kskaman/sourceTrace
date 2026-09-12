---
title: "Access Control Policy"
category: "IT"
doc_type: "policy"
last_updated: "2024-06-15"
owner: "Information Security"
classification: "Confidential"
---

# Access Control Policy

**Document ID:** ITSEC-003
**Effective Date:** June 15, 2024
**Approved by:** VP of Engineering
**Classification:** Confidential

## 1. Purpose

This policy defines the access controls that govern how employees, contractors, and systems access Acme Corp's production systems, internal applications, and sensitive data. Access controls ensure that only authorized individuals can access resources necessary for their role, reducing the risk of unauthorized disclosure, modification, or destruction of company and customer information.

## 2. Principles

### 2.1 Least Privilege

All access is granted on the principle of least privilege. Users receive the minimum level of access necessary to perform their assigned duties. Elevated access for temporary tasks (e.g., incident investigation, migration) must be requested through the IT portal and is automatically revoked after the approved duration.

### 2.2 Separation of Duties

Critical functions must be divided among multiple individuals to prevent any single person from having end-to-end control over a sensitive process. Examples include:

- The person who writes code must not be the same person who deploys it to production.
- The person who creates a vendor payment must not be the same person who approves it.
- Database administrators must not have the ability to modify audit logs.

### 2.3 Need-to-Know

Access to Confidential and Restricted data requires a documented business justification. Access controls for these classifications are enforced at the application, database, and network levels.

## 3. Role-Based Access Controls (RBAC)

### 3.1 Role Definitions

Acme Corp uses role-based access controls to manage permissions. Standard roles include:

| Role | Access Level | Example Systems |
|---|---|---|
| Viewer | Read-only access to non-sensitive data | Wiki, internal dashboards, team documents |
| Contributor | Read and write access to team resources | Code repositories, project boards, shared drives |
| Admin | Full control over a specific system or application | System configuration, user management, data exports |
| Super Admin | Cross-system administrative access | Identity provider, secrets management, production infrastructure |

### 3.2 Role Assignment

Roles are assigned based on job function and level. The default access for a new employee is determined by their department and role during onboarding. Additional access beyond the default requires a formal access request.

| Job Function | Default Role |
|---|---|
| Individual contributor | Viewer + Contributor (own team resources) |
| People manager | Viewer + Contributor + Admin (team-specific systems) |
| IT operations | Contributor + Admin (infrastructure systems) |
| Security engineer | Contributor + Admin (security tools) + Viewer (production logs) |
| Executive (L7+) | Viewer (company-wide dashboards) |

### 3.3 Privileged Access

Privileged accounts (Admin and Super Admin) are subject to additional access controls:

- Multi-factor authentication is required for every session.
- Sessions are logged with full command capture for production systems.
- Privileged access is reviewed monthly (not quarterly) by the InfoSec team.
- Just-in-time (JIT) access is used where possible: privileged access is granted for a defined window and automatically revoked.

## 4. Access Lifecycle

### 4.1 Provisioning

New access is provisioned through the following process:

1. Employee or manager submits a request via the IT portal, specifying the system, the role requested, and the business justification.
2. The system owner reviews and approves or denies within 2 business days.
3. IT provisions the access and confirms with the requestor.
4. The access grant is logged in the identity management system with the approval chain.

### 4.2 Modification

When an employee's role changes (promotion, lateral move, team transfer), the following occurs:

- The employee's previous access is reviewed within 5 business days of the effective date.
- Access that is no longer required is revoked.
- New access appropriate to the new role is provisioned through the standard request process.

Managers are responsible for initiating the access review when a direct report changes roles.

### 4.3 Revocation

Access is revoked:

- Immediately upon involuntary termination.
- At the end of the business day on the employee's last day for voluntary resignation.
- At the end of the contract period for contractors (per the Contractor Access Policy).
- Within 1 business day when a system owner determines that access is no longer needed.

### 4.4 Quarterly Access Reviews

System owners conduct quarterly access reviews for all systems handling Confidential or Restricted data. The review process:

1. IT generates a report of all active accounts and their roles for each system.
2. The system owner reviews each account and confirms or revokes access.
3. Accounts that have not been used in 90 days are flagged for removal.
4. The completed review is submitted to the InfoSec team and retained for audit purposes.

Quarterly access reviews are a SOC 2 control and must be completed within 15 business days of the quarter end.

## 5. Access Controls for Specific Environments

### 5.1 Production Environment

Access to production systems is restricted to:

- On-call engineers (read access to logs and metrics; write access limited to incident remediation).
- Database administrators (through the approved database proxy with query logging).
- The automated deployment pipeline (no interactive human access).

Direct SSH access to production servers is prohibited. All production access is through the bastion host with MFA and full session recording.

### 5.2 Customer Data

Access to customer data requires:

- A documented business justification reviewed by the system owner.
- Completion of the data handling training for the relevant classification level.
- For Restricted data (PII, PHI): approval from the Data Protection Officer in addition to the system owner.

Customer data access is logged and audited monthly by the InfoSec team.

### 5.3 Third-Party Access

Third-party vendors and partners who require access to Acme Corp systems must:

- Sign a data processing agreement (see the Data Processing Agreement Template).
- Access only through the vendor VPN gateway with MFA.
- Be sponsored by an Acme Corp employee who serves as the access owner.
- Have access scoped to the minimum necessary for the contracted work.

Third-party access is reviewed monthly by the sponsoring employee and IT.

## 6. Monitoring and Enforcement

All access control events (grants, revocations, denials, escalations) are logged in the identity management system and forwarded to the SIEM for monitoring. The InfoSec team investigates anomalies including:

- Access requests for systems outside the employee's normal scope.
- Repeated access denials.
- Accounts with excessive permissions relative to their role.
- Dormant accounts with active access.

Violations of this policy are reported to the employee's manager and Human Resources. Repeated or willful violations may result in disciplinary action up to and including termination.

## 7. Policy Governance

This policy is reviewed annually by the Information Security team and approved by the VP of Engineering. Questions should be directed to security@acmecorp.com.

---

*Version 2.0 — Last revised June 15, 2024*
